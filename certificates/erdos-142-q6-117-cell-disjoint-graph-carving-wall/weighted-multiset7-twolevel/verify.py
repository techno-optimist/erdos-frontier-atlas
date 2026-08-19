#!/usr/bin/env python3
"""Portable source-plus-hostile replay for the two-level weighted bound."""

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
EXPECTED = {
    SOURCE: {
        "THEOREM.md": "92d2690ac412dcf5438e63f3ac56c6095801ac9b9bfdc1343ac9aa77df70afc4",
        "verify.py": "bae091ada91a3266c066386fa13e00a94a7a81e480a02186b848007b2414a122",
        "run.ps1": "9b17764fcc51b63288b4d3509d84e310d7b80cf3a1375e936939acacf98f0414",
        "SHA256SUMS": "d73625924640cb570077f0cff5128eee8591503ef65743458e748ed7892da1cf",
    },
    AUDIT: {
        "HOSTILE_AUDIT.md": "48dc37249d4d1e954da0cbd0cc79c84031893a6c767eaf5a30b1e5535b62ce4a",
        "independent_audit.py": "147a6395a5e32c254f610614897cc02459eb961c70c5782e971f29ede17ba7de",
        "run.ps1": "b4c622c58ac5d6caaa0c058c39b17b45e5557d90aac5e076b34e46c12b56d67e",
        "run.sh": "2dd458fad3c2557664658e9dc687f9f33b466a05b3a8190ddc25c87d41bad256",
        "SHA256SUMS.hostile": "8b866e8c86e06d1fc4935aa19fdb5c81598e8fc6c0dd6761edbfe94918363e92",
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
        names = {path.name for path in directory.iterdir() if path.is_file()}
        need(names == set(expected), f"frozen file census: {directory.name}")
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
            (sys.executable, "-I", str(SOURCE / "verify.py")),
            "PASS_WEIGHTED_MULTISET7_TWO_LEVEL_BOUND",
        ),
        (
            (sys.executable, "-I", str(AUDIT / "independent_audit.py"), str(SOURCE)),
            "PASS_INDEPENDENT_TWO_LEVEL_WEIGHTED_HOSTILE_AUDIT",
        ),
    )
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = tuple(executor.submit(run_checked, command, marker)
                        for command, marker in runs)
        outputs = tuple(future.result() for future in futures)
    for output in outputs:
        print(output, end="" if output.endswith("\n") else "\n")

    need(snapshot() == before, "replay mutated frozen weighted bytes")
    print("PLANTED_BAD_ARG_REJECTED")
    print("TWO_LEVEL_WEIGHTED_SOURCE_AND_AUDIT_NONMUTATION_OK")
    print("PASS_PORTABLE_WEIGHTED_MULTISET7_TWO_LEVEL_BOUND")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
