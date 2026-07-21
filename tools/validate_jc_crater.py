#!/usr/bin/env python3
"""Validator + propagation engine for the JC crater implication graph.

THIN WRAPPER. The engine now lives in tools/craterlib/ and is crater-agnostic;
everything Jacobian-specific -- paths, the status vocabulary, and every verbatim
byte of generated prose -- is declared in atlas/jc-crater/crater.json. This file
exists because its CLI and its module surface are referenced by
RESULTS_REGISTRY.md, the crater README, the skills, and tests/test_jc_crater.py;
its behaviour is byte-identical to the pre-migration engine. Equivalent generic
invocations: `python3 tools/crater.py validate jc-crater [--write]` and
`python3 tools/validate_crater.py jc-crater [--write]`.

The graph (atlas/jc-crater/implication_graph.json) stores VERIFIED nodes (each
with a primary-source statement) and TYPED edges (each with a citation). This
tool computes every node's post-counterexample status from the certified roots
by mechanical propagation -- statuses are DERIVED, never asserted -- and fails
loudly on schema violations, on drift between the committed generated view
(computed_statuses.json) and a fresh recomputation, and on INCONSISTENCY
(an edge chain that would refute a proven theorem means an edge is wrong).

NOTE this only staleness-gates the GENERATED VIEW against the committed graph
-- it says nothing about whether the graph's certified root (Alpöge's 2026
counterexample, "awaiting confirmation") is still current literature. For
that, see tools/jc_root_tripwire.py and atlas/jc-crater/root_claim.json.

Status vocabulary (computed):
  REFUTED_ALL_N_GE_3        chain of dimension-preserving implications from the
                            certified root (which the stabilization machine
                            check lifts from n=3 to all n>=3)
  REFUTED_SOME_FINITE_DIM   chain passes through a dimension-mixing edge: the
                            universal statement fails in at least one finite
                            dimension, location unknown (the honest modality)
  TRUE_THEOREM              proven statement (citation on the node)
  OPEN                      untouched by propagation
  EXCLUDED_UNVERIFIED       node failed literature verification; quarantined,
                            never propagated through

Flags (computed, orthogonal to status):
  orphaned_conditional_support   the node's known support was an implication
                                 FROM a now-refuted statement; its truth value
                                 is untouched (falsity never propagates forward
                                 along implications) but the support is void.

Propagation rules (modus tollens only -- truth never flows forward):
  X --implies(dimension_preserving)--> Y,  Y REFUTED_ALL_N_GE_3
      => X REFUTED_ALL_N_GE_3            (per-n: X_n => Y_n; not-Y_n => not-X_n)
  X --implies(dimension_mixing)--> Y,  Y refuted in any mode
      => X REFUTED_SOME_FINITE_DIM       (universal X => universal Y; Y fails
                                          somewhere => X fails somewhere)
  X --implies(dimension_preserving)--> Y,  Y REFUTED_SOME_FINITE_DIM
      => X REFUTED_SOME_FINITE_DIM       (the unknown failing dimension carries)
  X <--equivalent(dimension_preserving)--> Y   statuses copy both ways
  X <--equivalent(dimension_mixing)--> Y       refutation degrades to
                                               REFUTED_SOME_FINITE_DIM crossing
  Y --implies--> X,  Y refuted  =>  X.orphaned_conditional_support = true

Machine-checked edges name a script; the validator EXECUTES it and requires
exit 0 before the edge participates (e.g. the stabilization edge runs
atlas/jc-crater/padding_check.py; the root cites
certificates/jacobian-conjecture/verify.py).

Usage:
  python3 tools/validate_jc_crater.py            # validate + drift-check
  python3 tools/validate_jc_crater.py --write    # regenerate computed view
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import craterlib  # noqa: E402  (tools/ must be on the path first)

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "atlas" / "jc-crater" / "crater.json"
GRAPH = ROOT / "atlas" / "jc-crater" / "implication_graph.json"
COMPUTED = ROOT / "atlas" / "jc-crater" / "computed_statuses.json"
QUANTITIES = ROOT / "atlas" / "jc-crater" / "quantities.json"
README = ROOT / "atlas" / "jc-crater" / "README.md"

_BASE = craterlib.load_config(CONFIG, root=ROOT)

# The rendered map lives between these markers in the README and is regenerated
# from the ledger on --write; plain validation fails if it has drifted.
MAP_BEGIN = _BASE.map_begin
MAP_END = _BASE.map_end

# status -> (fill, label, css class, glyph, text colour, swatch)
# Mirrors atlas/jc-crater/crater.json for introspection and for callers that
# read this module's surface. Colour is NEVER load-bearing: every node also
# carries its glyph, and the fills differ in LIGHTNESS as well as hue so the map
# survives greyscale and red/green colour blindness.
STATUS_META = {lv.name: (lv.fill, lv.label, lv.css, lv.glyph, lv.text, lv.swatch)
               for lv in _BASE.levels}
_STATUS_ORDER = list(STATUS_META)
_MEANING = {lv.name: lv.meaning for lv in _BASE.levels}

EDGE_TYPES = set(_BASE.edge_types)
DIM_SEMANTICS = {k for k in _BASE.semantic_values if k.startswith("dimension_")}
# The two modalities that PROPAGATE by modus tollens. REFUTED_INDEPENDENTLY_PRE_2026
# is intentionally absent: nodes carrying it are historical context leaves, and
# load_graph forbids any edge incident to them, so they neither receive nor emit
# propagation -- the exclusion here is correct by construction, not a silent gap.
REFUTED = set(_BASE.propagating)
NODE_VERIFICATION = set(craterlib.NODE_VERIFICATION)


def _spec():
    """A fresh CraterSpec built from THIS module's globals on every call.

    Late binding is deliberate: callers (tests, ad-hoc scripts) rebind GRAPH /
    ROOT / QUANTITIES / README to scratch copies and then call the functions
    below, so a spec captured at import time would silently validate the wrong
    files. The level vocabulary and the map prose come from crater.json.
    """
    s = craterlib.load_config(CONFIG, root=ROOT)
    s.root = Path(ROOT)
    s.graph_path, s.computed_path = Path(GRAPH), Path(COMPUTED)
    s.quantities_path, s.readme_path = Path(QUANTITIES), Path(README)
    s.map_begin, s.map_end = MAP_BEGIN, MAP_END
    return s


def fail(msg):
    craterlib.failer(_BASE.label)(msg)


def load_graph():
    return craterlib.load_graph(_spec())


def run_machine_checks(g):
    return craterlib.run_machine_checks(_spec(), g)


def propagate(g, nodes):
    return craterlib.propagate(_spec(), g, nodes)


def _short(name):
    return craterlib.short_label(name)


def render_map_block(g, nodes, status, flags):
    return craterlib.render_map_block(_spec(), g, nodes, status, flags)


def build_view(g, nodes, status, flags, checks):
    return craterlib.build_view(_spec(), g, nodes, status, flags, checks)


def check_quantities():
    return craterlib.check_quantities(_spec())


def extract_readme_map():
    return craterlib.extract_readme_map(_spec())


def splice_readme_map(block):
    return craterlib.splice_readme_map(_spec(), block)


def main():
    return craterlib.validate(_spec(), write="--write" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
