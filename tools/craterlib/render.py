#!/usr/bin/env python3
"""The generated VIEW (computed_statuses.json) and the generated README map.

Both are deterministic functions of (graph, computed statuses, crater config), so
both are staleness-gated: a hand edit to either is caught by a plain validate
run. Every human sentence in the map comes from the crater config verbatim --
the renderer supplies only structure (counts, bar, table, mermaid, ordering).
"""
import re

from .spec import failer


def short_label(name):
    # Strip parenthetical qualifiers (which may lead OR trail), keep the first
    # clause, render comparison operators, drop chars that break mermaid labels.
    s = re.sub(r"\([^)]*\)", "", name)
    s = s.split(",")[0].split(" — ")[0].split(":")[0]
    s = s.replace("<=", "≤").replace(">=", "≥")
    for bad in ('"', "<", ">", "[", "]", "{", "}", "|"):
        s = s.replace(bad, "")
    return " ".join(s.split()) or name.strip()


def build_view(spec, g, nodes, status, flags, checks):
    """Key order is contractual (it is the committed file's byte order)."""
    return {
        "schema": spec.view_schema,
        "note": spec.view_note,
        "machine_checks": checks,
        "statuses": {
            nid: {
                "status": status[nid],
                spec.support_flag_name: flags[nid][spec.support_flag_name],
                "name": nodes[nid]["name"],
            } for nid in sorted(nodes)
        },
        "summary": {
            s: sorted(n for n in status if status[n] == s)
            for s in sorted(set(status.values()))
        },
    }


def render_map_block(spec, g, nodes, status, flags):
    """The human-readable map, GENERATED from the ledger: an ASCII proportion
    bar, a status table, and a colored Mermaid implication graph. Deterministic
    (sorted), so the README block is staleness-gated like the computed view."""
    fail = failer(spec.label)
    counts = {}
    for nid in nodes:
        counts[status[nid]] = counts.get(status[nid], 0) + 1
    total = sum(counts.values())
    quar = g.get("quarantine_findings", {})
    n_quar = sum(len(quar.get(s, [])) for s in spec.quarantine_sections)
    present = [s for s in spec.level_order if counts.get(s)]
    peak = max(counts.values()) if counts else 1

    L = [spec.map_begin, ""]
    L.append(spec.map_header)
    L.append("")
    L.append(spec.map_preamble.format(total=total, quarantined=n_quar))
    L.append("")

    # ASCII proportion bar -- renders everywhere, monospace in a fence.
    L.append("```text")
    label_w = max(len(spec.level(s).label) for s in present)
    for s in present:
        lv = spec.level(s)
        c = counts[s]
        bar = "█" * max(1, round(20 * c / peak))
        L.append(f"{lv.glyph} {lv.label.ljust(label_w)}  {bar} {c}")
    L.append("")
    L.append(f"{' ' * (label_w + 2)}  "
             + spec.map_bar_footer.format(total=total, quarantined=n_quar))
    L.append("```")
    L.append("")

    # Status table. The swatch column is what ties the diagram's colours to the
    # glyphs; without it the bar chart speaks in glyphs and the graph speaks in
    # colour, with nothing mapping between.
    L.extend(spec.map_table_header)
    for s in present:
        lv = spec.level(s)
        L.append(f"| {lv.swatch} | {lv.glyph} | **{lv.label}** | {counts[s]} | {lv.meaning} |")
    L.append("")

    # Mermaid map: nodes coloured by level, the crater centre a distinct SHAPE.
    # Every label carries its glyph so the map is readable in greyscale, when
    # colour-blind, and when screenshotted away from this legend (which is how
    # it usually travels) -- colour is NEVER load-bearing.
    L.append("```mermaid")
    L.append(f"flowchart {spec.map_direction}")
    ordered = sorted(nodes, key=lambda nid: (spec.level_order.index(status[nid]), nid))
    for nid in ordered:
        lv = spec.level(status[nid])
        if spec.map_root_node is not None and nid == spec.map_root_node:
            if not spec.map_root_template:
                fail("map.root_node is declared without a map.root_template")
            L.append(spec.map_root_template.format(
                id=nid, short=short_label(nodes[nid]["name"])))
        else:
            L.append(f'  {nid}["{lv.glyph} {short_label(nodes[nid]["name"])}"]:::{lv.css}')
    for e in g["edges"]:
        arrow = (spec.map_arrow_preserving
                 if spec.edge_semantics(e, fail) == "index_preserving"
                 else spec.map_arrow_transforming)
        L.append(f"  {e['from']} {arrow} {e['to']}")
    L.extend(spec.map_legend_lines)
    L.extend(spec.map_classdef_lines)
    for s in spec.level_order:
        lv = spec.level(s)
        L.append(f"  classDef {lv.css} fill:{lv.fill},stroke:{lv.stroke},color:{lv.text};")
    L.append("```")
    L.append("")
    L.append(spec.map_footnote)
    L.append("")
    L.append(spec.map_end)
    return "\n".join(L)


def extract_readme_map(spec):
    """Return the current generated map block (inclusive of markers), or None."""
    text = spec.readme_path.read_text()
    i, j = text.find(spec.map_begin), text.find(spec.map_end)
    if i == -1 or j == -1 or j < i:
        return None
    return text[i:j + len(spec.map_end)]


def splice_readme_map(spec, block):
    """Replace the marked block in README.md (markers must already exist)."""
    text = spec.readme_path.read_text()
    i, j = text.find(spec.map_begin), text.find(spec.map_end)
    if i == -1 or j == -1 or j < i:
        failer(spec.label)(
            f"README.md is missing the crater-map markers "
            f"({spec.map_begin} ... {spec.map_end}) -- add them where the map "
            "should render")
    spec.readme_path.write_text(text[:i] + block + text[j + len(spec.map_end):])
