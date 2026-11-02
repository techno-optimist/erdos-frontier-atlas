import Mathlib

open scoped BigOperators
open Finset

namespace Erdos357

def block (a : ℕ → ℕ) (r i : ℕ) : ℕ :=
  ∑ j ∈ range r, a (i + j)

def span (a : ℕ → ℕ) (k : ℕ) : ℝ :=
  ∑ i ∈ range k, (a i : ℝ)

structure Admissible (k N : ℕ) (a : ℕ → ℕ) : Prop where
  positive : ∀ i < k, 1 ≤ a i
  bounded : ∀ i < k, a i ≤ N
  injective : Set.InjOn a {i | i < k}
  distinct : ∀ r i s j, 0 < r → i + r ≤ k → 0 < s → j + s ≤ k →
    block a r i = block a s j → r = s ∧ i = j

def extend {k : ℕ} (x : Fin k → ℕ) (i : ℕ) : ℕ :=
  if hi : i < k then x ⟨i, hi⟩ else 0

theorem block_as_fin_Icc {k : ℕ} (x : Fin k → ℕ) (u v : Fin k) (huv : u ≤ v) :
    block (extend x) (v.val + 1 - u.val) u.val = ∑ i ∈ Icc u v, x i := by
  unfold block
  refine sum_bij (fun j hj => (⟨u.val + j, by
    have hj' := mem_range.mp hj
    have hv := v.isLt
    have hu : u.val ≤ v.val := huv
    omega⟩ : Fin k)) ?_ ?_ ?_ ?_
  · intro j hj
    have hj' := mem_range.mp hj
    have hu : u.val ≤ v.val := huv
    simp only [mem_Icc, Fin.le_iff_val_le_val]
    constructor <;> omega
  · intro j hj l hl he
    have := congrArg Fin.val he
    dsimp at this
    omega
  · intro i hi
    obtain ⟨hui, hiv⟩ := mem_Icc.mp hi
    have hui' : u.val ≤ i.val := hui
    have hiv' : i.val ≤ v.val := hiv
    refine ⟨i.val - u.val, mem_range.mpr (by omega), ?_⟩
    apply Fin.ext
    dsimp
    omega
  · intro j hj
    have hj' := mem_range.mp hj
    have hv := v.isLt
    have hu : u.val ≤ v.val := huv
    simp only [extend, dif_pos (show u.val + j < k by omega)]

theorem admissible_extend {k N : ℕ} (x : Fin k → ℕ)
    (hinj : Function.Injective x)
    (hrange : ∀ i, 1 ≤ x i ∧ x i ≤ N)
    (hblocks : ∀ u v u' v' : Fin k, u ≤ v → u' ≤ v' →
      (∑ i ∈ Icc u v, x i) = (∑ i ∈ Icc u' v', x i) →
      u = u' ∧ v = v') :
    Admissible k N (extend x) := by
  constructor
  · intro i hi
    simpa [extend, hi] using (hrange ⟨i, hi⟩).1
  · intro i hi
    simpa [extend, hi] using (hrange ⟨i, hi⟩).2
  · intro i hi j hj he
    simp only [Set.mem_ofPred_eq] at hi hj
    have he' : x ⟨i, hi⟩ = x ⟨j, hj⟩ := by simpa [extend, hi, hj] using he
    exact congrArg Fin.val (hinj he')
  · intro r i s j hr hir hs hjs he
    let u : Fin k := ⟨i, by omega⟩
    let v : Fin k := ⟨i + r - 1, by omega⟩
    let u' : Fin k := ⟨j, by omega⟩
    let v' : Fin k := ⟨j + s - 1, by omega⟩
    have huv : u ≤ v := by change i ≤ i + r - 1; omega
    have huv' : u' ≤ v' := by change j ≤ j + s - 1; omega
    have hlen : v.val + 1 - u.val = r := by dsimp [u, v]; omega
    have hlen' : v'.val + 1 - u'.val = s := by dsimp [u', v']; omega
    have h1 := block_as_fin_Icc x u v huv
    have h2 := block_as_fin_Icc x u' v' huv'
    rw [hlen] at h1
    rw [hlen'] at h2
    have hh : (∑ t ∈ Icc u v, x t) = ∑ t ∈ Icc u' v', x t := by
      rw [← h1, ← h2]
      exact he
    obtain ⟨hu, hv⟩ := hblocks u v u' v' huv huv' hh
    have hstart := congrArg Fin.val hu
    have hend := congrArg Fin.val hv
    dsimp [u, u', v, v'] at hstart hend
    constructor <;> omega

abbrev BlockIndex := Σ _ : ℕ, ℕ

def indices (k h : ℕ) : Finset BlockIndex :=
  (range h).sigma fun r => range (k - r)

def blockValue (a : ℕ → ℕ) (b : BlockIndex) : ℕ := block a (b.1 + 1) b.2

@[simp] theorem mem_indices {k h : ℕ} {b : BlockIndex} :
    b ∈ indices k h ↔ b.1 < h ∧ b.2 + b.1 < k := by
  simp only [indices, mem_sigma, mem_range]
  omega

theorem blockValue_injOn {k N h : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a) :
    Set.InjOn (blockValue a) (indices k h : Set BlockIndex) := by
  intro b hb c hc he
  have hb' := mem_indices.mp hb
  have hc' := mem_indices.mp hc
  obtain ⟨hr, hi⟩ := ha.distinct (b.1 + 1) b.2 (c.1 + 1) c.2
    (by omega) (by omega) (by omega) (by omega) he
  cases b with
  | mk r i =>
    cases c with
    | mk s j =>
      dsimp at hr hi
      have : r = s := by omega
      subst s
      subst j
      rfl

theorem block_positive {k N : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a)
    {r i : ℕ} (hr : 0 < r) (hir : i + r ≤ k) : 1 ≤ block a r i := by
  have hi : i < k := by omega
  calc
    1 ≤ a i := ha.positive i hi
    _ = a (i + 0) := by simp
    _ ≤ block a r i := by
      unfold block
      exact single_le_sum (f := fun j => a (i + j))
        (fun j _ => Nat.zero_le _) (mem_range.mpr hr)

theorem blockValue_positive {k N h : ℕ} {a : ℕ → ℕ} (ha : Admissible k N a)
    {b : BlockIndex} (hb : b ∈ indices k h) : 1 ≤ blockValue a b := by
  have hb' := mem_indices.mp hb
  exact block_positive ha (by omega) (by omega)

theorem span_nonneg (a : ℕ → ℕ) (k : ℕ) : 0 ≤ span a k := by
  exact sum_nonneg fun i _ => Nat.cast_nonneg _

end Erdos357
