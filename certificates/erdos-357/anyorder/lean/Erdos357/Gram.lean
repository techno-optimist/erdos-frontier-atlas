import Erdos357.Correlation

open scoped BigOperators
open Finset

namespace Erdos357

def prefixSum (a : ℕ → ℕ) (j : ℕ) : ℕ := ∑ i ∈ range j, a i

theorem prefixSum_add (a : ℕ → ℕ) (i r : ℕ) :
    prefixSum a (i+r) = prefixSum a i + block a r i := by
  simp only [prefixSum, block, sum_range_add]

noncomputable def phase (a : ℕ → ℕ) (k j : ℕ) : ℝ :=
  3*Real.pi*((prefixSum a j : ℝ)/k-j)

theorem phase_correlation (a : ℕ → ℕ) (k r : ℕ) :
    correlation a k r =
      ∑ i ∈ range (k+1-r), Real.cos (phase a k (i+r)-phase a k i) := by
  apply sum_congr rfl
  intro i hi
  dsimp [wave, phase]
  rw [prefixSum_add]
  push_cast
  congr 1
  ring

theorem shifted_real_sum {n m j : ℕ} {f : ℕ → ℝ}
    (h : m+j ≤ n) (hf : ∀ i < n, -1 ≤ f i) :
    (∑ i ∈ range m, f (i+j)) ≤ (∑ i ∈ range n, f i)+(n : ℝ)-m := by
  have hi : Set.InjOn (fun i : ℕ => i+j) (range m : Set ℕ) := by
    intro i _ l _ he
    dsimp at he
    omega
  have hs : (range m).image (fun i => i+j) ⊆ range n := by
    intro l hl
    obtain ⟨i, him, rfl⟩ := mem_image.mp hl
    have := mem_range.mp him
    exact mem_range.mpr (by omega)
  have hsum : (∑ i ∈ range m, (f (i+j)+1)) ≤ ∑ i ∈ range n, (f i+1) := by
    rw [← sum_image (f := fun i => f i+1) hi]
    apply sum_le_sum_of_subset_of_nonneg hs
    intro i hin _
    have := hf i (mem_range.mp hin)
    linarith
  simp only [sum_add_distrib, sum_const, card_range, nsmul_eq_mul, mul_one] at hsum
  linarith

/-- The exact nine-term sum-of-squares identity, expressed with real sine and
cosine coordinates so it requires no additional complex-number conventions. -/
theorem nine_square_identity (θ : ℕ → ℝ) :
    (∑ j ∈ range 9, Real.cos (θ j))^2 +
      (∑ j ∈ range 9, Real.sin (θ j))^2 =
        9+2*∑ r ∈ range 8, ∑ j ∈ range (8-r), Real.cos (θ (j+r+1)-θ j) := by
  have he : (∑ j ∈ range 9, Real.cos (θ j))^2 +
      (∑ j ∈ range 9, Real.sin (θ j))^2 =
        (∑ j ∈ range 9, (Real.cos (θ j)^2+Real.sin (θ j)^2))+
          2*∑ r ∈ range 8, ∑ j ∈ range (8-r), Real.cos (θ (j+r+1)-θ j) := by
    norm_num only [sum_range_succ, sum_range_zero, Nat.reduceSub, Nat.reduceAdd,
      zero_add, add_zero, Real.cos_sub]
    ring
  have hd : (∑ j ∈ range 9, (Real.cos (θ j)^2+Real.sin (θ j)^2)) = 9 := by
    have hterm : ∀ j, Real.cos (θ j)^2+Real.sin (θ j)^2 = 1 := by
      intro j
      nlinarith [Real.sin_sq_add_cos_sq (θ j)]
    simp only [hterm, sum_const, card_range, nsmul_eq_mul]
    norm_num
  rwa [hd] at he

