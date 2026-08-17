# Independent all-pattern audit

`independent_replay.py` was written from a fresh reconstruction of the q=6
EHPS support and does not import the discovery sweep or `verify.py`.

It exhausts all `8^5 = 32,768` D4 role assignments and reconstructs the exact
five-cylinder union.  Exactly 256 assignments have maximum mass 3,645.  For
each one, the five 729-point cylinders are pairwise disjoint, so a potential
labelled by cylinder and full six-dimensional vertex is exactly an arbitrary
function on the geometric union.

The replay directly enumerates the 324 coordinate-level triples satisfying
all three modular midpoint equations.  It checks all 125 ordered cylinder
patterns, retaining full vertex identities, integer carries, raw canonical
endpoint costs, and coefficient accumulation when labels coincide.  Exactly
the five diagonal patterns have no positive cycle.  Each of the other 120
patterns hits all 256 maximizers, hence all 32 global D4 orbits.

Five live controls reject a corrupted midpoint, replacement of modular by
ordinary midpoint equality, a diagonal zero cycle, cross-cylinder point-label
merging, and zero right-hand side.

Replay:

```bash
python3 -I independent_replay.py
```

Expected verdict:

```text
PASS_INDEPENDENT_Q6_ALL_PATTERN_TORSION_AUDIT
```

Scope: finite q=6 only, unrestricted global potential on each maximum-mass
union.  This is not a continuum theorem, not a construction, and not a new
bound for `r_3(N)`.
