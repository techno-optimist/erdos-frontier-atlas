#!/usr/bin/env python3
"""CraterSpec -- the per-crater DECLARATION the generic engine runs on.

A "crater" is a directed implication graph with certified roots, whose every
node status is COMPUTED from the roots by mechanical propagation. The engine
(engine.py, schema.py, render.py) knows the *structure* of that computation and
nothing else; a crater declares its own vocabulary, prose and paths here.

The split is deliberate and is documented in atlas/jc-crater/README.md:

  the ENGINE derives     the level lattice (ranks + max-merge), which levels
                         propagate, the FULL-vs-FLOOR choice per edge from
                         (polarity, index semantics, source level), the
                         immune/external/excluded sentinels, the inconsistency
                         condition, the fixpoint, the flags;
  the CRATER declares    the level NAMES, their human meanings, and every byte
                         of rendered prose. Names are opaque strings to the
                         engine.

Why the names are not derived: a name like REFUTED_ALL_N_GE_3 asserts a
mathematical REACH ("every n >= 3") that does not follow from (polarity, index
semantics, root index). For the JC crater that reach is licensed by a separate
machine check (the stabilization lift, atlas/jc-crater/padding_check.py). A
generic rule that minted the same name from the triple would fabricate reach for
a crater whose root has no such lift. So the name stays declared -- and a level
in the "full" role MUST name the artifact licensing its reach in
`reach_license`, which the driver checks is among the machine checks actually
executed. That makes the one part of the name that IS a mathematical claim
traceable to a passing check instead of being free text.
"""
import json
from pathlib import Path

POLARITIES = {"refuted", "proved"}
# Roles are the ENGINE-visible semantics of a level; names are crater prose.
#   full     the strongest propagating level (survives an index-preserving hop)
#   floor    the conservative propagating level (any index-transforming hop)
#   neutral  untouched by propagation (the seed for an ordinary node)
#   immune   opposite-polarity fact; receiving a propagated level = INCONSISTENCY
#   external settled out of band; never propagates, never overridden
LEVEL_ROLES = {"full", "floor", "neutral", "immune", "external"}
REQUIRED_ROLES = ("full", "floor", "neutral")
CANON_SEMANTICS = ("index_preserving", "index_transforming")
SUPPORT_RULES = {"propagated_source_neutral_target", "propagated_target_neutral_source"}
NODE_VERIFICATION = {"VERIFIED", "UNVERIFIED_CANDIDATE"}
CONFIG_SCHEMA = "efa-crater-config/v1"


class ConfigError(Exception):
    """Malformed crater.json -- raised before any crater-labelled failure."""


def failer(label):
    """A crater-labelled hard failure. Every validation path raises SystemExit
    with '<label> INVALID: <msg>' -- never a warning, never a silent skip."""
    def fail(msg):
        raise SystemExit(f"{label} INVALID: {msg}")
    return fail


class Level:
    __slots__ = ("name", "role", "rank", "propagates", "label", "meaning",
                 "glyph", "swatch", "fill", "stroke", "text", "css",
                 "reach_license")

    def __init__(self, d):
        for field in ("name", "role", "label", "meaning", "glyph", "swatch",
                      "fill", "stroke", "text", "css"):
            v = d.get(field)
            if not (isinstance(v, str) and v.strip()):
                raise ConfigError(f"level {d.get('name','?')}: {field} must be a non-empty string")
            setattr(self, field, v)
        if self.role not in LEVEL_ROLES:
            raise ConfigError(f"level {self.name}: bad role {self.role!r}")
        rank = d.get("rank")
        if type(rank) is not int:          # bool is an int subclass; reject it
            raise ConfigError(f"level {self.name}: rank must be an int")
        self.rank = rank
        prop = d.get("propagates")
        if not isinstance(prop, bool):
            raise ConfigError(f"level {self.name}: propagates must be a bool")
        self.propagates = prop
        self.reach_license = d.get("reach_license")


