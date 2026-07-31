> **ERRATUM 2026-07-30 (appended before publication; lane original untouched).**
> (1) Statement numbering: the `egin{definition}` at TeX 297 consumes counter
> 4.1, so `prop-it` = **Proposition 4.2**, `AP` = **Theorem 4.9**, `Chang` =
> **Lemma 4.10** (identical in all three arXiv versions). References below to
> "Prop 4.1 / Thm 4.8 / Lemma 4.9" are off by one; mathematics unaffected.
> (2) The "B^1..B^7 are dilates of B" premise is literally false — there is
> exactly one non-dilate hop, the deterministic A-independent automorphism
> 2*B^2 (frequency set 2^{-1}Lambda); the no-directional-freedom conclusion
> survives verbatim (lane research_erdos142_direction_hinge_20260730).
> (3) The Lemma-4.9(=4.10) nesting flag is CLOSED (proved from the paper's own
> printed statement). (4) Open Lemma A as literally stated is REFUTED in the
> F_3 model (G1: J*(D+1) <= n = Theta(L) by Ellenberg-Gijswijt), and the model
> is PROVABLY unable to decide the Z/N residue (wrong dimension budget; no
> shadow of radius-shrink increments) — lane research_erdos142_final_form_20260730.

# WALL A — THE FENCE COMPLEX

### Erdős 142 / Wall A · consolidation of the 2026-07-30 campaign
### The definitive, self-contained record for the next attacker

```
erdos142_solved: false
new_r3_bound:    false
cracked:         false
date:            2026-07-30 (late)
primary source:  E:/arena/tmp/raghavan2603_source/main__2_.tex
                 sha256 b31eb727fd30ac6194184e4462ea1f73f0ce74e18a2a31abe101fa26b814d6bc
                 (re-verified at write time of this document)
authorship:      arXiv:2603.27045v3, *Improved Bounds for 3-Progressions*, and ALL
                 mathematics audited here, remain R. Raghavan's.  Schoen's and
                 Schoen–Sisask's results remain theirs.  This campaign claims only
                 the audit, the fences, the constructions, and the ledgers.
```

**Read this first.** Nothing in this campaign improves any exponent. Its output is
*negative and navigational*: a fully verified `1/6` baseline, a refined ledger that
names the only live quantity, and a complex of fences that tells you which attacks are
already dead so you do not re-walk them. If you are about to attack the `log 2K` factor
of Raghavan's `L⁴` chamber, §3 is the list of ways that has already failed and §4 is the
only thing left standing there. If you want the highest-value untouched target, skip to
**§5 — `𝔏(η)` and the `p = Θ(L)` Hölder cost**, which nobody attacked at all.

---

## 0. THE ONE-PAGE STATE OF THE WALL

| object | status |
|---|---|
| Raghavan's `1/6` exponent and every load-bearing step of it | **VERIFIED** (audit + Lemma A.7 closed) |
| `log N = O(L⁶ log L)` ambient ledger | **VERIFIED** (recomputed from the recursions, no hidden power) |
| the `L⁴` = `log 2K · 𝔏(η)` autopsy, both factors `Θ(L²)` from one exponent `θ` | **PROVED** (given the chamber) |
| S-ledger `d_J = O(L²)·S`, `S = Σ_j log 2K_j`, `log N = O(L³ log L · S)` | **UPPER PROVED / LOWER MEASURED** |
| every attack on `log 2K` | **dead, redundant, or reduced to the spike question** |
| the spike question (two named open lemmas) | **OPEN — the honest residue** |
| `𝔏(η)`, the other `Θ(L²)` | **NEVER ATTACKED** |

Four lanes, all under `E:/arena/`:

```
  research_erdos142_chamber_audit_20260730/     CHAMBER_MAP.md            (the audit + L⁴ autopsy)
  research_erdos142_sifted_doubling_20260730/   R2_narrowdensity_VERDICT.md  (Lemma A.7 CLOSED)
                                                R1B_SIFTED_DOUBLING_RECORD.md (shift law fenced)
                                                R1C_sifted_doubling_VERDICT.md (measurement + R1C-1)
  research_erdos142_dichotomy_r1ca_20260730/    R1D_CORRIDOR_LEDGER_RECORD.md (corridor + a-ledger)
                                                R1CX_DICHOTOMY_R1CA_RECORD.md (R1C-A refuted, sharp)
                                                R1CA_DICHOTOMY_VERDICT.md     (ff counterexample family)
  research_erdos142_bound_a_20260730/           R2A_BOUND_A_VERDICT.md    (S-ledger; corridor redundant)
                                                R1E_RANK_RELAXED_DICHOTOMY_RECORD.md (T1–T4)
                                                DA_LINE3_DEVILS_ADVOCATE_VERDICT.md  (DA-1..DA-5)
                                                judge_r2a.log             (the adversarial judge)
```

**§7 of this document is a transcription-drift register.** Nine claims in the lane
records are stale, overstated, or contradicted by their own code or by the lane judges.
Every one is listed with the correction. *Do not quote a lane record without checking §7
first* — that is exactly how false lemmas propagate through a consolidation.

---

## 1. THE VERIFIED `1/6` BASELINE AND ITS EXACT PARAMETER LEDGER

### 1.1 Verdict on the chamber

> **THE CHAMBER IS SOUND.** Every load-bearing step from Lemma 4.5 through
> Proposition 4.1 is **VERIFIED** or **TYPO-REPAIRABLE** by a repair evident from the
> surrounding text that **changes no parameter**. There is **no GAP**. The `L⁶ log L`
> ambient ledger and the `1/6` exponent stand.
> *(`CHAMBER_MAP.md` §0; 22 scripts, >130 enumerated exact assertions, 0 unexplained
> failures.)*

The v1/v2/v3 mathematical body is byte-identical (whole v2→v3 diff = 3 hunks / 20 lines,
all before line 103). The lemma dependency graph is a machine-verified **DAG — no
circularity** (`SKEPTIC_depgraph.py`).

**The single UNCLEAR import of the audit was closed the same day.** `CHAMBER_MAP` §4.5
flagged Lemma A.7 (`narrowdensity`, TeX 705) as *"the single largest unverified
load-bearing dependency"* — stated with no proof, apparently strengthened. The
`R2_narrowdensity_VERDICT.md` lane **found the source and closed it**: A.7 is verbatim
**Schoen, arXiv:2310.09584, Lemma 12** with the numerical `1/20` promoted to a free `ε`
(`1−4·(1/20) = 8/10`, `1+2·(1/20) = 1.1` — every constant matches), a complete four-step
proof is given in that record, and it was machine-checked on **18 630 `(A,B′,B″)`
triples** across 23 Bohr configurations in exact arithmetic, plus a small-`ε` regime down
to `ε₀ = 4.996·10⁻⁴` and a 400-move adversarial hill-climb. **The audit's "strengthened
import" concern was unfounded: the common translate is Schoen's own conclusion.**

> With A.7 closed, **every load-bearing step of the `1/6` is verified.** What remains
> outside the audit's reach are two *imports whose proofs are not in this source*:
> Theorem 4.8 = [SS, Thm 5.1] and Lemma 4.9 = [SS, Prop 5.3] (Schoen–Sisask, *Forum
> Math. Sigma* **4** (2016)). Their **interfaces** were machine-verified exactly; their
> **proofs** were not. Also uncited-but-standard: Lemma A.1, Prop A.2.

### 1.2 The exact parameter ledger

Throughout `L := 𝔏(α) = log(2/α)`, defined (TeX 106) for `α ∈ (0,1]` only.

| quantity | exact value | TeX | status |
|---|---|---|---|
| `c` (global constant) | `1/(2¹³·100) = 1/819200` | 295 | **binding constraint is A.7**: needs `c ≤ 1/(100(2¹³−1)) = 1/819100`; margin `1.221·10⁻⁴` |
| `ε` (Thm 4.8) | `2⁻¹²` ⇒ `ε⁻² = 2²⁴ = 16777216` | 597 | **absolute — carries no `L`** |
| `k` (Thm 4.8) | `19` admissible at `ν = 2⁻¹⁸` ⇒ `k² = 361` | 621 | **absolute — and only because of Lemma 4.4(4)** |
| σ-chamber | `σ ∈ [1+2⁻¹², α⁻¹]` | 305 | Prop 4.1 output |
| A.7 branch (2) | `1+2ε = 1+2⁻¹²` at `ε = 2⁻¹³` | 582 | produces the σ-chamber's lower endpoint exactly |
| A.7 branch (1) | `1−4ε = 1−2⁻¹¹` | 582 | the **common** translate `y`; `α′ ≥ (1−2⁻¹¹)α` |
| Lemma 4.6 call sites | `ε=1/2 → p ≥ 3`; `ε=2⁻⁷ → p = 796`; `ε=2⁻¹⁰ → q = 9933` | 520/533/551 | all `O(1)` — **the sift contributes no power of `L`** |
| Hölder exponent | `p₀ = O(𝔏(γ))`, `γ ≥ (1−2⁻¹¹)α` | 367 | ★ **L-POWER #1: `p = O(L)`** |
| sift loop length | `σ ≥ 2^{J−1}` against `‖μ_A∘μ_A‖_∞ ≤ α⁻¹μ(B)⁻¹` ⇒ `J ≤ 1+log₂(1/α)` | 542/545 | ★ **L-POWER #3: `J = Θ(L)`** (cap exact in 120/120) |
| descendant density | `dens(A_i) ≥ α^{p+O(𝔏(α))} = α^θ`, `θ = Θ(L)` | 405/592 | `θ = max(p, J·c₀)` — **the single quantity behind both `L²`s** |
| doubling | `K = \|A₂+B⁷\|/\|A₂\| ≤ 2\|B⁶\|/\|A₂\| = α^{−Θ(L)}` | 597 | ★ **`log 2K = Θ(L²)`** |
| sparsity | `η = \|A₁\|/\|S\| ≥ \|A₁\|/(2\|B⁵\|) = α^{Θ(L)}` | 599 | ★ **`𝔏(η) = Θ(L²)`** |
| AP output | `log(1/dens X) = Θ(k²ε⁻²𝔏(η)log 2K) = Θ(L⁴)` | 600 | ratio `log(2K)·𝔏(η)/L⁴` varies by 1.14 over `α ∈ [10⁻²⁴,10⁻³]` — genuine `Θ` |
| Chang | `𝔏(ξ) = Θ(L⁴)`, `rank ≤ d+O(L⁴)`, `radius ≥ Ω(ρ/(d²L⁴))` | 607 | per increment |
| iteration | `∏ⱼσⱼ ≤ α⁻¹` ⇒ `J = O(L)`; `d_J ≤ J·O(L⁴) = O(L⁵)` | 314/320 | ★ **L-POWER #8** |
| radius | `log(1/ρ_J) = Σⱼ O(log σⱼ)·log(2dL/c) = O(L log L)` | 320 | and `= Ω(L log L)` — see FENCE 9 |
| ambient | `log 1/(μ(B′)μ(B″)) = O(d_J log(1/ρ_J)) = O(L⁶ log L)` | 324/325 | ⇒ `L = Θ((log N/loglog N)^{1/6})` |

