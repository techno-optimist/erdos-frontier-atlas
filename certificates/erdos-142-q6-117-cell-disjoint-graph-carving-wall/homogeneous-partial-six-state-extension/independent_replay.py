#!/usr/bin/env python3
"""Portable slow replay of the independent six-state hostile audit."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
AUDIT = HERE / "audit"
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
    AUDIT: {
        "HOSTILE_AUDIT.md": "24ca7957b267cdb37083d51d0113561dfb65a1c3404ff22be71e754e54886d6e",
        "independent_six_state.cpp": "da915b410f2ca37356a2479d9979bc53dfc382d3e734122f468e00e3c1252d3f",
        "independent_six_scope_physical.py": "2a68daeab13b46452768a7e437118f596d2bc7d0687bf13b9f189a621f7425ca",
        "run_hostile.ps1": "e435615c86363d7f267eafa1b573065a1ff3016427f8478f0c5017ad656a8384",
        "run_hostile.sh": "cbf1d8bc631279d29038d036c092f3d167d2bf83ef355f8e888f8c2dc917920a",
        "SHA256SUMS.hostile": "9db4670f186bae130f85dd15c55c2bf3d2ea7f2c131b836a1330733adb8aefa2",
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


def source_replay() -> str:
    return run_checked(
        [sys.executable, "-I", str(HERE / "verify.py")], HERE,
        "PASS_PORTABLE_AT_MOST_SIX_STATE_SOURCE")


def hostile_cpp_replay(compiler: str) -> str:
    with tempfile.TemporaryDirectory(prefix="q42-six-state-hostile-") as name:
        binary = Path(name) / ("audit.exe" if os.name == "nt" else "audit")
        run_checked([
            compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
            str(AUDIT / "independent_six_state.cpp"), "-o", str(binary),
        ], AUDIT)
        return run_checked(
            [str(binary)], AUDIT,
            "PASS_INDEPENDENT_SIX_STATE_PRODUCT_FIRST_WALL")


def hostile_physical_replay() -> str:
    return run_checked([
        sys.executable, "-I",
        str(AUDIT / "independent_six_scope_physical.py"),
        "--source", str(SOURCE), "--five", str(FIVE),
    ], AUDIT, "PASS_INDEPENDENT_SIX_SCOPE_AND_PHYSICAL_HOSTILE_REPLAY")


def main(argv: list[str]) -> None:
    require_no_args(argv)
    verify_cli_control()
    before = verify_bytes()
    compiler = shutil.which("g++")
    need(compiler is not None, "g++ is required for the hostile replay")
    with ThreadPoolExecutor(max_workers=3) as executor:
        source_future = executor.submit(source_replay)
        cpp_future = executor.submit(hostile_cpp_replay, compiler)
        physical_future = executor.submit(hostile_physical_replay)
        source_output = source_future.result()
        cpp_output = cpp_future.result()
        physical_output = physical_future.result()

    for marker in (
        "INDEPENDENT_SIX rooted_accessible=23836540 rooted_strong=12346720 strong_orbits=2058472 full=2056831 incomplete=1641",
        "witnessed_pairs=74045916 missing_pairs=59076 incomplete_below_B=1640 incomplete_equal_B=1 incomplete_above_B=0",
        "boundary_checksum=9776710376808584319 boundary_code_sum=1041120840919",
        "max_reached=798 max_horizon=50",
    ):
        need(marker in cpp_output, f"missing hostile census marker: {marker}")
    for marker in (
        "PASS_FROZEN_SIX_AND_FIVE_HASH_SCOPE_CONTRACT",
        "PASS_ACCEPTED_RATE_LIVE_TRIM_AND_SINGLETON_EXIT_CONTROL",
        "PASS_FULL_Q42_DISJOINT_ONE_RED_PER_PACKET_PACKING_REPLAY",
        "PASS_ALL_441_SIZE7_PACKETS_ROWS_AND_POSITIVE_RAW_COST",
        "PASS_LENGTH50_WITNESS_AND_ALL_SEVEN_RED_ROLE_PHYSICAL_LIFTS",
    ):
        need(marker in physical_output, f"missing hostile physical marker: {marker}")

    # Preserve source, independent C++, independent Python output order.
    for output in (source_output, cpp_output, physical_output):
        print(output, end="" if output.endswith("\n") else "\n")
    need(verify_bytes() == before, "portable hostile replay mutated frozen bytes")
    print("PLANTED_BAD_ARG_REJECTED")
    print("PORTABLE_SIX_HOSTILE_BYTES_NONMUTATION_OK")
    print("APPROVE_Q42_AT_MOST_SIX_STATE_SLOW_HOSTILE_REPLAY")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
