# Method substrate

The attack graph says where to strike. This ledger says **what reusable lemma to try next**, on this problem and on the others that share its shape.

It does **not** edit `atlas/graph/`, `views/graph/`, or `tools/build_graph.py` (those belong to the attack-graph lane). It does **not** set a status.

## Commands

From the atlas root:

```sh
python3 tools/query_substrate.py methods
python3 tools/query_substrate.py for 699
python3 tools/query_substrate.py for 854
python3 tools/query_substrate.py for 993
python3 tools/query_substrate.py open
python3 -I experiments/astra-substrate-20260911/verify.py
```

`for N` always reads the live attack graph for OEIS families, then overlays kernel-checked or reviewed methods. `open` walks all 1,217 stubs and lists every open/movable hit.

A **CANDIDATE** row is a tag or OEIS shape match. It is not a theorem about that problem.

## What is in the toolbox

| Method | Status | Proved on | Shape match |
|---|---|---|---|
| adjacent-binomial-gcd | kernel_checked | #699 wrap | binomial coefficients |
| coprime-divisor-transfer | kernel_checked | #699 wrap | binomial coefficients |
| i2-d3-divisor | kernel_checked | #699 i=2, n=2j+3 | binomial coefficients |
| p699-d2-line | informal_reviewed | #699 n=2j+2 | binomial coefficients |
| prime-window | informal_reviewed | #699 even-i d=3 | binomial+primes |
| crt-endpoint-safe | informal_reviewed | #687, #854 | A048670 / A389839 |
| wheel-gap-operator | informal_reviewed | #687, #854 | A048670 / A389839 |
| nonpath-lc-obstruction | informal_reviewed | #993 (not unimodality) | #993 only |
| laurent-hub-block | informal_reviewed | #993 block only | #993 only |
| tail-compression | informal_reviewed | #993 tails | #993 only |

The committed board is [BOARD.md](BOARD.md). `verify.py` regenerates it and compares.

## Trust

Kernel-checked methods still leave EEES, localization, and the rest of #699 unformalized. Informal methods are reviewed Python/proofs, not Lean. Candidate matches exist so the next agent does not have to rediscover the toolbox from chat history.
