# 3 · The Observatory

The observatory measures **emitted-proof sizes**: how large a machine-checkable
proof one *pinned pipeline* — encoding, solver version, configuration, seed,
all recorded — happens to emit for members of a parameterized formula family.
This is observational science, and its central discipline is knowing what the
instrument measures. An emitted size is an achievable upper bound on proof
length under that pipeline; it is **not** a minimal certificate, and the two
can diverge exponentially (the charter's cautionary exhibit: CDCL emits
exponential DRAT for pigeonhole formulas whose minimal DRAT certificates are
polynomial). Every number below carries that caveat structurally — it is
recorded in the data file itself, not appended by an editor.

The first family under observation is the upper half of `R(3,k)`: the CNF
statement that a 2-coloring of `K_n` at `n = R(3,k)` avoiding a red triangle
and a blue `K_k` exists, which is unsatisfiable — so each point is a
solver-emitted, independently checked DRAT refutation. Variance is measured
before trend: seeds within a pipeline, and two clause orders of the same
clause set, are separate axes, and a family trend would be meaningful only if
it dominated that spread. So far it is reported as ratios, not a law — the
honest no-fit posture is itself the result.

```efa:table observatory_curve
```

Two observations ride along with the curve. The small end is strangely rigid:
the `R(3,3)` refutation came out **byte-identical** across every seed, both
clause orders, and two independent sessions — at this scale the emitted proof
behaves like a canonical object of the pipeline, not an accident of search.
And the large end carries the instrument's own limits honestly: the third
seed of `R(3,5)` was aborted by the operator after gigabyte-scale proof
traffic twice destabilized the shared machine, and the abort — with its
reason — is part of the measurement record. An observatory that documents
its instrument is more credible than one that pretends it has none.
