#!/usr/bin/env python3
"""The briefcase: proved reductions as executable operators, and the residuals they leave.

  python3 tools/briefcase.py row N I              decide the whole row (n, i) of Erdős #699
  python3 tools/briefcase.py anatomy N I          the positional table behind that decision
  python3 tools/briefcase.py certify N I [-o F]   a JSON certificate that the row holds
  python3 tools/briefcase.py verify F             recheck a certificate independently
  python3 tools/briefcase.py residuals            the residual ledger (atlas/residuals.json)
  python3 tools/briefcase.py residual ID [N]      one residual; with N, test membership and decide
  python3 tools/briefcase.py factor N             exact factorization (proven below 3.3e24)

N may be written as an expression of integers, +, -, *, ** and parentheses (e.g. 2**64+1).
Nothing here reads or writes a status. See tools/briefcaselib/ for the operators and their
theorems.
"""
import argparse
import ast
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from briefcaselib import nt, p699, residuals  # noqa: E402


def integer(text):
    """Parse an integer expression safely: literals, + - * ** // and parentheses only."""
    node = ast.parse(text.replace("^", "**"), mode="eval").body

    def ev(x):
        if isinstance(x, ast.Constant) and isinstance(x.value, int):
            return x.value
        if isinstance(x, ast.UnaryOp) and isinstance(x.op, (ast.USub, ast.UAdd)):
            v = ev(x.operand)
            return -v if isinstance(x.op, ast.USub) else v
        if isinstance(x, ast.BinOp) and isinstance(x.op, (ast.Add, ast.Sub, ast.Mult, ast.Pow, ast.FloorDiv)):
            a, b = ev(x.left), ev(x.right)
            if isinstance(x.op, ast.Pow):
                if b < 0 or b > 4096 or abs(a) > 2 ** 64:
                    raise ValueError("exponent out of range")
                return a ** b
            return {ast.Add: a + b, ast.Sub: a - b, ast.Mult: a * b}.get(type(x.op)) if not isinstance(
                x.op, ast.FloorDiv) else a // b
        raise ValueError(f"not an integer expression: {text}")

    value = ev(node)
    if value < 1:
        raise ValueError("need a positive integer")
    return value


def cmd_row(a):
    rep = p699.row(integer(a.n), a.i)
    print(f"row (n, i) = ({rep['n']}, {rep['i']})")
    for s in rep["stages"]:
        print(f"  - {s}")
    for s in rep["survivors"]:
        print(f"  survivor j = {s['j']}: common prime {s['common_prime']}")
    print("holds: every j in (i, n/2] has a common prime p >= i" if rep["holds"]
          else "COUNTEREXAMPLE — no common prime for some j")
    return 0 if rep["holds"] else 1


def cmd_anatomy(a):
    n, i = integer(a.n), a.i
    print(f"n = {n}, i = {i}: n - t = S_t * R_t (R_t: prime powers of primes > i, or i^e with e >= 2)")
    print(f"{'t':>3}  {'S_t':>22}  {'R_t = blocks M (j mod M must be <= t)':<}")
    for t in range(i):
        fac = nt.factor(n - t)
        S, R = nt.smooth_rough(n - t, i, fac)
        blk = [f"{p}^{e}" if e > 1 else str(p) for p, e in fac.items() if p > i or (p == i and e >= 2)]
        print(f"{t:>3}  {S:>22}  {' * '.join(blk) or '1'}")
    rep = p699.row(n, i)
    print()
    for s in rep["stages"]:
        print(f"  - {s}")
    if rep.get("candidates"):
        print(f"  candidates m (j = R_0 m): {rep['candidates'][:20]}{' ...' if len(rep['candidates']) > 20 else ''}")
    print("holds" if rep["holds"] else "COUNTEREXAMPLE")
    return 0 if rep["holds"] else 1


def cmd_certify(a):
    cert = p699.certify_row(integer(a.n), a.i)
    text = json.dumps(cert, indent=1) + "\n"
    if a.o:
        pathlib.Path(a.o).write_text(text, encoding="utf-8")
        print(f"wrote {a.o} ({cert['kind']})")
    else:
        sys.stdout.write(text)
    return 0


def cmd_verify(a):
    cert = json.loads(pathlib.Path(a.file).read_text(encoding="utf-8"))
    ok, msg = p699.verify_row(cert)
    print(("VERIFIED: " if ok else "REJECTED: ") + msg)
    return 0 if ok else 1


def cmd_residuals(a):
    data = residuals.load()
    print(f"{'id':<10} {'problem':>7}  {'slice':<8} {'searched through':>16}  {'survivors':>9}  residual")
    for r in data["residuals"]:
        print(f"{r['id']:<10} {r['problem']:>7}  {r['slice']:<8} {r['searched_through']:>16}  "
              f"{r['survivors']:>9}  {r['residual'][:60]}")
    return 0


def cmd_residual(a):
    rec = residuals.get(a.id)
    if a.n is None:
        print(json.dumps(rec, indent=1, ensure_ascii=False))
        front = residuals.frontier(rec)
        if front:
            print(f"\nfirst unsearched members: {front}")
        return 0
    n = integer(a.n)
    inside = residuals.member(rec, n)
    print(f"n = {n} is {'IN' if inside else 'not in'} the residual of {rec['id']}")
    if n <= residuals.bound(rec):
        print(f"(n <= searched bound {rec['searched_through']}: covered by {rec['evidence']})")
    rep = residuals.decide(rec, n)
    for s in rep["stages"]:
        print(f"  - {s}")
    print("row holds" if rep["holds"] else "COUNTEREXAMPLE")
    return 0 if rep["holds"] else 1


def cmd_factor(a):
    n = integer(a.n)
    f = nt.factor(n)
    print(" * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in f.items()) or "1")
    if max(f, default=1) >= nt.PROVEN_PRIME_BOUND:
        print("note: a factor exceeds 3.3e24, so its primality is Baillie-PSW, not a proof")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("row", cmd_row), ("anatomy", cmd_anatomy), ("certify", cmd_certify)):
        s = sub.add_parser(name)
        s.add_argument("n")
        s.add_argument("i", type=int)
        if name == "certify":
            s.add_argument("-o")
        s.set_defaults(fn=fn)
    s = sub.add_parser("verify")
    s.add_argument("file")
    s.set_defaults(fn=cmd_verify)
    sub.add_parser("residuals").set_defaults(fn=cmd_residuals)
    s = sub.add_parser("residual")
    s.add_argument("id")
    s.add_argument("n", nargs="?")
    s.set_defaults(fn=cmd_residual)
    s = sub.add_parser("factor")
    s.add_argument("n")
    s.set_defaults(fn=cmd_factor)
    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
