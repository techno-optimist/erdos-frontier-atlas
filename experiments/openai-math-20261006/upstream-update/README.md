# OpenAI mathematics source update — October 8, 2026

The original October 6 catalogue and graph remain historical snapshots. This addendum compares their pinned commit [`adc7f124…`](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a) with [`fd4aeeb2…`](https://github.com/openai/math/commit/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb), committed **October 8, 05:20 UTC**. Upstream groups the changes under **October 7** in its [history](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/history.md); the individual withdrawal notices say **October 6**. These are distinct source dates.

The update withdraws three manuscripts, publishes 27 replacement editions and adds 11 formalization configurations. It also adds an all-length exact-arithmetic statement to the F130 scope. No Lean proof or Comparator was run here; the changes do not promote any atlas problem status.

| Metadata | October 6 snapshot | New pinned snapshot |
| --- | ---: | ---: |
| Result families | 372 | 372 |
| Catalogue manuscripts | 722 | 719 |
| Families with a catalogue Lean link | 235 | 242 |

The counts are independently extracted from both retained manuscript maps. A family link is not complete coverage of its papers or local proof verification. The publisher separately reports 300 of 719 top-line results formalized; that uses a different denominator from family links.

## Withdrawals and corrected editions

All three withdrawals belong to **F032**:

- [Algebraicity of Weil classes on split abelian eightfolds](raw/withdrawal-1.md.txt).
- [Algebraicity of Kuga–Satake Correspondences for K3 Surfaces](raw/withdrawal-2.md.txt).
- [The rational Hodge conjecture for products of K3 surfaces](raw/withdrawal-3.md.txt).

The notices identify a sign error in the stabilization-trace construction and the dependent proofs. The withdrawal leaves these claimed results unproved by those manuscripts; it does not establish that the mathematical statements are false. F032's current catalogue title is narrowed to the rational Hodge conjecture for CM abelian varieties. Do not transfer the withdrawal to every remaining paper in that family.

The publisher describes **14 corrected/revised manuscripts**, including proof repairs, statement/hypothesis changes and one obsolete-citation correction. These cover Lipschitz heights/Ashkin–Teller currents, Kähler minimal models/abundance, taming/hypersymplectic deformation, incompressible box transport and the low-Selmer-corank BSD introduction. Another **13 editions update companion references and version dates**. [update.json](update.json) pairs every old and new manuscript path by its unchanged title within its family and records this publisher classification. It does not independently adjudicate the repaired arguments.

The retained, nontruncated Git directory trees independently account for 27 added edition directories and exactly three modified withdrawn-paper directories. The other 719 old manuscript directories retain their exact Git tree identity. This preserves earlier versions; it is not evidence of their correctness. The GitHub compare endpoint's capped file list was not used as a complete inventory.

## Formalization and local graph impact

Six new configurations concern additional main results: F049, F075, F103, F130, F137 and F157. The new [Comparator README](raw/comparator-readme.md.txt) explicitly distinguishes five **supporting-result-only** additions: F027, F066, F195, F237 and F301. Their appearance does not certify their papers' complete main theorems. [update.json](update.json) retains the exact configuration names, family mapping and this distinction.

The union of changed catalogue families and formalization additions intersects the [historical connection graph](../connections.json) at exactly three edges:

| Historical edge | Current reading |
| --- | --- |
| `analytic-audit-18`: F075 → P996 | Still a blocked transfer. Fourier convergence does not itself supply the required operator-specific maximal estimate for dilated averages. |
| `combinatorics-58`: F103 → P78 | Still a blocked transfer. An appropriate log-space construction/search reduction and the Ramsey guarantees remain separate. |
| `combinatorics-57`: F130 → P969 | Still a blocked transfer, with an updated source premise. The new scope separately reports an all-length exact DFT/convolution construction in ideal complex arithmetic. The old graph's all-length absence is superseded at that source-statement level. Finite-precision/error control and the squarefree-variance or mixed-moment analytic bridge remain unestablished. |

The F130 qualification is supported by the retained [old](raw/old-scope-130.md.txt) and [new](raw/new-scope-130.md.txt) scope documents. The new statement allows unrestricted exact complex coefficients and a supplied root of unity; it does not establish a practical finite-precision implementation. The original subsequential statement also remains in the new scope. These are reported source statements, not locally checked formal results.

F032 has **no node or edge in this graph**. The old [catalogue](../catalogue.json) and [number-theory abstract review](../swarm/number-theory.json) do retain the now-withdrawn K3-products claim. They must be read with this notice as historical reports. None of these historical files, graph edges, manifests or receipts was rewritten.

## Retained evidence and replay

[sources.json](sources.json) gives exact public URLs, retrieval time, lengths and SHA-256 identities for the metadata, notices and Git tree responses. [update.json](update.json) records derived differences and affected-edge annotations. [manifest.json](manifest.json) pins this mathematical metadata packet. Fetched Markdown is stored byte-for-byte as `.md.txt` data because its links use upstream paths. Upstream metadata is retained under its [Apache-2.0 license](raw/LICENSE); only public mathematical source metadata and notices are included.

```sh
python3 -I -B experiments/openai-math-20261006/upstream-update/verify.py --check
python3 -I -B -O experiments/openai-math-20261006/upstream-update/verify.py --check
```

Replay reads retained files only: source hashes, complete directory comparisons, exact catalogue counts and edition pairs, formalization configuration additions, historical artifact pins and graph overlap. It performs no downloads, proof builds or status changes. A later upstream revision requires another dated comparison; this packet is not a live feed.
