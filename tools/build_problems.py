#!/usr/bin/env python3
"""Archive-only bootstrap from the original 51 deep audits.

This is not the release snapshot generator. The published Atlas contains later
curation, evidence, and campaign corrections that the source audit cannot
reproduce. Running this tool therefore requires an explicit destructive
bootstrap flag.

Board-class rule (documented in atlas/schema.json and README):

  READY  := (R1) the witness check is exact integer/rational arithmetic, a-priori
            bounded on a byte-capped witness, <= ~1 s per candidate;
            (R2) the record contains a concrete OPEN numeric frontier that a single
            submitted finite witness would strictly improve;
            (R3) the witness conditions are discrete or open/robust (strict
            inequalities), so integer/rational witnesses are lossless;
            (R4) one board per finite frontier object (duplicate audit entries
            cross-reference the carrier entry).
  HEAVY  := exact adjudication exists but fails R1 timing (a long MIS/SAT run per
            candidate) or the movable claim is certificate-shaped (DRAT chain,
            exhaustion receipt, SDP dual) rather than a small witness.
  NONE   := no exact poly-time verifier in any movable direction, or witness not
            finitely representable, or no open finite frontier at all
            (asymptotic-only / solved / duplicate object).
"""
import json
import re
import sys
from pathlib import Path

# Source audits live in the cultural-soliton-observatory research session;
# pass an alternative path as argv[1] if that checkout is elsewhere.
_DEFAULT_SRC = (
    "/Users/nivek/Desktop/cultural-soliton-observatory/research_sessions/"
    "res_20260711_erdos_machinery_audit/audits.json"
)
if len(sys.argv) < 2 or sys.argv[1] != "--bootstrap-from-audits":
    raise SystemExit(
        "refusing to overwrite the curated Atlas; pass --bootstrap-from-audits "
        "only when intentionally rebuilding from the archival audit source"
    )
SRC = Path(sys.argv[2] if len(sys.argv) > 2 else _DEFAULT_SRC)
OUT = Path(__file__).resolve().parents[1] / "atlas" / "problems.json"

READY = {21, 41, 1, 67, 241, 552, 166, 138, 140, 86, 1029, 183, 564}
HEAVY = {582, 165, 139, 13, 20, 30, 39, 64, 107, 159, 687, 720, 19, 712}

LANE = {}
for i in (41, 552, 86, 107, 720, 19):
    LANE[i] = "SAT+DRAT-nonexistence"
for i in (1, 21, 241, 52, 139, 13, 30, 39, 64, 687):
    LANE[i] = "exact-backtracking"
for i in (67, 20, 166, 159, 138, 140, 1029, 183, 564, 582, 165):
    LANE[i] = "witness-local-search"
LANE[712] = "LP/SDP-certificate"

P42_SLUG = {
    21: "q6-intersecting-hypergraph",
    1: "distinct-subset-sums-a11",
    41: "b3-ruler-11-marks",
    241: "b3-subset-first-jump-9",
    67: "edp-c3-longest-sequence",
}

