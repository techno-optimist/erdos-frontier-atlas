import Mathlib

open scoped BigOperators

theorem erdos357_any_order_improvement
    (k N : ℕ) (x : Fin k → ℕ)
    (hinj : Function.Injective x)
    (hrange : ∀ i, 1 ≤ x i ∧ x i ≤ N)
    (hblocks : ∀ u v u' v' : Fin k, u ≤ v → u' ≤ v' →
      (∑ i ∈ Finset.Icc u v, x i) = (∑ i ∈ Finset.Icc u' v', x i) →
      u = u' ∧ v = v')
    (hk : 10 ^ 22 ≤ k) :
    ((3 : ℝ) / 2 + 1 / (10 : ℝ) ^ 10) * (k : ℝ) < (N : ℝ) := by
  sorry

set_option pp.all true
#check @erdos357_any_order_improvement
