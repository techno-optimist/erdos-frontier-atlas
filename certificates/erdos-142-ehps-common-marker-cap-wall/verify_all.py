#!/usr/bin/env python3
"""Portable aggregate replay for the literal common-marker h=4,...,8 wall."""

from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
CHECKS = (
    (HERE / "verify.py", "PASS_LITERAL_EHPS_COMMON_MARKER_H4_CAP_WALL"),
    (HERE / "h7-q9-cap-wall" / "verify.py", "PASS_H7_Q9_CAP_AUDIT"),
    (HERE / "h8-q9-peel-cap-wall" / "verify_all.py",
     "PASS_Q9_COMBINED_PACKAGE"),
)


def main() -> None:
    before = Path(__file__).read_bytes()
    for script, marker in CHECKS:
        result = subprocess.run(
            [sys.executable, "-I", str(script)],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"{script.name} failed with exit {result.returncode}: "
                f"{result.stderr.strip()}"
            )
        if marker not in result.stdout:
            raise AssertionError(f"{script.name} omitted {marker}")
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if Path(__file__).read_bytes() != before:
        raise AssertionError("aggregate replay mutated itself")
    print("PASS_LITERAL_EHPS_COMMON_MARKER_H4_H8_WALL")
    print("SCOPE common_marker literal_EHPS_AB pointwise_phase_labelled_potential")


if __name__ == "__main__":
    main()
