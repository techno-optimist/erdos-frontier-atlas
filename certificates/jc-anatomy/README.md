# Anatomy of the counterexample map

Six stdlib-only certificates that take Alpöge's dim-3 Keller map apart: *where*
it fails to be proper, *what* its fibers look like, *which* Galois group its
3-sheeted cover has, *what* it fails to hit, and *why* it could not have been
ruled out by the existing dim-3 theorems.

**Claim typing.** The map `F` is **Alpöge's** (with Claude Fable assistance);
we **verify and derive, we do not discover the root**. Everything here is
**CONDITIONAL** on that root claim — his counterexample is *awaiting
confirmation*: widely machine-verified within a day, **not** peer-reviewed, and
nothing in this directory has been peer-reviewed either. See
[`../jacobian-conjecture/`](../jacobian-conjecture/) for the root certificate
and [`../../atlas/jc-crater/root_claim.json`](../../atlas/jc-crater/root_claim.json)
for the tracked claim identity.

The map:

```
f1 = (1+xy)^3 z + y^2 (1+xy)(4+3xy)
f2 = y + 3x(1+xy)^2 z + 3xy^2 (4+3xy)
f3 = 2x - 3x^2 y - x^3 z          det J_F ≡ −2  (étale), generically 3-to-1
```

Target coordinates `t = (t1,t2,t3)`. Two polynomials run through everything —
the same object under two names, because the two workstreams met in the middle:

```
E(t) = Q(t) = 27 t1²t3² − 18 t1t2t3 + 16 t1 + t2³t3 − t2²      (degree 4)
G1(t;y) = 2y³ − 3t2 y² + 18t1 y + (27t1²t3 − 18t1t2 + t2³)     (the fiber cubic)
```

`E` is called `E` in the non-properness certificate and `Q` in the fiber
certificates. **Not claimed:** that it is irreducible over **Q** or **C**. That
was a CAS-level discovery probe with no replay path here, and no result below
uses it — the density argument is stated per irreducible component precisely so
it never needs to know what the components are.

## Results

### 1. The non-properness set is exactly `V(E)` — `certify_nonproperness.py`

`S_F = V(E)`: the Jelonek set (asymptotic set = the set of points at which `F`
is not proper) is exactly this quartic hypersurface. Over `C³ ∖ V(E)` the map
is proper and étale, hence an **unbranched 3-sheeted covering**; over every
point of `V(E)` at least one preimage has escaped to infinity.

**Only `x` escapes.** `y` and `z` satisfy cubics over `C[t]` with *constant*
leading coefficients (2 and 8), while an annihilator of `x`

```
Phi_x(t,X) = E(t)·X³ + (4 − 3t2t3)·X − 2t3
```

has leading coefficient exactly `E(t)` — the cubic term dies precisely on
`V(E)`, and two roots fly to infinity. (`Phi_x` is claimed to be **an**
annihilator, never the minimal one; minimality is a CAS-level step this
certificate quarantines rather than uses.)

**Mechanism.** `disc_Y(G1) = −2916·t1²·E(t)`, certified. Where the fiber cubic
degenerates, an étale map cannot branch — so on the `E` factor the colliding
preimages must instead vanish to infinity, while the `t1²` factor is a *false
alarm*: two fiber points share a `y` but differ in `x`, and `F` stays proper
there. That is why `S_F` is `V(E)` and not the full discriminant locus.

18 machine checks (3 annihilator identities + 1 discriminant identity + 3
density facts + 3 witness fibers + 2 omitted-curve identities + 1 off-`V(E)`
fiber + 5 planted-failure controls). The script tallies its own `check()` calls
and refuses to certify if the total drifts from 18.

### 2. Exact generic fiber count — `fiber_count_generic.py`

The `x`-elimination leading coefficient factors as `D = 9·t1·t2·Q`, and

> **for every `t` with `t1·t2·Q(t) ≠ 0`, `#F⁻¹(t) = 3` exactly.**

Round 2 certified "generically 3-to-1"; this upgrades *generically* to an
**explicit dense open set**. All fiber degeneracy — including the empty fibers —
is confined to the hypersurface `{t1·t2·Q = 0}`.

### 3. Galois type is `S3` — `galois_group_s3.py`

`disc = −2916·t1²·Q = −(54t1)²·Q`, so `disc` is a square in `C(t)` iff `Q` is.
Specializing `(t1,t2) = (1,0)` gives `−78732w² − 46656`, certified squarefree,
hence not a square in `C[w]`; a field square would be a polynomial square (UFD
step) and would specialize to a square. So the Galois group of the closure is

> **`S3`, not `C3`: the 3:1 étale cover is NON-NORMAL, Galois closure degree 6.**