FRONTIER = {
    21: "14 <= q(6) <= 18 (lower: Sivashankar arXiv:2606.24878 Thm 1; upper: Barat arXiv:2011.04444, PG(2,5) 18-line family)",
    41: "a(11) <= 445 (Tromp 2013, A227358); optimality open, suspected < 440",
    1: "310 <= a(11) <= 594 (upper: Conway-Guy 11-set; lower: Dyson a(10)=309 plus deletion)",
    67: "C=3 general witness >= 130,000 (Konev-Lisitsa unrestricted witness, exactly re-verified by P42); C=2 tight at 1160",
    241: "A387704 b-file to a(150)=8 (Kesarwani, Dec 2025); first jump to 9 elements open (N >= 151)",
    552: "Repository-certified: a(12..16) = 17,18,19,20,21; next open term 21 <= a(17) <= 23",
    20: "Sun(3,3)=21 proven; Sun(4,3) >= 55 (1972), Sun(3,4) >= 39 (1992), Sun(3,5) >= 89 (1974) - construction records static 30-50 yr",
    166: "R(4,6) in [36,40] (lower 36 = Exoo 2012)",
    159: "39 <= R(C4,K11) <= 44 (Lange-Radziszowski-Xu 2014/2016)",
    138: "W(2,7) >= 3703 (Ahmed et al. 2014); W(2,6)=1132 exact (Kouril-Paul 2008)",
    140: "r_3(211)=43 exact (A003002, Cariboni); r_3(212) in {43,44} - 44-set witness would settle it",
    52: "A263996 small-case table (smallest |A+A u AA| over n-sets); contest-set records",
    86: "ex(Q7,C4) >= 304, ex(Q8,C4) >= 680 (SA, arXiv:2603.29127, May 2026); exact values open past ex(Q6,C4)=132",
    1029: "R(5,5) in [43,46]; best public K43 colorings have exactly 2 monochromatic K5s (a 0-defect witness proves R(5,5) >= 44)",
    107: "33 <= f(7) <= 127 (a 33-point general-position set with no convex 7-gon would refute Erdos-Szekeres at n=7)",
    183: "R_4(3) in [51,62] (Chung 1973 lower), R_5(3) in [162,307] (Exoo)",
    564: "R_3(4,5;3) >= 35 (SAT class-decomposition record)",
    582: "21 <= Fe(3,3;4) <= 786 (Lange-Radziszowski-Xu 2012); Graham's $100 for a K4-free graph <= 100 vertices arrowing (3,3)",
    165: "R(3,10) in [40,41] (R(3,9)=36, McKay-Zhang ~1990s)",
    139: "exact r_k(N) tables beyond r_3: certificate-tier (exhaustion receipts); r_3 frontier object carried by #140",
    13: "f(N) exact small-N table uncharted (Bedert arXiv:2301.07065 proved the theorem; threshold ineffective) - certified table = new OEIS sequence",
    30: "OGR-28 (length 585) proven optimal Nov 2022 by distributed.net after 8.5 yr; next move (OGR-29) is an exhaustion claim",
    39: "Sidon/Golomb optimality beyond OGR-28: exhaustion-certificate tier; asymptotic headline (Ruzsa exponent ~0.4142) untouchable",
    64: "no counterexample: verified for all cubic graphs <= 28 vertices (Royle-Markstrom ~2004); extension = exhaustive-generation certificate",
    687: "A048670 exact to a(64) (Bozek 2021, Google-Cloud pruned exhaustion); next term = pruned-exhaustion certificate claim",
    720: "size-Ramsey exact small values (r-hat(P5,P5)=11, ...); each upper-bound move = one host + one DRAT UNSAT certificate",
    19: "EFL fully verified n <= 12; the n=13 bucket is a whole-family DRAT-certificate claim (pigeonhole-hard CDCL)",
    712: "5/9 <= pi(K_4^3) <= 0.561666 (Razborov flag-algebra SDP 2010); movable claim = a better SDP dual certificate",
}

