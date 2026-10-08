# OpenAI mathematics release: sources, connections and local proofs

This directory is a mathematical research overlay. It preserves a dated source
catalogue, explicit transfers and obstructions, and locally checked proof
components. It does not change the production atlas graph or problem statuses.
The [publication scope](SCOPE.md) and [current findings](CURRENT_FINDINGS.md)
separate external claims, local arguments, formal components and finite checks.

The **October 6 snapshot** at upstream commit
[`adc7f124`](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a)
contains **722 manuscripts in 372 families**, with 235 family-level Lean links.
These are historical catalogue counts, not verified theorem counts.
The [October 8 source update](upstream-update/README.md) compares
[`fd4aeeb2`](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb):
**719 manuscripts**, three withdrawals, 27 replacement editions and 11 new
formalization configurations. The original catalogue remains unchanged so its
source identities and mathematical crosswalk remain reproducible.

| To inspect | Start here | Evidence boundary |
| --- | --- | --- |
| The original release and source identities | [Catalogue](catalogue.json), [source ledger](sources.json), [upstream status](upstream-status.json) | Reported source statements; no blanket proof verification |
| Connections to existing problems | [133-edge analysis](CONNECTIONS.md), [typed graph](connections.json), [connection sources](connection-sources.json) | Conditions and failed transfers stay explicit |
| P699 cubic strip and infinite diagonals | [Arithmetic proof](research-sprint/arithmetic/README.md), [local algebra](research-sprint/density-transport/CUBIC_STRIP.md) | The number-theoretic reduction is informal; the algebraic component is Lean-checked |
| P699 rational-position gaps and higher-i constraints | [Next mathematical pass](research-next/README.md) | Explicit necessary conditions, not a full solution |
| Positional and weighted formal bridges | [Block bridge](research-next/formal-bridge/README.md), [weighted bridge](lead-phase/weighted-formal/README.md) | Explicit supplied block/factorization hypotheses; extraction remains separate |
| P841 transport of finite joint events | [Density transport](research-sprint/density-transport/README.md) | Checked implication from leakage and marginal hypotheses; arithmetic premises remain separate |
| P969 correlation obstruction | [Proof and exact finite example](research-sprint/correlation-barrier/README.md) | Pair cancellation alone does not imply the required window-energy bound |
| A selected external proof-source chain | [F003 source audit](research-sprint/source-audit/README.md) | Bounded source inspection, not a complete dependency audit or external build |
| Withdrawals and changed formalization scope | [Source update](upstream-update/README.md) | Metadata replay; no repaired argument or external Lean proof independently verified |

## Reproduce the mathematical overlay

From the repository root, using Python 3.10 or newer:

```sh
python3 -I -B experiments/openai-math-20261006/build_connections.py --check
python3 -I -B experiments/openai-math-20261006/check_evidence.py
python3 -I -B experiments/openai-math-20261006/check_evidence.py --replay-finite
```

The [evidence index](evidence-index.json) names each finding, its exact local
paths, receipt hashes and finite replay command. The default check validates
those joins and local Markdown links without downloading sources. Finite replay
checks the retained exact arithmetic examples and source-update metadata; it
is not a replacement for the proofs.

Local Lean components have their own toolchain and replay instructions. The
[weighted verifier](lead-phase/weighted-formal/README.md) rebuilds only pinned
local predecessors and rejects optimized Python before its assertion-based
gates. No external OpenAI solution or Comparator is run by the bundle checker.

## The next source question

F130 now has a separately reported **all-length exact DFT/convolution** result,
in addition to the original subsequential circuit statement. Its model allows
exact complex arithmetic, unrestricted coefficients and a supplied root of
unity. Audit the [selected source statement](upstream-update/raw/new-scope-130.md.txt),
its Comparator bindings and the charged operations before inferring a usable
finite-precision algorithm. Neither exact computation nor its operation count
supplies the missing P969 squarefree-variance or mixed-moment estimate.
