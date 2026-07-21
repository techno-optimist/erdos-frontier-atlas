#!/usr/bin/env python3
"""Schema validation for a crater implication graph. Polarity-agnostic.

Every check here is about STRUCTURE (ids, required fields, edge endpoints,
citations, quarantine hygiene, root well-formedness) and is shared by every
crater regardless of which way its implications flow. The crater-specific
vocabulary arrives through the CraterSpec.
"""
import json

from .spec import NODE_VERIFICATION, failer


def load_graph(spec):
    """Parse + validate the crater graph. Returns (graph, {id: node})."""
    fail = failer(spec.label)
    g = json.loads(spec.graph_path.read_text())
    if g.get("schema") != spec.graph_schema:
        fail("bad schema tag")
    ids = [n["id"] for n in g["nodes"]]
    if len(ids) != len(set(ids)):
        fail("duplicate node ids")
    nodes = {n["id"]: n for n in g["nodes"]}
    for n in g["nodes"]:
        for field in ("id", "name", "statement", "verification", "primary_source"):
            if not str(n.get(field, "")).strip():
                fail(f"node {n.get('id','?')}: missing {field}")
        if n["verification"] not in NODE_VERIFICATION:
            fail(f"node {n['id']}: bad verification {n['verification']}")
        if n["verification"] == "VERIFIED" and not n.get("sources"):
            fail(f"node {n['id']}: VERIFIED but no sources[]")
        if "proven_theorem" in n and n["proven_theorem"] is not True:
            fail(f"node {n['id']}: proven_theorem must be literal true, not "
                 f"{n['proven_theorem']!r}")
        fact = n.get("independent_fact")
        if fact is not None:
            if spec.external is None:
                fail(f"node {n['id']}: independent_fact but the crater declares "
                     "no external level")
            if set(fact) != {"status", "citation"} or \
               fact["status"] != spec.external or \
               not str(fact["citation"]).strip():
                fail(f"node {n['id']}: malformed independent_fact")
            if n.get("proven_theorem"):
                fail(f"node {n['id']}: cannot be both proven_theorem and "
                     "independent_fact")
    # Index semantics declared per ORDERED pair. See engine.py: a mis-typed edge
    # launders FLOOR into FULL and the engine cannot detect it. This is the one
    # slice of that failure mode a machine CAN see -- the same ordered pair
    # declared both ways is a contradiction by construction, so one of the two
    # declarations is wrong. It catches contradictory typing only; a single,
    # consistently mis-typed edge passes, and always will.
    semantics_by_pair = {}
    for e in g["edges"]:
        if e["from"] not in nodes or e["to"] not in nodes:
            fail(f"edge {e['from']}->{e['to']}: unknown endpoint")
        if e["type"] not in spec.edge_types:
            fail(f"edge {e['from']}->{e['to']}: bad type {e['type']}")
        canon = spec.edge_semantics(e, fail)
        # ORDERED, deliberately. Opposite-direction edges between the same two
        # nodes legitimately differ: in the JC graph DC_n => JC_n is preserving
        # while JC_2n => DC_n is transforming. Only (from, to) repeating with
        # two different semantics is a contradiction.
        pair = (e["from"], e["to"])
        prior = semantics_by_pair.setdefault(pair, canon)
        if prior != canon:
            fail(f"edge {e['from']}->{e['to']}: two edges on this ORDERED pair "
                 f"disagree on index semantics ({prior} vs {canon}) -- one of "
                 "them is mis-typed; check both citations against the primary "
                 "source (a mis-typed edge silently upgrades the floor level to "
                 "the full one and nothing downstream can detect it)")
        if not str(e.get("citation", "")).strip():
            fail(f"edge {e['from']}->{e['to']}: missing citation")
        for end in (e["from"], e["to"]):
            if nodes[end]["verification"] != "VERIFIED":
                fail(f"edge {e['from']}->{e['to']}: endpoint {end} not VERIFIED "
                     "(quarantined nodes cannot carry edges)")
            if nodes[end].get("independent_fact"):
                # independent_fact nodes are historical CONTEXT leaves: their
                # status is fixed by an out-of-band citation and does not take
                # part in propagation. Forbidding incident edges makes the
                # engine's non-participation correct by construction (rather
                # than a silent under-derivation if an edge were added later).
                fail(f"edge {e['from']}->{e['to']}: endpoint {end} carries an "
                     "independent_fact and must stay an unconnected context node")
    quarantine = g.get("quarantine_findings", {})
    q_ids = [q["id"] for section in spec.quarantine_sections
             for q in quarantine.get(section, [])]
    if len(q_ids) != len(set(q_ids)):
        fail("duplicate ids in quarantine_findings")
    for section in spec.quarantine_sections:
        for q in quarantine.get(section, []):
            if q["id"] in nodes:
                fail(f"quarantined id {q['id']} collides with an admitted node")
            if not str(q.get("finding", "")).strip():
                fail(f"quarantined id {q['id']}: empty finding")
    seen_roots = set()
    for r in g["roots"]:
        if r["node"] not in nodes:
            fail(f"root {r['node']}: unknown node")
        if r["node"] in seen_roots:
            fail(f"root {r['node']}: duplicate root entry")
        seen_roots.add(r["node"])
        if r["fact"] not in spec.root_facts():
            fail(f"root {r['node']}: bad fact {r['fact']}")
        if not str(r.get("certificate", "")).strip():
            fail(f"root {r['node']}: missing certificate")
        # A root SEEDS a status by assignment, so it must not silently override
        # or launder a node's own declared nature.
        rn = nodes[r["node"]]
        if rn["verification"] != "VERIFIED":
            fail(f"root {r['node']}: node is not VERIFIED "
                 "(a quarantined candidate cannot be a certified root)")
        if rn.get("proven_theorem") and r["fact"] != spec.immune:
            fail(f"root {r['node']}: node is a proven_theorem but the root "
                 f"asserts {r['fact']} (inconsistent)")
        if rn.get("independent_fact") and \
           r["fact"] != rn["independent_fact"]["status"]:
            fail(f"root {r['node']}: conflicts with the node's independent_fact")
    return g, nodes


def count_quarantined(spec, g):
    q = g.get("quarantine_findings", {})
    return sum(len(q.get(s, [])) for s in spec.quarantine_sections)
