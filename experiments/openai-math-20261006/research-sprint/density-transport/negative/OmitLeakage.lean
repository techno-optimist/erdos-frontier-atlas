import DensityTransport
open DensityTransport

-- EXPECTED TO FAIL: the marginal upper inequality holds, but leakage is nonzero.
example : discrepancy [0] (fun _ => true) (fun _ => false) ≤ 0 := by
  decide
