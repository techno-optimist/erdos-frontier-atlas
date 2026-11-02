import Erdos357.Packing

open scoped BigOperators
open Finset MeasureTheory

namespace Erdos357

theorem continuous_of_ten_lipschitz {f : ℝ → ℝ}
    (hf : ∀ x y, |f x - f y| ≤ 10 * |x-y|) : Continuous f := by
  have hl : LipschitzWith 10 f := by
    apply LipschitzWith.of_dist_le_mul
    simpa only [Real.dist_eq, NNReal.coe_ofNat] using hf
  exact hl.continuous

theorem integral_abs_le_length {f : ℝ → ℝ} (hf : ∀ x, |f x| ≤ 1) (a b : ℝ) :
    |∫ x in a..b, f x| ≤ |b-a| := by
  simpa only [Real.norm_eq_abs, one_mul] using
    (intervalIntegral.norm_integral_le_of_norm_le_const (a := a) (b := b)
      (C := 1) (fun x _ => show ‖f x‖ ≤ 1 by simpa only [Real.norm_eq_abs] using hf x))

theorem integral_endpoints {f : ℝ → ℝ} (hc : Continuous f)
    (hf : ∀ x, |f x| ≤ 1) (a b c d : ℝ) :
    |(∫ x in a..b, f x) - ∫ x in c..d, f x| ≤ |c-a| + |d-b| := by
  rw [intervalIntegral.integral_interval_sub_interval_comm
    (hc.intervalIntegrable a b) (hc.intervalIntegrable c d) (hc.intervalIntegrable a c)]
  exact (abs_sub _ _).trans (add_le_add (integral_abs_le_length hf a c)
    (integral_abs_le_length hf b d))

theorem grid_cell {f : ℝ → ℝ} (hf : ∀ x y, |f x-f y| ≤ 10*|x-y|)
    (a t : ℝ) (ht : 0 ≤ t) :
    |t * f a - ∫ x in a..(a+t), f x| ≤ 10*t^2 := by
  have hc := continuous_of_ten_lipschitz hf
  have he : t*f a - (∫ x in a..(a+t), f x) =
      ∫ x in a..(a+t), (f a - f x) := by
    rw [intervalIntegral.integral_sub (continuous_const.intervalIntegrable _ _)
      (hc.intervalIntegrable _ _), intervalIntegral.integral_const]
    simp
  rw [he]
  have hb := intervalIntegral.norm_integral_le_of_norm_le_const
    (a := a) (b := a+t) (f := fun x => f a-f x) (C := 10*t) (by
      intro x hx
      have hx' : a < x ∧ x ≤ a+t := by
        simpa only [Set.uIoc_of_le (show a ≤ a+t by linarith), Set.mem_Ioc] using hx
      have habs : |a-x| ≤ t := by rw [abs_of_nonpos (by linarith)]; linarith
      simpa only [Real.norm_eq_abs] using (hf a x).trans (by linarith))
  simpa only [Real.norm_eq_abs, add_sub_cancel_left, abs_of_nonneg ht, pow_two,
    mul_assoc] using hb

theorem grid_integral {f : ℝ → ℝ} (hf : ∀ x y, |f x-f y| ≤ 10*|x-y|)
    (A t : ℝ) (ht : 0 ≤ t) (m : ℕ) :
    |t * (∑ j ∈ range m, f (A+j*t)) - ∫ x in A..(A+m*t), f x| ≤
      10*(m : ℝ)*t^2 := by
  have hc := continuous_of_ten_lipschitz hf
  have hsum := intervalIntegral.sum_integral_adjacent_intervals
    (μ := volume) (f := f) (a := fun j : ℕ => A+(j : ℝ)*t) (n := m)
    (fun j _ => hc.intervalIntegrable _ _)
  simp only [Nat.cast_zero, zero_mul, add_zero] at hsum
  rw [← hsum, mul_sum, ← sum_sub_distrib]
  calc
    _ ≤ ∑ j ∈ range m, |t*f (A+j*t) - ∫ x in (A+j*t)..(A+(j+1 : ℕ)*t), f x| :=
      abs_sum_le_sum_abs _ _
    _ ≤ ∑ _j ∈ range m, 10*t^2 := by
      apply sum_le_sum
      intro j hj
      have he : A+((j+1 : ℕ) : ℝ)*t = (A+(j : ℝ)*t)+t := by push_cast; ring
      rw [he]
      exact grid_cell hf (A+j*t) t ht
    _ = _ := by simp; ring

theorem delete_sum_error {s t : Finset ℕ} (ht : t ⊆ s) {f : ℝ → ℝ}
    (hf : ∀ x, |f x| ≤ 1) (K : ℝ) :
    |(∑ b ∈ s, f (b/K)) - ∑ b ∈ t, f (b/K)| ≤ (s.card : ℝ) - t.card := by
  rw [← sum_sdiff ht, add_sub_cancel_right]
  calc
    _ ≤ ∑ b ∈ s \ t, |f (b/K)| := abs_sum_le_sum_abs _ _
    _ ≤ ∑ _b ∈ s \ t, (1 : ℝ) := sum_le_sum (fun b _ => hf _)
    _ = _ := by
      simp only [sum_const, nsmul_eq_mul, mul_one, card_sdiff_of_subset ht]
      rw [Nat.cast_sub (card_le_card ht)]

theorem sorted_transport {s : Finset ℕ} {L : ℕ}
    (hL : ∀ b ∈ s, L ≤ b) {f : ℝ → ℝ}
    (hf : ∀ x y, |f x-f y| ≤ 10*|x-y|) (K : ℝ) (hK : 0 < K) :
    |(∑ b ∈ s, f (b/K)) - ∑ j : Fin s.card, f (((L : ℝ)+j.val)/K)| ≤
      10/K*((∑ b ∈ s, (b : ℝ)) - (s.card : ℝ)*L -
        (s.card : ℝ)*((s.card : ℝ)-1)/2) := by
  let z := s.orderEmbOfFin rfl
  have hz : ∀ j, (L : ℝ)+j.val ≤ z j := by
    intro j
    exact_mod_cast rank_lower z.strictMono (fun i => hL _ (s.orderEmbOfFin_mem rfl i)) j
  have hsum : (∑ b ∈ s, f (b/K)) = ∑ j : Fin s.card, f ((z j : ℝ)/K) :=
    (sum_sorted s (fun b => f (b/K))).symm
  rw [hsum, ← sum_sub_distrib]
  calc
    _ ≤ ∑ j : Fin s.card, |f ((z j : ℝ)/K)-f (((L : ℝ)+j.val)/K)| :=
      abs_sum_le_sum_abs _ _
    _ ≤ ∑ j : Fin s.card, (10/K)*((z j : ℝ)-L-j.val) := by
      apply sum_le_sum
      intro j hj
      have ha : 0 ≤ (z j : ℝ)/K-((L : ℝ)+j.val)/K := by
        exact sub_nonneg.mpr ((div_le_div_iff_of_pos_right hK).mpr (hz j))
      have hl := hf ((z j : ℝ)/K) (((L : ℝ)+j.val)/K)
      rw [abs_of_nonneg ha] at hl
      calc
        _ ≤ 10 * ((z j : ℝ)/K-((L : ℝ)+j.val)/K) := hl
        _ = _ := by ring
    _ = _ := by
      rw [← mul_sum]
      congr 1
      dsimp [z]
      rw [sum_sub_distrib, sum_sub_distrib, sum_sorted, sum_fin_vals]
      simp

end Erdos357
