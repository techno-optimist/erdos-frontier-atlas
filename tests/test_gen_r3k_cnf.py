"""r3k-edge-cnf generator: contract tests (charter WS5).

The load-bearing test is reproduction of the committed
``certificates/ramsey-3-3/problem.cnf`` exemplar: same variable numbering,
same clause *set* (the generator is logically identical, not byte-identical —
the committed file interleaves clause pairs per triangle and carries a
different header; see the generator docstring).
"""
import importlib.util
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "gen_r3k_cnf", ROOT / "tools" / "gen_r3k_cnf.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


def _parse_dimacs(text):
    """Return (nvars, nclauses_declared, [frozenset(literals), ...])."""
    nvars = nclauses = None
    clauses = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p cnf"):
            _, _, v, c = line.split()
            nvars, nclauses = int(v), int(c)
            continue
        lits = [int(t) for t in line.split()]
        assert lits[-1] == 0, f"clause line not 0-terminated: {line!r}"
        clauses.append(frozenset(lits[:-1]))
    return nvars, nclauses, clauses


# ---------------------------------------------------------------------------
# Reproduction of the committed R(3,3) exemplar
# ---------------------------------------------------------------------------

def test_reproduces_ramsey_3_3_certificate():
    committed = (ROOT / "certificates" / "ramsey-3-3" / "problem.cnf").read_text()
    generated = gen.generate_dimacs(3, 6)
    cv, cc, cclauses = _parse_dimacs(committed)
    gv, gc, gclauses = _parse_dimacs(generated)
    assert (cv, cc) == (gv, gc) == (15, 40)
    # No duplicate clauses on either side, and the clause SETS are equal —
    # i.e. identical up to clause ordering, with identical variable numbering.
    assert len(set(cclauses)) == len(cclauses) == 40
    assert len(set(gclauses)) == len(gclauses) == 40
    assert set(cclauses) == set(gclauses)


# ---------------------------------------------------------------------------
# Structure: counts, determinism, argument validation
# ---------------------------------------------------------------------------

def test_counts_r34_n9():
    nv, nc, clauses = _parse_dimacs(gen.generate_dimacs(4, 9))
    assert nv == 36                       # C(9,2)
    assert nc == len(clauses) == 84 + 126  # C(9,3) red + C(9,4) blue
    assert sum(1 for c in clauses if all(l < 0 for l in c)) == 84
    assert sum(1 for c in clauses if all(l > 0 for l in c)) == 126
    assert all(len(c) == 6 for c in clauses if all(l > 0 for l in c))


def test_counts_r35_n14():
    nv, nc, clauses = _parse_dimacs(gen.generate_dimacs(5, 14))
    assert nv == 91                         # C(14,2)
    assert nc == len(clauses) == 364 + 2002  # C(14,3) red + C(14,5) blue
    assert all(len(c) == 10 for c in clauses if all(l > 0 for l in c))


def test_deterministic():
    assert gen.generate_dimacs(4, 9) == gen.generate_dimacs(4, 9)


def test_rejects_bad_args():
    import pytest
    with pytest.raises(ValueError):
        list(gen.generate_clauses(2, 6))
    with pytest.raises(ValueError):
        list(gen.generate_clauses(4, 3))


# ---------------------------------------------------------------------------
# Exactness: brute-force truth of the encoding on small instances.
# These check the SEMANTICS (Ramsey colorings <-> satisfying assignments),
# independently of the committed certificate.
# ---------------------------------------------------------------------------

def _brute_force_sat(k, n):
    nv, _, clauses = _parse_dimacs(gen.generate_dimacs(k, n))
    for bits in product([False, True], repeat=nv):
        if all(any(bits[l - 1] if l > 0 else not bits[-l - 1] for l in cl)
               for cl in clauses):
            return True
    return False


def test_k3_n5_sat():
    # R(3,3) = 6, so K_5 admits a good coloring (the pentagon):
    assert _brute_force_sat(3, 5)


def test_k3_n6_unsat():
    # ... and K_6 does not (friends-and-strangers), by 2^15 exhaustion:
    assert not _brute_force_sat(3, 6)


def test_k4_n5_sat():
    # R(3,4) = 9 > 5, so the k=4 blue clauses must leave K_5 satisfiable:
    assert _brute_force_sat(4, 5)


def test_semantics_match_coloring():
    # A concrete K_5 pentagon coloring (red = 5-cycle) satisfies (3,5); a
    # monochromatic-red coloring of K_6 violates exactly the red clauses.
    var = gen.edge_vars(5)
    red = {(1, 2), (2, 3), (3, 4), (4, 5), (1, 5)}
    assign = {var[e]: (e in red) for e in var}
    _, _, clauses = _parse_dimacs(gen.generate_dimacs(3, 5))
    assert all(any(assign[abs(l)] == (l > 0) for l in cl) for cl in clauses)
