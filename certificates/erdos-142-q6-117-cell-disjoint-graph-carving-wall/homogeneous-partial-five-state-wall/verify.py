#!/usr/bin/env python3
"""Portable exact replay for the frozen at-most-five-state source packet."""

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
SOURCE_HASHES = {
    "AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md": "6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72",
    "exhaust_five_state_orbits.cpp": "2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb",
    "verify_lower_state_live_sccs.py": "b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139",
    "run.ps1": "302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631",
    "run.sh": "853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74",
    "SHA256SUMS": "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71",
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


def verify_source() -> dict[str, str]:
    files = {path.name for path in SOURCE.iterdir() if path.is_file()}
    need(files == set(SOURCE_HASHES), "frozen source file census")
    actual = {name: sha256(SOURCE / name) for name in SOURCE_HASHES}
    need(actual == SOURCE_HASHES, "frozen source hashes")
    manifest = {}
    for line in (SOURCE / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        manifest[name] = digest
    need(manifest == {name: digest for name, digest in SOURCE_HASHES.items()
                      if name != "SHA256SUMS"}, "frozen source manifest")
    return actual


def run_checked(argv: list[str], cwd: Path, marker: str | None = None) -> str:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    completed = subprocess.run(
        argv, cwd=cwd, env=env, check=False, capture_output=True,
        text=True, encoding="utf-8",
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise AssertionError(
            f"subprocess failed ({completed.returncode}): {argv}\n{output[-2000:]}")
    if marker is not None:
        need(marker in output, f"missing subprocess marker: {marker}")
    return output


def main(argv: list[str]) -> None:
    require_no_args(argv)
    verify_cli_control()
    before = verify_source()
    compiler = shutil.which("g++")
    need(compiler is not None, "g++ is required for the five-state replay")
    with tempfile.TemporaryDirectory(prefix="q42-five-state-primary-") as temporary:
        binary = Path(temporary) / ("verify.exe" if os.name == "nt" else "verify")
        run_checked([
            compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
            str(SOURCE / "exhaust_five_state_orbits.cpp"), "-o", str(binary),
        ], SOURCE)
        cpp_output = run_checked(
            [str(binary)], SOURCE, "PASS_FIVE_STATE_STRONG_ORBIT_WALL")
    python_output = run_checked(
        [sys.executable, "-I", str(SOURCE / "verify_lower_state_live_sccs.py")],
        SOURCE, "PASS_LOWER_ONE_THROUGH_FOUR_LIVE_SCC_WALL")

    for marker in (
        "PASS_Q42_SIZE7_PHYSICAL_ROLE_GEOMETRY",
        "STRONG_S5_ORBITS 64057",
        "ABOVE_BLUE_ORBITS 54184",
        "ABOVE_GATE_ORBITS 49047",
        "PAIRS 1354600",
        "MAX_PRODUCT_REACHABLE 335",
        "MAX_HORIZON 25",
    ):
        need(marker in cpp_output, f"missing primary semantic marker: {marker}")
    for marker in (
        "RATE_SCOPE accepted_language_limsup_equals_rho_of_reachable_coaccessible_trim",
        "AMBIENT_DEAD_SINK_RHO_EXCLUDED",
        "SOURCE_NONMUTATION_OK",
    ):
        need(marker in python_output, f"missing lower-state semantic marker: {marker}")

    print(cpp_output, end="" if cpp_output.endswith("\n") else "\n")
    print(python_output, end="" if python_output.endswith("\n") else "\n")
    need(verify_source() == before, "portable primary replay mutated frozen source")
    print("PLANTED_BAD_ARG_REJECTED")
    print("PORTABLE_SOURCE_NONMUTATION_OK")
    print("PASS_PORTABLE_AT_MOST_FIVE_STATE_PRIMARY")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
