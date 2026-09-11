import I3
open P699I3
example : ∀ n j : Nat, 3 ≤ j → j ≤ n →
    j * (j - 1) * (j - 2) < binom n 3 →
    2 ≤ Nat.gcd (binom n 3) (binom n j) :=
  i3_gcd_ge_two_of_gt
#print axioms i3_gcd_ge_two_of_gt
#print axioms binom_pred3_identity
#print axioms binom_three_odd_of_mod4
#print axioms i3_gcd_ge_three_of_mod4_of_gt
