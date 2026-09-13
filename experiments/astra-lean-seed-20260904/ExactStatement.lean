import AdjacentBinomialGcd

set_option autoImplicit false

-- Independent check: precisely the requested universal identity, no hypotheses.
example : ∀ j k : Nat,
    (k + 1) * Nat.gcd (Nat.choose j k) (Nat.choose (j + 1) (k + 1)) =
      Nat.choose j k * Nat.gcd (k + 1) (j + 1) :=
  AdjacentBinomialGcd.adjacent_binomial_gcd

#print axioms AdjacentBinomialGcd.mul_gcd_of_mul_eq_mul
#print axioms AdjacentBinomialGcd.adjacent_binomial_gcd
