#!/usr/bin/env python3
"""Standalone exact audit of the 117-cell common-successor/spectral wall.

No project modules are imported.  All closure pricing uses stdlib Fraction.
The scope is the position-independent open-path potential
P(c_0,...,c_{m-1}) = g[c_0]/2 + sum H[c_i,c_{i+1}] + g[c_{m-1}]/2.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

Q = 6
S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
D = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
     (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
PAIRS = ((0, 12), (1, 4), (3, 18), (5, 17),
         (7, 24), (16, 31), (25, 36))


class AuditError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def alphabet() -> tuple[tuple[int, int, int, int], ...]:
    cells = tuple((a, b, (a + da) % Q, (b + db) % Q)
                  for a, b in S0 for da, db in D)
    require(len(cells) == 117 and len(set(cells)) == 117,
            "not 117 distinct q=6 decoder cells")
    return cells


U = alphabet()


def scalar_cost(a: int, b: int, c: int) -> Fraction | None:
    """Raw q^2-scaled closure supremum for one scalar digit triple."""
    candidates: list[Fraction] = []
    defect = a + c - 2 * b
    for carry in (-1, 0, 1):
        ell = Q * carry - defect
        if ell not in (-1, 0, 1):
            continue
        low, high = {
            -1: (Fraction(1, 2), Fraction(1)),
             0: (Fraction(0), Fraction(1)),
             1: (Fraction(0), Fraction(1, 2)),
        }[ell]
        t = low if carry > 0 else high
        candidates.append(-2 * Q * carry *
                          (Fraction(a + c, 2) + b + 2 * t + Fraction(ell, 2)))
    return max(candidates) if candidates else None


SCALAR = tuple(tuple(tuple(scalar_cost(a, b, c) for c in range(Q))
                     for b in range(Q)) for a in range(Q))


def rhs(x: int, y: int, z: int) -> int | None:
    values = [SCALAR[U[x][j]][U[y][j]][U[z][j]] for j in range(4)]
    if any(value is None for value in values):
        return None
    answer = sum(values, Fraction(0))
    require(answer.denominator == 1, "nonintegral 4D raw RHS")
    return int(answer)


def census() -> None:
    all_rows = sum(rhs(x, y, z) is not None
                   for x, y, z in product(range(117), repeat=3))
    require(all_rows == 98167, f"wrong legal-row census: {all_rows}")
    print(f"ALPHABET_AND_CLOSURE_OK cells=117 legal_4d_rows={all_rows}")


def verify_pairs() -> None:
    require(len(set(sum((list(pair) for pair in PAIRS), []))) == 14,
            "claimed bad pairs are not vertex-disjoint")
    for a, b in PAIRS:
        first, second = rhs(a, b, b), rhs(a, a, b)
        require(first is not None and second is not None,
                f"pair {(a, b)} has an incompatible closure row")
        require(first + second == 72,
                f"pair {(a, b)} gap is {first + second}, not 72")
        require(first + second > 0, f"pair {(a, b)} is not a wall")
        print(f"PAIR_OK {a}->{b} rows=({a},{b},{b}):{first},({a},{a},{b}):{second},gap=72")


def wall_coefficients(a: int, b: int, p: int) -> tuple[dict[int, Fraction], dict[tuple[int, int], int]]:
    """Replay (a,b,b),(p,p,p) plus (a,a,b),(p,p,p)."""
    g: dict[int, Fraction] = {}
    edges: dict[tuple[int, int], int] = {}
    for triple in ((a, b, b), (a, a, b)):
        for label, coefficient in zip(triple, (1, -2, 1)):
            g[label] = g.get(label, Fraction(0)) + Fraction(coefficient, 2)
            g[p] = g.get(p, Fraction(0)) + Fraction(coefficient, 2)
            edge = (label, p)
            edges[edge] = edges.get(edge, 0) + coefficient
    return g, edges


def verify_symbolic_wall() -> None:
    # p may equal a or b: loops are allowed in the hostile graph scope.
    # Only the two required transitions a->p and b->p are used.
    for a, b in PAIRS:
        for p in (0, a, b, 116):
            g, edges = wall_coefficients(a, b, p)
            require(not any(g.values()), f"G does not cancel for {(a, b, p)}")
            require(not any(edges.values()), f"J does not cancel for {(a, b, p)}")
            require(rhs(p, p, p) == 0, "diagonal local row is not zero")
    print("TWO_ROW_FARKAS_OK all_G_and_directed_J_cancel rhs=72 diagonal_rhs=0")


def spectral_accounting() -> None:
    """Symbolic Perron proof, including reducible matrices and arbitrary loops.

    For Av=rho*v, v>=0, S=sum(v), a singleton obeys rho*v_i<=S.
    Disjoint N+(a),N+(b) gives rho*(v_a+v_b)<=S.  Summing the
    seven pair blocks and the other 103 vertices gives rho*S<=110*S.
    """
    covered = {x for pair in PAIRS for x in pair}
    require(len(covered) == 14, "bad-pair cover size mismatch")
    singleton_count = 117 - len(covered)
    block_count = len(PAIRS) + singleton_count
    require(singleton_count == 103 and block_count == 110,
            "wrong block accounting")
    gate = Fraction(441, 4)
    require(Fraction(block_count) < gate, "capacity bound misses density gate")
    print(f"PERRON_SYMBOLIC_OK pair_blocks=7 singleton_blocks=103 rho_le={block_count} gate={gate}")


def planted_failures() -> None:
    try:
        a, _ = PAIRS[0]
        fake = (a, a)
        require(len(set(sum((list(pair) for pair in (fake,) + PAIRS[1:]), []))) == 14,
                "planted repeated vertex accepted")
    except AuditError:
        pass
    else:
        raise AuditError("vertex-disjointness plant escaped")
    try:
        a, b = PAIRS[0]
        require(rhs(a, b, b) + rhs(a, a, b) == 73,
                "planted wrong RHS accepted")
    except AuditError:
        pass
    else:
        raise AuditError("wrong-RHS plant escaped")
    try:
        a, b = PAIRS[0]
        g, edges = wall_coefficients(a, b, 116)
        edges[a, 116] += 1
        require(not any(g.values()) and not any(edges.values()),
                "planted noncancellation accepted")
    except AuditError:
        pass
    else:
        raise AuditError("coefficient plant escaped")
    print("PLANTED_FAILURES_REJECTED repeated_vertex wrong_rhs noncancelling_J")


def main() -> None:
    census()
    verify_pairs()
    verify_symbolic_wall()
    spectral_accounting()
    planted_failures()
    print("AUDIT_PASS scope=0-1-directed-graphs fixed-117 position-independent-g-H two-block-closure")


if __name__ == "__main__":
    main()
