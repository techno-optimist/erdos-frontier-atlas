#!/usr/bin/env python3
"""Portable aggregate replay for the normalized q=9 four-cap certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "SHA256SUMS.txt"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def manifest_snapshot():
    rows = []
    for line_no, raw in enumerate(MANIFEST.read_text(encoding="ascii").splitlines(), 1):
        need(len(raw) >= 67 and raw[64:66] == "  ",
             "malformed manifest line %d" % line_no)
        checksum, relative = raw[:64], raw[66:]
        need(all(c in "0123456789abcdef" for c in checksum),
             "manifest checksum syntax")
        need(relative and "\\" not in relative and not relative.startswith("/") and
             ".." not in Path(relative).parts, "unsafe manifest path")
        rows.append((relative, checksum))
    need(len(rows) == len({relative for relative, _ in rows}),
         "duplicate manifest path")
    listed = {relative for relative, _ in rows}
    actual = {path.relative_to(HERE).as_posix()
              for path in HERE.rglob("*") if path.is_file()}
    need(actual == listed | {"SHA256SUMS.txt"},
         "manifest closure mismatch missing=%r extra=%r" %
         (sorted(listed - actual), sorted(actual - listed - {"SHA256SUMS.txt"})))
    current = {}
    for relative, checksum in rows:
        path = HERE / relative
        need(path.is_file(), "missing " + relative)
        current[relative] = digest(path)
        need(current[relative] == checksum, "hash mismatch " + relative)
    return current


def run(command, cwd=HERE):
    print("RUN", " ".join(map(str, command)), flush=True)
    result = subprocess.run(command, cwd=cwd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    need(result.returncode == 0, "command failed: %r" % (command,))
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-proof-dir", type=Path)
    parser.add_argument("--checker", type=Path)
    parser.add_argument("--proof-jobs", type=int, default=2)
    parser.add_argument("--core-census", action="store_true",
                        help="also replay the independent core6/7/8 packet")
    args = parser.parse_args()
    need((args.external_proof_dir is None) == (args.checker is None),
         "provide both --external-proof-dir and --checker")

    before = manifest_snapshot()
    print("PASS_MANIFEST files=%d" % len(before))
    python = [sys.executable, "-I", "-B"]
    run(python + [str(HERE / "verify_profile_reduction.py")])
    run(python + [str(HERE / "generate_case2_core6_cnf.py")])

    contract = json.loads((HERE / "CONTRACT.json").read_text(encoding="ascii"))
    need(contract["schema"] == "q9-four-cap-certificate-v1" and
         contract["base_cnf"] == {
             "bytes": 2915646, "clauses": 131681,
             "sha256": "3d490be403585b03ddc30b7aff7445b4c4e9d3b7550e2e97077964b627a88108",
             "variables": 11203} and
         contract["external_drat"] == {
             "cases": 24, "proof_bytes": 265645848,
             "result_each": "s VERIFIED"}, "contract schema")
    ledger = json.loads((HERE / "PROOF_PROVENANCE.json").read_text(encoding="ascii"))
    expected_names = ({"case2_center_second_%02d" % i for i in range(4)} |
                      {"case2_corner_second_%02d" % i for i in range(10)} |
                      {"case2_sat_second_%02d" % i for i in range(10)})
    need(ledger["schema"] == "q9-four-cap-drat-provenance-v1" and
         ledger["totals"] == {"cases": 24, "cnf_bytes": 69976122,
                               "proof_bytes": 265645848} and
         {row["case"] for row in ledger["cases"]} == expected_names and
         all(row["checker_result"] == "s VERIFIED"
             for row in ledger["cases"]), "proof ledger schema")
    with tempfile.TemporaryDirectory(prefix="q9_fourcap_") as temp_raw:
        temp = Path(temp_raw)
        run(python + [str(HERE / "generate_orbit_cnfs.py"),
                      "--write-dir", str(temp)])
        for row in ledger["cases"]:
            path = temp / (row["case"] + ".cnf")
            need(path.stat().st_size == row["cnf_bytes"] and
                 digest(path) == row["cnf_sha256"],
                 row["case"] + " regenerated CNF mismatch")
        print("PASS_REGENERATED_CASE_CNFS cases=24")

    if args.core_census:
        run(python + [str(HERE / "core_census_certificate" / "replay.py")],
            cwd=HERE / "core_census_certificate")

    if args.external_proof_dir is not None:
        run(python + [str(HERE / "verify_external_drat.py"),
                      "--artifact-dir", str(args.external_proof_dir),
                      "--checker", str(args.checker),
                      "--jobs", str(args.proof_jobs)])
        print("CONCLUSION_NORMALIZED_FOUR_CAP_SIZE31_UNSAT")
    else:
        print("FOUR_CAP_CERTIFICATE_READY external_drat_required_for_unsat_replay")

    after = manifest_snapshot()
    need(after == before, "package mutated during replay")
    print("PASS_NONMUTATION")


if __name__ == "__main__":
    main()
