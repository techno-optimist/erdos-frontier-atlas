import WeightedFormal

-- The retained blocks permit 210 | 15Q, not 210 | Q.
example : (210 : Int) ∣ FormalBridge.Q 7 16 := by
  decide
