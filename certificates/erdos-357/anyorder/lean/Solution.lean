import Erdos357.Gram

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
  by_contra hn
  have hN : (N : ℝ) ≤ ((3 : ℝ)/2+1/(10 : ℝ)^10)*(k : ℝ) := le_of_not_gt hn
  have ha := Erdos357.admissible_extend x hinj hrange hblocks
  exact Erdos357.step6_nine_term_contradiction (Erdos357.extend x) hk
    (fun r hr hr8 => Erdos357.step5_negative_correlations ha hk hN hr hr8)

#print axioms erdos357_any_order_improvement
