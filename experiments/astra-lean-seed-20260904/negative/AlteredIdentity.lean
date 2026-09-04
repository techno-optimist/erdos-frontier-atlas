import AdjacentBinomialGcd

-- Deliberately false alteration: replace gcd(k+1,j+1) by 1.
-- It is NOT a target of lake build. At j=3,k=1 it asserts 6=3.
example : (1 + 1) * Nat.gcd (Nat.choose 3 1) (Nat.choose (3 + 1) (1 + 1)) =
    Nat.choose 3 1 * 1 := by
  decide
