# Density transport from a one-sided comparison

This module isolates the reusable logic in the proposed P841 transfer. Its
inputs are explicit Boolean events and error bounds. No result from an OpenAI
manuscript, BPZ24, or prime-factor theory is assumed as an axiom.

Verified locally with official Lean 4.33.1: all 13 audited theorems compiled,
all dependencies are standard Lean axioms, and both planted false controls
were rejected. See [execution.json](execution.json) and
[axiom-audit.log](axiom-audit.log).

## Exact finite statement

For two events A and B on the same finite observation list, let

- a and b be their occurrence counts;
- e count observations in A but outside B;
- D count observations where their indicators disagree.

The exact counting identity is

    D + a = b + 2e.

Therefore e <= E and b <= a+G imply

    D <= 2E+G.

The count imbalance needs only this upper direction. In applications where
the marginals converge to the same density, one may take G=max(b-a,0), which
is o(n). A one-sided containment outside an exceptional set supplies E.

For two pairs of events, the discrepancy between the two intersections is
at most the sum of the coordinate discrepancies. More generally, take any
fixed finite list of coordinates and **any Boolean function of their joint
indicator vector**. Its discrepancy is at most the sum of all coordinate
discrepancies. This covers intersections, unions, complements, exact patterns,
and every event in a fixed finite Boolean joint law. Independence is not a
hypothesis. Observation lists and coordinate lists may contain repeats.

## Asymptotic statement actually represented in Lean

To avoid importing mathlib, the module defines `Sublinear f` for natural-valued
errors by the exact quantifier statement

    for every positive integer k,
    there is N such that every n >= N satisfies k*f(n) <= n.

This is the usual f(n)=o(n) condition for nonnegative integer counts, expressed
without real-number limits. The module proves its closure under finite sums
and pointwise domination. It then proves that sublinear one-sided leakage
and sublinear positive marginal excess imply sublinear discrepancy for every
fixed finite-coordinate Boolean event. A final theorem bounds the symmetric
count gap, represented by `(a-b)+(b-a)` using truncated natural subtraction.
The event arrays are permitted to depend on n, so the result also covers
thresholds that move with the observation scale.

`asymptotic_joint_count_gap` is the main reusable theorem. Its hypotheses are
sublinearity of actual observed leakage and positive marginal excess for each
coordinate. It concludes sublinearity of the resulting joint-event count gap.
The growth parameter is n; for ordinary natural density use the observation
list `[1,...,n]`. For other sampling conventions, n is still the declared
normalizing parameter and must be interpreted accordingly.

## Ordinary density corollary and the P841 interface

The following real-limit interpretation is a mathematical explanation; the
module's exact checked language is the natural-number `Sublinear` predicate.
If every coordinate pair has one-sided containment error o(n), and both
marginal frequencies approach the same limit, its positive marginal excess
is o(n). The theorem then makes every finite joint-event frequency differ by
o(1). Whenever a limiting joint law for B is known, A has the same limiting
law. This transfers an existing law; it does not prove one exists.

For the proposed P841 application, A_a(n) denotes the waiting-time threshold
event and B_a(n) the largest-prime-factor threshold event. The arithmetic work
must separately establish the exceptional-set bound, the correct one-sided
comparison, the marginal laws, shift handling, and whichever external joint
law is being used. None of those arithmetic facts is proved in this module.
In particular, equal marginals **alone** would not suffice: two complementary
events can both have density one half while disagreeing everywhere.

## Verification

Use the official Lean 4.33.1 executable, with its bundled Std library. No
mathlib dependency, elan installation, or global toolchain configuration is
required:

```sh
python3 verify.py --lean /absolute/path/to/lean-4.33.1/bin/lean
```

The verifier compiles `DensityTransport.lean`, checks the `#print axioms`
reports against the permitted standard Lean axioms, and requires both planted
false claims in `negative/` to be rejected for proof failure. One omits the
marginal condition; the other omits the leakage condition. These controls
would expose either missing hypothesis in the finite transport rule.

The generated `.build/` directory is ignored. `--record` writes the execution
receipt and logs; ordinary replay leaves the recorded receipts alone.
`execution.json` records the actual compiler version, source and binary hashes,
command, axiom dependencies, and negative-control results. The checked receipt
is the authority for whether compilation passed; source text alone is not.

The isolated macOS ARM64 toolchain is downloaded from the official Lean GitHub
release. Its archive digest from GitHub's release API is
`88c45aad985b5d2a8d925fe10bd1296bd35f66f408480ab182d3facccd065a9d`.
This receipt concerns only the local transport proof. It is not a Lean rebuild
or verification of any external discovery.
