#!/usr/bin/env python3
"""`crater new <slug>` -- a skeleton crater that validates on the first run.

The skeleton ships a single certified root, one machine check, a README with the
map markers, and a config whose level names are DELIBERATELY generic
(REFUTED_ALL_INDICES / PROVED_SOME_INDICES ...). Rename them to something that
says what your crater actually proved -- and when you do, remember the rule from
spec.py: a name that asserts REACH must name the artifact that licenses it in
`reach_license`, or the driver will reject the level as unlicensed.

House rule for a new crater (not enforceable here, so it is written down): ship
at least one PLANTED-FAILURE control alongside it -- a synthetic graph proving
that flipping one edge changes the computed statuses. See craterlib/selftest.py.
"""
import json
from pathlib import Path

REFUTED_LEVELS = [
    ("REFUTED_ALL_INDICES", "full", 2, True, "Refuted at every index in scope",
     "false at every index in scope (reached through index-preserving edges only)",
     "✕", "🟥", "#991b1b", "#450a0a", "#fff", "alln"),
    ("REFUTED_SOME_INDEX", "floor", 1, True, "Refuted at some index",
     "false at at least one index, location unknown (an index-transforming reduction)",
     "⊘", "🟧", "#f59e0b", "#92400e", "#1c1917", "somedim"),
    ("OPEN", "neutral", 0, False, "Open",
     "untouched — the root says nothing about it", "○", "🟦", "#1d4ed8",
     "#1e3a8a", "#fff", "open"),
    ("TRUE_THEOREM", "immune", 0, False, "Survives (proven theorem)",
     "a proven theorem, still standing", "✓", "🟩", "#15803d", "#14532d",
     "#fff", "theorem"),
    ("REFUTED_INDEPENDENTLY", "external", 3, False, "Refuted independently",
     "already refuted out of band, by a different mechanism", "■", "⬜",
     "#9ca3af", "#4b5563", "#1c1917", "indep"),
]

PROVED_LEVELS = [
    ("PROVED_ALL_INDICES", "full", 2, True, "Proved at every index in scope",
     "true at every index in scope (reached through index-preserving edges only)",
     "★", "🟩", "#15803d", "#14532d", "#fff", "allidx"),
    ("PROVED_SOME_INDICES", "floor", 1, True, "Proved on a sub-family of indices",
     "true on the image of an index transform only — a proper sub-family, not "
     "the universal statement", "◐", "🟨", "#facc15", "#a16207", "#1c1917",
     "someidx"),
    ("OPEN", "neutral", 0, False, "Open",
     "untouched — the root says nothing about it", "○", "🟦", "#1d4ed8",
     "#1e3a8a", "#fff", "open"),
    ("REFUTED_FACT", "immune", 0, False, "Refuted (standing counterexample)",
     "a refuted statement; a proof reaching it means an edge is wrong", "✕",
     "🟥", "#991b1b", "#450a0a", "#fff", "refuted"),
    ("PROVED_INDEPENDENTLY", "external", 3, False, "Proved independently",
     "already proved out of band, by a different argument", "■", "⬜", "#9ca3af",
     "#4b5563", "#1c1917", "indep"),
]

_FIELDS = ("name", "role", "rank", "propagates", "label", "meaning", "glyph",
           "swatch", "fill", "stroke", "text", "css")


def _levels(polarity):
    src = REFUTED_LEVELS if polarity == "refuted" else PROVED_LEVELS
    return [dict(zip(_FIELDS, row)) for row in src]


