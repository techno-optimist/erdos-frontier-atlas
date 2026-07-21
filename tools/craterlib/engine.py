#!/usr/bin/env python3
"""The propagation engine: a monotone fixpoint over a typed implication graph.

ONE algorithm serves both polarities. For each edge the crater's polarity yields
a set of LICENSED ORDERED PAIRS (src, dst); for each pair, if src carries a
propagating level then dst receives

    FULL   if the edge is index_preserving AND src is at FULL
    FLOOR  otherwise

merged by max-rank. That is the whole generalization: polarity is *only* the
licensed-pair function, and every other line is shared.

  refuted polarity (modus tollens, backwards)
      implies      licenses [(to, from)]     -- not-Y => not-X
      equivalent   licenses [(from,to), (to,from)]
    Statuses are claims about an indexed family X = forall n X_n. index_preserving
    means X_n => Y_n per n, so a FULL refutation ("false at every index in scope")
    carries at FULL. An index_transforming edge only relates the UNIVERSAL
    statements, so all you learn is an EXISTENTIAL -- some index fails, location
    unknown. That is the FLOOR, and it does not re-strengthen ALONG THE CHAIN: an
    existential composed with any further implication stays existential. (The
    NODE may still reach FULL through a different, independently justified edge --
    see WHAT IT DOES NOT GUARANTEE below. It is the propagated level that cannot
    climb, not the node.)

  proved polarity (modus ponens, forwards)
      implies      licenses [(from, to)]     -- X => Y
      equivalent   licenses [(from,to), (to,from)]
    index_preserving carries a universal proof; an index_transforming edge
    (n -> 2n, say) only establishes the target on the IMAGE of the index map, a
    proper sub-family -- the FLOOR.

    HONEST BOUNDARY, stated rather than hidden. Under refutation the floor is an
    existential, which is genuinely closed under further composition, so the
    2-point ladder loses nothing. Under proof the natural object is a SET of
    indices and the natural merge is union: proving Y on the evens and separately
    on {n = 3 mod 5} is strictly more than either. Collapsing that to FULL/FLOOR
    is a LOSSY COARSENING. We coarsen anyway, matching the JC discipline: the
    engine computes the coarse level and any sharper index set lives in the
    node's `notes` as hand analysis, never as a computed status.

WHAT THE ALGEBRA GUARANTEES. Three things, all structural, all cheap:

  1. Monotone max-rank merge over EDGE-JUSTIFIED levels. Each licensed pair is
     an independent justification for its target; a node keeps the strongest
     level any single one of them justifies. Nothing is ever lowered.
  2. Termination. `merge` only ever raises a node's rank on a finite ladder, so
     the fixpoint is order-independent and terminates even with cycles; the
     iteration cap is a live-lock tripwire, not the termination argument.
  3. Cross-polarity contact is an INCONSISTENCY, not a merge: a propagated level
     reaching an immune node halts the run, because some edge's direction or
     semantics is wrong.

WHAT IT DOES NOT GUARANTEE -- read this before trusting a FULL. **FULL is NOT
structurally reserved to roots.** `merge` is a bare max over ranks, so any edge
DECLARED index_preserving out of a node that already sits at FULL yields FULL on
its target, whatever that target held before -- FLOOR included. That is not a
leak, it is the point: a chain of index-preserving implications from a FULL node
carries the universal statement the whole way, and a node whose only prior
justification was an existential legitimately gains a universal one the moment a
second, stronger edge justifies it. That is exactly the intended modus
tollens/ponens. (What the engine genuinely declines to do is arithmetic: it never
composes declared index_maps to re-derive universality. It does not need to in
order to hand out FULL.)

CONSEQUENCE: LAUNDERING IS NOT PREVENTED ALGEBRAICALLY. Mis-type one edge -- an
index_transforming reduction declared index_preserving -- and FLOOR is silently
upgraded to FULL along it. The fixpoint stays internally consistent, the computed
view stays byte-stable, and every gate in this repo goes green. The engine cannot
detect it and no amount of algebra here will. **A mis-typed edge WILL launder.**
The protection is a RELEASE GATE, not a theorem: per-edge citations quoting the
primary source, human primary-source review of every edge's index semantics, and
the machine checks. This is not hypothetical -- this repo has already shipped
exactly that error. The Dixmier edge was re-typed twice (preserving -> mixing ->
preserving) before two independent fetches of the primary text settled it; in the
interim the computed statuses were wrong while every automated gate passed. See
the `notes` field on that edge in atlas/jc-crater/implication_graph.json.

Stated in the register of Aperture/verifier/WITNESS_SPEC.md section D.3, "The
soundness contract, honestly stated": edge-typing soundness is an OUT-OF-BAND
CONJUNCTION -- the release gate plus primary-source review -- not a property the
propagation provides. The fixpoint propagates levels; it does not validate edge
types. The per-edge citation exists so a computed status can at least NAME the
source its index semantics rests on; naming trust is not removing it. Stated as a
release gate, not miscredited to the algebra.

The one machine-checkable slice we DO enforce lives in schema.py: two edges on
the same ORDERED pair that disagree on index semantics are rejected, since a
graph declaring X->Y both preserving and transforming is mis-typed by
construction. That catches CONTRADICTORY typing only. A single, consistently
mis-typed edge -- the actual Dixmier failure mode -- passes it, and always will.
(Opposite-DIRECTION edges legitimately disagree: in the JC graph DC_n => JC_n is
preserving while JC_2n => DC_n is transforming. Only the same ordered pair is a
contradiction.)
"""
from .spec import failer


