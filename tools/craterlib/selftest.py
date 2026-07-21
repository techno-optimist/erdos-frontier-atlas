#!/usr/bin/env python3
"""Selftest for the generic crater engine -- PLANTED-FAILURE controls first.

A validator that only ever passes is indistinguishable from one that does
nothing. Every gate here is exercised twice: once on a well-formed crater (must
pass) and once on a crater with one byte deliberately broken (must FAIL, with
the right message). The forward-polarity cases are the proof that the
generalization is real and not a rename: a `proved` crater propagates by modus
ponens, degrades across an index-transforming edge, never upgrades back, and
halts on cross-polarity contact.

Run: python3 tools/crater.py selftest
"""
import json
import shutil
import tempfile
from pathlib import Path

from . import driver
from .engine import propagate
from .scaffold import default_config
from .schema import load_graph
from .spec import load_config

OK_CHECK = "import sys; sys.exit(0)\n"
BAD_CHECK = "import sys; print('planted failure'); sys.exit(1)\n"

CASES = []


def case(fn):
    CASES.append(fn)
    return fn


def expect_fail(fragment, thunk):
    try:
        thunk()
    except SystemExit as exc:
        msg = str(exc)
        if fragment not in msg:
            raise AssertionError(f"expected {fragment!r} in failure, got: {msg}")
        return msg
    raise AssertionError(f"expected a failure containing {fragment!r}, got success")


# -- fixture construction ---------------------------------------------------

def node(nid, **kw):
    base = {"id": nid, "name": nid, "statement": f"statement of {nid}",
            "verification": "VERIFIED", "primary_source": "selftest",
            "sources": ["selftest"]}
    base.update(kw)
    return base


def edge(a, b, type="implies", sem="index_preserving", **kw):
    base = {"from": a, "to": b, "type": type, "index_semantics": sem,
            "citation": "selftest citation"}
    base.update(kw)
    return base


def make_crater(td, slug, polarity, nodes, edges, roots, cfg_patch=None,
                check_body=OK_CHECK):
    """Write a complete crater under <td>/atlas/<slug> and return its spec."""
    root = Path(td)
    d = root / "atlas" / slug
    (d / "checks").mkdir(parents=True, exist_ok=True)
    (d / "checks" / "root_check.py").write_text(check_body)
    cfg = default_config(slug, polarity,
                         reach_license=f"atlas/{slug}/checks/root_check.py")
    if cfg_patch:
        cfg_patch(cfg)
    (d / "crater.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    graph = {"schema": cfg["graph_schema"], "roots": roots, "nodes": nodes,
             "edges": edges,
             "quarantine_findings": {"likely_confabulated": [],
                                     "unclear_pending_rename": []}}
    (d / "implication_graph.json").write_text(json.dumps(graph, ensure_ascii=False))
    (d / "README.md").write_text(
        f"# {slug}\n\n{cfg['map']['markers']['begin']}\n"
        f"{cfg['map']['markers']['end']}\n")
    return load_config(d / "crater.json", root=root)


def root_of(nid, fact, cert_slug):
    return [{"node": nid, "fact": fact,
             "certificate": f"atlas/{cert_slug}/checks/root_check.py"}]


def statuses(spec):
    g, nodes = load_graph(spec)
    return propagate(spec, g, nodes)


# -- the live JC crater (the byte gate's canary) -----------------------------

@case
def live_jc_crater_still_validates():
    """The migrated engine reproduces the committed JC view and README map."""
    repo = Path(__file__).resolve().parent.parent.parent
    cfg = repo / "atlas" / "jc-crater" / "crater.json"
    if not cfg.exists():
        return "SKIP (no jc-crater in this checkout)"
    spec = load_config(cfg, root=repo)
    driver.validate(spec, write=False, quiet=True)


# -- refuted polarity (modus tollens) ---------------------------------------

@case
def refuted_modus_tollens_preserving_carries_full():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "t1", "refuted",
                        [node("jc"), node("a")], [edge("a", "jc")],
                        root_of("jc", "REFUTED_ALL_INDICES", "t1"))
        st, _ = statuses(s)
        assert st["a"] == "REFUTED_ALL_INDICES", st


@case
def refuted_transforming_edge_degrades_and_never_upgrades():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "t2", "refuted",
                        [node("jc"), node("b"), node("c")],
                        [edge("b", "jc", sem="index_transforming"), edge("c", "b")],
                        root_of("jc", "REFUTED_ALL_INDICES", "t2"))
        st, _ = statuses(s)
        assert st["b"] == "REFUTED_SOME_INDEX", st
        # A FLOOR source yields FLOOR even across a preserving edge. (This is
        # the true rule; it is NOT "FULL originates only from a root" -- see
        # engine.py: a FULL source across a preserving edge does hand out FULL.)
        assert st["c"] == "REFUTED_SOME_INDEX", st


