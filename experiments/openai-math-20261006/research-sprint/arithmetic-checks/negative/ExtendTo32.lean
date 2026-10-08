import Std
-- Deliberately false: the algebraic obstruction cannot simply include d=32.
-- This is not a P699 counterexample, only a failed strengthening of one inequality.
example : 32 * (348 * 348) < 32 * ((348 - 1) * (348 - 2)) + 32 * 32 * 32 := by
  decide
