# ANATOMY 2 — Fiber structure + Galois type of Alpöge's dim-3 Keller counterexample

**Date:** 2026-07-20 · **Round:** jc-round3 / fibers
**Claim-typing:** the counterexample is ALPÖGE's (with Claude Fable assistance); we verify
and derive. EVERYTHING below is CONDITIONAL on the root claim
(`atlas/jc-crater/root_claim.json`, tracked by `tools/jc_root_tripwire.py`).
**Map (certified root form):** f1=(1+xy)³z+y²(1+xy)(4+3xy), f2=y+3x(1+xy)²z+3xy²(4+3xy),
f3=2x−3x²y−x³z; det J ≡ −2 (étale); generically 3-to-1 (round-2 certified).
Base coordinates t=(t1,t2,t3); fiber cubic G1(t;y)=2y³−3t2y²+18t1y+(27t1²t3−18t1t2+t2³)
(round-2 certified elimination relation, re-verified in every certificate here).

## Headline results (all replayable, stdlib-only, exact rationals)

Let  **Q(t) = 27t1²t3² − 18t1t2t3 + 16t1 + t2³t3 − t2²**  (degree 4).

> **Not claimed:** that Q is irreducible over **Q**. Earlier drafts of this
> headline said so; that was a **CAS-level discovery probe** (sympy
> factorization) with **no stdlib replay path** in this directory, and nothing
> below uses it. Demoted to a discovery note, not a certified property. (Same
> demotion in `findings_nonproperness.md`, where this polynomial is called `E`.)

1. **GALOIS TYPE = S3** (`galois_group_s3.py`, exit 0).
   disc_y(G1) = **−2916·t1²·Q(t)** = −(54t1)²·Q. Specializing (t1,t2)=(1,0) gives
   −78732w²−46656, a certified-squarefree quadratic, hence not a square in C[w]; a
   field-square would be a polynomial square (UFD step) and would specialize to a square
   — contradiction. So disc is NOT a square in C(t1,t2,t3) and
   **Gal(closure of C(x,y,z)/C(f1,f2,f3)) = S3**, not C3: the 3:1 étale cover is
   NON-NORMAL, Galois closure degree 6. (Positive control: the same pipeline computes
   disc(y³−3y+1)=81=9², i.e. it would answer C3 for a genuine C3 cubic.)

2. **EXACT COUNT OFF THE DISCRIMINANT SET** (`fiber_count_generic.py`, exit 0).
   The x-elimination leading coefficient factors as **D = 9·t1·t2·Q** — the same Q.
   Certified lifting identities: (2D)·D³·(f_i(x(y,t),y,z(y,t)) − t_i) ≡ 0 mod G1 in
   Q[y,t] (x(y,t), z(y,t) read off the certified linear relations G2, G3). Combined with
   the pullback identities and disc = −2916t1²Q:
   **for every t with t1·t2·Q(t) ≠ 0, #F⁻¹(t) = 3 exactly.**
   All fiber degeneracy lives on the hypersurface {t1·t2·Q = 0}.

