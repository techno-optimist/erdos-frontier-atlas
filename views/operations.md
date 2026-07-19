# Operations annex — campaigns, board classes, packaged boards

Deep operational material moved out of the front-door README (2026-07-19) so the
README can be signal. Nothing here was deleted; it was routed.

## Active computational frontiers

**Status on 2026-07-16.** The scout is the first agent working *from the hub*.
The unattended publisher cannot write to `main`; it writes provisional receipts
to `automation/frontier-scout`, and a reviewed PR promotes only evidence that
still passes the current verifier, replay, scope, and provenance requirements.

| problem | current state | highest-value next work | do not spend effort on |
|---|---|---|---|
| **#552 — `R(C4,K1,n)`** | **n=17 CLOSED**: `R(C4,K1,17) = 22` (Parsons 1975; independently, min-degree-5 on 22 vertices needs 55 edges > `ex(22;C4)=52`). **n=39 CORRECTED (2026-07-17)**: the earlier "=46 new value" claim is retracted — DS1 rev.18 lists `46 <= f(39) <= 47`, OPEN (lower bound 46 = Wu–Sun–Radziszowski 2015; our certified 45-vertex witness, [`certificates/erdos-552-f39/`](certificates/erdos-552-f39/), independently re-derives it). | The open cells and their SAT deciders: `f(39)` via a C4-free **46**-vtx min-deg-7 graph (UNSAT ⇒ 46, SAT ⇒ 47); `f(42)` via (49, min-deg 7); `f(44)` via (51, min-deg 7). Polarity-deletion families certified UNSAT at 49/51. | Attacking n=17 (closed since 1975). Trusting any single survey table for an equality claim — check DS1. |
| **#21 — `q(6)`** | The literature bracket remains `14 <= q(6) <= 18`. A recorded negative: the global-τ SAT/DRAT encoding is combinatorially hostile and reproducing even `q(5)>=13` by SAT times out. | Isomorph-free orderly generation with canonical augmentation and τ-deficiency pruning for `14 <= m <= 17`, including Barát's proven `V <= 29` cap when `m = 14`. Validate every survivor with the pinned board verifier. | Repeating the global-τ SAT/DRAT encoding that already hit the combinatorial blowup; treating a partial or well-sharded no-hit search as a lower bound. |

### Where agents should contribute

1. Start from the relevant record in [`atlas/problems.json`](atlas/problems.json)
   and its pinned verifier or certificate. Do not reconstruct a weaker
   session-local checker when a canonical one already exists.
2. Put bounded, provisional work in a feature branch and open a PR targeting
   `automation/frontier-scout`. A receipt must state the exact frontier,
   action, verifier output, artifact SHA-256, failure scope, and next gate.
3. Open a PR targeting `main` only for a durable promotion packet: the final
   witness or certificate, deterministic replay command, hostile fixtures,
   complete provenance, and a narrowly worded claim that the replay proves.
4. Coordinate around the two next gates above. Split work by independent
   bottleneck—construction, certified nonexistence, verifier hardening, or
   orderly generation—instead of cloning the same random search.

The newest certified movement is Erdős #552: five C₄-free graph witnesses meet
Parsons' upper bound and establish `R(C4,K1,n) = n + ceil(sqrt(n)) + 1` for
`12 <= n <= 16`; `n=17` is closed at 22; and a 45-vertex witness gives a
machine-checkable certificate of `R(C4,K1,39) >= 46` (a re-derivation of the
Wu–Sun–Radziszowski 2015 bound — the repository's earlier "=46" claim was
retracted after our own novelty gate found the cell open at `46-47` in DS1).
Re-run with `python3 certificates/erdos-552/verify.py` and
`python3 certificates/erdos-552-f39/verify.py`.

## The board classification (recomputed, not inherited)

`board_class` is recomputed from the verifier and frontier fields by a
four-conjunct rule (full text in `atlas/schema.json`):

- **READY (13)** — a submitted witness settles the claim in under a second of
  exact integer arithmetic, against a concrete open frontier, with no lossy
  restriction on the witness space. These can be bounty boards *today*.
- **HEAVY (14)** — exact adjudication exists but each claim costs a SAT run, a
  DRAT check, or an exhaustion-receipt audit: optimistic-oracle tier.
- **NONE (24)** — no exact poly-time verifier, or no representable witness, or
  no open finite frontier. These are the walls.

Crucially, `board_class` is independent of `beatable`: several of the thirteen
READY boards are **walls for us** (Ramsey lower bounds, W(2,7), the r₃(212)
witness…) where the honest play is market-making — host the board, pin the
verifier, pay whoever's new construction wins. Walls for us are not walls for
everyone.

## The seven packaged boards

Seven READY entries are already full P42 packages (pinned exact verifiers,
hostile fixtures, lying-claim tests) in the P42 Prizes repository:

`q6-intersecting-hypergraph` (#21) · `distinct-subset-sums-a11` (#1; a(10)=309 was closed exactly by Dyson in Oct 2025 — the board targets the open a(11) ∈ [310,594]) ·
`b3-ruler-11-marks` (#41) · `b3-subset-first-jump-9` (#241) ·
`edp-c3-longest-sequence` (#67) · `c4-star-ramsey-a17` (#552) ·
`hypercube-q7-c4-free` (#86)

These are independent computational-frontier bounties on Erdős problems —
**not** Erdős's own historical prizes, which are administered separately and
attach to asymptotic statements.

**q(6) (Erdős #21) — a recorded negative, and why it matters.** Our first
flagship pick was q(6): bracket 14 ≤ q(6) ≤ 18, incumbent record set by a
search abandoned at a 2014 4-core storage wall. We attacked it with the exact
SAT+DRAT pipeline that produced our R(5,5) certificates — and it **failed**.
q(r) is τ-critical: valid families are vanishingly rare among candidates and
the τ≥r constraint is a C(V,r−1) encoding blowup whose resolution proofs
explode. Reproducing even the *known* q(5)≥13 by SAT timed out (3600 s / 6.4 GB);
the target D(6,14) could not be decided at any proven vertex count. R(5,5)
worked because its constraints are **local** (SAT-friendly); q(r)'s are
**global and rare** (SAT-hostile). The right tool is **orderly generation**
(canonical augmentation — what Barát used), not SAT. So q(6) stays as a
**market-maker board**: the exact verifier works, the frontier is real and
movable — by generation or cluster cube-and-conquer, by someone whose tool
fits. This is the atlas doing its actual job: **routing the right method to
each problem, and recording where a method does not fit** is as valuable as
recording where it does. (Full arc + vertex bounds for the generation attack
in the campaign notes; entry #21 `campaign_finding`.)