BOARD_REASON_NONE = {
    52: "no concrete n, authoritative seed witness, or tracked per-n record is identified; the asymptotic headline is not advanced by an unscoped finite score (R2 fails)",
    142: "asymptotic formula; the prize headline explicitly 'cannot be resolved by finite computation'; the finite r_k table object is carried by #140",
    77: "asymptotic limit only; the finite R(5,5) frontier object is carried by #1029 (R4 dedupe)",
    548: "no finite search space (n unbounded) and no numeric record; positive direction has no finite certificate",
    128: "verifier is NP-hard (Sparsest-k-Subgraph); meaningful regime is flag-algebra SDP blowups, not finite witnesses",
    161: "no numeric record exists - the frontier is a growth rate, not a value",
    500: "finite lower bound is a closed-form construction (A140462) believed exact, not an open tracked frontier; density side carried by #712",
    2: "witness not representable: a min-modulus-40+ covering system already has > 10^50 recursively-defined congruences; no flat poly-time check",
    146: "no poly-time exact verifier for the asymptotic claim; small-n ex(n;H0) values are disconnected from the conjecture",
    114: "transcendental objective (elliptic-integral arc length); no exact/DRAT verifier exists; Tao proved the conjecture for large n (Dec 2025)",
    97: "existence bounty with no numeric frontier, and the defining condition (4 equidistant points) is equality-constrained real geometry (R3 fails: rational restriction lossy)",
    707: "headline DISPROVED, Lean-verified (Alexeev-Mixon, PNAS 2025); nothing movable remains",
    708: "no tracked record, and the upper-bound direction quantifies over unbounded sets with no finite verifier",
    43: "problem DISPROVED (both questions resolved negatively); no movable number",
    27: "headline DISPROVED (Filaseta-Ford-Konyagin-Pomerance-Yu 2007); extremal witnesses not finitely representable",
    92: "headline disproved with #90; exact-value direction has no finite verifier; equality-constrained coordinates (R3 fails)",
    703: "extremal witness has size ~2^(n-1) - not representable at any n where the answer is unknown",
    1135: "exhaustion claim (2^71 sieve) has no certificate - adjudication = full recompute at GPU-supercomputer scale; cycle-witness side is an existence bounty with no frontier",
    182: "'contains a k-regular subgraph' is NP-complete for k >= 3: no poly-time exact verifier",
    83: "proved theorem (Ahlswede-Khachatrian 1997); a MIS solve certifies nothing new",
    90: "exact-value verifier is ExistsR-hard (unit-distance realizability); witness side requires algebraic coordinates - equality constraint makes the rational restriction lossy (R3 fails)",
    101: "collinearity is an equality constraint: optimal configurations may require irrational coordinates (ExistsR realizability gap), so a rational-witness board is not lossless (R3 fails); nonexistence side has no DRAT route",
    211: "same ExistsR/collinearity obstruction as #101 - orchard-type equality-constrained geometry (R3 fails)",
    588: "same ExistsR/collinearity obstruction as #101 (R3 fails); the continuous search is unconstrained by the verifier",
}

BOARD_REASON_READY = {
    21: "witness = <= 64 six-sets; pairwise-intersect + complete 5-cover branch-and-bound <= 9,331 nodes, ms-exact; open bracket 14..18 witness-improvable (m <= 17 wins)",
    41: "witness = 11 integers; 286 triple-sum distinctness checks, exact, microseconds; open frontier 445 witness-improvable",
    1: "witness = 11 integers; 2048 subset sums, exact and fast; live bracket 310 <= a(11) <= 594",
    67: "witness = +-1 sequence; O(N log N) integer prefix-sum scan; exactly re-verified 130,000-term frontier witness-extendable",
    241: "witness = subset of {1..N}; O(k^3) triple-sum distinctness, exact; first-jump frontier witness-improvable",
    552: "witness = C4-free red graph with minimum degree >= m-n; codegree and degree checks are exact and cheap; the next open cell a(17) is witness-improvable from the certified m=20 seed",
    166: "witness = 2-coloring on <= ~40 vertices; K4/K6 clique scans trivial; R(4,6) >= 37 witness-improvable",
    138: "witness = 2-coloring of [N]; O(N^2/k) mono-AP scan, exact; W(2,7) > 3703 witness-improvable",
    140: "witness = 44-subset of [1,212] with no 3-AP; O(|S|^2) midpoint test, trivial; would settle r_3(212)=44 (witness side only - the UNSAT side is a named wall)",
    86: "witness = edge subset of Q7; scan the 672 4-cycles, exact, microseconds; ex(Q7,C4) >= 305 witness-improvable",
    1029: "witness = 2-coloring of K43; mono-K5 count, exact, cheap (our R(5,5) verifier); a 0-defect coloring proves R(5,5) >= 44 - EinsteinArena-style market board",
    183: "witness = k-edge-coloring; per-color triangle scan O(k n^3), exact; R_4(3) >= 52 witness-improvable",
    564: "witness = 2-coloring of triples on 35+ vertices; O(m^5) scan of 4-/5-subsets, exact, cheap; R_3(4,5;3) >= 36 witness-improvable",
}

