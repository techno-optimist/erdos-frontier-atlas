#!/usr/bin/env python3
"""Portable fast replay of the first independent five-state hostile audit."""

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
AUDIT = HERE / "audit-a"

EXPECTED = {
    SOURCE: {
        "AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md": "6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72",
        "exhaust_five_state_orbits.cpp": "2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb",
        "verify_lower_state_live_sccs.py": "b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139",
        "run.ps1": "302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631",
        "run.sh": "853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74",
        "SHA256SUMS": "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71",
    },
    AUDIT: {
        "HOSTILE_AUDIT.md": "7794162fc6406f16d1305f9a1ddcd11d3b5c20c5a362552949800bb223f7e0c5",
        "independent_five_state_orbit_audit.cpp": "199ad25bf4b866b8514d282cbbc9402d6798db6c635cfbef339014846e6bc48c",
        "independent_lower_physical_scope_audit.py": "76cd5b1e1124c48d44a938f1d9a73dc525f6553088c34d88b7fd6f0add7435dd",
        "run.ps1": "d2adb35f928a8aea3eb9d76d4f9dc9d5d9043691518d71220abfb1e4e1826993",
        "run.sh": "a1097093e175f9e1a5430705eae32a32f68ed0b9c4c2d2320aae938bd90965ea",
        "SHA256SUMS": "f841480d2b25adf06c4f3410435f25aaf79b99036bbf4f69c0612b7c833461b9",
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
            f"subprocess failed ({completed.returncode}): {argv}\n{output[-2000:]}")
    if marker is not None:
        need(marker in output, f"missing subprocess marker: {marker}")
    return output


def cpp_replay(compiler: str) -> str:
    with tempfile.TemporaryDirectory(prefix="q42-five-audit-fast-") as temporary:
        binary = Path(temporary) / ("audit.exe" if os.name == "nt" else "audit")
        run_checked([
            compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
            str(AUDIT / "independent_five_state_orbit_audit.cpp"),
            "-o", str(binary),
        ], AUDIT)
        return run_checked(
            [str(binary)], AUDIT,
            "PASS_INDEPENDENT_FIVE_STATE_S5_ORBIT_AND_PRODUCT_AUDIT")


def python_replay() -> str:
    return run_checked(
        [sys.executable, "-I",
         str(AUDIT / "independent_lower_physical_scope_audit.py")],
        AUDIT, "PASS_INDEPENDENT_LOWER_SCOPE_AND_FULL_Q42_PHYSICAL_AUDIT")


def main(argv: list[str]) -> None:
    require_no_args(argv)
    verify_cli_control()
    before = verify_bytes()
    compiler = shutil.which("g++")
    need(compiler is not None, "g++ is required for the hostile replay")
    with ThreadPoolExecutor(max_workers=2) as executor:
        cpp_future = executor.submit(cpp_replay, compiler)
        python_future = executor.submit(python_replay)
        cpp_output = cpp_future.result()
        python_output = python_future.result()

    # Preserve file order even though the two read-only checks ran concurrently.
    print(cpp_output, end="" if cpp_output.endswith("\n") else "\n")
    print(python_output, end="" if python_output.endswith("\n") else "\n")
    need(verify_bytes() == before, "portable hostile replay mutated frozen bytes")
    print("PLANTED_BAD_ARG_REJECTED")
    print("PORTABLE_HOSTILE_BYTES_NONMUTATION_OK")
    print("APPROVE_Q42_AT_MOST_FIVE_STATE_FAST_HOSTILE_REPLAY")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
