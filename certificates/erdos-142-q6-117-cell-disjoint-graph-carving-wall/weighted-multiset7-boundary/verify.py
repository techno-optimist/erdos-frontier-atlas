#!/usr/bin/env python3
"""Portable aggregate for the frozen weighted multiset-7 source and audit."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "erdos142_weighted_multiset7_sunflower_20260819"
AUDIT = HERE / "audit"
EXPECTED = {
    SOURCE: {
        "README.md": "9313303477481dd313f96532750a07f0cdb06f6abee3276fec4028f099797045",
        "THEOREM.md": "37e9674e49d5fbeb3793cd2a21c06797082d8027c0b4ff2a63103020cf2a8692",
        "FINITE_STATE.md": "431307c1bc4463988ec7cd4d3f6d585237f7eeac98ed35e5347fc48b43cd7534",
        "verify_weighted_multiset7.py": "10e584bc7974ae2216bd1dd9d004e50ed12d9146c3c45a580ad632eaf3374775",
        "finite_state_explorer.py": "1d221fc9c847616708e24f8cf80f6557150c606f3326a891e56f3b29a9a1d89e",
        "run.ps1": "40808472fd211a4435f087de96b7471d7c3d247ad83b033a2a8a92282b29d2a0",
        "SHA256SUMS": "c54c33d95df9979be73b683d42af4ab858c7791684252fba808b56bfa0c87f22",
    },
    AUDIT: {
        "HOSTILE_AUDIT.md": "0e6fdf1b9cd1698d39dae4f8ccaba31564df00b4b693e552148588bfb783e88f",
        "independent_weighted_multiset7_audit.py": "0537ab3246f1f739f22bd5352187190a59d8a2ac624427b9fe9965ee353efde6",
        "run.ps1": "9ef8cf9bce9ff4869c617eb51eec2afa482078d91da53e9fc7c35bac4b738eb8",
        "SHA256SUMS": "c116feb1a3c2e508b650501d8f0879329e24e597cd163fbcf0a2c35132f2eaa1",
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


def run_checked(argv: list[str], cwd: Path, marker: str) -> str:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    completed = subprocess.run(
        argv, cwd=cwd, env=env, check=False, capture_output=True,
        text=True, encoding="utf-8",
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise AssertionError(
            f"subprocess failed ({completed.returncode}): {argv}\n{output[-2000:]}")
    need(marker in output, f"missing subprocess marker: {marker}")
    return output


def main(argv: list[str]) -> None:
    require_no_args(argv)
    verify_cli_control()
    before = verify_bytes()
    primary = run_checked(
        [sys.executable, "-I", str(SOURCE / "verify_weighted_multiset7.py")],
        SOURCE, "PASS_WEIGHTED_MULTISET7_SUNFLOWER_PACKET")
    hostile = run_checked(
        [sys.executable, "-I", str(AUDIT / "independent_weighted_multiset7_audit.py")],
        AUDIT, "APPROVE_WEIGHTED_MULTISET7_SUNFLOWER_PACKET")
    for marker in (
        "PASS_MULTISET_REDUCTION_EXHAUSTIVE_D4",
        "PASS_M1_M2_STRENGTHENED_RECURSION_AND_CONSTRUCTIONS",
        "PASS_EXACT_RATIONAL_LYM_CAP_HORIZONS",
    ):
        need(marker in primary, f"missing weighted-primary marker: {marker}")
    for marker in (
        "PASS_INDEPENDENT_MULTISET_EQUIVALENCE",
        "PASS_INDEPENDENT_TENSOR_UNIFORMIZATION",
        "PASS_INDEPENDENT_LYM_PRIMAL_DUAL",
        "PASS_INDEPENDENT_DFA_ALL_LENGTHS",
        "SOURCE_PACKET_NONMUTATION_OK",
    ):
        need(marker in hostile, f"missing weighted-audit marker: {marker}")
    print(primary, end="" if primary.endswith("\n") else "\n")
    print(hostile, end="" if hostile.endswith("\n") else "\n")
    need(verify_bytes() == before, "weighted replay mutated frozen bytes")
    print("PLANTED_BAD_ARG_REJECTED")
    print("PORTABLE_WEIGHTED_BYTES_NONMUTATION_OK")
    print("PASS_PORTABLE_WEIGHTED_MULTISET7_BOUNDARY")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