def default_config(slug, polarity="refuted", label=None, root_node=None,
                   reach_license=None, quantities_required=False):
    """A complete, renderable crater config. Every string under "map" is
    VERBATIM generated output -- editing one rewrites README bytes."""
    levels = _levels(polarity)
    if reach_license:
        levels[0]["reach_license"] = reach_license
    flag = ({"name": "orphaned_conditional_support",
             "rule": "propagated_source_neutral_target",
             "doc": "the node's known support was an implication FROM a now-refuted "
                    "statement; its truth value is untouched (falsity never "
                    "propagates forward) but the support is void"}
            if polarity == "refuted" else
            {"name": "obsolete_refutation_route",
             "rule": "propagated_target_neutral_source",
             "doc": "the contrapositive route 'refute the target to refute this "
                    "node' is dead now that the target is proved; the node's own "
                    "truth value is untouched"})
    arrows = ("X to Y means X implies Y, so Y falling pulls X down"
              if polarity == "refuted" else
              "X to Y means X implies Y, so X holding pushes Y up")
    refuted = polarity == "refuted"
    # The root MARKER, distinct from every level glyph so the crater centre is
    # legible in greyscale. A refuted crater's root is the impact that made the
    # hole (radiation); a proved crater's root is ground taken and held, so it
    # gets a planted flag -- and NOT ★/◐/○/✕/■, which are already spoken for by
    # the PROVED_* level glyphs above.
    root_glyph = "☢" if refuted else "⚑"
    # ...and the matching centre colour: blood-red is a refutation aesthetic and
    # is simply wrong on a theorem. Proved roots take the deep green of the
    # PROVED_ALL_INDICES stroke.
    root_fill = "#450a0a" if refuted else "#14532d"
    # Legend arrows must point the way the crater's REAL edges point, or the
    # generated legend contradicts the generated graph directly beneath it.
    # Under refutation the root is the SINK (X implies root; the root falling
    # pulls X down); under proof it is the SOURCE (root implies Y).
    if refuted:
        legend_edges = [
            '  LP1["any statement"]:::legendbox -->|"solid: index-preserving — the full level flows"| LP2["the root"]:::legendbox',
            '  LM1["any statement"]:::legendbox -.->|"dashed: index-TRANSFORMING — only the weaker floor level flows"| LM2["the root"]:::legendbox',
        ]
    else:
        legend_edges = [
            '  LP1["the root"]:::legendbox -->|"solid: index-preserving — the full level flows"| LP2["any statement"]:::legendbox',
            '  LM1["the root"]:::legendbox -.->|"dashed: index-TRANSFORMING — only the weaker floor level flows"| LM2["any statement"]:::legendbox',
        ]
    header = ("## The blast radius at a glance" if refuted else
              "## What the root reaches at a glance")
    footnote = (
        "**Reading the map.** Each node carries its status **glyph** as well as "
        "its colour, so the map survives greyscale, colour blindness and being "
        f"screenshotted away from this legend. {root_glyph} is the root; "
        "everything else is *computed* from it, never asserted.")
    return {
        "schema": "efa-crater-config/v1",
        "slug": slug,
        "label": slug,
        "title": f"The {slug} crater",
        "note": ("Declares everything crater-SPECIFIC. The propagation ENGINE lives in "
                 "tools/craterlib/ and knows none of it. Every string under \"map\" and "
                 "\"view_note\" is verbatim generated output: editing one rewrites "
                 "README.md / computed_statuses.json bytes."),
        "polarity": polarity,
        "index": {"variable": "n", "domain": "TODO: state the index domain, and "
                                             "which indices the root does NOT cover",
                  "root_index": None},
        "graph_schema": f"efa-{slug}/v1",
        "view_schema": f"efa-{slug}-computed/v1",
        "view_note": (f"GENERATED by tools/crater.py validate {slug} --write -- do not "
                      "hand-edit. Statuses are computed from certified roots + typed "
                      "edges; regenerate with --write."),
        "edge_types": ["implies", "equivalent"],
        "edge_semantics": {
            "key_aliases": ["index_semantics"],
            "value_aliases": {"index_preserving": "index_preserving",
                              "index_transforming": "index_transforming"},
            "required": True,
        },
        "levels": levels,
        "excluded_level": "EXCLUDED_UNVERIFIED",
        "inconsistency_phrase": ("a proven theorem" if polarity == "refuted"
                                 else "a standing counterexample"),
        "support_flag": flag,
        "paths": {"graph": "implication_graph.json",
                  "computed": "computed_statuses.json",
                  "quantities": "quantities.json", "readme": "README.md"},
        "quantities": {"required": quantities_required,
                       "evidence_keys": ["type", "artifact", "note"]},
        "quarantine_sections": ["likely_confabulated", "unclear_pending_rename"],
        "map": {
            "markers": {
                "begin": f"<!-- efa:crater-map:begin (generated by crater.py validate {slug} --write) -->",
                "end": "<!-- efa:crater-map:end -->",
            },
            "header": header,
            "preamble": ("*Generated from the ledger by `tools/crater.py validate "
                         f"{slug} --write`: all {{total}} nodes, every count, colour and "
                         "edge below are computed from `implication_graph.json` — never "
                         "hand-drawn. Plus {quarantined} quarantined candidate names.*"),
            "bar_footer": "{total} sourced statements (+{quarantined} quarantined)",
            "table_header": ["| | | Status | Count | What it means |",
                             "|:-:|:-:|:--|--:|:--|"],
            "flowchart_direction": "RL" if polarity == "refuted" else "LR",
            "arrow_preserving": "-->",
            "arrow_transforming": "-.->",
            "root_node": root_node,
            "root_template": '  {id}["' + root_glyph + ' {short} — THE ROOT"]:::root',
            "legend_lines": [
                "    direction LR",
                f'  LKEY["how to read the arrows — {arrows}"]:::legendnote',
            ] + legend_edges + [
                "  end",
            ],
            "classdef_lines": [
                f"  classDef root fill:{root_fill},stroke:#000,color:#fff,stroke-width:4px;",
                "  classDef legendbox fill:#f5f5f4,stroke:#78716c,color:#1c1917,stroke-dasharray:2 2;",
                "  classDef legendnote fill:#fffbeb,stroke:#a16207,color:#1c1917;",
                "  style legend fill:#fffbeb,stroke:#a16207;",
            ],
            "footnote": footnote,
        },
    }


