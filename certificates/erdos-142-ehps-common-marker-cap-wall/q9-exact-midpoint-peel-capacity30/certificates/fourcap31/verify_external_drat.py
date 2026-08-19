#!/usr/bin/env python3
"""Strictly replay the external four-cap DRAT ledger with drat-trim."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time


HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path,
                        default=HERE / "PROOF_PROVENANCE.json")
    parser.add_argument("--artifact-dir", type=Path, default=HERE)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    need(1 <= args.jobs <= 24, "jobs range")
    ledger = json.loads(args.ledger.read_text(encoding="ascii"))
    need(ledger["schema"] == "q9-four-cap-drat-provenance-v1",
         "ledger schema")
    cases = ledger["cases"]
    need(len(cases) == 24 and len({row["case"] for row in cases}) == 24,
         "case census")
    checker_hash = digest(args.checker)
    expected = {row["binary_sha256"] for row in ledger["checkers"]}
    need(checker_hash in expected, "checker hash is not pinned")

    for row in cases:
        cnf = args.artifact_dir / (row["case"] + ".cnf")
        proof = args.artifact_dir / (row["case"] + ".drat")
        need(cnf.stat().st_size == row["cnf_bytes"] and
             digest(cnf) == row["cnf_sha256"], row["case"] + " CNF hash")
        need(proof.stat().st_size == row["proof_bytes"] and
             digest(proof) == row["proof_sha256"], row["case"] + " proof hash")

    def replay(row):
        started = time.monotonic()
        cnf = args.artifact_dir / (row["case"] + ".cnf")
        proof = args.artifact_dir / (row["case"] + ".drat")
        result = subprocess.run([str(args.checker), str(cnf), str(proof)],
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        need(result.returncode == 0, "%s checker exit %d" %
             (row["case"], result.returncode))
        need(any(line.strip() == "s VERIFIED" for line in result.stdout.splitlines()),
             row["case"] + " missing VERIFIED marker")
        return row["case"], time.monotonic() - started

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(replay, cases))
    for name, seconds in results:
        print("DRAT_VERIFIED case=%s seconds=%.3f" % (name, seconds))
    print("PASS_EXTERNAL_DRAT cases=24 checker_sha256=%s elapsed=%.3f" %
          (checker_hash, time.monotonic() - started))


if __name__ == "__main__":
    main()
