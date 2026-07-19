# R(3,4) = 9, upper half — machine-checkable nonexistence certificate

**Claim.** Every 2-coloring of the edges of `K_9` contains a red triangle or a
blue `K_4` (the upper-bound half of the Ramsey number `R(3,4) = 9`; classical,
Greenwood–Gleason 1955).

**Certificate.** [`problem.cnf`](problem.cnf) encodes "a 2-coloring of `K_9`'s
36 edges with no red triangle and no blue `K_4`" as CNF (36 variables — one per
edge, red = true; 84 red-triangle clauses + 126 blue-`K_4` clauses, 210
clauses). It was generated deterministically by
[`tools/gen_r3k_cnf.py`](../../tools/gen_r3k_cnf.py) (encoding `r3k-edge-cnf`
v1.0.0, no symmetry breaking):

```sh
python3 tools/gen_r3k_cnf.py 4 9 -o problem.cnf
```

It is UNSAT, and [`proof.drat`](proof.drat) is a **565,470-byte** plain-text
DRAT proof of that unsatisfiability, emitted by the pinned WS5 pipeline
([`observatory/pipeline.json`](../../observatory/pipeline.json)):

```sh
cadical --no-binary --seed=1 problem.cnf proof.drat   # CaDiCaL 3.0.0
drat-trim problem.cnf proof.drat                      # expect the line: s VERIFIED
```

**Caution when scripting the check:** `drat-trim` can exit 0 on *both* verified
and not-verified outcomes — parse the `s VERIFIED` line, never the exit code.
And match the substring `s VERIFIED` rather than anchoring at line start: the
checker's progress output uses carriage returns, so the verdict may not begin a
fresh line in a pipe.

**Negative control.** [`truncated_negctl.drat`](truncated_negctl.drat) is the
same proof deliberately truncated (the first 10,456 of its 17,427 lines, so the
derivation never reaches the empty clause);
`drat-trim problem.cnf truncated_negctl.drat` must report `s NOT VERIFIED`,
demonstrating the checker can actually fail.

**Honest scope.**
- This is a *tiny, classical* result; its value here is as the second measured
  family point of the WS5 certificate-size observatory
  ([`observatory/`](../../observatory/)) under the same pinned pipeline as the
  [`ramsey-3-3`](../ramsey-3-3/) exemplar.
- The 565,470 bytes are the size of the proof **emitted by one pinned solver
  run** (CaDiCaL 3.0.0, plain-text DRAT, default config, seed 1) — an
  *achievable upper bound* on proof size under that pipeline, **not** a minimal
  certificate. Unlike the seed-invariant `R(3,3)` point, this instance's
  emitted size varies with the seed: seeds 1/2/3 gave 565,470 / 574,869 /
  561,523 bytes (all verified; see
  [`observatory/measurements.json`](../../observatory/measurements.json)).

**SHA-256.**
```
7c46f311cdf3c35fe3839b38b12acaa906b540f25ff27d5299e337d95325caa0  problem.cnf
f2739bee8872178402d08fa056cfb52361aa5d5ba8a97ef718bcb5b0d2fe56c6  proof.drat
f85366205b67c127df1f70d2e49717c61e2e22c937182f3ba81b3835e729f540  truncated_negctl.drat
```