ROOT_CHECK = '''#!/usr/bin/env python3
"""Placeholder root certificate for the {slug} crater.

REPLACE THIS. A crater's root is only as good as the check that certifies it:
this script must EXECUTE the claim (recompute the counterexample, replay the
proof witness, re-derive the table cell) and exit non-zero if it does not hold.
Exiting 0 unconditionally, as it does now, certifies nothing.
"""
import sys

print("{slug}: PLACEHOLDER root check -- certifies nothing yet")
sys.exit(0)
'''

README_STUB = """# {slug}

TODO: what fell, what certified it, and what the crater does NOT cover.

The block below is GENERATED by `python3 tools/crater.py validate {slug} --write`
and is staleness-gated: hand edits between the markers make validation fail.

{begin}
{end}
"""


def new_crater(root, slug, polarity="refuted", force=False):
    """Create atlas/<slug>/ and return the list of paths written."""
    root = Path(root)
    d = root / "atlas" / slug
    if d.exists() and not force:
        raise SystemExit(f"crater new: {d} already exists (refusing to overwrite)")
    (d / "checks").mkdir(parents=True, exist_ok=True)
    written = []

    check_rel = f"atlas/{slug}/checks/root_check.py"
    cfg = default_config(slug, polarity, root_node="root_claim_node",
                         reach_license=check_rel)
    (d / "crater.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
    written.append(d / "crater.json")

    full = cfg["levels"][0]["name"]
    graph = {
        "schema": cfg["graph_schema"],
        "title": f"{slug} implication graph",
        "note": ("Nodes are VERIFIED statements with a primary source; edges are TYPED "
                 "and CITED. Statuses are never stored here -- they are computed into "
                 "computed_statuses.json."),
        "roots": [{
            "node": "root_claim_node",
            "fact": full,
            "certificate": check_rel,
            "note": "TODO: what the certificate actually establishes, and at which index.",
        }],
        "nodes": [{
            "id": "root_claim_node",
            "name": "TODO: the root statement",
            "statement": "TODO: the precise mathematical statement.",
            "verification": "VERIFIED",
            "primary_source": "TODO: primary source",
            "sources": ["TODO"],
        }],
        "edges": [],
        "quarantine_findings": {"likely_confabulated": [],
                                "unclear_pending_rename": []},
    }
    (d / "implication_graph.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    written.append(d / "implication_graph.json")

    (d / "checks" / "root_check.py").write_text(ROOT_CHECK.format(slug=slug))
    written.append(d / "checks" / "root_check.py")

    (d / "README.md").write_text(README_STUB.format(
        slug=slug, begin=cfg["map"]["markers"]["begin"],
        end=cfg["map"]["markers"]["end"]))
    written.append(d / "README.md")
    return written