theorem nine_square_nonneg (θ : ℕ → ℝ) :
    0 ≤ 9+2*∑ r ∈ range 8, ∑ j ∈ range (8-r), Real.cos (θ (j+r+1)-θ j) := by
  rw [← nine_square_identity]
  positivity

theorem correlation_partial {k r j : ℕ} (a : ℕ → ℕ) (hk : 8 ≤ k)
    (hr : r < 8) (hj : j < 8-r) :
    (∑ i ∈ range (k-7), Real.cos (phase a k (i+(j+r+1))-phase a k (i+j))) ≤
      correlation a k (r+1)+(7-r : ℕ) := by
  have hp := shifted_real_sum (n := k+1-(r+1)) (m := k-7) (j := j)
    (f := fun i => Real.cos (phase a k (i+(r+1))-phase a k i))
    (by omega) (fun i hi => Real.neg_one_le_cos _)
  rw [← phase_correlation] at hp
  have hn : k+1-(r+1) = (k-7)+(7-r) := by omega
  rw [hn, Nat.cast_add] at hp
  have he : (fun i => Real.cos (phase a k ((i+j)+(r+1))-phase a k (i+j))) =
      (fun i => Real.cos (phase a k (i+(j+r+1))-phase a k (i+j))) := by
    funext i
    rw [show (i+j)+(r+1) = i+(j+r+1) by omega]
  rw [he] at hp
  linarith

/-- Step 6 of `PROOF.md`: the exact boundary-corrected nine-window obstruction. -/
theorem step6_nine_term_contradiction {k : ℕ} (a : ℕ → ℕ) (hk : 10^22 ≤ k)
    (hC : ∀ r, 1 ≤ r → r ≤ 8 → correlation a k r ≤ -3*(k : ℝ)/20) : False := by
  have hk8 : 8 ≤ k := by omega
  have hn : 0 ≤ ∑ i ∈ range (k-7),
      (9+2*∑ r ∈ range 8, ∑ j ∈ range (8-r),
        Real.cos (phase a k (i+(j+r+1))-phase a k (i+j))) := by
    apply sum_nonneg
    intro i hi
    exact nine_square_nonneg (fun j => phase a k (i+j))
  rw [sum_add_distrib, sum_const, card_range, nsmul_eq_mul, ← mul_sum] at hn
  have hex : (∑ i ∈ range (k-7), ∑ r ∈ range 8, ∑ j ∈ range (8-r),
        Real.cos (phase a k (i+(j+r+1))-phase a k (i+j))) =
      ∑ r ∈ range 8, ∑ j ∈ range (8-r), ∑ i ∈ range (k-7),
        Real.cos (phase a k (i+(j+r+1))-phase a k (i+j)) := by
    rw [sum_comm]
    apply sum_congr rfl
    intro r hr
    rw [sum_comm]
  rw [hex] at hn
  have hu : (∑ r ∈ range 8, ∑ j ∈ range (8-r), ∑ i ∈ range (k-7),
        Real.cos (phase a k (i+(j+r+1))-phase a k (i+j))) ≤
      ∑ r ∈ range 8, ∑ _j ∈ range (8-r), (-3*(k : ℝ)/20+(7-r : ℕ)) := by
    apply sum_le_sum
    intro r hr
    apply sum_le_sum
    intro j hj
    have hp := correlation_partial a hk8 (mem_range.mp hr) (mem_range.mp hj)
    have hc := hC (r+1) (by omega) (by have := mem_range.mp hr; omega)
    linarith
  have hsum : (∑ r ∈ range 8, ∑ _j ∈ range (8-r),
      (-3*(k : ℝ)/20+(7-r : ℕ))) = -27*(k : ℝ)/5+168 := by
    norm_num [sum_range_succ]
    ring
  rw [hsum] at hu
  rw [Nat.cast_sub (show 7 ≤ k by omega)] at hn
  norm_num only [Nat.cast_ofNat] at hn
  have hk' : (10 : ℝ)^22 ≤ k := by exact_mod_cast hk
  nlinarith

end Erdos357
