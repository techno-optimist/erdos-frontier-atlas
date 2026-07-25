# 5 · Methods — the field's instruments

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

The rule earned its keep by taking something away. The map's strongest bound
had been raised to class C1 on exactly that basis — a spec-only blind
reimplementation, a different algorithm, agreeing on a hundred windows out of a
hundred. In July 2026 it was **demoted back to C2**, because that second
implementation lives in a private repository: a reader could not run it, and a
class that counts evidence a stranger cannot execute is measuring our
confidence rather than the claim's. The bound itself was reduced to the range
the public certificate actually covers. **The ledger now contains no C1 entry at
all** — and that emptiness is the instrument working, not a hole in it. C1 is a
statement about independent replication; until the replication is publishable,
the honest column is C2.

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

Joining is one command deep. `make hello-frontier` replays a nonexistence
certificate, its negative control, and a witness verifier, then prints one
ledger entry with its computed class — the whole epistemology, demonstrated.
From there: verify any certificate, dispute any entry, prove any
conjecture-grade relation, or submit a witness to any record board. The map
is the field, and the field is open.
