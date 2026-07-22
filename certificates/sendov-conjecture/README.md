# Sendov’s Conjecture — wall ledger (computational assault, 2026-07-21)

**Problem.** Sendov’s conjecture (1958; also “Ilieff’s conjecture” by misattribution
in Hayman 1967): if a complex polynomial \(f\) of degree \(n\ge 2\) has all zeroes in
the closed unit disk \(\overline D(0,1)\), then for every zero \(\lambda\) there is a
critical point (zero of \(f'\)) in \(\overline D(\lambda,1)\).

Equivalently, writing
\[
d(f)=\max_i\min_j|z_i-\zeta_j|
\]
for roots \(z_i\) and critical points \(\zeta_j\), the conjecture asserts \(d(f)\le 1\)
for every such \(f\). A **counterexample** is any \(f\) with roots in the disk and
\(d(f)>1\).

## Literature status (unchanged by this certificate)

| Regime | Status | Reference |
|--------|--------|-----------|
| \(n<9\) | **proved** | Brown–Xiang 1999 |
| \(n\) sufficiently large | **proved** (non-explicit \(n_0\)) | Tao, *Acta Math.* 229 (2022); arXiv:2012.04125 |
| Intermediate \(9\le n<n_0\) | **open** | — |
| Equality case | \(z^n-1\) achieves \(d=1\) | classical |

Unlike the Jacobian Conjecture (refuted 2026 by an explicit dim-3 map — see
[`../jacobian-conjecture/`](../jacobian-conjecture/)), Sendov already has large
affirmative regions. The only place a CE can live is the intermediate-degree band.

## What is certified here

`verify.py` (numpy + stdlib; ~few seconds) checks:

1. **Unity extremals** for several \(n\): \(\beta=1\), all crit at \(0\) ⇒
   \(p(z)=(z^n-1)/n\), radius \(r=1\), max\|root\|=1 — equality case, **not** a CE.
2. **Miller 2005 local extrema** (arXiv math/0505424): reconstructed from published
   \(P'\); each has \(0.7<r<0.99\) and roots in the disk — local maximizers **below** 1.
3. **Dual-ray wall (sampled)**: scaling crit \(=t\cdot u\) from \(0\) until radius
   \(\ge R\in\{1.01,1.05,1.1\}\) forces min max\|root\| \(>1\) on a fixed seed list of
   directions (no ray CE).
4. **Committed result tables** under `results/` are CE-free and match the claimed
   qualitative wall (dual-ray positive slack; squeeze \(\delta=0\Rightarrow r=1\);
   jet sample count + empty CE list).
5. **Negative control**: a configuration with \(r>1\) is **not** flagged as a CE
   when roots leave the disk.

This is a **negative-result / wall ledger**, not a disproof and not a proof for any
new \(n\).

## Campaign findings (summary)

Multi-lane assault (crit-param optimizers, free complex \(\beta\), Miller-type
multiplicities, Tao near-CE family, lune dual, extremal jet, dual-ray, squeeze
curves, dense grids, arc-roots, mpmath polish). Aggregate: **0 counterexamples**;
best **feasible** \(d=1\).

| Lane | Scope | Result |
|------|--------|--------|
| Crit-param / free \(\beta\) / rich multiplicity | \(n\) up to 26+ | Always rediscover \(r=1\) at \(\beta=1\) |
| Extremal jet | 26 775 samples, \(n\in\{9,10,12,15,20\}\) | best feasible \(r\le 0.99998\); every \(r>1\) infeasible; 0/80 FD dirs raise \(r\) without raising maxroot |
| Dual-ray | \(n\in\{9..30\}\), \(R\in\{1.001,1.01,1.05,1.1\}\) | min maxroot \(\approx 2R-1>1\); CE=0 |
| Dual-fast | \(n=9..30\), 65 rows | \(r>1\Rightarrow\) maxroot\(>1\); positive slack; CE=0 |
| Deep multi-lane | \(n\in\{9..16,20,26\}\), 77 configs | best feasible score \(=1.0\) (unity) every \(n\); CE=0 |
| Squeeze \(r^*(\delta)\) | \(n\in\{9,10,12,15,20\}\) | \(\delta\le 10^{-3}\Rightarrow r=1\); \(\delta\ge 10^{-2}\Rightarrow r<1\) |
| Lune dual (force crit into \(D(0,1)\setminus D(a,1)\)) | \(n\in\{9,10,12,15,20\}\), \(a\)-grid | feasible \(\Leftrightarrow r\le 1\); best feasible \(r\to 1^-\); CE=0 |
| Miller dense grids | \(n=9..12\) | best on-grid \(r\sim 0.95\); CE=0 |
| Wave3 free complex \(\beta\) + dual | \(n=9..20\), 3 penalties + dual R-grid | all free-\(\beta\) hits \(r=1\); dual \(r>1\Rightarrow\) maxroot\(>1\); CE=0 |
| Tao near-CE family | \(n=9..80\) | best feasible gap \(\sim 0.75\) |
| Wave6 two-real-crit | \(n\in\{9,10,12,15,20\}\) | best feasible \(r\le 0.997\); CE=0 |
| Wave7 complex two-crit dual | \(n\in\{9,10,12,15,20\}\), \(R\in\{1.01,1.05,1.1\}\) | dual force never CE; CE=0 |
| Wave7b three-real-crit | \(n\in\{9,10,12,15\}\) | best feasible \(r\sim 0.929\); CE=0 |
| Wave8 n=9 lattice | 271 908 two-crit evals | best feasible \(r=0.9975\); CE=0 |
| Wave9 free dual \(n=9\) | free \(\beta\) + 8 complex crits, \(R\in\{1.001..1.1\}\) | CE=0; \(R=1.1\Rightarrow\) maxroot\(\gg 1\) |
| Wave9b free dual \(n=12\) | free \(\beta\) + 11 complex crits | CE=0; meets \(R\) only with positive maxroot slack |
| Dense \(\beta\)-scan | \(n=9..30\) complete, 321 configs | best feasible \(=1\) (unity) every \(n\); CE=0 |
| Wave12 arc-crit dual | equal-spaced crits on circle, \(n\in\{9,12,15,20\}\) | dual CE=0 (never maxroot\(\le 1\) at \(r>1\)) |
| Wave10 Miller dual | \(n\in\{9,12,15,20,26\}\), Miller \(P'\) shape | dual \(R>1\Rightarrow\) maxroot\(>1\); CE=0 |
| Wave10b true \(d(f)\) \(n=9\) | free roots in disk, maximin \(d\) | best numeric \(d\approx 0.991\) (underestimates unity); CE=0 |
| Wave11 free dual \(n=15\) | free \(\beta\) + 14 complex crits | CE=0; dual force never CE |

**Theorem (equal-crit family).** If all critical points coincide at \(c\) and \(p(\beta)=0\), roots lie on the circle of radius \(|\beta-c|\) about \(c\). Hence \(r>1\) forces some root outside the unit disk — **no CE in this family for any \(n\ge 2\)**. See [`THEOREM_EQUAL_CRIT.md`](THEOREM_EQUAL_CRIT.md).

**Structural slogan (empirical, within these families):**  
*To get Sendov radius past 1, you leave the unit disk.*

Machine-readable tables: [`results/`](results/).

## What is NOT certified

- Absence of a counterexample in **all** of \(\mathbb C^n\) configuration space.
- Any new degree \(n\) for which Sendov is proved.
- An effective Tao \(n_0\).
- Novelty/priority of Miller’s local extrema or Tao’s analysis (cited, not claimed).

## Clues read from the rest of the atlas (why this lives here)

- **JC crater** (`atlas/jc-crater/`): dim-3 JC is refuted; **plane JC (\(n=2\))** remains
  open — a surviving affine-geometry frontier. Sendov is a different polynomial
  geometry question (roots vs critical points), also open in an intermediate band,
  also equality-sharp. Same atlas posture: name walls as loudly as targets.
- **`atlas/walls.md`**: “an atlas that only lists targets is advertising; an atlas
  that names its walls is a map.” This certificate is a wall ledger for a natural
  CE-hunt after JC fell.
- **Tao near-CE analysis** (arXiv:2012.04125): perturbative families that *would*
  give a CE if critical points landed in an open lune fail on average — consistent
  with our dual-ray / jet numbers.

## Epistemic status

A counterexample would be self-certifying (exhibit \(f\), check \(d(f)>1\) and
roots in the disk). We did **not** find one. We **did** machine-check the classical
extremals, Miller locals, and a dual-ray wall sample, and we ship the campaign’s
result tables CE-free. Treat this as **C1–C2 computational evidence** for a wall
in the attacked families — not as a theorem for intermediate \(n\).

## Replay

```bash
python3 certificates/sendov-conjecture/verify.py   # exit 0 = baselines hold
```

Dependencies: `numpy` (already required by other certificates’ ecosystems;
verify itself is one file + `results/`).

## Provenance

- Campaign: 2026-07-21 agent lane `agent/sendov-wall-ledger-20260721`.
- Literature anchors: Brown–Xiang 1999; Miller arXiv math/0505424; Tao arXiv:2012.04125.
- Sister JC certificate: external Alpöge construction; here the *search* and
  *wall map* are ours, and the claim is narrow enough that `verify.py` proves it.