class CraterSpec:
    """Everything the engine needs about one crater. Paths are absolute."""

    def __init__(self, cfg, root, crater_dir):
        if cfg.get("schema") != CONFIG_SCHEMA:
            raise ConfigError(f"crater config schema must be {CONFIG_SCHEMA}")
        self.config = cfg
        self.root = Path(root)
        self.dir = Path(crater_dir)
        self.slug = cfg["slug"]
        self.label = cfg.get("label", self.slug)
        self.title = cfg.get("title", self.slug)

        self.polarity = cfg.get("polarity")
        if self.polarity not in POLARITIES:
            raise ConfigError(f"polarity must be one of {sorted(POLARITIES)}")
        self.index = cfg.get("index", {})

        self.graph_schema = cfg["graph_schema"]
        self.view_schema = cfg["view_schema"]
        self.view_note = cfg["view_note"]

        self.edge_types = set(cfg.get("edge_types", ["implies", "equivalent"]))
        es = cfg.get("edge_semantics", {})
        self.semantic_keys = list(es.get("key_aliases", ["index_semantics"]))
        self.semantic_values = dict(es.get("value_aliases", {v: v for v in CANON_SEMANTICS}))
        for k, v in self.semantic_values.items():
            if v not in CANON_SEMANTICS:
                raise ConfigError(f"edge_semantics: {k!r} maps to non-canonical {v!r}")
        self.semantics_required = bool(es.get("required", True))

        levels = [Level(d) for d in cfg["levels"]]
        if not levels:
            raise ConfigError("levels[] must be non-empty")
        self.levels = levels
        # ORDER IS LOAD-BEARING: it drives the bar rows, the status-table rows
        # and the mermaid node ordering. crater.json stores it as a JSON array.
        self.level_order = [lv.name for lv in levels]
        if len(set(self.level_order)) != len(self.level_order):
            raise ConfigError("duplicate level names")
        self._by_name = {lv.name: lv for lv in levels}
        self._by_role = {}
        for lv in levels:
            if lv.role in ("full", "floor", "neutral", "immune", "external") \
               and lv.role in self._by_role:
                raise ConfigError(f"two levels share role {lv.role}")
            self._by_role[lv.role] = lv
        for role in REQUIRED_ROLES:
            if role not in self._by_role:
                raise ConfigError(f"levels[] must declare a {role} level")
        self.full = self._by_role["full"].name
        self.floor = self._by_role["floor"].name
        self.neutral = self._by_role["neutral"].name
        self.immune = self._by_role["immune"].name if "immune" in self._by_role else None
        self.external = self._by_role["external"].name if "external" in self._by_role else None
        self.propagating = {lv.name for lv in levels if lv.propagates}
        if self.full not in self.propagating or self.floor not in self.propagating:
            raise ConfigError("the full and floor levels must both propagate")
        if self._by_role["full"].rank <= self._by_role["floor"].rank:
            raise ConfigError("the full level must outrank the floor level")
        self.excluded_level = cfg.get("excluded_level", "EXCLUDED_UNVERIFIED")
        if self.excluded_level in self._by_name:
            raise ConfigError("excluded_level must NOT be a rendered level")
        self.inconsistency_phrase = cfg.get("inconsistency_phrase", "a proven theorem")

        sf = cfg.get("support_flag", {})
        self.support_flag_name = sf.get("name", "orphaned_conditional_support")
        self.support_flag_rule = sf.get("rule", "propagated_source_neutral_target")
        if self.support_flag_rule not in SUPPORT_RULES:
            raise ConfigError(f"support_flag.rule must be one of {sorted(SUPPORT_RULES)}")

        p = cfg.get("paths", {})
        self.graph_path = self.dir / p.get("graph", "implication_graph.json")
        self.computed_path = self.dir / p.get("computed", "computed_statuses.json")
        self.quantities_path = self.dir / p.get("quantities", "quantities.json")
        self.readme_path = self.dir / p.get("readme", "README.md")

        q = cfg.get("quantities", {})
        self.quantities_required = bool(q.get("required", False))
        self.evidence_keys = set(q.get("evidence_keys", ["type", "artifact", "note"]))

        self.quarantine_sections = list(cfg.get("quarantine_sections", []))

        m = cfg.get("map", {})
        self.map_begin = m["markers"]["begin"]
        self.map_end = m["markers"]["end"]
        self.map_header = m.get("header", "")
        self.map_preamble = m.get("preamble", "")
        self.map_bar_footer = m.get("bar_footer", "{total} statements (+{quarantined} quarantined)")
        self.map_table_header = list(m.get("table_header", []))
        self.map_direction = m.get("flowchart_direction", "RL")
        self.map_arrow_preserving = m.get("arrow_preserving", "-->")
        self.map_arrow_transforming = m.get("arrow_transforming", "-.->")
        self.map_root_node = m.get("root_node")
        self.map_root_template = m.get("root_template")
        self.map_legend_lines = list(m.get("legend_lines", []))
        self.map_classdef_lines = list(m.get("classdef_lines", []))
        self.map_footnote = m.get("footnote", "")

    # -- level access -------------------------------------------------------
    def level(self, name):
        try:
            return self._by_name[name]
        except KeyError:
            raise ConfigError(f"no such level {name!r} in {self.slug}")

    def rank(self, name):
        lv = self._by_name.get(name)
        return lv.rank if lv else 0

    def root_facts(self):
        """Facts a root entry may assert: any propagating level, or the immune
        one (a crater may certify that a node is a standing theorem)."""
        return set(self.propagating) | ({self.immune} if self.immune else set())

    # -- edge semantics -----------------------------------------------------
    def edge_semantics(self, e, fail):
        """Canonical index semantics of one edge, honouring the key/value alias
        table. The alias table is what lets a legacy graph keep its own key
        (JC's `dimension_semantics`) with zero output-byte risk: the canonical
        value is never emitted, it only picks solid-vs-dashed and FULL-vs-FLOOR."""
        present = [k for k in self.semantic_keys if k in e]
        if len(present) > 1:
            fail(f"edge {e.get('from')}->{e.get('to')}: declares more than one of "
                 f"{self.semantic_keys}")
        if not present:
            if self.semantics_required:
                fail(f"edge {e.get('from')}->{e.get('to')}: missing "
                     f"{self.semantic_keys[0]}")
            return "index_preserving"
        raw = e[present[0]]
        canon = self.semantic_values.get(raw)
        if canon is None:
            fail(f"edge {e.get('from')}->{e.get('to')}: bad {present[0]}")
        return canon


def load_config(path, root=None):
    """Load a crater.json. `root` defaults to the repo root two levels above
    the crater directory (atlas/<slug>/crater.json -> repo)."""
    path = Path(path).resolve()
    cfg = json.loads(path.read_text())
    crater_dir = path.parent
    if root is None:
        root = crater_dir.parent.parent
    return CraterSpec(cfg, root, crater_dir)
