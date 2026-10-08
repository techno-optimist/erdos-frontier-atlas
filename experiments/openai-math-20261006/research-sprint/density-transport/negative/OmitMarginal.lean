import DensityTransport
open DensityTransport

-- EXPECTED TO FAIL: p is empty, q is full. Leakage is zero but discrepancy is one.
example : discrepancy [0] (fun _ => false) (fun _ => true) ≤
    2 * leakage [0] (fun _ => false) (fun _ => true) := by
  decide
