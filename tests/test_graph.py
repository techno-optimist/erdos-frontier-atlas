"""The attack graph must stay honest, deterministic, and branch-scoped.

The graph (atlas/graph/ + views/sorties.md + views/graph/) is a generated
overlay: it may organize what the ledgers say, never say anything of its own.
These tests pin the properties that make it trustworthy:

- deterministic: two builds are byte-identical, and the committed outputs
  match a fresh build (`make check-graph` is the same gate);
- statuses only from stubs: no claim, card, or ranking sets or shades one;
- branch scoping: #64 is simultaneously a $1000 trap (general branch) and a
  vetted TARGET (cubic branch) — collapsing that split is the graph's own
  #64 failure mode, so the split IS the fixture;
- retraction pins: every string the contracts ban (must_not_contain) stays
  banned in every generated view — the graph must not resurrect a retraction;
- licensing firewall: link-only problems render no statement text;
- the documentation executes: every command GRAPH.md shows an agent works.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_graph  # noqa: E402
from validate_graph import validate  # noqa: E402


def _load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _graph():
    return _load("atlas/graph/graph.json")


_DUMP = ("import json, sys; sys.path.insert(0, 'tools'); import build_graph; "
         "print(json.dumps({str(k): v for k, v in build_graph.emit().items()}, "
         "sort_keys=True))")


def test_two_builds_are_byte_identical_across_hash_seeds():
    """Cross-process with different PYTHONHASHSEEDs: a same-interpreter double
    build shares one hash seed and could never catch set-iteration order
    leaking into output."""
    import os
    outs = []
    for seed in ("1", "2"):
        p = subprocess.run([sys.executable, "-c", _DUMP], cwd=ROOT,
                           capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": seed})
        assert p.returncode == 0, p.stderr
        outs.append(p.stdout)
    assert outs[0] == outs[1]


def test_committed_outputs_match_fresh_build():
    p = subprocess.run([sys.executable, "tools/build_graph.py", "--check"],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr


def test_validator_passes_on_committed_graph():
    p = subprocess.run([sys.executable, "tools/validate_graph.py"],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr


def test_validator_fails_on_planted_status_edit():
    graph = _graph()
    stubs = _load("atlas/stubs.json")["problems"]
    victim = next(n for n in graph["nodes"]
                  if n["type"] == "problem" and n["status"] == "wall")
    victim["status"] = "movable"  # the exact edit a claim would love to make
    errors = validate(graph, _load("atlas/graph/quarantine.json"), stubs, {})
    assert any("byte-equal" in e for e in errors)


def test_disagreement_cells_pinned():
    """#13/#21/#67: upstream closed the headline, our finite cell still moves.
    Both registers must survive — merging them loses the repo's niche."""
    nodes = {n["id"]: n for n in _graph()["nodes"]}
    for eid in (13, 21, 67):
        p = nodes[f"P{eid}"]
        assert p["status"] == "solved-upstream", (eid, p["status"])
        assert p["deep"]["beatable"] == "MOVABLE", (eid, p["deep"])


def test_trap_edges_pinned():
    traps = sorted(int(e["src"][1:]) for e in _graph()["edges"]
                   if e["type"] == "trap")
    assert traps == [19, 64, 97, 107, 114, 128, 548]
    for e in _graph()["edges"]:
        if e["type"] == "trap":
            assert "prize" in e, "prize must ride ON the trap edge"


def test_64_branch_split_survives():
    """#64 is walled on its general branch ($1000 trap) and live on its cubic
    sub-branch. What this pins is the SPLIT, not which live verdict the cubic
    branch currently carries — it moved TARGET -> MAYBE on 2026-07-27 when an
    unrefereed artifact pre-empted the n=30 cell, and the split still holds.
    Collapsing the two branches to one verdict is the failure mode."""
    graph = _graph()
    assert any(e["type"] == "trap" and e["src"] == "P64"
               for e in graph["edges"]), "#64 general branch must stay a trap"
    tri = next(n for n in graph["nodes"] if n["id"] == "S:triage:64")
    assert tri["verdict"] in ("TARGET", "MAYBE"), \
        "#64 cubic sub-branch must stay live, not collapse into the wall"
    card = (ROOT / "views" / "graph" / "P64.md").read_text(encoding="utf-8")
    assert card.index("TRAP") < card.index(tri["verdict"]), \
        "the trap must render before the live sub-branch on the card"