BOARD_REASON_HEAVY = {
    582: "witness (K4-free) is cheap, but adjudicating 'G arrows (3,3)' costs one large CDCL UNSAT + DRAT check per candidate - optimistic-oracle tier (R1 fails)",
    165: "lower-bound witness needs an independence-number <= 9 verification: ~8.5e8 subset scan / MIS run per candidate - minutes, not seconds (R1 fails)",
    139: "movable content is the exact-table certificate side (exhaustion receipts for r_k, k >= 4); the r_3(212) witness object is carried by #140",
    13: "no defended record to beat (uncharted table); the boardable product is a certified exact-value table - ILP/SAT certificate claims, not single witnesses (R2 fails)",
    20: "the survey entry combines several distinct (uniformity, sunflower-size) frontiers; split and seed one exact cell before admission (R4 fails)",
    30: "frontier is proven-optimal (OGR-28); the next move is an optimality/exhaustion claim adjudicated by receipts, not a witness",
    39: "optimality claims (branch-and-bound nonexistence receipts) are the movable half; witness side has no open tracked value",
    64: "movable claim = exhaustive-generation certificate ('no cubic counterexample <= 30 vertices'); a counterexample itself would be witness-cheap but is believed nonexistent (existence bounty, no frontier)",
    107: "orientation checking is exact, but no a-priori coordinate bit bound is established; a byte-capped integer format could exclude valid order types (R1/R3 admission proof pending)",
    159: "C4-freeness is cheap, but alpha <= 10 requires a measured and a-priori-bounded exact MIS adjudication; the survey does not establish the <=1 s R1 contract",
    687: "next A048670 term requires the upper-bound side: certified nonexistence over all residue choices - pruned-exhaustion receipt, not a witness",
    720: "each exact-value move = host graph + DRAT UNSAT certificate (upper) + enumeration receipt (lower) - certificate-tier adjudication",
    19: "the movable n=13 step is a whole-bucket DRAT certificate (pigeonhole-hard, resolution-exponential); coloring witnesses certify nothing new",
    712: "movable claim = an improved flag-algebra SDP dual certificate - exact-rational certificate check, heavy and specialist (LP/SDP lane)",
}

OEIS_RE = re.compile(r"\bA\d{6}\b")
ARXIV_RE = re.compile(r"arXiv[: ]?(\d{4}\.\d{4,5})", re.IGNORECASE)

# A391599 was cited on the erdosproblems.com #21 page but has been deleted from
# OEIS as AI-generated; the audit flags it as spurious. Keep it out of links.
OEIS_EXCLUDE = {21: {"A391599"}}
# The corrected q(6) lower bound comes from the Phase-A literature verification
# (phase_a_literature.json), which post-dates the audit blob text.
ARXIV_ADD = {21: ["2606.24878"]}

CAMPAIGN_FINDING = {
    67: (
        "2026-07-12 correction: the unrestricted Konev-Lisitsa length-130,000 witness was "
        "recovered from the authors' archived result artifact and exactly re-verified by the P42 "
        "verifier. Earlier ~14,000 frontier and search-cost prose in the originating audit is "
        "superseded; new work must start above 130,000."
    ),
    552: (
        "2026-07-13: a local PySAT/CaDiCaL edge-SAT pass found exact lower-bound "
        "witnesses meeting Parsons' upper bound for every n=12..16. The dependency-free "
        "verifier recomputed all degrees and pair-codegrees; CHRONOS independently rechecked "
        "n=12. A limited 1,000,000-conflict pass on n=17,m=22 returned UNKNOWN, not UNSAT. "
        "Do not repeat n=12..16, and do not treat the n=17 timeout as a bound."
    ),
}

