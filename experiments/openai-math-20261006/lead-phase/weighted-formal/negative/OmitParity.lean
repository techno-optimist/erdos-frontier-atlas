import WeightedFormal

-- n=6,d=4,A=1,m=0 satisfies the weighted identity and threshold.
-- Without row parity, the claimed strict coefficient-two bound is false.
example : (2 : Int)*(6*6) < 1*4*4*4 := by
  decide
