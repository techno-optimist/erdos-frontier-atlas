import Erdos357.Span

open scoped BigOperators
open Finset

namespace Erdos357

def entries (a : ℕ → ℕ) (k : ℕ) : Finset ℕ := (range k).image a

theorem entries_inj {k N : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    Set.InjOn a (range k : Set ℕ) := by
  intro i hi j hj he
  exact ha.injective (mem_range.mp hi) (mem_range.mp hj) he

theorem card_entries {k N : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    (entries a k).card = k := by
  rw [entries, card_image_of_injOn (entries_inj ha), card_range]

theorem sum_entries {k N : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    (∑ b ∈ entries a k, (b : ℝ)) = span a k := sum_image (entries_inj ha)

theorem entry_bound {k N : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a)
    {b : ℕ} (hb : b ∈ entries a k) : b ≤ N := by
  obtain ⟨i, hi, rfl⟩ := mem_image.mp hb
  exact ha.bounded i (mem_range.mp hi)

theorem span_upper {k N : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    span a k ≤ (k : ℝ) * N - (k : ℝ) * ((k : ℝ) - 1) / 2 := by
  have h := packed_upper (entries a k) N (fun _ hb => entry_bound ha hb)
  rwa [card_entries ha, sum_entries ha] at h

noncomputable def cutoff (k : ℕ) : ℕ := ⌈((1 : ℝ) / 2 - 1 / 10000) * k⌉₊

def badEntries (a : ℕ → ℕ) (k L : ℕ) : Finset ℕ :=
  (entries a k).filter (· < L)

theorem cutoff_bounds (k : ℕ) :
    ((1 : ℝ) / 2 - 1 / 10000) * k ≤ (cutoff k : ℝ) ∧
    (cutoff k : ℝ) ≤ ((1 : ℝ) / 2 - 1 / 10000) * k + 1 := by
  constructor
  · exact Nat.le_ceil _
  · exact (Nat.ceil_lt_add_one (by positivity)).le

theorem large_sqrt {k : ℕ} (hk : 10^22 ≤ k) :
    10^11 ≤ Real.sqrt (k : ℝ) ∧ Real.sqrt (k : ℝ) ≤ (k : ℝ) / 10^11 := by
  have hk' : (10 : ℝ)^22 ≤ k := by exact_mod_cast hk
  have ht0 := Real.sqrt_nonneg (k : ℝ)
  have ht2 := Real.sq_sqrt (Nat.cast_nonneg k)
  have hl : (10 : ℝ)^11 ≤ Real.sqrt k := by nlinarith
  constructor
  · exact hl
  · nlinarith

theorem span_upper_near {k N : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a)
    (hN : (N : ℝ) ≤ ((3 : ℝ)/2 + 1/10^10) * k) :
    span a k ≤ (1 + 1/(10 : ℝ)^10) * (k : ℝ)^2 + k/2 := by
  have hu := span_upper ha
  have hn := mul_le_mul_of_nonneg_left hN (Nat.cast_nonneg k : (0 : ℝ) ≤ k)
  nlinarith

/-- Step 2 of `PROOF.md`: at most `k/250000` entries lie below the cutoff. -/
theorem step2_few_small {k N : ℕ} {a : ℕ → ℕ}
    (ha : Admissible k N a) (hk : 10^22 ≤ k)
    (hN : (N : ℝ) ≤ ((3 : ℝ)/2 + 1/10^10) * k) :
    ((badEntries a k (cutoff k)).card : ℝ) ≤ (k : ℝ) / 250000 := by
  have hk1 : 1 ≤ k := by omega
  have hk' : (10 : ℝ)^22 ≤ k := by exact_mod_cast hk
  have hkpos : (0 : ℝ) < k := by positivity
  have hslo := step1_span ha hk1
  have hshi := span_upper ha
  have hsnear := span_upper_near ha hN
  obtain ⟨htlo, hthi⟩ := large_sqrt hk
  obtain ⟨hLlo, hLhi⟩ := cutoff_bounds k
  let E : ℝ := (k : ℝ) * N - (k : ℝ) * ((k : ℝ) - 1) / 2 - span a k
  have hNmul := mul_le_mul_of_nonneg_left hN hkpos.le
  have hE : E ≤ (2 / (10 : ℝ)^10) * (k : ℝ)^2 := by
    have ht := mul_le_mul_of_nonneg_left hthi hkpos.le
    have hkk := mul_le_mul_of_nonneg_left hk' hkpos.le
    dsimp [E]
    nlinarith
  have hB : (k : ℝ)/2 - 2*Real.sqrt k + 1/2 ≤ (N : ℝ) - k + 1 := by
    nlinarith
  have hBL : (k : ℝ)/20000 ≤ (N : ℝ) - k + 1 - cutoff k := by
    nlinarith
  have hq := packed_bad_count (entries a k) N (cutoff k)
    (fun _ hb => entry_bound ha hb)
  rw [card_entries ha, sum_entries ha] at hq
  change ((badEntries a k (cutoff k)).card : ℝ) *
    ((N : ℝ) - k + 1 - cutoff k) ≤ E at hq
  have hq0 : (0 : ℝ) ≤ (badEntries a k (cutoff k)).card := Nat.cast_nonneg _
  have hprod := mul_le_mul_of_nonneg_left hBL hq0
  nlinarith

end Erdos357