ENTRY_OVERRIDE = {
    552: {
        "finite_object": "For fixed n, a simple red graph on m labeled vertices with no C4 and minimum degree at least m-n. Its complement then has no K1,n. Maximizing m improves the lower bound R(C4,K1,n) >= m+1.",
        "current_record": "OEIS A006672 publishes {4,4,6,7,8,9,11,12,13,14,16} for n=1..11 (a(11) from Alex Towell, Jun 2026). P42 exact certificates establish a(12..16)={17,18,19,20,21}, meeting Parsons' upper bound. The next open term is a(17), bracketed 21 <= a(17) <= 23.",
        "beatable_reason": "The n=12..16 endpoints are closed by exact witnesses. Route new compute to n=17, where the top endpoint is a C4-free graph on 22 vertices with minimum degree 5.",
        "attack": "Start at n=17. Search m=21 or 22 with exact C4 clauses and minimum-degree constraints; m=22 reaches Parsons' upper bound. Require DRAT/LRAT for nonexistence.",
        "verdict": "PARTIAL. The asymptotic prize headline remains analytic and is not claimed. Exact certificates close n=12..16; n=17 remains open in 21..23.",
        "evidence": {
            "status": "verified",
            "checked_at": "2026-07-13T06:20:00Z",
            "digest": "sha256:3ecdf116fb1eb0cc397ebcce8273899c008dec16c19a582425529662a8f7deda",
            "artifact_path": "certificates/erdos-552/witnesses.json",
            "artifact_sha256": "3ecdf116fb1eb0cc397ebcce8273899c008dec16c19a582425529662a8f7deda",
            "verifier_path": "certificates/erdos-552/verify.py",
            "verifier_sha256": "cbcdf4b4c2127a77de27f21dc6fe8fdeb6f88addaa97f1408c6f38bd3fe51103",
            "claims": [f"R(C4,K1,{n})={n + (4 if n <= 16 else 5) + 1}" for n in range(12, 17)],
            "independent_review": "CHRONOS hostile-referee replay passed n=12; the bundled verifier checks all five graphs identically.",
        },
        "compute": {
            "schema": "p42-atlas-compute-v1",
            "status": "completed",
            "method": "edge SAT with exact C4 clauses and sequential-counter minimum-degree constraints",
            "solver": "PySAT 1.9.dev5 / CaDiCaL 1.9.5",
            "hardware": "local Apple workstation; single solver process",
            "parameter_region": {"n_min": 12, "n_max": 17, "top_endpoint_only": True},
            "coverage": [
                {
                    "axis": "n", "start": 12, "end": 16, "status": "CERTIFIED",
                    "result": "Exact values 17,18,19,20,21",
                    "artifact_sha256": "3ecdf116fb1eb0cc397ebcce8273899c008dec16c19a582425529662a8f7deda",
                },
                {
                    "axis": "n", "start": 17, "end": 17, "status": "UNKNOWN",
                    "result": "Top endpoint m=22 undecided after bounded conflict budget",
                },
            ],
            "result": "SAT witnesses closed n=12..16; n=17,m=22 remained UNKNOWN",
            "limits": "n=17 endpoint used a 1,000,000-conflict budget; UNKNOWN is not an exclusion.",
        },
    }
}

VERIFIER_OVERRIDE = {
    552: (
        "Represent the red graph. Check C_4-freeness by requiring every vertex pair to have "
        "codegree <= 1. A blue S_n is absent exactly when every blue degree is <= n-1, "
        "equivalently every red degree is >= m-n on an m-vertex complete graph. Both checks "
        "are exact and tiny for m ~ 15-45."
    ),
}


