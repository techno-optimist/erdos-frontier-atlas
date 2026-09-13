import AdjacentBinomialGcd

set_option autoImplicit false

-- Separate universal contract for the optional divisibility lemma.
example : ∀ U A B C j : Nat,
    U ∣ B → Nat.gcd U A = 1 → A * C = (j + 1) * B → U ∣ C :=
  AdjacentBinomialGcd.divisor_transfer

#print axioms AdjacentBinomialGcd.divisor_transfer