@case
def refuted_falsity_never_flows_forward_but_orphans_support():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "t3", "refuted",
                        [node("jc"), node("d")], [edge("jc", "d")],
                        root_of("jc", "REFUTED_ALL_INDICES", "t3"))
        st, fl = statuses(s)
        assert st["d"] == "OPEN", st
        assert fl["d"]["orphaned_conditional_support"] is True, fl


@case
def planted_flipped_edge_changes_computed_statuses():
    """Direction integrity: reversing one implication must NOT be a no-op."""
    with tempfile.TemporaryDirectory() as td:
        good = make_crater(td, "t4", "refuted", [node("jc"), node("a")],
                           [edge("a", "jc")], root_of("jc", "REFUTED_ALL_INDICES", "t4"))
        st_good, _ = statuses(good)
        bad = make_crater(td, "t4f", "refuted", [node("jc"), node("a")],
                          [edge("jc", "a")], root_of("jc", "REFUTED_ALL_INDICES", "t4f"))
        st_bad, fl_bad = statuses(bad)
        assert st_good["a"] == "REFUTED_ALL_INDICES", st_good
        assert st_bad["a"] == "OPEN", st_bad
        assert fl_bad["a"]["orphaned_conditional_support"] is True
        assert st_good != st_bad


@case
def refuted_reaching_a_theorem_is_an_inconsistency():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "t5", "refuted",
                        [node("jc"), node("t", proven_theorem=True)],
                        [edge("t", "jc")], root_of("jc", "REFUTED_ALL_INDICES", "t5"))
        expect_fail("INCONSISTENCY", lambda: statuses(s))


# -- proved polarity (modus ponens) -- the generalization under test ---------

@case
def proved_modus_ponens_runs_forwards():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "p1", "proved",
                        [node("thm"), node("y")], [edge("thm", "y")],
                        root_of("thm", "PROVED_ALL_INDICES", "p1"))
        st, _ = statuses(s)
        assert st["y"] == "PROVED_ALL_INDICES", st


@case
def proved_backwards_edge_proves_nothing():
    """The dual of 'falsity never flows forward': X --implies--> Y with Y proved
    says nothing about X, but kills the contrapositive refutation route."""
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "p2", "proved",
                        [node("thm"), node("x")], [edge("x", "thm")],
                        root_of("thm", "PROVED_ALL_INDICES", "p2"))
        st, fl = statuses(s)
        assert st["x"] == "OPEN", st
        assert fl["x"]["obsolete_refutation_route"] is True, fl


@case
def proved_transforming_edge_only_reaches_a_sub_family():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "p3", "proved",
                        [node("thm"), node("y"), node("z")],
                        [edge("thm", "y", sem="index_transforming"), edge("y", "z")],
                        root_of("thm", "PROVED_ALL_INDICES", "p3"))
        st, _ = statuses(s)
        assert st["y"] == "PROVED_SOME_INDICES", st
        # and a FLOOR source never yields FULL, whatever the edge's semantics
        assert st["z"] == "PROVED_SOME_INDICES", st


@case
def proved_reaching_a_refuted_fact_is_an_inconsistency():
    """Cross-polarity contact halts, exactly as a refutation reaching a theorem
    does under the other polarity."""
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "p4", "proved",
                        [node("thm"), node("gone", proven_theorem=True)],
                        [edge("thm", "gone")],
                        root_of("thm", "PROVED_ALL_INDICES", "p4"))
        expect_fail("INCONSISTENCY", lambda: statuses(s))


@case
def equivalence_copies_both_ways_in_both_polarities():
    for polarity, full, floor, slug in (
            ("refuted", "REFUTED_ALL_INDICES", "REFUTED_SOME_INDEX", "e1"),
            ("proved", "PROVED_ALL_INDICES", "PROVED_SOME_INDICES", "e2")):
        with tempfile.TemporaryDirectory() as td:
            s = make_crater(td, slug, polarity,
                            [node("r"), node("u"), node("v")],
                            [edge("r", "u", type="equivalent"),
                             edge("v", "r", type="equivalent",
                                  sem="index_transforming")],
                            root_of("r", full, slug))
            st, _ = statuses(s)
            assert st["u"] == full, (polarity, st)
            assert st["v"] == floor, (polarity, st)


# -- the honest FULL boundary (engine.py's corrected corollary) --------------

