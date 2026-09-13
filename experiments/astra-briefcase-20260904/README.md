# The briefcase: proofs and obstructions transferred through the atlas

**Unpromoted research. No full Erdős problem solution, no formalization, and no novelty claim.**

This second sortie uses graph connections to transfer mathematical structure rather than treating shared tags as implications. It builds on the first Astra bundle in [PR #135](https://github.com/techno-optimist/erdos-frontier-atlas/pull/135). The production graph, status records, and frozen certificates are unchanged.

## What came out

| Route | Mathematical result | What it does not establish |
|---|---|---|
| `P993` / `S:triage:993` — weighted obstruction → ordinary trees | [Every non-path tree can occur as the exact induced branch-vertex graph of a tree whose independence polynomial is not log-concave.](transfer-theorem.md) The construction is explicit, with a proved eventual-sign argument. | Not non-unimodality. No converse for path cores. No priority claim. |
| `P699` / `S:triage:699` — adjacent binomial gcd | [The entire line **n=2j+2**, for all **2≤i<j**, has a common prime ≥i dividing both binomial coefficients.](699/result.md) The [prime-window completion](699/diagonal-completion.md) also covers n=2j+3 for **every even i≥2**. | Not the whole conjecture. The deductions use EEES and the first note's lifted localization; the diagonal completion also uses Nagura's prime-interval theorem. |
| `P993` / `S:triage:993` — positive-cone majorants | [The three-hub Laurent block is centrally unimodal for all integer r,s,t≥1 and real c,d,e≥1.](block/RESULT.md) | A complete block argument is not a global tree argument: the combinatorial partition, connector cases, and outside factors remain missing. |
| `P687` → `P854` / `S:gap:854:c322ba75` — shared A048670 family | [Exact endpoint-safe CRT counting and a wheel-transfer identity.](bridge/REPORT.md) At modulus 30030 a 22-gap exists but no 20-gap, disproving endpoint-oblivious witness transfer. | The endpoint-safe equivalence and wheel method have predecessors; no new spectrum cell or asymptotic result is claimed. |

## Inspect the obstruction compiler

Open **[briefcase.html](briefcase.html)**. Each selection is a real saved witness; browser `BigInt` recomputes its displayed determinant.

The compiler was exercised on **all 40 non-path unlabelled core trees through eight vertices**, using the atlas's existing free-tree generator. Every resulting failure was independently checked against the full decorated-tree polynomial. Output orders range from **38 to 194**. **All 40 full polynomials remain unimodal.** This is exhaustive only in the stated core list, not in all decorations or all trees of these orders.

For the claw core the construction at N=2 attaches (2,5,5,5) pendant P2 bundles, giving 38 vertices and

    a18 = 50721, a19 = 448, a20 = 4
    a19² − a18*a20 = −2180.

Vertex labels may permute the bundle vector. This is not a smallest-counterexample claim; the first bundle already contains the known 26-vertex control.

A separate compression demonstration computes **six leading coefficients of a 2,000,004-vertex tree**, exactly, without materializing it. This is a six-coefficient calculation, not a full-polynomial or full-tree enumeration. Its hexadecimal coefficient receipt avoids decimal serialization limits. Arithmetic operation counts can be small while integer bit complexity still grows.

## Replay

From the atlas root, with Python 3.9+ (tested locally using Python 3.11 for the locked repository suite):

```sh
python3 -I -B -m unittest discover -s experiments/astra-briefcase-20260904 -p 'test_*.py' -v
python3 -I experiments/astra-briefcase-20260904/verify.py
python3 -I experiments/astra-briefcase-20260904/699/check_shifted.py
python3 -I experiments/astra-briefcase-20260904/699/independent_check.py
python3 -I experiments/astra-briefcase-20260904/block/check.py --bound 24
python3 -I experiments/astra-briefcase-20260904/block/review_check.py
python3 -I experiments/astra-briefcase-20260904/bridge/check_bridge.py
```

Use `-I`, **not `-O`**: these research checkers intentionally use assertions. `verify.py` recomputes the full core list, compiler outputs, full-polynomial checks, and million-vertex tail receipt. It also uses the existing `certificates/erdos-993/freetrees.py` and `experiments/astra-20260904/probe.py` as independent oracles. It does not overwrite evidence. The CRT checker was changed from its exploratory emitter into a read-only receipt checker and is tested against a poisoned count.

The P699 negative control must exit nonzero:

```sh
python3 -I experiments/astra-briefcase-20260904/699/check_shifted.py --negative-control
```

It asserts the deliberately false strengthening “5 divides C(9,2)” from the actual wrap example (n,i,j)=(18,4,8). The valid proof needs a **gcd size bound**, not that false divisibility.

### Counts and their meaning

- P699: 19,411 d=2 triples; 9,512 even-i d=3 probes, of which 9,483 exercise the original non-diagonal gcd domain; 54 large-j/small-degree inequality samples; all five admissible EEES exception triples across the two claims. These check implementation and exceptions, not the all-parameter proof.
- Block: 13,824 unit-scalar blocks; 16 single-P, 15 double-P, and 20 small-block boundary cases; independent active-state and shifted-expansion checks. The unbounded proof reduces to those finite boundaries; the larger sweep alone proves nothing unbounded.
- CRT: 150 DP-versus-period cells, 60 inclusion–exclusion checks, 25 wheel-recurrence coefficients, and an endpoint mutation rejected by the same gap verifier.

## Review and status

[The independent transfer-theorem audit](transfer-audit.md) found no gap and checked its limiting normalization using a separate full-tree DP. The P699 deductions, diagonal completion, and general block each have separate mathematical reviews beside their proofs. These are informal audits, not formal verification.

The [final independent code review](reviews/final-code-review.json) found no security or logic issues in the 12 reviewed code files. Local replay passed **18 unit tests**, including poisoned receipts and malformed proof-table controls, and all seven replay commands above. [Full replay output](reviews/replay.log) and [repository audit output](reviews/repository-audit.log) are preserved. The locked Python 3.11 `make audit-fast` passed, including all 15 fast certificate contracts and **148 repository tests, 2 skipped**. The deliberately false shifted-integrality control exited 1 with its intended assertion.

[MANIFEST.json](MANIFEST.json) pins the packaged files and the two external code oracles. It is an integrity inventory, not a proof of the unbounded mathematical claims.

No new upstream status is promoted. The bridge lane checked the live P854 claim page and found an **unaccepted** partial claim; the accepted status must not be inferred from a manuscript or a shared sequence identifier. See its [source ledger](bridge/sources.json) and [cited report](bridge/REPORT.md).

This directory is a research workbench, not an Erdős prize claim.
