import Std

/-!
Finite event transport. All inputs are explicit; no arithmetic distribution
result is assumed. Lists may contain repeated observations or coordinates.
-/
namespace DensityTransport

/-- Sum a natural-valued function over an observation list. -/
def total {α : Type} : List α → (α → Nat) → Nat
  | [], _ => 0
  | x :: xs, f => f x + total xs f

/-- Boolean indicator, with value zero or one. -/
def bit (b : Bool) : Nat := if b then 1 else 0

def count {α : Type} (xs : List α) (p : α → Bool) : Nat :=
  total xs (fun x => bit (p x))

/-- Number of observations where two event indicators disagree. -/
def discrepancy {α : Type} (xs : List α) (p q : α → Bool) : Nat :=
  count xs (fun x => p x != q x)

/-- One-sided containment error: observations in p but outside q. -/
def leakage {α : Type} (xs : List α) (p q : α → Bool) : Nat :=
  count xs (fun x => p x && !q x)

theorem total_add {α : Type} (xs : List α) (f g : α → Nat) :
    total xs (fun x => f x + g x) = total xs f + total xs g := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp only [total, ih]; omega

theorem total_zero {α : Type} (xs : List α) : total xs (fun _ => 0) = 0 := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp [total, ih]

theorem total_mono {α : Type} (xs : List α) (f g : α → Nat)
    (h : ∀ x, f x ≤ g x) : total xs f ≤ total xs g := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons x xs ih => simp only [total]; have hx := h x; omega

theorem total_swap {α ι : Type} (xs : List α) (is : List ι) (f : α → ι → Nat) :
    total xs (fun x => total is (f x)) = total is (fun i => total xs (fun x => f x i)) := by
  induction xs with
  | nil => simp only [total]; exact (total_zero is).symm
  | cons x xs ih => simp only [total, ih]; exact (total_add is (f x) _).symm

theorem discrepancy_balance {α : Type} (xs : List α) (p q : α → Bool) :
    discrepancy xs p q + count xs p = count xs q + 2 * leakage xs p q := by
  induction xs with
  | nil => simp [discrepancy, count, leakage, total]
  | cons x xs ih =>
    cases hp : p x <;> cases hq : q x <;>
      simp_all [discrepancy, count, leakage, total, bit] <;> omega

/-- One-sided error plus an upper marginal imbalance controls full discrepancy. -/
theorem one_sided_transport {α : Type} (xs : List α) (p q : α → Bool)
    (e g : Nat) (he : leakage xs p q ≤ e)
    (hg : count xs q ≤ count xs p + g) :
    discrepancy xs p q ≤ 2 * e + g := by
  have h := discrepancy_balance xs p q
  omega

/-- Every event count differs by at most its discrepancy, in both directions. -/
theorem count_stability {α : Type} (xs : List α) (p q : α → Bool) :
    count xs p ≤ count xs q + discrepancy xs p q ∧
    count xs q ≤ count xs p + discrepancy xs p q := by
  induction xs with
  | nil => simp [count, discrepancy, total]
  | cons x xs ih =>
    cases hp : p x <;> cases hq : q x <;>
      simp_all [count, discrepancy, total, bit] <;> omega

/-- Intersections are stable under replacement of each input event. -/
theorem intersection_stability {α : Type} (xs : List α) (p q r s : α → Bool) :
    discrepancy xs (fun x => p x && r x) (fun x => q x && s x) ≤
      discrepancy xs p q + discrepancy xs r s := by
  induction xs with
  | nil => simp [discrepancy, count, total]
  | cons x xs ih =>
    cases hp : p x <;> cases hq : q x <;> cases hr : r x <;> cases hs : s x <;>
      simp_all [discrepancy, count, total, bit] <;> omega

/-- Replacing two coordinates costs at most the sum of their explicit budgets. -/
theorem intersection_one_sided_transport {α : Type} (xs : List α)
    (p q r s : α → Bool) (e₁ g₁ e₂ g₂ : Nat)
    (h₁ : leakage xs p q ≤ e₁) (m₁ : count xs q ≤ count xs p + g₁)
    (h₂ : leakage xs r s ≤ e₂) (m₂ : count xs s ≤ count xs r + g₂) :
    discrepancy xs (fun x => p x && r x) (fun x => q x && s x) ≤
      (2 * e₁ + g₁) + (2 * e₂ + g₂) := by
  have h := intersection_stability xs p q r s
  have a := one_sided_transport xs p q e₁ g₁ h₁ m₁
  have b := one_sided_transport xs r s e₂ g₂ h₂ m₂
  omega

