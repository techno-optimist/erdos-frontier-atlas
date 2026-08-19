#!/usr/bin/env python3
"""Portable aggregate replay for the structural at-most-fourteen-state wall."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
AUDIT = HERE / "audit"
PACKAGE = HERE.parent
SIX_SOURCE = PACKAGE / "homogeneous-partial-six-state-extension" / "source"
FIVE_SOURCE = PACKAGE / "homogeneous-partial-five-state-wall" / "source"

EXPECTED = {
    SOURCE: {
        "AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL.md": "c623c98bc19d2cc2d2024afee78c67a1d9eaaf0fa03d01d3c23ad8d1c35f70fc",
        "independent_structural_audit.py": "0f4e9d8c55e2ef53dc7c4a353342de6e3dd5f4107fa4a4eda46e3394d5fa4e9d",
        "run.ps1": "56b758c1ad547cb1f9f5c6c9aa6f29b36edbd37670b17fe3979f6e52c954b66a",
        "run.sh": "7da855a1700f28ed9685a657ed8d273e9fa28838f224f876cd0488e356b27989",
        "SHA256SUMS": "e25f34d571ddeb3b7dedf99924a00b2f2511d90777962f01ebeda97f4ce1a5eb",
        "verify_structural_closure.py": "d4c9812fe0f1468e50c8408d3d948f0c132e3afa6bc6453d4a009b654cf2ccb1",
    },
    AUDIT: {
        "HOSTILE_AUDIT.md": "2fb272025e7284e1820bca57c6b584342e9dd056afc281d78b2127daab92e891",
        "hostile_core_audit.py": "9bbf41f5b53ef6cbd10ab1fac5df18ad7ac295e352e66a2dd3c8ae6c6a964c5c",
        "run.ps1": "2a33500244e10db9cf7befd931610a8ab9a57edc31d993dc626d0ff875bcb405",
        "run.sh": "bc92ce9c8d3762521ff428beea93334236c65ecf8fc56ef9c8dd19d4a66859e1",
        "SHA256SUMS": "425fd3ee333ccf77fb41ba4c8269b39ccbefe33b0a89d1b14bd0cda74660992b",
    },
}


class UsageError(Exception):
    pass


def need(condition: bool, note: str) -> None:
    if not condition:
        raise AssertionError(note)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_no_args(argv: list[str]) -> None:
    if argv:
        raise UsageError("this verifier accepts no arguments")


def snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    for directory, expected in EXPECTED.items():
        actual_names = {path.name for path in directory.iterdir() if path.is_file()}
        need(actual_names == set(expected), f"frozen file census: {directory.name}")
        for name, expected_hash in expected.items():
            actual = digest(directory / name)
            need(actual == expected_hash, f"frozen hash: {directory.name}/{name}")
            result[str(directory / name)] = actual
    return result


def run_checked(argv: tuple[str, ...], marker: str) -> str:
    completed = subprocess.run(
        argv,
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise AssertionError(
            f"sub-replay failed ({completed.returncode}): {argv}\n{output[-3000:]}")
    need(marker in output, f"missing sub-replay marker: {marker}")
    return output


def main(argv: list[str]) -> None:
    require_no_args(argv)
    try:
        require_no_args(["--planted-invalid-argument"])
    except UsageError:
        pass
    else:
        raise AssertionError("planted invalid argument was accepted")

    before = snapshot()
    runs = (
        (
            (sys.executable, "-I", str(SOURCE / "verify_structural_closure.py")),
            "PASS_EXACT_Q42_HOMOGENEOUS_PARTIAL_STRUCTURAL_CLOSURE",
        ),
        (
            (sys.executable, "-I", str(SOURCE / "independent_structural_audit.py")),
            "PASS_INDEPENDENT_Q42_PARTIAL_STRUCTURAL_AUDIT",
        ),
        (
            (sys.executable, "-I", str(AUDIT / "hostile_core_audit.py"),
             "--source", str(SOURCE)),
            "APPROVE_Q42_PARTIAL_FOURTEEN_STATE_STRUCTURAL_CLOSURE",
        ),
        (
            (sys.executable, "-I", str(SIX_SOURCE / "verify_six_scope_physical.py"),
             str(FIVE_SOURCE)),
            "PASS_SIX_STATE_SCOPE_DEPENDENCY_AND_Q42_PHYSICAL_REPLAY",
        ),
    )
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = tuple(executor.submit(run_checked, command, marker)
                        for command, marker in runs)
        outputs = tuple(future.result() for future in futures)
    for output in outputs:
        print(output, end="" if output.endswith("\n") else "\n")

    need(snapshot() == before, "replay mutated frozen fourteen-state bytes")
    print("PLANTED_BAD_ARG_REJECTED")
    print("FOURTEEN_STATE_SOURCE_AND_AUDIT_NONMUTATION_OK")
    print("PASS_PORTABLE_AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
