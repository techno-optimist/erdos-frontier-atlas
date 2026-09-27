# Erdős #1016 — minimal pancyclic graphs: h(n) through n = 186, t₆ = 67 and t₇ = 114

**Problem node `P1016`; gap-map surface `S:gap:1016:e03342cc` (the cell m(38)).**
A graph on n vertices is *pancyclic* if it has a cycle of every length
3, …, n. Such a graph is Hamiltonian, so it is Cₙ plus chords, and the least
number of edges is m(n) = n + h(n), where h(n) is the least number of chords
making Cₙ pancyclic. Write t_k for the largest n with h(n) ≤ k.

## What this certificate establishes

| n | h(n) | m(n) | status here |
|---|---:|---|---|
| 3 | 0 | 3 | exact |
| 4–5 | 1 | n+1 | exact |
| 6–8 | 2 | n+2 | exact |
| 9–14 | 3 | n+3 | exact |
| 15–24 | 4 | n+4 | exact |
| 25–40 | 5 | n+5 | exact |
| 41–67 | 6 | n+6 | exact |
| **68–114** | **7** | **n+7** | **exact** |
| **115–186** | **8** | **n+8** | **exact** |
| ≥ 187 | ≥ 8 | ≥ n+8 | lower bound only (h(187) ≤ 9) |

1. **No graph Cₙ + 6 chords is pancyclic for any n ≥ 68.** Hence **t₆ = 67**
   and h(n) ≥ 7 for every n ≥ 68.
2. **h(n) = 7 for every 68 ≤ n ≤ 108**, by (1) and explicit 7-chord witnesses.
3. The whole table above for n ≤ 67 is recomputed from scratch:
   t₁, …, t₆ = 5, 8, 14, 24, 40, 67.
4. **No graph Cₙ + 7 chords is pancyclic for any n ≥ 115.** Some Cₙ + 7 chords
   is pancyclic for every 109 ≤ n ≤ 114, so **t₇ = 114**, h(n) = 7 for
   68 ≤ n ≤ 114 and h(n) ≥ 8 for every n ≥ 115 (the k = 7 extension below).
5. **h(n) = 8 for every 115 ≤ n ≤ 186**, by (4) and explicit 8-chord witnesses.

Claims 1–3 are replayed by `verify.py`, claims 4–5 by `verify_k7.py --full`;
they are separate contract claims (`certificates/contracts.json`).

The atlas cell m(38) ∈ {43, 44} is **m(38) = 43**.

## What is new here, and what is replication

Credit for everything below 68 belongs to the people who found it first; this
directory re-derives it independently.

- **Griffin (2013)**, *Minimal Pancyclicity*, arXiv:1312.0274: m(n) for
  n ≤ 37 (t₁..t₄ = 5, 8, 14, 24). Reproduced; also matches OEIS A105206
  (n = 3..22, unchanged in the OEIS data export of 2026-09-27).
- **P. White and Claude (2026-07-29)**, *Erdős #1016 working report*
  (erdosproblemaday.com/report/1016): m(38), m(39), m(40) = n + 5.
  Reproduced (our own witnesses).
