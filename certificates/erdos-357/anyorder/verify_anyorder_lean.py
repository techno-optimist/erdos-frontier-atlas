#!/usr/bin/env python3
"""Erdos #357, any order: replay the Lean audit of a(k) > (3/2 + 10^-10) k for k >= 10^22.

The claim (OEIS A364153, sequences in any order): if k distinct integers from 1..N, in a
fixed order, have all consecutive-block sums distinct and k >= 10^22, then
N > (3/2 + 10^-10) k.  The argument and the Lean formalization are by Kevin Russell with
GPT Astra; Ford audited them (erdos_357_anyorder_math_audit_20261102.txt and
erdos_357_anyorder_lean_audit_20261102.txt).  AI-only review, not refereed.

Default (fast, does NOT certify): dependency-free, a few seconds.
  * the zip, the two receipts and the five audit files have their pinned sha256;
  * every file of the zip equals, byte for byte, the unpacked copy in lean/;
  * the 15 source hashes printed in the Lean receipt match lean/;
  * the theorem headers of Challenge.lean and Solution.lean are identical;
  * escape-hatch grep: no sorry/admit (outside Challenge.lean), axiom, native_decide,
    implemented_by, unsafe, opaque, csimp, extern, ofReduceBool, set_option, macro, elab,
    syntax, notation, instance, attribute (except @[simp]) in the 12 project .lean files;
  * toolchain v4.33.1 and Mathlib 0df444a3 are pinned in lean-toolchain, lakefile, manifest;
  * planted failures are rejected (see PLANTED below).

--full (certifies): additionally copies lean/ and lean_audit/ to a temporary directory
OUTSIDE the repository, runs `lake exe cache get` and `lake build` with the pinned
toolchain (needs elan and network for the Mathlib cache), then `lake env lean` on the
audit files, and requires every printed axiom list to be exactly
[propext, Classical.choice, Quot.sound], CrossCheck and Witness to elaborate (rc 0), and
the pp.all statements of Challenge and Solution to agree.  This is the build + axiom
part of the Lean audit; the independent-kernel runs (nanoda, con-ron, leanchecker
--fresh) are recorded in the Lean receipt and are not re-run here.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAN = HERE / "lean"
AUDIT = HERE / "lean_audit"
ZIP = HERE / "erdos357_anyorder_lean_a1d0674.zip"
LEAN_RECEIPT = HERE / "erdos_357_anyorder_lean_audit_20261102.txt"
MATH_RECEIPT = HERE / "erdos_357_anyorder_math_audit_20261102.txt"

PINS = {
    ZIP.name: "52a688a1a16a7b0c9e133cd1f61a3562e8c101740d440dbcd8b795410aa7602f",
    LEAN_RECEIPT.name: "e0eba9c3fbbd1f6da854199db3460f6bbc6bb17034253f3f2eb4d259a804348a",
}
AUDIT_PINS = {
    "AuditAxioms.lean": "0100b630cd837e1e97901207f41eaaecc9f7705eb18ebb173310d34c70eced99",
    "CrossCheck.lean": "92657f1905d882ae89e95ef62eb35b7dbb9c704e395704ca4622af52c8d940ed",
    "IdChallenge.lean": "3df6900f7ef1d87738e3a269901ab761c0b1ad1ab5494549ef476b45d889b503",
    "IdSolution.lean": "78f2f95e84ea06c0c83d9a396fcdaab7b5a9b137e879da31fbbb17287444fb91",
    "Witness.lean": "be6615933ac80817ba7182e68e27d45531bf71ab97d6b92eb1529e5547c45acd",
}
TOOLCHAIN = "leanprover/lean4:v4.33.1"
MATHLIB = "0df444a360eaa60ab8c11dca51a86af692955474"
THEOREM = "erdos357_any_order_improvement"
STD_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
DECLS = [THEOREM] + ["Erdos357." + n for n in (
    "admissible_extend", "step1_span", "step2_few_small", "step3_packing_stability",
    "step4_test_function", "step5_negative_correlations", "step6_nine_term_contradiction")]
FORBIDDEN = re.compile(
    r"\b(sorry|admit|axiom|native_decide|implemented_by|unsafe|opaque|extern|ofReduceBool|"
    r"set_option|macro|elab|syntax|notation|instance|run_cmd|unseal)\b|@\[csimp\]|#eval")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def header(text: str) -> str:
    start = text.index("theorem " + THEOREM)
    return text[start:text.index(" := by", start)]


def zip_members(data: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return {i.filename: z.read(i) for i in z.infolist() if not i.is_dir()}


def tree(root: Path) -> dict[str, bytes]:
    return {"lean/" + p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


def receipt_hashes(text: str) -> list[str]:
    sec = text[text.index("1. PINNED SOURCE"):text.index("2. BUILD")]
    return re.findall(r"\b[0-9a-f]{64}\b", sec)


def project_sources(files: dict[str, bytes]) -> dict[str, str]:
    return {k: v.decode() for k, v in files.items() if k.endswith(".lean")}


def escape_hatches(srcs: dict[str, str]) -> list[str]:
    hits = []
    for name, text in srcs.items():
        body = re.sub(r"/-.*?-/", "", text, flags=re.S)
        body = re.sub(r"--[^\n]*", "", body)
        for m in FORBIDDEN.finditer(body):
            if name == "lean/Challenge.lean" and m.group(0) == "sorry":
                continue
            hits.append(f"{name}: {m.group(0)}")
        for m in re.finditer(r"@\[([^\]]*)\]", body):
            if m.group(1).strip() != "simp":
                hits.append(f"{name}: @[{m.group(1)}]")
    return hits


def check_static(files: dict[str, bytes], zipbytes: bytes, receipt: str) -> list[str]:
    """Return a list of problems; empty means the static audit passes."""
    errs = []
    if sha(zipbytes) != PINS[ZIP.name]:
        errs.append("zip sha256 differs from the pin")
    try:
        members = zip_members(zipbytes)
    except zipfile.BadZipFile:
        return errs + ["zip does not open"]
    if members != files:
        diff = sorted(set(members) ^ set(files)) or sorted(
            k for k in members if members[k] != files.get(k))
        errs.append(f"lean/ differs from the zip: {diff[:5]}")
    pinned = receipt_hashes(receipt)
    want = [sha(files.get("lean/" + n, b"")) for n in (
        "Challenge.lean", "Solution.lean", "AxiomAudit.lean") + tuple(
        "Erdos357/" + m + ".lean" for m in ("Basic", "Packing", "Span", "SmallEntries",
                                             "Stability", "Transport", "Empirical",
                                             "Correlation", "Gram")) + (
        "lakefile.toml", "lake-manifest.json", "lean-toolchain")]
    if PINS[ZIP.name] not in pinned or pinned[-15:] != want:
        errs.append("source hashes do not match the Lean receipt section 1")
    srcs = project_sources(files)
    if len(srcs) != 12:
        errs.append(f"expected 12 project .lean files, found {len(srcs)}")
    try:
        if header(srcs["lean/Challenge.lean"]) != header(srcs["lean/Solution.lean"]):
            errs.append("Challenge and Solution theorem headers differ")
    except (KeyError, ValueError):
        errs.append("theorem header missing")
    if len(re.findall(r"\bsorry\b", srcs.get("lean/Challenge.lean", ""))) != 1:
        errs.append("Challenge.lean should hold exactly one sorry")
    if any(re.search(r"^import\s+.*\bChallenge\b", t, re.M) for t in srcs.values()):
        errs.append("something imports Challenge")
    errs += [f"escape hatch {h}" for h in escape_hatches(srcs)]
    imports = {m for t in srcs.values() for m in re.findall(r"^import\s+(\S+)", t, re.M)}
    if not all(i == "Mathlib" or i.startswith("Erdos357.") or i == "Solution" for i in imports):
        errs.append(f"unexpected imports {sorted(imports)}")
    if files.get("lean/lean-toolchain", b"").decode().strip() != TOOLCHAIN:
        errs.append("toolchain pin")
    if f'rev = "{MATHLIB}"' not in files.get("lean/lakefile.toml", b"").decode():
        errs.append("lakefile Mathlib pin")
    try:
        man = json.loads(files.get("lean/lake-manifest.json", b"{}"))
        if next(p for p in man["packages"] if p["name"] == "mathlib")["rev"] != MATHLIB:
            errs.append("manifest Mathlib pin")
    except (KeyError, StopIteration, json.JSONDecodeError):
        errs.append("manifest unreadable")
    if "(3/2 + 10^-10)k for k >= 10^22" not in receipt or "PASS." not in receipt:
        errs.append("Lean receipt verdict missing")
    return errs


def parse_axioms(out: str) -> dict[str, list[str]]:
    res = {}
    for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", out):
        res[m.group(1)] = [a.strip() for a in m.group(2).split(",") if a.strip()]
    for m in re.finditer(r"'([^']+)' does not depend on any axioms", out):
        res[m.group(1)] = []
    return res


def axioms_ok(out: str, decls: list[str]) -> bool:
    got = parse_axioms(out)
    return all(d in got and set(got[d]) <= set(STD_AXIOMS) for d in decls) and \
        "sorryAx" not in out


def planted(files, zipbytes, receipt) -> int:
    n = 0
    flipped = bytearray(zipbytes); flipped[len(flipped) // 2] ^= 1
    cases = [("zip with one flipped bit", files, bytes(flipped), receipt)]
    for label, path, old, new in [
        ("sorry inserted in Solution.lean", "lean/Solution.lean", "  by_contra hn", "  sorry"),
        ("axiom declared in Basic.lean", "lean/Erdos357/Basic.lean", "namespace Erdos357",
         "namespace Erdos357\naxiom cheat : False"),
        ("Challenge bound weakened to 10 ^ 2", "lean/Challenge.lean", "10 ^ 22", "10 ^ 2"),
        ("native_decide in Gram.lean", "lean/Erdos357/Gram.lean", "namespace Erdos357",
         "namespace Erdos357\nexample : 1 = 1 := by native_decide"),
    ]:
        f2 = dict(files)
        t = f2[path].decode()
        if old not in t:
            fail(f"planted-failure anchor missing in {path}")
        f2[path] = t.replace(old, new, 1).encode()
        cases.append((label, f2, zipbytes, receipt))
    for label, f, z, r in cases:
        if not check_static(f, z, r):
            fail(f"planted failure accepted: {label}")
        n += 1
    good = "'X' depends on axioms: [propext, Classical.choice, Quot.sound]"
    if not axioms_ok(good, ["X"]):
        fail("axiom parser rejects the standard three")
    for bad in ["'X' depends on axioms: [propext, sorryAx, Quot.sound]",
                "'X' depends on axioms: [propext, Classical.choice, Quot.sound, Erdos357.cheat]",
                "'Y' depends on axioms: [propext]"]:
        if axioms_ok(bad, ["X"]):
            fail(f"axiom parser accepted {bad!r}")
        n += 1
    return n


def run(cmd, cwd, timeout):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def full_build() -> None:
    lake = shutil.which("lake") or str(Path.home() / ".elan/bin/lake")
    if not Path(lake).exists():
        fail("--full needs elan/lake on PATH")
    with tempfile.TemporaryDirectory(prefix="erdos357-anyorder-") as td:
        work = Path(td) / "lean"
        shutil.copytree(LEAN, work)
        for f in AUDIT.glob("*.lean"):
            shutil.copy(f, work / f.name)
        for cmd, t in ((["lake", "exe", "cache", "get"], 7200), (["lake", "build"], 14400)):
            rc, out = run([lake] + cmd[1:], work, t)
            print(f"{' '.join(cmd)}: rc {rc}")
            if rc != 0 or re.search(r"(?m)^(error|warning)|declaration uses 'sorry'", out):
                fail(f"{' '.join(cmd)} failed:\n{out[-2000:]}")
        outs = {}
        for name in ("AuditAxioms", "CrossCheck", "Witness", "IdChallenge", "IdSolution"):
            rc, out = run([lake, "env", "lean", f"{name}.lean"], work, 7200)
            print(f"lake env lean {name}.lean: rc {rc}")
            if rc != 0:
                fail(f"{name}.lean failed:\n{out[-2000:]}")
            outs[name] = out
        if not axioms_ok(outs["AuditAxioms"], DECLS):
            fail(f"axioms beyond the standard three:\n{outs['AuditAxioms']}")
        if not axioms_ok(outs["CrossCheck"], ["challenge_statement_copy"]):
            fail("CrossCheck axioms")
        wit = parse_axioms(outs["Witness"])
        if "sorryAx" in outs["Witness"] or any(set(v) - set(STD_AXIOMS) for v in wit.values()):
            fail("Witness axioms")

        def stmt(o):
            return "\n".join(l for l in o.splitlines()
                             if "declaration uses 'sorry'" not in l and "warning" not in l).strip()
        if stmt(outs["IdChallenge"]) != stmt(outs["IdSolution"]):
            fail("pp.all statements of Challenge and Solution differ")
        print("full: lake build clean; 8 declarations on [propext, Classical.choice, Quot.sound]; "
              "CrossCheck, Witness and pp.all statement match pass")


def main() -> None:
    full = "--full" in sys.argv[1:]
    zipbytes = ZIP.read_bytes()
    receipt_bytes = LEAN_RECEIPT.read_bytes()
    if sha(receipt_bytes) != PINS[LEAN_RECEIPT.name]:
        fail("Lean receipt sha256 differs from the pin")
    receipt = receipt_bytes.decode()
    for name, digest in AUDIT_PINS.items():
        if sha((AUDIT / name).read_bytes()) != digest or digest not in receipt:
            fail(f"audit file {name} does not match the Lean receipt")
    math = MATH_RECEIPT.read_text()
    if PINS[ZIP.name] not in math or LEAN_RECEIPT.name not in math:
        fail("math receipt does not point at the Lean zip and receipt")
    files = tree(LEAN)
    errs = check_static(files, zipbytes, receipt)
    if errs:
        fail("; ".join(errs))
    print(f"static: zip {PINS[ZIP.name][:12]} == lean/ ({len(files)} files); 15 receipt hashes, "
          "headers identical, no escape hatches, pins v4.33.1 / mathlib 0df444a3")
    n = planted(files, zipbytes, receipt)
    print(f"planted failures rejected: {n}")
    print(json.dumps({"receipt_consistent_erdos357_anyorder": True}, separators=(",", ":")))
    if full:
        full_build()
        print(json.dumps({"verified_erdos357_anyorder_lean": True}, separators=(",", ":")))
    print("all checks passed")


if __name__ == "__main__":
    main()
