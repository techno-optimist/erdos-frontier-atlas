# Direct size-31 slab order-CNF certificates

## Exact claim

Let `S` be a 31-point subset of `(Z/9Z)^2`.  Suppose every mod-3 fibre of
`S` has size at most four and, after an affine midpoint automorphism, `S`
contains either of the two frozen 12-point saturated-slab representatives
`T0` or `T1` in `search_unary_rank_sat.py`.  Then `S` is not peelable.

This is a direct statement.  The two `*_direct_unary31.cnf` instances use no
allowed-point list and no conditional blocker ledger.  They depend only on
the fixed slab, size/fibre cardinalities, and all physical midpoint rows.

The fibre bound loses nothing for a peelable set: peelability is hereditary,
and a single mod-3 fibre is an affine copy of `(Z/3Z)^2`, whose peelable
capacity is four (a transparent 512-subset check suffices).

## Encoding

For every physical point `v` and boundary `t=0,...,31`, the Boolean variable
`q[v,t]` says that `v` was inserted before boundary `t`.  The clauses set
`q[v,0]=false` and make each row monotone.  Selection is `q[v,31]`, and an
exact sequential counter selects 31 points.

For each of the 3,240 unordered pairs of distinct physical points `a,b` (all
6,480 ordered endpoint directions, quotiented only by the symmetry in `a,b`), let
`m=(a+b)/2 mod 9`.  For every `t=0,...,30` the CNF contains

```
q[m,t] OR -q[m,t+1] OR -q[a,t+1] OR -q[b,t+1].
```

If selected `m` transitions at `t`, the clause says that two selected
endpoints cannot both have transitioned by `t+1`; at least one has strictly
larger rank.  Thus all ordered physical midpoint rows are present.  Conversely
any reverse-add order assigns the 31 selected points transition ranks
`0,...,30` and satisfies the clauses.  The CNF is therefore satisfiable if
and only if a size-31 peelable extension of the fixed slab exists.

Both direct instances have 5,872 variables and 109,614 clauses.  The solver
artifacts are:

| case | CNF SHA-256 | proof bytes | proof SHA-256 |
|---|---|---:|---|
| T0 | `5f5b635ac07727751368bb766b91bacc9524f4c4818b95254e53bb62e03b0c15` | 1,328,969,194 | `9f5bcc00a49243325d2ad1726feb03a173ce578b5dbec1e3e11b88653de759a5` |
| T1 | `54f931b253189be9b921fb83c1c1bdefffe425c1f340ff73fd2dcda8e2a3d8e8` | 803,141,910 | `b90e04b56b4deae08785f10ac903aa3ac1ad2ec6d1113a23a2d7268e1ced2322` |

Official CaDiCaL 3.0.1 at commit
`c60730422e758ef1cebe7aeddf2dda31c996bf04` emitted both binary DRAT files
and returned exit 20.
For T1, independently compiled native-Windows and Linux `drat-trim` builds
both read all 803,141,910 bytes and identically reported:

```
52472 of 109614 clauses in core
5063741 of 10636505 lemmas in core using 283260141 resolution steps
0 RAT lemmas in core
s VERIFIED
```

For T0, both checkers read all 1,328,969,194 bytes and identically reported:

```
53338 of 109614 clauses in core
8967833 of 17335854 lemmas in core using 496922885 resolution steps
0 RAT lemmas in core
s VERIFIED
```

The Linux verification time was 2,286.464 seconds.  The native checker exited
zero and printed the same byte count, census, and `s VERIFIED`; only its final
time field overflowed the upstream checker's 32-bit Windows `clock()` counter
and displayed a negative number.  This is a reporting-only overflow after the
completed verification, not a proof or exit-status discrepancy.

## Replay and checker provenance

`verify_direct_cnf.py` byte-regenerates both CNFs using PySAT 1.9.dev7's public
`CardEnc` sequential-counter API, independently reconstructs all geometry,
and exhausts the 512 subsets of one mod-3 fibre.  The standard-library-only
`verify_direct_structure_stdlib.py` separately checks the physical rank and
midpoint clause blocks, counter variable scopes, both templates, and the same
fibre census.  It is the semantic replay used by WSL, where PySAT need not be
installed.

Run the short native and WSL layers with:

```
powershell -ExecutionPolicy Bypass -File .\run_direct_native.ps1 -SkipProof
bash ./run_direct_wsl.sh --skip-proof
```

Omit the skip flag for a full DRAT replay.  `checker/drat-trim.c` is official
`drat-trim` commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` source.  The native binary was compiled with
`fopen_binary_shim.h`, which changes read-only `fopen(...,"r")` calls to
`"rb"`; otherwise the Windows CRT treats a binary-proof byte `0x1a` as EOF.
No checking logic is changed.  Rebuild it with:

```
gcc -include .\fopen_binary_shim.h .\checker\drat-trim.c -std=c99 -O2 -Dgetc_unlocked=getc -o .\drat-trim-binary-windows.exe
```

## Scope

These certificates close the saturated-quotient-line branch only.  They do
not address the remaining normalized branch with four saturated quotient
fibres forming an affine 4-cap and five fibres of size three.  Consequently
they do not by themselves prove `C9=30`.
