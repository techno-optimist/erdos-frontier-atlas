import Solution
open Erdos357 Finset

/-! Non-vacuity check: the k = 19, N = 29 witness satisfies every hypothesis of the
main theorem except `10 ^ 22 ≤ k`. Kernel `decide` only (no native_decide). -/

def w : Fin 19 → ℕ := ![4, 1, 2, 10, 22, 15, 21, 24, 28, 29, 27, 16, 26, 20, 18, 23, 25, 19, 11]
def wl : List ℕ := [4, 1, 2, 10, 22, 15, 21, 24, 28, 29, 27, 16, 26, 20, 18, 23, 25, 19, 11]
def bs (i r : ℕ) : ℕ := ((wl.drop i).take r).sum

theorem w_inj : Function.Injective w := by decide
theorem w_range : ∀ i, 1 ≤ w i ∧ w i ≤ 29 := by decide

theorem block_eq : ∀ i < 20, ∀ r < 20, i + r ≤ 19 → block (extend w) r i = bs i r := by
  decide +kernel

set_option synthInstance.maxSize 4096 in
set_option synthInstance.maxHeartbeats 400000 in
set_option maxHeartbeats 4000000 in
theorem bs_distinct : ∀ i < 19, ∀ r < 19, ∀ j < 19, ∀ s < 19,
    i + r + 1 ≤ 19 → j + s + 1 ≤ 19 → bs i (r + 1) = bs j (s + 1) → i = j ∧ r = s := by
  decide +kernel

theorem w_blocks : ∀ u v u' v' : Fin 19, u ≤ v → u' ≤ v' →
    (∑ i ∈ Icc u v, w i) = (∑ i ∈ Icc u' v', w i) → u = u' ∧ v = v' := by
  intro u v u' v' h1 h2 he
  rw [← block_as_fin_Icc w u v h1, ← block_as_fin_Icc w u' v' h2] at he
  have hu := u.isLt; have hv := v.isLt; have hu' := u'.isLt; have hv' := v'.isLt
  have h1' : u.val ≤ v.val := h1
  have h2' : u'.val ≤ v'.val := h2
  rw [block_eq u.val (by omega) (v.val + 1 - u.val) (by omega) (by omega),
    block_eq u'.val (by omega) (v'.val + 1 - u'.val) (by omega) (by omega)] at he
  have key := bs_distinct u.val hu (v.val - u.val) (by omega) u'.val hu' (v'.val - u'.val) (by omega)
    (by omega) (by omega)
    (by rw [show v.val - u.val + 1 = v.val + 1 - u.val by omega,
            show v'.val - u'.val + 1 = v'.val + 1 - u'.val by omega]; exact he)
  exact ⟨Fin.ext key.1, Fin.ext (by omega)⟩

/-- All non-`hk` hypotheses of `erdos357_any_order_improvement` hold at k = 19, N = 29. -/
theorem witness_satisfies_hypotheses :
    ∃ x : Fin 19 → ℕ, Function.Injective x ∧ (∀ i, 1 ≤ x i ∧ x i ≤ 29) ∧
      (∀ u v u' v' : Fin 19, u ≤ v → u' ≤ v' →
        (∑ i ∈ Icc u v, x i) = (∑ i ∈ Icc u' v', x i) → u = u' ∧ v = v') :=
  ⟨w, w_inj, w_range, w_blocks⟩

/-- Sensitivity: hblocks really constrains the row (a repeated block sum is rejected).
    Row 1,2,3: blocks [1,2] and [3] both sum to 3. -/
theorem hblocks_rejects_bad_row :
    ¬ (∀ u v u' v' : Fin 3, u ≤ v → u' ≤ v' →
        (∑ i ∈ Icc u v, (![1, 2, 3] : Fin 3 → ℕ) i) = (∑ i ∈ Icc u' v', (![1, 2, 3] : Fin 3 → ℕ) i) →
        u = u' ∧ v = v') := by
  intro h
  have := h 0 1 2 2 (by decide) (by decide) (by decide +kernel)
  exact absurd this.1 (by decide)

#print axioms witness_satisfies_hypotheses
#print axioms hblocks_rejects_bad_row
