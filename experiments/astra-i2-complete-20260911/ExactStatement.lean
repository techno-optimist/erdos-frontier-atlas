import I2All

open P699I2All

example : ∀ n j : Nat, 3 ≤ j → 2 * j ≤ n → 2 ≤ Nat.gcd (binom n 2) (binom n j) :=
  i2_gcd_ge_two

#print axioms i2_gcd_ge_two
#print axioms binom_pred2_identity
#print axioms binom_two_gt
