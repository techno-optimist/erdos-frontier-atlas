# 2 · Fences

Some theorems are true "for all sufficiently large N" — and silent about where
sufficiently large begins. When the proof runs through compactness, ergodic
limits, or the Subspace Theorem, no computable threshold falls out at all: the
theorem is **ineffective**. Its finite side, though, is often computable, and
that asymmetry is a place where machine work adds something a theorem cannot:
compute the exact values in a finite range and record where the asymptotic
statement is last violated. That last violation is a **lower fence** for the
ineffective threshold — a measured point the threshold provably sits above.

A fence is not a location. Sporadic exceptions beyond the computed range are
never excluded — the theorem itself is what forbids claiming otherwise — and
every fence table must say so in the same breath as its data. The exemplar is
Erdős–Sárközy #13: Bedert proved `f(N) ≤ ⌊N/3⌋ + 1` for all large N with an
ineffective threshold, and the certified exact table locates the last
exception in the computed range.

```efa:table fence_13
```

Fence-hunting generalizes. The WS4 shortlist below is the result of a graded
hunt across three thematic slices for more theorems with this shape —
ineffective threshold, computable finite side. The hunt's discipline is the
point: every candidate passed an effectivization check (a literature search
for a later effective bound) *before* grading, and the candidates that failed
it are recorded as dead rather than discarded, so the search is never repeated.

```efa:table shortlist
```

The hunt's second build taught the method its sharpest lesson so far. The
Furstenberg–Katznelson axis-aligned square survived every effectivization check
— the theorem is genuinely rate-free through the current literature — and its
exact table `D(1..9)` is certified and externally consistent with OEIS A227133
([`certificates/fk-square`](../certificates/fk-square)). But the fence is
structurally **degenerate**: the density decays so slowly that no pinned
threshold is crossed within any exact-search range. A fence needs an
*interior* exception, and this configuration cannot produce one. That null is
recorded in the shortlist rather than discarded — the correction of a research
direction is a result, and the next hunt inherits it: prefer one-dimensional
configurations whose search reach extends deep into the exception zone.