3. **STRATIFIED ANCHOR COUNTS 3 / 1 / 0** (`fiber_anchors.py`, exit 0). Ten rational
   anchors, one per stratum, each with a complete exact solve (linear-in-z resultant
   lemma + triple gcd + squarefree-part degree; every complex root accounted):

   | t | stratum | #fiber |
   |---|---|---|
   | (−1/4,0,0) | t2=0, Q=−4 (the root cert's collision target) | 3 |
   | (0,2,3) | t1=0, Q=20 — **disc=0 yet 3 points** | 3 |
   | (1,4,0), (2,5,1/4), (2,5,7/27) | Q=0 smooth | 1 |
   | (−16/27,0,1) | Q=0 ∩ t2=0 | 1 |
   | (0,1,1) | Q=0 ∩ t1=0 (t2t3=1) | 1 |
   | (0,0,5) | t1=t2=0 (⊂ Q=0; triple root, off-cusp) | 1 |
   | (3,6,2/9), (1/3,2,2/3) | cusp curve | **0 — EMPTY** |

   Readings: at (0,2,3) the cubic has a double root but two honest fiber points share
   y=2 (they differ in x) — **the t1² factor of disc is a y-elimination artifact, not
   fiber degeneracy; {Q=0} carries the true degeneracy.** On Q=0 anchors exactly the
   SIMPLE root of the cubic lifts; the two sheets merging in y escape to infinity
   (non-properness in action).

4. **F IS NOT SURJECTIVE — the image omits an entire rational curve**
   (`cusp_curve_empty.py`, exit 0). On the cusp curve **t(s) = (s²/12, s, 4/(3s))**
   (the locus where the t3-discriminant (t2²−12t1)³ of Q has its cusp), certified:
   G1(s²/12,s,T;y) = ¼(2y−s)³ + (1/16)s³(3sT−4), so over t(s) the only candidate is
   y=s/2; the slice resultants collapse to R12 = −⅛s(sx+2)² and R13 = 3(sx+2)(sx−2)+4;
   R12=0 forces sx=−2 where R13=4≠0. **F⁻¹(t(s)) = ∅ for EVERY complex s ≠ 0.**
   Consistent with theory (an étale map omitting a point is non-proper; Keller-ness
   never implied surjectivity) — but the explicit certified curve in the complement is
   a new invariant of the counterexample.

   Corollary bracket (new quantity candidate): **dim(C³ ∖ im F) ∈ [1, 2]** — lower
   bound from the cusp curve (result 4), upper bound because the complement is
   contained in the hypersurface {t1t2Q=0} (result 2).

## Fiber-count stratification (certified + honest edges)

- **{t1t2Q ≠ 0}: count 3** — THEOREM (result 2).
- **{t1=0 or t2=0} ∖ {Q=0}: count 3** — certified at anchors (0,2,3) and (−1/4,0,0);
  full t1=0 slice done as HAND ANALYSIS (discovery: branch xy=−1 gives 1 point, a
  quadratic in x at y=v gives 2; degenerates exactly on Q|t1=0 = t2²(t2t3−1)); the full
  t2=0 slice is anchor-level only. NOT a parametrized certificate — documented boundary.
- **{Q=0} ∖ cusp: count 1** — certified at 6 anchors covering all observed sub-strata;
  the "all points" version is a CONJECTURE supported by every probe. Boundary: no
  parametrized certificate (the double root's non-lifting was not certified familywise).
- **cusp curve: count 0** — THEOREM for all s≠0 (result 4).
- **Fiber-count spectrum observed = {0,1,3}. Whether count 2 occurs anywhere is OPEN**
  (theory caps fibers at 3 via ZMT/degree; our certificates never exhibited a 2).

## What is machine-checked vs human steps

Machine (identity-shaped, planted-failure controls, all exact): every polynomial
identity above; Sylvester det(G1,G1') = −2·disc grounding disc↔multiple-root;
squarefree tests via Euclid gcd; anchor solves; the collapse/resultant identities.
Human steps (stated in each docstring, elementary): Galois disc criterion for cubics +
constants-are-squares-in-C; UFD square argument + specialization soundness; the
linear-in-z resultant lemma (necessity/sufficiency, incl. a1=a3 cannot both vanish);
the final readings. Round-2 inheritances: irreducibility of G1 over C(t) (Gauss's
lemma step in `geometric_degree.py`).

**One exception to "all exact":** `galois_group_s3.py` **leg 4** is a
double-precision Durand–Kerner root computation compared at relative tolerance
1e-6. It **is** wired into that script's exit code (so it can fail the run), and
it is **not** part of the argument for S₃ — it only pins the discriminant
normalization convention from the root side. An earlier draft labelled it "not in
the trust path" while the ok-chain consumed it anyway; the label now matches the
wiring. Legs 1–3, which carry the S₃ conclusion, are exact.

## Files

- `galois_group_s3.py` — result 1 (runs ~0.1 s)
- `fiber_count_generic.py` — result 2 (~0.3 s)
- `fiber_anchors.py` — result 3 (~0.05 s)
- `cusp_curve_empty.py` — result 4 (~0.05 s)
- `run_all.sh` — replay every certificate in this directory
- `findings_fibers.md` — this file (round-3 working name: `findings.md` under
  `scratchpad/jc-round3/fibers/`; renamed on assembly so both anatomy findings
  files can share one directory)

**Not shipped** (round-3 scratchpad only, deliberately outside every trust
path): `discover1..6.py` — sympy DISCOVERY runs. Everything they found that
survives is re-proved from scratch by the certificates above; nothing cites them.

## Crater/registry suggestions (orchestrator's call, not done here)

- New certified invariants for the crater README: Galois type S3; disc = −2916t1²Q;
  D = 9t1t2Q; non-surjectivity + explicit missed rational curve.
- Quantity candidates: `jc-image-complement-dimension` [1,2] OPEN (is the complement
  exactly the cusp curve?); `jc-fiber-count-spectrum` ⊇{0,1,3}, membership of 2 OPEN.
- No typed edge is contradicted; nothing here touches per-dimension JC statuses.
