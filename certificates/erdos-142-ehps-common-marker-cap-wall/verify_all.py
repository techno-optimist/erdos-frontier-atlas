#!/usr/bin/env python3
"""Portable structural replay for the literal common-marker h=4,...,8 wall."""

from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
CHECKS = (
    (HERE / "verify.py", "PASS_LITERAL_EHPS_COMMON_MARKER_H4_CAP_WALL"),
    (HERE / "h7-q9-cap-wall" / "verify.py", "PASS_H7_Q9_CAP_AUDIT"),
    (HERE / "q9-exact-midpoint-peel-capacity30" / "verify_all.py",
     "STRUCTURE_READY_EXTERNAL_PROOFS_REQUIRED"),
)


def main() -> None:
    before = Path(__file__).read_bytes()
    for script, marker in CHECKS:
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
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
        if "CONCLUSION_EXACT_C9_30" in result.stdout:
            raise AssertionError(
                f"{script.name} emitted the external-proof conclusion in "
                "compact mode"
            )
        if marker == "STRUCTURE_READY_EXTERNAL_PROOFS_REQUIRED" and (
                not result.stdout.rstrip().endswith("PASS_NONMUTATION")):
            raise AssertionError(
                "exact q9 compact replay did not terminate after its "
                "nonmutation gate"
            )
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if Path(__file__).read_bytes() != before:
        raise AssertionError("aggregate replay mutated itself")
    print("PASS_LITERAL_EHPS_COMMON_MARKER_H4_H7_LOCAL_SUBCOMPONENTS")
    print("SCOPE common_marker literal_EHPS_AB pointwise_phase_labelled_potential")
    print("STRUCTURE_READY_EXTERNAL_PROOFS_REQUIRED")


if __name__ == "__main__":
    main()
