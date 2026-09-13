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
example : ∀ n j d : Nat, 3 ≤ j → j ≤ n →
    d ∣ binom n 3 → Nat.Coprime d (fac j) → d ∣ binom n j :=
  cancel_coprime_fac
#print axioms cancel_coprime_fac
example : ∀ n j : Nat, 3 ≤ j → j < n →
    Nat.Coprime n 6 → Nat.Coprime n (fac j) → n ∣ binom n j :=
  coprime_six_cancel
#print axioms coprime_six_cancel
