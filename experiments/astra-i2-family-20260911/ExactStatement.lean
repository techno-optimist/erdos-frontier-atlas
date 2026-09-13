import P699I2

open P699I2

example : ∀ j : Nat, 3 ≤ j →
    ∃ m, 3 ≤ m ∧ m ∣ binom (2 * j + 3) 2 ∧ m ∣ binom (2 * j + 3) j :=
  erdos699_i2_divisor

#print axioms erdos699_i2_divisor
#print axioms i2_m_divides
#print axioms mul_binom_eq
