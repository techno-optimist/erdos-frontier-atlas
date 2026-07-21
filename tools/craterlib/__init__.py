#!/usr/bin/env python3
"""craterlib -- the generic crater engine (stdlib only, Python 3).

A CRATER is a directed graph of mathematical statements with certified roots,
in which every node's status is COMPUTED from the roots by mechanical
propagation along typed, cited edges -- never asserted. The first one was the JC
crater (atlas/jc-crater), built around the 2026 Jacobian Conjecture
counterexample; this package is that engine with the Jacobian removed.

  spec.py      CraterSpec: the per-crater declaration (levels, polarity, paths,
               verbatim map prose). See its docstring for the derive-vs-declare
               split and why level NAMES are not derived.
  schema.py    graph validation (polarity-agnostic structure)
  engine.py    the propagation fixpoint; polarity is one licensed-pair function
  checks.py    machine-check runner + WS7 quantities ledger gate
  render.py    computed view + generated README map
  driver.py    validate/regenerate one crater end to end
  scaffold.py  `crater new <slug>` skeleton
  selftest.py  planted-failure controls

Entry points: tools/crater.py (new | list | validate | selftest),
tools/validate_crater.py <slug>, tools/validate_jc_crater.py (thin JC wrapper).
"""
from .checks import (check_quantities, check_reach_license, collect_checks,
                     gap_map_module, run_machine_checks)
from .driver import compute, serialize_view, validate
from .engine import licensed_pairs, propagate, seed
from .render import (build_view, extract_readme_map, render_map_block,
                     short_label, splice_readme_map)
from .schema import count_quarantined, load_graph
from .spec import (CANON_SEMANTICS, CONFIG_SCHEMA, ConfigError, CraterSpec,
                   Level, NODE_VERIFICATION, POLARITIES, failer, load_config)

__all__ = [
    "CANON_SEMANTICS", "CONFIG_SCHEMA", "ConfigError", "CraterSpec", "Level",
    "NODE_VERIFICATION", "POLARITIES", "build_view", "check_quantities",
    "check_reach_license", "collect_checks", "compute", "count_quarantined",
    "extract_readme_map", "failer", "gap_map_module", "licensed_pairs",
    "load_config", "load_graph", "propagate", "render_map_block",
    "run_machine_checks", "seed", "serialize_view", "short_label",
    "splice_readme_map", "validate",
]
