import Erdos357.SmallEntries

open scoped BigOperators
open Finset

namespace Erdos357

/-- Retaining every sum at least `L` is a harmless enlargement of the retained
set in PROOF.md: it has the same lower bound and only reduces the number lost. -/
def goodSums (a : ℕ → ℕ) (k h L : ℕ) : Finset ℕ :=
  (sums a k h).filter (L ≤ ·)

noncomputable def displacement (s : Finset ℕ) (L : ℕ) : ℝ :=
  (∑ b ∈ s, (b : ℝ)) - (s.card : ℝ)*L - (s.card : ℝ)*((s.card : ℝ)-1)/2

theorem first_le_block (a : ℕ → ℕ) (r i : ℕ) : a i ≤ block a (r+1) i := by
  simpa only [block, Nat.add_zero] using
    (single_le_sum (s := range (r+1)) (f := fun j => a (i+j))
      (fun j _ => Nat.zero_le _) (show 0 ∈ range (r+1) by simp))

theorem small_block_count {k N h L : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    ((sums a k h).filter (· < L)).card ≤ h * (badEntries a k L).card := by
  have he : ((sums a k h).filter (· < L)).card =
      ((indices k h).filter (fun b => blockValue a b < L)).card := by
    rw [sums, filter_image]
    apply card_image_of_injOn
    exact (blockValue_injOn ha).mono (filter_subset _ _)
  rw [he, indices, filter_sigma, card_sigma]
  calc
    _ ≤ ∑ r ∈ range h, (badEntries a k L).card := by
      apply sum_le_sum
      intro r hr
      apply card_le_card_of_injOn a
      · intro i hi
        obtain ⟨hi, hval⟩ := mem_filter.mp hi
        have hik : i < k := by have := mem_range.mp hi; omega
        refine mem_filter.mpr ⟨mem_image.mpr ⟨i, mem_range.mpr hik, rfl⟩, ?_⟩
        exact lt_of_le_of_lt (first_le_block a r i) hval
      · intro i hi j hj heq
        have hi' := mem_range.mp (mem_filter.mp hi).1
        have hj' := mem_range.mp (mem_filter.mp hj).1
        exact ha.injective (by dsimp; omega) (by dsimp; omega) heq
    _ = _ := by simp

theorem good_card_loss {k N h L : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    (indices k h).card ≤ (goodSums a k h L).card + h*(badEntries a k L).card := by
  have hc := card_filter_add_card_filter_not (s := sums a k h) (p := fun b => L ≤ b)
  simp only [not_le] at hc
  have hl := small_block_count (h := h) (L := L) ha
  rw [card_sums ha] at hc
  dsimp [goodSums]
  omega

theorem good_displacement_nonneg (a : ℕ → ℕ) (k h L : ℕ) :
    0 ≤ displacement (goodSums a k h L) L := by
  have hp := packed_lower (goodSums a k h L) L (fun _ hb => (mem_filter.mp hb).2)
  dsimp [displacement]
  linarith

theorem good_total_upper {k N h L : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hh : h ≤ k) :
    (∑ b ∈ goodSums a k h L, (b : ℝ)) ≤
      ((h : ℝ)*((h : ℝ)+1)/2) * span a k := by
  calc
    _ ≤ ∑ b ∈ sums a k h, (b : ℝ) :=
      sum_le_sum_of_subset_of_nonneg (filter_subset _ _) (fun _ _ _ => Nat.cast_nonneg _)
    _ = _ := sum_sums ha _
    _ ≤ _ := block_total_upper a hh

theorem missing_bounds {k N h : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hk : 10^22 ≤ k)
    (hN : (N : ℝ) ≤ ((3 : ℝ)/2 + 1/10^10) * k) (hh : h ≤ 8) :
    0 ≤ (h : ℝ)*k - (goodSums a k h (cutoff k)).card ∧
    (h : ℝ)*k - (goodSums a k h (cutoff k)).card ≤ (k : ℝ)/6000 := by
  have hhk : h ≤ k := by omega
  have hcard := card_indices_real hhk
  have hsub := card_le_card (filter_subset (fun b => cutoff k ≤ b) (sums a k h))
  rw [card_sums ha] at hsub
  have hsub' : ((goodSums a k h (cutoff k)).card : ℝ) ≤ (indices k h).card := by
    exact_mod_cast hsub
  have hsmall := step2_few_small ha hk hN
  have hloss := good_card_loss (h := h) (L := cutoff k) ha
  have hloss' : ((indices k h).card : ℝ) ≤ (goodSums a k h (cutoff k)).card +
      (h : ℝ)*(badEntries a k (cutoff k)).card := by exact_mod_cast hloss
  have hh0 : (0 : ℝ) ≤ h := Nat.cast_nonneg _
  have hh8 : (h : ℝ) ≤ 8 := by exact_mod_cast hh
  have hq0 : (0 : ℝ) ≤ (badEntries a k (cutoff k)).card := Nat.cast_nonneg _
  have hq8 := mul_le_mul_of_nonneg_right hh8 hq0
  have hk' : (10 : ℝ)^22 ≤ k := by exact_mod_cast hk
  have htri : 0 ≤ (h : ℝ)*((h : ℝ)-1) := by
    rcases Nat.eq_zero_or_pos h with he | hp
    · simp [he]
    · have : (1 : ℝ) ≤ h := by exact_mod_cast hp
      positivity
  constructor <;> nlinarith

/-- Step 3 of `PROOF.md`, including the nonnegativity of the displacement. -/
theorem step3_packing_stability {k N h : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hk : 10^22 ≤ k)
    (hN : (N : ℝ) ≤ ((3 : ℝ)/2 + 1/10^10) * k)
    (hh : h ≤ 8) :
    0 ≤ displacement (goodSums a k h (cutoff k)) (cutoff k) ∧
    displacement (goodSums a k h (cutoff k)) (cutoff k) / (k : ℝ)^2 ≤ 9/4000 := by
  refine ⟨good_displacement_nonneg a k h (cutoff k), ?_⟩
  have hk' : (10 : ℝ)^22 ≤ k := by exact_mod_cast hk
  have hkpos : (0 : ℝ) < k := by positivity
  have hh0 : (0 : ℝ) ≤ h := Nat.cast_nonneg _
  have hh8 : (h : ℝ) ≤ 8 := by exact_mod_cast hh
  let M : ℝ := (goodSums a k h (cutoff k)).card
  let d : ℝ := (h : ℝ)*k-M
  let T : ℝ := (h : ℝ)*((h : ℝ)+1)/2
  have hM : 0 ≤ M := Nat.cast_nonneg _
  obtain ⟨hd0, hdhi⟩ := missing_bounds ha hk hN hh
  change 0 ≤ d at hd0
  change d ≤ (k : ℝ)/6000 at hdhi
  have hT0 : 0 ≤ T := by dsimp [T]; positivity
  have hT36 : T ≤ 36 := by dsimp [T]; nlinarith
  have hu := good_total_upper (h := h) (L := cutoff k) ha (by omega)
  change (∑ b ∈ goodSums a k h (cutoff k), (b : ℝ)) ≤ T * span a k at hu
  have hs := mul_le_mul_of_nonneg_left (span_upper_near ha hN) hT0
  have hL := mul_le_mul_of_nonneg_left (cutoff_bounds k).1 hM
  have hdel : displacement (goodSums a k h (cutoff k)) (cutoff k) ≤
      (T/10^10 + (h : ℝ)/10000)*(k : ℝ)^2 +
        ((h : ℝ)+1/2)*d*k + (T+h)*k/2 := by
    have hid : T*((1+1/(10 : ℝ)^10)*(k : ℝ)^2+k/2) -
        M*((1:ℝ)/2-1/10000)*k - M*(M-1)/2 =
        (T/10^10+(h : ℝ)/10000)*(k : ℝ)^2 +
        ((h : ℝ)+1/2)*d*k + (T+h)*k/2 -
        d*k/10000 - d^2/2-d/2 := by dsimp [d, T]; ring
    have hdk : 0 ≤ d*(k : ℝ) := mul_nonneg hd0 hkpos.le
    dsimp [displacement, M] at *
    nlinarith [sq_nonneg d]
  have ht := mul_le_mul_of_nonneg_right hT36 (sq_nonneg (k : ℝ))
  have hhq := mul_le_mul_of_nonneg_right hh8 (sq_nonneg (k : ℝ))
  have hdk := mul_le_mul_of_nonneg_right hdhi hkpos.le
  have hhd := mul_le_mul_of_nonneg_right hh8 (mul_nonneg hd0 hkpos.le)
  have htk := mul_le_mul_of_nonneg_right hT36 hkpos.le
  have hhk := mul_le_mul_of_nonneg_right hh8 hkpos.le
  have hkk := mul_le_mul_of_nonneg_right hk' hkpos.le
  apply (div_le_iff₀ (sq_pos_of_pos hkpos)).mpr
  nlinarith

end Erdos357
