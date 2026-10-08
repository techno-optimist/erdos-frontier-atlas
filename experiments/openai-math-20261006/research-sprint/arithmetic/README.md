# P699: a reduced-denominator cubic and eight infinite diagonals

Research derivation, 2026-10-06. Graph attachment: `P699`, `S:triage:699`.
This is an elementary, self-contained informal proof with bounded exact tests.
It is not a proof of the full problem or of its full i = 3 slice. No canonical
status or frozen certificate is changed. Literature novelty is unverified.

**Result.** For every integer j > 3 and every d in {4, 8, 12, 16, 20, 24, 28, 32},
put n = 2j + d. Some odd prime divides both binomial(n,3) and binomial(n,j).
In particular this proves the entire n = 2j + 4 family, with no upper bound on j.
More generally, every remaining i = 3 counterexample with 4 | n and
d = n−2j ≥ 4 must satisfy **d³ ≥ 2n²+(d−2)(3n−2) > 2n²**.
Thus the growing near-central band (n−2j)³ ≤ 2n² is excluded.

The new structural input is sharper than these eight applications: if 4 divides
n, 0 < j < n/2, and the positional conditions at n−1 and n−2 hold, then, writing
j/n = u/v in lowest terms,

    (n−1)(n−2) divides u(v−u)(v−2u).                                  (1)

The earlier [i = 3 note](../../../claude-699-i3-position-20260928/README.md)
retained a possible denominator 6 and used the unreduced denominator 2K.
Restoring the small factors and reducing j/n sharpens its universal cubic bound
by a factor of three, and further by gcd cancellation when present.
This is a new derivation relative to the inspected checkout, not a priority claim.

## 1. The precise implication from a P699 failure

Suppose no odd prime divides both binomial(n,3) and binomial(n,j).
For t = 0, 1, 2 and an odd prime p dividing n−t, let M be the full power
p^e exactly dividing n−t. Call M relevant when p > 3, or when p = 3 and e ≥ 2.
Every relevant p divides binomial(n,3): among the three numerator factors
exactly one is divisible by p, and division by 6 removes only one factor of 3.

**Localization.** For each relevant M at position t,

    j mod M ≤ t.                                                     (2)

Indeed, p does not divide binomial(n,j). Kummer's carry formula says addition of
j and n−j has no carries in base p. In particular their residues modulo p^e
sum without overflow. Their sum is n mod M = t, proving (2).
Only this elementary standard formula is imported; no external proof code is used.

The converse is not assumed. Testing only the largest block at each position
does not replace checking all carries. Consequently a positional pass is a
necessary condition for a counterexample, and none is called a counterexample here.

## 2. Reduced-denominator cubic lemma

Assume 4 | n, 0 < j < n/2, and (2) at all relevant blocks of positions 1 and 2.
Put g = gcd(n,j), u = j/g, v = n/g, and Q = u(v−u)(v−2u) > 0. Define

    B = (n−1) / 3^[3 exactly divides n−1],
    C = (n−2) / (2 · 3^[3 exactly divides n−2]).

Because 4 | n, B and C are odd, coprime, and consist exactly of the relevant
prime-power blocks of n−1 and n−2 respectively.

For a block M at position t, (2) gives j ≡ r (mod M) for some 0 ≤ r ≤ t.
The exact identity nu = vj, together with n ≡ t (mod M), gives
tu ≡ rv (mod M). Thus M divides the product over 0 ≤ r ≤ t of (tu−rv).
At t = 1 this gives B | u(v−u). At t = 2 the product is 4Q; since C is odd,
C | Q. Therefore BC | Q. This argument does not require the position-0 condition.

Let D = (n−1)(n−2)/(BC). Then D is 2 or 6.

* Q is always even: if v is even, either u is even or v−2u is even;
  if v is odd, either u or v−u is even.
* If D = 6, a lone factor of 3 was removed from n−1 or n−2. Consequently
  3 does not divide n and hence does not divide v. Modulo 3 the three roots
  of u(v−u)(v−2u) exhaust all residues for u, so 3 | Q. Also 3 does not divide BC.

Since BC is odd, these observations give DBC | Q in either case, proving (1).

