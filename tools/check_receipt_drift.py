#!/usr/bin/env python3
"""Gate: a certificate's committed receipt must SURVIVE its own verifier.

THE DEFECT THIS CATCHES
-----------------------
Most certificate verifiers in this repo both CHECK a witness and EMIT their
receipt on the same code path. That makes replay self-erasing: if the committed
receipt disagrees with what the verifier now computes, the verifier *overwrites*
the disagreement and exits 0. The evidence silently conforms to the code.

Observed 2026-07-21: certificates/fibonacci-macro-residual committed
N11_L7_S7_MACRO_WITNESS_RESULT.json with "vertex_count": 117 (commit fe3bd66);
replaying its own committed verifier deterministically produces 136, with the
verifier unchanged between those commits. Nothing caught it -- the verifier
rewrote the receipt and exited 0. A static scan finds ~47 of 75 scripts under
certificates/ writing a committed receipt in their own directory, concentrated
in fibonacci-macro-residual and jc-family-fences, so this is systemic rather
than one bad lane. (An earlier draft of this docstring also named erdos-552 and
erdos-552-f39; that was wrong -- both verify.py are print-only and write no
receipt. Corrected after an independent ablation.)

WHAT IT DOES
------------
For each verifier, snapshot its directory's tracked receipts, run the verifier,
then diff. Drift is classified:

  SUBSTANTIVE  a claim-bearing field changed (anything not in COSMETIC_KEYS).
               This is the N11 defect: committed evidence disagrees with the
               code that is supposed to certify it. ALWAYS FAILS.

  COSMETIC     only timing/provenance fields changed (elapsed_sec, timestamps).
               Hygiene debt, not a correctness bug: reported, not fatal, so the
               gate is adoptable today without first rewriting 42 scripts.

Exit 0 iff no SUBSTANTIVE drift. Cosmetic drift is listed so the debt is visible
and shrinking rather than invisible and growing.

Usage:
  python3 tools/check_receipt_drift.py                  # changed dirs vs origin/main
  python3 tools/check_receipt_drift.py --all            # every certificate dir
  python3 tools/check_receipt_drift.py --dir certificates/foo
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Fields whose change on replay is provenance/timing noise, not a claim.
COSMETIC_KEYS = {
    "elapsed_sec", "elapsed", "duration", "duration_sec", "runtime_sec",
    "timestamp", "generated", "generated_at", "created_at", "date", "ran_at",
    "wall_sec", "seconds",
}
# fk-square/verify.py legitimately runs ~2min (exhaustive D(1..9) recompute);
# a 120s budget made it permanently INCONCLUSIVE, i.e. a lane that can never
# be green. Budget must exceed the slowest honest verifier.
PER_SCRIPT_TIMEOUT = 420


def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, capture_output=True, text=True)


def tracked_files():
    return set(sh(["git", "ls-files"]).stdout.split())


def changed_cert_dirs(base):
    out = sh(["git", "diff", "--name-only", f"{base}...HEAD"]).stdout.split()
    dirs = {str(Path(p).parent) for p in out if p.startswith("certificates/")}
    return sorted(d for d in dirs if (ROOT / d).is_dir())


def verifiers_in(d):
    return sorted(p for p in (ROOT / d).glob("*.py")
                  if p.name.startswith(("verify", "check")))


def json_drift(path):
    """Return (substantive_keys, cosmetic_keys) for a modified tracked JSON."""
    before = sh(["git", "show", f"HEAD:{path}"]).stdout
    after = (ROOT / path).read_text()
    try:
        b, a = json.loads(before), json.loads(after)
    except Exception:
        return (["<unparseable JSON: treat as substantive>"], [])
    sub, cos = [], []

    def walk(x, y, trail=""):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in set(x) | set(y):
                walk(x.get(k), y.get(k), f"{trail}.{k}" if trail else k)
        elif x != y:
            leaf = trail.split(".")[-1]
            # Cosmetic only if the NAME is a known timing/provenance key AND both
            # values look like timings/stamps. A claim field that happens to be
            # called "seconds" or "date" must not get a free pass on its value.
            # Cosmetic ONLY at the top level of the receipt and only for a known
            # timing key. Independent ablation showed a value-shape test cannot
            # separate "elapsed_sec 0.137 -> 0.032" from "seconds 42 -> 999":
            # both are numeric. So we do not try -- we restrict by POSITION
            # instead. A nested `proof.seconds` is a claim and stays substantive.
            timingish = all(isinstance(v, (int, float)) for v in (x, y)) or \
                all(isinstance(v, str) and any(c.isdigit() for c in v) for v in (x, y))
            is_cos = leaf in COSMETIC_KEYS and "." not in trail and timingish
            (cos if is_cos else sub).append(trail)
    walk(b, a)
    return sub, cos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dir")
    ap.add_argument("--base", default="origin/main")
    args = ap.parse_args()

    # Only TRACKED modifications block attribution; untracked files (including
    # this gate before it is committed, and build artifacts) are irrelevant.
    if sh(["git", "status", "--porcelain", "--untracked-files=no"]).stdout.strip():
        print("receipt-drift: refusing to run with modified tracked files "
              "(cannot attribute drift to the verifier)", file=sys.stderr)
        return 2

    if args.dir:
        # A typo'd path must never read as green.
        if not (ROOT / args.dir).is_dir():
            print(f"receipt-drift: --dir {args.dir!r} does not exist", file=sys.stderr)
            return 2
        dirs = [args.dir]
    elif args.all:
        dirs = sorted(str(p.relative_to(ROOT))
                      for p in (ROOT / "certificates").iterdir() if p.is_dir())
    else:
        dirs = changed_cert_dirs(args.base)

    if not dirs:
        print("receipt-drift: no certificate directories in scope; nothing to check")
        return 0

    tracked = tracked_files()
    substantive, cosmetic, ran, failed_runs, uncovered = [], [], 0, [], []
    touched = set()  # tracked receipts a verifier actually rewrote (coverage)

    for d in dirs:
        vs = verifiers_in(d)
        # A directory holding committed .json receipts but exposing no runnable
        # verifier cannot be checked at all. Reporting OK there is a false green.
        if not vs and any(str(p.relative_to(ROOT)) in tracked
                          for p in (ROOT / d).glob("*.json")):
            uncovered.append(d)
        for v in vs:
            ran += 1
            # mtime snapshot: a verifier that rewrites a receipt BYTE-IDENTICALLY
            # is invisible to `git diff`, but it did re-derive it. Coverage must
            # count those, or an honest lane looks unchecked.
            before_mt = {p: p.stat().st_mtime
                         for p in (ROOT / d).glob("*.json")
                         if str(p.relative_to(ROOT)) in tracked}
            try:
                p = subprocess.run([sys.executable, "-I", v.name], cwd=v.parent,
                                   capture_output=True, text=True,
                                   timeout=PER_SCRIPT_TIMEOUT)
                if p.returncode != 0:
                    failed_runs.append(f"{d}/{v.name} (exit {p.returncode})")
            except subprocess.TimeoutExpired:
                failed_runs.append(f"{d}/{v.name} (timeout)")
            for p, mt in before_mt.items():
                try:
                    if p.stat().st_mtime != mt:
                        touched.add(str(p.relative_to(ROOT)))
                except FileNotFoundError:
                    touched.add(str(p.relative_to(ROOT)))
            # Classify any TRACKED file this run modified. Use `git diff
            # --name-only`, which lists exactly the tracked-and-modified paths.
            # (An earlier version parsed `git status --porcelain` with
            # partition(" "); porcelain prefixes unstaged edits with a LEADING
            # space, so every path came back as "M <path>", matched nothing, and
            # the gate silently caught nothing. It was inert. Do not reintroduce.)
            for path in sh(["git", "diff", "--name-only"]).stdout.split():
                if path.endswith(".json"):
                    sub, cos = json_drift(path)
                    if sub:
                        substantive.append((path, v.name, sub))
                    elif cos:
                        cosmetic.append((path, v.name, cos))
                else:
                    substantive.append((path, v.name, ["<non-JSON receipt rewritten>"]))
            # Restore for the next verifier. NOTE this reverts the whole worktree
            # to HEAD, so an UNCOMMITTED verifier fix cannot be validated by this
            # gate -- commit the fix first, then re-run. (The dirty-tree guard
            # above means we can only ever start from a clean tree, so this is
            # safe in sanctioned use.)
            sh(["git", "checkout", "--", "."])

    # Coverage: a receipt no verifier ever rewrites was never re-derived, so this
    # gate says nothing about it. Silence there is not evidence, and it is the
    # largest remaining blind spot -- report it explicitly.
    rederived = {p for p, _, _ in substantive} | {p for p, _, _ in cosmetic} | touched
    total_receipts = 0
    for d in dirs:
        for p in (ROOT / d).glob("*.json"):
            if str(p.relative_to(ROOT)) in tracked:
                total_receipts += 1
    print(f"receipt-drift: ran {ran} verifier(s) across {len(dirs)} dir(s)")
    if total_receipts:
        print(f"  coverage: {len(rederived)}/{total_receipts} committed receipt(s) "
              f"re-derived by a verifier "
              f"({total_receipts - len(rederived)} never re-derived -- unchecked)")
    if uncovered:
        print(f"  NOT CHECKED: {len(uncovered)} dir(s) hold committed .json receipts "
              "but expose no verify*/check* script -- their receipts are unverifiable "
              "by this gate:")
        for d in uncovered:
            print(f"    - {d}")
    if failed_runs:
        print("  verifiers that did not exit 0 / timed out:")
        for f in failed_runs:
            print(f"    - {f}")
    if cosmetic:
        print(f"  COSMETIC drift (timing/provenance only) in {len(cosmetic)} receipt(s) "
              "-- hygiene debt, not fatal:")
        for path, v, keys in cosmetic[:10]:
            print(f"    - {path} <- {v}: {', '.join(keys[:4])}")
    if substantive:
        print(f"\nreceipt-drift FAILED: {len(substantive)} committed receipt(s) "
              "disagree with their own verifier")
        for path, v, keys in substantive:
            print(f"  - {path}")
            print(f"      rewritten by {v}; claim fields changed: {', '.join(keys[:6])}")
        print("\nA receipt that changes when its verifier runs is not evidence: the")
        print("verifier is overwriting the disagreement instead of reporting it.")
        print("Fix the receipt (commit what the verifier actually produces), or")
        print("split the script so checking never writes (emit behind --emit).")
        return 1

    if failed_runs:
        # A verifier that cannot complete has not certified its receipt. Green
        # here would read as "checked and fine" when nothing was checked.
        print(f"\nreceipt-drift INCONCLUSIVE: {len(failed_runs)} verifier(s) did not "
              "complete, so their receipts were never re-derived.")
        return 1
    print("receipt-drift OK: no committed receipt disagrees with its verifier")
    if uncovered:
        print("  (note: the uncovered dirs above were not checked at all)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
