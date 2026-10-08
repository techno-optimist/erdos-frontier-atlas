import FormalBridge

-- n=4,u=1,v=3,B=C=1,D=6 satisfies every restore_cubic premise except h3.
example :
    ((1 : Int) ∣ 1*(3-1)) →
    ((1 : Int) ∣ 4*FormalBridge.Q 1 3) →
    Int.gcd (1 : Int) 4 = 1 → Int.gcd (1 : Int) 1 = 1 →
    ((6 : Int) = 2 ∨ (6 : Int) = 6) → Int.gcd (6 : Int) (1*1) = 1 →
    ((4 : Int)-1)*(4-2) = 6*(1*1) →
    ((4 : Int)-1)*(4-2) ∣ FormalBridge.Q 1 3 := by
  decide