**Ledger stress test (no hidden power).** The three rows `d_J = O(L⁵)`,
`log(1/ρ_J) = O(L log L)`, `log 1/(μ(B′)μ(B″)) = O(L⁶ log L)` were recomputed directly
from the recursions at TeX 314–316 over four σ-families while `L` grew ×49: **maximum
upward drift of any normalised ratio 1.215.** A hidden extra power of `L` would have
produced drift ≥ 49. Independently reproduced in the corridor lane (drift 1.167 over
`L ×8`).

### 1.3 The `L⁴` autopsy — where the four powers actually are

```
   L⁴  =  log(2K) · 𝔏(η)  =  [θ·log(1/α)] · [θ·log(1/α)]      θ = Θ(L), log(1/α) = Θ(L)

   θ = Θ(L) = max(  p = O(𝔏(γ))          [Lem 4.3 line 367 — Hölder lifting]
                 ,  J·c₀ , J = Θ(L)      [Lem 4.4 lines 542+545 — the sift loop]  )
```

**Both `Θ(L²)` factors are the same `θ`, entering twice.** `ε⁻²` and `k²` are absolute
constants; the Croot–Sisask *bootstrap* is not where the `L`s are. Shaving `L⁴ → L³`
gives ambient `O(L⁵ log L)` and **exponent `1/5`**; `L⁴ → L²` gives **`1/4`**.

**Two structural facts worth carrying:**

1. **Lemma 4.4 conclusion (4) is worth two powers of `L`.** Without it, line 621 needs
   `k = Θ(L)` rather than `k = O(1)`, giving `k² = Θ(L²)`, `log(1/dens X) = Θ(L⁶)`,
   `d_J = O(L⁷)`, ambient `L⁸ log L`, **exponent `1/8`**. Any redesign that drops the
   self-energy balancing loses more than it gains.
2. **`|S| ≤ 2|B⁵|` is SHARP.** In `Z/401Z` with `B¹ = G`, `A′ = [0,40)`,
   `B⁵ = {|x| ≤ 20}`, the super-level set at `σ′ = 25664/5115 ≈ 5.017` **contains all of
   `B⁵`**, and `S` only grows as `σ′` falls to the `1+2⁻¹²` bottleneck. **No upper bound
   on the level set alone can shave `𝔏(η)`** — only descendant density can.

### 1.4 The defect register

**19 real printed defects** are on record: 18 in `CHAMBER_MAP` §4 (7 load-bearing, 7
real-but-not, 4 import/hypothesis mismatches) plus **D20** (ff section, from the
`bound_a` lane). *Every one is TYPO-REPAIRABLE with a repair that changes no parameter.*
The three you must not read past:

* **D1** (TeX 347/352/381/390): Lemma A.3's bound is **vacuous at the parameters used** —
  `200(ρ+δ)d = 200c+1 = 4097/4096 > 1` where the proof needs `≤ 2⁻⁷`. Repair: take
  `B⁰ = B_{1+c/d}`, giving `400c = 4.883·10⁻⁴ ≤ 2⁻⁷` and `1000c = 1.221·10⁻³ ≤ 2⁻⁸`.
  *(All four rationals re-verified in this consolidation.)*
* **D14/D15** (TeX 428/429): two real errors inside Lemma 4.5's proof computation —
  wrong orientation (`c₁−c₂` for `c₂−c₁`) and a dropped exponent `p`. Machine-demonstrated
  with 142/240 and 201/240 exact counterexamples; **the lemma's statement at line 419 is
  correct as printed** (240/240) and the two errors are self-cancelling.
* **D5** (TeX 547/557/607×2): `𝔏(σ)` applied outside its domain — `𝔏(σ) < 0` for `σ > 2`.
  Repair `J = O(log σ)`, which lines 305/406/593 already use.

**D20** (TeX 205, ff section): the codimension recursion for `V_j` is printed with
"**times**" where "**more than**" is required. Real typo; **but see §7 (F)**: the
contradiction the lane derived from it is backwards, and the judge supplied the correct
break.

---

## 2. THE S-LEDGER — THE ONLY LIVE QUANTITY, AND ITS PROOF-STATUS SPLIT

### 2.1 Statement

> ### THEOREM (S-ledger). *Upper bound: PROVED, given the paper's chamber.*
> Keep the paper's own bookkeeping **round by round** instead of worst-casing it
> (TeX 568 → 600 → 607 → 320). With
> ```
>            S  :=  Σ_{j ≤ J}  log 2K_j ,        K_j = |A₂+B⁷|/|A₂| at round j,
> ```
> and using `k = O(1)`, `ε = 2⁻¹²` absolute (Lemma 4.4(4)) and `𝔏(η_j) = Θ(L²)`:
> ```
>     rank increment at round j  =  O( k²ε⁻²·𝔏(η_j)·log 2K_j )                [TeX 607]
>     ───────────────────────────────────────────────────────────────────────
>     d_J          =  O(L²) · S
>     log(1/ρ_J)   =  O(L log L)                                              [TeX 320]
>     log N        =  O( L³ log L · S )                                       [TeX 324]
>     ───────────────────────────────────────────────────────────────────────
>     S = Θ(L³)        →  L⁶ log L  →  exponent 1/6      (the paper)
>     S = O(L^{3−t})   →                exponent 1/(6−t)
>     S = O(L²)        →  L⁵ log L  →  exponent 1/5
> ```

### 2.2 The proof-status split — state it every time

| half | status |
|---|---|
| **`log N = O(L³ log L · S)`** — the ledger as an **upper** bound | **PROVED**, given the paper's chamber (and hence inheriting the two SS imports) |
| **`S = Ω(L³)`** — that the paper's `S` really is that large | **MEASURED ONLY.** The word `Θ` was explicitly **withdrawn**. |

The lower half rests on Line C's measurement that `K` saturates the crude bound
(`log K_meas = m·log(1/α) + O(1)`, slope/L `= 1.00 ± 0.02`) at `N ≤ 200 003`, `m ≤ 8`,
`α ≥ 0.08`, rank ≤ 2 — extrapolated to `m = Θ(L)`, `ν = exp(−Θ(L⁴ log L))`,
rank `d = O(L⁴)`. **That extrapolation was refuted as a proof by the lane judge and must
be carried as a measurement.** Only `K_j ≤ 2|B⁶|/|A₂|` is proved.

### 2.3 Why `S` and not `a`

The earlier corridor lane reduced Wall A to an integer `a` := the number of rounds
exiting through Theorem AP + Chang, with `log N = O((1 + a·L⁴)·L log L)`. That reduction
is **true and proved**, and it is **superseded**:

* `S` is the quantity the ledger actually contains; `a` is a coarse two-value proxy for
  it. The two agree within a factor **1.9984** for every `a ∈ [1,L]`.
* The corridor that `a` was defined on is **redundant** (FENCE 6, §3).
* `S` needs no corridor, no branch test and no case split.

> **Carry `S`. Retire `a`.** Every statement anyone wanted to make about `a` is a weaker
> statement about `S`.

### 2.4 The `a`-boundary conditions, for orientation only

`a = Θ(L)` → `1/6` (the paper, bitwise, no regression — verified by running the TeX
314–316 recursions directly). `a = O(1)` → `1/5`, consistent with Behrend at every scale
tested (`log N` to `10⁸⁰`). `a = 0` → `log N = O(L log L)`, i.e. `√(log N) ≤ C loglog N`,
**refuted by Behrend** for `log N ≥ 10⁶`. So **branch (a) must fire**, and the corridor
is live only in `1 ≤ a ≤ J`.

---

## 3. THE FENCE COMPLEX

Nine fences. Each is given as: **exact statement · where it is proved · what it kills.**

---

### FENCE 1 — ABSOLUTE-CONSTANT SHADOWS ARE IDENTICALLY SILENT AT THE BOTTLENECK

**Statement.** Lemma 4.4(1) delivers, exactly (machine-verified on 18 170 `(instance,σ,x)`
triples, 0 mismatches), with `h_A(x) := |A ∩ (A+x)|/|A|`:

```
      μ_A∘μ_A(x) ≥ (1−2⁻¹⁰)·σ·μ(B)⁻¹      ⟺      h_A(x) ≥ (1−2⁻¹⁰)·σ·α .
```

