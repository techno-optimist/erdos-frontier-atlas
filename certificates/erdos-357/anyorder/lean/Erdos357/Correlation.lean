import Erdos357.Empirical

open scoped BigOperators
open Finset MeasureTheory

namespace Erdos357

theorem pi_lt_ten_thirds : Real.pi < (10 : ℝ)/3 := by
  have hp : Real.pi < (63 : ℝ)/20 := by
    convert Real.pi_lt_d2 using 1
    norm_num
  linarith

noncomputable def wave (r t : ℝ) : ℝ := Real.cos (3*Real.pi*(t-r))

theorem wave_bounded (r t : ℝ) : |wave r t| ≤ 1 := Real.abs_cos_le_one _

theorem wave_lipschitz (r x y : ℝ) : |wave r x-wave r y| ≤ 10*|x-y| := by
  have hp : 0 ≤ 3*Real.pi := by positivity
  have he : 3*Real.pi*(x-r)-3*Real.pi*(y-r) = (3*Real.pi)*(x-y) := by ring
  have hc := Real.abs_cos_sub_cos_le (3*Real.pi*(x-r)) (3*Real.pi*(y-r))
  rw [he, abs_mul, abs_of_nonneg hp] at hc
  have hab := abs_nonneg (x-y)
  have hb := pi_lt_ten_thirds
  change |wave r x-wave r y| ≤ _ at hc
  nlinarith

theorem wave_integral (r : ℝ) :
    (∫ t in (r-1/2)..(r+1/2), wave r t) = -2/(3*Real.pi) := by
  have hp : 3*Real.pi ≠ 0 := by positivity
  have he : (fun t => wave r t) = (fun t => Real.cos (3*Real.pi*t-3*Real.pi*r)) := by
    funext t
    dsimp [wave]
    congr 1
    ring
  rw [he, intervalIntegral.integral_comp_mul_sub Real.cos hp,
    integral_cos]
  have hleft : 3*Real.pi*(r-1/2)-3*Real.pi*r = -(Real.pi/2+Real.pi) := by ring
  have hright : 3*Real.pi*(r+1/2)-3*Real.pi*r = Real.pi/2+Real.pi := by ring
  rw [hleft, hright]
  simp only [Real.sin_neg, Real.sin_add_pi, Real.sin_pi_div_two,
    neg_neg, smul_eq_mul]
  ring

noncomputable def correlation (a : ℕ → ℕ) (k r : ℕ) : ℝ :=
  ∑ i ∈ range (k+1-r), wave (r : ℝ) ((block a r i : ℝ)/k)

theorem empirical_increment {k N : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a)
    (r : ℕ) (f : ℝ → ℝ) :
    empirical a k (r+1) f - empirical a k r f =
      (∑ i ∈ range (k-r), f ((block a (r+1) i : ℝ)/k)) / k := by
  unfold empirical
  rw [sum_sums ha, sum_sums ha]
  simp only [indices, sum_sigma, blockValue, sum_range_succ]
  ring

/-- Step 5 of `PROOF.md`: all eight correlations are uniformly negative. -/
theorem step5_negative_correlations {k N r : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hk : 10^22 ≤ k)
    (hN : (N : ℝ) ≤ ((3 : ℝ)/2+1/10^10)*k) (hr : 1 ≤ r) (hr8 : r ≤ 8) :
    correlation a k r ≤ -3*(k : ℝ)/20 := by
  obtain ⟨r, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (show r ≠ 0 by omega)
  have hkpos : (0 : ℝ) < k := by
    have hkn : 0 < k := by omega
    exact_mod_cast hkn
  let f := wave ((r+1 : ℕ) : ℝ)
  have hf : ∀ x, |f x| ≤ 1 := wave_bounded _
  have hlip : ∀ x y, |f x-f y| ≤ 10*|x-y| := wave_lipschitz _
  have h1 := step4_test_function ha hk hN hr8 hf hlip
  have h0 := step4_test_function ha hk hN (show r ≤ 8 by omega) hf hlip
  have hc := continuous_of_ten_lipschitz hlip
  have hi := intervalIntegral.integral_interval_sub_left
    (μ := volume) (f := f)
    (hc.intervalIntegrable (1/2) (((r+1 : ℕ) : ℝ)+1/2))
    (hc.intervalIntegrable (1/2) ((r : ℝ)+1/2))
  have he : (r : ℝ)+1/2 = ((r+1 : ℕ) : ℝ)-1/2 := by push_cast; ring
  rw [he] at hi
  have hval := wave_integral ((r+1 : ℕ) : ℝ)
  change (∫ t in (((r+1 : ℕ) : ℝ)-1/2)..(((r+1 : ℕ) : ℝ)+1/2), f t) = _ at hval
  rw [hval] at hi
  rw [← he] at hi
  have hec := empirical_increment ha r f
  have hecorr : correlation a k (r+1)/(k : ℝ) =
      empirical a k (r+1) f - empirical a k r f := by
    rw [hec]
    simp only [correlation, Nat.add_sub_add_right]
    rfl
  have hp : -2/(3*Real.pi) ≤ -(1 : ℝ)/5 := by
    have hpi := pi_lt_ten_thirds
    have hpp : 0 < 3*Real.pi := by positivity
    apply (div_le_iff₀ hpp).mpr
    linarith
  have hh1 := (abs_le.mp h1).2
  have hh0 := (abs_le.mp h0).1
  have hfinal : correlation a k (r+1)/(k : ℝ) ≤ -(3 : ℝ)/20 := by
    rw [hecorr]
    linarith
  have := (div_le_iff₀ hkpos).mp hfinal
  linarith

end Erdos357
