import Solution

open scoped BigOperators

theorem challenge_statement_copy
    (k N : ℕ) (x : Fin k → ℕ)
    (hinj : Function.Injective x)
    (hrange : ∀ i, 1 ≤ x i ∧ x i ≤ N)
    (hblocks : ∀ u v u' v' : Fin k, u ≤ v → u' ≤ v' →
      (∑ i ∈ Finset.Icc u v, x i) = (∑ i ∈ Finset.Icc u' v', x i) →
      u = u' ∧ v = v')
    (hk : 10 ^ 22 ≤ k) :
    ((3 : ℝ) / 2 + 1 / (10 : ℝ) ^ 10) * (k : ℝ) < (N : ℝ) :=
  erdos357_any_order_improvement k N x hinj hrange hblocks hk

#print axioms challenge_statement_copy
