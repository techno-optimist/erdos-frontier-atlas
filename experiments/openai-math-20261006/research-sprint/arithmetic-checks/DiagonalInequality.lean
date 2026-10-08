import Std

namespace DiagonalInequality

/-- Exact polynomial obstruction for the seven listed diagonals.
This proves only the algebraic inequality, not the arithmetic reduction from P699. -/
theorem seven_diagonal_positive (n d : Nat)
    (hd : d = 4 ∨ d = 8 ∨ d = 12 ∨ d = 16 ∨ d = 20 ∨ d = 24 ∨ d = 28)
    (hn : d + 8 ≤ n) :
    d * (n * n) < 32 * ((n - 1) * (n - 2)) + d * d * d := by
  have hr : ∃ r : Nat, n = r + d + 8 := ⟨n - d - 8, by omega⟩
  obtain ⟨r, rfl⟩ := hr
  have h₁ : r + d + 8 - 1 = r + d + 7 := by omega
  have h₂ : r + d + 8 - 2 = r + d + 6 := by omega
  rw [h₁, h₂]
  rcases hd with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals
    simp only [Nat.add_mul, Nat.mul_add]
    omega

/-- The weak inequality forced by a failure is incompatible with these diagonals. -/
theorem seven_diagonal_no_weak_bound (n d : Nat)
    (hd : d = 4 ∨ d = 8 ∨ d = 12 ∨ d = 16 ∨ d = 20 ∨ d = 24 ∨ d = 28)
    (hn : d + 8 ≤ n)
    (hbad : 32 * ((n - 1) * (n - 2)) ≤ d * (n * n - d * d)) : False := by
  have hp := seven_diagonal_positive n d hd hn
  have hsq : d * d ≤ n * n := Nat.mul_self_le_mul_self (by omega)
  have hm : d * (d * d) ≤ d * (n * n) := Nat.mul_le_mul (Nat.le_refl d) hsq
  have he : d * (n * n - d * d) + d * d * d = d * (n * n) := by
    rw [Nat.mul_sub]
    have hc : d * d * d = d * (d * d) := Nat.mul_assoc d d d
    rw [hc]
    exact Nat.sub_add_cancel hm
  omega

/-- The same contradiction with an explicit gcd-sized parameter g >= 2. -/
theorem seven_diagonal_no_gcd_bound (n d g : Nat)
    (hd : d = 4 ∨ d = 8 ∨ d = 12 ∨ d = 16 ∨ d = 20 ∨ d = 24 ∨ d = 28)
    (hn : d + 8 ≤ n) (hg : 2 ≤ g)
    (hbad : (4 * g * g * g) * ((n - 1) * (n - 2)) ≤ d * (n * n - d * d)) : False := by
  have hg₁ : 4 * 2 ≤ 4 * g := Nat.mul_le_mul (Nat.le_refl 4) hg
  have hg₂ : 4 * 2 * 2 ≤ 4 * g * g := Nat.mul_le_mul hg₁ hg
  have hg₃ : 32 ≤ 4 * g * g * g := Nat.mul_le_mul hg₂ hg
  have hlow : 32 * ((n - 1) * (n - 2)) ≤ (4 * g * g * g) * ((n - 1) * (n - 2)) :=
    Nat.mul_le_mul hg₃ (Nat.le_refl _)
  exact seven_diagonal_no_weak_bound n d hd hn (Nat.le_trans hlow hbad)

#print axioms seven_diagonal_positive
#print axioms seven_diagonal_no_weak_bound
#print axioms seven_diagonal_no_gcd_bound
end DiagonalInequality
