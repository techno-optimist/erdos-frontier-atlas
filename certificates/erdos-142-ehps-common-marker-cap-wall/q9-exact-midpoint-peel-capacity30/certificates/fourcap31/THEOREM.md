# Normalized four-cap size-31 UNSAT certificate

## Exact statement

Let `G = Z_9^2`, and let `m(a,b) = (a+b)/2` in `G` for distinct points
`a,b`. A finite support is midpoint-peelable when its points admit a removal
order in which the point removed at each step is not the midpoint of two other
points still present.

There is no midpoint-peelable 31-point support whose nine fibres modulo 3 have
size 4 on

`{(1,0), (2,0), (0,1), (0,2)}`

and size 3 on each of the other five quotient points.

Equivalently, the normalized non-slab four-cap profile `4^4 3^5` is UNSAT.
This packet does not by itself assert `C9 = 30`: the universal fibre-cap lemma,
the slab reduction, the two direct slab UNSAT certificates, and a size-30 lower
witness are separate inputs to that final conclusion.

## Finite proof

Reverse a peel order. If the resulting insertion order has ranks `0,...,30`,
then every selected midpoint triple satisfies

`rank(m(a,b)) < max(rank(a), rank(b))`.

`generate_case2_core6_cnf.py` encodes exactly one selected transition at every
rank, exact size 31, the normalized `4^4 3^5` fibre profile, and every midpoint
rank inequality. It deterministically regenerates the frozen CNF:

- 11,203 variables;
- 131,681 clauses;
- 2,915,646 bytes;
- SHA-256
  `3d490be403585b03ddc30b7aff7445b4c4e9d3b7550e2e97077964b627a88108`.

The 108 local three-line clauses, 3,402 five-core clauses, and 2,916 six-core
clauses are redundant support blockers. The generator independently queue-peels
every five-core row and constructs and queue-validates every six-core, so their
addition cannot remove a peelable support.

The full lifted affine stabilizer of the normalized quotient four-cap has 5,832
elements. It has exactly three point orbits, represented by `(1,0)`, `(0,0)`,
and `(1,1)`, of sizes 36, 9, and 36. Thus the first removed point may be fixed
to one of those representatives. After fixing it, the second removed point is
split into all stabilizer orbits:

- saturated first point: stabilizer 162, 10 orbits with sizes
  `1,1,2,2,2,9,9,18,18,18`;
- centre first point: stabilizer 648, 4 orbits with sizes `4,4,36,36`;
- corner first point: stabilizer 162, 10 orbits with sizes
  `1,1,2,2,2,9,9,18,18,18`.

These 24 disjoint orbit cases cover all 80 choices of the second point in each
first-point case. `generate_orbit_cnfs.py` exhaustively reconstructs the group,
the orbit covers, and each case CNF. Each case has 11,203 variables and 131,685
clauses (the base plus four rank-fixing unit clauses).

Official CaDiCaL 3.0.1 produced a binary DRAT proof for every case. The pinned
solver-independent `drat-trim` checker returned `s VERIFIED` on all 24. The
proof traces total 265,645,848 bytes; the largest is 78,921,554 bytes. Their
exact CNF/proof sizes and SHA-256 digests are in `PROOF_PROVENANCE.json`.
Proof payloads and compiled binaries are external provenance and are
intentionally absent from this compact packet.

## Trust boundary and replay

The standard compact replay checks the closed package manifest, quotient
profile census, deterministic base-CNF bytes, exact affine orbit cover, all 24
regenerated case-CNF hashes, and nonmutation:

```text
python -I -B verify_all.py
```

This standard replay requires only Python 3. The generator contains a direct
standard-library implementation of the exact Knuth/Healy irredundant
sequential counter used to create the frozen CNF; it reproduces the bytes and
hash above on both Windows and Linux.

Given a directory containing the 24 pinned `.cnf` and `.drat` pairs and a
pinned checker binary, the theorem-grade proof replay is:

```text
python -I -B verify_all.py --external-proof-dir PATH --checker CHECKER --proof-jobs 4
```

That invocation hashes every external artifact before checking it and emits
`CONCLUSION_NORMALIZED_FOUR_CAP_SIZE31_UNSAT` only after all 24 checker runs
return exactly `s VERIFIED`.

`drat-trim-binary-windows.c` is the pinned upstream checker source with the
minimal Windows binary-I/O portability patch: proof files are opened as `rb`,
and `getc_unlocked` maps to `getc`. This patched native build independently
replayed the same 24 proofs. No compiled checker is shipped.

The nested `core_census_certificate` is a separately frozen, solver-free
structural certificate for deletion-minimal cores of sizes 6, 7, and 8. Its
manifest SHA-256 is
`b8f441d155a430e8052aee0cf1d0e8e76fa0dc291d7a5dab743726096864ca27`.
Its size-8 census is not needed by the 24 DRAT proofs; it is included as an
independent structural result and possible future compact-proof strengthening.

## Scope of `verify_profile_reduction.py`

Assuming the separately proved bound of at most four points per modulo-3 fibre,
the script exhausts all 1,278 size-31 fibre profiles. Exactly 1,224 contain a
line of three saturated fibres (the slab lane). The remaining 54 have profile
`4^4 3^5`; their four saturated quotient points are four-caps, and all 54 lie
in one `AGL(2,3)` orbit. This arithmetic census identifies the case certified
here but does not itself prove the fibre-cap lemma or settle the slab lane.
