#!/usr/bin/env python3
"""Build atlas/graph/ — the attack graph (SORTIE, schema efa-attack-graph-v1).

The graph's unit of value is the MOVE, not the problem: every node and edge
exists to answer "I have N hours of compute and this toolchain: where do I
strike, what exactly do I run, what must my receipt contain to be promotable,
and what must I NOT touch?" — routed through the repo's own honesty machinery.

Inputs (committed artifacts only; this tool reads nothing else):
  atlas/stubs.json                     1217 problem stubs (three-register status)
  atlas/problems.json                  51 deep audited records
  atlas/gap_map.json                   222 bounded-quantity surfaces
  atlas/finite_handle_triage.json      43 feasibility-triaged branches
  atlas/ai_claims.json                 89 external AI claims (never set status)
  atlas/lean_lane.json                 external Lean formalization pins
  atlas/effectivization_shortlist.json plausible + dead_do_not_rehunt ledgers
  certificates/contracts.json          promoted claims + replay contracts
  atlas/jc-crater/implication_graph.json  cited-implication island (T1)
  tools/state_of_frontier.py           is_workable — imported, never forked

Outputs (all deterministic: no timestamps, sorted keys, byte-identical on
regeneration from unchanged inputs — that is what makes --check meaningful):
  atlas/graph/graph.json       nodes + tiered edges + verbatim predicates
  atlas/graph/quarantine.json  LLM-extracted / suggestion-tier material (v1: empty)
  views/sorties.md             the Quartermaster: do-not-spend first, then strikes
  views/graph/P<id>.md         one attack card per problem with graph content
  views/graph/INDEX.md         card index

  python3 tools/build_graph.py            # (re)write all outputs
  python3 tools/build_graph.py --check    # exit 1 if any committed output is stale

Standing rules. Rules 1, 3, 4 and 5 are gated by tools/validate_graph.py +
tests/test_graph.py; rule 2 holds by construction — the ranking predicate
never reads `prize` — and is pinned by a test over the rendered order:
  1. A claim NEVER sets a status — statuses in the graph are byte-equal to
     atlas/stubs.json.
  2. Prizes are history, not targets — a prize renders beside its trap warning,
     never as a ranking key.
  3. Walls render before temptation — every card opens with STOP; the sorties
     view opens with DO-NOT-SPEND.
  4. Only cited-implication edges may ever feed status propagation; LLM- or
     embedding-suggested edges live in quarantine.json and carry zero weight.
  5. Link-only problems carry no statement text (the licensing firewall).
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from state_of_frontier import is_workable  # noqa: E402  (imported, never forked)

GRAPH_DIR = ROOT / "atlas" / "graph"
VIEWS_DIR = ROOT / "views" / "graph"
SORTIES = ROOT / "views" / "sorties.md"

SCHEMA = "efa-attack-graph-v1"

# ---------------------------------------------------------------- predicates
# Every mechanical rule the builder applies, stated verbatim. These strings
# ship inside graph.json; tests pin the implementation to them.
PREDICATES = {
    "workable": (
        "APPLIES(witness-local-search, gap surface) iff "
        "status == 'open' AND witness_side != 'none' AND "
        "witness_feasibility in ('open-easy', 'plausible') "
        "— imported from tools/state_of_frontier.is_workable, never forked."
    ),
    "lane-move": (
        "APPLIES(<lane>, deep surface) iff problems.json lane not in "
        "('wall',) — the lane field is authoritative (see atlas/lanes.md)."
    ),
    "triage-move": (
        "APPLIES(finite-witness-search, triage surface) iff "
        "finite_handle_triage verdict in ('TARGET', 'MAYBE')."
    ),
    "hot-claim": (
        "APPLIES(external-claim-replay, problem) iff an ai_claims entry has "
        "our_recorded_status in ('open', 'wall', 'movable') — a live claim "
        "against a problem we record unresolved is a verification target, "
        "never a status change."
    ),
    "trap": (
        "TRAP(problem) iff stubs upstream_finite_handle is set AND stubs "
        "status == 'wall' — upstream says a finite object could settle it, "
        "our status register records a wall. That wall may be BRANCH-SCOPED: "
        "a triage surface on the same card can carry a live TARGET/MAYBE "
        "sub-branch (#64 is exactly this). The predicate reads the two "
        "registers and nothing else; the reason lives in atlas/walls.md and "
        "on the surfaces. The prize rides ON the edge so renderers must show "
        "temptation and trap together."
    ),
    "strike-ranking": (
        "Strike tiers, in order: T1 triage TARGET branches; T2 movable "
        "boards (stubs status='movable' UNION deep beatable='MOVABLE'); "
        "T3 workable gap surfaces (the 'workable' predicate); T4 triage "
        "MAYBE branches. Within a tier: witness_feasibility class "
        "('historic' < 'open-easy' < 'plausible' < 'hard'), then problem id "
        "ascending. Prize is NEVER a key (standing rule 2)."
    ),
}

STANDING_RULES = [
    "A claim never sets a status: graph statuses are byte-equal to atlas/stubs.json.",
    "Prizes are history, not targets: a prize renders beside its trap warning, never as a ranking key.",
    "Walls render before temptation: every card opens with STOP; sorties opens with DO-NOT-SPEND.",
    "Only cited-implication edges feed propagation; LLM/embedding suggestions stay in quarantine.json at zero weight.",
    "Link-only problems carry no statement text (licensing firewall: no erdosproblems.com prose).",
]

SOURCES = [
    "atlas/stubs.json",
    "atlas/problems.json",
    "atlas/gap_map.json",
    "atlas/finite_handle_triage.json",
    "atlas/ai_claims.json",
    "atlas/lean_lane.json",
    "atlas/effectivization_shortlist.json",
    "certificates/contracts.json",
    "atlas/jc-crater/implication_graph.json",
    "atlas/jc-crater/computed_statuses.json",
]

# Carried onto every imported crater node: the whole island is downstream of
# an external counterexample that has not been confirmed.
CRATER_CONDITIONALITY = (
    "Conditional on Levent Alpöge's 2026-07-19 dim-3 counterexample "
    "(external; 'awaiting confirmation', not yet peer-reviewed). "
    "`lit_verification` records that an independent literature agent matched "
    "the statement to a primary source — it is NOT a truth verdict. "
    "`computed_status` is a conservative machine-propagated floor "
    "(tools/validate_jc_crater.py), not a hand analysis."
)

FEAS_ORDER = {"historic": 0, "open-easy": 1, "plausible": 2, "hard": 3, "none": 4}

MOVES = [
    {
        "id": "M:witness-local-search",
        "name": "witness local search",
        "what": "search for a single finite witness that strictly improves a recorded bound; the entry's stated verifier adjudicates",
        "predicate": "workable",
    },
    {
        "id": "M:exact-backtracking",
        "name": "exact backtracking",
        "what": "exhaustive exact-arithmetic search over a bounded space, emitting a completeness certificate",
        "predicate": "lane-move",
    },
    {
        "id": "M:SAT+DRAT-nonexistence",
        "name": "SAT + DRAT nonexistence",
        "what": "encode the finite case as CNF, certify UNSAT with a DRAT proof (replayable, dependency-pinned)",
        "predicate": "lane-move",
    },
    {
        "id": "M:LP/SDP-certificate",
        "name": "LP/SDP certificate",
        "what": "rational-certified linear/semidefinite bound with exact dual verification",
        "predicate": "lane-move",
    },
    {
        "id": "M:finite-witness-search",
        "name": "finite-handle witness search",
        "what": "attack the smallest untested case of an upstream decidable/falsifiable/verifiable handle",
        "predicate": "triage-move",
    },
    {
        "id": "M:external-claim-replay",
        "name": "external claim replay",
        "what": "independently verify a hot external AI claim against a problem we record unresolved; the verdict lands as evidence, never as a status edit",
        "predicate": "hot-claim",
    },
    {
        "id": "M:literature-freshness-check",
        "name": "literature freshness check",
        "what": "before any strike: re-check erdosproblems.com/<id>, OEIS history, DS1-class surveys, arXiv — the #552/DS1 retraction is why this move exists",
        "predicate": None,
    },
]


def h8(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def clip(text, limit=700):
    """Deterministic prose truncation for cards."""
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + " …[truncated; see source]"


def cell(text, limit=700):
    """clip() for a markdown table cell: pipes would break the row."""
    return clip(text, limit).replace("|", "\\|")


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ builders
def build_graph():
    stubs = load("atlas/stubs.json")["problems"]
    deep = {p["id"]: p for p in load("atlas/problems.json")["problems"]}
    gap = load("atlas/gap_map.json")["entries"]
    triage_doc = load("atlas/finite_handle_triage.json")
    triage = triage_doc["entries"]
    triage_vintage = triage_doc["triaged"]
    ai = load("atlas/ai_claims.json")["entries"]
    lean_lane = load("atlas/lean_lane.json")["records"]
    effect = load("atlas/effectivization_shortlist.json")
    contracts = load("certificates/contracts.json")
    crater = load("atlas/jc-crater/implication_graph.json")

    stub_by_id = {p["id"]: p for p in stubs}
    nodes = {}   # id -> node dict
    edges = []

    def add_node(nid, ntype, **attrs):
        # Fail closed: a silent overwrite would drop a ledger row invisibly.
        # Intended-reuse sites guard with `if nid not in nodes` before calling.
        if nid in nodes:
            raise SystemExit(f"build_graph: node id collision on {nid!r} "
                             f"({nodes[nid]['type']} vs {ntype})")
        node = {"id": nid, "type": ntype}
        node.update(attrs)
        nodes[nid] = node
        return node

    def add_edge(etype, src, dst, tier, source, **attrs):
        e = {"type": etype, "src": src, "dst": dst, "tier": tier,
             "source": source}
        e.update(attrs)
        edges.append(e)
        return e

    # -- problems (three-register status; statuses byte-equal to stubs) ------
    for p in stubs:
        pid = f"P{p['id']}"
        attrs = {
            "erdos_id": p["id"],
            "status": p["status"],
            "upstream_status": p["upstream_status"],
            "upstream_state_raw": p["upstream_state_raw"],
            "upstream_finite_handle": p["upstream_finite_handle"],
            "prize": p["prize"],
            "tags": p["tags"],
            "msc": sorted({m.zfill(2) for m in p.get("msc", [])}),
            "oeis": sorted(set(p.get("oeis", []))
                           | set((deep.get(p["id"], {}).get("links") or {}).get("oeis", []))),
            "oeis_stub_only": sorted(set(p.get("oeis", []))),
            "statement_source": p["statement_source"],
            "erdos_url": p["erdos_url"],
        }
        if p["statement_source"] == "lean" and p.get("statement"):
            attrs["statement"] = p["statement"]
        fz = p.get("formalized") or {}
        if fz.get("in_lean"):
            attrs["lean"] = {"path": fz.get("lean_path"),
                             "formal_status": fz.get("formal_status"),
                             "answer": fz.get("answer")}
        if p["id"] in deep:
            d = deep[p["id"]]
            attrs["deep"] = {
                "title": d["title"],
                "beatable": d["beatable"],
                "lane": d["lane"],
                "board_class": d["board_class"],
                "fit_score": d["fit_score"],
                "impact_score": d["impact_score"],
            }
        add_node(pid, "problem", **attrs)

    # -- surfaces: one per overlay row; never merged across overlays ---------
    for e in gap:
        sid = f"S:gap:{e['problem']}:{h8(e['quantity'])}"
        add_node(sid, "surface",
                 overlay="gap_map", problem=e["problem"],
                 quantity=e["quantity"], kind=e["kind"],
                 lower=e["lower"], upper=e["upper"],
                 witness_side=e["witness_side"],
                 witness_object=e["witness_object"],
                 witness_verifier=e["witness_verifier"],
                 witness_feasibility=e["witness_feasibility"],
                 exact_feasibility=e["exact_feasibility"],
                 status=e["status"], confidence=e["confidence"],
                 oeis=e["oeis"], notes=e["notes"],
                 evidence=e["evidence"])
        add_edge("has_surface", f"P{e['problem']}", sid,
                 "deterministic-rule", "atlas/gap_map.json")
        if e["oeis"]:
            add_edge("measures", sid, f"O:{e['oeis']}",
                     "deterministic-rule", "atlas/gap_map.json")
        if is_workable(e):
            add_edge("applies", "M:witness-local-search", sid,
                     "deterministic-rule", "atlas/gap_map.json",
                     predicate="workable")
        if e["exact_feasibility"] == "wall":
            wid = f"W:gap:{e['problem']}:{h8(e['quantity'])}"
            add_node(wid, "wall", scope="surface",
                     reason=clip(e["notes"], 500),
                     source="atlas/gap_map.json exact_feasibility=wall",
                     witness_side_note=(
                         "witness side may remain live — check witness_feasibility"
                         if e["witness_feasibility"] in ("open-easy", "plausible", "historic")
                         else None))
            add_edge("walled", sid, wid, "deterministic-rule",
                     "atlas/gap_map.json")

    for pid_, d in sorted(deep.items()):
        sid = f"S:deep:{pid_}"
        add_node(sid, "surface",
                 overlay="problems.json", problem=pid_,
                 finite_object=d["finite_object"],
                 current_record=clip(d["current_record"], 900),
                 frontier=d.get("frontier"),
                 verifier=clip(d["verifier"], 700),
                 attack=clip(d["attack"], 700),
                 beatable=d["beatable"], lane=d["lane"],
                 board_class=d["board_class"])
        add_edge("has_surface", f"P{pid_}", sid,
                 "deterministic-rule", "atlas/problems.json")
        if d["lane"] != "wall":
            add_edge("applies", f"M:{d['lane']}", sid,
                     "deterministic-rule", "atlas/problems.json",
                     predicate="lane-move")
        if d.get("wall_reason"):
            wid = f"W:prob:{pid_}"
            add_node(wid, "wall", scope="problem",
                     reason=clip(d["wall_reason"], 900),
                     source="atlas/problems.json wall_reason")
            add_edge("walled", f"P{pid_}", wid, "deterministic-rule",
                     "atlas/problems.json")

    for e in triage:
        sid = f"S:triage:{e['erdos_id']}"
        add_node(sid, "surface",
                 overlay="finite_handle_triage", problem=e["erdos_id"],
                 verdict=e["verdict"],
                 upstream_handle=clip(e["upstream_handle"], 300),
                 statement_short=clip(e["statement_short"], 700),
                 what_a_witness_is=clip(e["what_a_witness_is"], 700),
                 smallest_untested_case=clip(e["smallest_untested_case"], 500),
                 known_computational_frontier=clip(e["known_computational_frontier"], 500),
                 search_space_estimate=clip(e["search_space_estimate"], 400),
                 verification_is_cheap_and_exact=bool(
                     e["verification_is_cheap_and_exact"]),
                 verdict_reason=clip(e["verdict_reason"], 700))
        add_edge("has_surface", f"P{e['erdos_id']}", sid,
                 "deterministic-rule", "atlas/finite_handle_triage.json")
        if e["verdict"] in ("TARGET", "MAYBE"):
            add_edge("applies", "M:finite-witness-search", sid,
                     "deterministic-rule", "atlas/finite_handle_triage.json",
                     predicate="triage-move")
        else:
            wid = f"W:triage:{e['erdos_id']}"
            add_node(wid, "wall", scope="surface",
                     reason=clip(e["verdict_reason"], 700),
                     source="atlas/finite_handle_triage.json verdict=WALL")
            add_edge("walled", sid, wid, "deterministic-rule",
                     "atlas/finite_handle_triage.json")

    # deep-audit walls: beatable=WALL is a wall even when wall_reason is empty
    # (#139/#140/#166/#720 are named in atlas/walls.md but carry no
    # wall_reason field, and would otherwise render as "no recorded walls").
    for pid_, d in sorted(deep.items()):
        if d["beatable"] == "WALL" and f"W:prob:{pid_}" not in nodes:
            wid = f"W:prob:{pid_}"
            add_node(wid, "wall", scope="problem",
                     reason=clip(d.get("beatable_reason")
                                 or "deep audit records beatable=WALL — "
                                    "see atlas/walls.md", 900),
                     source="atlas/problems.json beatable=WALL")
            add_edge("walled", f"P{pid_}", wid, "deterministic-rule",
                     "atlas/problems.json")

    # problem-scope walls from stubs, where neither deep path gave a wall node
    for p in stubs:
        if p["status"] == "wall" and f"W:prob:{p['id']}" not in nodes:
            wid = f"W:prob:{p['id']}"
            add_node(wid, "wall", scope="problem",
                     reason="catalogued wall — see atlas/walls.md",
                     source="atlas/stubs.json status=wall")
            add_edge("walled", f"P{p['id']}", wid, "deterministic-rule",
                     "atlas/stubs.json")

    # -- traps: finite handle x wall, prize on the edge ----------------------
    for p in stubs:
        if p["upstream_finite_handle"] and p["status"] == "wall":
            add_edge("trap", f"P{p['id']}", f"W:prob:{p['id']}",
                     "deterministic-rule", "atlas/stubs.json",
                     predicate="trap", prize=p["prize"],
                     upstream_finite_handle=p["upstream_finite_handle"])

    # -- moves ---------------------------------------------------------------
    for m in MOVES:
        add_node(m["id"], "move", name=m["name"], what=m["what"],
                 predicate=m["predicate"])

    # -- evidence: promoted contract claims + certificate containers ---------
    for c in contracts["claims"]:
        cid = f"E:claim:{c['id']}"
        replay = None
        for r in c.get("replays", []):
            if r.get("certifies_claim"):
                replay = {"argv": r["argv"], "profile": r["profile"],
                          "stdout_contains": r.get("stdout_contains", [])}
                break
        add_node(cid, "evidence_claim", claim_id=c["id"], status=c["status"],
                 statement=c["statement"], scope=c.get("scope"),
                 artifacts=c.get("artifacts", []), replay=replay)
        # deterministic claim->problem link: erdos-<id>-... claim id prefix
        parts = c["id"].split("-")
        if parts[0] == "erdos" and parts[1].isdigit():
            eid = int(parts[1])
            if eid in stub_by_id:
                add_edge("evidenced_by", f"P{eid}", cid,
                         "validator-enforced", "certificates/contracts.json",
                         rule="claim id prefix erdos-<id>")
        for b in c.get("publication_bindings", []):
            for pin in b.get("must_not_contain", []):
                iid = f"I:pin:{h8(pin)}"
                if iid not in nodes:
                    add_node(iid, "incident", kind="retraction_pin",
                             banned_string=pin,
                             source="certificates/contracts.json must_not_contain")
                add_edge("retracts", iid, cid, "validator-enforced",
                         "certificates/contracts.json")
    for d in contracts["directories"]:
        did = f"E:dir:{d['path'].replace('/', ':')}"
        add_node(did, "evidence_container", path=d["path"],
                 classification=d["classification"], boundary=d["boundary"])

    # -- external claims (never set status) ----------------------------------
    for c in ai:
        xid = f"X:ai:{c['erdos_id']}:{h8(c['claim_title'])}"
        hot = c["our_recorded_status"] in ("open", "wall", "movable")
        add_node(xid, "external_claim", origin="ai_claims",
                 erdos_id=c["erdos_id"], claim_title=c["claim_title"],
                 our_recorded_status=c["our_recorded_status"],
                 our_verdict=c["our_verdict"], hot=hot,
                 status_changed_by_this_claim=c["status_changed_by_this_claim"],
                 registry_says_not_a_resolution=c.get("registry_says_not_a_resolution"))
        add_edge("claims_about", xid, f"P{c['erdos_id']}",
                 "deterministic-rule", "atlas/ai_claims.json", hot=hot)
        if hot:
            add_edge("applies", "M:external-claim-replay", f"P{c['erdos_id']}",
                     "deterministic-rule", "atlas/ai_claims.json",
                     predicate="hot-claim")
    for r in lean_lane:
        xid = f"X:lean:{r['erdos_problem']}"
        add_node(xid, "external_claim", origin="lean_lane",
                 erdos_id=r["erdos_problem"], claim_title=r["title"],
                 repository=r["repository"], commit=r["commit"],
                 lane_status=r["status"], hot=False,
                 status_changed_by_this_claim=False)
        add_edge("claims_about", xid, f"P{r['erdos_problem']}",
                 "deterministic-rule", "atlas/lean_lane.json", hot=False)

    # -- incidents: dead_do_not_rehunt + campaign findings -------------------
    for d in effect.get("dead_do_not_rehunt", []):
        iid = f"I:dead:{h8(d['name'])}"
        add_node(iid, "incident", kind="dead_do_not_rehunt",
                 name=d["name"], source_ref=clip(d["erdos_or_source"], 400),
                 source="atlas/effectivization_shortlist.json")
    for pid_, d in sorted(deep.items()):
        cf = d.get("campaign_finding")
        if cf:
            iid = f"I:campaign:{pid_}"
            add_node(iid, "incident", kind="campaign_finding",
                     problem=pid_, finding=clip(cf, 700),
                     source="atlas/problems.json campaign_finding")
            add_edge("learned_from", f"P{pid_}", iid, "deterministic-rule",
                     "atlas/problems.json")

    # -- bridges: OEIS / tag / MSC -------------------------------------------
    oeis_members = {}
    for p in stubs:
        pid = f"P{p['id']}"
        for o in nodes[pid]["oeis"]:
            oeis_members.setdefault(o, []).append(p["id"])
        for t in p["tags"]:
            tid = f"T:{t.replace(' ', '-')}"
            if tid not in nodes:
                add_node(tid, "tag", name=t)
            add_edge("tagged", pid, tid, "deterministic-rule",
                     "atlas/stubs.json")
        for m in nodes[pid]["msc"]:
            mid = f"MSC:{m}"
            if mid not in nodes:
                add_node(mid, "msc", code=m)
            add_edge("classified", pid, mid, "deterministic-rule",
                     "atlas/stubs.json", note="zero-padding normalized at build")
    for e in gap:
        if e["oeis"]:
            oeis_members.setdefault(e["oeis"], [])
    for o in sorted(oeis_members):
        members = sorted(set(oeis_members[o]))
        add_node(f"O:{o}", "oeis_seq", a_number=o, problems=members)
        for pid_ in members:
            add_edge("references", f"P{pid_}", f"O:{o}",
                     "deterministic-rule",
                     "atlas/stubs.json oeis UNION problems.json links.oeis")
    # same_family: one edge per unordered problem pair sharing >=1 sequence
    fam = {}
    for o, members in oeis_members.items():
        ms = sorted(set(members))
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                fam.setdefault((ms[i], ms[j]), []).append(o)
    for (a, b), seqs in sorted(fam.items()):
        add_edge("same_family", f"P{a}", f"P{b}", "deterministic-rule",
                 "atlas/stubs.json oeis UNION problems.json links.oeis",
                 shared=sorted(seqs))

    # -- crater import: the cited-implication island (T1) --------------------
    # Everything JC-derived is conditional on an EXTERNAL counterexample that
    # is still awaiting confirmation. The caveats travel with the nodes, or
    # the import would launder "awaiting confirmation" into "settled".
    crater_statuses = load("atlas/jc-crater/computed_statuses.json")["statuses"]
    crater_roots = {r["node"]: r for r in crater["roots"]}
    for n in crater["nodes"]:
        computed = crater_statuses.get(n["id"], {})
        node = {
            "name": n["name"],
            # NOT truth-of-statement: this records that an independent
            # literature agent verified the statement against a primary source.
            "lit_verification": n["verification"],
            "computed_status": computed.get("status"),
            "orphaned_conditional_support": computed.get(
                "orphaned_conditional_support"),
            "pre_2026_status": n.get("pre_2026_status"),
            "notes": clip(n.get("notes", ""), 600),
            "statement": clip(n.get("statement", ""), 500),
            "primary_source": clip(n.get("primary_source", ""), 300),
            "conditionality": CRATER_CONDITIONALITY,
        }
        if n["id"] in crater_roots:
            r = crater_roots[n["id"]]
            node["root_fact"] = {"fact": r["fact"],
                                 "certificate": r["certificate"],
                                 "note": clip(r.get("note", ""), 400)}
        add_node(f"jc:{n['id']}", "crater_node", **node)
    for e in crater["edges"]:
        add_edge("cascades_to", f"jc:{e['from']}", f"jc:{e['to']}",
                 "cited-implication", "atlas/jc-crater/implication_graph.json",
                 crater_type=e["type"],
                 dimension_semantics=e.get("dimension_semantics"),
                 citation=clip(e.get("citation", ""), 400))

    # -- counts (recomputed, never asserted) ---------------------------------
    from collections import Counter
    ncounts = Counter(n["type"] for n in nodes.values())
    ecounts = Counter(e["type"] for e in edges)
    tiers = Counter(e["tier"] for e in edges)

    graph = {
        "schema": SCHEMA,
        "note": ("Generated by tools/build_graph.py — regenerate with "
                 "`make graph`, do not hand-edit. `make check-graph` fails "
                 "if this file is stale. Any disagreement with this graph "
                 "is a bug report against its SOURCES, never a patch here."),
        "sources": SOURCES,
        "standing_rules": STANDING_RULES,
        "predicates": PREDICATES,
        "source_vintages": {"finite_handle_triage": triage_vintage},
        "counts": {
            "nodes": dict(sorted(ncounts.items())),
            "edges": dict(sorted(ecounts.items())),
            "tiers": dict(sorted(tiers.items())),
        },
        "nodes": [nodes[k] for k in sorted(nodes)],
        "edges": sorted(edges, key=lambda e: (e["type"], e["src"], e["dst"])),
    }
    quarantine = {
        "schema": SCHEMA + "/quarantine",
        "note": ("LLM-extracted and suggestion-tier material lands here with "
                 "mandatory file/line/quote anchors, zero ranking weight, "
                 "and zero propagation, until promoted with a cited source "
                 "(the jc-crater quarantine discipline). Empty in v1: the "
                 "committed graph is 100% deterministic."),
        "entries": [],
    }
    return graph, quarantine


# ------------------------------------------------------------------ renderers
def _wall_lines(graph, pid):
    """STOP-section lines for problem P<id>: traps, walls, retraction pins."""
    nodes = {n["id"]: n for n in graph["nodes"]}
    erdos_id = int(pid[1:])
    lines = []
    # A live sub-branch on the same problem: the trap line must not claim the
    # handle is dead everywhere when our own triage says one branch is alive.
    live_branch = next(
        (n for n in graph["nodes"]
         if n["type"] == "surface"
         and n.get("overlay") == "finite_handle_triage"
         and n.get("problem") == erdos_id
         and n.get("verdict") in ("TARGET", "MAYBE")), None)
    for e in graph["edges"]:
        if e["type"] == "trap" and e["src"] == pid:
            lure = (f"prize **{e['prize']}** + upstream says"
                    if e["prize"] != "no" else "upstream says")
            if live_branch:
                lines.append(
                    f"- **TRAP (branch-scoped)** — {lure} "
                    f"`{e['upstream_finite_handle']}`, and our status register "
                    f"records a **wall**. The wall covers the GENERAL branch; "
                    f"our triage marks a sub-branch "
                    f"**{live_branch['verdict']}** (see `{live_branch['id']}` "
                    f"below). Strike the sub-branch, not the headline.")
            else:
                lines.append(
                    f"- **TRAP** — {lure} "
                    f"`{e['upstream_finite_handle']}`, but our status register "
                    f"records a **wall**: the finite handle does not make it "
                    f"reachable here (reasons in atlas/walls.md, finite-handle "
                    f"table). Decidable in principle is not reachable in "
                    f"practice.")
    # Retraction pins: a stronger claim on this problem was withdrawn. Named by
    # claim id and pin hash only — never the banned string itself.
    claim_ids = {e["dst"] for e in graph["edges"]
                 if e["type"] == "evidenced_by" and e["src"] == pid}
    pins = sorted({(e["src"], e["dst"]) for e in graph["edges"]
                   if e["type"] == "retracts" and e["dst"] in claim_ids})
    for pin_id, claim_id in pins:
        lines.append(
            f"- **RETRACTION PIN** — claim `{nodes[claim_id]['claim_id']}` "
            f"carries a banned phrasing (pin `{pin_id}`): a stronger earlier "
            f"statement was withdrawn and must not be resurrected. Check "
            f"`certificates/contracts.json` publication_bindings before "
            f"publishing any prose about this problem.")
    for e in graph["edges"]:
        if e["type"] == "walled":
            w = nodes[e["dst"]]
            owner = e["src"]
            if owner == pid:
                lines.append(f"- **WALL (problem)** — {w['reason']} "
                             f"[{w['source']}]")
            elif owner.startswith("S:") and nodes[owner]["problem"] == int(pid[1:]):
                s = nodes[owner]
                label = s.get("quantity") or s.get("statement_short") or s["overlay"]
                lines.append(f"- **WALL (surface: {clip(label, 90)})** — "
                             f"{w['reason']} [{w['source']}]")
    return lines


def render_card(graph, erdos_id):
    nodes = {n["id"]: n for n in graph["nodes"]}
    pid = f"P{erdos_id}"
    p = nodes[pid]
    surfaces = [nodes[e["dst"]] for e in graph["edges"]
                if e["type"] == "has_surface" and e["src"] == pid]
    surfaces.sort(key=lambda s: ({"finite_handle_triage": 0,
                                  "problems.json": 1,
                                  "gap_map": 2}[s["overlay"]],
                                 s.get("quantity", "")))
    applies = {}
    for e in graph["edges"]:
        if e["type"] == "applies":
            applies.setdefault(e["dst"], []).append(
                (nodes[e["src"]]["name"], e["predicate"]))
    claims = [nodes[e["dst"]] for e in graph["edges"]
              if e["type"] == "evidenced_by" and e["src"] == pid]
    externals = [nodes[e["src"]] for e in graph["edges"]
                 if e["type"] == "claims_about" and e["dst"] == pid]
    incidents = [nodes[e["dst"]] for e in graph["edges"]
                 if e["type"] == "learned_from" and e["src"] == pid]
    fams = []
    for e in graph["edges"]:
        if e["type"] == "same_family":
            if e["src"] == pid:
                fams.append((int(e["dst"][1:]), e["shared"]))
            elif e["dst"] == pid:
                fams.append((int(e["src"][1:]), e["shared"]))
    fams.sort()

    L = []
    w = L.append
    title = (p.get("deep") or {}).get("title") or f"Erdős problem #{erdos_id}"
    w(f"# Erdős #{erdos_id} — attack card")
    w("")
    w(f"> {title} · {p['erdos_url']}")
    w("> Generated by `tools/build_graph.py` from committed ledgers — "
      "regenerate with `make graph`. A disagreement with this card is a bug "
      "report against its sources, never an edit here.")
    w("")
    # 1. STOP — always first (standing rule 3; byte-order enforced by tests)
    w("## STOP — read before spending")
    w("")
    stop = _wall_lines(graph, pid)
    for x in incidents:
        stop.append(f"- **CAMPAIGN FINDING** — {x['finding']} [{x['source']}]")
    if stop:
        L.extend(stop)
    else:
        w("- No recorded walls, traps, retraction pins, or campaign findings "
          "on this problem. Absence of a wall is not evidence of feasibility "
          "— run `M:literature-freshness-check` before any strike.")
    w("")
    # 2. STATUS — three registers, never merged
    w("## STATUS — three registers, never merged")
    w("")
    w(f"- ours: **{p['status']}** (atlas/stubs.json)")
    handle = f", finite handle `{p['upstream_finite_handle']}`" if p["upstream_finite_handle"] else ""
    w(f"- upstream: **{p['upstream_status']}** (raw `{p['upstream_state_raw']}`{handle})")
    if p.get("lean"):
        w(f"- formal: {p['lean']['formal_status']}, answer "
          f"`{p['lean']['answer']}` ({p['lean']['path']})")
    else:
        w("- formal: not in formal-conjectures")
    prize = p["prize"]
    if prize != "no":
        w(f"- prize: {prize} — prizes are history, not targets "
          "(standing rule 2).")
    w("")
    if p.get("statement"):
        w("## STATEMENT (Apache-licensed, Lean-derived)")
        w("")
        w(p["statement"])
        w("")
    # 3. SURFACES
    w("## ATTACK SURFACES — which overlay said so")
    w("")
    if not surfaces:
        w("No branch-level surface is recorded for this problem yet. "
          "The stub registers are above; adding a gap_map row is how a "
          "surface is born.")
        w("")
    for s in surfaces:
        sid = s["id"]
        mv = applies.get(sid, [])
        mvtxt = ("; ".join(f"applies: **{n}** (predicate `{pr}`)"
                           for n, pr in sorted(mv))
                 if mv else "no move applies mechanically")
        if s["overlay"] == "finite_handle_triage":
            w(f"### `{sid}` — triage verdict **{s['verdict']}** "
              f"(finite_handle_triage, "
              f"{graph['source_vintages']['finite_handle_triage']})")
            w("")
            w(f"- our summary: {s['statement_short']}")
            w(f"- witness: {s['what_a_witness_is']}")
            w(f"- smallest untested case: {s['smallest_untested_case']}")
            w(f"- known frontier: {s['known_computational_frontier']}")
            w(f"- search-space estimate: {s['search_space_estimate']}")
            w("- verification cheap and exact: "
              f"{'yes' if s['verification_is_cheap_and_exact'] else 'no'}")
            w(f"- verdict reason: {s['verdict_reason']}")
            w(f"- {mvtxt}")
        elif s["overlay"] == "problems.json":
            w(f"### `{sid}` — deep audit: **{s['beatable']}**, lane "
              f"`{s['lane']}`, board **{s['board_class']}** (problems.json)")
            w("")
            w(f"- finite object: {clip(s['finite_object'], 500)}")
            w(f"- current record: {s['current_record']}")
            if s.get("frontier"):
                w(f"- frontier: {clip(json.dumps(s['frontier'], ensure_ascii=False) if isinstance(s['frontier'], dict) else s['frontier'], 400)}")
            w(f"- verifier: {s['verifier']}")
            w(f"- attack: {s['attack']}")
            w(f"- {mvtxt}")
        else:  # gap_map
            w(f"### `{sid}` — {clip(s['quantity'], 120)} (gap_map, "
              f"kind `{s['kind']}`, confidence {s['confidence']})")
            w("")
            lo, up = s["lower"] or {}, s["upper"] or {}
            w(f"- bounds: lower {lo.get('value', '—')} "
              f"({lo.get('source', '—')}) · upper {up.get('value', '—')} "
              f"({up.get('source', '—')})")
            w(f"- witness side: `{s['witness_side']}` · witness feasibility "
              f"`{s['witness_feasibility']}` · exact feasibility "
              f"`{s['exact_feasibility']}`")
            w(f"- witness object: {clip(s['witness_object'], 400)}")
            w(f"- witness verifier: {clip(s['witness_verifier'], 300)}")
            w(f"- notes: {clip(s['notes'], 500)}")
            w(f"- {mvtxt}")
        w("")
    # 4. EVIDENCE
    w("## EVIDENCE — replayable, or it does not count")
    w("")
    if claims:
        # Dense evidence cards are context packs, not duplicate dossiers.
        # Keep every claim id and replay command, but compress prose once the
        # claim ledger itself would push a card over the enforced 12k budget.
        statement_cap = 16 if len(claims) > 12 else None
        for c in claims:
            statement = (clip(c['statement'], statement_cap)
                         if statement_cap is not None else c['statement'])
            w(f"- contract claim `{c['claim_id']}` [{c['status']}]: "
          f"{statement}")
            if c.get("replay"):
                w(f"  - one-command replay: `{' '.join(c['replay']['argv'])}`")
    else:
        w("- No promoted contract claim touches this problem "
          "(certificates/contracts.json).")
    for x in externals:
        tag = "**HOT** — verification target" if x.get("hot") else "recorded"
        w(f"- external claim ({x['origin']}, {tag}): "
          f"{clip(x['claim_title'], 200)} — our verdict: "
          f"“{x.get('our_verdict', 'recorded')}”. A claim never sets a "
          "status (standing rule 1).")
    w("")
    # 5. BRIDGES
    w("## BRIDGES — structurally adjacent problems")
    w("")
    if fams:
        carded = set(card_problem_ids(graph))
        for other, seqs in fams[:12]:
            where = (f"card `views/graph/P{other}.md`" if other in carded
                     else "no card (registers only: `atlas/stubs.json`)")
            w(f"- #{other} shares {', '.join(seqs)} → {where}")
        if len(fams) > 12:
            w(f"- … and {len(fams) - 12} more (query: "
              f"`python3 tools/query_graph.py bridges {erdos_id}`)")
    else:
        w("- No shared-OEIS family recorded. Tag neighbors: "
          + ", ".join(f"`{t}`" for t in p["tags"]) + ".")
    w("")
    # 6. PROMOTE
    w("## PROMOTE — what a win must look like")
    w("")
    w("1. Receipt: `python3 -I <verifier>.py` — exact arithmetic, a planted-"
      "failure control that must FAIL, emit/check split so replays never "
      "rewrite the artifact, machine verdict on stdout.")
    w("2. Evidence slot: an `evidence[]` item on the surface's gap_map row "
      "(`{type, artifact, date}`) and, for certificate-grade results, a "
      "claim in `certificates/contracts.json` with sha256-pinned artifacts.")
    w("3. Freshness: before the strike, run `M:literature-freshness-check` — "
      "the #552/DS1 retraction is why.")
    w(f"4. Name the node: cite `{pid}` and the surface id in your receipt so "
      "the next agent's graph build finds your result.")
    w("")
    return "\n".join(L)


def render_sorties(graph):
    nodes = {n["id"]: n for n in graph["nodes"]}
    L = []
    w = L.append
    w("# SORTIES — the Quartermaster's board")
    w("")
    w("> Generated by `tools/build_graph.py` from committed ledgers — "
      "regenerate with `make graph`; `make check-graph` fails if stale. "
      "Ranking predicate: see `strike-ranking` in `atlas/graph/graph.json` "
      "(verbatim, versioned). Entry point for agents: `GRAPH.md`.")
    w("")
    # --- DO-NOT-SPEND first (standing rule 3)
    traps = [e for e in graph["edges"] if e["type"] == "trap"]
    w("## DO-NOT-SPEND — the traps, priced honestly")
    w("")
    w(f"{len(traps)} problems carry an upstream finite handle "
      "(`decidable/falsifiable/verifiable`) AND our catalogued wall. The "
      "prize renders beside the trap because the prize is the lure:")
    w("")
    w("| problem | prize | upstream handle | card |")
    w("|---|---|---|---|")
    for e in sorted(traps, key=lambda x: int(x["src"][1:])):
        eid = int(e["src"][1:])
        prize = e["prize"] if e["prize"] != "no" else "—"
        w(f"| #{eid} | {prize} | `{e['upstream_finite_handle']}` | "
          f"`views/graph/P{eid}.md` |")
    w("")
    w("Full wall registry with reasons: `atlas/walls.md` (surface-scoped "
      "walls render on each card's STOP section). `#64` is the standing "
      "lesson: its *general* branch is the $1000 trap above, its *cubic* "
      "branch is strike T1-a below — walls are per-branch, read the card.")
    w("")
    # --- strikes
    tri = [n for n in graph["nodes"] if n["type"] == "surface"
           and n["overlay"] == "finite_handle_triage"]
    targets = sorted((s for s in tri if s["verdict"] == "TARGET"),
                     key=lambda s: s["problem"])
    maybes = sorted((s for s in tri if s["verdict"] == "MAYBE"),
                    key=lambda s: s["problem"])
    w("## STRIKE LIST")
    w("")
    w("### T1 — triage TARGET branches (vetted "
      f"{graph['source_vintages']['finite_handle_triage']}; every triage "
      "criterion passes)")
    w("")
    for s in targets:
        w(f"- **#{s['problem']}** (`{s['id']}`) — "
          f"{clip(s['statement_short'], 220)}")
        w(f"  - smallest untested case: {clip(s['smallest_untested_case'], 260)}")
        w(f"  - est: {clip(s['search_space_estimate'], 200)}")
        w(f"  - card: `views/graph/P{s['problem']}.md`")
    w("")
    movable = sorted({n["erdos_id"] for n in graph["nodes"]
                      if n["type"] == "problem"
                      and (n["status"] == "movable"
                           or (n.get("deep") or {}).get("beatable") == "MOVABLE")})
    w("### T2 — movable boards (stub `movable` ∪ deep `MOVABLE`)")
    w("")
    for eid in movable:
        p = nodes[f"P{eid}"]
        d = p.get("deep") or {}
        extra = (f" — lane `{d['lane']}`, board {d['board_class']}"
                 if d else "")
        w(f"- **#{eid}** [{p['status']} / upstream {p['upstream_status']}]"
          f"{extra} — card `views/graph/P{eid}.md`")
    w("")
    workable = []
    for e in graph["edges"]:
        if (e["type"] == "applies" and e["src"] == "M:witness-local-search"
                and e.get("predicate") == "workable"):
            workable.append(nodes[e["dst"]])
    workable.sort(key=lambda s: (FEAS_ORDER[s["witness_feasibility"]],
                                 s["problem"]))
    w(f"### T3 — witness-workable gap surfaces ({len(workable)}; "
      "predicate `workable`, imported from state_of_frontier)")
    w("")
    w("| # | quantity | feas | witness verifier | confidence |")
    w("|---|---|---|---|---|")
    for s in workable:
        w(f"| #{s['problem']} | {cell(s['quantity'], 70)} | "
          f"{s['witness_feasibility']} | {cell(s['witness_verifier'], 60)} | "
          f"{s['confidence']} |")
    w("")
    w("### T4 — triage MAYBE branches")
    w("")
    for s in maybes:
        w(f"- **#{s['problem']}** (`{s['id']}`) — "
          f"{clip(s['verdict_reason'], 220)}")
    w("")
    # --- disagreement cells
    w("## DISAGREEMENT CELLS — the highest-information rows")
    w("")
    w("Where two registers disagree, the disagreement IS the product "
      "(uncomputed-table-cells niche):")
    w("")
    cells = sorted(eid for eid in (n["erdos_id"] for n in graph["nodes"]
                                   if n["type"] == "problem"
                                   and n["status"] == "solved-upstream"
                                   and (n.get("deep") or {}).get("beatable") == "MOVABLE"))
    w(f"- solved-upstream × deep MOVABLE: "
      + ", ".join(f"#{c}" for c in cells)
      + " — upstream closed the headline; our finite table cell still moves.")
    split = sorted({s["problem"] for s in targets}
                   & {int(e["src"][1:]) for e in traps})
    if split:
        w(f"- trap × TARGET branch split: "
          + ", ".join(f"#{c}" for c in split)
          + " — the general branch is walled, a sub-branch is live.")
    nwalls = sum(1 for n in graph["nodes"]
                 if n["type"] == "problem" and n["status"] == "wall")
    w(f"- upstream Open × our wall: the {nwalls} catalogued walls "
      "(`atlas/walls.md`) — 'falsifiable upstream' is not 'reachable here'.")
    w("")
    # --- hot claims
    hot = sorted({n["erdos_id"] for n in graph["nodes"]
                  if n["type"] == "external_claim" and n.get("hot")})
    w(f"## HOT CLAIMS — {len(hot)} external claims against problems we "
      "record unresolved")
    w("")
    w("Verification targets for `M:external-claim-replay` — a claim never "
      "sets a status (standing rule 1):")
    w("")
    w(", ".join(f"#{c}" for c in hot))
    w("")
    # --- replay recipes
    w("## REPLAY RECIPES — run a working verifier first, then adapt")
    w("")
    w("Every promoted claim replays in one command; the fastest way to learn "
      "the receipt contract is to run one and read its verifier:")
    w("")
    for n in sorted((n for n in graph["nodes"]
                     if n["type"] == "evidence_claim" and n.get("replay")),
                    key=lambda n: n["claim_id"]):
        w(f"- `{n['claim_id']}`: `{' '.join(n['replay']['argv'])}`")
    w("")
    return "\n".join(L)


def render_index(graph, card_ids):
    L = []
    w = L.append
    w("# Attack cards — index")
    w("")
    w("> Generated by `tools/build_graph.py`. One card per problem with "
      "graph content (a surface, wall, trap, evidence, hot claim, or deep "
      "audit). Cold-start: read `GRAPH.md`, then `views/sorties.md`, then "
      "one card.")
    w("")
    nodes = {n["id"]: n for n in graph["nodes"]}
    for eid in card_ids:
        p = nodes[f"P{eid}"]
        d = p.get("deep") or {}
        label = d.get("title") or ", ".join(p["tags"])
        w(f"- [P{eid}](P{eid}.md) — {p['status']} / upstream "
          f"{p['upstream_status']} — {clip(label, 90)}")
    w("")
    return "\n".join(L)


def card_problem_ids(graph):
    """Problems that earn a card: any surface, wall, trap, evidence claim,
    hot external claim, or deep record."""
    ids = set()
    for e in graph["edges"]:
        if e["type"] in ("has_surface", "walled", "trap", "evidenced_by"):
            if e["src"].startswith("P"):
                ids.add(int(e["src"][1:]))
        if e["type"] == "claims_about" and e.get("hot"):
            ids.add(int(e["dst"][1:]))
    for n in graph["nodes"]:
        if n["type"] == "problem" and n.get("deep"):
            ids.add(n["erdos_id"])
    return sorted(ids)


# ------------------------------------------------------------------ main
def emit():
    graph, quarantine = build_graph()
    outputs = {}
    outputs[GRAPH_DIR / "graph.json"] = (
        json.dumps(graph, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    outputs[GRAPH_DIR / "quarantine.json"] = (
        json.dumps(quarantine, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    outputs[SORTIES] = render_sorties(graph) + "\n"
    ids = card_problem_ids(graph)
    for eid in ids:
        outputs[VIEWS_DIR / f"P{eid}.md"] = render_card(graph, eid) + "\n"
    outputs[VIEWS_DIR / "INDEX.md"] = render_index(graph, ids) + "\n"
    return outputs


def orphans(outputs):
    """Committed generated files that this build no longer produces."""
    expected = {p.resolve() for p in outputs}
    found = []
    for d, pattern in ((VIEWS_DIR, "*.md"), (GRAPH_DIR, "*.json")):
        if d.exists():
            for f in sorted(d.glob(pattern)):
                if f.resolve() not in expected:
                    found.append(f)
    return found


def main():
    check = "--check" in sys.argv[1:]
    outputs = emit()
    stale = []
    for path, content in outputs.items():
        # Compare BYTES: text mode translates newlines, so a CRLF hand-edit
        # would pass a text comparison and the byte-identity claim would be a
        # lie. Write bytes for the same reason.
        blob = content.encode("utf-8")
        if check:
            if not path.exists() or path.read_bytes() != blob:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
    extra = orphans(outputs)
    if check:
        stale += [str(f.relative_to(ROOT)) + " (orphaned)" for f in extra]
        if stale:
            print("STALE graph outputs (run `make graph`):")
            for s in sorted(stale):
                print("  " + s)
            raise SystemExit(1)
        print(f"graph up to date ({len(outputs)} files).")
    else:
        # `make graph` must actually converge: the --check remedy says to run
        # it, so it has to remove what it no longer generates.
        for f in extra:
            f.unlink()
        cards = len([p for p in outputs if p.parent == VIEWS_DIR]) - 1
        print(f"wrote {len(outputs)} files ({cards} cards)"
              + (f", removed {len(extra)} orphaned" if extra else "") + ".")


if __name__ == "__main__":
    main()
