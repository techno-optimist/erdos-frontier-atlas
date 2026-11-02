import Erdos357.Stability
import Erdos357.Transport

open scoped BigOperators
open Finset MeasureTheory

namespace Erdos357

noncomputable def empirical (a : ℕ → ℕ) (k h : ℕ) (f : ℝ → ℝ) : ℝ :=
  (∑ b ∈ sums a k h, f ((b : ℝ)/k)) / k

/-- Step 4 of `PROOF.md`, for every bounded 10-Lipschitz real test function. -/
theorem step4_test_function {k N h : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hk : 10^22 ≤ k)
    (hN : (N : ℝ) ≤ ((3 : ℝ)/2+1/10^10)*k) (hh : h ≤ 8)
    {f : ℝ → ℝ} (hf : ∀ x, |f x| ≤ 1)
    (hlip : ∀ x y, |f x-f y| ≤ 10*|x-y|) :
    |empirical a k h f - ∫ t in (1/2 : ℝ)..((h : ℝ)+1/2), f t| ≤ 1/40 := by
  have hk' : (10000000000000000000000 : ℝ) ≤ k := by exact_mod_cast hk
  have hkpos : (0 : ℝ) < k := by positivity
  have hkne : (k : ℝ) ≠ 0 := ne_of_gt hkpos
  have hc := continuous_of_ten_lipschitz hlip
  let s := sums a k h
  let t := goodSums a k h (cutoff k)
  let M : ℝ := t.card
  let L : ℝ := cutoff k
  let d : ℝ := (h : ℝ)*k-M
  let D : ℝ := displacement t (cutoff k)
  let A : ℝ := (∑ b ∈ s, f ((b : ℝ)/k)) / k
  let B : ℝ := (∑ b ∈ t, f ((b : ℝ)/k)) / k
  let G : ℝ := (∑ j : Fin t.card, f ((L+j.val)/k)) / k
  let J : ℝ := ∫ x in L/k..((L+M)/k), f x
  let I : ℝ := ∫ x in (1/2 : ℝ)..((h : ℝ)+1/2), f x
  have ht : t ⊆ s := filter_subset _ _
  obtain ⟨hd0, hdhi⟩ := missing_bounds ha hk hN hh
  change 0 ≤ d at hd0
  change d ≤ (k : ℝ)/6000 at hdhi
  have hddiv : d/(k : ℝ) ≤ 1/6000 := (div_le_iff₀ hkpos).mpr (by linarith)
  have hddiv0 : 0 ≤ d/(k : ℝ) := div_nonneg hd0 hkpos.le
  obtain ⟨hD0, hDhi⟩ := step3_packing_stability ha hk hN hh
  change 0 ≤ D at hD0
  change D/(k : ℝ)^2 ≤ 9/4000 at hDhi
  have hcard := card_indices_real (show h ≤ k by omega)
  have hsM : (s.card : ℝ)-M ≤ d := by
    have htri : 0 ≤ (h : ℝ)*((h : ℝ)-1) := by
      rcases Nat.eq_zero_or_pos h with hz | hp
      · simp [hz]
      · have : (1 : ℝ) ≤ h := by exact_mod_cast hp
        positivity
    have hsc : s.card = (indices k h).card := card_sums ha
    dsimp [d]
    rw [hsc, hcard]
    linarith
  have hAB : |A-B| ≤ 1/6000 := by
    have he := delete_sum_error ht hf (k : ℝ)
    have he' := div_le_div_of_nonneg_right he hkpos.le
    dsimp [A, B]
    rw [← sub_div, abs_div, abs_of_pos hkpos]
    exact he'.trans ((div_le_div_of_nonneg_right hsM hkpos.le).trans hddiv)
  have hBG : |B-G| ≤ 9/400 := by
    have he := sorted_transport (s := t) (L := cutoff k)
      (fun _ hb => (mem_filter.mp hb).2) hlip (k : ℝ) hkpos
    change |(∑ b ∈ t, f ((b : ℝ)/k)) -
      ∑ j : Fin t.card, f ((L+j.val)/k)| ≤ 10/(k : ℝ)*D at he
    have he' := div_le_div_of_nonneg_right he hkpos.le
    have hr : (10/(k : ℝ)*D)/k = 10*(D/(k : ℝ)^2) := by ring
    rw [hr] at he'
    dsimp [B, G]
    rw [← sub_div, abs_div, abs_of_pos hkpos]
    linarith
  have hM8 : M ≤ 8*(k : ℝ) := by
    have hh' : (h : ℝ) ≤ 8 := by exact_mod_cast hh
    have hp := mul_le_mul_of_nonneg_right hh' hkpos.le
    dsimp [d] at hd0
    linarith
  have hGJ : |G-J| ≤ 80/(k : ℝ) := by
    have he := grid_integral hlip (L/(k : ℝ)) (1/(k : ℝ))
      (by positivity) t.card
    have hgrid : (∑ j ∈ range t.card, f (L/(k : ℝ)+(j : ℝ)*(1/k))) =
        ∑ j : Fin t.card, f ((L+j.val)/k) := by
      rw [← Fin.sum_univ_eq_sum_range]
      apply sum_congr rfl
      intro j hj
      congr 1
      ring
    rw [hgrid] at he
    have hep : L/(k : ℝ) + (t.card : ℝ)*(1/k) = (L+M)/k := by
      dsimp [M]; ring
    rw [hep] at he
    have he' : |G-J| ≤ 10*M/(k : ℝ)^2 := by
      have heleft : (1/(k : ℝ))*(∑ j : Fin t.card, f ((L+j.val)/k)) = G := by
        dsimp [G]
        ring
      rw [heleft] at he
      change |G-J| ≤ 10*M*(1/(k : ℝ))^2 at he
      calc
        _ ≤ 10*M*(1/(k : ℝ))^2 := he
        _ = _ := by ring
    have hr : 10*(8*(k : ℝ))/(k : ℝ)^2 = 80/(k : ℝ) := by field_simp; ring
    calc
      _ ≤ 10*M/(k : ℝ)^2 := he'
      _ ≤ 10*(8*(k : ℝ))/(k : ℝ)^2 := div_le_div_of_nonneg_right
        (mul_le_mul_of_nonneg_left hM8 (by norm_num)) (sq_nonneg _)
      _ = _ := hr
  have hLbounds := cutoff_bounds k
  have hLlo : (1/2 : ℝ)-1/10000 ≤ L/k := by
    apply (le_div_iff₀ hkpos).mpr
    exact hLbounds.1
  have hLhi : L/(k : ℝ) ≤ (1/2 : ℝ)-1/10000+1/k := by
    apply (div_le_iff₀ hkpos).mpr
    have hh' : ((1/2 : ℝ)-1/10000+1/k)*k =
        ((1/2 : ℝ)-1/10000)*k+1 := by field_simp
    rw [hh']
    exact hLbounds.2
  have hinv : 0 ≤ 1/(k : ℝ) := by positivity
  have heL : |(1/2 : ℝ)-L/k| ≤ 1/10000+1/k := by
    rw [abs_le]
    constructor <;> linarith
  have heR : |((h : ℝ)+1/2)-(L+M)/k| ≤ 1/10000+1/k+d/k := by
    have heq : ((h : ℝ)+1/2)-(L+M)/k = ((1/2 : ℝ)-L/k)+d/k := by
      dsimp [d]
      field_simp
      ring
    rw [heq]
    calc
      _ ≤ |(1/2 : ℝ)-L/k|+|d/(k : ℝ)| := abs_add_le _ _
      _ ≤ _ := by rw [abs_of_nonneg hddiv0]; linarith
  have hJI : |J-I| ≤ 2/10000+2/(k : ℝ)+1/6000 := by
    have he := integral_endpoints hc hf (L/(k : ℝ)) ((L+M)/k) (1/2) ((h : ℝ)+1/2)
    change |J-I| ≤ _ at he
    simp only [div_eq_mul_inv] at he heL heR hddiv ⊢
    linarith
  have hall : |A-I| ≤ |A-B|+|B-G|+|G-J|+|J-I| := by
    have h1 := abs_sub_le A B G
    have h2 := abs_sub_le A G J
    have h3 := abs_sub_le A J I
    linarith
  have herror : 82/(k : ℝ) ≤ 1/40-9/400-2/6000-2/10000 := by
    apply (div_le_iff₀ hkpos).mpr
    norm_num only [one_div, inv_div, inv_one] at *
    linarith
  change |A-I| ≤ 1/40
  simp only [div_eq_mul_inv] at hAB hBG hGJ hJI hall herror ⊢
  linarith

end Erdos357
