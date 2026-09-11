/- Isolated negative control, not a default success target.
Naive claim “the cancellation modulus is always 3” is false at j = 4. -/
example : (2 * 4 + 3) / Nat.gcd (2 * 4 + 3) 4 = 3 := by decide
