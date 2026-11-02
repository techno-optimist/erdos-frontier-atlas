import Mathlib

open scoped BigOperators
open Finset

namespace Erdos357

theorem rank_lower {m L : ℕ} {f : Fin m → ℕ}
    (hf : StrictMono f) (hL : ∀ i, L ≤ f i) (i : Fin m) :
    L + i.val ≤ f i := by
  have aux : ∀ n (hn : n < m), L + n ≤ f ⟨n, hn⟩ := by
    intro n
    induction n with
    | zero => intro hn; simpa using hL ⟨0, hn⟩
    | succ n ih =>
      intro hn
      have hn' : n < m := by omega
      have hp := ih hn'
      have hs := hf (show (⟨n, hn'⟩ : Fin m) < ⟨n + 1, hn⟩ by
        change n < n + 1; omega)
      omega
  exact aux i.val i.isLt

theorem rank_upper {m N : ℕ} {f : Fin m → ℕ}
    (hf : StrictMono f) (hN : ∀ i, f i ≤ N) (i : Fin m) :
    f i + (m - 1 - i.val) ≤ N := by
  let g : Fin m → ℕ := fun j => N - f j.rev
  have hg : StrictMono g := by
    intro j l hjl
    have hr : l.rev < j.rev := Fin.rev_lt_rev.mpr hjl
    have hfl := hf hr
    have hj := hN j.rev
    have hl := hN l.rev
    dsimp [g]
    omega
  have hl := rank_lower (L := 0) hg (fun _ => Nat.zero_le _) i.rev
  have hi := hN i
  simp only [g, Fin.rev_rev, Fin.val_rev, zero_add] at hl
  omega

theorem sum_fin_vals (m : ℕ) :
    (∑ i : Fin m, (i.val : ℝ)) = (m : ℝ) * ((m : ℝ) - 1) / 2 := by
  induction m with
  | zero => simp
  | succ m ih =>
    rw [Fin.sum_univ_castSucc]
    simp only [Fin.val_castSucc, Fin.val_last, ih, Nat.cast_add, Nat.cast_one]
    ring

theorem sum_range_vals (m : ℕ) :
    (∑ i ∈ range m, (i : ℝ)) = (m : ℝ) * ((m : ℝ) - 1) / 2 := by
  rw [← Fin.sum_univ_eq_sum_range]
  exact sum_fin_vals m

theorem sum_sorted {α : Type*} [LinearOrder α] (s : Finset α) (f : α → ℝ) :
    (∑ i : Fin s.card, f (s.orderEmbOfFin rfl i)) = ∑ x ∈ s, f x := by
  conv_rhs => rw [← s.map_orderEmbOfFin_univ rfl]
  rw [sum_map]
  rfl

theorem packed_lower (s : Finset ℕ) (L : ℕ) (hL : ∀ x ∈ s, L ≤ x) :
    (s.card : ℝ) * L + (s.card : ℝ) * ((s.card : ℝ) - 1) / 2 ≤
      ∑ x ∈ s, (x : ℝ) := by
  let f := s.orderEmbOfFin rfl
  have hl : ∀ i, L + i.val ≤ f i :=
    rank_lower f.strictMono (fun i => hL _ (s.orderEmbOfFin_mem rfl i))
  have hsum := sum_le_sum (s := (univ : Finset (Fin s.card)))
    (fun i _ => (show (L : ℝ) + i.val ≤ (f i : ℝ) by exact_mod_cast hl i))
  dsimp [f] at hsum
  simpa only [sum_add_distrib, sum_const, card_univ, Fintype.card_fin,
    nsmul_eq_mul, sum_fin_vals, sum_sorted] using hsum

theorem packed_upper (s : Finset ℕ) (N : ℕ) (hN : ∀ x ∈ s, x ≤ N) :
    (∑ x ∈ s, (x : ℝ)) ≤
      (s.card : ℝ) * N - (s.card : ℝ) * ((s.card : ℝ) - 1) / 2 := by
  let f := s.orderEmbOfFin rfl
  have hl : ∀ i, (f i : ℝ) ≤ (N : ℝ) - (s.card : ℝ) + 1 + i.val := by
    intro i
    have hu := rank_upper f.strictMono (fun j => hN _ (s.orderEmbOfFin_mem rfl j)) i
    have hi := i.isLt
    have hu' : f i + s.card ≤ N + 1 + i.val := by omega
    have hu'' : (f i : ℝ) + s.card ≤ (N : ℝ) + 1 + i.val := by exact_mod_cast hu'
    linarith
  have hsum := sum_le_sum (s := (univ : Finset (Fin s.card))) (fun i _ => hl i)
  dsimp [f] at hsum
  simp only [sum_add_distrib, sum_const, card_univ, Fintype.card_fin,
    nsmul_eq_mul, sum_fin_vals, sum_sorted] at hsum
  nlinarith

theorem packed_bad_count (s : Finset ℕ) (N L : ℕ) (hN : ∀ x ∈ s, x ≤ N) :
    ((s.filter (· < L)).card : ℝ) * ((N : ℝ) - s.card + 1 - L) ≤
      (s.card : ℝ) * N - (s.card : ℝ) * ((s.card : ℝ) - 1) / 2 -
        ∑ x ∈ s, (x : ℝ) := by
  let f := s.orderEmbOfFin rfl
  let D : Fin s.card → ℝ := fun i => (N : ℝ) - s.card + 1 + i.val - f i
  let b : Finset (Fin s.card) := univ.filter (fun i => f i < L)
  have hD : ∀ i, 0 ≤ D i := by
    intro i
    have hu := rank_upper f.strictMono (fun j => hN _ (s.orderEmbOfFin_mem rfl j)) i
    have hi := i.isLt
    have hn : f i + s.card ≤ N + 1 + i.val := by omega
    have hn' : (f i : ℝ) + s.card ≤ (N : ℝ) + 1 + i.val := by exact_mod_cast hn
    dsimp [D]
    linarith
  have hb : ∀ i ∈ b, (N : ℝ) - s.card + 1 - L ≤ D i := by
    intro i hi
    have hiL : f i < L := (mem_filter.mp hi).2
    have hiL' : (f i : ℝ) ≤ L := by exact_mod_cast hiL.le
    have hi0 : (0 : ℝ) ≤ i.val := Nat.cast_nonneg _
    dsimp [D]
    linarith
  have hcard : b.card = (s.filter (· < L)).card := by
    have him : b.image f = s.filter (· < L) := by
      dsimp [b, f]
      have he := filter_image (s := (univ : Finset (Fin s.card)))
        (f := (s.orderEmbOfFin rfl)) (p := fun x => x < L)
      rw [s.image_orderEmbOfFin_univ rfl] at he
      exact he.symm
    rw [← him, card_image_of_injective _ f.injective]
  calc
    _ = ∑ i ∈ b, ((N : ℝ) - s.card + 1 - L) := by
      rw [sum_const, nsmul_eq_mul, hcard]
    _ ≤ ∑ i ∈ b, D i := sum_le_sum hb
    _ ≤ ∑ i : Fin s.card, D i :=
      sum_le_sum_of_subset_of_nonneg (filter_subset _ _) (fun i _ _ => hD i)
    _ = _ := by
      dsimp [D, f]
      rw [sum_sub_distrib, sum_add_distrib, sum_const, sum_fin_vals]
      simp only [card_univ, Fintype.card_fin, nsmul_eq_mul, sum_sorted]
      ring

end Erdos357
