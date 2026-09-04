import AdjacentBinomialGcd

#check Nat.gcd_mul_left
#check Nat.add_one_mul_choose_eq
#check Nat.gcd_mul_right_right_of_gcd_eq_one
#check Nat.dvd_mul_left_of_dvd
#print AdjacentBinomialGcd.mul_gcd_of_mul_eq_mul
#print AdjacentBinomialGcd.adjacent_binomial_gcd
#print AdjacentBinomialGcd.divisor_transfer

-- A kernel-reduced concrete witness explaining the isolated negative control.
example : (1 + 1) * Nat.gcd (Nat.choose 3 1) (Nat.choose 4 2) = 6 := by decide
example : Nat.choose 3 1 * 1 = 3 := by decide