@case
def full_source_upgrades_a_floor_target_this_is_intended():
    """The behaviour engine.py's docstring used to deny. FULL is NOT reserved to
    roots: `a` first gets FLOOR through a transforming edge, then a SECOND,
    independent preserving edge out of a FULL node justifies FULL for it, and
    max-rank keeps the stronger justification. Correct modus tollens -- and the
    exact shape a mis-typed edge would exploit, which is why the protection is a
    release gate (per-edge citations + primary-source review), not this algebra.
    """
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "f1", "refuted",
                        [node("jc"), node("a"), node("m")],
                        [edge("a", "jc", sem="index_transforming"),   # a -> FLOOR
                         edge("m", "jc"),                             # m -> FULL
                         edge("a", "m")],                             # m FULL -> a FULL
                        root_of("jc", "REFUTED_ALL_INDICES", "f1"))
        st, _ = statuses(s)
        assert st["m"] == "REFUTED_ALL_INDICES", st
        assert st["a"] == "REFUTED_ALL_INDICES", st   # FLOOR was upgraded to FULL


@case
def planted_same_ordered_pair_disagreeing_on_semantics_fails():
    """The one machine-checkable slice of mis-typing: X->Y declared BOTH
    preserving and transforming is a contradiction by construction."""
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "x1", "refuted", [node("jc"), node("a")],
                        [edge("a", "jc"),
                         edge("a", "jc", sem="index_transforming")],
                        root_of("jc", "REFUTED_ALL_INDICES", "x1"))
        expect_fail("disagree on index semantics", lambda: load_graph(s))


@case
def opposite_direction_edges_may_disagree_on_semantics():
    """...and the check is ORDERED, so the real JC shape stays legal: DC_n =>
    JC_n is preserving while JC_2n => DC_n is transforming."""
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "x2", "refuted", [node("jc"), node("dc")],
                        [edge("dc", "jc"),
                         edge("jc", "dc", sem="index_transforming")],
                        root_of("jc", "REFUTED_ALL_INDICES", "x2"))
        st, _ = statuses(s)
        assert st["dc"] == "REFUTED_ALL_INDICES", st


# -- structural gates -------------------------------------------------------

@case
def alias_table_accepts_a_legacy_semantics_key():
    """A crater may keep its own edge key (JC's `dimension_semantics`) forever;
    canonicalization is invisible in output."""
    def patch(cfg):
        cfg["edge_semantics"]["key_aliases"] = ["dimension_semantics", "index_semantics"]
        cfg["edge_semantics"]["value_aliases"].update(
            {"dimension_preserving": "index_preserving",
             "dimension_mixing": "index_transforming"})
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "a1", "refuted", [node("jc"), node("a")],
                        [{"from": "a", "to": "jc", "type": "implies",
                          "dimension_semantics": "dimension_mixing",
                          "citation": "c"}],
                        root_of("jc", "REFUTED_ALL_INDICES", "a1"), cfg_patch=patch)
        st, _ = statuses(s)
        assert st["a"] == "REFUTED_SOME_INDEX", st


@case
def planted_two_semantics_keys_on_one_edge_fails():
    def patch(cfg):
        cfg["edge_semantics"]["key_aliases"] = ["dimension_semantics", "index_semantics"]
        cfg["edge_semantics"]["value_aliases"]["dimension_preserving"] = "index_preserving"
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "a2", "refuted", [node("jc"), node("a")],
                        [{"from": "a", "to": "jc", "type": "implies",
                          "dimension_semantics": "dimension_preserving",
                          "index_semantics": "index_transforming",
                          "citation": "c"}],
                        root_of("jc", "REFUTED_ALL_INDICES", "a2"), cfg_patch=patch)
        expect_fail("more than one of", lambda: load_graph(s))


@case
def planted_quarantined_node_cannot_carry_an_edge():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "q1", "refuted",
                        [node("jc"), node("q", verification="UNVERIFIED_CANDIDATE")],
                        [edge("q", "jc")], root_of("jc", "REFUTED_ALL_INDICES", "q1"))
        expect_fail("not VERIFIED", lambda: load_graph(s))


@case
def planted_broken_machine_check_fails_the_crater():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "m1", "refuted", [node("jc")], [],
                        root_of("jc", "REFUTED_ALL_INDICES", "m1"),
                        check_body=BAD_CHECK)
        expect_fail("machine check", lambda: driver.validate(s, write=True, quiet=True))


@case
def planted_unlicensed_reach_is_rejected():
    """A `full` level naming a reach_license that was never executed must fail --
    the reach in the level's NAME has to trace to a passing check."""
    def patch(cfg):
        cfg["levels"][0]["reach_license"] = "atlas/m2/checks/never_run.py"
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "m2", "refuted", [node("jc")], [],
                        root_of("jc", "REFUTED_ALL_INDICES", "m2"), cfg_patch=patch)
        expect_fail("unlicensed", lambda: driver.validate(s, write=True, quiet=True))