A shadow inequality activating at `h_A(d) > 1/3` therefore fires iff
`σ > (1024/3069)·α⁻¹ = 0.333659…·α⁻¹` (exact rational, re-verified here). Against the
chamber `σ ∈ [1+2⁻¹², α⁻¹]`:

1. the activation window has **fixed absolute length** `log(3(1−2⁻¹⁰)) = 1.097635…` in
   `log σ`, while the chamber has length `≈ log(1/α) = Θ(L)`; the reachable fraction is
   `Θ(1/L)` (0.4767 at `α=10⁻¹` falling to 0.0099 at `α=10⁻⁴⁸`);
2. **and the reachable sliver is exactly the branch that is already cheap**: if every
   `σⱼ` were shadow-reachable then `∏ⱼσⱼ ≤ α⁻¹` forces **`J = 1`** (max admissible `J` =
   1.911 at `α=10⁻¹`, 1.020 at `α=10⁻²⁴`), whence `d_J = O(L⁴)`, ambient `O(L⁵ log L)` —
   **exponent `1/5` already, with no shadow at all.**

**Where proved.** `CHAMBER_MAP.md` §3.3; `CHAMBERMAP_L4_autopsy_checks.py` checks C1–C3
(16 passed, 0 failed).

**What it kills.** *Every* shadow/activation inequality with an **absolute** activation
constant, not just `1/3`. Widening `1/3` to any other constant `c > 0` moves the window's
endpoint but not its `Θ(1/L)` fraction, because the obstruction is that the activation
level is a constant while the delivered level is `Θ(α)`. **A usable variant must activate
at level `Θ(σα)` with `σ = 1+2⁻¹²` — i.e. at popularity `Θ(α)`, threshold tending to 0
with the density.** An `α^{o(1)}` threshold would suffice; an absolute one provably would
not.

---

### FENCE 2 — THE SHIFT LAW CANNOT BUY DOUBLING CONTROL

**Statement (four proved parts).** With `A_i(s) = C_i ∩ (A+s₁) ∩ … ∩ (A+s_p)`,
`P(s) = α₁(s)α₂(s)/D` the size-biased law of Lemma 4.5, `T = B⁷`, `K(s) = |A₂(s)+T|/|A₂(s)|`:

* **R1B-1 (the marginal shift law, PROVED).** For every `k` and every `F : G^k → Q`,
  `Σ_{s∈G^p} Σ_x F(x)Π_j 1_{A₂(s)}(x_j) = Σ_{x∈C₂^k} F(x)·|∩_j (x_j−A)|^p`.
  Consequence: `P`'s moment algebra is **exactly** the `k`-point correlations — the
  factorisation over `i = 1..p` exists iff the integrand is a product of functions of the
  individual `s_i`, i.e. exactly the monomial case, and nothing else.
* **R1B-2 (PROVED).** `|A₂+T|` enters only by inclusion–exclusion, as a `2^{|B⁷|}`-term
  alternating sum: it is an `L⁰` (support) functional and `1[f>0] ≤ f^θ` needs a
  **fractional** moment, while the shift law produces only integer moments. Every
  classical bridge runs the wrong way (`|A₂+T| ≥ (|A₂||T|)²/E(A₂,T)`: small energy ⇒
  **large** sumset).
* **R1B-3 (PROVED).** The size-biasing is **neutral for sumsets**: the `α₁α₂` weight
  cancels completely and the only closed form the law offers for the doubling ratio is the
  **uniform-`s`** average. `P` gives no preference whatsoever to small-sumset shifts.
* **R1B-5 (PROVED, and this is the fence).** `K` *is* `P`-cheap as a fourth Markov
  functional at constant budget (`E_P[K] = (D|G|²)⁻¹ Σ_s |A₁(s)|·|A₂(s)+T|`, exact), but
  its entire content is one scalar:
  ```
       GAIN  =  E_P[K] / (free bound)  =  E_P[α₂⁻¹·cov] / E_P[α₂⁻¹]  ≤ 1 ,
  ```
  the `α₂⁻¹`-weighted **mean coverage**. Measured exactly on 60 instances:
  **min 0.2125, median 0.6360, max 0.9321.** To shave `log 2K` from `Θ(L²)` to `Θ(L)` one
  needs `GAIN = α^{Θ(L)} = exp(−Θ(L²))`. **`Θ(1)` is not `exp(−Θ(L²))`.**

Plus three blindness fences: **automorphism** (Aut-equivariant functionals of
`(A,C₁,C₂)` cannot see `|A₂+T|`; 12/12), **correlation** (in `Z/d²`, `K = 1000` vs `K = 1`
with `k=4` correlations agreeing to relative `0.0040` and `E(A₂)/|A₂|³ ≥ 0.99701`), and
**weight** (explicit `s ≠ s′` with identical `(α₁,α₂)` and `|A₂+T|` differing by 3/2, in
120/200 instances). **Oracle bound:** even unrestricted selection over `supp P` gains
`max 1/cov ≤ 3.5`; small-doubling `s` **do not exist**, so the obstruction is not the
Markov budget.

**Where proved.** `R1B_SIFTED_DOUBLING_RECORD.md`; `R1B_shiftlaw_doubling_exact.py`
(280 checks, 0 failures) and `R1B_doubling_fences_exact.py` (235 checks).

**What it kills.** Any hope that the sift's own measure supplies the structural input.
**The escape hatch is named exactly:** the crude bound can be beaten only through the
`q`-fold autocorrelation excess of `A′` along `B⁷`-differences — *structure in `A`, never
the shift law.* Worse, the sift law **actively selects against you**: in the `Z/NZ`
counterexample family the `P`-aligned share of the total weight is
`0.143, 0.327, 0.627, 0.839, 0.971, 0.994, 0.9997` at `p = 1,2,3,4,6,8,12` — a
`P`-typical `s` is precisely a *concentrating* shift vector.

---

### FENCE 3 — SPREADNESS IS MONOTONE THE WRONG WAY, AND HAS THE WRONG SIGN

**Statement (two independent halves).**

*(a) Monotonicity.* The standard Croot–Sisask pigeonhole gives
`|X| ≥ ½ K^{−m}|S|` with `m = O(k²ε⁻²𝔏(η))` — a **strictly decreasing** function of
`|A+S|`. Branch (a) of any dichotomy asserts `|A₂+B⁷| ≥ c|B⁶|`, and the trivial ceiling
is `|B⁶+B⁷| ≤ 2|B⁶|`; so in branch (a), `log 2K = 𝔏(α₂) + log(2/c) = Θ(L²)` **exactly**,
and the paper's line-597 bound is tight up to `log(2/c) = O(1)` (whose effect,
`exp(O(L²))`, is lower order against `exp(−O(L⁴))`). Spreadness is the *enemy* of the CS
pigeonhole: the argument is cheap for **clustered** `A`, and branch (a) is precisely the
statement that `A₂` is as un-clustered as the ceiling allows.

