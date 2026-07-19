# 5 · Methods — the field's instruments

<!-- DRAFT: lead pass pending -->

The unit of knowledge is the **certificate**: a claim exists when a stranger's
machine can verify it from the artifact alone — witness plus dependency-free
checker, solver-emitted DRAT proof replayed through an independent checker
(parse the `s VERIFIED` line, never the exit code, and ship a truncated-proof
negative control that must fail), a replayable enumeration receipt, or a formal
proof. No trust, no authority. Every certificate in this repository ships its
own verifier and replay command; `make hello-frontier` walks a stranger
through the loop end-to-end.

On top of certificates sits the **epistemic ledger**: every map entry carries
recorded evidence, and a mechanical rule computes its confidence class from
that evidence — the validator fails any stored class the artifacts do not
prove. Replication counts only when it is *evidence, not echo*: two
implementations are independent when the second is blind-reimplemented from
the spec alone, on different algorithms, and cross-checked against the first
only after both have run. An echo of the same code path replicates nothing.

```efa:table confidence_ledger
```

The remaining instruments are refusals. The **freshness gate**: no claim of
"new" ships before a survey-literature check — this project's one retraction
was caught by its own gate, and the retracted row stays on the board. The
**quarantine rule**: evidence is never deleted and history is never
force-pushed; a corrected claim is quarantined with a reason, visibly, so the
next agent does not re-walk it. And the **no-fit posture**: below the charter's
minimum family points, or with a variance axis unmeasured, a curve is reported
as points and ratios — declining to claim is an instrument, not a weakness.
