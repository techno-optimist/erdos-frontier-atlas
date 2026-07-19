"""r3k-edge-cnf generator: contract tests (charter WS5).

Two load-bearing reproduction tests against the committed
``certificates/ramsey-3-3/problem.cnf`` exemplar:

* the default (``lex``) order is logically identical to it — same variable
  numbering, same clause *set*, different clause order and header;
* the ``interleaved`` order reproduces it **byte-identically**.

Plus a byte-freeze regression: the default output's sha256s must never
change (adding ``--order`` must not move a byte of the default output).
"""
import hashlib
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
# Encoding-order variants (charter WS5, encoding-variance axis)
# ---------------------------------------------------------------------------

# Byte-freeze of the DEFAULT (lex, v1.0.0) output. These are the same
# cnf_sha256 values recorded in observatory/measurements.json; if this test
# fails, the encoding changed and the version string must be bumped.
LEX_SHA256 = {
    (3, 6): "b2becb9de1ca7edaf13b8bde4494c4548b22ccbe0beae0b6777d79dbadf252f9",
    (4, 9): "7c46f311cdf3c35fe3839b38b12acaa906b540f25ff27d5299e337d95325caa0",
    (5, 14): "41fdb48d6c984fef2531fe66059c94655d559ef99ea7f3f794fd291862cd5e2e",
}


def test_default_output_byte_frozen():
    for (k, n), want in LEX_SHA256.items():
        got = hashlib.sha256(gen.generate_dimacs(k, n).encode()).hexdigest()
        assert got == want, f"default (lex) output changed for (k={k}, n={n})"


def test_default_order_is_lex():
    assert gen.generate_dimacs(4, 9) == gen.generate_dimacs(4, 9, order="lex")


def test_interleaved_reproduces_committed_file_byte_identically():
    committed = (ROOT / "certificates" / "ramsey-3-3" / "problem.cnf").read_text()
    assert gen.generate_dimacs(3, 6, order="interleaved") == committed


def test_interleaved_same_clause_set_different_order():
    for k, n in [(3, 6), (4, 9), (5, 7)]:
        lv, lc, lex = _parse_dimacs(gen.generate_dimacs(k, n))
        iv, ic, il = _parse_dimacs(gen.generate_dimacs(k, n, order="interleaved"))
        assert (lv, lc) == (iv, ic)
        # No duplicates on either side, so set equality == multiset equality:
        assert len(set(lex)) == len(lex) == len(il) == len(set(il))
        assert set(lex) == set(il)
        assert lex != il  # genuinely a different ORDER, not the same file


def test_interleaved_structure_r34():
    # 84 red, 126 blue: 84 alternating (red, blue) pairs, then the 42
    # remaining blue clauses.
    clauses = list(gen.generate_clauses(4, 9, order="interleaved"))
    assert len(clauses) == 210
    for i in range(84):
        assert all(l < 0 for l in clauses[2 * i])
        assert all(l > 0 for l in clauses[2 * i + 1])
    assert all(all(l > 0 for l in c) for c in clauses[168:])


def test_interleaved_pairs_same_triangle_at_k3():
    # At k=3 the pair at each position is the SAME triangle, negated/positive
    # (the committed exemplar's pair-per-triangle order).
    clauses = list(gen.generate_clauses(3, 6, order="interleaved"))
    assert len(clauses) == 40
    for i in range(0, 40, 2):
        assert frozenset(-l for l in clauses[i]) == frozenset(clauses[i + 1])


def test_rejects_bad_order():
    import pytest
    with pytest.raises(ValueError):
        list(gen.generate_clauses(3, 6, order="shuffled"))


def test_cli_order_flag(tmp_path):
    out = tmp_path / "out.cnf"
    gen.main(["3", "6", "-o", str(out), "--order", "interleaved"])
    committed = (ROOT / "certificates" / "ramsey-3-3" / "problem.cnf").read_text()
    assert out.read_text() == committed
    out_lex = tmp_path / "out_lex.cnf"
    gen.main(["3", "6", "-o", str(out_lex)])
    want = LEX_SHA256[(3, 6)]
    assert hashlib.sha256(out_lex.read_bytes()).hexdigest() == want


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
