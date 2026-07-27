# WALLS — do not spend compute here

**This file is as load-bearing as the target list.** Every problem below has the
seductive shape of a verifier-first farm attack — a finite witness, a cheap
checker, a numeric record — and every one of them is a dead end for generic
compute. They are named here, with sources, so that no agent (ours or anyone
else's) burns a farm rediscovering them. Pricing the walls honestly IS the
product: an atlas that only lists targets is advertising; an atlas that names
its walls is a map.

A wall for **us** is not always a wall for **everyone** — a handful of these
have witness sides that remain fair market-maker boards (someone else's new
construction wins; our pinned verifier adjudicates). Those carry
`board_class: READY|HEAVY` in `problems.json` despite `beatable: WALL`. The
walls below are walls for *spending our own search compute*.

---

## "Falsifiable" upstream is not "reachable" here — read this before mining the handle

`atlas/stubs.json` now records `upstream_finite_handle` wherever erdosproblems.com
marks a problem `decidable`, `falsifiable` or `verifiable`. Forty-three problems
carry one. It is a genuinely useful signal, and it is **not** a target list.

Upstream is classifying **decidability in principle** — *if* the conjecture is
false, a finite counterexample exists and would settle it. This file classifies
**reachability in practice**. Those are orthogonal, and a problem can honestly be
both. Seven are, and **six of the seven carry a prize**, which makes them exactly
the entries a scout is most tempted by and most likely to burn a farm on:

| problem | upstream handle | prize | why the handle does not help |
|---|---|---|---|
| **#19** | `decidable` | $500 | Erdős–Faber–Lovász is **proved for large n** (Kang–Kelly–Kühn–Methuku–Osthus, *Annals* 2023). The witness branch is empty; what remains is small-case certification, which reduces to pigeonhole/resolution and has no compact certificate. |
| **#64** | `falsifiable` | $1000 | **This row was too coarse — see the split below.** The *general* problem (min degree ≥ 3, any graph) has an unbounded witness branch and remains a wall. The *cubic* sub-lane does not. |
| **#97** | `falsifiable` | $100 | Measure-zero collinearity defeats float search; nonexistence needs order-type enumeration with an **∃ℝ realizability gap** — no DRAT route exists. |
| **#107** | `falsifiable` | $500 | Happy Ending `f(7)=33`: Heule/Scheucher/Marić/Bogdan **already run our exact SAT+DRAT order-type pipeline**, at 2.28M CPU-sec per configuration. Do not duplicate an active, walled 2026 effort. |
| **#114** | `falsifiable` | $250 | Lemniscate length: transcendental objective (elliptic integrals) so no exact/DRAT verifier — and **Tao proved the conjecture for all large n** (arXiv:2512.12455). |
| **#128** | `falsifiable` | $250 | Sparse Half: the verifier is **NP-hard** (Sparsest-k-Subgraph), failing the cheap-verification precondition, and a counterexample is conjectured not to exist (tight at n²/50). |
| **#548** | `falsifiable` | — | Erdős–Sós: believed-empty witness branch. |

### #64 splits, and our wall only covered one half

A 2026-07-26 feasibility triage of all 43 finite-handled problems confirmed six of
the seven rows above — several with sharper reasons than we had — and **contradicted
#64**, correctly.

Erdős–Gyárfás asks whether every graph with minimum degree ≥ 3 contains a cycle
whose length is a power of two. Over *all* such graphs the witness branch really is
unbounded, which is what this file recorded. But the **cubic** sub-lane is bounded
and unswept:

- Klas Markström, *Extremal graphs for some problems on cycles in graphs*,
  Congr. Numer. 171 (2004), §4 — generated **all cubic graphs on fewer than 30
  vertices** with Brinkmann's `minibaum`, and found none.
- Cubic graphs on 30 vertices: **845,480,228,069** (OEIS [A002851](https://oeis.org/A002851),
  tabulated to 32 vertices, so the class is demonstrably generatable).
- ≈10¹² generations with C4/C8 early-abort — one workstation, days not years.
- Verification is bounded-DFS cycle detection on integers: exact, dependency-free,
  no floats, no CAS.
- **Nobody has swept n = 30.** The published frontier is still Markström 2004.

That is a live records-lane rung, not a resolution: a clean sweep yields "no cubic
counterexample on ≤ 30 vertices", two decades of nothing more. It is recorded here
rather than in the target list because the *problem* stays walled — only this one
sub-lane is reachable, and it should be entered with that expectation.

**The general lesson, which is why this is in walls.md and not a footnote:** a wall
row that says "witness branch unbounded or believed empty" can be true of a problem
and false of its most-studied special case. Two rows carried that phrasing (#64,
#548); #548 survived re-examination, #64 did not. When writing a wall, say which
*branch* is walled.

The pattern is worth naming, because it is why the handle misleads. A conjecture
gets marked falsifiable precisely when it is *believed true* — so the finite object
it promises is the one nobody expects to exist. Add the cases where the conjecture
is already **proved for all large n**, and "falsifiable" collapses to "finitely many
hard leftovers", which is a wall wearing a target's clothes.

Use the handle to *narrow* a search you already had reason to run. Never use it as
the reason to start one.

## Already attacked-and-walled by our exact toolset at ≥ our scale (the clearest traps)

- **#617 — Erdős–Gyárfás balanced colourings, r=5 (K₂₆).** *Added 2026-07-27;
  our own triage called this a TARGET nine days earlier and was already wrong.*
  **Closed upstream:** between 18 and 25 July 2026 the problem page collected
  **five independent claimed proofs for r=5** — Sneiderman (extremal),
  Silverstein (12 DRAT-certified UNSAT instances, **independently reproduced**
  by Del Pin from regenerated CNFs, 12/12), Rose (458 DRAT instances, ~13.4
  GiB), Land, and **Kara, a Lean 4 formalization whose finite obstruction is
  replayed inside the Lean kernel** — plus Sneiderman for r=6,7,8,9. None is
  refereed and a claim sets no status here, but five artefacts of that quality
  make our compute waste.
  **And the encoding is a fence in its own right.** We priced this lane by
  instance size — "sane, 1,625 vars / 1.15M clauses". Measured: cadical returns
  UNKNOWN at 300 s on **K₂₅, which is satisfiable and whose witness we hold**
  (AG(2,5); verified against all 888,800 clauses), and UNKNOWN at 2400 s on
  K₂₆. Rose reports the identical failure and identifies the cause as symmetry,
  not missing constraints: one instance of his drops from ≥14,400 s to 0.45 s
  under symmetry-breaking. **Never price a SAT lane by variable and clause
  count.** The cheap diagnostic we should have run first is one instance of
  known answer at the next size down. Full notes:
  [`certificates/erdos-617/FINDINGS.md`](../certificates/erdos-617/FINDINGS.md).

- **#139 / #140 — r₃(212), largest 3-AP-free set (A003002).** Last exact term
  r₃(211)=43; 212 ∈ {43,44}. **Ergezer 2026 (arXiv:2606.04016) threw ~7,850
  worker-hours** of CP-SAT + HiGHS-MIP + CDCL + DRAT/LRAT at it — *our exact
  arsenal, on a cluster larger than ours* — and hit a **paradigm-invariant hard
  pocket** (flat LP dual pinned at 0.0; 2 chunks survived 8-hour budgets). The
  author's own conclusion: it needs new theory (Fourier/SDP/Lean), not compute.
  **Do not duplicate an active, walled 2026 effort.** (The 44-set *witness*
  side stays a fair market board — that is the one exception, and it is
  believed empty.)
- **#107 — Happy Ending f(7)=33.** Heule/Scheucher/Marić/Bogdan **already run
  our exact SAT+DRAT order-type pipeline** (Bogdan Dec-2025: 16.67M clauses,
  heavy-tailed to 2.28M CPU-sec per configuration, "far from resolving"). No
  edge; heavy tails defeat a 100-core farm. (The 33-point refutation *witness*
  board is fair — and refuting Erdős–Szekeres at n=7 is believed impossible.)

## Records held by the same or superior tools, static for 12–60 years

- **#159 — R(C₄,K₁₁) ∈ [39,44]:** RIT/Radziszowski SAT + exhaustion, 12 years static.
- **#165 — R(3,10) ∈ [40,41], #166 — R(4,6) ∈ [36,40] / R(4,k):** Exoo simulated
  annealing + McKay orderly generation = literally our own tools.
- **#138 — W(2,7) van der Waerden:** a saturated, tuned-SLS arms race
  (Heule/Monroe); DRAT nonexistence infeasible at N ~ 10⁴–10⁵.
- **#564 — R₃(4,5;3) ≥ 35:** record set by the identical SAT class-decomposition
  we would bring.
- **#77 / #1029 — diagonal Ramsey R(5,5)/R(6,6):** our own R(5,5) campaign
  already closed this (no witness; 42 DRAT-certified asymmetry certificates —
  DOI [10.5281/zenodo.21305022](https://doi.org/10.5281/zenodo.21305022));
  R(6,6)/R(8,8) lower bounds static 55–60 years.
- **#30 (Sidon h(N)/OGR-28), #39 (OGR/A004137), #687 (Jacobsthal Y(x), A048670),
  #52 (sum-product A263996), #20 (sunflower Sun(m,s)):** records set by
  distributed.net / Al Zimmermann contests / Google-Cloud runs of **our own
  exhaustion tools at larger scale**. OGR-28 alone took a global volunteer grid
  8.5 years (completed Nov 2022).

## Verifier is NOT poly-time / no clean certificate (fails the core precondition)

- **#128 — Sparse Half:** the verifier is NP-hard Sparsest-k-Subgraph; a
  counterexample is ~nonexistent (conjectured tight at exactly n²/50); the real
  frontier is Razborov's flag-algebra SDP (2021).
- **#90 — unit distance u(22), #92 — equidistance g(5):** the exact-value
  verifier is **∃R-hard** (realizability of a graph in R²); the specialists'
  own embeddability solver returns "I don't know" (Alexeev–Mixon–Parshall,
  arXiv:2412.11914, ~6,100 CPU-hours for u(21)).
- **#211 / #588 / #101 — orchard 3-/4-point lines (A006065, A003035):**
  measure-zero collinearity defeats float search; nonexistence needs order-type
  enumeration with an **∃R realizability gap** — no DRAT route exists.
- **#114 — lemniscate length:** transcendental objective (elliptic integrals),
  no exact/DRAT verifier; Tao proved the conjecture for all large n
  (arXiv:2512.12455, Dec 2025).

## Polynomial geometry — post-JC CE-hunt walls (adjacent, not Erdős-numbered)

- **Sendov’s conjecture (Ilieff misattr.):** \(d(f)\le 1\) for polynomials with
  roots in the unit disk. Proved for \(n<9\) and for large \(n\) (Tao 2022,
  non-explicit \(n_0\)); open only for intermediate degrees. **Equality is sharp**
  (\(z^n-1\)). A 2026-07-21 multi-lane CE assault (crit-param, free \(\beta\),
  Miller strata, Tao near-CE family, dual-ray, extremal jet 26 775 samples,
  squeeze curves) found **0 counterexamples** and a consistent wall. Across the
  *sampled* families (not proved in general): forcing radius \(R>1\) drove
  max\|root\| \(\approx 2R-1>1\) on radial crit scalings, and local jets at the
  unity extremal never raised \(r\) without ejecting roots. These are search
  observations — a fence on where to spend compute, not a theorem.
  **Do not burn fleet DE on random roots of unity without high-precision
  validation** (double `np.roots` underestimates \(d\)). Wall ledger:
  [`certificates/sendov-conjecture/`](../certificates/sendov-conjecture/)
  (`python3 certificates/sendov-conjecture/verify.py`). Still open for a true
  exact \(n=9\) decision procedure or effective Tao \(n_0\) — that is theory /
  exact real algebra, not random search.

  **Update 2026-07-25 — the "effective \(n_0\)" half is CLAIMED; the wall does not
  move.** J. Pickhardt with an "Omniscience Research Agent" ([explicit
  threshold](https://omniscienceproject.com/papers/an-explicit-high-degree-threshold-for-sendovs-conjecture-deEGnk8R),
  2026-07-22, self-published, unrefereed, with a Lean companion) claims an explicit
  version of Tao's threshold at \(N_0=\exp(10^{126})\). We read it and did not break
  it, but **nothing here becomes computable**: \(N_0\) has \(\approx 4.34\times10^{125}\)
  decimal digits — the digit *count* is itself a 126-digit number — so \([9,N_0]\)
  still holds \(\sim10^{4.34\times10^{125}}\) undecided degrees. Skewes-type numbers are
  small by comparison. **No degree becomes reachable and no search becomes feasible;
  do not read "the gap is now finite" as an opening.**

  Two things in that paper *are* worth knowing before spending here. (1) The
  astronomical cost is **not diffuse** — it sits in a single sliver,
  \(0.99\le a\) with \(1-a>90/(n^{12}\log n)\); everything else is covered at
  \(n\ge e^{400}\), and the dominant term is the Fejér order (\(<10^{123}\)) needed
  for pointwise root density at \(\eta_0=4.73\times10^{-61}\). Anyone attacking the
  constant should attack that sliver, and the author's own view is that it needs a
  different argument, not sharper constants. (2) Its Corollary 11.2 gives Sendov for
  every marked zero with \(a\le 1/2\) at \(n\ge\lceil e^{400}\rceil\approx10^{174}\) —
  still unreachable, but \(10^{(4\times10^{125})}\) times smaller than the headline,
  and the part a follow-up would actually build on.

  Net for us: **\(n=9\) is now the sole tractable-looking target and remains a wall.**

## Witness not representable / physically astronomical

- **#2 / #27 — covering-system minimum modulus 42:** a minimum-40 witness
  already has **>10⁵⁰ recursively-defined congruences** — not encodable in any
  SAT/ILP/MIS instance; the density headline is already disproved
  (Filaseta–Ford–Konyagin–Pomerance–Yu 2007).
- **#1135 — Collatz:** the frontier 2⁷¹ is held by a GPU-supercomputer sieve
  (Barina, J. Supercomputing, Jan 2025) 2–4 orders of magnitude beyond a CPU
  farm; arithmetic iteration gives SAT/MIS **zero leverage**; the exhaustion
  claim has no compact certificate.
- **#19 — Erdős–Faber–Lovász:** conjecture proved for large n (Kang–Kelly–Kühn–
  Methuku–Osthus, Annals 2023), so the witness branch is empty; the small-case
  certification branch reduces to **pigeonhole, resolution-exponential** — a
  farm does nothing.

## Asymptotic-only / flag-algebra / already solved (no finite frontier at all)

- **#500 / #712 — Turán tetrahedron 5/9:** the lower bound is a closed-form
  construction (A140462, believed exact); the upper bound is flag-algebra SDP
  at its wall (Razborov 2010), with 6^{n/3}-fold extremal degeneracy.
- **#146 — degenerate bipartite Turán**, **#161 — hypergraph discrepancy
  jumps**, **#183 — R(3;k)^{1/k} limit**, **#182 — Erdős–Sauer** (NP-complete
  verifier, no tracked record; headline proved 2023–2024).
- **#43 / #83 / #703 / #707 — Sidon-pair / EKR / forbidden-intersection /
  perfect-difference-set:** proved or disproved (the last one Lean-verified,
  Alexeev–Mixon PNAS 2025); no movable number remains.
- **#708 — g(n) divisibility, #548 — Erdős–Sós, #64 — 2-power cycles,
  #552 — R(C₄,S_n):** unbounded or believed-empty witness branch — or, for
  #552, a table being pushed by the same SAT tools: repository certificates
  close a(12)…a(16) and certify the a(17) lower endpoint, so repeat compute on
  those cells is now a named wall; only n=17,m=22 and later remain live.
- **#421 — distinct consecutive products** (density-1 sequence with all
  \(\prod_{u\le i\le v} d_i\) distinct): erdosproblems.com states it **cannot be
  resolved with a finite computation**, so it is ineligible for our records and
  witness lanes — reference only. Recorded here because a **claimed solution is
  circulating** (P. Chojecki, ulam.ai, 2026-07-13, machine-authored, 5pp,
  self-hosted, not on arXiv) and **upstream still marks #421 OPEN** as of
  2026-07-25. We read it and found nothing wrong, but three earlier "final"
  proofs of the same statement by the same pipeline each had real errors found
  by readers within days, and a requested human-written version has not
  appeared. **Do not sink #421 on a headline** — a scraper that closes a cell
  because someone announced a proof is precisely the failure the #552 retraction
  was supposed to teach us. Status changes when *upstream* changes, not when a
  claim appears. Cross-refs: #786 (finite version, Selfridge density 1/e), #795.

---

## The meta-rule

Before any Erdős-adjacent compute spend, check this file and the audit
(`problems.json`, fields `beatable_reason` / `wall_reason`). If a problem looks
computational and is not in the READY/HEAVY board catalog, assume it is here,
and assume the reason is one of the four above: **someone already walled it
with our tools at larger scale · the verifier is not exact-poly-time · the
witness is not representable · there is no finite frontier at all.**

Source: 51 deep audits over the 95 Erdős prize problems, 2026-07-11
(`research_sessions/res_20260711_erdos_machinery_audit/AUDIT.md`, section 3).
