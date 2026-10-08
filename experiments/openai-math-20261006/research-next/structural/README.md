# P699: the central obstruction with an explicit small-prime defect

Graph attachment: `P699`, `S:triage:699`. Local informal derivation with exact
finite checks and independent agent review; not a full proof of P699, not a
formalized binomial theorem, and not a literature novelty claim.

The cubic obstruction extends to every fixed i ≥ 3. Its loss is an explicit
small-prime factor A. If 4 divides n and a pair i < j < n/2 fails P699, put
d = n−2j and g = gcd(n,j). Define A as the part of (n−1)(n−2)/2 supported on
primes at most i, retaining their full exponents. Then

    d ≥ 4A  implies  A d³ ≥ 2n² + (Ad−2)(3n−2) > 2n²,
                    Ad > 4g³.                                      (1)

If also 4 divides d, the coefficient 2 improves to 4:

    A d³ ≥ 4n² + (Ad−4)(3n−2).                                     (2)

This gives a computable forbidden region, not a conclusion for every j.
For A > 1, the inner range 0 ≤ d < 4A is not covered by (1).

When A = 1, the entire previous central band transfers: every i < j ≤ n/2
with d³ ≤ 2n² has a common prime **greater than i**, and so does each of
the eight diagonals d = 4,8,…,32 on these rows. The rows A = 1 have exact
natural density

    (1/4) ∏_{3 ≤ p ≤ i, p prime} (1−2/p).                           (3)

The [September general-i note](../../../claude-699-general-i-20260928/README.md)
already proves density-one coverage of all j for each fixed i, with a quantitative
exception count. Formula (3) does **not** improve that result. The contribution
here is an explicit divisibility and geometric constraint on individual pairs,
with no upper bound on n, and a transparent cost for the small-prime factors.

## 1. The arithmetic bridge

Let B and C be the products of full prime powers with prime p > i in n−1
and (n−2)/2, respectively. Because 4 | n, both original numbers are odd
and coprime. Consequently B and C are odd and coprime, and

    P = (n−1)(n−2) = 2ABC.

Suppose no prime p > i divides both binomial coefficients. This is a weaker
assumption than a P699 failure, which excludes common primes p ≥ i.
For each full block M = p^e of B (position t = 1) or C (t = 2), p divides
binomial(n,i): exactly one numerator factor n−t is divisible by p, and
p does not divide i!. The condition p > i is deliberately conservative.

Since p does not divide binomial(n,j), we must have j mod M ≤ t.
For a self-contained justification, Legendre's factorial formula expresses
the valuation of this binomial as the sum over h ≥ 1 of

    floor(n/p^h) − floor(j/p^h) − floor((n−j)/p^h).

