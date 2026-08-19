#!/usr/bin/env python3
"""Aggregate disjoint, total, and bounded homogeneous-partial trust paths."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
LEGACY_RUNS = (
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

FAST_EXTENSION_RUNS = (
    (
        (sys.executable, "-I", str(
            HERE / "homogeneous-partial-six-state-extension" / "verify.py")),
        "PASS_PORTABLE_AT_MOST_SIX_STATE_SOURCE",
    ),
    (
        (sys.executable, "-I", str(
            HERE / "homogeneous-partial-five-state-wall" /
            "fast_independent_replay.py")),
        "APPROVE_Q42_AT_MOST_FIVE_STATE_FAST_HOSTILE_REPLAY",
    ),
    (
        (sys.executable, "-I", str(
            HERE / "weighted-multiset7-boundary" / "verify.py")),
        "PASS_PORTABLE_WEIGHTED_MULTISET7_BOUNDARY",
    ),
)

RUNS = LEGACY_RUNS + FAST_EXTENSION_RUNS


def replay(run: tuple[tuple[str, ...], str]) -> str:
    argv, marker = run
    completed = subprocess.run(
        argv,
        cwd=HERE,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError(
            f"sub-replay failed ({completed.returncode}): {argv[2]}\n{output[-3000:]}")
    if marker not in output:
        raise AssertionError(f"missing sub-replay marker: {marker}")
    return output


def main() -> None:
    # The replay paths are independent. A bounded pool keeps the hosted fast
    # gate below its wall-clock budget without weakening any constituent check.
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = tuple(executor.submit(replay, run)
                        for run in RUNS)
        outputs = tuple(future.result() for future in futures)
    for output in outputs:
        if output:
            print(output, end="" if output.endswith("\n") else "\n")

    print("PASS_DISJOINT_AND_TOTAL_OVERLAP_REUSE_WALLS")
    print("PASS_DISJOINT_TOTAL_AND_PARTIAL_SIX_STATE_WALLS")


if __name__ == "__main__":
    main()