*(b) Sign.* Branch (a) constrains only the **support** of `g(x) = |A₂ ∩ (x+B⁷)|` — an
`L⁰`-type quantity — while every 3AP count needs an `L²`/`L³`-type quantity. Explicit
witness: `A₂ = (random half) ∪ (one full B⁷-cell)` has maximal support with half its mass
in one cell. **Spreadness gives no variance control at all.** And 3AP-freeness supplies no
tension: **Behrend's construction — the only known extremal 3AP-free family — is
simultaneously 3AP-free and near-maximally spread at every scale** (exact Behrend spheres
in `Z/p`, `p ∈ {1009, 4001, 10007}`, brute-force 3AP-free, with `|A+[0,w)|` at **0.37–1.00**
of the trivial ceiling `w|A|` at `w ∈ {2,8,32,128}` in the lane's run C12, and **0.2578–1.0000**
in the judge's **independent** reconstruction, J8a/J8b).

*(c) The one non-monotone surrogate saturates too.* Redo the pigeonhole entropically:
with `Δ := H(a+s) − log|A₂|`, `H(s|V) ≥ log|S| − mΔ`, and `Δ` can be far below `log K` —
formally. But if `A₂` is equidistributed at scale `B⁷`, which is exactly what the sift was
measured to produce, then `Δ ≈ 𝔏(α₂) = Θ(L²)`, the crude value
(`Δ/log(1/dens) ∈ [0.963, 0.996]` for uniform random `Y`). Falls out for free:

> **THEOREM R1D-1 (entropic R1C-1) — PROVED.** `H = −H` symmetric, `Y` finite,
> `a ~ Unif(Y)`, `s ~ Unif(H)` independent, `Δ = H(a+s) − log|Y|`. Then
> `max_x |Y ∩ (x+H)| ≥ |H|·e^{−Δ}` and `Δ ≤ log K`.

**Where proved.** `R1D_CORRIDOR_LEDGER_RECORD.md` §5 (FENCE R1D-5, checks C3/C9);
`R2A_BOUND_A_VERDICT.md` §4.2 (FENCE R2-5, check C12); `judge_r2a.log` J8.

**What it kills.** (i) The supersaturation/removal route — "`Θ(L)` consecutive spread
certificates force a 3AP". (ii) Any attempt to make spreadness of `A₂` feed either `L²`
factor. (iii) The "almost-AP" variant is **not new information — it is the machine**: it
is precisely the level set `S` and the pairing `⟨μ_A∘μ_A, μ_{A₁}∘μ_{A₂}⟩` the chamber
already forms, and its output is a density increment, not a contradiction.

*The surviving crack, named:* a Croot–Sisask theorem with exponent
`O(k²ε⁻²𝔏(η)·log L·Δ)` in the **entropic** doubling excess, together with a proof that
the sift produces `A₂` with `Δ = o(L²/log L)`. Branch (a) obstructs neither half and
supplies neither. Unchecked against the literature.

---

### FENCE 4 — THE SUPERSATURATION DENSITY BUDGET IS SHORT BY A FULL POWER, AND CIRCULAR

**Statement.** Any counting theorem forcing a 3AP inside `A₂` (legitimate, since
`A₂ ⊂ A′+s₁`, so a 3AP in `A₂` is a 3AP in `A`) needs `|A₂| > r₃(N)`:

```
   allowed  :  log( N / r₃(N) )  =  O(L)        [the paper's own theorem]
   delivered:  log( N / |A₂| )   =  Θ(L²)       [dens(A₂) = α^{Θ(L)}, TeX 405/592]
```

The deficit is exactly one power of `L`, and it is **already fatal at round `j = 1`,
before any Bohr localisation is charged**. Closing it means `θ = O(1)` — but `θ = O(1)`
collapses **both** `L²` factors to `L`, giving `d_J = O(L³)`, ambient `O(L⁴ log L)`,
**exponent `1/4` with no 3AP counting at all.**

**Where proved.** `R2A_BOUND_A_VERDICT.md` §4.1 (FENCE R2-4, checks C9a–C9d).

**What it kills.** The supersaturation route requires as an *input* something strictly
stronger than the improvement it would *output*. **Circular, and dominated.**

---

### FENCE 5 — THE NAIVE CORRIDOR REGRESSES TO EXPONENT `1/7`; THE σ′-GATE IS A STANDING RULE

**Statement.** The `1/6`-preserving restructuring of Prop 4.1 is: test
`K ≤ K_* := ((1−2⁻⁸)σ′α′)⁻¹` first; if so, Theorem R1C-1 delivers a translate with
`σ = (1−2⁻⁸)(1−2⁻¹¹)σ′` on `B⁷` at **rank exactly `d`**, regular, radius
`(c/2d)^{O(log σ′)+5}ρ`, **with no Theorem AP and no Chang** (R1D-2, PROVED). This is
regression-free *precisely because branch (b) delivers the paper's own `σ`*:
`(1−2⁻⁸)(1−2⁻¹¹)(1+2⁻⁷) = 67336065/67108864 ≥ 1025/1024` (exact; re-verified here), the
identical expression the paper reaches at TeX 628.

The **naive** version — branch (b) delivering only the constant `1+2⁻¹⁰` — **regresses**:
Lemma 4.4 has already charged `(c/2d)^{O(log σ′_j)}` with `σ′_j` up to `1/α′`, and bullet
(3) is indexed by the *delivered* `σ_j`, so it cannot absorb it. Costing the worst-case
schedule gives ambient `Θ(L⁷ log L)` — **exponent `1/7`, a regression from `1/6`.**
Gating the branch by `σ′ ≤ σ_max` (absolute) repairs it, reproducing `Θ(L⁵ log L)` at
`a = 1` with drift 1.121.

**Where proved.** `R1D_CORRIDOR_LEDGER_RECORD.md` §1, §4; `R1D_corridor_ledger.py` checks
C4, C5, C8 (21 passed, 0 failed).

**What it kills.** Not an attack but a **design rule**, and it should be quoted at anyone
proposing a dichotomy:

> **STANDING RULE.** Any proposed cheap branch must deliver `σ ≍ σ′`, because the sift's
> radius bill is drawn **before** the branch is known. Two of the three obvious dichotomy
> designs fail this test.

*Bookkeeping note that generalises:* the corridor is **not the first free exit — it is the
third**. Lemma A.7 case (2) (TeX 582, `σ = 1+2⁻¹²`, rank increment **0**) and Lemma 4.3
case (2) (TeX 586, `σ = 2(1−2⁻¹¹)`, rank increment **0**) already exist, and the paper's
bullet (2) over-charges both at `C L⁴`. **Making bullet (2) branch-dependent is free and
already available.**

---

### FENCE 6 — THE CORRIDOR IS REDUNDANT: BOUNDING `a` CANNOT PAY

**Statement (THEOREM R2-3).** Branch (b) fires at round `j` only if
`log 2K_j = O(L)` — indeed only if `log 2K_j ≤ 𝔏(α′_j) + O(1)`. But at exactly such
rounds the **paper's own round-by-round ledger already charges only**

```
     rank increment  =  O(k²ε⁻²·𝔏(η_j)·log 2K_j)  =  O(L²·L)  =  O(L³) ,
```

with no corridor, no branch test and no Theorem R1C-1. Hence

```
     d_J (no corridor)  =  a·O(L⁴) + (J−a)·O(L³)  =  O((a+1)·L⁴)
     d_J (corridor)     =  a·O(L⁴)                =  O(a·L⁴)
```

— **identical for every `a ≥ 1`** (ratio ∈ [1.0000, 1.9984], independently reproduced by
the judge, J3a). And `a = 0` is refuted by Behrend. **So the corridor changes the exponent
in no regime that is not already refuted, and `a = o(L)` is strictly subsumed by the
doubling estimate it was meant to serve.**

The magnitude of the gap that "bound `a`" would have to close (exact rationals in `α`, at
`σ′ = 1+2⁻¹²`): `log 2K / log 2K* = 39.9, 79.7, 159.5` at `α = 10⁻¹²,10⁻²⁴,10⁻⁴⁸`, i.e.
ratio/`L` = 1.408, 1.425, 1.434 — **`Θ(L)`, never better than one full power**; and
`Θ(L²)` at `σ′ = 1/α′` (judge-reproduced independently, J7a/J7b).

**Where proved.** `R2A_BOUND_A_VERDICT.md` §3 (checks C7a/C7b/C8); `judge_r2a.log` J3, J7.

**What it kills.** The entire "bound `a`" programme, *including* the version where you
succeed. **Two caveats you must carry** (both from the judge, §7 C and D): the printed
`iff` is not a biconditional (only branch(b) ⇒ `log 2K = O(L)`), and the ledger comparison
substitutes the always-AP run's cheap rounds for the corridor run's, which is licensed
only if the `a`-bound is round-local and uniform over admissible states. **Record R2-3 as
"redundancy proved modulo a uniformity hypothesis", not unconditionally.**

*Alignment note, so two fences are not confused:* `K_* = ((1−2⁻⁸)σ′α′)⁻¹` is strictly
decreasing in `σ′`, so the corridor's cheap branch is **widest exactly at the
`σ′ ≈ 1+2⁻¹²` bottleneck that produces the `1/6`** — the *opposite* alignment to the
absolute shadow of FENCE 1, which fires only in the top-`σ` sliver that is already `1/5`.
**The corridor's design is not misaligned; only its magnitude gap is fatal.**

---

### FENCE 7 — THEOREM R1C-1 IS EXACTLY OPTIMAL: THE DICHOTOMY THRESHOLD CANNOT BE RAISED

**The free floor.**

> **THEOREM R1C-1 (PROVED).** `H = −H` finite symmetric, `Y` finite in an abelian group,
> `|Y+H| ≤ K|Y|`. Then `max_x |Y ∩ (x+H)| ≥ |H|/K`.
> *Proof.* `Σ_x |Y ∩ (x+H)| = |Y||H|`, and the summand vanishes unless `x ∈ Y−H = Y+H`,
> a set of size `≤ K|Y|`. Average. ∎

At the call site (`A₂ ⊂ A′+s₁` by Lemma 4.5, `B⁷` symmetric) this gives the sharp
dichotomy: **either** `log 2K ≥ L − O(1)`, **or** `A′` has relative density
`≥ (1+2⁻¹⁰)α′` on a translate of `B⁷` — a density increment at rank `d`, radius
`(c/d)^{O(L)}ρ`, with **no Theorem AP and no Chang**.

**Statement of the fence (sharpness, two independent constructions).** The threshold
`1/((1+2⁻¹⁰)α′)` **cannot be raised by any argument using only call-site data**:

* **`Z/NZ` (`R1CX`):** an exact family with
  `K = (2h−D)/h′ = 2/α′ − α′^{−1}/h′`, i.e. `K·α′ = 2 − 1/h′`, sweeping the **entire**
  interval `[1/α′, 2/α′)`; at `h′ = 1` it sits **exactly on** the R1C-1 floor
  (`K·α′ = 1.000000`, brute-force verified), and `¬(b)` (which forces `h′ ≥ 1024`) pushes
  it to `K·α′ = 2 − 2⁻¹⁰`. Both endpoints are attained by configurations satisfying every
  call-site hypothesis: the Lemma-4.5 output shape, conclusions (1), (2), (4), a legal
  `σ′` (1.223417), and covering `≥ 100`.
* **`F₃ⁿ` (`R1CA`):** a **genuinely 3AP-free** family (anisotropic quadratic form
  `f(q)_r = q²_{2r−1}+q²_{2r}`, cap `C`) with `K = 1/α′` **exactly** and
  `max_x|A′∩(x+B⁷)|/|B⁷| = α′` **exactly** — the floor attained with equality, and branch
  (b) failing for **every** `ε > 0`, not merely `2⁻¹⁰`.

**Two routes proved dead in passing:**

* **R1CX-2 (multi-translate amplification, NO-GO with attainment).** `A₂` sits in `q+1`
  translates of `A′` simultaneously, but the only bound on the local density that follows
  from `¬(b)` is `min_i max_x |A′∩(x−s_i+B⁷)|/|B⁷| ≤ (1+2⁻¹⁰)α′`, **independently of `p`**,
  and this is attained with equality for every `p ≥ 1` (local density / `α′` = 1.000000 at
  `p = 1,2,3,4,5` while `α₂` falls by `β^p`). Amplifying would require a **local inverse
  theorem at the bottom scale** of the architecture.
* **R1CX-3 (energy route, DOMINATED).** Conclusion (4) plus small doubling yields only
  `K ≥ 2⁻⁴(σ′)^{−1/2}(α′)^{−1}√(|B⁸|/|B¹|)`, weaker than the R1C-1 floor by
  `exp(−Ω(d log(d/c)))` with `d = O(L⁴)`. Root cause: (4) reaches `A₂` only through
  `r_{A′}`, which lives at the `B¹` scale while the question lives at `B⁶/B⁷` — and (4) is
  **tight at the typical value** (the counterexample satisfies it with constant ~1 in
  place of `2⁸`: 40.41 and 255.39 against the allowance 313.19).

**Where proved.** `R1CX_DICHOTOMY_R1CA_RECORD.md` §§2–4, §8;
`R1CA_DICHOTOMY_VERDICT.md` §§2–5.

**What it kills.** CONJECTURE R1C-A's `Θ(L)`-power strengthening — *not merely unproved,
but unprovable from call-site data*. **And it leaves a genuine hole:** configurations with
`K ∈ [1/α′, 2/α′]` fire **neither** branch, and the constructions populate it. Any future
dichotomy must either widen branch (b)'s threshold below `(1+2⁻¹⁰)α′` — which conflicts
with what a density increment *means* — or accept the hole.

**Two scope limits you must carry** (they are the reason this is a fence and not a
theorem): the `Z/NZ` family's `A′` is **not 3AP-free** (its normalised 3AP count satisfies
`T ≥ 1` intrinsically, so `liftunbalance` case (1) discharges it before the sift), and the
`F₃` family is in the **subgroup model**, not `Z/N` Bohr. The `F₃` family closes the first
gap and the `Z/NZ` family closes the second; **neither closes both, and no `Z/N`
counterexample was built by anyone.** Additionally, see §7 (B): the `F₃` family's published
scaling table does **not** verify conclusion (4), and once (4) is imposed the family
refutes R1C-A only for constant pairs `C` below an absolute multiple of `c`.