Positive control: the same pipeline computes `disc(y³−3y+1) = 81 = 9²`, i.e. it
*would* answer `C3` for a genuine `C3` cubic.

### 4. Stratified fiber counts 3 / 1 / 0 — `fiber_anchors.py`

Ten rational anchors, one per stratum, each with a complete exact solve (every
complex root accounted for):

| `t` | stratum | `#F⁻¹(t)` |
|---|---|--:|
| `(−1/4,0,0)` | `t2=0`, `Q=−4` — the root certificate's collision target | 3 |
| `(0,2,3)` | `t1=0`, `Q=20` — **disc = 0 yet 3 points** | 3 |
| `(1,4,0)`, `(2,5,1/4)`, `(2,5,7/27)` | `Q=0`, smooth | 1 |
| `(−16/27,0,1)` | `Q=0 ∩ t2=0` | 1 |
| `(0,1,1)` | `Q=0 ∩ t1=0` | 1 |
| `(0,0,5)` | `t1=t2=0` | 1 |
| `(3,6,2/9)`, `(1/3,2,2/3)` | cusp curve | **0 — EMPTY** |

At `(0,2,3)` the cubic has a double root but two honest fiber points share
`y = 2` and differ in `x` — confirming the `t1²` factor is a `y`-elimination
artifact, not fiber degeneracy.

### 5. `F` is NOT surjective — `cusp_curve_empty.py` (and `(I6)` of result 1)

The image omits an entire punctured rational curve:

```
γ(s) = (s²/12, s, 4/(3s)),    s ≠ 0
```

Two independent certified routes. *(I6, non-properness certificate)*: on `γ`
both non-leading coefficients of `Phi_x` vanish identically while `−2t3 =
−8/(3s) ≠ 0`, so the annihilator identity is unsatisfiable — no preimage can
exist. *(`cusp_curve_empty.py`)*: `G1` collapses on `γ` so the only candidate is
`y = s/2`, and the slice resultants `R12 = −⅛s(sx+2)²`, `R13 = 3(sx+2)(sx−2)+4`
are simultaneously unsatisfiable — `R12 = 0` forces `sx = −2`, where `R13 = 4 ≠ 0`.

`γ` is exactly `V(E) ∩ {4 − 3t2t3 = 0}` (elimination witness is the perfect
square `3(t2² − 12t1)²`, machine-checked). *Observation, CAS-level, not used by
any claim: `γ` is precisely the singular locus of `V(E)` — the map omits exactly
the singular locus of its own Jelonek set.*

Keller-ness never implied surjectivity, and an étale map that omits a point is
necessarily non-proper — so this is consistent with theory. The *explicit
certified curve* in the complement is what is new.

### 6. The map is outside the proven dim-3 islands — `degree_floor_check.py`

A counterexample must not be a map the literature had already proved
invertible. Certified: `J_F` is **not symmetric** (so `F` is outside de Bondt's
gradient island, `arXiv:1203.6605`, where JC holds in dim ≤ 3), and the
normalized `J_F(0)⁻¹F = x + H` has **mixed-degree** `H` (component degree sets
`{3,4}`, `{2..6}`, `{2..7}`, so `F` is outside the de Bondt–van den Essen
homogeneous island, *J. Algebra* 294 (2005) 294–306). Both detectors carry a
planted-failure control: a genuine gradient map must read symmetric, and a
planted homogeneous `H = (0, x³, y³)` must be detected as homogeneous.

## Fiber-count spectrum

Observed and certified: **`{0, 1, 3}`**. Whether a fiber of size exactly **2**
occurs anywhere is **OPEN** — theory caps fibers at 3 (étale, degree 3), the
bound `≤ 2` is certified on `V(E) ∖ γ`, and every probe returned 1, but no
certificate ever exhibited a 2 and none excludes one.

## Replay

```
bash   certificates/jc-anatomy/run_all.sh                       # all six, exit 0 = all pass
python3 -I certificates/jc-anatomy/certify_nonproperness.py     # result 1   (~0.12 s)
python3 -I certificates/jc-anatomy/fiber_count_generic.py       # result 2   (~0.21 s)
python3 -I certificates/jc-anatomy/galois_group_s3.py           # result 3   (~0.02 s)
python3 -I certificates/jc-anatomy/fiber_anchors.py             # result 4   (~0.02 s)
python3 -I certificates/jc-anatomy/cusp_curve_empty.py          # result 5   (~0.02 s)
python3 -I certificates/jc-anatomy/degree_floor_check.py        # result 6   (~0.01 s)
```

