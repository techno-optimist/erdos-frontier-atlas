# Hostile audit: fifteen-state Hamiltonian-chain residual

Date: 2026-08-19. Verdict: **APPROVE**.

This is a separate, read-only hostile audit of
`D:\p42_scratch\erdos142_q42_partial_fifteen_chain_frontier_20260819`.
No producer byte was edited. The producer manifest SHA-256 is

```text
f502b1ed111160e81d3bb7dcead77de113817a94c69a31d6e001862f23af5e75.
```

The producer replay and this independent replay pass on native Windows and
WSL. The prior full physical auditor was also rerun on both runtimes.

## 1. Feedback and total-red reduction

For the blue Hamiltonian chain, `A^15=0`, so with

```text
P=(I-A)^(-1), Q=PC, s=R/B=40/597,
```

the exact factorization

```text
I-A-sC=(I-A)(I-sQ)
```

and the nonnegative M-matrix criterion give

```text
rho(A+sC)>1 iff rho(Q)>597/40.
```

Row `i` of `Q` is the sum of the red-map rows at sources `i,...,14`.
If at most fourteen red transitions are defined, every row sum is at most
14, strictly below `597/40`; thus an above-threshold map is total.

For a total map, let `q` be the number of red targets different from zero.
For `q>=2`, the vector `(1,77/80,...,77/80)` gives row-zero bound

```text
13+2(77/80)=597/40
```

and every later row is at most `14 < (597/40)(77/80)`. The hostile replay
exhausts all 20,580 extremal `q=2` controls; larger `q` only decreases the
row-zero bound.

For `q=1` with exceptional target `j>=2`, use `z_0=1`, `z_j=37/40`, and
`z_i=560/597` otherwise. Row zero equals `597/40`, ordinary later rows are
at most `14=(597/40)(560/597)`, and row `j` is at most `15-j<=13`, strictly
below `(597/40)(37/40)`. All 195 source/target controls pass exactly.

These cases exhaust everything except reset and a single target-one anomaly.
No floating point or sampled spectral inference is used.

## 2. Characteristic factors and all critical maps

There are exactly sixteen remaining maps: reset, and one map for each source
`p` whose red target is one while all other red targets are zero. Reset has
feedback root 15. For the anomaly maps, `Q` has only columns zero and one
nonzero. Independently summing its trace and all principal two-minors gives

```text
p=0:  lambda^2-14 lambda-14,
p>0:  lambda^2-15 lambda+1.
```

At `lambda=597/40` these are respectively `-311/1600` and `-191/1600`.
The threshold is above each small root, so every large root is strictly above
threshold. This verifies both claimed characteristic polynomials and all
sixteen above-`B` maps.

## 3. Every ordered pair and explicit physical lift

The hostile replay does not import the producer. It follows seven labeled
copies through the explicit `B`, `R`, and `U_0` constructions for every

```text
16 maps * 15 starts * 15 targets = 3,600 ordered cases.
```

Every transition is defined, every endpoint is pure at the requested target,
every column red count is in `{0,1,7}`, and every witness has a unit-red
column. The maximum construction length is 19. The full length histogram is

```text
((1,1),(2,16),(3,226),(4,239),(5,240),(6,240),(7,240),
 (8,240),(9,240),(10,240),(11,240),(12,240),(13,240),
 (14,240),(15,239),(16,225),(17,225),(18,28),(19,1)).
```

Every abstract witness is then lifted for all seven choices of the red role:
25,200 distinct seven-word physical lifts and 26,775 unit-packet columns.
All PLAN midpoint residuals are divisible by 42, all seven cyclic carry
ledgers are printed by the replay, and the exact canonical raw costs are

```text
(16/7,22/7,20/7,24/7,22/7,18/7,18/7).
```

Aggregate witness raw cost ranges from `16/7` to `48/7` and is always
positive. The seven PLAN rows have zero total role incidence, so every
whole-word potential coefficient cancels. A unit column gives seven distinct
physical symbols, hence all seven physical words are distinct even when six
abstract color words coincide.

The hash-bound prior physical auditor was also rerun. It reconstructs all
17,640 support-disjoint packets, all 441 actual size-seven packets, all 3,087
cyclic red alignments, all 49 ordered modular midpoint rows per packet and
their carry ledgers, and positive raw cost in every alignment. Its SHA-256 is

```text
2a68daeab13b46452768a7e437118f596d2bc7d0687bf13b9f189a621f7425ca
```

and its terminal marker remains

```text
PASS_INDEPENDENT_SIX_SCOPE_AND_PHYSICAL_HOSTILE_REPLAY.
```

## 4. Live trim and exact combined scope

The frozen at-most-fourteen package is bound at manifest SHA-256

```text
e25f34d571ddeb3b7dedf99924a00b2f2511d90777962f01ebeda97f4ce1a5eb.
```

Its live-trim reduction is exact: unreachable and noncoaccessible states do
not affect the accepted language; a rate above `B` selects a live Perron SCC;
fixed common prefix and suffix words preserve the unit-red core. For SCC size
at most fourteen, the prior theorem applies. Its cyclic-blue exceptional-word
lemma is state-count independent, so it also handles a fifteen-state SCC with
a blue cycle. In the remaining acyclic case, maximum blue-tail length at most
14 is covered by `14R<B`. A tail of length 15 visits every state and forces,
up to relabeling, exactly the Hamiltonian chain audited here. Thus the
combination honestly closes this same color-homogeneous partial deterministic
wall through fifteen live states.

## 5. Scope, hygiene, and verdict

Approved scope is only the frozen one-red-per-packet q42 coloring,
color-homogeneous partial deterministic interfaces with at most fifteen live
states, fixed-start/nonempty-accepting accepted-language rate, arbitrary
ordered singleton SCC endpoints, and the existing physical packet lift.

Not proved: sixteen states; arbitrary same-count colorings; physical-symbol-
dependent or box-sensitive transitions; state carving; nondeterminism;
unbounded states; a physical potential from packet avoidance; a new
`r_3(N)` bound; or Erdős Problem 142.

Nonblocking packaging notes: the producer verbally depends on the m14 and
physical packages but does not hash-bind them locally; this audit binds them.
The producer directory contains an unsigned `probe_chain_product.exe` outside
its manifest. Neither producer run script uses it; both rebuild a temporary
binary from the signed C++ source. No theorem defect follows.

**APPROVE. No blocker found.**