/-- Zero coordinate discrepancy means identical observed Boolean vectors. -/
theorem map_eq_of_zero {ι : Type} (is : List ι) (a b : ι → Bool)
    (h : total is (fun i => bit (a i != b i)) = 0) : is.map a = is.map b := by
  induction is with
  | nil => rfl
  | cons i is ih =>
    simp only [total] at h
    have ht : total is (fun j => bit (a j != b j)) = 0 := by omega
    have hi : a i = b i := by
      cases ha : a i <;> cases hb : b i <;> simp_all [bit]
    simp only [List.map_cons, hi, ih ht]

/-- Any Boolean statistic of a finite vector changes only if a coordinate changes. -/
theorem event_indicator_bound {ι : Type} (is : List ι) (a b : ι → Bool)
    (event : List Bool → Bool) :
    bit (event (is.map a) != event (is.map b)) ≤
      total is (fun i => bit (a i != b i)) := by
  by_cases h : total is (fun i => bit (a i != b i)) = 0
  · have hm := map_eq_of_zero is a b h
    simp [hm, bit]
  · have hb : bit (event (is.map a) != event (is.map b)) ≤ 1 := by
      cases event (is.map a) <;> cases event (is.map b) <;> decide
    omega

/-- Stability of any event in any fixed finite Boolean joint law. -/
theorem joint_event_stability {α ι : Type} (xs : List α) (is : List ι)
    (A B : ι → α → Bool) (event : List Bool → Bool) :
    discrepancy xs (fun x => event (is.map (fun i => A i x)))
      (fun x => event (is.map (fun i => B i x))) ≤
      total is (fun i => discrepancy xs (A i) (B i)) := by
  have hp := total_mono xs
    (fun x => bit (event (is.map (fun i => A i x)) != event (is.map (fun i => B i x))))
    (fun x => total is (fun i => bit (A i x != B i x)))
    (fun x => event_indicator_bound is (fun i => A i x) (fun i => B i x) event)
  rw [total_swap] at hp
  exact hp

/-- Joint-law transport from explicit one-sided errors and marginal imbalance. -/
theorem joint_one_sided_transport {α ι : Type} (xs : List α) (is : List ι)
    (A B : ι → α → Bool) (event : List Bool → Bool) (e g : ι → Nat)
    (he : ∀ i, leakage xs (A i) (B i) ≤ e i)
    (hg : ∀ i, count xs (B i) ≤ count xs (A i) + g i) :
    discrepancy xs (fun x => event (is.map (fun i => A i x)))
      (fun x => event (is.map (fun i => B i x))) ≤
      total is (fun i => 2 * e i + g i) := by
  have h₁ := joint_event_stability xs is A B event
  have h₂ := total_mono is
    (fun i => discrepancy xs (A i) (B i)) (fun i => 2 * e i + g i)
    (fun i => one_sided_transport xs (A i) (B i) (e i) (g i) (he i) (hg i))
  exact Nat.le_trans h₁ h₂

/-- The observable count itself is transported with the same finite error budget. -/
theorem joint_count_transport {α ι : Type} (xs : List α) (is : List ι)
    (A B : ι → α → Bool) (event : List Bool → Bool) (e g : ι → Nat)
    (he : ∀ i, leakage xs (A i) (B i) ≤ e i)
    (hg : ∀ i, count xs (B i) ≤ count xs (A i) + g i) :
    let a := count xs (fun x => event (is.map (fun i => A i x)))
    let b := count xs (fun x => event (is.map (fun i => B i x)))
    let budget := total is (fun i => 2 * e i + g i)
    a ≤ b + budget ∧ b ≤ a + budget := by
  have h₁ := joint_one_sided_transport xs is A B event e g he hg
  have h₂ := count_stability xs (fun x => event (is.map (fun i => A i x)))
    (fun x => event (is.map (fun i => B i x)))
  dsimp
  omega

#print axioms discrepancy_balance
#print axioms one_sided_transport
#print axioms count_stability
#print axioms intersection_stability
#print axioms intersection_one_sided_transport
#print axioms joint_event_stability
#print axioms joint_one_sided_transport
#print axioms joint_count_transport

/-- A natural-valued error is o(n), expressed without real-number infrastructure. -/
def Sublinear (f : Nat → Nat) : Prop :=
  ∀ k : Nat, 0 < k → ∃ N : Nat, ∀ n : Nat, N ≤ n → k * f n ≤ n

theorem sublinear_zero : Sublinear (fun _ => 0) := by
  intro k hk
  exact ⟨0, fun n _ => by simp⟩

theorem sublinear_mono (f g : Nat → Nat) (hg : Sublinear g)
    (h : ∀ n, f n ≤ g n) : Sublinear f := by
  intro k hk
  obtain ⟨N, hN⟩ := hg k hk
  exact ⟨N, fun n hn => Nat.le_trans (Nat.mul_le_mul_left k (h n)) (hN n hn)⟩