`run_all.sh` cds to its own directory, so it works from any cwd. `-I` isolates
the interpreter from `PYTHONPATH` and the user site-directory — these
certificates import only `fractions`, `sys` and (leg 4 of `galois_group_s3.py`)
`cmath`, and the flag makes that auditable rather than merely claimed. Every script uses the
same exact-`Fraction` monomial-dict engine as
[`../jacobian-conjecture/verify.py`](../jacobian-conjecture/verify.py), so all
of them agree on what "exact" means, and every script carries planted-failure
controls that must fail as planted.

## Honest boundaries

These are the load-bearing gaps. They are boundaries, not results.

- **Classical prose steps `(L1)–(L5)`** in `certify_nonproperness.py` are
  asserted, not machine-checked: the root bound (leading coefficient bounded
  away from 0 ⇒ roots bounded); asymptotic set = non-properness set
  (compactness); proper + étale ⇒ covering with sheet count = the certified
  generic degree 3; closedness of `S_F`; `disc = 0 ⇒ ≤ 2 distinct roots`. Each
  is standard, and each is stated in the docstring where the machine stops.
- **Irreducibility of `E`/`Q`** over **Q** or **C**: CAS-probed only, never
  certified, and deliberately never used.
- **`Phi_x` minimality**: not claimed. Only annihilation is certified.
- **`im(F) = C³ ∖ γ` exactly**: NOT established. What is certified is the two
  inclusions `γ ∩ im(F) = ∅` and `C³ ∖ V(E) ⊆ im(F)`. Closing the gap needs a
  limit argument plus one CAS-level step. Typed DERIVED-OBSERVATION; do not
  promote.
- **Fiber size 2**: existence/non-existence undetermined (see above).
- **Whole-stratum counts**: `{Q=0} ∖ cusp: count 1` and the full `t1=0` /
  `t2=0` slices are certified **at anchors**, not familywise. The "all points"
  versions are conjectures supported by every probe — there is no parametrized
  certificate.
- **`galois_group_s3.py` leg 4** is double-precision Durand–Kerner at relative
  tolerance `1e-6`. It **is** wired into that script's exit code (it can fail
  the run) and it is **not** part of the argument for `S3` — it only pins the
  discriminant normalization convention from the root side. Legs 1–3, which
  carry the conclusion, are exact. *(An earlier draft labelled it "not in the
  trust path" while the ok-chain consumed it anyway; the label now matches the
  wiring.)*
- **Round-2 inheritance**: irreducibility of `G1` over `C(t)` comes from
  [`../../atlas/jc-crater/geometric_degree.py`](../../atlas/jc-crater/geometric_degree.py)
  (specialization + Gauss's lemma; the Gauss step itself is left to the reader
  there).
- **No peer review**, of the root claim or of this directory.

Context for result 1: this is Jelonek's leading-coefficient method
(Z. Jelonek, *The set of points at which a polynomial map is not proper*, Ann.
Polon. Math. **58** (1993) 259–266), but the proof here is self-contained
modulo the classical lemmas — the annihilators are certified as identities, not
imported from a CAS.

## Files

| file | what |
|---|---|
| `certify_nonproperness.py` | result 1 — the Jelonek set `S_F = V(E)`, plus `(I6)` non-surjectivity |
| `fiber_count_generic.py` | result 2 — `#F⁻¹(t) = 3` off `{t1t2Q = 0}` |
| `galois_group_s3.py` | result 3 — Galois type `S3` |
| `fiber_anchors.py` | result 4 — stratified anchor counts 3 / 1 / 0 |
| `cusp_curve_empty.py` | result 5 — the omitted rational curve |
| `degree_floor_check.py` | result 6 — outside the proven dim-3 islands |
| `run_all.sh` | replays all six |
| `findings_nonproperness.md` | full round-3 write-up behind result 1 |
| `findings_fibers.md` | full round-3 write-up behind results 2–5 |

Round-3 working names, for anyone diffing against the scratchpad:
`findings_nonproperness.md` and `findings_fibers.md` were both `findings.md`
(in `nonproperness/` and `fibers/`), and `degree_floor_check.py` was
`lit-degree/consistency_check.py`.

**Deliberately not shipped:** the sympy `discover*.py` scripts that *found*
these objects. They are discovery, not trust path — everything they found that
survives is re-proved from scratch by the certificates above, and nothing here
cites them.

## Downstream

The bounded quantities these certificates mint are recorded in
[`../../atlas/jc-crater/quantities.json`](../../atlas/jc-crater/quantities.json)
(`jc-nonproperness-degree`, `jc-image-complement-dimension`,
`jc-fiber-count-spectrum-size`, `jc-generic-escape-count`), with computed
confidence classes and `evidence[]` pointing back at these files.
