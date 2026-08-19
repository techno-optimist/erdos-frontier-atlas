# Independent hostile replay for the compact q9 certificate

This is a self-contained, implementation-diverse replay of the finite claim

```text
30 <= C_9 <= 31.
```

It carries only two transparent blocker ledgers, standard-library Python, and
one C++14 source file.  It contains no CNF, SAT solver, DRAT trace, proof
checker, compiled binary, cache, network dependency, or absolute source path.

Requirements are Python 3 and a GCC-compatible C++14 compiler named `g++`,
`clang++`, or `c++`.  Run:

```text
python -I -B independent_replay.py
```

On Unix-like systems `./run.sh` is equivalent; on PowerShell use `./run.ps1`.
Compilation occurs only in a system temporary directory.  The replay checks a
closed SHA-256 manifest before and after execution.

The independent replay:

- parses both ledgers with a strict canonical grammar and recomputes every
  blocker core and every one-point minimality deletion using a fixed-point
  implementation different from the producer packet;
- verifies the exact 30-point reverse-add order and strict-potential ledger;
- independently enumerates all 157,464 saturated slabs and reconstructs the
  two affine orbits of size 2,916;
- compiles a separately written, profile-free fibre-cover search.  It builds
  local domains directly from the midpoint geometry, uses alternate symmetry-
  tied fibre orders, and traverses one joint target-size tree rather than the
  producer's 126 profile-root searches;
- checks the q9 Fubini normalization and exact h=8 gap arithmetic with rational
  arithmetic.

Expected independent target-20 fingerprints are 1,624,151 recursion nodes for
template0 and 1,192,358 for template1, both UNSAT.  The target-19 outputs are
controls for the relaxed listed-blocker master only.  They are not peelable
31-point witnesses; their template unions have residual cores of sizes 28 and
31.  These are different controls from the producer traversal.  The replay
also decodes the producer's masks against the identical allowed-point ordering
and confirms its corresponding residual sizes 27 and 31.

See `HOSTILE_AUDIT.md` for the proof decomposition, source binding, and scope.