Writing d = n−2j, identity (1) immediately implies the exact necessary inequality

    4 g³ (n−1)(n−2) ≤ d (n²−d²).                                    (3)

There is no floating-point bound in (3): Q = j(n−j)(n−2j)/g³.
Maximizing x(1−x)(1−2x) on 0 < x < 1/2 also gives

    6√3 (n−1)(n−2) ≤ v³,
    108 ((n−1)(n−2))² ≤ v⁶.                                         (4)

For comparison with the old notation n = 2KA and j = Am, one has v ≤ 2K.
Thus (4) gives (n−1)(n−2) ≤ 4K³/(3√3), versus the old 4K³/√3.
This is an additional structural exclusion, not an extended numerical frontier.

## 3. The n ≡ 2 (mod 4) branch, reproved

For completeness, suppose n ≡ 2 (mod 4), j > 3, j ≤ n/2, and no common odd prime
exists. Let ε = 1 if exactly one factor of 3 divides n, and ε = 0 otherwise.
Write n = 2 · 3^ε · A. The product of position-0 relevant blocks is A, so (2)
forces j = Am with 1 ≤ m ≤ K = 3^ε.

The central case j = n/2 is impossible: for every relevant block M from n−1,
the congruences 2j ≡ 1 (mod M) and j ≡ 0 or 1 (mod M) would make M divide 1.
Thus there are no such blocks, forcing n−1 to be 1 or 3. Neither permits j > 3.

If ε = 0 then m = 1 is central, already excluded. If ε = 1 then m = 1 or 2,
n = 6A, and B = n−1 is odd and prime to 3. For a block M of B, (2) and
gcd(A,M) = 1 imply M | m or M | 6−m. Thus B | m(6−m), which is 5 or 8.
As B is odd, this gives n ≤ 6, again impossible for j > 3. This closes the branch.

## 4. The seven diagonals

Let d be one of 4, 8, 12, 16, 20, 24, 28; j > 3; and n = 2j+d.
Then n is even and n ≥ d+8. The previous section handles n ≡ 2 (mod 4).
If 4 | n, both n and d are multiples of four, so j is even and g = gcd(n,j) ≥ 2.
A failure would therefore force, by (3),

    32(n−1)(n−2) ≤ d(n²−d²).                                        (5)

But with x = n−d−8 ≥ 0, the difference between the left and right sides is

    (32−d)x² + (−2d²+48d+416)x + 16d²+352d+1344.

All three coefficients are positive for every listed d. The difference is
strictly positive, contradicting (5). This proves the stated theorem.

In particular, for d = 4 the coefficients are 28, 576, and 3008. This is a
direct proof of n = 2j+4 for every j > 3, including both even residue classes.

## 5. Integrality excludes a growing near-central band

Assume the hypotheses of the cubic lemma and let d = n−2j ≥ 4.
Write Q = k(n−1)(n−2) with positive integer k. The exact expression for Q gives

    (4g³k−d)(n−1)(n−2) = d(3n−d²−2).                               (6)

If 3n > d²+2, the integer 4g³k−d is positive and hence at least 1.
Equation (6) would force (n−1)(n−2) ≤ d(3n−d²−2).
However, putting F = (n−1)(n−2) − d(3n−d²−2), we have

    4F = (2n−3d−3)² + 4d³−9d²−10d−1.

For y = d−4 ≥ 0, the second summand equals
4y³+39y²+110y+71 > 0. Thus F > 0, a contradiction.
It follows that m = 4g³k−d cannot be positive. Nor can m be zero: (6) would
give d² = 3n−2, whereas d is even and 4 | n, so the two sides are respectively
0 and 2 modulo 4. Therefore m ≤ −1. Negating (6) now gives the stronger condition

    (n−1)(n−2) ≤ d(d²−3n+2),
    d³ ≥ n²+(d−1)(3n−2) > n².                                      (7)

There is a further parity improvement: d is even, so m is even and m ≤ −2.
Replacing 1 by 2 in the preceding inequality gives

    d³ ≥ 2n²+(d−2)(3n−2) > 2n².                                    (8)

If 4 | d then 4 | m, hence m ≤ −4 and

    d³ ≥ 4n²+(d−4)(3n−2).                                          (9)

