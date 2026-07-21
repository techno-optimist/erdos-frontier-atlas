# Soft observation: two rational y-roots never both lift

Date: 2026-07-21

## Observation (not a closed theorem)

On **631** distinct rational points of the non-properness set \(V(E)\) of
Alpöge's map, whenever the fiber cubic \(G_1(t;y)\) has **exactly two**
distinct rational roots, the exact fiber cardinalities at those \(y\)-values
are always one of:

- `1+0` (309 points)
- `0+1` (299 points)

Never `1+1` and never `2+0`. Overall fiber histogram on the sample:
`{0: 12, 1: 619}` — **zero size-2 fibers**.

Artifact: `FIBER_TWO_Y_CONJECTURE.json`  
Engine: resultant-gcd fiber counts + rational root factoring of \(G_1\).

## Soft conjecture

For every rational \(t \in V(E)\) at which \(G_1(t;y)\) splits with two distinct
rational roots, exactly one of those roots lifts to a preimage under \(F\).

If true for all complex \(t \in V(E)\setminus\gamma\), this would exclude
size-2 fibers of the form "two simple \(y\)-roots each contributing one point",
narrowing the remaining size-2 possibilities to a single \(y\) with two
\((x,z)\) or irrational-\(y\) configurations.

## Scope

Rational sample only. **Not** a familywise certificate. Does **not** close
`jc-fiber-count-spectrum-size`.
