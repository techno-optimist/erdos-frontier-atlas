# R(3,3) = 6, upper half — machine-checkable nonexistence certificate

**Claim.** Every 2-coloring of the edges of `K_6` contains a monochromatic triangle
(the upper-bound half of the Ramsey number `R(3,3) = 6`, the friends-and-strangers
theorem).

**Certificate.** [`problem.cnf`](problem.cnf) encodes "a 2-coloring of `K_6`'s 15
edges with no monochromatic triangle" as CNF (15 variables — one per edge, color =
polarity; two clauses per triangle, 40 clauses). It is UNSAT, and
[`proof.drat`](proof.drat) is a **247-byte** DRAT proof of that unsatisfiability,
independently checkable with the standard `drat-trim` checker:

```sh
# drat-trim is a single-file C program: github.com/marijnheule/drat-trim
drat-trim problem.cnf proof.drat        # expect the line: s VERIFIED
```

**Caution when scripting the check:** `drat-trim` can exit 0 on *both* verified and
not-verified outcomes — parse the `s VERIFIED` line, never the exit code. And match
the substring `s VERIFIED` rather than anchoring at line start: the checker's
progress output uses carriage returns, so the verdict may not begin a fresh line in
a pipe.

**Negative control.** [`truncated_negctl.drat`](truncated_negctl.drat) is the same
proof deliberately truncated; `drat-trim problem.cnf truncated_negctl.drat` must
report `s NOT VERIFIED`, demonstrating the checker can actually fail.

**Honest scope.**
- This is a *tiny, classical* result (provable by hand since 1930); its value here is
  as the smallest end-to-end exemplar of a certified-nonexistence pipeline
  (solver-emitted proof + independent checker + negative control) and as a first
  measured point for certificate-size observation.
- The 247 bytes are the size of the proof **emitted by one pinned solver run**
  (CaDiCaL 3.0.0, plain-text DRAT, default config) — an *achievable upper bound* on
  proof size under that pipeline, **not** a minimal certificate. Emitted sizes depend
  on the encoding, solver configuration, and format; any cross-family comparison must
  pin all of these.

**SHA-256.**
```
e146a9afcb7e9529f9863851236729bc033c044efa8cc55cfb9d43f24c50c632  problem.cnf
38a9c5b06f8f481134b27842d6d257a59a62ed242ad25639e2c81a6f10df536b  proof.drat
34dcb4b9b2e536a6faf144b271faa84d7f8e2486b7a41abfe0d9d937517a80eb  truncated_negctl.drat
```
