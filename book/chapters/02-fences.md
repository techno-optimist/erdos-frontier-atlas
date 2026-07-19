# 2 · Fences

<!-- DRAFT: lead pass pending -->

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
