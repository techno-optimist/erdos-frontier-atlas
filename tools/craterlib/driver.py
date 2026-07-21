#!/usr/bin/env python3
"""Orchestration: validate (or regenerate) one crater end to end.

The CALL ORDER is contractual -- load, machine checks, quantities, propagate,
build view, render, write-or-compare. Machine checks run BEFORE propagation so a
failing certificate can never produce a status; the drift gate runs LAST so a
stale committed view is reported as staleness rather than as a schema error.
"""
import json

from . import checks as checks_mod
from .engine import propagate
from .render import build_view, extract_readme_map, render_map_block, splice_readme_map
from .schema import load_graph
from .spec import failer


def serialize_view(view):
    # ensure_ascii=False and the trailing newline are both load-bearing: the
    # graphs carry non-ASCII (o-umlaut, >=, the radiation glyph).
    return json.dumps(view, indent=2, ensure_ascii=False) + "\n"


def compute(spec):
    """Everything up to (not including) the write/compare decision."""
    g, nodes = load_graph(spec)
    checks = checks_mod.run_machine_checks(spec, g)
    checks_mod.check_reach_license(spec, checks)
    n_quantities = checks_mod.check_quantities(spec)
    status, flags = propagate(spec, g, nodes)
    view = build_view(spec, g, nodes, status, flags, checks)
    return {
        "graph": g, "nodes": nodes, "checks": checks,
        "n_quantities": n_quantities, "status": status, "flags": flags,
        "view": view, "rendered": serialize_view(view),
        "map_block": render_map_block(spec, g, nodes, status, flags),
    }


def validate(spec, write=False, quiet=False):
    fail = failer(spec.label)
    r = compute(spec)
    if write:
        spec.computed_path.write_text(r["rendered"])
        splice_readme_map(spec, r["map_block"])
        if not quiet:
            print(f"wrote {spec.computed_path.relative_to(spec.root)} "
                  "+ refreshed README map")
    else:
        if not spec.computed_path.exists():
            fail(f"{spec.computed_path.name} missing -- run with --write")
        if spec.computed_path.read_text() != r["rendered"]:
            fail(f"{spec.computed_path.name} is STALE -- statuses drifted from "
                 "the graph; regenerate with --write and review the diff")
        if extract_readme_map(spec) != r["map_block"]:
            fail(f"{spec.readme_path.name} crater map is STALE -- the rendered "
                 "graph/chart drifted from the ledger; regenerate with --write")
    if not quiet:
        counts = {}
        for s in r["status"].values():
            counts[s] = counts.get(s, 0) + 1
        print(f"{spec.label} VALID: "
              f"{len(r['nodes'])} nodes, {len(r['graph']['edges'])} edges, "
              f"{len(r['checks'])} machine checks passed, "
              f"{r['n_quantities']} quantities ledger-checked; statuses {counts}")
    return 0
