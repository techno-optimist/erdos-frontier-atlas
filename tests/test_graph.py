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


def test_two_builds_are_byte_identical():
    a = build_graph.emit()
    b = build_graph.emit()
    assert {str(k): v for k, v in a.items()} == {str(k): v for k, v in b.items()}


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
    graph = _graph()
    assert any(e["type"] == "trap" and e["src"] == "P64"
               for e in graph["edges"]), "#64 general branch must stay a trap"
    tri = next(n for n in graph["nodes"] if n["id"] == "S:triage:64")
    assert tri["verdict"] == "TARGET", "#64 cubic branch must stay a target"
    card = (ROOT / "views" / "graph" / "P64.md").read_text(encoding="utf-8")
    assert card.index("TRAP") < card.index("TARGET"), \
        "the trap must render before the target on the card"


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
        argv = [sys.executable] + cmd.split()[1:]
        argv = [a.split("#")[0] for a in argv if not a.startswith("#")]
        p = subprocess.run([a for a in argv if a], cwd=ROOT,
                           capture_output=True, text=True, timeout=60)
        assert p.returncode == 0, (cmd, p.stdout + p.stderr)
        assert p.stdout.strip(), cmd
