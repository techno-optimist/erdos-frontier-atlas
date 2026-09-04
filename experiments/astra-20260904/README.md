# Astra research sortie — 2026-09-04

Local, unpromoted research attached to the Erdős frontier graph. Baseline atlas: `0394e3d3b249439ffabec7d96a3311aa441651b8`. No remote publication, production graph edit, frozen-certificate change, or claimed Erdős-problem solution.

## 1. Freshness: 16 informal status changes

The [full source audit](freshness.md) compares all **1,217** records against pinned upstream versions. The [machine-readable diff](upstream-diff.json) was independently fetched and checked a second time, not merely trusted from the research handoff.

| Current informal state | Problems changed since July 27 baseline |
|---|---|
| Disproved | 1, 74, 106, 146, 180, 193, 575 |
| Proved | 126, 548, 557, 571 |
| Solved | 183, 346, 421, 730, 1005 |

These are **catalog status changes**, not assertions that all discoveries happened after July 27. There are 99 raw status-string changes against the atlas; 83 do not change the underlying informal state. New formalization tags must not be counted as new mathematical solutions.

Particularly consequential: #1 is now disproved/formalized, #548 proved/formalized, and #183 solved. The live site credits Astra for #1 and #548. The site and YAML are not perfectly synchronized: #501 appears in the recent-changes list but still has an open status; #547's page says #548 implies it while its own status remains decidable. These discrepancies are retained, not silently repaired.

For our candidate targets: #993's discussion reports a 32-vertex exhaustive check and a two-branch-vertex theorem; neither was rebuilt locally. #743's published 1990 cutoff was already 11, so order 10 was not a fresh frontier. #699 and #366 remain open. See the audit for exact citations and caveats.

## 2. P699: an infinite near-central strip, not more enumeration

[Full proof and provenance](699-strip.md).

For $2\le i<j$, let $p_+(i)$ be the least prime strictly larger than $i$. We derived the following corollary of the accepted prime-power method and the 1978 EEES theorem:

$$n=2j+d,\quad1\le d\le p_+(i)-i
\quad\Longrightarrow\quad
\exists p\ge i:\ p\mid\gcd\!\left(\binom ni,\binom nj\right).$$

The useful refinement is localization modulo $p^{a+1}$ rather than $p^a$ when the boundary prime is $p=i$. This compresses all non-common prime powers into $\binom j{\lceil(i-d)/2\rceil}$; Vandermonde contradicts the classical large-prime bound. The 12 classical exceptions are explicitly handled. The odd-central case $n=2j+1$ is included.

**Scope:** informal proof using a published theorem, not Lean-formalized, not a full solution, no novelty claim. A [separate reasoning audit](699-independent-audit.md) found no gap in the p-adic/size argument, while explicitly leaving source and exception checks to the parent investigation; those checks were then supplied in the main proof.

`check_699_lemmas.py` replays 1,078,287 prime-power cases, 554,659 sharpened Euclidean divisibilities, 18,815 strip cases, all 41 admissible exceptional triples, and additional size checks. These counts overlap and must not be summed as distinct triples. A deliberately excessive prime power is rejected.

## 3. A genuine standalone checker defect

`audit_699_receipt.py` changes only a disposable copy of the existing receipt to report one counterexample, consistently in its shard and total. The original standalone checker still exits zero and prints `verified: true, counterexamples: 0`.

The script also tests a minimal zero-count guard: it rejects the corrupted receipt and accepts the original. [Actual transcript](699-audit-result.json).

This is a semantic verifier bug, **not evidence that the published sweep has a counterexample**. Repository-level hash gates were not tested in this mutation. The proposed fix runs in a temporary copy only; the frozen verifier is unchanged.

## 4. P993: branch topology is a useful next target

The exact tree-DP probe sampled **21,500 distinct trees**, with every branching vertex on a common path, at orders up to **415**: no log-concavity failures. This is a biased finite sample, not a theorem or an exhaustive cutoff. `RESULT.json` records the seed, batch sizes, observed order ranges, distinct counts, and a digest of every sampled parameter set and coefficient sequence. The sampling distributions are explicit in `probe.py`. The default invocation recomputes and byte-compares the receipt.

The independent-set counter was checked against direct subset enumeration on small trees. It catches the known 26-vertex non-log-concave tree. Four source/receipt corruptions were rejected in isolated copies; see `mutation-results.json`.

The known 26-vertex example has $(i_{12},i_{13},i_{14})=(2979,51,1)$: $i_{13}^2=2601<2979=i_{12}i_{14}$. Rewiring one core edge to put the branch vertices on a path restores log-concavity for this example. This is a topology control, not a theorem about all such rewiring; see `topology-control.json`.

A [separate three-hub Laurent-block lemma](993-block.md) is proved for all its stated parameters and checked by independent eight-state expansion. It is **not** a full three-hub tree theorem: the required global partition argument remains missing. The same note gives an obstruction to a naive recurrence proof via nonnegative mixed log-concavity defects.

## Replay

From this directory, Python standard library only:

```sh
python3 -I test_probe.py
python3 -I probe.py
python3 -I check_699_lemmas.py
python3 -I check_993_block.py
python3 -I audit_699_receipt.py --repo /path/to/erdos-frontier-atlas
```

The last command needs the baseline repository; the other checks are standalone. This deliberately wrong control **must exit nonzero**:

```sh
python3 -I check_699_lemmas.py --negative-control
```

At repository root, the existing graph validation passed, and:

```sh
uv run --python 3.11 --with-requirements requirements-dev.lock python -m pytest tests/ -q
```

returned **148 passed, 2 skipped**. These test results do not formalize the new mathematical arguments. No exhaustive $10^8$ sweep, 32-vertex tree enumeration, or external Lean build was rerun.

## Open obligations

- Obtain human mathematical review and check whether the explicit P699 strip was already known before any novelty claim.
- Integrate a P699 checker fix only through the repository's versioned/frozen-certificate policy.
- Refresh production graph statuses with the site's/YAML's inconsistencies explicitly handled.
- A full three-hub theorem needs a global combinatorial argument; the block lemma and sampling do not supply it.
