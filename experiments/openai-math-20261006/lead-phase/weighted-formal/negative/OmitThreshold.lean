import WeightedFormal

-- At n=16,j=7,A=15,k=9, the quotient is positive because d >= 4A fails.
example : (4 : Int)*9-15*2 ≤ -1 := by
  decide