**One consequence that matters for how you read FENCE 3.** Because legal configurations
with `log 2K = L + O(1)` exist, **`log 2K = Θ(L²)` is *not* forced by the call-site
structure.** Route (ii) of the autopsy ("a genuine doubling estimate for `A₂`") rests
*entirely* on the measurement that **spread** `A` saturates the crude bound, together with
the LEGAL-INPUT table showing spread `A` reaches the sift (random spread `A` is legal at
Hölder `p = 4`, and the paper's `p = O(L)`; the `bumped` family is legal at `p = 1`).
**The measurement is load-bearing; the conjectured proof of it does not exist and cannot
be built at the call site.**

---

### FENCE 8 — T3: THE RANK-`d+O(1)` LOCAL DICHOTOMY IS FALSE; T4: NESTED DESCENT CANNOT REACH

**Setting.** After R1C-A was refuted, the repaired conjecture R1C-A′ asked for the density
increment on a Bohr set of rank `d+O(1)` instead of `d` (the refuting families all show an
increment **one rank down**, by a factor exactly 3). The local question — one `B⁷`-slice of
`A′` — is settled in both directions.

* **THEOREM T1 (PROVED, exact, unconditional).** `U` finite abelian, `T ⊆ U`, `a = |T|`,
  `α = a/|U|`, `D = T−T`. Then
  `max_{γ≠1}|T̂(γ)|² ≥ a³(|U|/|D| − 1)/(|U| − a)`, **with equality exactly when `T` is a
  coset of a subgroup** (machine-checked slack `0.0000`).
* **COROLLARY T1′ (PROVED).** In `F₃^u`: if `|T−T| ≤ c|U|` with
  `c < c*(α,ε) := α/(α + ε²(1−α))`, then some coset of some **codimension-1** subgroup
  carries `T` at relative density `≥ (1+ε)α`. *(The gloss `c* ≈ α/ε² = 2²⁰α` is valid only
  for `α ≪ ε²`; see §7 (H).)*
* **THEOREM T2 (ATTAINMENT — T1 is sharp to the absolute factor 3).** `q = 3^k`,
  `U = F_q³`, `T_q = {(x,x²,x⁴)}`: a Sidon set (`|T_q−T_q| = q²−q+1` exactly), so
  `c ≤ 1/q`, with `max_{γ≠1}|T̂_q| ≤ 3√q` by Weil and `≥ (1−o(1))√q` by T1. Machine-exact
  at `q = 9, 27, 81`: `M = 3√q` on the nose, `M/(T1 floor) = 2.984, 2.998, 3.000`. `T_q` is
  also 3AP-free.
* **THEOREM T3 — THE FENCE.** For every `R ≥ 1` and `ε ∈ (0,1)`, take `q` with
  `3^{R+1}·3 < ε√q`. Then `T_q` has **no** `(1+ε)`-density increment on any coset of any
  subgroup of codimension `≤ R`, while `|T_q−T_q|/|U| ≤ 1/q → 0`. Since `R` may be taken
  `≍ ¼·log₃(1/α)`, **the least admissible rank excess is `Θ(log(1/α)) = Θ(L)`, not
  `O(1)`.**
* **PROPOSITION T4 (PROVED).** Any argument concluding branch (b′) by applying R1C-1 at
  the bottom of a nested chain `B⁷ = B₀ ⊇ … ⊇ B_r` (index 3 each step) needs
  `r ≥ log₃((1+ε)α′K)`, which in the hole is `r = Θ(L²)` in the worst case — against an
  `O(1)` radius budget (`ρ₇(c/d)^{O(1)}`). **The descent cannot reach the target; this is
  a counting fact, not a failure of effort.**

**Ledger consequence.** Both rank forms are **ledger-neutral for every `a ≥ 1`**:
`d+O(1)` and `d+O(log 1/α)` give the identical exponent (`1/5` at `a = O(1)`, `1/6` at
`a = Θ(L)`). They separate only at `a = 0`, which is refuted independently. **The rank of
the corridor is not the bottleneck; the corridor's entry condition is.**

**Where proved.** `R1E_RANK_RELAXED_DICHOTOMY_RECORD.md` §§3–8;
`R1E_local_dichotomy.py` (8 sections, zero occurrences of `False` in the log).

**What it kills.** Any proof of R1C-A′ **at rank `d+O(1)`** that factors through
`{the B⁷-slice profile of A′, the doubling |A₂+B⁷|, the covering hypothesis}` — the exact
data set both prior lanes used. Only the `d+O(log(1/α))` form survives, and the ledger
shows the relaxation buys nothing anyway.

**The gap in T1's transfer, stated exactly (this is the honest limit).** T1–T4 are
unconditional theorems about the **local** problem; the call-site statement is proved only
under the *slice-translation ansatz* `S_m = T + g(m)` (which the refuting families do
satisfy exactly). Without it, `¬(a)` says only that a `P`-fold intersection
`⋂_i(S_{n−v_i}+u_i)` is empty for most `n`, and emptiness of a `P`-fold intersection does
not imply pairwise disjointness. **A Fourier-only argument provably cannot bridge it:** if
every slice has `max_{χ≠1}|Ŝ_m(χ)| ≤ εα′|U|`, the best pair bound is
`α′²|U| − εα′|U|√(α′|U|)`, vacuous once `|U| ≫ α′/ε²` — and the covering hypothesis
*forces* `|U| ≥ C/α₂ = α^{−Ω(L)}`. The transfer needs an `L⁴`/energy input.

---

### FENCE 9 — THE RADIUS ROUTE IS CLOSED TOO: `log(1/ρ_J) = Ω(L log L)`

**Statement.** The ff↔`Z/N` gap is *exactly* the radius factor: both models pay `Θ(L⁴)`
per increment and run `J = Θ(L)` rounds, reaching total rank/codimension `Θ(L⁵ )`;
subspaces have no radius, Bohr sets do, so

```
   ambient(ff)  = d_J                = Θ(L⁵)        → exponent 1/5
   ambient(Z/N) = d_J · log(1/ρ_J)   = Θ(L⁶ log L)  → exponent 1/6
   ────────────────────────────────────────────────────────────────
   ratio = log(1/ρ_J) = Θ(L log L)
```

making exact the paper's own remark about "a loss of one logarithm". That makes "kill the
radius factor" the natural sibling of "bound `a`" — each worth one power. It is closed at
the level of bullet (3) as stated: from TeX 316,
`log(1/ρ_J) = C·Σ_j log σ_j·log(2d_{j−1}𝔏(α)/c)`, and in the regime that produces the
`1/6` (`σ_j = 1+2⁻¹²` for `Θ(L)` rounds) the σ-budget is fully spent, so
`Σ_j log σ_j = Θ(L)`, and even at the smallest legal rank `d_{j−1} ≥ 1` the second factor
is `log(2L/c) = Ω(log L)`. Hence

> **`log(1/ρ_J) = Ω(L log L)` with no assumption on `d_J` whatsoever.**

**Also settled here: the finite-field model does *not* avoid the doubling input.** It pays
`K = |A+G|/|A| = 1/μ(A)` **exactly** — the identical crude bound — so `log 2K = 𝔏(α₂)`
identically, and Raghavan's ff exponent `ε⁻²k²𝔏(α₁)𝔏(α₂)` **is** Theorem 4.8's
`k²ε⁻²𝔏(η)log 2K`. **`Z/N` is strictly finer, not wasteful:** `K = |A₂+B⁷|/|A₂| ≤ 2|B⁶|/|A₂|`
= the ff quantity. The refinement is the slack; the formulation is not. And the ff proof
of Prop `prop-ff-it` **has no branch at all** — every round runs Hölder → sift → ff-AP →
ff-Chang — so **in the ff model `a = J = Θ(L)` and the exponent is `1/5` anyway.** No
mechanism for bounding `a` can be extracted from ff; ff does not bound `a`, it *has*
`a = J`.

**Where proved.** `R2A_BOUND_A_VERDICT.md` §1, §6 (FENCE R2-1, R2-7, checks C1–C5, C13);
`judge_r2a.log` J9. *Note the correction in §7 (E) to the identification's first argument.*

**What it kills.** The radius/one-logarithm route as stated. Improving it means replacing
the radius law itself — Lemma A.7 territory, i.e. the paper's own radius-saving ingredient.
**Both one-power routes are fenced. The only live object in the ledger is `S`.**

**Testability floor, worth knowing before you run any experiment.** `|A₂+B⁷| ≤ |A₂||B⁷|`
gives unconditionally `K ≤ |B⁷|`, so **branch (b) fires automatically whenever
`|B⁷| ≤ K* ≈ 1/α′`**; the branch predicate is non-trivial only once
`|B⁷| > 1/α′ = exp(Θ(L))`. At any computable `Z/p` with a realistic `α′` you would need
`p ≥ 10¹⁷` *and* a proper sub-Bohr set inside it. **Every `Z/p` probe of the branch
predicate below that is an artefact** — including the ones reported in the lane records,
which say so themselves. At the paper's own parameters `α′|B⁷| ≥ exp(Ω(L⁴) − L)`.

---

### THE DEVIL'S CONSTRUCTIONS — DA-3 / DA-4, which is why the residue is what it is

Not a fence against a technique but a **counter-model** to the only remaining hope, and it
is the reason §4 is phrased as it is.

* **THEOREM DA-1 (PROVED, model-free — the pivot).** With `B⁷ = −B⁷`,
  `K ≥ |B⁷| / max_x|A′∩(x+B⁷)|`. Consequently if
  `max_x|A′∩(x+B⁷)| < (1−2⁻⁸)σ′α′|B⁷|` then `K > K_*`, branch (b) is unavailable, and the
  round **must** exit through AP + Chang. Since `σ′ ≥ 1+2⁻⁷` it suffices that
  `max_x|A′∩(x+B⁷)|/|B⁷| < (1−2⁻⁸)(1+2⁻⁷)α′ = (32895/32768)α′ = (1+2⁻⁸−2⁻¹⁵)α′` (exact;
  re-verified here). Hence
  ```
     a ≥ J − #{ j : A'_j carries a (1+2⁻⁸)-factor density spike on some B⁷_j-translate }
  ```
  > **"Bounding `a`" is exactly: certify a CONSTANT-FACTOR, rank-`d` density spike for the
  > sifted iterate, at the sift's own scale, at all but `o(L)` of the rounds.**
  Fourier/Meshulam delivers only a `1+Θ(α′)` spike at rank `d+1` — *exponentially* short of
  `1+2⁻⁸`. **That gap is precisely why Prop 4.1 reaches for Theorem AP + Chang and pays
  `O(k²L⁴)` rank.** DA-1 also closes the loop with the measurement: saturation of the crude
  bound **is** branch-(a) forcing; the measurement and the criterion are the same statement.

* **THEOREM DA-3 (PROVED) — the Fourier-extremal capset.** `K = F_{3^j}`, `−λ` a
  non-square, `f(x,y) = x²+λy²`, `Q_j := {(f(x,y),x,y)} ⊂ F₃^{3j}`, `|Q_j| = 3^{2j}`,
  `α = 3^{−j}`. Then `Q_j` is 3AP-free and `|1̂_{Q_j}(γ)| = α²` **exactly** at every
  nonzero frequency with `a ≠ 0` (and `0` otherwise) — **the theoretical floor**, since a
  3AP-free `A ⊂ F₃ⁿ` must have `max_{γ≠0}|1̂| ≥ α² − 3^{−n}`. Hence
  `|Q_j ∩ (x+W)| ≤ (1+(3^r−1)α)α|W|` for every codimension-`r` subgroup, and **`Q_j`
  admits NO branch-(b) exit at any `B⁷` of codimension `r ≤ j−6`, in any direction.** The
  flat range is `D = Θ(L)`.

* **THEOREM DA-4 (PROVED, in the model) — the devil's tower.** `T_J := Q_1^{⊗J}`, a capset
  of size `9^J = 2.08008ⁿ` (against the best known capset `≈ 2.2174ⁿ` and the
  Ellenberg–Gijswijt ceiling `2.7551ⁿ` — **near-extremal, not a toy**). It is exactly flat
  on every vertical subgroup, exactly self-similar (freezing a block multiplies the
  relative density by exactly 3 and leaves `T_{J−1}`), and therefore admits a **legal**
  Theorem-1.4 execution of length `J = log₃(1/α) = Θ(L)` with `σ_j ≡ 3` and
  `∏σ_j = 1/α` — **bullet (1) saturated with equality** — in which, by DA-1, **every single
  round is crude-tight: `a = J`.** Call-site fidelity audited: at `σ′ = 3` (inside
  `[1+2⁻⁷,(α′)⁻¹]`), condition (1) holds **with equality to 1**, (2) and (4) hold with
  large margins, and the branch test gives `K = 9 > K_* = 3.01` (`T₂`), `K = 27 > K_* = 9.04`
  (`T₃`).

* **A dead end recorded so it is not re-walked.** Ellenberg–Gijswijt applied to
  `A′∩(x+B⁷)` would force flatness whenever `dim B⁷ ≳ 11.74·𝔏(α′)` — **but this is
  vacuous**: EG applied to `A′` inside `B¹` already gives `dim B¹ ≥ 11.74·𝔏(α′)`, and
  `dim B⁷ ≤ dim B¹`. Real capsets miss it by a factor `≈ 3.57` in the dimension. **No
  unconditional forcing comes from capset bounds.**

**Scope, stated plainly.** DA-4 refutes *"`a = O(1)` for every 3AP-free `A` and every legal
chain"*, which is the statement an improvement needs. It does **not** refute *"the greedy
branch-(b)-first chain has `a = O(1)`"*: `T_J` is not flat in the `ψ`-directions
(codimension-1 spike exactly `4/3 > 32895/32768`), so an adversarially chosen `B⁷` would
find an exit. The source-read argument that the prover **cannot** choose the direction of
`B⁷` at the real call site (TeX 597: `B⁷ ⊂_{c/d} B⁶`, and `B¹…B⁷` are all dilates of `B`)
is what makes the tower decisive — and that argument is **source-read, not
machine-checked**.

---

## 4. THE TWO NAMED OPEN LEMMAS — THE HONEST RESIDUE

Everything in §3 reduces the `log 2K` attack to a single finite-field question with two
faces. **Both faces are worth a lane; they are the same lemma with opposite answers.**

### OPEN LEMMA A — the direction-free flat descent question

> Does there exist a capset `A ⊂ F₃ⁿ` of density `α` and a **legal descent of length
> `Θ(𝔏(α))`** such that at **every** round the current iterate has
> `spike(W) := max_x|A′∩(x+W)|/(α′|W|) < 1 + 2⁻⁸` for **every** subgroup `W` of
> codimension `≤ Θ(𝔏(α))`?

*Why it is exactly the residue.* The two devil's properties pull against each other and,
in the block family `Q_j^{⊗r} ⊂ F₃^{3jr}`, the trade-off is exact:

| quantity | value |
|---|---|
| direction-free flat codimension range | `D = j − 6` (DA-3) |
| canonical descent length | `J = r`, `σ ≡ 3^j` |
| budget | `L = jr·ln 3`, `∏σ_j = 1/α` with equality |
| **product** | **`D·J ≤ L/ln 3`** (verified at `(j,r) = (1,40),(7,6),(10,4),(20,2),(40,1)`) |

> `J = Θ(L)` forces `D = O(1)`; `D = Θ(L)` forces `J = O(1)`.

The mechanism is transparent: for a product set the characters supported on one block have
relative bias `1/(block size)`. **Self-similarity under the descent wants small blocks;
direction-free flatness wants large blocks.** One cannot have both *in this family* —
and whether that is intrinsic is exactly Lemma A.

**If YES:** "bound `a`" is closed negatively without any direction caveat, and the corridor
is provably empty in the model.

### OPEN LEMMA B — the spike certificate question

> If the answer to A is **no**, the proof of "no" is a **spike-existence theorem**: every
> capset at every round of a `Θ(L)`-round descent carries a `(1+2⁻⁸)`-factor density spike
> at codimension `≤ Θ(L)`.

*Why that is the prize.* By DA-1 such a theorem is **exactly** the input a same-rank (or
`O(1)`-rank, R1C-A′) dichotomy needs, and it is the one thing that would make the corridor
real. Note the calibration: DA-3 **already refutes the natural strong form** ("every capset
has a `1+2⁻⁸` spike at codimension `≤ D` for some absolute `D`"), since `Q_j` has none for
`D` up to `j−6 = Θ(L)`. What is *not* refuted is the version with `D` allowed to grow with
the round index. **That is the entire remaining width of the question.**

**Nothing in the ledger, in R1C-A, in R1C-A′, in the paper, or anywhere in the
Kelley–Meka / Bloom–Sisask / Schoen–Sisask lineage decides this.** (The literature search
was explicit: the only increment-counting argument anywhere in the lineage is the standard
`∏σ_j ≤ α⁻¹`; **nothing distinguishes expensive from cheap increments.** Schoen–Sisask do
have a doubling dichotomy at exactly this call site — `lemma:large_sumset` /
`lemma:small_sumset` — but **both branches call almost-periodicity and both pay
`d′ ≪ log⁴(2/α)`**; the small-doubling branch uses `|A+A′|` only in the denominator of the
final pigeonhole, **not** to skip AP. In SS every round is expensive and `a` is not even
definable.)

**One more thing SS tells you, and it is a useful cross-check on the autopsy.** SS take
`K = 2/α` from Bohr regularity with `α` the *current* relative density, so SS's
`log 2K = Θ(L)`. Raghavan's is `Θ(L²)` because he applies AP to the **sift output** `A₂`,
of density `α^{Θ(L)}`. **This independently localises the extra power of `L` in the sift,
from outside the paper.** And SS reach the same `L⁴` with the *opposite* bookkeeping —
`k = O(log(2/εη)) = O(L)` so `k² = Θ(L²)` times `𝔏(η)log 2K = Θ(L)·Θ(L)`, where Raghavan
buys `k = O(1)` with Lemma 4.4(4) and pays `Θ(L²)·Θ(L²)`. **Same `L⁴`, opposite
decomposition** — have this ready when someone proposes attacking `k`.

---

## 5. WHAT WAS NEVER ATTACKED — `𝔏(η)` AND THE `p = Θ(L)` HÖLDER COST

**Every lane in this campaign says, in its own honest-limits section, that it does not
touch `𝔏(η)`.** All five records say it independently. It is the other `Θ(L²)`, it is half
the `L⁴`, and **no one has laid a glove on it.**

### 5.1 What it is, exactly

```
   𝔏(η) = Θ(L²) ,     η = |A₁|/|S| ≥ |A₁|/(2|B⁵|) ≥ ½·α^{Θ(L)}      [TeX 599]
```

Two conceivable routes, and **one is already dead**:

* *(DEAD)* **Make `|S|` smaller.** The bound used is the trivial `|S| ≤ 2|B⁵|` after
  truncating `S` to `B⁵+B⁶+t`. **Machine-verified sharp** (§1.3): the super-level set fills
  `B⁵` exactly in `Z/401Z`, and it only grows as `σ′` falls toward the bottleneck. **No
  upper bound on the level set alone can shave `𝔏(η)`.**
* *(OPEN)* **Make `A₁` denser** — `dens ≥ α^{o(L)}`.

### 5.2 Why it is the single highest-leverage target left

The open route is the **same** `θ` that produces `log 2K`:

```
   θ = Θ(L) = max(  p = O(𝔏(γ))   [Lem 4.3, TeX 367 — the Hölder lifting]
                 ,  J·c₀, J = Θ(L) [Lem 4.4, TeX 542+545 — the sift loop]  )
```

> **A lane that makes the descendants dense — `dens(A_i) = α^{o(L)}` — attacks `𝔏(η)` and
> `log 2K` SIMULTANEOUSLY, because both are the same `θ`.** No fence in §3 touches this
> route: every one of them attacks `K` at fixed `θ`.

And the counterfactual is already costed: `θ = O(1)` collapses **both** `L²`s to `L`,
giving `d_J = O(L³)`, ambient `O(L⁴ log L)`, **exponent `1/4`**. One `L²` alone gives
`L³`, ambient `O(L⁵ log L)`, **`1/5`**.

### 5.3 The two independent causes of `θ = Θ(L)`, and what each would require

* **`J = Θ(L)` — hard, and the mechanism is exact.** Energy doubles each round (TeX 542)
  against the cap `‖μ_A∘μ_A‖_∞ ≤ α⁻¹μ(B)⁻¹` (TeX 545, verified exactly in 120/120
  instances): `σ ≥ 2^{J−1}` and `σ ≤ α⁻¹`. To shorten the loop you need a per-round energy
  gain that is **super-constant**, or a per-round density cost `α^{o(1)}` instead of
  `α^{c₀}`. *Note: the remark that "the bootstrap length is already `O(1)`" refers to the
  `k`-fold convolution in Theorem 4.8 — it does **not** apply to `J`.*
  Independent evidence that the Markov step is not the leak: `dens(A₂)/((1/4)α^m)` sits in
  `[2.1, 4.1]` for every spread configuration (the sift gives away only the factor 4 it
  visibly discards), and drawing `s` uniformly instead of from `P(s)` changes `|A₂|` by a
  factor 1.0–1.6. **The density loss `α^{Θ(L)}` is real, not an artifact.**
* **`p = O(𝔏(γ))` — structural, not sloppy.** The Hölder exponent at TeX 367 is chosen so
  `γ^{−1/p₀} ≤ 3/2`. Machine-checked that this is exactly the origin of the `𝔏(η)`-type
  factors: `(‖1_L‖_p‖μ_M‖_{p′})^p = |L|/|M| = 1/η`, verified for `p ∈ {2,3,5,7}`. **Any
  Hölder-lifting step pays `log(1/density)` in the exponent.**

### 5.4 Two further genuinely untouched corners

* **The full sift provenance is discarded.** The `Θ(L)` nested rounds each carry their own
  `σ_j` and their own pair `(Z_{2j−1}, Z_{2j})` with a doubling-energy history (TeX
  537–545); **all of it is thrown away at TeX 547** and only the *terminal* cross law is
  used. Each individual sift round costs only `α^{−q}` in doubling *relative to its own
  parent*; over `J = Θ(L)` rounds that compounds to `α^{−Θ(L)}`, which is why `Z_{2J}` —
  not the last sift — is where the `L²` lives. **Whether the intermediate pairs admit a
  doubling recursion was never tried.**
* **The `q`-fold containment is used only through `i = 1`.** `A₂ ⊂ ⋂_{i≤q}(A′+s_i)` with
  `q = 9933`, and every argument in this campaign (R1C-1, R1D-2, DA-1) uses exactly one of
  the containments. If the other 9932 carry information, none of the forcing criteria here
  is sharpest.

---

## 6. CLAIM BOUNDARY

* **This is an audit of an external preprint.** Raghavan, arXiv:2603.27045v3, *Improved
  Bounds for 3-Progressions*. **Authorship of all mathematics audited here remains
  R. Raghavan's.** Lemma A.7 is Schoen's (arXiv:2310.09584, Lemma 12); Theorem 4.8 and
  Lemma 4.9 are Schoen–Sisask's. We claim only: the audit, the defect register, the machine
  tests, the `L⁴` autopsy, the S-ledger, Theorems R1C-1 / R1D-1 / R1D-2 / R2-2 / R2-3 /
  T1–T4 / DA-1–DA-5, the counterexample families, and the fences.
* **`erdos142_solved: false`.** Wall A alone does not crack #142; the prize is an asymptotic
  formula.
* **`new_r3_bound: false`.** **Nothing in this campaign improves any exponent.** The `1/6`
  is Raghavan's and remains Raghavan's. No bound on `a`, partial or otherwise, was obtained;
  no bound on `S` was obtained.
* **"PROVED" means *proved given the paper's chamber***, which inherits two imports whose
  proofs are not in this source (Theorem 4.8 = [SS, Thm 5.1], Lemma 4.9 = [SS, Prop 5.3]).
  Their interfaces were machine-verified; their proofs were not.
* **"MEASURED" is not "PROVED", and the distinction is load-bearing here.** The lower half
  of the S-ledger, the saturation of the crude doubling bound, and the `Z/N` flatness trend
  are all measurements at scales `N ≤ 5.3·10⁵`, `m ≤ 8`, `α ≥ 0.08`, rank ≤ 2, extrapolated
  across `exp(Ω(L⁴))`. A judge is entitled to discount every one of them; the proved content
  does not rest on them, but **the fence on route (ii) does.**
* **Model caveats.** DA-3/DA-4, R1CA, T1–T4 and R1C-A′ live in the finite-field (subgroup)
  model, where "Bohr set" = subgroup and there is no radius; the paper's "same rank, smaller
  radius" is unrepresentable there, and condition (3) of `iteratedsiftresult` and the whole
  radius/regularity ledger are not modelled at all. **DA-1 and R1C-1 are model-free.** No
  `Z/N` counterexample was constructed by anyone in this campaign.
* **Every fence in §3 is a fence, not an impossibility theorem.** Each closes a *route*
  under stated hypotheses. In particular FENCE 7 shows R1C-A is unprovable *from call-site
  data*; a proof that reaches back across the sift to re-import 3AP-freeness of `A` — which
  the architecture consumes exactly once, at `liftunbalance` case (1), and never references
  again — is not excluded by anything here. **Building such a mechanism is a strictly larger
  project than any lane in this campaign.**

---

## 7. TRANSCRIPTION-DRIFT REGISTER — NINE CORRECTIONS TO THE LANE RECORDS

*Found by cross-checking every claim in §§1–6 against its lane artifact, the lane judges,
and the generating code. Corrections (C)–(F) and (I) are the lane judge's; (A), (B), (G),
(H) were found in this consolidation. **Prefer this column to the lane record.***

**(A) Lemma A.7's status is stale in three later records.** `CHAMBER_MAP.md` §4.5 (11:23)
records A.7 as **UNCLEAR**; `R2_narrowdensity_VERDICT.md` (11:39) **closed it the same
morning** (VERIFIED = Schoen Lemma 12 + full proof + 18 630 exact instances). But
`R1D_CORRIDOR_LEDGER_RECORD.md` §8.5, `DA_LINE3_DEVILS_ADVOCATE_VERDICT.md` §7.9 and
`R2A_BOUND_A_VERDICT.md` §7 (12:47, 15:36, 16:03) **all still say "Lemma A.7 remains
UNCLEAR (CHAMBER_MAP §4.5)"**. → **Consolidated status: VERIFIED.** The `1/6` chamber has
no UNCLEAR import remaining. *(The `c`-margin observation stands and is sharper than the
UNCLEAR tag ever was: A.7 is the **binding** constraint on `c`, clearing it by
`1.221·10⁻⁴`; any upward re-tuning of `c` must re-check A.7 first.)*

**(B) `R1CA_DICHOTOMY_VERDICT.md` §5's scaling table does not verify conclusion (4), and
its universal claim is false as written.** The table is captioned *"every row satisfying
(1),(2),(4), a legal `σ′`"*, and the headline claims *"for every pair of absolute constants
`(c,C)` there is a member of the family with `δ ≥ C` and `|A₂+B⁷| < c|B⁶|`"*. But the
generating code `R1CA_closedform.analyse` **never computes a `cond4` predicate** — it
computes only `Elevel`, documented in the source as a *"condition (4) proxy"*, and
`R1CA_scaling.py` filters on `cond1 & cond_sigma & cond2 & not branchb` only. Evaluating
the lane's own proxy on the published rows gives `Elevel/(2⁸σ′)` =
**11.55, 36.54, 411.5, 4.785·10⁴, 3.414·10⁶** at `h = 1,2,4,8,12` — **every published row
fails it**, by up to six orders of magnitude. This is consistent with the lane judge's
finding as recorded in `COORDINATION.md` (*"the judge showed it caps `δ·3^h ≤ 512`, so
R1C-A is refuted ONLY for constant pairs `C < 512c`"*).
→ **New exact identity that explains the cap:** in this family
`δ·3^h = |A₂|/(#cells hit) = |C ∩ (C+σ)| = 2^{m−t}` **identically** (from
`δ = |A₂||B⁷|/|B⁶|`, `|A₂+B⁷| = occ₂|B⁷|`, `|A₂| = occ₂·2^{m−t}`), so **imposing (4) is
exactly a cap on `m−t`.** Re-running the lane's own proxy as a constraint over
`h ≤ 4, m ≤ 29` gives `max δ·3^h = 2¹⁴ = 16384` at `(j,j5,j′,h,m,t) = (1,1,1,1,23,9)` —
so the *numeric* cap is grid- and functional-dependent (512 vs 16384) while the
*qualitative* correction is robust. → **Corrected statement: the family refutes R1C-A for
every `c > 0` and every `C` below an absolute multiple of `c`, not for every `(c,C)`.**
FENCE 7's sharpness conclusion (R1C-1 optimal; threshold unraisable) is **unaffected** — it
rests on the `K·α′ = 1` attainment and the `Z/NZ` interval family, neither of which uses
the scaling table.

**(C) THEOREM R2-3's "iff" is false as a biconditional** (judge J2). `K = α⁻²` has
`log 2K = 2L + O(1) = O(L)` yet branch (b) does **not** fire (checked at
`α = 10⁻⁶,10⁻¹²,10⁻²⁴,10⁻⁴⁸`, ratio/L ≈ 2.0 in every case). → **The true predicate is
`log 2K_j ≤ 𝔏(α′_j) + O(1)`, i.e. `(1+o(1))L`, not the asymptotic class `O(L)`. Only
`branch(b) ⇒ log 2K = O(L)` holds.** FENCE 6's arithmetic survives; the printed
biconditional does not.

**(D) R2-3's ledger comparison rests on an unquantified counterfactual substitution**
(judge J4 — labelled by the judge *"the load-bearing defect"*). Branch (b) outputs `B⁷` at
rank `d_{j−1}`; branch (a) outputs `B⁸` at rank `d_{j−1}+O(k²L⁴)`. The two exits hand
**different Bohr sets** to round `j+1`, so the corridor run and the always-AP run diverge at
the first branch-(b) round — **and with them the numbers `K_j`**. `a` is defined on the
corridor run, while R2-3 charges `O(L³)` at the `J−a` cheap rounds *of the always-AP run*.
That substitution is licensed only if the `a`-bound is **round-local and uniform over
admissible states**; a purely amortised/dynamical bound does not transfer, and R2-3 supplies
no such uniformity. → **Record FENCE 6 as "redundancy proved modulo a uniformity hypothesis
on the `a`-bound."**

**(E) R2-1's first identification argument is wrong** (judge J1). `R2A_BOUND_A_VERDICT.md`
§1.1(a) states *"Both SS theorems carry the same hypothesis `|A+S| ≤ K|A|` — verified
verbatim (checks C0c, C0d)"*. In fact SS **Theorem 3.2** (`thm:Linfty-ap_FF`), the one
Raghavan's `ff-AP` cites, contains **no `|A+S| ≤ K|A|` hypothesis at all**; the string the
lane checked belongs to SS **Theorem 2.1** (`thm:Lp-ap`). SS Theorem 5.1 (`thm:Linfty-ap`)
*does* carry it. → **The conclusion of R2-1 survives via argument (b) only** — routing the
ff theorem through `thm:Lp-ap` at `S := G`, where the printed codimension is reproduced up
to the exact factor `1 + log2/log(1/α) → 1`. **Drop the "verbatim" claim; keep the routing
argument.** *(Also: SS's `thm:Lp` is cited to [CLS, Thm 7.4], which was not in the local
cache and was not audited.)*

**(F) Defect D20's stated contradiction is backwards** (judge J5). The typo at TeX 205
("**times**" for "**more than**") is real, and TeX 201 does set `V₀ = G`. But
`codim(V_J) = 0` gives `|V_J| = N`, which **satisfies** `|V_J| ≥ exp(−O(L⁵))N` — so the
lane's stated contradiction does not arise. → **The real break is bullet 1: `V_j = G` forces
`α ≥ (1+2⁻⁵)α`, so no `J ≥ 1` exists and the ff iteration is void from the start.** The
repair ("at most `C𝔏(α)⁴` **more than**", yielding `codim(V_J) = CJL⁴ = O(L⁵)`) is
unchanged, and D20 remains ff-section-only, TYPO-REPAIRABLE, with Theorem 1.4 unaffected.

**(G) "Route (ii) is dead" is a measurement, not a theorem.**
`R1C_sifted_doubling_VERDICT.md`'s headline says route (ii) *"is **dead**"*; its own §8.1
says *"This is measurement, not proof"*, and the lane judge refuted the extrapolation
(`m ≤ 8, α ≥ 0.08, N ≤ 200 003` vs `m = Θ(L)`; faithful instances need `N ~ e^{729}`).
Independently, FENCE 7 shows `log 2K = Θ(L²)` is **not forced** by call-site structure —
legal configurations with `log 2K = L + O(1)` exist. → **Carry it as: route (ii) is
measured-dead, and the measurement is load-bearing.** The correct fence statement is the
conditional one (§3, FENCE 3(a)): *under* branch (a), `log 2K = Θ(L²)` exactly.

**(H) T1′'s asymptotic gloss needs its hypothesis.** `R1E_..._RECORD.md`'s headline reads
*"Asymptotically `c* = (1+o(1))·α/ε²`, i.e. `c* = 2²⁰α′` at `ε = 2⁻¹⁰`."* Re-derived here
exactly: `c*/α = 4080` at `α = 2⁻¹²` (where `c* = 0.9961` has saturated toward its ceiling
1), `5.243·10⁵` at `α = 2⁻²⁰`, `1.048·10⁶ = 2²⁰` only at `α = 2⁻³⁰`. → **The exact form
`c* = α/(α+ε²(1−α))` is correct; the `α/ε²` gloss requires `α ≪ ε² = 2⁻²⁰`.** (Judge
correction, independently reproduced.) T1/T2/T3/T4 are unaffected.

**(I) Five `R2A` checks are definitional tautologies** (judge J6), and carry no evidential
content: `C4a` is `(x·y)/x/y == 1`; `C9b` ("deficit ratio exactly `L`") is `L²/L`; `C10a`
("`K*` strictly decreasing in `σ′`") is `x ↦ 1/x`; `C5b` is `0·x == 0`; `C7a/C7b` are the
author's own formulas re-evaluated. → The underlying claims stand on other grounds (and the
judge re-derived C8's gap independently, J7); **but do not cite these check numbers as
evidence.**

---

## 8. LIVENESS TEST

`verify_wall_a.py` in this directory re-runs the **cheapest exact check from each of the
four lanes**, plus an independent exact re-derivation of the campaign's load-bearing
constants and a regression tripwire for drift (B). Total runtime ≈ 5 s.

```
  python E:/arena/research_erdos142_wall_a_consolidation_20260730/verify_wall_a.py
```

| # | lane | script re-run | expected |
|---|---|---|---|
| L1 | `research_erdos142_chamber_audit_20260730` | `CHAMBERMAP_L4_autopsy_checks.py` | `16 passed, 0 failed` |
| L2 | `research_erdos142_sifted_doubling_20260730` | `R1B_shiftlaw_doubling_exact.py` | 280 checks, `failures 0`, `DONE (part 1)` |
| L3 | `research_erdos142_dichotomy_r1ca_20260730` | `R1D_corridor_ledger.py` | `21 passed, 0 failed` |
| L4 | `research_erdos142_bound_a_20260730` | `R1E_local_dichotomy.py t1` | `T1 verified on every instance: True` |

Plus, self-contained and exact (`fractions.Fraction` / integers, no float decides
anything): the source `sha256`; the shadow activation coefficient `1024/3069` and the
window length `log(3(1−2⁻¹⁰))`; the σ′-matched corridor constant
`(1−2⁻⁸)(1−2⁻¹¹)(1+2⁻⁷) = 67336065/67108864 ≥ 1025/1024`; the DA-1 forcing constant
`(1−2⁻⁸)(1+2⁻⁷) = 32895/32768 = 1+2⁻⁸−2⁻¹⁵`; A.7's binding constraint on `c`
(`1/819200 ≤ 1/819100`, margin `1.221·10⁻⁴`); D1's vacuity `4097/4096 > 1` and its repair;
`ε⁻² = 2²⁴`, `k² = 361`; T1′'s exact threshold with the `α ≪ ε²` caveat; the DA-5
trade-off `D·J ≤ L/ln 3`; and the drift-(B) tripwire `δ·3^h = 2^{m−t}` with the
conclusion-(4) proxy failing on every published scaling row.

---

*Record written 2026-07-30 (late). Source sha256 verified at write time. Every claim
transcribed here was checked against its lane artifact, its generating code, and the lane
judges; nine corrections are registered in §7. Authorship of arXiv:2603.27045v3 and all of
its mathematics remains R. Raghavan's.*

`erdos142_solved: false` · `new_r3_bound: false` · `cracked: false`