def test_366_two_branches_never_merge():
    graph = _graph()
    tri = next(n for n in graph["nodes"] if n["id"] == "S:triage:366")
    assert tri["verdict"] == "TARGET"
    gap_walled = [n for n in graph["nodes"]
                  if n["type"] == "surface" and n.get("overlay") == "gap_map"
                  and n.get("problem") == 366
                  and n.get("exact_feasibility") == "wall"]
    assert gap_walled, "#366's A060355 branch wall must survive beside the target"


def test_workable_predicate_is_imported_not_forked():
    from state_of_frontier import is_workable
    gap = _load("atlas/gap_map.json")["entries"]
    expected = sum(1 for e in gap if is_workable(e))
    got = sum(1 for e in _graph()["edges"]
              if e["type"] == "applies" and e["src"] == "M:witness-local-search"
              and e.get("predicate") == "workable")
    assert got == expected


def test_no_claim_sets_a_status():
    graph = _graph()
    stubs = {p["id"]: p for p in _load("atlas/stubs.json")["problems"]}
    for n in graph["nodes"]:
        if n["type"] == "problem":
            assert n["status"] == stubs[n["erdos_id"]]["status"]
        if n["type"] == "external_claim":
            assert n["status_changed_by_this_claim"] is False


def test_retraction_pins_stay_banned_in_every_view():
    contracts = _load("certificates/contracts.json")
    banned = [pin
              for c in contracts["claims"]
              for b in c.get("publication_bindings", [])
              for pin in b.get("must_not_contain", [])]
    assert banned, "expected at least one must_not_contain pin"
    views = [ROOT / "views" / "sorties.md"] \
        + sorted((ROOT / "views" / "graph").glob("*.md"))
    for path in views:
        text = path.read_text(encoding="utf-8")
        for pin in banned:
            assert pin not in text, (str(path), pin)


def test_licensing_firewall_on_link_only_problems():
    graph = _graph()
    for n in graph["nodes"]:
        if n["type"] == "problem" and n["statement_source"] == "link":
            assert "statement" not in n, n["id"]
            card = ROOT / "views" / "graph" / f"P{n['erdos_id']}.md"
            if card.exists():
                assert "## STATEMENT" not in card.read_text(encoding="utf-8")


def test_every_card_opens_with_stop():
    for path in sorted((ROOT / "views" / "graph").glob("P*.md")):
        h2s = [ln for ln in path.read_text(encoding="utf-8").splitlines()
               if ln.startswith("## ")]
        assert h2s and h2s[0].startswith("## STOP"), path.name


def test_card_token_budget():
    for path in sorted((ROOT / "views" / "graph").glob("P*.md")):
        size = len(path.read_text(encoding="utf-8"))
        assert size <= 12000, f"{path.name} is {size} chars — cards are " \
            "context packs, not dossiers"


def test_only_cited_implication_edges_cascade():
    for e in _graph()["edges"]:
        if e["type"] == "cascades_to":
            assert e["tier"] == "cited-implication" and e.get("citation")


def test_prize_is_never_a_ranking_key():
    """Standing rule 2, pinned over the rendered order: T3 ranks by
    feasibility class then problem id — recompute it from the ledger and
    require the view to match, so a prize-weighted sort would fail here."""
    from state_of_frontier import is_workable
    from build_graph import FEAS_ORDER
    gap = _load("atlas/gap_map.json")["entries"]
    expected = [e["problem"] for e in sorted(
        (e for e in gap if is_workable(e)),
        key=lambda e: (FEAS_ORDER[e["witness_feasibility"]], e["problem"]))]
    text = (ROOT / "views" / "sorties.md").read_text(encoding="utf-8")
    table = text.split("### T3")[1].split("### T4")[0]
    import re
    got = [int(m.group(1)) for m in
           (re.match(r"\| #(\d+) \|", ln) for ln in table.splitlines())
           if m]
    assert got == expected


def test_trap_lines_do_not_contradict_a_live_sub_branch():
    """#64 is walled on its general branch and TARGET on its cubic branch.
    The trap line must say branch-scoped, not 'the handle does not help'."""
    card = (ROOT / "views" / "graph" / "P64.md").read_text(encoding="utf-8")
    stop = card.split("## STOP")[1].split("## STATUS")[0]
    assert "TRAP (branch-scoped)" in stop
    assert "does not make it reachable here" not in stop


