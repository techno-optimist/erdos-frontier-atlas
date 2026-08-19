#!/usr/bin/env python3
"""Portable aggregate entrypoint for the compact q9 theorem certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def safe_relative(relative):
    pure = PurePosixPath(relative)
    return (relative == pure.as_posix() and not pure.is_absolute() and
            relative not in ("", ".") and "\\" not in relative and
            all(part not in ("", ".", "..") for part in pure.parts))


def regular_files(root):
    result = set()
    for path in root.rglob("*"):
        if path.is_file():
            need(not path.is_symlink(), "symlinked payload is forbidden")
            result.add(path.relative_to(root).as_posix())
    return result


def verify_manifest(root):
    result = {}
    raw = (root / "SHA256SUMS.txt").read_bytes()
    need(raw.endswith(b"\n") and b"\r" not in raw,
         "manifest must be LF-terminated ASCII")
    lines = raw.decode("ascii").splitlines()
    for line in lines:
        need(len(line) >= 67 and line[64:66] == " *",
             "malformed manifest line")
        expected = line[:64]
        need(all(char in "0123456789abcdef" for char in expected),
             "nonhex manifest digest")
        relative = line[66:]
        need(safe_relative(relative), "unsafe manifest path")
        need(relative != "SHA256SUMS.txt", "manifest cannot hash itself")
        need(relative not in result, "duplicate manifest path")
        path = root.joinpath(*relative.split("/"))
        need(path.is_file(), "missing manifest file: %s" % relative)
        actual = sha256(path)
        need(actual == expected, "manifest mismatch: %s" % relative)
        result[relative] = actual
    need(result, "empty manifest")
    need(list(result) == sorted(result), "manifest paths are not sorted")
    need(regular_files(root) == set(result) | {"SHA256SUMS.txt"},
         "unlisted or overlisted regular file")
    return result


def verify_inventory(root):
    raw = (root / "FILE_SIZES.tsv").read_bytes()
    need(raw.endswith(b"\n") and b"\r" not in raw,
         "inventory must be LF-terminated UTF-8")
    lines = raw.decode("utf-8").splitlines()
    need(lines and lines[0] == "bytes\tpath", "bad inventory header")
    result = {}
    for line in lines[1:]:
        fields = line.split("\t")
        need(len(fields) == 2, "bad inventory row")
        size_text, relative = fields
        need(size_text.isdigit() and str(int(size_text)) == size_text,
             "noncanonical inventory size")
        need(safe_relative(relative), "unsafe inventory path")
        need(relative not in result, "duplicate inventory path")
        result[relative] = int(size_text)
    need(list(result) == sorted(result), "inventory paths are not sorted")
    actual = regular_files(root)
    need(set(result) == actual, "inventory does not list every regular file")
    for relative, expected in result.items():
        need((root.joinpath(*relative.split("/")).stat().st_size == expected),
             "inventory size mismatch: %s" % relative)
    return result


def no_duplicate_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: %s" % key)
        result[key] = value
    return result


EXPECTED_BINDINGS = {
    "date": "2026-08-19",
    "scope": ("path-free provenance bindings only; combined replay is "
              "self-contained"),
    "template0_packet": {
        "archive_label": ("q9_q27_frontier_attack_20260819/"
                          "template0_certificate"),
        "manifest_sha256":
            "eb932b89539793f564bee3c8ba03ab56b5d33c71a08afcd16f8e816362431794",
        "copied_files": {
            "blockers.txt":
                "6616ff7d8262b7e5f597b606df09e71b60bb9edd34f43cfbd2a9d710fba58fa8",
            "template0.cnf":
                "e09943895dbfceb742d5addfd0263a433d6f7646c662d04e0e48fb25aacba456",
        },
    },
    "template1_packet": {
        "archive_label": ("q9_q27_frontier_attack_20260819/"
                          "template1_certificate"),
        "manifest_sha256":
            "54bf3b2ca4d5c93330b26be39e0c020c6fa0671441dd85be95f2668458250df6",
        "copied_files": {
            "blocker_reps.json":
                "f11ea7553f55ca5020c23ad949cd6d1e8330fd422e5af25d185d5262cd3d3335",
            "template1.cnf":
                "4100d2ab7501395107d4b23a746f741e4c403f74d17c644fcfb620ac0a0e1681",
        },
        "generated_transparent_ledger_sha256":
            "4938f64aaac275f62eca702af1fb310ff9e7bf3448c460d1f32c250cd9ac75c6",
        "slab_orbit_verifier_sha256":
            "01e2c0918e3e155846b67d137a0284876401562ea29c81774897d038f216718b",
    },
    "size30_packet": {
        "archive_label": ("q9_capacity32_independent_20260819/"
                          "boundary_exact"),
        "manifest_sha256":
            "7a9dc265e802cc78e3b870cb82cf8209c453669bba83c232465641624ec6b76a",
        "verifier_sha256":
            "9381da53cd746b233bbf8f2433dc48905f11ddbf52c599849dc3fdb39775e207",
    },
}


def verify_source_bindings(root, manifest):
    bindings = json.loads((root / "SOURCE_BINDINGS.json").read_text("utf-8"),
                          object_pairs_hook=no_duplicate_object)
    need(bindings == EXPECTED_BINDINGS, "unexpected source-binding schema/value")
    need(manifest["data/template0_blockers.txt"] ==
         bindings["template0_packet"]["copied_files"]["blockers.txt"],
         "template0 blocker provenance mismatch")
    need(manifest["data/template0.cnf"] ==
         bindings["template0_packet"]["copied_files"]["template0.cnf"],
         "template0 CNF provenance mismatch")
    need(manifest["data/template1_blocker_reps.json"] ==
         bindings["template1_packet"]["copied_files"]["blocker_reps.json"],
         "template1 reps provenance mismatch")
    need(manifest["data/template1.cnf"] ==
         bindings["template1_packet"]["copied_files"]["template1.cnf"],
         "template1 CNF provenance mismatch")
    need(manifest["data/template1_blockers.txt"] ==
         bindings["template1_packet"]["generated_transparent_ledger_sha256"],
         "template1 generated-ledger provenance mismatch")


def run(command, root, expected=0, quiet=False):
    kwargs = {"cwd": str(root), "text": True}
    if quiet:
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    completed = subprocess.run(command, **kwargs)
    need(completed.returncode == expected,
         "command returned %d, expected %d: %s\n%s\n%s" %
         (completed.returncode, expected, command,
          completed.stdout if quiet else "",
          completed.stderr if quiet else ""))
    return completed


def find_compiler():
    for candidate in ("g++", "clang++", "c++"):
        path = shutil.which(candidate)
        if path:
            return path
    raise AssertionError("no C++14 compiler found (tried g++, clang++, c++)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive-template0", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent

    before = verify_manifest(root)
    before_sizes = verify_inventory(root)
    print("PASS_HASH_MANIFEST_INITIAL", flush=True)
    verify_source_bindings(root, before)
    print("PASS_SOURCE_BINDINGS_JSON", flush=True)

    python = [sys.executable, "-I", "-B"]
    run(python+[str(root / "verify_finite_geometry.py")], root)
    semantic = python+[str(root / "verify_blocker_semantics.py")]
    if args.exhaustive_template0:
        semantic.append("--exhaustive-template0")
    run(semantic, root)
    run(python+[str(root / "generate_template1_ledger.py")], root)

    compiler = find_compiler()
    with tempfile.TemporaryDirectory(prefix="q9_combined_") as temporary:
        temp = Path(temporary)
        binary = temp / ("compact_fibre_verify.exe" if os.name == "nt"
                         else "compact_fibre_verify")
        run([compiler, "-O3", "-std=c++14", "-Wall", "-Wextra", "-pedantic",
             "-o", str(binary), str(root / "compact_fibre_verify.cpp")], root)
        run([str(binary), str(root), "0"], root)
        run([str(binary), str(root), "1"], root)
        run([str(binary), str(root), "2"], root, expected=2, quiet=True)
        run([str(binary), str(root)], root, expected=2, quiet=True)

        bad_root = temp / "bad_ledger"
        bad_data = bad_root / "data"
        bad_data.mkdir(parents=True)
        bad_ledger = bad_data / "template0_blockers.txt"
        shutil.copyfile(root / "data" / "template0_blockers.txt", bad_ledger)
        with bad_ledger.open("ab") as stream:
            stream.write(b"9,0\n")
        run([str(binary), str(bad_root), "0"], root, expected=2, quiet=True)
        print("PASS_NEGATIVE_CONTROLS bad_argc bad_index malformed_ledger",
              flush=True)

    after = verify_manifest(root)
    after_sizes = verify_inventory(root)
    need(after == before, "manifested source/data mutation")
    need(after_sizes == before_sizes, "inventory/source mutation")
    need(not (root / "__pycache__").exists(), "unexpected __pycache__")
    print("PASS_HASH_MANIFEST_FINAL", flush=True)
    print("PASS_Q9_CAPACITY_THEOREM 30<=C9<=31", flush=True)
    print("LITERAL_COMMON_MARKER_H8_COROLLARY "
          "model=one_common_marker pointwise_physical epsilon=1/n n>=1022543",
          flush=True)
    print("PASS_Q9_COMBINED_PACKAGE", flush=True)


if __name__ == "__main__":
    main()