def main() -> None:
    audits = json.loads(SRC.read_text())
    entries = []
    for a in sorted(audits, key=lambda x: x["id"]):
        pid = a["id"]
        board = "READY" if pid in READY else ("HEAVY" if pid in HEAVY else "NONE")
        lane = LANE.get(pid, "wall")
        blob = " ".join(
            str(a.get(k, "")) for k in ("statement", "current_record", "verifier", "attack_sketch")
        )
        oeis = sorted(set(OEIS_RE.findall(blob)) - OEIS_EXCLUDE.get(pid, set()))
        arxiv = sorted(
            set(m.group(1) for m in ARXIV_RE.finditer(blob)) | set(ARXIV_ADD.get(pid, []))
        )
        if board == "READY":
            reason = BOARD_REASON_READY[pid]
        elif board == "HEAVY":
            reason = BOARD_REASON_HEAVY[pid]
        else:
            reason = BOARD_REASON_NONE[pid]
        entry = {
            "id": pid,
            "title": a["short_title"],
            "prize": a.get("prize"),
            "statement": a["statement"],
            "finite_object": a["finite_object"],
            "current_record": a["current_record"],
            "frontier": FRONTIER.get(pid),
            "beatable": a["beatable"],
            "beatable_reason": a["beatable_reason"],
            "fit_score": a["fit_score"],
            "impact_score": a["impact_score"],
            "impact_reason": a["impact_reason"],
            "verifier": VERIFIER_OVERRIDE.get(pid, a["verifier"]),
            "attack": a["attack_sketch"],
            "our_edge": a["our_edge"],
            "verdict": a["verdict"],
            "lane": lane,
            "board_class": board,
            "board_class_reason": reason,
            "wall_reason": reason if board == "NONE" else None,
            "p42_slug": P42_SLUG.get(pid),
            "erdos_url": f"https://www.erdosproblems.com/{pid}",
            "links": {"oeis": oeis, "arxiv": arxiv},
        }
        if pid in CAMPAIGN_FINDING:
            entry["campaign_finding"] = CAMPAIGN_FINDING[pid]
        entry.update(ENTRY_OVERRIDE.get(pid, {}))
        entries.append(entry)

    doc = {
        "atlas_version": "0.2.0",
        "generated": "2026-07-13",
        "source": "research_sessions/res_20260711_erdos_machinery_audit (cultural-soliton-observatory), 51 deep audits over 95 triaged Erdos prize problems",
        "board_class_rule": {
            "READY": "R1: exact integer/rational witness check, a-priori bounded on a byte-capped witness, <= ~1 s per candidate. R2: a concrete OPEN numeric frontier that a single submitted finite witness strictly improves. R3: witness conditions discrete or open/robust (strict inequalities) so integer/rational witnesses are lossless. R4: one board per finite frontier object (duplicates cross-reference the carrier).",
            "HEAVY": "Exact adjudication exists but fails R1 timing (long MIS/SAT run per candidate) or the movable claim is certificate-shaped (DRAT chain, exhaustion receipt, SDP dual) rather than a small witness. Optimistic-oracle tier.",
            "NONE": "No exact poly-time verifier in any movable direction, or witness not finitely representable, or no open finite frontier (asymptotic-only / solved / duplicate object). Do not board; usually also a do-not-enter wall (see atlas/walls.md).",
        },
        "counts": {
            "total": len(entries),
            "READY": sum(1 for e in entries if e["board_class"] == "READY"),
            "HEAVY": sum(1 for e in entries if e["board_class"] == "HEAVY"),
            "NONE": sum(1 for e in entries if e["board_class"] == "NONE"),
        },
        "problems": entries,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    lanes = {}
    for e in entries:
        lanes[e["lane"]] = lanes.get(e["lane"], 0) + 1
    print("counts:", doc["counts"])
    print("lanes:", lanes)


if __name__ == "__main__":
    main()