@case
def planted_missing_quantities_ledger_fails_when_required():
    def patch(cfg):
        cfg["quantities"]["required"] = True
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "m3", "refuted", [node("jc")], [],
                        root_of("jc", "REFUTED_ALL_INDICES", "m3"), cfg_patch=patch)
        expect_fail("quantities ledger missing",
                    lambda: driver.validate(s, write=True, quiet=True))


@case
def planted_mutated_computed_view_is_caught_by_the_drift_gate():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "d1", "refuted", [node("jc"), node("a")],
                        [edge("a", "jc")], root_of("jc", "REFUTED_ALL_INDICES", "d1"))
        driver.validate(s, write=True, quiet=True)
        driver.validate(s, write=False, quiet=True)          # clean run passes
        text = s.computed_path.read_text()
        s.computed_path.write_text(text.replace("REFUTED", "REFUTEDX", 1))
        expect_fail("STALE", lambda: driver.validate(s, write=False, quiet=True))


@case
def planted_mutated_readme_map_is_caught_by_the_drift_gate():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "d2", "refuted", [node("jc"), node("a")],
                        [edge("a", "jc")], root_of("jc", "REFUTED_ALL_INDICES", "d2"))
        driver.validate(s, write=True, quiet=True)
        text = s.readme_path.read_text()
        s.readme_path.write_text(text.replace("blast radius", "blast  radius", 1))
        expect_fail("STALE", lambda: driver.validate(s, write=False, quiet=True))


@case
def planted_missing_readme_markers_fail_loudly():
    with tempfile.TemporaryDirectory() as td:
        s = make_crater(td, "d3", "refuted", [node("jc")], [],
                        root_of("jc", "REFUTED_ALL_INDICES", "d3"))
        s.readme_path.write_text("# no markers here\n")
        expect_fail("markers", lambda: driver.validate(s, write=True, quiet=True))


@case
def scaffolded_crater_validates_out_of_the_box():
    from .scaffold import new_crater
    for polarity in ("refuted", "proved"):
        td = tempfile.mkdtemp()
        try:
            new_crater(td, f"s-{polarity}", polarity)
            s = load_config(Path(td) / "atlas" / f"s-{polarity}" / "crater.json",
                            root=Path(td))
            driver.validate(s, write=True, quiet=True)
            driver.validate(s, write=False, quiet=True)
        finally:
            shutil.rmtree(td, ignore_errors=True)


@case
def scaffolded_legend_points_the_same_way_as_the_scaffolded_edges():
    """A generated legend that contradicts the graph printed directly beneath it
    is worse than no legend. Under refutation the root is the arrow SINK; under
    proof it is the SOURCE. Also pins the root glyph off JC's radiation sign for
    a proved crater."""
    from .scaffold import new_crater
    for polarity, first, last, glyph, banned in (
            ("refuted", "any statement", "the root", "☢", "⚑"),
            ("proved", "the root", "any statement", "⚑", "☢")):
        td = tempfile.mkdtemp()
        try:
            new_crater(td, f"g-{polarity}", polarity)
            s = load_config(Path(td) / "atlas" / f"g-{polarity}" / "crater.json",
                            root=Path(td))
            driver.validate(s, write=True, quiet=True)
            readme = s.readme_path.read_text()
            for arrow in ("-->", "-.->"):
                line = next(ln for ln in readme.splitlines()
                            if ln.strip().startswith(("LP1[", "LM1["))
                            and arrow in ln and "|" in ln)
                head, tail = line.split(arrow, 1)
                assert f'"{first}"' in head, (polarity, arrow, line)
                assert f'"{last}"' in tail, (polarity, arrow, line)
            assert f"{glyph} " in readme, (polarity, "root glyph missing")
            assert banned not in readme, (polarity, f"{banned} leaked in")
        finally:
            shutil.rmtree(td, ignore_errors=True)


def run(verbose=True):
    """Run every control. Returns (passed, failed, skipped)."""
    passed = failed = skipped = 0
    for fn in CASES:
        try:
            out = fn()
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {exc}")
        except SystemExit as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}: unexpected hard failure: {exc}")
        else:
            if isinstance(out, str) and out.startswith("SKIP"):
                skipped += 1
                if verbose:
                    print(f"  skip  {fn.__name__}: {out}")
            else:
                passed += 1
                if verbose:
                    print(f"  ok    {fn.__name__}")
    print(f"crater selftest: {passed} passed, {failed} failed, {skipped} skipped "
          f"({len(CASES)} controls)")
    return passed, failed, skipped
