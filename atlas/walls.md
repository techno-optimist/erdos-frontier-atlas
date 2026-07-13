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

## Already attacked-and-walled by our exact toolset at ≥ our scale (the clearest traps)

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
  close a(12)…a(16), so repeat compute on those cells is now a named wall;
  only a(17) and later remain live.

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
