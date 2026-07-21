# Two rational y-roots: at most one lifts (soft → structural)

Date: 2026-07-21 (updated)

## Observation (sample)

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

## Structural upgrade (2026-07-21)

See [`THEOREM_FIBER_NO_SIZE2_ON_VE.md`](THEOREM_FIBER_NO_SIZE2_ON_VE.md).

On \(V(E)\), \(G_1=2(y-a)^2(y-b)\) (or a triple root). The multiple root \(a\)
**never lifts**: the \(R_{12}\) residual at \(y=a\) equals \(a-t_2\) independently
of \(x\) (using \(t_1=a(t_2-a)/3\) from \(G_1'=0\)), and the only candidate
\(x=-1/a\) is blocked by \(b_1=-t_1\) whenever \(t_1\neq 0\). Combined with the
reduced annihilator \(\Phi_x\) (unique forced \(x_*\) on \(V(E)\setminus\gamma\)),
at most the simple root can lift, and at most once.

So the observational patterns `1+0` / `0+1` are the only possibilities for
double+simple points: the double side is always the zero.

Artifact: `FIBER_TWO_Y_LEMMA.json`, probes `probe_fiber_two_y_lemma.py`,
`probe_fiber_no_size2_ve.py`.

## Scope

Structural non-lifting of the double root is elementary algebra on anatomy
annihilators (human case-split + specialization checks). **Does not**
auto-update the crater ledger; root claim remains external.
