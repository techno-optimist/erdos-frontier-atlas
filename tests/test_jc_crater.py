"""Unit tests for the JC crater propagation engine (tools/validate_jc_crater.py).

Each propagation rule is exercised on a synthetic mini-graph; the committed
crater graph is then validated end-to-end (machine checks included) and its
generated view checked for staleness.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "validate_jc_crater", ROOT / "tools" / "validate_jc_crater.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def node(nid, **kw):
    base = {"id": nid, "name": nid, "statement": f"statement of {nid}",
            "verification": "VERIFIED", "primary_source": "test source",
            "sources": ["test"]}
    base.update(kw)
    return base


def graph(nodes, edges, roots):
    return {"schema": "efa-jc-crater/v1", "nodes": nodes, "edges": edges,
            "roots": roots}


def edge(a, b, type="implies", sem="dimension_preserving", **kw):
    base = {"from": a, "to": b, "type": type, "dimension_semantics": sem,
            "citation": "test citation"}
    base.update(kw)
    return base


ROOT_JC = [{"node": "jc", "fact": "REFUTED_ALL_N_GE_3", "certificate": "x"}]


def run(g):
    nodes = {n["id"]: n for n in g["nodes"]}
    return M.propagate(g, nodes)


def test_modus_tollens_dimension_preserving():
    g = graph([node("jc"), node("a")], [edge("a", "jc")], ROOT_JC)
    status, _ = run(g)
    assert status["a"] == "REFUTED_ALL_N_GE_3"


def test_modus_tollens_dimension_mixing_degrades_modality():
    g = graph([node("jc"), node("b")],
              [edge("b", "jc", sem="dimension_mixing")], ROOT_JC)
    status, _ = run(g)
    assert status["b"] == "REFUTED_SOME_FINITE_DIM"


def test_weak_modality_carries_through_preserving_chain():
    g = graph([node("jc"), node("b"), node("c")],
              [edge("b", "jc", sem="dimension_mixing"), edge("c", "b")],
              ROOT_JC)
    status, _ = run(g)
    assert status["c"] == "REFUTED_SOME_FINITE_DIM"  # never upgraded


def test_equivalence_preserving_copies_full_refutation():
    g = graph([node("jc"), node("e")],
              [edge("jc", "e", type="equivalent")], ROOT_JC)
    status, _ = run(g)
    assert status["e"] == "REFUTED_ALL_N_GE_3"


def test_equivalence_mixing_degrades():
    g = graph([node("jc"), node("e")],
              [edge("jc", "e", type="equivalent", sem="dimension_mixing")],
              ROOT_JC)
    status, _ = run(g)
    assert status["e"] == "REFUTED_SOME_FINITE_DIM"


def test_falsity_never_flows_forward_but_orphans_support():
    g = graph([node("jc"), node("d")], [edge("jc", "d")], ROOT_JC)
    status, flags = run(g)
    assert status["d"] == "OPEN"
    assert flags["d"]["orphaned_conditional_support"] is True


def test_true_theorem_refutation_is_inconsistency():
    g = graph([node("jc"), node("t", proven_theorem=True)],
              [edge("t", "jc")], ROOT_JC)
    with pytest.raises(SystemExit, match="INCONSISTENCY"):
        run(g)


def test_quarantined_nodes_cannot_carry_edges():
    g = graph([node("jc"), node("q", verification="UNVERIFIED_CANDIDATE")],
              [edge("q", "jc")], ROOT_JC)
    with pytest.raises(SystemExit, match="not VERIFIED"):
        _validate_via_file(g)


def _validate_via_file(g, tmpdir=None):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "atlas" / "jc-crater"
        p.mkdir(parents=True)
        (p / "implication_graph.json").write_text(json.dumps(g))
        old_graph, old_root = M.GRAPH, M.ROOT
        try:
            M.GRAPH, M.ROOT = p / "implication_graph.json", Path(td)
            return M.load_graph()
        finally:
            M.GRAPH, M.ROOT = old_graph, old_root


def test_verified_node_requires_sources():
    g = graph([node("jc"), node("s", sources=[])], [], ROOT_JC)
    with pytest.raises(SystemExit, match="no sources"):
        _validate_via_file(g)


def test_committed_graph_validates_and_view_is_fresh():
    """End-to-end: the real graph + machine checks + staleness gate."""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_jc_crater.py")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "jc-crater VALID" in proc.stdout


def test_readme_map_staleness_gate(tmp_path):
    """The generated README map must be regenerated, not hand-edited: mutating
    the block between the markers must make the validator fail."""
    readme = ROOT / "atlas" / "jc-crater" / "README.md"
    original = readme.read_text()
    assert M.MAP_BEGIN in original and M.MAP_END in original
    try:
        # perturb a stable token inside the generated block (count-agnostic so
        # this test survives the graph growing)
        mutated = original.replace("The blast radius at a glance",
                                   "The blast radius at a glance ", 1)
        assert mutated != original
        readme.write_text(mutated)
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate_jc_crater.py")],
            capture_output=True, text=True)
        assert proc.returncode != 0
        assert "README" in proc.stdout + proc.stderr and \
               "STALE" in proc.stdout + proc.stderr
    finally:
        readme.write_text(original)


def test_short_label_handles_leading_parenthetical():
    """_short must not return an empty label for names that START with '(...)'."""
    assert M._short("(Stable) Hom-Dixmier Conjecture (Bäck 2026)") == \
        "Hom-Dixmier Conjecture"
    assert M._short("Jacobian Conjecture (Keller 1939), n >= 3") == \
        "Jacobian Conjecture"
    assert M._short("Dixmier Conjecture DC_n (endomorphisms of Weyl algebras)") == \
        "Dixmier Conjecture DC_n"


def test_rendered_mermaid_is_structurally_sound():
    """Every edge endpoint in the generated map is a declared node, and no node
    label is empty (an empty label renders a broken box)."""
    import re as _re
    g, nodes = M.load_graph()
    status, flags = M.propagate(g, nodes)
    block = M.render_map_block(g, nodes, status, flags)
    mm = block[block.find("```mermaid") + 10: block.find("```", block.find("```mermaid") + 10)]
    declared = set(_re.findall(r'^\s*([a-z_0-9]+)\["', mm, _re.M))
    assert declared == set(nodes)
    assert not _re.findall(r'\["\s*"\]', mm)  # no empty labels
    endpoints = {x for e in _re.findall(r'^\s*([a-z_0-9]+)\s*-\.?->\s*([a-z_0-9]+)', mm, _re.M) for x in e}
    assert endpoints <= declared


def test_staleness_gate_catches_drift(tmp_path):
    """Mutating the committed view must make the validator fail."""
    committed = (ROOT / "atlas" / "jc-crater" / "computed_statuses.json")
    original = committed.read_text()
    try:
        committed.write_text(original.replace("REFUTED", "REFUTEDX", 1))
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate_jc_crater.py")],
            capture_output=True, text=True)
        assert proc.returncode != 0
        assert "STALE" in proc.stdout + proc.stderr
    finally:
        committed.write_text(original)


def test_root_cannot_launder_quarantined_node():
    """wave-2 audit: a root naming an UNVERIFIED_CANDIDATE must not come out
    REFUTED with exit 0 (quarantine laundering)."""
    g = graph([node("q", verification="UNVERIFIED_CANDIDATE")], [],
              [{"node": "q", "fact": "REFUTED_ALL_N_GE_3", "certificate": "x"}])
    with pytest.raises(SystemExit, match="not VERIFIED"):
        _validate_via_file(g)


def test_root_cannot_override_proven_theorem():
    """wave-2 audit: root fact conflicting with a proven_theorem node must fail,
    not be a silent no-op."""
    g = graph([node("t", proven_theorem=True)], [],
              [{"node": "t", "fact": "REFUTED_ALL_N_GE_3", "certificate": "x"}])
    with pytest.raises(SystemExit, match="proven_theorem"):
        _validate_via_file(g)


def test_root_cannot_downgrade_independent_fact():
    """wave-2 audit: a root must not silently overwrite REFUTED_INDEPENDENTLY."""
    g = graph([node("r", independent_fact={
                   "status": "REFUTED_INDEPENDENTLY_PRE_2026", "citation": "c"})],
              [], [{"node": "r", "fact": "REFUTED_SOME_FINITE_DIM", "certificate": "x"}])
    with pytest.raises(SystemExit, match="independent_fact"):
        _validate_via_file(g)


def test_duplicate_root_fails():
    g = graph([node("jc")], [],
              [{"node": "jc", "fact": "REFUTED_ALL_N_GE_3", "certificate": "x"},
               {"node": "jc", "fact": "REFUTED_SOME_FINITE_DIM", "certificate": "y"}])
    with pytest.raises(SystemExit, match="duplicate root"):
        _validate_via_file(g)


def test_edge_incident_to_independent_fact_node_fails():
    """wave-2 audit: independent_fact nodes are context leaves; an incident edge
    would silently under-derive, so it must be rejected."""
    g = graph([node("jc"),
               node("r", independent_fact={
                   "status": "REFUTED_INDEPENDENTLY_PRE_2026", "citation": "c"})],
              [edge("r", "jc")], ROOT_JC)
    with pytest.raises(SystemExit, match="independent_fact"):
        _validate_via_file(g)


def test_proven_theorem_must_be_literal_true():
    g = graph([node("jc"), node("t", proven_theorem=1)], [], ROOT_JC)
    with pytest.raises(SystemExit, match="literal true"):
        _validate_via_file(g)


def test_quantities_gate_fails_when_file_missing():
    """wave-2 audit: deleting quantities.json must NOT silently pass."""
    import tempfile
    old = M.QUANTITIES
    try:
        M.QUANTITIES = Path(tempfile.gettempdir()) / "definitely_absent_quantities.json"
        with pytest.raises(SystemExit, match="quantities ledger missing"):
            M.check_quantities()
    finally:
        M.QUANTITIES = old


def test_orphan_flag_is_edge_order_independent():
    """wave-2 audit: for a node both downstream of a refuted node AND itself
    refuted, the orphan flag must be a function of FINAL status, not edge order."""
    nodes_ = [node("jc"), node("mid"), node("leaf")]
    # mid implies jc (so mid is refuted); jc implies mid too (forward) -- final
    # status of mid is REFUTED, so it must NOT be flagged orphaned regardless of
    # the order these two edges appear in.
    e_fwd = edge("jc", "mid")
    e_tollens = edge("mid", "jc")
    g1 = graph(nodes_, [e_fwd, e_tollens], ROOT_JC)
    g2 = graph(nodes_, [e_tollens, e_fwd], ROOT_JC)
    _, f1 = run(g1)
    _, f2 = run(g2)
    assert f1["mid"]["orphaned_conditional_support"] == \
           f2["mid"]["orphaned_conditional_support"]
    # mid ends REFUTED, so it is not an orphan in either ordering
    assert f1["mid"]["orphaned_conditional_support"] is False


def test_flipped_edge_changes_computed_statuses():
    """Direction integrity: reversing an implication edge must change the
    propagation result (a flipped edge cannot be a silent no-op)."""
    g = graph([node("jc"), node("a")], [edge("a", "jc")], ROOT_JC)
    status_correct, _ = run(g)
    g_flipped = graph([node("jc"), node("a")], [edge("jc", "a")], ROOT_JC)
    status_flipped, flags_flipped = run(g_flipped)
    assert status_correct["a"] == "REFUTED_ALL_N_GE_3"
    assert status_flipped["a"] == "OPEN"
    assert flags_flipped["a"]["orphaned_conditional_support"] is True
    assert status_correct != status_flipped
