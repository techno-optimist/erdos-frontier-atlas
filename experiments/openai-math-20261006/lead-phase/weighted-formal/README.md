# A checked weighted bridge for P699

Graph attachment: `P699`, `S:triage:699`. The weighted algebraic gap in the
[higher-i smooth-defect argument](../../research-next/structural/README.md)
is now Lean-checked. This is an unbounded theorem from explicit finite
positional blocks, with the factorization and coprimality data supplied as
hypotheses. It is not a formal proof of the binomial localization, construction
of those blocks, or full P699.

## What the main theorem says

Let `n = gv`, `j = gu`, `d = n−2j`, where `n ≥ 3`, `g > 0`,
`0 < j < n/2`, and `4 | n`. Put `P = (n−1)(n−2)` and
`Q = u(v−u)(v−2u)`. Given integers `A ≥ 1`, `B`, and `C`, assume

```
B | u(v−u),       C | 4Q,
gcd(C,4) = gcd(B,C) = gcd(2,BC) = 1,
P = 2ABC,        d ≥ 4A.
```

The checked conclusion is

```
A d³ ≥ 2n² + (Ad−2)(3n−2) > 2n²,
Ad > 4g³.
```

`WeightedFormal.strip_from_products` supplies this theorem directly.
`strip_from_blocks` first derives the product divisibility from two finite
lists of explicit positional blocks, using the pinned
[earlier formal bridge](../../research-next/formal-bridge/README.md).
Within each list, a block is coprime to the product of later blocks. Blocks
at position `t` divide `n−t` and have a residue `0 ≤ r ≤ t` for `j`.
The coprimality of the two list products follows from their divisibility
into consecutive integers. No abstract quotient, cubic identity, or nonzero
parity condition is left as an assumption in these main theorems.

All quantities use Lean integers with explicit positivity and normalization
conditions, avoiding truncated natural subtraction. The theorem even permits
normalizations other than the gcd: the application may supply `g = gcd(n,j)`.
The finite checks use that actual gcd.

For `4 | d`, `four_strip_from_weighted` additionally gives

```
A d³ ≥ 4n² + (Ad−4)(3n−2).
```

Its input weighted divisor follows from `restore_weighted` and the same
product data. The generic `quotient_bound` also transports any supplied
lower bound on the magnitude of the negative quotient.

## Why the proof closes

Oddness and coprimality give `2BC | Q`, hence **`P | AQ`**. Positivity yields
an integer `k ≥ 1` with `AQ = kP`. The normalization then gives, without a
further assumption,

```
m = 4g³k−Ad,
mP = Ad(3n−d²−2).
```

For `F = P−Ad(3n−d²−2)`, the following exact identity makes the threshold
transparent:

```
4F = (2n−3Ad−3)² + 4Ad²(d−4A)
     + 7(Ad−4)² + 46(Ad−4) + 71.
```

Every term is nonnegative when `A ≥ 1` and `d ≥ 4A`, and the constant is
positive. Thus `m < 1`. The row parity excludes `m = 0`; `m` is even, so
`m ≤ −2`. Substitution gives the bound and its strict positive margin.
If `4 | d`, the same argument gives `m ≤ −4`.

## Controls and proof scope

The exact input `(n,j,A,B,C) = (16,7,15,1,7)` satisfies the product
conditions and normalization. It has `Q = 126`, `P = 210`, `k = 9`,
`d = 2`, and `m = 6`. Therefore:

- omitting `A` from the divisor is false (`210` does not divide `126`);
- omitting the threshold allows a positive quotient;
- this does not show the constant `4` in the threshold is optimal.

The second control `(n,d,A,m) = (6,4,1,0)` satisfies the weighted identity
and threshold but fails row parity and the strict coefficient-two bound.
These are algebraic controls, not counterexamples to P699. Two control
theorems check their numerical content, and three deliberately false Lean
files must be rejected by `decide`.

There are **13 algebraic theorems and two numerical control theorems** in
[WeightedFormal.lean](WeightedFormal.lean). Their audited dependencies are
limited to Lean's standard `propext`, `Classical.choice`, and `Quot.sound`
(some use fewer). There are no proof holes or custom axioms. The verifier
rebuilds both pinned predecessor sources into its own ignored `.build/`;
old proof files and receipts remain unchanged. No external OpenAI proof
or Lake configuration is executed.

The remaining formal interface is explicit: binomial valuations must supply
the retained prime-power blocks and the small-prime factor `A`. This module
does not formalize that extraction, nor the separate `d = 0,2` boundary
arguments. No canonical problem status or novelty claim changes.

## Replay

Use an official Lean 4.33.1 executable:

```sh
python3 -I experiments/openai-math-20261006/lead-phase/weighted-formal/verify.py \
  --lean /path/to/lean-4.33.1/bin/lean
```

The command checks [execution.json](execution.json), source hashes, all 15
axiom audits, and the three false-theorem rejections. Only ignored build
outputs are written. `--record` is the explicit command for recording a new
receipt after a reviewed source change. Paths in the receipt are relative
to the bundle or the documented command working directory; binary hashes
record this build, while source and proof-verdict comparisons are portable.
Optimized Python (`-O` or `-OO`) is explicitly rejected before verification,
so disabling assertions cannot silently bypass the gates; each replay checks
that rejection in a separate process.

Supplementary exact Python controls check 56,172 completed-square instances,
22,968 admissible product inputs, and 1,829 normalized weighted-divisor
instances through `n = 400`. In 39 of the latter, `P` does not divide `Q`,
so the weighted check exercises cases beyond the unweighted divisor.
These finite counts audit implementation; the Lean statements cover all
integers satisfying their hypotheses.