- **Robinfxa (2026-09-17, Lean 2026-09-22)**,
  [JSP-000846](https://github.com/Robinfxa/JSP-000846): m(41) = 47.
  Reproduced; at n = 41 our search meets exactly the 328 skeleton classes
  their certificates cover.
- **J. Pinckard and ToolsEnabled agents (2026-09-24)**,
  [erdos-1016-pancyclic](https://github.com/JoshuaPinckard/erdos-1016-pancyclic):
  h(n) = 6 for 41 ≤ n ≤ 67 (their 5-chord exclusion is one shape search,
  cross-checked at n = 41 only), the 6-chord family Fₙ used below, and no
  6-chord pancyclic graph for n ∈ {68, …, 71, 80, 82} or n ≥ 86. Their runs
  stopped with n ∈ {72, …, 79, 81, 83, 84, 85} **unfinished**, so t₆ was left
  as "67 or one of those". Everything they finished is reproduced here with
  two independent implementations.

**New in this certificate** (to our knowledge as of 2026-09-27; see the
freshness note): the thirteen open levels are excluded, which determines
**t₆ = 67**; the exact values **h(n) = 7 for 68 ≤ n ≤ 108**; and the first
two-implementation exclusion of 5-chord pancyclic graphs across 42 ≤ n ≤ 65.
The 7-chord witnesses are the external family Fₙ plus one chord found here.

**New in the k = 7 extension** (same caveat): the complete 7-chord census —
every one of the 496,875 dihedral classes of 7-chord skeletons refuted at every
115 ≤ n ≤ 215, and none with more than 213 distinct cycles, which settles
n ≥ 216 — so **t₇ = 114**; the 7-chord family G7(n) found by the search
(skeleton 0-2 0-11 1-6 3-8 4-10 5-9 7-12, arcs 1 1 1 4 (n−60) 8 1 13 2 25 1 2 1),
pancyclic for **every 61 ≤ n ≤ 113** and missing only length 61 at n = 114; one
other class for n = 114; and **h(n) = 8 for 115 ≤ n ≤ 186**, all witnessed by one
explicit 8-chord family S8(n) (skeleton 0-2 0-13 1-6 3-11 4-9 5-12 7-14 8-10,
arcs 1 1 1 13 1 8 1 22 (n−107) 1 50 4 1 2 1), pancyclic for **every
108 ≤ n ≤ 186** and missing only length 108 at n = 187. The skeleton of S8 is a
one-chord extension of G7's; it was found by an exact search over those
extensions at n = 185.

This is a finite computation. It says nothing about the asymptotic question
that Erdős #1016 actually asks (whether h(n) − log₂ n → ∞, with Bondy's
bounds log₂(n−1) − 1 ≤ h(n) ≤ log₂ n + log* n + O(1)). A claimed Lean proof of
h(n) = log₂ n + log* n + O(1) exists at
[JWKNT/erdos1016](https://github.com/JWKNT/erdos1016); it is **not** checked
here and sets no status in this atlas.

## Method

**Reduction.** Put the t chord endpoints of Cₙ + k chords in cyclic order.
The chords become k distinct pairs on {0, …, t−1} using every point (a
*skeleton*), and the graph is fixed by the t arc lengths x₀, …, x_{t−1} ≥ 1
with sum n (x_i ≥ 2 when a chord joins the two ends of arc i, otherwise it
would duplicate a cycle edge). A vertex inside an arc has degree 2, so a cycle
uses an arc entirely or not at all: every cycle is a connected 2-regular
sub-multigraph of the skeleton, of length |S| + Σ x_i over its arcs, where S
is its chord set. For a given S, evenness at each endpoint forces the arc
indicator r_i = r_{i−1} ⊕ (d_i mod 2), leaving r or its complement, so there
are at most 2^{k+1} − 1 cycles and exactly the listed *cycle forms*. This is
the reduction used by Griffin, Robinfxa and Pinckard et al.; it is re-derived,
not imported.

**Decision.** For one skeleton and one n, `pancyclic.Search` decides exactly
whether some arc lengths realise all of 3..n. It discards a partial state only
by *capacity* (fewer distinct forms can still reach an uncovered length than
there are uncovered lengths — each form takes one value) or *domain* (some
uncovered length is reachable by no form), and it branches exhaustively: pick
an uncovered length ℓ; some non-constant form must equal ℓ, i.e. the free arcs
in that form sum to a fixed value, so enumerate those arcs (or, equivalently,
the complementary free arcs). Each child fixes at least one more arc. These
are the rules Robinfxa's n = 41 certificates use; the code is independent.

**Counting beyond the search.** k chords give at most 2^{k+1} − 1 cycles, and
a skeleton with fewer than n − 2 distinct forms cannot be pancyclic. The most
distinct forms any 6-chord skeleton has is 109, so n ≥ 112 needs no search.
Adding a chord keeps a graph pancyclic, so excluding 6 chords excludes ≤ 6.

**k = 7.** The same search over the 496,875 classes of 7-chord skeletons
would take the Python reference about 10 CPU-hours, so it runs in `pancyc.c`,
a C port of `pancyclic.Search` that keeps its class order, cycle forms, memo,
target shortlist and branching order. Every replay first checks that the port
reproduces `RESULT.json` **node for node** at all 45 k = 6 levels. The most
distinct forms any 7-chord skeleton has is 213, so n ≥ 216 needs no search;
the full k = 7 exhaustion (115 ≤ n ≤ 215) is about 560 million search nodes,
roughly 80 CPU-minutes. The hardest level is the boundary n = 115 (151,157
eligible classes, 119.5 million nodes).

## Why the negative result can be trusted

A search that prunes too much reports "no graph" and looks exactly like a
theorem. The checks are aimed at that failure:

- **Two implementations that share no code.** `pancyclic.py` searches one
  skeleton per dihedral class (21,878 for k = 6), computes cycles by the
  parity recurrence, and branches on a cost-chosen length. `xcheck.c`
  searches **all 384,668 labeled** 6-chord skeletons with no symmetry
  reduction, enumerates cycles by DFS on the skeleton multigraph, and always
  branches on the smallest uncovered length. Both report zero pancyclic
  skeletons at every n from 68 to 111. At every one of those orders the
  orbit-weighted Python class counts equal the C labeled counts, and the
  orbit sizes sum to exactly 384,668.
- **It finds what exists.** At n = 67 the complete census finds exactly **2**
  pancyclic classes out of 6,859 eligible — the external family Fₙ, and the
  class of the second graph Pinckard et al. found by a blind control run. The
  C code finds the same 44 labeled skeletons (2 classes × 22 labelings). A
  search that only ever said "no" would fail here, at n = 40 for 5 chords, and
  at every n ≤ 66 where our own 6-chord witnesses were found.
- **Independent oracles.** Cycle forms are compared with a plain DFS over the
  actual graph (250 random graphs per replay); the search verdict is compared
  with brute-force enumeration of every arc-length vector (400 instances per
  replay, both verdicts well represented; development runs compared 1,500 more).
  Skeleton counts per t are compared with an inclusion–exclusion formula,
  and k = 5 reproduces Robinfxa's published census (1,236 classes; 6, 222,
  1581, 4410, 5880, 3780, 945 labeled by t).
- **Planted failures.** Fₙ at n = 68 (missing only length 33) must be rejected;
  every committed witness with one chord deleted must be rejected; a chord
  equal to a cycle edge must be rejected.

For the k = 7 exclusion, which rests on `pancyc.c`:

- **The port is pinned to the reference.** At k = 6 its per-level eligible,
  pancyclic and node counts equal `RESULT.json` at all 45 levels, and its
  orbit-weighted eligible counts equal the labeled counts recorded by
  `xcheck.c`. At k = 7 the Python reference re-decides every eligible class at
  150 ≤ n ≤ 215 (222,323 class–level pairs) and must match each verdict
  and node count. Node-for-node agreement means the two programs took the
  same search tree, not merely the same verdict. Once, outside the contract
  replay (2026-09-27, `verify_k7.py --python-levels 115-115`, about 2.2
  CPU-hours), the Python reference also re-decided the boundary level n = 115
  that fixes t₇: all 151,157 classes, same verdicts, same 119,519,846 nodes.
- **Census.** 496,875 classes whose orbit sizes sum to 10,398,480, the
  inclusion–exclusion count of labeled 7-chord skeletons.
- **It finds what exists, up to the boundary.** At every 109 ≤ n ≤ 114 the
  engine finds a pancyclic class (G7 at 109–113, a second class at 114); each
  is realised and re-checked by DFS, and both classes are refuted at n = 115.
- **An independent program where it can reach.** `xcheck.c` (all labeled
  skeletons, DFS cycle enumeration, no memo) finds the same labeled skeletons
  eligible and none pancyclic at every level 140 ≤ n ≤ 215
  (`xcheck_k7_summary.txt`). It has no memo, so the boundary levels are out of
  its reach; there the exclusion rests on the port alone (see Scope).
- **Planted failures.** G7(n) at n = 114 (missing only length 61) and S8(n) at
  n = 187 (missing only length 108) must be rejected, as must every k = 7
  witness with one chord deleted and a receipt with one node count altered.

## Replay

From the repository root:

```sh
python3 -I certificates/erdos-1016/verify.py            # full, ~5 CPU-minutes, uses up to 4 processes
python3 -I certificates/erdos-1016/verify.py --with-c   # also builds and runs xcheck.c (slower)
```

The last line of a passing replay is a JSON verdict containing
`"t6":67` and `"verified":true`. `--quick` samples the heavy levels and says
so; it is for development, not certification.

The k = 7 extension (needs a C compiler; the binary is built in a temporary
directory):

```sh
python3 -I certificates/erdos-1016/verify_k7.py          # quick, about a minute: all checks except levels 115..149
python3 -I certificates/erdos-1016/verify_k7.py --full   # certifying, ~80 CPU-minutes over up to 4 processes
```

A passing `--full` replay ends with a verdict containing `"t7":114` and
`"verified":true`; the quick replay prints `"verified":false` by design.

| file | role |
|---|---|
| `pancyclic.py` | skeletons, cycle forms, the exact search, the DFS graph check |
| `verify.py` | the replay; reads the two JSON files, never writes them |
| `RESULT.json` | receipt: census, per-order verdicts and class counts, h(n), t_k |
| `witnesses.json` | one pancyclic chord set with exactly h(n) chords for each 3 ≤ n ≤ 108 |
| `emit_result.py` | regenerates the two JSON files into a *different* directory |
| `xcheck.c`, `xcheck_summary.txt` | the independent C implementation and its recorded output |
| `pancyc.c` | C port of `pancyclic.Search`; carries the k = 7 exhaustion |
| `k7lib.py` | builds and drives `pancyc.c`; the explicit families G7(n) and S8(n) |
| `verify_k7.py` | the k = 7 replay; reads its JSON files, never writes them |
| `RESULT_k7.json` | receipt: k = 7 census, positive controls 109..114, per-level exclusion 115..215, h(n) for 109..186 |
| `witnesses_k7.json` | pancyclic chord sets: 7 chords for 109 ≤ n ≤ 114, S8(n) for 115 ≤ n ≤ 186 |
| `emit_result_k7.py` | regenerates the two k = 7 JSON files into a *different* directory |
| `xcheck_k7_summary.txt` | `xcheck.c` output at k = 7 over its reachable levels |

## Scope — what is not certified

- **Not Erdős #1016.** A finite table cannot move the asymptotic question.
- **h(n) for n ≥ 187 is only bounded**: 8 ≤ h(n), and h(187) ≤ 9. t₈ is not
  determined: S8(n) stops at n = 187, a development search found no arc
  lengths on S8's skeleton at 187 ≤ n ≤ 190 (not packaged here), other 8-chord
  skeletons were not searched there, and an 8-chord exclusion was not
  attempted.
- **The k = 7 exclusion has one implementation at 116 ≤ n ≤ 139.** There it
  rests on `pancyc.c`, which is checked node for node against the Python
  reference at every k = 6 level and, class by class, at 150 ≤ n ≤ 215 for
  k = 7 in every full replay (and once at n = 115), but not at those levels
  themselves (about 8 CPU-hours in Python; `verify_k7.py --python-levels
  LO-HI` runs any range).
- **A verified-search receipt, not a formal proof.** Two independent programs
  agree, and the oracles above test them, but neither is formalised. The
  reduction and the exclusion rules are the ones Robinfxa formalised in Lean
  for (k, n) = (5, 41); this certificate does not rebuild that Lean project.
- **Freshness is bounded by what this session could reach.** On 2026-09-27
  the external repository's latest state (2026-09-24) still lists the thirteen
  levels as unfinished, the Justin Sun Prize catalogue (2026-09-24) lists the
  problem as open, and OEIS A105206 is unchanged; the erdosproblems.com forum
  and erdosproblemaday.com could not be read from here. "New" means new
  relative to those sources.
