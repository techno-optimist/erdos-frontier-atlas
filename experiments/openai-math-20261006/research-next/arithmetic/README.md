# P699: rational-position gaps and a transfer at every position

Research derivation, 2026-10-06. Graph nodes: `P699`, `S:triage:699`.
Informal proofs and bounded exact tests; not a resolution of P699 or its i = 3
slice. Literature novelty is unverified. Existing sprint files are preserved.

**New interface.** For any i ≥ 3, a counterexample's positional block at t forces

    R_t gcd(R_t,b)^t | ∏_(r=0..t) (D+ta−rb),    D = bj−an.             (1)

Here a,b are integers with b > 0; no coprimality or b < i restriction is needed.
The factor gcd(R_t,b)^t retains extra information when the chosen rational
denominator meets a block prime. This is a necessary condition, not an assertion
that the full binomial carries have been checked.

**Concrete i = 3 consequence.** If 4 | n, 3 < j ≤ n/2, and no common odd prime
exists, then

    (6j−2n−1)² ≥ 4(n−1) gcd(n−1,3) + 9.                            (2)

Thus a growing interval around j ≈ n/3 is excluded, in addition to the previous
central interval around n/2. Both small exceptional offsets in the derivation
are eliminated exactly, so (2) has no large-n qualifier or unchecked finite tail.
For each other fixed rational a/b in (0,1/2), §4 gives an explicit eventual
square-root-width gap. Section 5 explains why the earlier cubic quotient has a
different leading term at the center; it does not assert that larger gaps away
from the center are impossible.

## 1. Inputs and notation

For i ≥ 3 and 0 ≤ t < i, factor n−t = S_t R_t, where R_t contains each full
prime power p^e exactly dividing n−t with p > i, or p = i and e ≥ 2.
Only prime p are meant. Every such p divides binomial(n,i): a prime p ≥ i
occurs at only one of the i numerator positions, and i! removes a single factor
only in the case p = i.

If p does not divide binomial(n,j), Kummer's carry formula forces j mod p^e ≤ t.
Indeed the residues of j and n−j modulo p^e must sum without overflow to
n mod p^e = t. Therefore a failure of the p ≥ i common-prime assertion forces
this localization at every relevant block. This is the repository's existing
[general positional lemma](../../../claude-699-general-i-20260928/README.md).

For i = 3 and 4 | n, the first two products are

    B = R_1 = (n−1)/3^[3 exactly divides n−1],
    C = R_2 = (n−2)/(2·3^[3 exactly divides n−2]).

They are odd and coprime, and B ≥ (n−1)/3, C ≥ (n−2)/6.

## 2. Transfer with the denominator gcd retained

Fix a,b with b > 0 and put D = bj−an. For a block M = p^e at t, choose
r₀ in {0,…,t} with j ≡ r₀ (mod M). The r-th factor of (1) is exactly

    L_r = b(j−r) − a(n−t).

Consequently M | L_(r₀). Moreover, every L_r is divisible by gcd(M,b), since
M | n−t and b divides the other summand. Thus, for f = v_p(b), the product
contains at least e + t·min(e,f) factors of p: use e from L_(r₀), and
min(e,f) from each of the other t factors. Different blocks use distinct primes.
Multiplication proves (1).

For a nonzero right side, (1) supplies the exact size obstruction

    n−t ≤ S_t |∏(D+ta−rb)| / gcd(R_t,b)^t.                          (3)

This works at every position, including i ≥ 4, and at arbitrary rational
denominators. It complements the earlier reduced-denominator statement about
j/n itself: here a/b is a freely chosen reference position and D is its offset.
When b is not prime to R_t, the displayed divisibility is not claimed equivalent
to localization; when b is prime to R_t, the usual distinct-factor argument
does recover equivalence. Neither version alone is a full carry test.

The gcd exponent t cannot uniformly be replaced by t+1. At i = 3, n = 16,
j = 5, t = 1, a = 1, b = 5, localization at R_1 = 5 holds and the product
is 50. It is divisible by R_1 gcd(R_1,b) = 25, but not by 125.

## 3. An exact gap around one third

First suppose 3 | b. Under position-1 localization, (1) gives
B gcd(B,b) | (D+a)(D+a−b). If n−1 has a lone factor of 3, both factors on
the right are divisible by 3: they equal bj−a(n−1) and b(j−1)−a(n−1).
The two factors restore 3², exactly the factor missing when replacing B gcd(B,b)
by (n−1) gcd(n−1,b). In every other case B = n−1. Hence

    (n−1) gcd(n−1,b) | (D+a)(D+a−b),      when 3 | b.                (4)

The hypothesis on b matters. For n = 16, j = 5, a = 1, b = 2, position-1
localization holds but the right side is 35, which is not divisible by n−1 = 15.

Set a = 1 and b = 3. Then D = 3j−n and (4) becomes

    (n−1) gcd(n−1,3) | (D+1)(D−2).                                (5)

There are two potential zero products, and neither can be a P699 failure in
the stated domain:

* D = −1 gives n = 3j+1, so n ≡ 1 (mod 3) and C = (n−2)/2. The position-2
  product in (1) is (D+2)(D−1)(D−4) = 10, hence the odd integer C divides 10.
  Therefore C = 1 or 5 and n = 4 or 12. The second value is not 1 modulo 3;
  the first gives j = 1. Neither has j > 3.