def test_retraction_pins_render_on_their_problems_cards():
    """#979 and #1107 both carry withdrawn stronger claims."""
    for eid in (979, 1107):
        card = (ROOT / "views" / "graph" / f"P{eid}.md").read_text(
            encoding="utf-8")
        stop = card.split("## STOP")[1].split("## STATUS")[0]
        assert "RETRACTION PIN" in stop, eid


def test_deep_audit_walls_are_reified():
    """beatable=WALL is a wall even without a wall_reason field: #139/#140/
    #166/#720 are named in atlas/walls.md and must not render as unwalled."""
    nodes = {n["id"]: n for n in _graph()["nodes"]}
    for eid in (139, 140, 166, 720):
        assert f"W:prob:{eid}" in nodes, eid
        stop = (ROOT / "views" / "graph" / f"P{eid}.md").read_text(
            encoding="utf-8").split("## STOP")[1].split("## STATUS")[0]
        assert "No recorded walls" not in stop, eid


def test_crater_import_keeps_its_caveats():
    """Everything JC-derived is conditional on an unconfirmed external
    counterexample; the import must not launder that into a settled fact."""
    crater = [n for n in _graph()["nodes"] if n["type"] == "crater_node"]
    assert crater
    for n in crater:
        assert "awaiting confirmation" in n["conditionality"]
        assert "lit_verification" in n and "verification" not in n
    root = next(n for n in crater if n["id"] == "jc:jacobian_conjecture")
    assert root["root_fact"]["fact"] == "REFUTED_ALL_N_GE_3"
    assert root["computed_status"]


def test_no_dangling_card_links_in_generated_views():
    import re
    cards = {p.name for p in (ROOT / "views" / "graph").glob("*.md")}
    for path in sorted((ROOT / "views" / "graph").glob("*.md")) \
            + [ROOT / "views" / "sorties.md"]:
        for ref in re.findall(r"views/graph/(P\d+\.md)",
                              path.read_text(encoding="utf-8")):
            assert ref in cards, f"{path.name} links missing card {ref}"


def test_markdown_tables_have_uniform_column_counts():
    """An unescaped pipe from free-text data silently misaligns a row."""
    for path in [ROOT / "views" / "sorties.md"] \
            + sorted((ROOT / "views" / "graph").glob("*.md")):
        rows, widths = [], []
        for ln in path.read_text(encoding="utf-8").splitlines():
            if ln.startswith("|"):
                rows.append(ln)
                widths.append(len(ln.replace("\\|", "").split("|")))
            elif rows:
                assert len(set(widths)) == 1, (path.name, rows[0][:60])
                rows, widths = [], []


def test_check_mode_detects_a_crlf_hand_edit():
    """Text-mode comparison would translate newlines and pass."""
    target = ROOT / "views" / "graph" / "P64.md"
    original = target.read_bytes()
    try:
        target.write_bytes(original.replace(b"\n", b"\r\n"))
        p = subprocess.run([sys.executable, "tools/build_graph.py", "--check"],
                           cwd=ROOT, capture_output=True, text=True)
        assert p.returncode == 1, "CRLF hand-edit passed the staleness gate"
    finally:
        target.write_bytes(original)


def test_node_id_collision_fails_closed():
    nodes = {}

    def add(nid):
        if nid in nodes:
            raise SystemExit("collision")
        nodes[nid] = 1
    add("X")
    try:
        add("X")
    except SystemExit:
        return
    raise AssertionError("add_node must fail closed on id reuse")


def test_quarantine_is_empty_in_v1():
    q = _load("atlas/graph/quarantine.json")
    assert q["entries"] == [], \
        "quarantine promotion requires quote anchors and its own review"


def test_cold_start_probe_graph_md_commands_run():
    """GRAPH.md is executable documentation: every CLI line it shows works."""
    text = (ROOT / "GRAPH.md").read_text(encoding="utf-8")
    cmds = [ln.strip() for ln in text.splitlines()
            if ln.strip().startswith("python3 tools/query_graph.py")]
    assert len(cmds) >= 6, "GRAPH.md lost its query examples"
    for cmd in cmds:
        argv = [sys.executable] + cmd.split("#", 1)[0].split()[1:]
        p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                           timeout=60)
        assert p.returncode == 0, (cmd, p.stdout + p.stderr)
        assert p.stdout.strip(), cmd
