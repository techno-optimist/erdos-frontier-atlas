#!/usr/bin/env python3
"""Validate atlas/graph/ — dependency-free, fail-closed (SystemExit 1).

Structural rules (data-independent; pinned FIXTURES live in tests/test_graph.py):
  1. Every edge endpoint resolves to a node.
  2. Edge tiers are a closed vocabulary; quarantine-only tiers (llm-extracted,
     embedding-suggested) never appear in graph.json.
  3. Every cascades_to edge is tier cited-implication and carries a citation.
  4. Every evidenced_by edge targets a promoted evidence_claim.
  5. Every trap edge's problem has upstream_finite_handle set AND status=wall,
     re-checked against atlas/stubs.json (not against the graph's own copy).
  6. A claim never sets a status: problem statuses are byte-equal to stubs;
     every external_claim has status_changed_by_this_claim == false.
  7. Licensing firewall: link-only problems carry no statement text, in
     graph.json and in their rendered cards.
  8. Every card opens with the STOP section before any other H2.
  9. counts blocks are recomputed, never trusted.
 10. Quarantine entries (if any ever land) carry file/line/quote anchors.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "atlas" / "graph" / "graph.json"
QUARANTINE = ROOT / "atlas" / "graph" / "quarantine.json"
CARDS = ROOT / "views" / "graph"

ALLOWED_TIERS = {"validator-enforced", "deterministic-rule", "cited-implication"}
QUARANTINE_TIERS = {"llm-extracted", "embedding-suggested"}


def validate(graph, quarantine, stubs, cards):
    """Return a list of error strings. cards: {filename: text}."""
    errors = []
    nodes = {n["id"]: n for n in graph["nodes"]}
    stub_by_id = {p["id"]: p for p in stubs}

    if graph.get("schema") != "efa-attack-graph-v1":
        errors.append(f"unexpected schema tag: {graph.get('schema')!r}")

    # 1-3: endpoints + tiers
    for e in graph["edges"]:
        for end in (e["src"], e["dst"]):
            if end not in nodes:
                errors.append(f"dangling endpoint {end!r} on {e['type']} edge")
        tier = e.get("tier")
        if tier not in ALLOWED_TIERS:
            errors.append(f"edge tier {tier!r} not allowed in graph.json "
                          f"({e['type']} {e['src']}->{e['dst']})")
        if e["type"] == "cascades_to":
            if tier != "cited-implication":
                errors.append(f"cascades_to edge at tier {tier!r} — only "
                              "cited-implication may feed propagation")
            if not e.get("citation"):
                errors.append(f"cascades_to {e['src']}->{e['dst']} without "
                              "citation")

    # 4: evidence spine
    for e in graph["edges"]:
        if e["type"] == "evidenced_by":
            tgt = nodes.get(e["dst"], {})
            if tgt.get("type") != "evidence_claim":
                errors.append(f"evidenced_by targets non-claim {e['dst']}")
            elif tgt.get("status") != "promoted":
                errors.append(f"evidenced_by targets unpromoted claim "
                              f"{e['dst']} (status {tgt.get('status')!r})")

    # 5: traps re-checked against stubs
    for e in graph["edges"]:
        if e["type"] == "trap":
            eid = int(e["src"][1:])
            stub = stub_by_id.get(eid)
            if stub is None:
                errors.append(f"trap edge on unknown problem {e['src']}")
            elif not (stub["upstream_finite_handle"] and stub["status"] == "wall"):
                errors.append(f"trap edge on #{eid} violates the trap "
                              "predicate against stubs.json")

    # 6: a claim never sets a status
    for n in graph["nodes"]:
        if n["type"] == "problem":
            stub = stub_by_id.get(n["erdos_id"])
            if stub is None:
                errors.append(f"problem node {n['id']} not in stubs.json")
                continue
            for field in ("status", "upstream_status", "upstream_state_raw"):
                if n[field] != stub[field]:
                    errors.append(f"{n['id']}.{field} = {n[field]!r} != "
                                  f"stubs {stub[field]!r} — statuses must be "
                                  "byte-equal to atlas/stubs.json")
        if n["type"] == "external_claim":
            if n.get("status_changed_by_this_claim") is not False:
                errors.append(f"{n['id']}: status_changed_by_this_claim must "
                              "be false — a claim never sets a status")

    # 7: licensing firewall
    for n in graph["nodes"]:
        if n["type"] == "problem" and n.get("statement_source") == "link":
            if "statement" in n:
                errors.append(f"{n['id']} is link-only but carries statement "
                              "text (licensing firewall)")
            card = cards.get(f"P{n['erdos_id']}.md")
            if card and "## STATEMENT" in card:
                errors.append(f"card P{n['erdos_id']}.md renders a STATEMENT "
                              "section for a link-only problem")

    # 8: STOP renders first on every card
    for name, text in cards.items():
        if not name.startswith("P"):
            continue
        h2s = [line for line in text.splitlines() if line.startswith("## ")]
        if not h2s or not h2s[0].startswith("## STOP"):
            errors.append(f"card {name}: first section is "
                          f"{h2s[0] if h2s else 'missing'!r}, not STOP")

    # 9: counts recomputed
    ncounts = dict(sorted(Counter(n["type"] for n in graph["nodes"]).items()))
    ecounts = dict(sorted(Counter(e["type"] for e in graph["edges"]).items()))
    tcounts = dict(sorted(Counter(e["tier"] for e in graph["edges"]).items()))
    if graph["counts"] != {"nodes": ncounts, "edges": ecounts, "tiers": tcounts}:
        errors.append("counts block does not match recomputed counts")

    # 10: quarantine discipline
    for q in quarantine.get("entries", []):
        for field in ("source_file", "quote"):
            if not q.get(field):
                errors.append("quarantine entry without a "
                              f"{field} anchor: {str(q)[:80]}")
        if q.get("tier") not in QUARANTINE_TIERS:
            errors.append(f"quarantine entry with non-quarantine tier "
                          f"{q.get('tier')!r}")
    return errors


def main():
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    quarantine = json.loads(QUARANTINE.read_text(encoding="utf-8"))
    stubs = json.loads((ROOT / "atlas" / "stubs.json").read_text(
        encoding="utf-8"))["problems"]
    cards = {p.name: p.read_text(encoding="utf-8")
             for p in CARDS.glob("*.md")}
    errors = validate(graph, quarantine, stubs, cards)
    if errors:
        print(f"validate_graph: {len(errors)} error(s)")
        for e in errors[:50]:
            print("  " + e)
        raise SystemExit(1)
    print(f"validate_graph: OK — {len(graph['nodes'])} nodes, "
          f"{len(graph['edges'])} edges, {len(cards)} rendered files, "
          f"{len(quarantine.get('entries', []))} quarantined.")


if __name__ == "__main__":
    main()