theorem sublinear_add (f g : Nat → Nat) (hf : Sublinear f) (hg : Sublinear g) :
    Sublinear (fun n => f n + g n) := by
  intro k hk
  have hk₂ : 0 < 2 * k := by omega
  obtain ⟨N, hN⟩ := hf (2 * k) hk₂
  obtain ⟨M, hM⟩ := hg (2 * k) hk₂
  refine ⟨N + M, ?_⟩
  intro n hn
  have a := hN n (by omega)
  have b := hM n (by omega)
  rw [Nat.mul_assoc] at a b
  rw [Nat.mul_add]
  omega

theorem sublinear_total {ι : Type} (is : List ι) (f : ι → Nat → Nat)
    (h : ∀ i, Sublinear (f i)) : Sublinear (fun n => total is (fun i => f i n)) := by
  induction is with
  | nil => exact sublinear_zero
  | cons i is ih => exact sublinear_add (f i) _ (h i) ih

/-- Full finite-dimensional density-zero transport, allowing triangular arrays.
The growth parameter is n; no external arithmetic density theorem is used. -/
theorem asymptotic_joint_transport {α ι : Type}
    (samples : Nat → List α) (is : List ι) (A B : ι → Nat → α → Bool)
    (event : List Bool → Bool) (e g : ι → Nat → Nat)
    (he : ∀ i n, leakage (samples n) (A i n) (B i n) ≤ e i n)
    (hg : ∀ i n, count (samples n) (B i n) ≤ count (samples n) (A i n) + g i n)
    (se : ∀ i, Sublinear (e i)) (sg : ∀ i, Sublinear (g i)) :
    Sublinear (fun n => discrepancy (samples n)
      (fun x => event (is.map (fun i => A i n x)))
      (fun x => event (is.map (fun i => B i n x)))) := by
  have sb : ∀ i, Sublinear (fun n => 2 * e i n + g i n) := by
    intro i
    have s := sublinear_add _ _ (sublinear_add _ _ (se i) (se i)) (sg i)
    apply sublinear_mono _ _ s
    intro n
    omega
  apply sublinear_mono _ _ (sublinear_total is _ sb)
  intro n
  exact joint_one_sided_transport (samples n) is (fun i => A i n)
    (fun i => B i n) event (fun i => e i n) (fun i => g i n)
    (fun i => he i n) (fun i => hg i n)

#print axioms sublinear_add
#print axioms asymptotic_joint_transport

/-- No auxiliary error-budget functions are needed: use observed leakage and
positive marginal excess directly. Equality of limiting marginals supplies
sublinearity of the latter in a real-analysis application. -/
theorem asymptotic_joint_from_marginals {α ι : Type}
    (samples : Nat → List α) (is : List ι) (A B : ι → Nat → α → Bool)
    (event : List Bool → Bool)
    (leak : ∀ i, Sublinear (fun n => leakage (samples n) (A i n) (B i n)))
    (marg : ∀ i, Sublinear (fun n =>
      count (samples n) (B i n) - count (samples n) (A i n))) :
    Sublinear (fun n => discrepancy (samples n)
      (fun x => event (is.map (fun i => A i n x)))
      (fun x => event (is.map (fun i => B i n x)))) := by
  apply asymptotic_joint_transport samples is A B event
    (fun i n => leakage (samples n) (A i n) (B i n))
    (fun i n => count (samples n) (B i n) - count (samples n) (A i n))
  · intro i n; exact Nat.le_refl _
  · intro i n; omega
  · exact leak
  · exact marg

/-- Finite symmetric count gap is bounded by observation discrepancy. -/
theorem count_gap_le_discrepancy {α : Type} (xs : List α) (p q : α → Bool) :
    (count xs p - count xs q) + (count xs q - count xs p) ≤ discrepancy xs p q := by
  have h := count_stability xs p q
  omega

/-- Every finite-coordinate Boolean event has the same normalized count up to o(n). -/
theorem asymptotic_joint_count_gap {α ι : Type}
    (samples : Nat → List α) (is : List ι) (A B : ι → Nat → α → Bool)
    (event : List Bool → Bool)
    (leak : ∀ i, Sublinear (fun n => leakage (samples n) (A i n) (B i n)))
    (marg : ∀ i, Sublinear (fun n =>
      count (samples n) (B i n) - count (samples n) (A i n))) :
    Sublinear (fun n =>
      let a := count (samples n) (fun x => event (is.map (fun i => A i n x)))
      let b := count (samples n) (fun x => event (is.map (fun i => B i n x)))
      (a - b) + (b - a)) := by
  apply sublinear_mono _ _ (asymptotic_joint_from_marginals samples is A B event leak marg)
  intro n
  exact count_gap_le_discrepancy (samples n) _ _

#print axioms asymptotic_joint_from_marginals
#print axioms count_gap_le_discrepancy
#print axioms asymptotic_joint_count_gap

end DensityTransport
