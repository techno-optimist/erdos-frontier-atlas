import Erdos357.Basic
import Erdos357.Packing

open scoped BigOperators
open Finset

namespace Erdos357

theorem card_indices_real {k h : ℕ} (hh : h ≤ k) :
    ((indices k h).card : ℝ) = (h : ℝ) * k - (h : ℝ) * ((h : ℝ) - 1) / 2 := by
  rw [indices, card_sigma, Nat.cast_sum]
  simp only [card_range]
  have hc : (∑ r ∈ range h, ((k - r : ℕ) : ℝ)) =
      ∑ r ∈ range h, ((k : ℝ) - r) := by
    apply sum_congr rfl
    intro r hr
    rw [Nat.cast_sub (show r ≤ k by have := mem_range.mp hr; omega)]
  rw [hc, sum_sub_distrib, sum_const, card_range, nsmul_eq_mul, sum_range_vals]

theorem shifted_sum_le_span {k m j : ℕ} (a : ℕ → ℕ) (hm : m + j ≤ k) :
    (∑ i ∈ range m, (a (i + j) : ℝ)) ≤ span a k := by
  have hi : Set.InjOn (fun i : ℕ => i + j) (range m : Set ℕ) := by
    intro i _ l _ he
    dsimp at he
    omega
  have hs : (range m).image (fun i => i + j) ⊆ range k := by
    intro l hl
    obtain ⟨i, him, rfl⟩ := mem_image.mp hl
    have := mem_range.mp him
    exact mem_range.mpr (by omega)
  rw [← sum_image (f := fun t => (a t : ℝ)) hi]
  exact sum_le_sum_of_subset_of_nonneg hs (fun _ _ _ => Nat.cast_nonneg _)

theorem block_total_upper {k h : ℕ} (a : ℕ → ℕ) (hh : h ≤ k) :
    (∑ b ∈ indices k h, (blockValue a b : ℝ)) ≤
      ((h : ℝ) * ((h : ℝ) + 1) / 2) * span a k := by
  rw [indices, sum_sigma]
  have he : ∀ r ∈ range h,
      (∑ i ∈ range (k - r), (blockValue a ⟨r, i⟩ : ℝ)) ≤
        ((r : ℝ) + 1) * span a k := by
    intro r hr
    have hrh := mem_range.mp hr
    simp only [blockValue, block, Nat.cast_sum]
    rw [sum_comm]
    calc
      _ ≤ ∑ j ∈ range (r + 1), span a k := by
        apply sum_le_sum
        intro j hj
        have hjr := mem_range.mp hj
        exact shifted_sum_le_span a (by omega)
      _ = ((r : ℝ) + 1) * span a k := by simp
  calc
    _ ≤ ∑ r ∈ range h, ((r : ℝ) + 1) * span a k := sum_le_sum he
    _ = ((h : ℝ) * ((h : ℝ) + 1) / 2) * span a k := by
      rw [← sum_mul, sum_add_distrib, sum_range_vals]
      simp only [sum_const, card_range, nsmul_eq_mul, mul_one]
      ring

def sums (a : ℕ → ℕ) (k h : ℕ) : Finset ℕ := (indices k h).image (blockValue a)

theorem card_sums {k N h : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    (sums a k h).card = (indices k h).card :=
  card_image_of_injOn (blockValue_injOn ha)

theorem sum_sums {k N h : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) (f : ℕ → ℝ) :
    (∑ b ∈ sums a k h, f b) = ∑ b ∈ indices k h, f (blockValue a b) :=
  sum_image (blockValue_injOn ha)

theorem short_block_span {k N h : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hh : h ≤ k) :
    ((indices k h).card : ℝ) * ((indices k h).card + 1) ≤
      (h : ℝ) * ((h : ℝ) + 1) * span a k := by
  have hl := packed_lower (sums a k h) 1 (by
    intro b hb
    obtain ⟨c, hc, rfl⟩ := mem_image.mp hb
    exact blockValue_positive ha hc)
  rw [card_sums ha, sum_sums ha] at hl
  have hu := block_total_upper a hh
  norm_num only [Nat.cast_one, mul_one] at hl
  nlinarith

/-- Step 1 of `PROOF.md`. Here `k * sqrt k` is the unambiguous real
expression for `k^(3/2)`. No asymptotic estimate is used. -/
theorem step1_span {k N : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hk : 1 ≤ k) :
    (k : ℝ)^2 - 2 * k * Real.sqrt k ≤ span a k := by
  let h := Nat.sqrt k
  have hh : h ≤ k := Nat.sqrt_le_self k
  have hh1 : 1 ≤ h := by
    have := Nat.sqrt_le_sqrt hk
    simpa [h] using this
  have hhr : (1 : ℝ) ≤ h := by exact_mod_cast hh1
  have hhpos : (0 : ℝ) < h := by linarith
  have hhplus : (0 : ℝ) < (h : ℝ) + 1 := by positivity
  have hk0 : (0 : ℝ) ≤ k := Nat.cast_nonneg _
  have ht0 := Real.sqrt_nonneg (k : ℝ)
  have ht2 := Real.sq_sqrt hk0
  have hht : (h : ℝ) ≤ Real.sqrt k := Real.nat_sqrt_le_real_sqrt
  have hth : Real.sqrt k ≤ (h : ℝ) + 1 := Real.real_sqrt_le_nat_sqrt_succ
  have hshort := short_block_span ha hh
  rw [card_indices_real hh] at hshort
  have hm0 : 0 ≤ (h : ℝ) * k - (h : ℝ) * ((h : ℝ) - 1) / 2 := by
    rw [← card_indices_real hh]
    positivity
  have hsq : ((h : ℝ) * k - (h : ℝ) * ((h : ℝ) - 1) / 2)^2 ≤
      (h : ℝ) * ((h : ℝ) + 1) * span a k := by nlinarith
  let W : ℝ := (k : ℝ)^2 - (k : ℝ)^2 / ((h : ℝ) + 1) - k * ((h : ℝ) - 1)
  have hid : ((h : ℝ) * k - (h : ℝ) * ((h : ℝ) - 1) / 2)^2 -
      (h : ℝ) * ((h : ℝ) + 1) * W =
        (h : ℝ)^2 * ((h : ℝ) - 1)^2 / 4 + h * k * ((h : ℝ) - 1) := by
    dsimp [W]
    field_simp
    ring
  have hnn : 0 ≤ (h : ℝ)^2 * ((h : ℝ) - 1)^2 / 4 +
      h * k * ((h : ℝ) - 1) := by positivity
  have hw : W ≤ span a k := by
    have hp : 0 < (h : ℝ) * ((h : ℝ) + 1) := mul_pos hhpos hhplus
    nlinarith
  have hdiv : (k : ℝ)^2 / ((h : ℝ) + 1) ≤ k * Real.sqrt k := by
    apply (div_le_iff₀ hhplus).mpr
    have ht := mul_le_mul_of_nonneg_left hth ht0
    have hk' : (k : ℝ) ≤ Real.sqrt k * ((h : ℝ) + 1) := by nlinarith
    have := mul_le_mul_of_nonneg_left hk' hk0
    nlinarith
  have hprod := mul_le_mul_of_nonneg_left hht hk0
  dsimp [W] at hw
  nlinarith

end Erdos357
