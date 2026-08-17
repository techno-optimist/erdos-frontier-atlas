#!/usr/bin/env python3
"""Exact, stdlib-only replay of the q=24 two-tile core-wall certificates.

The two companion ``*.witnesses.bin`` files are complete ordered global
witness records, not solver output: one 21-byte record is
    (u,v,w, x1,y1,z1, x2,y2,z2, x3,y3,z3),
where each point occupies its two canonical coordinates.  This program
reconstructs their midpoint equations, raw costs, sparse inequalities, and
an exact Farkas ray.  It never imports a numerical package or runs a solver.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path

Q = 24
WORDS = {3: ("P3", "B", "B"), 4: ("B", "B", "P3")}
HERE = Path(__file__).resolve().parent
CASES = {
    "base_to_swap": (177, "ed8bf693b7cc4905682d6a42f113405e16e5bbfa99dbb15e60f564a25c25dcc4",
                     "d8b61837bd09bde420e15c3e7df617df6486073397e3129a652e218826e67da0"),
    "swap_to_base": (174, "91f978fefc26e9d8907a36338fa0474bc8f63cea29a087a38bfe5baba9efe940",
                     "cf358139a34a80dd79906f8fb28899f0d804b1cf071161b35e3bb0228bbb1b88"),
}


def tile() -> set[tuple[int, int]]:
    """EHPS T at q=24, epsilon=1/24, using its exact face conventions."""
    ans = set()
    for a in range(Q):
        for b in range(Q):
            s = a + b
            t1 = a >= 12 and s > 16 and s <= 28
            t2 = a >= 12 and b < 12 and s >= 29 and s <= 34
            t3 = a < 12 and b >= 12 and s >= 29 and s <= 34 and 2*a+b >= 37
            if t1 or t2 or t3:
                ans.add((a, b))
    return ans


def midpoint_ok(x, y, z) -> bool:
    return all((x[i] + z[i] - 2*y[i]) % Q == 0 for i in (0, 1))


def cost(x, z) -> int:
    return sum((x[i] - z[i]) ** 2 for i in (0, 1))


def hash_constraints(rows) -> str:
    # This is the source engine's canonical sparse-row serialization.
    payload = json.dumps([[list(c), rhs] for c, rhs in rows], separators=(",", ":"))
    return sha256(payload.encode()).hexdigest()


def decode_case(name: str):
    count, witness_digest, constraint_digest = CASES[name]
    raw = (HERE / (name + ".witnesses.bin")).read_bytes()
    if sha256(raw).hexdigest() != witness_digest:
        raise AssertionError("witness-data hash mismatch")
    if len(raw) != 21 * count:
        raise AssertionError("bad witness record length")
    T = tile()
    top = {(b, a) for a, b in T}
    if name == "base_to_swap":
        supports = {"B": T-top, "P3": top-T}
    else:
        supports = {"B": top-T, "P3": T-top}
    if len(T) != 163 or len(T & top) != 53 or {len(v) for v in supports.values()} != {110}:
        raise AssertionError("unexpected exact core sizes")
    # Same role ordering as PotentialIndexer: P3 precedes B.
    labels = [("P3", p) for p in sorted(supports["P3"])] + [("B", p) for p in sorted(supports["B"])]
    index = {label: i for i, label in enumerate(labels)}
    rows = []
    for offset in range(0, len(raw), 21):
        d = raw[offset:offset+21]
        if tuple(d[:3]) not in {(3, 3, 3), (3, 3, 4), (3, 4, 3), (3, 4, 4),
                                (4, 3, 3), (4, 3, 4), (4, 4, 3), (4, 4, 4)}:
            raise AssertionError("inactive codeword in certificate")
        u, v, w = (WORDS[d[0]], WORDS[d[1]], WORDS[d[2]])
        coefficients, rhs = {}, 0
        for i in range(3):
            a = 3 + 6*i
            x, y, z = tuple(d[a:a+2]), tuple(d[a+2:a+4]), tuple(d[a+4:a+6])
            for role, point in ((u[i], x), (v[i], y), (w[i], z)):
                if point not in supports[role]:
                    raise AssertionError("witness point is outside its role support")
            if not midpoint_ok(x, y, z):
                raise AssertionError("non-midpoint witness")
            rhs += cost(x, z)
            for role, point, c in ((u[i], x, 1), (v[i], y, -2), (w[i], z, 1)):
                j = index[(role, point)]
                coefficients[j] = coefficients.get(j, 0) + c
        rows.append((tuple(sorted((j, c) for j, c in coefficients.items() if c)), rhs))
    if hash_constraints(rows) != constraint_digest:
        raise AssertionError("reconstructed-constraint hash mismatch")
    source = json.dumps({"q": Q, "orientation": name, "B": sorted(supports["B"]), "P3": sorted(supports["P3"])}, separators=(",", ":"))
    return labels, rows, sha256(source.encode()).hexdigest(), witness_digest, constraint_digest


def independent_equations(rows, nvars: int):
    """Choose a rank-maximal row subset over a fixed prime (selection only)."""
    prime, basis, chosen = 1000003, {}, []
    for variable in range(nvars):
        row = {j: c % prime for j, (sp, _) in enumerate(rows) for v, c in sp if v == variable}
        while row:
            pivot = min(row)
            if row[pivot] == 0:
                del row[pivot]
                continue
            if pivot not in basis:
                inv = pow(row[pivot], -1, prime)
                basis[pivot] = {j: (x*inv) % prime for j, x in row.items() if x % prime}
                chosen.append(variable)
                break
            factor = row[pivot]
            for j, x in basis[pivot].items():
                row[j] = (row.get(j, 0) - factor*x) % prime
            row = {j: x for j, x in row.items() if x}
    return chosen


def primitive_ray(rows, nvars: int):
    """Exact Fraction RREF for the one-dimensional left nullspace."""
    selected = independent_equations(rows, nvars)
    n = len(rows)
    if len(selected) != n - 1:
        raise AssertionError("certificate does not have the expected nullity one")
    matrix = []
    for variable in selected:
        line = [Fraction(0) for _ in range(n)]
        for j, (sp, _) in enumerate(rows):
            for v, c in sp:
                if v == variable:
                    line[j] = Fraction(c)
                    break
        matrix.append(line)
    pivots, rank = [], 0
    for column in range(n):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        divisor = matrix[rank][column]
        matrix[rank] = [x / divisor for x in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][column]:
                factor = matrix[i][column]
                matrix[i] = [x - factor*y for x, y in zip(matrix[i], matrix[rank])]
        pivots.append(column)
        rank += 1
        if rank == len(matrix):
            break
    free = next(c for c in range(n) if c not in set(pivots))
    ray = [Fraction(0) for _ in range(n)]
    ray[free] = Fraction(1)
    for i, column in enumerate(pivots):
        ray[column] = -matrix[i][free]
    den = 1
    for x in ray:
        den = den * x.denominator // gcd(den, x.denominator)
    integers = [int(x * den) for x in ray]
    common = 0
    for x in integers:
        common = gcd(common, abs(x))
    integers = [x // common for x in integers]
    if all(x < 0 for x in integers):
        integers = [-x for x in integers]
    if not all(x > 0 for x in integers):
        raise AssertionError("nonpositive Farkas multiplier")
    return integers


def replay(name: str) -> dict:
    labels, rows, source_hash, witness_hash, constraint_hash = decode_case(name)
    lam = primitive_ray(rows, len(labels))
    # Source convention: C f >= r.  Audit convention: A f <= b with A=-C,b=-r.
    balance = [Fraction(0) for _ in labels]
    bdot = Fraction(0)
    for multiplier, (sp, rhs) in zip(lam, rows):
        bdot -= Fraction(multiplier * rhs)  # lambda^T b, b=-r
        for j, coefficient in sp:
            balance[j] -= Fraction(multiplier * coefficient)  # A=-C
    if any(balance) or not bdot < 0:
        raise AssertionError("invalid exact Farkas certificate")
    cert = json.dumps(lam, separators=(",", ":")).encode()
    return {"case": name, "variables": len(labels), "rows": len(rows), "lambda_min": min(lam),
            "lambda_max_digits": len(str(max(lam))), "lambda_sum": sum(lam),
            "lambda_dot_b": f"{bdot.numerator}/{bdot.denominator}",
            "source_sha256": source_hash, "witness_sha256": witness_hash,
            "constraint_sha256": constraint_hash, "certificate_sha256": sha256(cert).hexdigest()}


if __name__ == "__main__":
    print(json.dumps([replay(name) for name in CASES], indent=2, sort_keys=True))