* D = 2 again gives n ≡ 1 (mod 3) and C = (n−2)/2. Now the position-2 product
  is −8, forcing C = 1 and n = 4, j = 2, again inadmissible.

Thus the product in (5) is nonzero. For integer D, D²−D−2 is at least −2.
But (n−1) gcd(n−1,3) ≥ 7 because n ≥ 8. A negative nonzero product therefore
cannot have the required divisibility. We conclude

    D²−D−2 ≥ (n−1) gcd(n−1,3).

Multiplying by 4 and completing the square proves (2). Any admissible pair
violating (2) therefore has a common odd prime. The interval's center is
(2n+1)/6 and its radius is asymptotic to √(n gcd(n−1,3))/3.

This also separates the prior sprint's two nontrivial cubic false positives:
(n,j) = (496,171) gives (D+1)(D−2) = 270, not divisible by 1485;
(1464,561) gives 47740, not divisible by 1463. Their combined cubic passes
forgot the position-1 assignment. No P699 counterexample is claimed.

## 4. Explicit gaps around every fixed rational

Fix positive integers a,b with 2a < b, and put

    N(a,b) = 6a(b−a)(2b−a) + 2.

For i = 3, 4 | n, n > N(a,b), and a hypothetical failure, one has

    3(2bj−2an+2a−b)² ≥ 3b² + 4(n−1).                             (6)

Proof: position 1 makes B divide (D+a)(D+a−b). If this vanishes, D is −a
or b−a. The position-2 product then has absolute value respectively
a(b−a)(2b−a) or a(b−a)(a+b), both at most a(b−a)(2b−a), since 2a < b.
As C ≥ (n−2)/6, this would give n ≤ N(a,b), contrary to the hypothesis.
Thus |(D+a)(D+a−b)| ≥ (n−1)/3.

Writing x = D+a, a nonpositive x(x−b) has absolute value at most b²/4.
The threshold n > N(a,b) implies (n−1)/3 > b²/4: indeed a ≥ 1,
b−a > b/2 and 2b−a > 3b/2 give N(a,b) > 9b²/2.
Therefore x(x−b) is positive, and completing the square gives (6).

For 3 | b, (4) improves (6) to

    (2bj−2an+2a−b)² ≥ b²+4(n−1) gcd(n−1,b).                      (7)

These describe gaps of order √n/b in the j coordinate, centered at
an/b + 1/2 − a/b. They are unbounded structural consequences, not larger
finite searches. For general i the unconditional transfer is (1)–(3);
large small-prime parts S_t prevent replacing R_t by a fixed fraction of n
without additional assumptions.

## 5. Why the center is algebraically special

This is an exact diagnostic identity, not a proof that square-root gaps are best.
For the earlier i = 3 cubic, put g = gcd(n,j), P = (n−1)(n−2), and
k = j(n−j)(n−2j)/(g³P), assumed to be an integer. Define

    c₀ = a(b−a)(b−2a),    c₁ = b²−6ab+6a²,    c₂ = 6a−3b,
    m = b³g³k − c₀(n+3) − c₁D,    D = bj−an.

Polynomial division gives

    mP = (c₂D²+3c₁D+7c₀)n + 2D³−2c₁D−6c₀.                     (8)

To check it, expand b³j(n−j)(n−2j) as
c₀n³+c₁Dn²+c₂D²n+2D³ and use
n³ = (n+3)P+7n−6, n² = P+3n−2.
For a/b ≠ 1/2 the D²n term remains; at the center c₂ = 0 and also c₀ = 0.
That cancellation explains why the previous near-center integrality argument
reaches an n^(2/3) distance while its direct rational-offset version first
encounters a √n scale. Stronger off-center exclusions would need additional
arithmetic; (8) alone supplies no optimality claim.

## 6. Verification and freshness

Replay: `python3 -I experiments/openai-math-20261006/research-next/arithmetic/verify.py`.
The verifier independently factors small rows, checks block localization against
exact binomial coefficients, checks the transfer at positions for i = 3,…,8,
checks the restored divisor, checks the rational-gap implications, and rejects
the two deliberately false strengthened claims above. Bounded computations test
the proofs but do not establish their unbounded conclusions. Bounds, counts and
source hashes appear in `receipt.json`.

The local prior art consulted is the general positional note and the September
4 strip and September 11 type-B residual notes. Their exact rational-position
corollary concerns j/n = a/b with b < i; it does not state (1), the denominator
gcd gain, or the explicit offset intervals here.

A primary-source freshness check on 2026-10-06 read [Bergman's paper,
arXiv:0806.0607v2](https://arxiv.org/html/0806.0607), especially the gcd bounds
and Kummer lemma. Its growing bound concerns the magnitude of the common gcd;
that alone does not locate a prime ≥ i. This narrow read and targeted searches
did not identify the present rational-offset formulas, but do not establish
novelty. The [official P699 page](https://www.erdosproblems.com/699) again returned
a fetch error. No latest-status or priority claim is made and no restricted
website prose is reproduced.
