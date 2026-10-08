# Independent review of the P699 arithmetic reduction

Reviewed 2026-10-06 by the density-transport worker, independently of the
arithmetic author. **No mathematical flaw found in the stated derivation.**
This is an informal proof review, not a formalization of Kummer localization or
the cubic divisibility lemma, and not a literature-priority assessment.

Reviewed snapshots (SHA-256):

- `../arithmetic/README.md`:
  `092ee86bf917960d92f86a02762b64a6ba4c2d586d0e28add423a12ef135ef07`.
- `../arithmetic-checks/DiagonalInequality.lean`:
  `163628ca453cc23792d6d42f48e2b6ef27ffdd15fd9885638332fac215dde9d5`.

## Checks of the arithmetic interface

1. **Full prime powers are justified.** For a relevant block `p^e || n-t`,
   the prime `p` divides `binomial(n,3)`, including `p=3,e>=2` after division
   by 6. A hypothetical failure therefore has no base-p carries at any digit
   of `j+(n-j)`. This implies `j mod p^e <= t`, with the full exponent `e`,
   even though division by 6 reduced the exponent in `binomial(n,3)`.
   No converse to this necessary localization is used.

2. **Reduction of the denominator loses no congruence.** With
   `g=gcd(n,j), u=j/g, v=n/g`, the identity `n*u=v*j` is exact. Reducing
   this identity modulo a block gives `t*u=r*v`; division by `g` modulo
   that block is unnecessary. Thus a block at position 1 divides
   `u*(v-u)`, and a block at position 2 divides
   `2u*(2u-v)*(2u-2v)=4u*(v-u)*(v-2u)`.

3. **The omitted factors 2 and 3 can be restored.** When `4|n`, the
   2-adic valuation of `n-2` is exactly one. The stated `B,C` are odd and
   coprime; each is the product of all relevant full blocks at its position.
   Hence `BC|Q`. The remaining quotient is precisely 2 or 6. The product
   `Q=u*(v-u)*(v-2u)` is even. In the quotient-6 case, `3` divides neither
   `n` nor `v`, and the three linear factors give all three roots for `u`
   modulo 3. Also `3` does not divide `BC`. Consequently the quotient and
   `BC` are coprime divisors of `Q`, proving the exact divisibility
   `(n-1)*(n-2)|Q`. Positivity follows from `0<j<n/2`.

4. **The branch `n=2 mod 4` closes.** Position 0 gives
   `j=A*m`, with `n=2*3^epsilon*A` and `1<=m<=3^epsilon`.
   In the central case a relevant block of `n-1` would divide 1, forcing
   `n-1` to be 1 or 3, inconsistent with `j>3`.
   Otherwise only `epsilon=1,m=1 or 2` remains. Every full block of the
   odd number `B=n-1`, which is prime to 3, divides `m` or `6-m`.
   Coprime block assembly yields `B|m*(6-m)`, equal to 5 or 8.
   Oddness of `B` then gives `n<=6`, again impossible. This justifies
   excluding the entire branch, not only bounded samples of it.

5. **The seven diagonal contradiction has the claimed scope.** The exact
   identity `4*g^3*Q=d*(n^2-d^2)` converts the positive divisibility to
   the necessary inequality. For each listed `d`, `4|n` implies `2|j`,
   so `g>=2`. Substituting `n=x+d+8`, `x>=0`, into the difference of
   the two sides of the weakened inequality gives exactly
   `(32-d)*x^2+(-2*d^2+48*d+416)*x+16*d^2+352*d+1344`.
   Each coefficient is positive for `d=4,8,12,16,20,24,28`.
   The separate Lean module states these final polynomial implications
   with sufficient hypotheses; it does not claim the number-theoretic
   reduction is kernel checked.

The result therefore supports the seven unbounded families as an informal
theorem, with a separately formalized final algebraic obstruction. It does not
settle the full `i=3` slice, all fixed `d`, or P699. No additional finite search
was used for this review. Kummer's formula remains the explicit standard
number-theoretic input.