Each summand is 0 or 1. If j mod p^e > t = n mod p^e, its e-th summand
is 1, a contradiction. This is the localization also expressed by Kummer's
carry theorem; see [Granville's article](https://dms.umontreal.ca/~andrew/Binomial/intro.html).

Put u = j/g, v = n/g and Q = u(v−u)(v−2u) > 0. From nu = vj,
the block congruence j ≡ r mod M gives tu ≡ rv mod M. Multiplying over
the possible r gives

    B | u(v−u),             C | 4Q.

As C is odd, C | Q; hence BC | Q. Also Q is always even: if v is even,
v−2u is even; if v is odd, one of u and v−u is even. Therefore 2BC | Q,
and we obtain the exact generalization

    (n−1)(n−2) | A u(v−u)(v−2u).                                  (4)

Only positions 1 and 2 were used. No unverified OpenAI theorem enters this
argument. It transfers the [previous reduced cubic](../../research-sprint/arithmetic/README.md)
through the older general-i positional method.

## 2. The integral quotient excludes a region

By (4), write AQ = kP with integer k ≥ 1. The identity
4g³Q = d(n²−d²) gives, for m = 4g³k−Ad,

    mP = Ad(3n−d²−2).                                              (5)

Assume d ≥ 4A. Let F = P−Ad(3n−d²−2). Completing the square gives

    4F = (2n−3Ad−3)² + Ad²(4d−9A) − 10Ad − 1.

Since 4d−9A ≥ 7A and Ad ≥ 4, the last three terms are at least
7(Ad)²−10Ad−1 > 0. Thus F > 0. Equation (5) would contradict F > 0
if the integer m were positive. If m = 0, then d² = 3n−2; but d is even
and 4 | n, making the two sides 0 and 2 modulo 4. Hence m < 0.

In fact m is even, so −m ≥ 2. Negating (5) and using P = n²−3n+2 yields

    A d³ ≥ 2P + Ad(3n−2) = 2n² + (Ad−2)(3n−2).

The last summand is positive. Also m < 0 and k ≥ 1 imply Ad > 4g³.
When 4 | d, the integer m is divisible by 4, giving (2).

More precisely, if r is the least positive residue of Ad modulo 4g³,

    A d³ ≥ rP + Ad(3n−2).                                         (6)

This is stronger when the actual gcd and residue are available. It follows
because −m is a positive integer congruent to Ad modulo 4g³.

## 3. Defect-free rows and boundary cases

For A = 1, (1) applies whenever d ≥ 4. If d = 0, then j = n/2.
Any prime-power block M in B = n−1 would require j ≡ 0 or 1 mod M,
but 2j = n ≡ 1 mod M, forcing M | 1. Thus n−1 = 1, impossible when
i < j and i ≥ 3. For d = 2, g ≥ 1 gives

    0 < Q ≤ (n²−4)/2 < (n−1)(n−2),

since the difference is (n−2)(n−4)/2 > 0. This contradicts P | Q.
Together these arguments exclude d³ ≤ 2n² on all A = 1 rows.

For d in {4,8,…,32}, both n and d are multiples of 4, so j is even
and g ≥ 2. The condition d > 4g³ ≥ 32 is impossible. This establishes
the eight diagonals for arbitrary i on A = 1 rows, with the stated j > i
restriction. It does not settle those diagonals on every higher-i row.

The condition A = 1 is exactly

    4 | n,       gcd((n−1)(n−2)/2, i!) = 1.

For each odd prime p ≤ i this excludes precisely n ≡ 1,2 mod p.
The Chinese remainder theorem gives ∏(p−2) allowed classes modulo
4∏p, proving (3). In particular every multiple of 4∏p belongs to the
family. Examples of the density are 1/12 for i = 3,4; 1/20 for i = 5;
1/28 for i = 7; and 9/308 for i = 11.

## 4. Why the hypotheses matter

Take (n,i,j) = (16,6,7). The two retained rough products are B = 1,
C = 7, and the localization conditions at positions 1 and 2 hold.
Here A = 15, g = 1, Q = 126 and P = 210. Thus P does not divide Q,
but P divides AQ with quotient k = 9. The defect cannot simply be omitted.

Also d = 2 and m = 4k−Ad = 6 > 0: quotient negativity fails when the
threshold d ≥ 4A is omitted. This pair is **not** a P699 counterexample;
other positions supply a common prime. It is a negative control on these
two tempting strengthenings of the algebraic method.

## 5. Evidence and replay

Run `python3 -I experiments/openai-math-20261006/research-next/structural/verify.py`.
The read-only standard-library verifier checks exact binomial valuations,
all retained block implications, the defect divisibility, quotient identities,
the exclusions and explicit prime witnesses on bounded inputs. It enumerates
complete CRT periods through i = 13 and checks both negative controls.
The bounds, counts and source hashes are in [receipt.json](receipt.json).
Finite checks support the implementation and catch algebra mistakes; the
unbounded conclusions rest on the proof above.

Two other agents independently checked the restoration, complete-square
argument, parity and density calculation. The existing local Lean components
and the [finite-block formal bridge](../formal-bridge/README.md) cover the
A = 1 algebraic specialization, and the earlier i = 3 restoration of a lone
factor of 3. The weighted A > 1 theorem here is not Lean-formalized.

The October 6 literature check inspected the local general-i antecedent,
Granville's primary exposition, and [Bergman's related paper](https://arxiv.org/abs/0806.0607v2).
The direct [P699 page](https://www.erdosproblems.com/699) returned HTTP 403.
No successful current-status or novelty certification follows from that check.
Canonical statuses and frozen certificates remain unchanged.
