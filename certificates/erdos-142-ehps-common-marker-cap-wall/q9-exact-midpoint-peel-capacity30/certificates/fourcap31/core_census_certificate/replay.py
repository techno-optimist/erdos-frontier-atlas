#!/usr/bin/env python3
"""Nonmutating replay for the q=9 minimal-core census certificate."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent

EXPECTED={
    6:(324540216,14688,2916),
    7:(3477216600,129600,0),
    8:(32164253550,1476549,17496),
}


def need(condition,message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def verify_manifest():
    manifest=ROOT/"SHA256SUMS.txt"
    entries={}
    for raw in manifest.read_text(encoding="ascii").splitlines():
        expected,relative=raw.split("  ",1)
        need(relative not in entries,"duplicate manifest path")
        need("\\" not in relative and not relative.startswith("/") and ".." not in relative.split("/"),
             "nonportable manifest path")
        entries[relative]=expected
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}
    need(actual==set(entries)|{"SHA256SUMS.txt"},
         f"manifest file-set mismatch extra={sorted(actual-set(entries)-{'SHA256SUMS.txt'})} "
         f"missing={sorted(set(entries)-actual)}")
    for relative,expected in entries.items():
        need(digest(ROOT/relative)==expected,f"hash mismatch {relative}")
    return digest(manifest)


def run(command,cwd,env=None):
    result=subprocess.run(command,cwd=cwd,env=env,text=True,
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    sys.stdout.write(result.stdout)
    need(result.returncode==0,f"command failed {command!r}")
    return result.stdout


def compiler():
    found=shutil.which("g++") or shutil.which("c++")
    need(found is not None,"a C++14 compiler with OpenMP support is required")
    return found


def compile_cpp(source,output):
    run([compiler(),"-O3","-std=c++14","-fopenmp",str(source),"-o",str(output)],ROOT)


def quick_replay(threads):
    env=os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"]="1"
    env["OMP_NUM_THREADS"]=str(threads)
    out=run([sys.executable,"-I",str(ROOT/"verify_core6.py")],ROOT,env)
    need("PASS_CORE6_SEMANTICS rows=2916" in out and
         "PASS_CORE6_SINGLE_AFFINE_ORBIT" in out,"core6 semantic fingerprint")
    need((ROOT/"minimal_core7.txt").read_bytes()==b"","core7 ledger must be empty")
    out=run([sys.executable,"-I",str(ROOT/"verify_core8.py")],ROOT,env)
    need("PASS_CORE8_SEMANTICS rows=17496 deletion_checks=139968" in out and
         "orbits=1 sizes=(17496,)" in out,"core8 semantic fingerprint")
    with tempfile.TemporaryDirectory(prefix="q9_core_quick_") as tmp_raw:
        tmp=Path(tmp_raw)
        for name,tokens in (
            ("verify_core67_anchored.cpp",(
                "PASS_ANCHORED_CORE6 combinations=24040016 self=1088 minimal=216",
                "PASS_ANCHORED_CORE7 combinations=300500200 self=11200 minimal=0")),
            ("verify_core8_anchored.cpp",(
                "PASS_ANCHORED_CORE8 combinations=3176716400 self=145832 minimal=1728",
                "DOUBLE_COUNT full_self=1476549 full_minimal=17496")),
        ):
            binary=tmp/(Path(name).stem+(".exe" if os.name=="nt" else ""))
            compile_cpp(ROOT/name,binary)
            out=run([str(binary)],ROOT,env)
            need(all(token in out for token in tokens),f"anchored fingerprint {name}")
    print("PASS_QUICK_REPLAY")


def full_replay(threads):
    env=os.environ.copy()
    env["OMP_NUM_THREADS"]=str(threads)
    with tempfile.TemporaryDirectory(prefix="q9_core_full_") as tmp_raw:
        tmp=Path(tmp_raw)
        for size,(combos,self_count,minimal_count) in EXPECTED.items():
            binary=tmp/(f"enumerate_core{size}"+(".exe" if os.name=="nt" else ""))
            compile_cpp(ROOT/f"enumerate_core{size}.cpp",binary)
            out=run([str(binary)],tmp,env)
            tokens=(f"COMBINATIONS {combos}",f"SELF_CORE{size} {self_count}",
                    f"DELETION_MINIMAL_CORE{size} {minimal_count}")
            need(all(token in out for token in tokens),f"full census fingerprint size {size}")
            generated=tmp/f"minimal_core{size}.txt"
            need(generated.read_bytes()==(ROOT/generated.name).read_bytes(),
                 f"ledger byte mismatch size {size}")
            generated.unlink()
    print("PASS_FULL_REGENERATION")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--full",action="store_true",
                        help="also regenerate all 35,966,010,366 subset decisions; about ten minutes on the source host")
    parser.add_argument("--threads",type=int,default=12)
    args=parser.parse_args()
    need(args.threads>=1,"positive thread count")
    before=verify_manifest()
    print("PASS_MANIFEST",before)
    quick_replay(args.threads)
    if args.full:
        full_replay(args.threads)
    after=verify_manifest()
    need(after==before,"manifest changed during replay")
    print("PASS_NONMUTATION")
    print("PASS_Q9_MINIMAL_CORE_6_7_8_CERTIFICATE")


if __name__=="__main__":
    main()
