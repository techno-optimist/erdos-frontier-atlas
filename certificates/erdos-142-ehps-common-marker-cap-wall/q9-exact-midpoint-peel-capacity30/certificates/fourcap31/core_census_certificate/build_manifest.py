#!/usr/bin/env python3
"""Build or check the deterministic size inventory and SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
INVENTORY="FILE_SIZES.tsv"
MANIFEST="SHA256SUMS.txt"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ordinary_files():
    return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
                  if p.is_file() and p.name not in (INVENTORY,MANIFEST))


def construct():
    paths=ordinary_files()
    sizes={path:(ROOT/path).stat().st_size for path in paths}
    sizes[INVENTORY]=0
    sizes[MANIFEST]=0
    inventory=b""
    manifest=b""
    for _ in range(10):
        inventory=("bytes\tpath\n"+"".join(
            f"{sizes[path]}\t{path}\n" for path in sorted(sizes))).encode("ascii")
        payload={path:(ROOT/path).read_bytes() for path in paths}
        payload[INVENTORY]=inventory
        manifest="".join(f"{sha(payload[path])}  {path}\n"
                         for path in sorted(payload)).encode("ascii")
        updated=(len(inventory),len(manifest))
        if updated==(sizes[INVENTORY],sizes[MANIFEST]):
            return inventory,manifest
        sizes[INVENTORY],sizes[MANIFEST]=updated
    raise AssertionError("size inventory did not stabilize")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args=parser.parse_args()
    inventory,manifest=construct()
    if args.write:
        (ROOT/INVENTORY).write_bytes(inventory)
        (ROOT/MANIFEST).write_bytes(manifest)
        print("WROTE_MANIFEST")
    else:
        assert (ROOT/INVENTORY).read_bytes()==inventory
        assert (ROOT/MANIFEST).read_bytes()==manifest
        print("PASS_MANIFEST_GENERATOR")


if __name__=="__main__":
    main()
