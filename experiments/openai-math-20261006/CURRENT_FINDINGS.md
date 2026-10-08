# Current mathematical findings and evidence levels

This is the reading guide to the [mathematical source package](README.md).
The [evidence index](evidence-index.json) records replayable paths and hashes.
External assertions, local deductions and executed proof components are
separate evidence levels. Canonical atlas statuses are unchanged.

## Source freshness

The retained October 6 catalogue has 722 manuscripts in 372 families at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
The [dated upstream comparison](upstream-update/README.md) records the later
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` snapshot: 719 manuscripts,
three F032 withdrawals, 14 corrected/revised manuscripts, 13 companion
reference/version updates and 11 added formalization configurations.
The notices withdraw proofs, not the truth of the underlying statements.
Publisher counts and formalization labels are not local proof verdicts.

The updated F130 scope separately reports all-length exact DFT/convolution in
ideal complex arithmetic. This supersedes the historical graph's all-length
absence only at the source-statement level. Numerical precision, error control
and the P969 analytic bridge remain unestablished. The original graph is retained;
[dated edge annotations](upstream-update/update.json) identify this qualification.

## Results by evidence level

| Level | Result | Scope and unresolved obligation |
| --- | --- | --- |
| External claim / source trace | [Release catalogue](catalogue.json) and [source ledger](sources.json) | Source inventory and selected scope checks; no blanket acceptance of external proofs |
| Conditional deduction | [133 mathematical connections](CONNECTIONS.md) | Every edge distinguishes hypotheses, compatible objects and blocked transfers |
| Local informal proof | [P699 cubic strip and eight infinite diagonals](research-sprint/arithmetic/README.md) | In the remaining i=3 branch, d=n−2j≥4 implies d³≥2n²+(d−2)(3n−2)>2n²; not a full solution |
| Formal component | [Cubic-strip algebra](research-sprint/density-transport/CUBIC_STRIP.md) and [seven-diagonal algebra](research-sprint/arithmetic-checks/README.md) | Recorded local Lean builds from explicit algebraic hypotheses; Kummer localization is not formalized here |
| Local informal proof | [P699 rational-position exclusions](research-next/arithmetic/README.md) | Exact gap near j=n/3 and eventual square-root-width gaps near fixed rationals in (0,1/2); no optimality claim |
| Local informal proof | [Higher-i small-prime defect](research-next/structural/README.md) | Explicit weighted central constraint; does not improve the older density-one theorem |
| Formal component | [Positional block bridge](research-next/formal-bridge/README.md) | Sixteen declarations construct the cubic divisibility and strip from supplied finite blocks; deriving them from binomial failure remains informal |
| Formal component | [Weighted P699 bridge](lead-phase/weighted-formal/README.md) | Thirteen algebraic declarations and two controls restore the small-prime factor and derive the weighted strip; factorization and extraction obligations remain |
| Formal component | [P841 joint-event density transport](research-sprint/density-transport/README.md) | Thirteen declarations give finite and asymptotic transport under explicit leakage and marginal hypotheses; the arithmetic/Dickman inputs are separate |
| Local informal proof | [P969 pair-correlation barrier](research-sprint/correlation-barrier/README.md) | A bounded nonmultiplicative sequence has strong pair cancellation but unbounded normalized polynomial-window energy; it is not a counterexample to a multiplicative conjecture |
| Finite evidence | [Arithmetic](research-sprint/arithmetic/receipt.json), [window](research-sprint/correlation-barrier/receipt.json), [rational](research-next/arithmetic/receipt.json) and [higher-i](research-next/structural/receipt.json) checks | Exact bounded controls corroborate only their tested finite assertions; infinite claims rest on proofs |
| Source trace | [F003 selected Lean chain](research-sprint/source-audit/README.md) | A 2,000-module source prefix was scanned and 84 modules remain on its frontier; no complete external dependency build or Comparator run |
| Source trace | [Upstream corrections](upstream-update/README.md) | Retained catalogue/notice/Git-tree bytes establish changes and source scope, not validity of corrected proofs |

Separate agent reviews are recorded where available. They are not human
acceptance or a substitute for the stated proof and replay boundary.

## Remaining mathematical work

- **P699:** formalize extraction of the positional blocks and small-prime factor
  from the binomial-gcd failure. Existing local algebra starts after that
  interface. The residual problem beyond the proved exclusions stays open.
- **P841:** establish the arithmetic leakage, exceptional-set and joint-law
  hypotheses needed to apply the checked transport theorem. Marginal limits
  alone do not discharge them.
- **P969:** obtain the operator-specific window-energy or signed mixed-moment
  estimate. Pairwise cancellation or faster exact transforms alone do not imply it.
- **F003 and F130 source verification:** retain distinctions among prose,
  Comparator challenge, selected declaration, full dependency build and audited
  axioms. A source prefix or scope note is not a completed proof audit.

The [research-sprint result ledger](research-sprint/results.json) and
[research-next result ledger](research-next/results.json) preserve original
proof-component receipts. The weighted bridge has its own
[execution record](lead-phase/weighted-formal/execution.json). The production
atlas graph, certificates, method registry and problem-status ledgers are
outside this overlay and remain unchanged.
