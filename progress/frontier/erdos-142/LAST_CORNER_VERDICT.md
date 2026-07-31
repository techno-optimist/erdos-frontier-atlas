# THE LAST CORNER — `L(eta)`, the `p = Theta(L)` Hölder cost, and the σ-floor

    erdos142_solved: false
    new_r3_bound:    false
    cracked:         false
    date:            2026-07-30 (late)
    lane:            Erdős 142 / Wall A / consolidation
    primary source:  E:/arena/tmp/raghavan2603_source/main__2_.tex
                     sha256 b31eb727fd30ac6194184e4462ea1f73f0ce74e18a2a31abe101fa26b814d6bc
                     (re-verified in-script as check C0 before any TeX was quoted)
    artifacts:       LC_holder_exponent_lab.py  ->  LC_holder_exponent_lab.log
                     31 enumerated checks, 31 PASS, 0 FAIL, all arithmetic exact
    answers:         WALL_A_FENCE_COMPLEX.md §5 ("the highest-value untouched
                     target ... which nobody attacked at all") — same directory,
                     written earlier the same session; §7b below corrects its §5.2
    authorship:      This is an AUDIT of an external preprint (Raghavan,
                     arXiv:2603.27045v3). All mathematics of the preprint remains
                     R. Raghavan's. This lane claims only the audit, the criterion,
                     the profiles and the machine tests.

---

## 0. HEADLINE

> **The last corner is empty. The `p = Theta(L)` Hölder cost is not forced, and even
> if it were it would not matter.**
>
> Question (i) — *is `p = Theta(L)` forced?* — **REFUTED as stated**, by exact
> computation on the very object the GOAL named as the extreme candidate. Replaced
> by a **proved, exact criterion**: `p_min = Theta(L)` **iff** the convolution excess
> of `mu_A o mu_A` sits at **constant height** on measure `Theta(alpha)`; at excess
> height `alpha^{-s}` the minimal exponent is pinned at `p_min ~ (1+s)/s`.
>
> Question (ii) — *is the bottom avoidable?* — **the bottom is already a constant**
> (`sigma >= 1+2^-12`, TeX 305). There is nothing to reschedule. Every constant
> floor leaves `J = Theta(L)`; DA-4 exhibits a legal execution with `sigma_j == 3`
> and `J = Theta(L)`. **Refuted as a route.**
>
> Question (iii) — the combined fence — **is not the fence the GOAL expected.** The
> descendant-density exponent `theta = Theta(L)` **is** intrinsic, but its cause is
> the **sift budget**, not the CS/unbalancing route: the paper's own guarantee
> carries an *unconditional* `alpha^{lo(alpha)/log 2 + O(1)}` floor (TeX 468, 540,
> 555, 561) that is present at `J = 1` and is independent of `p` and of `gamma`.
> **Setting `p = 0` leaves the `L^4`, the `L^6 log L` ambient and the `1/6`
> bit-identical.** The Hölder exponent is **redundant** — the same shape as the
> `R1D-2 / R2-3` redundancy already recorded for the corridor.

Nothing here improves any exponent. The `1/6` is Raghavan's and remains Raghavan's.

---

## 1. Setup: what "the Hölder cost" actually is

The `p` in question is created at exactly one place, **TeX 365–367**:

> `By H\"older's inequality, for any $p_0\geq 1$, the left-hand side is bounded above by`
> `\[\gamma^{-1/p_0}\|(\mu_{A}-\mu_{B^0}\ast \mu_{B'}) \ast (\mu_{A}-\mu_{B^0}\ast \mu_{B'})\|_{p_0(\mu_{B'})}\geq 3\cdot 2^{-3}\mu(B)^{-1}.\]`
> `We choose $p_0 = O(\lo{\gamma})$ such that $\gamma^{-1/p_0} \leq 3/2$`

The loss is the **dual-norm factor** `||mu_C||_{p_0'(mu_{B'})} = gamma^{-1/p_0}`, and
`gamma >= (1-2^-11)alpha` at the call site (TeX 584), so `lo(gamma) = Theta(L)`. The
unbalancing lemma (TeX 333, `[BS1, Lemma 7]`) then multiplies by `O_epsilon(1)` at the
absolute `epsilon = 2^-3`, so the *proof's* exponent is `Theta(L)`.

Define the object the forcing question is really about:

```
   p_min(f, nu, tau)  :=  least integer p >= 1 with  ||f||_{p(nu)} >= tau ,
   f = mu_A o mu_A ,   tau = (1+2^-5) mu(B)^{-1}   [TeX 341, 400] .
```
`||f||_{p(nu)}` is non-decreasing in `p`, so the predicate is monotone and `p_min` is
well defined and bisectable — used throughout the lab.

---

## 2. LC-1 — THE DIAGONAL CERTIFICATE  *(PROVED, one line, hypothesis-free)*

> **LC-1.** For any `A`, any probability measure `nu`, with `nu_0 :=` the `nu`-mass of
> the atom `{0}`:
> ```
>       ||f||_{p(nu)}^p  >=  nu_0 * (alpha^{-1} mu(B)^{-1})^p
>   =>  p_min  <=  log(1/nu_0) / log(1/(alpha*tau)) .
> ```
> *Proof.* `f(0) = mu_A o mu_A(0) = alpha^{-1}mu(B)^{-1}` (TeX 545), and drop every
> other atom. ∎

This is the **trivial-progression term**, and it costs nothing. Its whole content is
the ratio `log(ambient) / L`:

| `log(1/nu_0)` | certificate | meaning |
|---|---|---|
| `Theta(L)` | `p = O(1)` | near-extremal capset / EG regime |
| `Theta(L^2)` | `p = Theta(L)` | the Behrend balance |
| `>> L^2` | `p >> L`, **useless** | **both theorems' operative regime** |

**The regime caveat matters and is easy to get wrong.** At *extremal* capset density
(`alpha <= (2.756/3)^n`, Ellenberg–Gijswijt) the certificate gives `p <= 13` for every
`A ⊂ F_3^n` — machine-checked, and it is `p <= 4` at the best known capset density
`2.2174^n` and at the DA-3/DA-4 density `2.0801^n`. **But the operative regime of
Theorem 1.5 is `n = Theta(L^5)`, not `n = Theta(L)`** — the theorem asserts
`alpha <= exp(-Omega((n log 3)^{1/5}))`, so the binding instances have `L ~ n^{1/5}`
and the certificate degrades to `Theta(L^4)`. In `Z/N` it is worse still: at the
Lemma 4.3 call site `nu = mu_{B''} o mu_{B''} * mu_{B'''} o mu_{B'''}` gives
`nu_0 >= 1/(|B''||B'''|)`, and `log N = Theta(L^6 log L)` (TeX 325), so the certificate
is `Theta(L^5 log L)`.

**Consequence, and it is a positive one for the paper:** the `gamma^{-1/p}` Hölder
route is a *genuine* gain over the trivial term in both operative regimes. Lemma 4.3
is not being sloppy. `p = O(lo(gamma))` is the right kind of bound.

---

## 3. LC-2 — THE NAMED EXTREME CANDIDATE REFUTES FORCING  *(PROVED, exact)*

The GOAL names `the DA-3 capset profile with |1hat| = alpha^2` as "the extreme
candidate — its `f` is maximally flat". It is the extreme candidate, and it goes the
**other** way.

> **LC-2a.** For `Q_j = {(x^2+lambda y^2, x, y)} ⊂ K + K^2`, `K = F_{3^j}`, `-lambda`
> a non-square (DA-3), `alpha = 3^{-j}`:
> ```
>       f(psi,q)  =  mu_{Q_j} o mu_{Q_j}(psi,q)  =  1 + 1_{q=0} * (3^j * 1_{psi=0} - 1)
> ```
> i.e. `f` is **exactly 1** off the subgroup `{q=0}`, **exactly 0** on
> `{q=0}\{0}`, and `1/alpha` at the origin. Hence
> ```
>       E f^p  =  1 - alpha^2 + alpha^{3-p}   for every p >= 1 .
> ```

*Machine:* built over `F_3`, `F_9`, `F_27` (`|G|` up to `3^9 = 19683`); 3AP-freeness
exhaustive for `j = 1,2`; the closed form checked at **every** point of `G`; the
moment identity exact for `p = 1..8`. (Checks C1.1–C1.3.)

> **LC-2b.** `p_min(Q_j, 1+2^-3) = p_min(Q_j, 1+2^-5) = 3` for **every** `j >= 3`.

Because the entire convolution excess of the flattest capset sits in the **single
diagonal atom**, of measure `alpha^3` (`|G| = alpha^{-3}`), the certificate LC-1 fires
at `p = 3`: `||f||_3^3 = 2 - alpha^2`, so `||f||_3 = 2^{1/3} = 1.2599... >= 9/8`.
Machine-checked exactly for `j = 1..12` (C2).

> **LC-2c.** For the devil's tower `T_J = Q_1^{⊗J}` (DA-4) — the near-extremal capset
> on which **every** round of the Theorem-1.4 iteration is crude-tight —
> ```
>       E f_{T_J}^p  =  (8/9 + 3^{p-3})^J  ,       p_min(T_J) <= 3  for EVERY J,
> ```
> and `p_min` is **non-increasing** in `J`: the tower gets *easier*, not harder, as
> `alpha -> 0`. Machine-checked to `J = 10^4` exactly, with the tensor identity
> verified by brute force in `F_3^{3J}` for `J = 1,2,3` (C3).

**Reading.** `p = Theta(L)` is **not** a theorem about admissible inputs to Lemma
4.3 / Lemma 2.5. On the same object where the *sift loop* is provably `Theta(L)`
(DA-4: `sigma_j == 3`, `J = log_3(1/alpha)`), the *Hölder lift* is `O(1)`. **The two
`Theta(L)`s in `theta = max(p, c_0 J)` are independent, and only the second one is
carried by the devil.**

---

## 4. LC-3 — WHAT IS ACTUALLY FORCED: an exact shape criterion  *(PROVED at profile level)*

Model of the Lemma 4.3 input, units `mu(B)^{-1} = 1`. A *profile* is an atomic
probability density `f >= 0`, `E f = 1`, with

```
    origin : mass 1/N      value 1/alpha          (forced: f(0) = 1/alpha)
    excess : mass beta     value lambda
    bulk   : mass ~1       value c < 1            (fixed by E f = 1)
```
and the **model hypothesis** is the *exact* Hölder input of TeX 364/366:

```
    exists C of mass gamma = alpha  with  (1/gamma) <f - 1, 1_C>  >=  3 * 2^-3 .
```
Give the excess the **least** mass that still meets it with **equality**:
`beta = (3/8) alpha / (lambda - 1)` (`<= alpha` iff `lambda >= 11/8`). Write
`s = log(lambda)/log(1/alpha)` for the **excess height exponent**.

> **LC-3.** `p_min = log(1/beta) / log(lambda/tau) * (1+o(1)) ~ (1+s)/s`.
> Hence **`p_min = Theta(L)` iff `s = Theta(1/L)`, i.e. iff the excess sits at
> CONSTANT height.** At the flat end `lambda = 11/8`,
> `p_min = log(1/alpha)/log(4/3) = 3.4761... * L * (1+o(1))`.

Machine (C6), `alpha = 2^-40`, `log N = 1.1e4 >> L^2 = 808` (the chamber's regime, so
LC-1 is not binding), exact:

| `lambda` | `s` | `beta` | `p_min` | `p_min/L` | closed form |
|---|---|---|---|---|---|
| `11/8` | 0.01149 | `2^-40.00` | **97** | **3.413** | 96.38 |
| `3/2` | 0.01462 | `2^-40.42` | 75 | 2.639 | 74.76 |
| `2` | 0.02500 | `2^-41.42` | 43 | 1.513 | 43.34 |
| `4` | 0.05000 | `2^-43.00` | 22 | 0.774 | 21.99 |
| `16` | 0.10000 | `2^-45.32` | 12 | 0.422 | 11.46 |
| `1024` | 0.25000 | `2^-51.41` | 5 | 0.176 | 5.16 |
| `2^20` | 0.50000 | `2^-61.42` | 3 | 0.106 | 3.08 |
| `2^40 = 1/alpha` | 1.00000 | `2^-81.42` | **2** | 0.070 | 2.04 |

and the flat row's `p_min/L` was tracked over `alpha = 2^-12 .. 2^-48`, rising
monotonically to `3.415` against the predicted `1/ln(4/3) = 3.4761`.

**This settles question (i) in the only form in which it has an answer.**

* The Hölder step `gamma^{-1/p} <= 3/2` is **sharp as an inequality** — equality holds
  iff `g*g` is constant on `C` and `0` off `C`, which is *exactly* the `lambda = 11/8`
  row. At that configuration `p = Theta(L)` **is** forced, with the exact constant
  `1/ln(4/3)`, and the paper's `O(lo(gamma))` is order-optimal.
* But **nothing in the chamber forces that configuration**, and the near-extremal
  capsets sit at the opposite extreme `s = 1` where `p_min = 2`.
* So `p = Theta(L)` is a statement about the **shape of the excess**, not about the
  chamber. A "lower-bound construction where no `p = o(L)` certifies the level"
  exists as a **profile**; whether it is realised by a **set** at a legal call site is
  the residual gap, and §8 says why that gap is not worth closing.

---

## 5. LC-4 — THE LEVEL IS NOT THE COST DRIVER  *(PROVED, exact)*

The GOAL's framing is *"the unbalancing lemma needs `||f||_p` to SEE the level"*, with
the worry that the bottom `sigma ~ 1+2^-7` is what makes `p` large. **It is not.**
`p_min` depends on `tau` only through `log(lambda/tau)`, and `lambda` is `alpha^{-s}`,
so the `tau`-dependence is a *lower-order additive shift in the denominator*:

| `alpha` | `L` | `tau=1+2^-7` | `1+2^-5` | `1+2^-3` | `2` | `4` | `16` |
|---|---|---|---|---|---|---|---|
| `2^-32` | 22.87 | 3.001 | 3.004 | 3.016 | 3.097 | 3.200 | 3.429 |
| `2^-128` | 89.42 | 3.000 | 3.001 | 3.004 | 3.024 | 3.048 | 3.097 |

Max ratio across `tau ∈ [1+2^-7, 16]` at `alpha <= 2^-32`: **1.1425** (C5). Raising the
unbalancing target from `1+2^-5` to any absolute constant changes `p` by `O(1)`.
**"The level sits near the bottom" is a red herring for `p`.**

---

## 6. LC-5 — QUESTION (ii): THE BOTTOM IS ALREADY A CONSTANT  *(PROVED from the TeX)*

The GOAL asks whether the iteration could be re-scheduled to consume only
`sigma >= 1+delta_0` for constant `delta_0`. **It already does, verbatim:**

| TeX line | statement |
|---|---|
| 305 (Prop 4.1) | `sigma ∈ [1+2^-12, alpha^{-1}]` |
| 402 (Lem 4.4) | `sigma' ∈ [1+2^-7, (alpha')^{-1}]` |
| 400 / 341 (Lem 4.3 case 3) | input level `(1+2^-5) mu(B)^{-1}` |
| 314/320 (Thm 1.4) | `prod_j sigma_j <= alpha^{-1}` |

`delta_0 = 2^-12` **is** an absolute constant. There is nothing to reschedule away,
and re-scheduling to a **larger** constant is free and buys nothing, because the
budget is an *identity* (densities multiply and are `<= 1`), so
`J >= log(1/alpha)/log(1+delta_0)`:

| `delta_0` | `1/log(1+delta_0)` | `J` at `alpha=2^-64` |
|---|---|---|
| `2^-12` (Prop 4.1) | 4096.500 | 181726.6 |
| `2^-7` (Lem 4.4) | 128.499 | 5700.4 |
| `1` (`sigma=2`) | 1.443 | 64.0 |
| `2` (`sigma=3`, DA-4) | 0.910 | 40.4 |
| `7` (`sigma=8`) | 0.481 | 21.3 |

Every row is `Theta(L)`. Only `sigma_j = alpha^{-Omega(1)}` escapes — a per-round
energy gain **polynomial in `1/alpha`**, which the chamber cannot deliver (Lemma 4.7
case (1) delivers `2^6 sigma` where `1 sigma` is required — the only tight link,
CHAMBER_MAP §2; case (2) and property (3) at TeX 542 deliver a factor `2`).

And it is **refuted by construction**: DA-4's devil's tower executes the Theorem-1.4
chain with `sigma_j ≡ 3` for every `j` — far above every floor in the chamber — and
`prod_j sigma_j = alpha^{-1}` with **equality**, `J = log_3(1/alpha) = Theta(L)`.
**No scheduling can manufacture large `sigma`.** (C7.)

---

## 7. LC-6 — QUESTION (iii)'s SURPRISE: `p` IS REDUNDANT  *(PROVED from the TeX)*

Read the paper's own density guarantees:

| TeX line | guarantee |
|---|---|
| 468 (Lem 4.7 conclusion) | `dens >= min( alpha^{O(1)} * gamma , alpha^{lo(alpha)/log 2 + O(1)} )` |
| 472 (Lem 4.7 proof) | `p = max( lo(gamma)/lo(alpha) , lo(alpha)/log 2 ) + O(1)` |
| 540 / 555 / 561 (Lem 4.4) | `zeta_j >= min( alpha^{c_0} zeta_{j-1}, … , alpha^{lo(alpha)/log 2 + c_0} )` |
| 405 / 556 (Lem 4.4 concl. 2) | `dens(A_i) >= alpha^{p + O(lo(alpha))}` |

The floor exponent `lo(alpha)/log 2 = log_2(2/alpha) = L/log 2 = 1.442695 * L`
(exact, C8) is:

* **independent of the Hölder exponent `p`**,
* **independent of `gamma`**,
* **independent of the number of rounds** — it is already there at `J = 1`,
* and it is one of the two branches of the `max` at TeX 472, **both** of which
  CHAMBER_MAP's `[MT]` shows are necessary.

> **LC-6.** `theta = p + Theta(L)` with the `Theta(L)` unconditional. Therefore
> **`p = 0` gives `theta = Theta(L)`**, and the whole downstream ledger is unchanged:

| `p` | `theta` | `log(1/dens X)` | rank/incr | `d_J` | ambient | exponent |
|---|---|---|---|---|---|---|
| `0` | `Theta(L)` | `Theta(L^4)` | `O(L^4)` | `O(L^5)` | `O(L^6 log L)` | **1/6** |
| `O(1)` | `Theta(L)` | `Theta(L^4)` | `O(L^4)` | `O(L^5)` | `O(L^6 log L)` | **1/6** |
| `Theta(L)` | `Theta(L)` | `Theta(L^4)` | `O(L^4)` | `O(L^5)` | `O(L^6 log L)` | **1/6** |
| *(and only if the unconditional floor went too)* | `O(1)` | `Theta(L^2)` | `O(L^2)` | `O(L^3)` | `O(L^4 log L)` | 1/4 |

Both `Theta(L^2)` factors of the `L^4` — `log 2K` and `lo(eta)` — are `Theta(theta*L)`
with the **same** `theta` (CHAMBER_MAP §3.1, `[MT]`), so shaving `p` alone moves
neither. **The Hölder/unbalancing route is fenced out of the `L^4`.**

This is the same redundancy shape as `R2-3` for the `R1D-2` corridor: the quantity is
real, the question about it is answerable, and the answer changes nothing.

### 7b. A correction to the campaign's own bookkeeping: `θ` has THREE causes, not two

`CHAMBER_MAP.md` §3.1 and `WALL_A_FENCE_COMPLEX.md` §5.2/§5.3 both decompose

```
   θ = Θ(L) = max(  p = O(𝔏(γ))  [Lem 4.3, TeX 367]  ,  J·c₀, J = Θ(L)  [Lem 4.4, TeX 542+545]  )
```

**That list is missing a term, and the missing term is the decisive one.** Lemma 4.7's
own conclusion (TeX 468), via the second branch of the `max` at TeX 472, carries

```
   dens ≥ min( α^{O(1)}·γ ,  α^{𝔏(α)/log 2 + O(1)} )        [TeX 468]
   p    = max( 𝔏(γ)/𝔏(α) , 𝔏(α)/log 2 ) + O(1)             [TeX 472]
```

so **a SINGLE application of Lemma 4.7 — `J = 1`, any `γ`, any `p`, case (2) — already
guarantees only `α^{Θ(L)}`.** (CHAMBER_MAP does record this as `★ L-POWER #2` in its
flow diagram; what is missing is its consequence in §3.1's `θ` decomposition.)

Consequences, both of which change what the next attacker should do:

* Shaving `p` alone: useless (LC-6).
* **Shortening the sift loop alone (`J = O(1)`): also useless**, unless Lemma 4.7's
  own case-(2) floor is removed at the same time. `WALL_A_FENCE_COMPLEX` §5.3's
  "per-round energy gain that is super-constant" would shorten `J` and still leave
  `θ = Θ(L)`.
* The only decomposition that closes is: `θ = O(1)` requires **all three** of
  {`p = O(1)`, `J = O(1)`, Lemma 4.7 case (2) avoided} — and DA-4 refutes the second
  in the model. The correct headline is not *"make the descendants dense"* but
  *"make the descendants dense against three independent `Θ(L)` tolls, one of which
  fires at `J = 1`."*

---

## 8. THE COMBINED FENCE  *(the answer to (iii), stated exactly)*

> **THE LAST-CORNER FENCE.**
>
> 1. The descendant-density exponent `theta = Theta(L)` **is** intrinsic to the
>    chamber, and with the `S`-ledger and the `L^4` autopsy this pins the whole
>    insertion point: `L^4 = log(2K) * lo(eta) = [theta L][theta L]`.
> 2. **But `theta`'s intrinsic cause is the SIFT BUDGET, not the CS/unbalancing
>    route.** The Hölder-lifting exponent `p` is (a) **not forced** — refuted on the
>    DA-3/DA-4 near-extremal capsets, where `p_min <= 3` uniformly (LC-2), and shown
>    to be a property of the excess *shape* rather than of the chamber (LC-3); and
>    (b) **redundant** — `theta = p + Theta(L)` with the `Theta(L)` unconditional
>    (LC-6), so `p = 0` leaves the `1/6` bit-identical.
> 3. The intrinsic half is the **SIFT**, and it charges `Theta(L)` in *two*
>    independent ways (§7b):
>    * **the loop length.** `prod_j sigma_j <= alpha^{-1}` (TeX 314/320) is an
>      **identity**; every deliverable `sigma_j` is a constant (`sigma >= 1+2^-12` is
>      already the floor, LC-5, and DA-4 realises `sigma_j ≡ 3`), hence
>      `J = Theta(L)` rounds at `alpha^{c_0}` each;
>    * **the per-application floor.** Lemma 4.7's own conclusion (TeX 468, via the
>      `lo(alpha)/log 2` branch of TeX 472) guarantees only `alpha^{Theta(L)}` at
>      **`J = 1`**, for every `gamma` and every `p` (C8b).
>    Killing either one alone leaves `theta = Theta(L)`.
> 4. Therefore **"the descendant-density exponent `Theta(L)` is intrinsic to any
>    CS/unbalancing route through this chamber" is TRUE but MIS-ATTRIBUTED.** The
>    `Theta(L)` is not a Hölder / `lo(eta)` / `p` / unbalancing-level cost at all: it
>    is the sift's toll, charged twice over. An attacker who spends a lane on the
>    Hölder exponent — on `p`, on the unbalancing level `tau`, or on the "bottom of
>    the chamber" — is provably spending it on a redundant parameter; and an attacker
>    who only shortens the loop has not escaped either.

**Where the live slack actually is** (unchanged from CHAMBER_MAP §3.2, and this lane
confirms it is the only place left): a non-trivial doubling estimate
`|A_2 + B^7| <= K|A_2|` with `log K = o(L^2)` for the *sifted* set
`A_2 = C_2 ∩ (A'+s_1) ∩ … ∩ (A'+s_p)`. That attacks `log 2K` directly and requires no
new inequality anywhere else. The sifted structure of `A_2` is used by the paper to
control its **density** and never to control its **doubling**.

---

## 9. HONEST LIMITS — what is measured, what is proved, what is neither

1. **The `Theta(L)` witness is a PROFILE, not a SET.** LC-3's `lambda = 11/8` row is an
   admissible atomic probability density satisfying the model Hölder hypothesis with
   equality. **No `A ⊂ B` realising it at a legal Lemma 4.3 call site is exhibited.**
   So *"`p = Theta(L)` is forced at the call site"* is **neither proved nor refuted**
   here. What is proved is (a) the *universally quantified* form is **false**
   (DA-3/DA-4), and (b) the exact criterion that decides it. Given LC-6, closing this
   gap has no consequence for any exponent — which is why the lane stops here rather
   than hunting a set realisation.
2. **The model hypothesis is a faithful but simplified stand-in.** LC-3 imposes the
   TeX 364/366 pairing bound on `f - 1` directly; the paper's object is
   `g*g` with `g = mu_A - mu_{B^0}*mu_{B'}`, converted to `g o g` by `firstcompare`
   (TeX 370) and then unbalanced (TeX 372). Those two steps are constant-factor and
   were audited in CHAMBER_MAP; they are **not** re-derived here.
3. **LC-6 reports what the paper PROVES, not what is TRUE for every `A`.**
   `theta = p + Theta(L)` is read off the stated guarantees at TeX 405/468/540/555.
   A different sift with a smaller unconditional floor is not excluded by this lane —
   it is excluded, at the level of the loop length, by LC-5 + DA-4.
4. **DA-4 is a statement about one legal execution in the finite-field (subgroup)
   model**, as its own lane states. Its `Z/N` status is *fenced, not closed*. LC-2's
   refutation of universal `p = Theta(L)` is model-free (it is an exact computation
   about `mu_A o mu_A` for an explicit `A`), but its *relevance* to the `Z/N` call
   site inherits DA-4's caveat.
5. **The DA-3/DA-4 densities are not the operative regime.** `Q_j` and `T_J` have
   `alpha = exp(-Theta(n))`, i.e. `log|G| = Theta(L)`; the operative regime of
   Theorem 1.5 is `n = Theta(L^5)`. This is why LC-1 fires on them and not at the
   call site. They still refute the universally-quantified forcing claim — they are
   admissible inputs to Lemma 2.5 — but they are not evidence about the binding
   instances. **This distinction is easy to lose and this lane makes it explicit.**
6. **Everything downstream of `theta` is inherited, not re-verified.** The
   `log 2K = Theta(L^2)`, `lo(eta) = Theta(L^2)`, `L^4`, `L^6 log L`, `1/6` chain is
   CHAMBER_MAP's, with its `[MT]` status; §7's counterfactual table only substitutes
   `theta` into it.
7. **The §7b correction is about the campaign's own records, not about the preprint.**
   TeX 468/472 are correct as printed; what was incomplete is CHAMBER_MAP §3.1's and
   WALL_A_FENCE_COMPLEX §5.2's two-term decomposition of `θ`. Both documents record
   the missing term elsewhere (CHAMBER_MAP's `★ L-POWER #2`); only its consequence was
   not drawn.
8. **Lemma A.7 is no longer the open import.** As of the concurrent
   `research_erdos142_sifted_doubling_20260730/R2_narrowdensity_VERDICT.md` it is
   **VERIFIED + PROVED-HERE**. Theorem 4.8 = `[SS, Thm 5.1]` and Lemma 4.9 =
   `[SS, Prop 5.3]` remain unverified-from-this-source; their *interfaces* were
   machine-checked in CHAMBER_MAP, their *proofs* were not. Nothing in this lane
   touches them, and §8's fence is stated *given the chamber*.
9. `erdos142_solved: false`, `new_r3_bound: false`. Wall A's honest output remains the
   completed fence complex.

---

## 10. MACHINE TEST REGISTER — `LC_holder_exponent_lab.py` (31 PASS / 0 FAIL)

All group-algebra arithmetic exact (`fractions.Fraction`, Python ints, `F_{3^j}` via
polynomial tables). Floating point appears only in ratio tables and in the log-space
`p_min` solver, which is **cross-checked against the exact rational solver** at
`alpha = 2^-12` (agreement on both profiles).

| check | what it tests | result |
|---|---|---|
| **C0** | source sha256 vs the GOAL | MATCH |
| **C1.1–C1.3** | `Q_j` built over `F_3, F_9, F_27`; 3AP-freeness exhaustive (`j=1,2`); closed form `f = 1 + 1_{q=0}(3^j 1_{psi=0} - 1)` at **every** point; `E f^p = 1 - alpha^2 + alpha^{3-p}` for `p=1..8` | 8/8 PASS |
| **C2** | `p_min(Q_j, tau)` exact, `j = 1..12`, four `tau` | `= 3` for `tau ∈ {1+2^-3, 1+2^-5}`, all `j>=3`; bounded overall |
| **C3** | per-block moments `8/9 + 3^{p-3}`; tensor identity `E f_{T_J}^p = (E f_{Q_1}^p)^J` by brute force in `F_3^{3J}`, `J=1..3`, `p=1..6`; `p_min(T_J)` to `J = 10^4` | identity exact; `p_min <= 3` for every `J`, **non-increasing** in `J` |
| **C4** | LC-1 dominates the exact `p_min` on `Q_j`, `j=3..12`; EG corollary `p <= 13`; operative-regime degradation `Theta(L^4)` (ff) and `Theta(L^4 log L)` (`Z/N`) | 3/3 PASS |
| **C5** | `tau`-insensitivity over `tau ∈ [1+2^-7, 16]`, `alpha = 2^-8 .. 2^-128` | max ratio **1.1425** |
| **C6** | profile dichotomy: hypothesis met with **equality** in every row; log-space solver vs exact rational solver; FLAT `p_min/L -> 1/ln(4/3)`; SPIKY `p_min = 2`; the full `lambda = alpha^{-s}` family vs the closed form | 6/6 PASS, closed form matched to `<= 1` integer in all 10 rows |
| **C7** | `J >= log(1/alpha)/log(1+delta_0)` for six constant floors; DA-4's `sigma ≡ 3` | PASS |
| **C8** | `lo(alpha)/log 2 = L/log 2 = 1.442695 L` exactly; counterfactual ledger for `p ∈ {0, O(1), Theta(L)}` | 2/2 PASS |
| **C8b** | which branch of TeX 468's `min` binds at `gamma = alpha^1`, `alpha = 2^-4 .. 2^-128` | branch (2) always — `J = 1` already pays `Theta(L)` |

### Explicitly READ, NOT machine-tested
* The proofs of Lemma A.7, Theorem 4.8, Lemma 4.9 (absent from the source).
* The `O_epsilon(1)` constant inside the unbalancing lemma `[BS1, Lemma 7]` (TeX 333) —
  its *shape* is used, its implied constant is not extracted; the paper does not state it.
* `firstcompare`'s `*` → `o` conversion constant at TeX 370–371 (audited in CHAMBER_MAP).

---

## 11. CLAIM BOUNDARY

* This is an **audit of an external preprint**: Raghavan, arXiv:2603.27045v3,
  *Improved Bounds for 3-Progressions*. **Authorship of all mathematics of the
  preprint remains R. Raghavan's.**
* `erdos142_solved: false`. Wall A alone does not crack #142; the prize is an
  asymptotic formula.
* `new_r3_bound: false`. **Nothing here improves any exponent.** The `1/6` is
  Raghavan's and remains Raghavan's.
* The only new results here are **negative or navigational**: LC-1 (the diagonal
  certificate and its regime), LC-2 (the exact profile of the Fourier-extremal capset
  and the refutation of universal `p`-forcing), LC-3 (the exact shape criterion and
  the constant `1/ln(4/3)`), LC-4 (`tau`-insensitivity), LC-5 (the σ-floor is already
  constant; rescheduling refuted), LC-6 (`p` is redundant), and the combined fence of
  §8. **These are fences and maps, not bounds.**

---

*Record written 2026-07-30. Source sha256 verified in-script before any TeX was
quoted. Script and log alongside this file in
`E:/arena/research_erdos142_wall_a_consolidation_20260730/`.*
