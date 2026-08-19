#!/usr/bin/env python3
"""Aggregate the independent disjoint and total-overlap trust paths."""

from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
RUNS = (
    (
        (sys.executable, "-I", str(HERE / "independent_replay.py"), "--full"),
        "PASS_INDEPENDENT_DISJOINT_GRAPH_CARVING_WALL_AUDIT",
    ),
    (
        (sys.executable, "-I", str(HERE / "universal-total-decoder-wall" / "verify.py")),
        "PASS_UNIVERSAL_TOTAL_DECODER_WALL",
    ),
    (
        (sys.executable, "-I", str(HERE / "universal-total-decoder-wall" / "independent_replay.py")),
        "PASS_MINRANK_IDEMPOTENT_SANDWICH_AUDIT",
    ),
)


def main() -> None:
    for argv, marker in RUNS:
        completed = subprocess.run(
            argv,
            cwd=HERE,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        output = completed.stdout + completed.stderr
        if output:
            print(output, end="" if output.endswith("\n") else "\n")
        if completed.returncode != 0:
            raise SystemExit(f"sub-replay failed ({completed.returncode}): {argv[2]}")
        if marker not in output:
            raise AssertionError(f"missing sub-replay marker: {marker}")
    print("PASS_DISJOINT_AND_TOTAL_OVERLAP_REUSE_WALLS")


if __name__ == "__main__":
    main()
