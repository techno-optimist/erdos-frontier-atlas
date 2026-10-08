import FormalBridge

-- Dropping coprimality cannot justify multiplying two divisors of the same number.
example : ((2 : Int) ∣ 2) → ((2 : Int) ∣ 2) → (2 : Int)*2 ∣ 2 := by
  decide