def licensed_pairs(spec, e):
    """The ordered (src, dst) pairs this edge licenses under the crater's
    polarity. This function is the ENTIRE polarity generalization."""
    a, b = e["from"], e["to"]
    if e["type"] == "implies":
        return [(b, a)] if spec.polarity == "refuted" else [(a, b)]
    # equivalent: statuses copy both ways (degrading across a transforming edge
    # in BOTH directions -- an equivalence across an index transform is two
    # implications with non-identity transforms).
    return [(a, b), (b, a)]


def seed(spec, g, nodes, fail):
    status = {}
    for nid, n in nodes.items():
        if n["verification"] != "VERIFIED":
            status[nid] = spec.excluded_level
        elif n.get("independent_fact"):
            # settled independently of the crater's root event; recorded
            # directly, never overridden
            status[nid] = n["independent_fact"]["status"]
        elif n.get("proven_theorem"):
            if spec.immune is None:
                fail(f"node {nid}: proven_theorem but the crater declares no "
                     "immune level")
            status[nid] = spec.immune
        else:
            status[nid] = spec.neutral
    for r in g["roots"]:
        status[r["node"]] = r["fact"]
    return status


def propagate(spec, g, nodes):
    """(status, flags) for every node. Statuses are DERIVED, never asserted."""
    fail = failer(spec.label)
    flags = {nid: {spec.support_flag_name: False} for nid in nodes}
    status = seed(spec, g, nodes, fail)

    def merge(nid, new):
        # A node keeps its strongest justified level; excluded and immune nodes
        # never accept a propagated level (immune contact = inconsistency).
        cur = status[nid]
        if cur == spec.excluded_level:
            fail(f"propagation reached quarantined node {nid} (validator bug)")
        if spec.immune is not None and cur == spec.immune:
            fail(f"INCONSISTENCY: edges derive {new} for {nid}, which is "
                 f"{spec.inconsistency_phrase} -- some edge's direction or "
                 "semantics is wrong")
        if spec.rank(new) > spec.rank(cur):
            status[nid] = new
            return True
        return False

    # Phase 1 -- status fixpoint. Flags are NOT touched here: a target that is
    # neutral mid-iteration may become propagated later, so an in-loop flag
    # would depend on edge order. Flags are a pure function of the FINAL
    # statuses, computed in phase 2.
    changed = True
    iterations = 0
    while changed:
        iterations += 1
        if iterations > len(nodes) + len(g["edges"]) + 5:
            fail("propagation failed to reach a fixpoint (cycle with growth?)")
        changed = False
        for e in g["edges"]:
            preserving = spec.edge_semantics(e, fail) == "index_preserving"
            for src, dst in licensed_pairs(spec, e):
                if status[src] in spec.propagating:
                    new = (spec.full if preserving and status[src] == spec.full
                           else spec.floor)
                    changed |= merge(dst, new)

    # Phase 2 -- the support flag, deterministic from final statuses. Under
    # refutation: a refuted X with X --implies--> Y whose Y is STILL neutral lost
    # its conditional support (falsity never flows forward; only the support
    # voids). Under proof the dual: Y proved with X --implies--> Y and X still
    # neutral means the contrapositive route "refute Y to refute X" is dead.
    for e in g["edges"]:
        if e["type"] != "implies":
            continue
        if spec.support_flag_rule == "propagated_source_neutral_target":
            probe, target = e["from"], e["to"]
        else:
            probe, target = e["to"], e["from"]
        if status[probe] in spec.propagating and status[target] == spec.neutral:
            flags[target][spec.support_flag_name] = True
    return status, flags
