#!/usr/bin/env python3
"""Portable exact replay for the frozen at-most-six-state source packet."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
FIVE = HERE.parent / "homogeneous-partial-five-state-wall" / "source"

EXPECTED = {
    SOURCE: {
        "AT_MOST_SIX_STATE_SUNFLOWER_WALL.md": "4e0059d11babefbfe6a19853b2d0b1b1d464879727d99ea49d5c5e26e3fa1bbc",
        "exhaust_six_state_orbits_cegar.cpp": "6f59fb09b6568f2bcb1a98d6045db1e42fbb99179263c913e97e92f77d17ce88",
        "verify_six_state_burnside.cpp": "50e81a587d7b67a4137031f740ffbc8d74217218d0a0569f2aacb1fc19c5b442",
        "verify_six_boundary.py": "7a362535f2afb528e9646540281eade02e4f03201c31daf422cad61359bee3bf",
        "verify_six_scope_physical.py": "607060c1d94551778db723f420db55c74d296d7b60eff5a7f60e75ab5dd241a6",
        "run.ps1": "cb28712f45c531afa60233a98bb728a53782db06d877045ca309dd3a09f61a7b",
        "run.sh": "fe83fa43245bd9ed9a90cc1257c255108c56adad95660b59864fef732a616cff",
        "SHA256SUMS": "a62da6552877464d13c45f615f1d61e9b05cee7c52e81b472db3f6a77dc97d01",
    },
    FIVE: {
        "AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md": "6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72",
        "exhaust_five_state_orbits.cpp": "2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb",
        "verify_lower_state_live_sccs.py": "b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139",
        "run.ps1": "302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631",
        "run.sh": "853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74",
        "SHA256SUMS": "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71",
    },
}


class UsageError(Exception):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_no_args(argv: list[str]) -> None:
    if argv:
        raise UsageError("this verifier accepts no arguments")


def verify_cli_control() -> None:
    try:
        require_no_args(["--planted-invalid-argument"])
    except UsageError:
        return
    raise AssertionError("planted invalid argument was accepted")


def verify_bytes() -> dict[str, str]:
    snapshot = {}
    for directory, expected in EXPECTED.items():
        files = {path.name for path in directory.iterdir() if path.is_file()}
        need(files == set(expected), f"frozen file census: {directory.name}")
        actual = {name: sha256(directory / name) for name in expected}
        need(actual == expected, f"frozen hashes: {directory.name}")
        snapshot.update({str(directory / name): digest
                         for name, digest in actual.items()})
    manifest = {}
    for line in (SOURCE / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        manifest[name] = digest
    need(manifest == {name: digest for name, digest in EXPECTED[SOURCE].items()
                      if name != "SHA256SUMS"}, "frozen source manifest")
    return snapshot


def run_checked(argv: list[str], cwd: Path, marker: str | None = None) -> str:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    completed = subprocess.run(
        argv, cwd=cwd, env=env, check=False, capture_output=True,
        text=True, encoding="utf-8",
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise AssertionError(
            f"subprocess failed ({completed.returncode}): {argv}\n{output[-3000:]}")
    if marker is not None:
        need(marker in output, f"missing subprocess marker: {marker}")
    return output


def primary_boundary_replay(compiler: str, temporary: Path) -> tuple[str, str]:
    binary = temporary / ("six-primary.exe" if os.name == "nt" else "six-primary")
    certificate = temporary / "six-boundary.tsv"
    run_checked([
        compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
        str(SOURCE / "exhaust_six_state_orbits_cegar.cpp"), "-o", str(binary),
    ], SOURCE)
    primary = run_checked(
        [str(binary), str(certificate)], SOURCE,
        "PASS_EXACT_SIX_STATE_S6_ORBIT_CEGAR_WALL")
    boundary = run_checked(
        [sys.executable, "-I", str(SOURCE / "verify_six_boundary.py"),
         str(certificate)], SOURCE,
        "PASS_INDEPENDENT_SIX_STATE_INCOMPLETE_BOUNDARY_REPLAY")
    return primary, boundary


def burnside_replay(compiler: str, temporary: Path) -> str:
    binary = temporary / ("six-burnside.exe" if os.name == "nt" else "six-burnside")
    run_checked([
        compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
        str(SOURCE / "verify_six_state_burnside.cpp"), "-o", str(binary),
    ], SOURCE)
    return run_checked(
        [str(binary)], SOURCE,
        "PASS_INDEPENDENT_SIX_STATE_BURNSIDE_ORBIT_COUNT")


def physical_replay() -> str:
    return run_checked(
        [sys.executable, "-I", str(SOURCE / "verify_six_scope_physical.py"),
         str(FIVE)], SOURCE,
        "PASS_SIX_STATE_SCOPE_DEPENDENCY_AND_Q42_PHYSICAL_REPLAY")


def main(argv: list[str]) -> None:
    require_no_args(argv)
    verify_cli_control()
    before = verify_bytes()
    compiler = shutil.which("g++")
    need(compiler is not None, "g++ is required for the six-state replay")
    with tempfile.TemporaryDirectory(prefix="q42-six-state-primary-") as name:
        temporary = Path(name)
        # Keep the two exhaustive C++ jobs sequential.  On the supported
        # two-core Windows runner this is faster than competing enumerators;
        # the package aggregate supplies the useful outer concurrency.
        primary_output, boundary_output = primary_boundary_replay(
            compiler, temporary)
        burnside_output = burnside_replay(compiler, temporary)
        physical_output = physical_replay()

    for marker in (
        "SIX_ROOTED accessible=23836540 strong=12346720",
        "SIX_S6_ORBITS strong=2058472 fully_product_screened=2056831 incomplete_product=1641",
        "SIX_PAIRS witnessed=74045916 missing=59076 incomplete_above_blue=0",
        "SIX_INCOMPLETE_RATES below=1640 equal=1 checksum=9776710376808584319 code_sum=1041120840919",
        "SIX_PRODUCT max_reached=798 max_horizon=50",
    ):
        need(marker in primary_output, f"missing primary semantic marker: {marker}")
    need("BURNSIDE_SUM 1482099840 S6_ORBITS 2058472" in burnside_output,
         "missing independent Burnside census")
    need("INDEPENDENT_BOUNDARY orbits=1641 missing_pairs=59076 below=1640 equal=1 above=0" in boundary_output,
         "missing independent boundary census")
    for marker in (
        "SIX_SCOPE accepted_language_limsup_equals_live_trim_rho",
        "SIX_PHYSICAL frozen_one_red_per_17640_packets",
    ):
        need(marker in physical_output, f"missing physical semantic marker: {marker}")

    # Emit in frozen source-file order, independent of scheduling.
    for output in (primary_output, burnside_output, boundary_output, physical_output):
        print(output, end="" if output.endswith("\n") else "\n")
    need(verify_bytes() == before, "portable source replay mutated frozen bytes")
    print("PLANTED_BAD_ARG_REJECTED")
    print("PORTABLE_SIX_AND_FIVE_BYTES_NONMUTATION_OK")
    print("PASS_PORTABLE_AT_MOST_SIX_STATE_SOURCE")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
