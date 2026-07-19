# 1 · The Map

The unit of progress in this practice is not the theorem and not the paper —
it is the **bracket**. Knowledge state is a versioned ledger of `[L, U]` gaps
on bounded quantities of open problems, and a result is a monotone movement of
that ledger: a lower bound raised by a witness, an upper bound lowered by a
nonexistence certificate, a verified-up-to-N frontier pushed outward. Improving
a bound is a first-class result, not a consolation prize (charter Tenet 2).

The gap map is that ledger. Each entry records the bracket, its sources, what
a machine-verifiable witness would be, how feasible one is, and an `evidence[]`
block from which the entry's confidence class is *computed* — never asserted.
Most entries are agent-mined and honestly labeled as such: structurally
validated, literature-grade, class C3 until an in-project verification
artifact exists. The map does not pretend its own entries are verified; the
labeling *is* the release gate.

```efa:table gap_map_summary
```

Movements against this ledger are recorded on the Frontier Board — the done-work
record, tiered by verification, with corrected claims kept in place so no one
re-walks them:

```efa:table board
```

The board is not only a record — it is an invitation. Every row's certificate
replays on a stranger's machine, and a movement that passes a pinned verifier
belongs to whoever produced it. Disputes are welcome; Tenet 5 guarantees a
correction stays visible longer than the claim it corrects.
