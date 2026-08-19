#!/usr/bin/env python3
"""Portable aggregate replay for the exact q=9 capacity certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "SHA256SUMS.txt"
BASE = HERE / "certificates" / "capacity32_base"
FOURCAP = HERE / "certificates" / "fourcap31"
DIRECT = HERE / "certificates" / "direct_slab31"


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
    for line_no, raw in enumerate(
            MANIFEST.read_text(encoding="ascii").splitlines(), 1):
        need(len(raw) >= 67 and raw[64:66] == "  ",
             "malformed manifest line %d" % line_no)
        checksum, relative = raw[:64], raw[66:]
        need(re.fullmatch(r"[0-9a-f]{64}", checksum) is not None,
             "manifest checksum syntax")
        parts = Path(relative).parts
        need(relative and "\\" not in relative and
             not relative.startswith("/") and ".." not in parts,
             "unsafe manifest path")
        rows.append((relative, checksum))
    need(len(rows) == len({relative for relative, _ in rows}),
         "duplicate manifest path")

    all_entries = list(HERE.rglob("*"))
    need(not any(path.is_symlink() for path in all_entries),
         "symbolic links are forbidden")
    empty_dirs = [path.relative_to(HERE).as_posix() for path in all_entries
                  if path.is_dir() and not any(path.iterdir())]
    need(not empty_dirs, "empty directories: %r" % empty_dirs)
    listed = {relative for relative, _ in rows}
    actual = {path.relative_to(HERE).as_posix()
              for path in all_entries if path.is_file()}
    need(actual == listed | {"SHA256SUMS.txt"},
         "manifest closure mismatch missing=%r extra=%r" %
         (sorted(listed - actual),
          sorted(actual - listed - {"SHA256SUMS.txt"})))

    current = {}
    for relative, checksum in rows:
        path = HERE / relative
        need(path.is_file(), "missing " + relative)
        current[relative] = digest(path)
        need(current[relative] == checksum, "hash mismatch " + relative)
    return current


def run(command, cwd, required=(), suppress_prefixes=()):
    print("RUN", " ".join(map(str, command)), flush=True)
    result = subprocess.run(command, cwd=cwd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    visible = "\n".join(
        line for line in result.stdout.splitlines()
        if not line.startswith(tuple(suppress_prefixes)))
    if visible:
        print(visible)
    need(result.returncode == 0, "command failed: %r" % (command,))
    for marker in required:
        need(marker in result.stdout, "missing marker %r" % marker)
    return result.stdout


def read_json(path):
    return json.loads(path.read_text(encoding="ascii"))


def validate_contracts():
    contract = read_json(HERE / "CONTRACT.json")
    need(contract["schema"] == "q9-exact-c9-30-theorem-v1" and
         contract["lower_bound"] == 30 and contract["upper_bound"] == 30 and
         contract["size31_profile_partition"] == {
             "all": 1278, "slab": 1224, "fourcap": 54} and
         contract["raw_proofs_shipped"] is False and
         contract["conditional_literal_h8_corollary"] == {
             "gap": "(129-1022544*epsilon+1539648*epsilon^2)/46656",
             "maximal_small_endpoint":
                 "258/(1022544+sqrt(1044801773568))",
             "strict_reciprocal_window":
                 "epsilon=1/n for integers n>=7926"},
         "root contract")

    bindings = read_json(HERE / "BINDINGS.json")
    need(bindings["schema"] == "q9-exact-c9-30-binding-v1",
         "binding schema")
    need(bindings["capacity32_base"]["manifest_sha256"] ==
         "19cb6aacab9760b76a5c466b02bdfa554c1da5c1e7875d3fcf24e0bcbade4e4d",
         "base manifest binding")
    need(bindings["fourcap31"]["manifest_sha256"] ==
         "4eea352671abf93c9f83f5abdc3ae4512a7469f4e5d4bc6b7e78327d5166b8b7",
         "four-cap manifest binding")
    need(bindings["direct_slab31"]["source_packet_manifest_sha256"] ==
         "3325d2618ef5523c57849988ff9c1dc731ad53245a5039e714ac03df0e5baa9e",
         "direct manifest binding")
    need(bindings["capacity32_base"]["bound_facts"] == {
             "fibre_capacity": 4,
             "size30_midpoint_rows": 131,
             "size30_min_defect": 18,
             "size30_min_physical_margin": 1448,
             "peelable_saturated_slabs": 5832,
             "saturated_slab_orbits": 2,
             "slab_orbit_sizes": [2916, 2916]}, "base fact binding")
    need(bindings["fourcap31"]["profile_census"] == {
             "all_size31_profiles": 1278,
             "slab_profiles": 1224,
             "nonslab_profiles": 54,
             "normalized_nonslab_profile": "4^4 3^5"},
         "profile binding")
    need(bindings["conditional_literal_h8"] == {
             "section_bound": "30/81=10/27",
             "marker_bound":
                 "30/2916+2*(4*epsilon/3-2*epsilon^2)",
             "gap": "43/15552-(263/12)*epsilon+33*epsilon^2",
             "discriminant": 1044801773568,
             "smaller_root":
                 "258/(1022544+sqrt(1044801773568))",
             "reciprocal_inside":
                 "G(1/7926)=7651/27138877632",
             "reciprocal_outside":
                 "G(1/7925)=-65309/976753080000"},
         "conditional h8 binding")
    print("PASS_ROOT_CONTRACTS")
    return bindings


def parse_source_manifest(path):
    rows = {}
    for line_no, raw in enumerate(
            path.read_text(encoding="ascii").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64}) \*(.+)", raw)
        need(match is not None, "source manifest line %d" % line_no)
        checksum, relative = match.groups()
        need(relative not in rows and "\\" not in relative and
             ".." not in Path(relative).parts,
             "source manifest path")
        rows[relative] = checksum
    return rows


def validate_direct_projection(bindings):
    direct = bindings["direct_slab31"]
    source_manifest = DIRECT / "SOURCE_SHA256SUMS.txt"
    need(digest(source_manifest) == direct["source_packet_manifest_sha256"],
         "direct source manifest hash")
    rows = parse_source_manifest(source_manifest)
    need(len(rows) == 19, "direct source manifest census")

    copied = {
        "checker/drat-trim.c": "checker/drat-trim.c",
        "cnf/case0_direct_unary31.cnf": "cnf/case0_direct_unary31.cnf",
        "cnf/case1_direct_unary31.cnf": "cnf/case1_direct_unary31.cnf",
        "fopen_binary_shim.h": "fopen_binary_shim.h",
        "logs/case0_direct_cadical.log": "logs/case0_direct_cadical.log",
        "logs/case0_direct_drat_linux.log": "logs/case0_direct_drat_linux.log",
        "logs/case0_direct_drat_windows.log": "logs/case0_direct_drat_windows.log",
        "logs/case1_direct_cadical.log": "logs/case1_direct_cadical.log",
        "logs/case1_direct_drat_linux.log": "logs/case1_direct_drat_linux.log",
        "logs/case1_direct_drat_windows.log": "logs/case1_direct_drat_windows.log",
        "README.md": "SOURCE_README.md",
        "verify_direct_cnf.py": "verify_direct_cnf.py",
        "verify_direct_structure_stdlib.py":
            "verify_direct_structure_stdlib.py",
    }
    omitted = {
        "drat-trim-binary-windows.exe", "drat-trim-linux",
        "proof/case0_direct_unary31.drat",
        "proof/case1_direct_unary31.drat",
        "run_direct_native.ps1", "run_direct_wsl.sh",
    }
    need(set(rows) == set(copied) | omitted,
         "direct compact projection partition")
    for source_name, compact_name in copied.items():
        need(digest(DIRECT / compact_name) == rows[source_name],
             "direct copied hash " + source_name)

    cnf = direct["cnf"]
    need((DIRECT / "cnf/case0_direct_unary31.cnf").stat().st_size ==
         cnf["case0_bytes"] and rows["cnf/case0_direct_unary31.cnf"] ==
         cnf["case0_sha256"], "direct T0 CNF binding")
    need((DIRECT / "cnf/case1_direct_unary31.cnf").stat().st_size ==
         cnf["case1_bytes"] and rows["cnf/case1_direct_unary31.cnf"] ==
         cnf["case1_sha256"], "direct T1 CNF binding")
    need(rows["proof/case0_direct_unary31.drat"] ==
         direct["proofs"]["case0"]["sha256"] and
         rows["proof/case1_direct_unary31.drat"] ==
         direct["proofs"]["case1"]["sha256"],
         "direct external proof hashes")

    log_names = {
        "case0_cadical": "case0_direct_cadical.log",
        "case0_linux": "case0_direct_drat_linux.log",
        "case0_windows": "case0_direct_drat_windows.log",
        "case1_cadical": "case1_direct_cadical.log",
        "case1_linux": "case1_direct_drat_linux.log",
        "case1_windows": "case1_direct_drat_windows.log",
    }
    for key, name in log_names.items():
        need(digest(DIRECT / "logs" / name) == direct["log_sha256"][key],
             "direct log binding " + key)
    for case in (0, 1):
        cadical = (DIRECT / "logs" /
                   ("case%d_direct_cadical.log" % case)).read_text(
                       encoding="utf-8", errors="replace")
        need("\ns UNSATISFIABLE\n" in cadical and "\nc exit 20\n" in cadical,
             "CaDiCaL terminal markers case%d" % case)
        proof = direct["proofs"]["case%d" % case]
        expected = (
            "finished parsing, read %d bytes" % proof["bytes"],
            "%s clauses in core" % proof["core_clauses"].replace("/", " of "),
            "%s lemmas in core using %d resolution steps" %
                (proof["core_lemmas"].replace("/", " of "),
                 proof["resolutions"]),
            "%d RAT lemmas in core; %d redundant literals" %
                (proof["rat_lemmas"], proof["redundant_literals"]),
            "s VERIFIED",
        )
        for platform in ("linux", "windows"):
            text = (DIRECT / "logs" /
                    ("case%d_direct_drat_%s.log" % (case, platform))).read_text(
                        encoding="utf-8", errors="replace")
            for marker in expected:
                need(marker in text,
                     "direct checker marker case%d %s: %s" %
                     (case, platform, marker))
    print("PASS_DIRECT_SOURCE_PROJECTION payloads=19 copied=13 omitted=6")
    print("PASS_DIRECT_DOUBLE_VERIFIED_LOGS cases=2 platforms=2")


def replay_direct_proofs(bindings, checker, proof_dir):
    direct = bindings["direct_slab31"]
    checker_hash = digest(checker)
    need(checker_hash in direct["accepted_checker_sha256"],
         "direct checker hash is not pinned")
    for case in (0, 1):
        row = direct["proofs"]["case%d" % case]
        proof = proof_dir / row["filename"]
        need(proof.is_file() and proof.stat().st_size == row["bytes"] and
             digest(proof) == row["sha256"],
             "external direct proof hash case%d" % case)
        output = run(
            [str(checker),
             str(DIRECT / "cnf" / ("case%d_direct_unary31.cnf" % case)),
             str(proof)], HERE, required=("s VERIFIED",))
        need("finished parsing, read %d bytes" % row["bytes"] in output,
             "direct checker byte census case%d" % case)
        print("DIRECT_DRAT_VERIFIED case=%d checker_sha256=%s" %
              (case, checker_hash))
    print("PASS_EXTERNAL_DIRECT_DRAT cases=2")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fourcap-artifact-dir", type=Path)
    parser.add_argument("--direct-proof-dir", type=Path)
    parser.add_argument("--checker", type=Path)
    parser.add_argument("--proof-jobs", type=int, default=2)
    args = parser.parse_args()
    supplied = (args.fourcap_artifact_dir is not None,
                args.direct_proof_dir is not None,
                args.checker is not None)
    need(all(supplied) or not any(supplied),
         "provide all three external-proof arguments or none")
    need(1 <= args.proof_jobs <= 24, "proof-jobs range")

    before = manifest_snapshot()
    print("PASS_MANIFEST files=%d" % len(before))
    bindings = validate_contracts()
    need(digest(BASE / "SHA256SUMS.txt") ==
         bindings["capacity32_base"]["manifest_sha256"],
         "nested base manifest")
    need(digest(FOURCAP / "SHA256SUMS.txt") ==
         bindings["fourcap31"]["manifest_sha256"],
         "nested four-cap manifest")
    print("PASS_NESTED_MANIFEST_BINDINGS")

    python = [sys.executable, "-I", "-B"]
    run(python + [str(BASE / "verify_all.py")], BASE,
        tuple(bindings["capacity32_base"]["required_markers"]),
        suppress_prefixes=("H8 ", "H8_",
                           "LITERAL_COMMON_MARKER_H8_COROLLARY"))

    fourcap_command = python + [str(FOURCAP / "verify_all.py")]
    if all(supplied):
        fourcap_command += [
            "--external-proof-dir", str(args.fourcap_artifact_dir.resolve()),
            "--checker", str(args.checker.resolve()),
            "--proof-jobs", str(args.proof_jobs)]
        fourcap_markers = (
            "PASS_REGENERATED_CASE_CNFS cases=24",
            "PASS_EXTERNAL_DRAT cases=24",
            "CONCLUSION_NORMALIZED_FOUR_CAP_SIZE31_UNSAT",
            "PASS_NONMUTATION")
    else:
        fourcap_markers = tuple(bindings["fourcap31"]["required_markers"])
    run(fourcap_command, FOURCAP, fourcap_markers)

    validate_direct_projection(bindings)
    run(python + [str(DIRECT / "verify_direct_structure_stdlib.py")], DIRECT,
        ("PASS_STDLIB_FIBRE_CAPACITY best=4 size4=54",
         "PASS_STDLIB_DIRECT_CNF case=0 vars=5872 clauses=109614",
         "PASS_STDLIB_DIRECT_CNF case=1 vars=5872 clauses=109614",
         "PASS_STDLIB_DIRECT_SLAB_STRUCTURE"))
    run(python + [str(HERE / "verify_direct_cnf_stdlib.py")], HERE,
        ("PASS_STDLIB_DIRECT_CNF_REGEN case=0 vars=5872 clauses=109614",
         "PASS_STDLIB_DIRECT_CNF_REGEN case=1 vars=5872 clauses=109614",
         "PASS_STDLIB_DIRECT_CNF_REGEN_ALL cases=2"))
    run(python + [str(HERE / "verify_h8_corollary.py")], HERE,
        ("PASS_H8_C9_30_ARITHMETIC",
         "H8_RECIPROCAL_STRICT n>=7926",
         "PASS_H8_SOURCE_NONMUTATION"))

    if all(supplied):
        replay_direct_proofs(bindings, args.checker.resolve(),
                             args.direct_proof_dir.resolve())
        print("CONCLUSION_EXACT_C9_30")
    else:
        print("STRUCTURE_READY_EXTERNAL_PROOFS_REQUIRED")

    after = manifest_snapshot()
    need(after == before, "package mutated during replay")
    print("PASS_NONMUTATION")


if __name__ == "__main__":
    main()