Also m = 4g³k−d < 0 and k ≥ 1 force **d > 4g³**. For 4 | d we have g ≥ 2,
so d > 32. This excludes **all eight diagonals d = 4, 8, …, 32** at once
when 4 | n; §3 closes their n ≡ 2 (mod 4) branch. Section 4 is an independent
size-based proof of the first seven. On surviving cases with 4 | d, necessarily
d > 32, so (9) is strictly stronger than d³ > 4n².

For the exact gcd-sensitive version, let r be the least positive residue of d
modulo 4g³, namely r = d−4g³ floor((d−1)/(4g³)). Then −m ≥ r and

    d³ ≥ r(n−1)(n−2)+d(3n−2).                                     (10)

Thus a P699 failure with 4 | n must lie more than (2n²)^(1/3)/2 positions away
from j = n/2. For each fixed even d ≥ 4, only the finite range 2n² < d³
remains after this argument; this statement does not assert that those finitely
many pairs have all been checked for every d. The strengthening from the initial
square-root bound to (7) was identified by the parent reviewer from identity (6);
the independent source-audit reviewer supplied the parity refinements (8)–(9)
and the d = 32 extension. The parent and arithmetic lanes independently wrote (10).

The two omitted even distances cause no gap in the stated strip: d = 0 is
excluded by the central argument in §3, whose block proof applies to every
even n. For d = 2 and j > 3, one has n > 4 and
Q ≤ (n²−4)/2 < (n−1)(n−2), with difference (n−2)(n−4)/2 > 0.
This contradicts the positive divisibility (1). Thus d = 0 and d = 2 are excluded too.

The eight-diagonal theorem disposes of their whole finite ranges without any
enumeration. The growing-band argument is an additional consequence
of the integer quotient in (1), beyond the size estimate (3).

## 6. Scope and concrete boundaries

The argument also excludes every individual pair satisfying the strict reverse
of (3), regardless of d. It leaves an explicit gcd-sensitive interface for future
work, rather than an assertion that all fixed distances have been settled.

For example, n = 348, j = 158 gives d = 32 and g = 2. Here (3) holds:
the seven-diagonal size argument no longer contradicts failure. This pair is
**not** a P699 counterexample; it fails the stronger cubic divisibility and has
a common odd prime. It is a boundary control against extending (5) to all d.
The growing-band corollary does exclude this pair, because 32³ < 348².

For a counterexample to treating cubic divisibility as sufficient, take n = 496,
j = 171. Here g = 1 and Q = 35(n−1)(n−2), but the relevant block 11 from n−1
has j mod 11 = 6 > 1. Indeed the exact binomial gcd is 310992, divisible by 11.
The multiplication into a single cubic has forgotten which factor each block
must divide. Positional localization retains this additional information.

The d = 4,…,28 result does not rely on F012's density-one theorem. Density-one
control does not eliminate an exceptional arithmetic family. The external-source
swarm helped isolate the exact missing interface; the result above is obtained
from the repository's positional method by elementary divisibility.

## 7. Replay and freshness

Run `python3 -I experiments/openai-math-20261006/research-sprint/arithmetic/verify.py`.
The standalone standard-library verifier checks localization directly against
exact binomial coefficients, reduced products, nonvacuous positional passes,
the seven polynomial coefficient identities, and direct common-odd-prime existence
on a small bounded sample. It also checks the d = 32 boundary and a deliberately
false extra-factor control. The unbounded assertion rests on the proof, not on
these finite checks. `receipt.json` records the executed bounds and counts.

Local antecedents inspected: the two September 28 positional README files,
`experiments/astra-i3-20260911/typeB2b.md`,
`experiments/astra-20260904/699-strip.md`, and `tools/briefcaselib/p699.py`.
The old strip covered d ≤ 2 for i = 3; no exact reduced-denominator cubic or
eight-diagonal result was located in these notes and targeted repository searches.

A freshness attempt on 2026-10-06 opened the [official P699 page](https://www.erdosproblems.com/699),
but the browser returned an internal fetch error. Searches for combinations of
“699”, “binomial coefficients”, “2j+4”, “Erdős”, and “Rocca” did not yield a usable
primary-source match. These failed/limited checks establish no literature novelty
and do not certify the latest public problem status. No erdosproblems.com prose
has been reproduced here.
