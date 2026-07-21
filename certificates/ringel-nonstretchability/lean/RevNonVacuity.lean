/- SCRATCH CHECK (not part of the result): is the reversed-orientation predicate non-vacuous?
   Same definitional SHAPE as `IsRingelRealizationRev`, but with the all-one table in place of
   chi_Ringel.  The all-one table is a genuine uniform rank-3 chirotope (nine points on the
   moment curve) and is not either orientation of chi_Ringel (which has negative entries).
   If the reversed predicate were vacuously unsatisfiable for definitional reasons, no witness
   could exist here. -/
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Push
import Mathlib.Data.Real.Basic

abbrev Pt (R : Type*) := R × R × R

variable {R : Type*} [CommRing R]

def br (a b c : Pt R) : R :=
  a.1 * (b.2.1 * c.2.2 - b.2.2 * c.2.1)
  - b.1 * (a.2.1 * c.2.2 - a.2.2 * c.2.1)
  + c.1 * (a.2.1 * b.2.2 - a.2.2 * b.2.1)

/-- The all-one chirotope on sorted triples: realizable, and not an orientation of chi_Ringel. -/
def chiOnes (i j k : Fin 9) : ℤ := if i < j ∧ j < k then 1 else 0

/-- Exactly the shape of `IsRingelRealizationRev`, with `chiOnes` for `chiRingel`. -/
def IsOnesRealizationRev (p : Fin 9 → Pt ℝ) : Prop :=
  ∀ i j k : Fin 9, i < j → j < k → 0 < -(chiOnes i j k : ℝ) * br (p i) (p j) (p k)

/-- Exactly the shape of `IsRingelRealization`, with `chiOnes` for `chiRingel`. -/
def IsOnesRealization (p : Fin 9 → Pt ℝ) : Prop :=
  ∀ i j k : Fin 9, i < j → j < k → 0 < (chiOnes i j k : ℝ) * br (p i) (p j) (p k)

/-- Antipodal moment curve: minus (1, t, t^2) at t = 0 .. 8. -/
def qAnti (i : Fin 9) : Pt ℝ := (-1, -(i.val : ℝ), -((i.val : ℝ) ^ 2))

/-- Moment curve: (1, t, t^2) at t = 0 .. 8. -/
def qMoment (i : Fin 9) : Pt ℝ := (1, (i.val : ℝ), ((i.val : ℝ) ^ 2))

private theorem vandermonde_pos (i j k : Fin 9) (hij : i < j) (hjk : j < k) :
    (0:ℝ) < ((j.val : ℝ) - i.val) * ((k.val : ℝ) - i.val) * ((k.val : ℝ) - j.val) := by
  have hij' : (i.val : ℝ) < (j.val : ℝ) := by
    have : i.val < j.val := hij
    exact_mod_cast this
  have hjk' : (j.val : ℝ) < (k.val : ℝ) := by
    have : j.val < k.val := hjk
    exact_mod_cast this
  have hik' : (i.val : ℝ) < (k.val : ℝ) := lt_trans hij' hjk'
  exact mul_pos (mul_pos (sub_pos.mpr hij') (sub_pos.mpr hik')) (sub_pos.mpr hjk')

/-- WITNESS 1: the REVERSED predicate is satisfied by the antipodal moment curve.
So the reversed shape is not vacuously unsatisfiable. -/
theorem ones_rev_realizable : IsOnesRealizationRev qAnti := by
  intro i j k hij hjk
  have hchi : chiOnes i j k = 1 := by simp [chiOnes, hij, hjk]
  have hgoal : -(chiOnes i j k : ℝ) * br (qAnti i) (qAnti j) (qAnti k)
      = ((j.val : ℝ) - i.val) * ((k.val : ℝ) - i.val) * ((k.val : ℝ) - j.val) := by
    rw [hchi]; simp only [br, qAnti, Int.cast_one]; ring
  rw [hgoal]
  exact vandermonde_pos i j k hij hjk

/-- WITNESS 2: the FORWARD predicate for the same table is satisfied by the moment curve.
Neither orientation of the all-one chirotope is obstructed, so the obstruction proved in
`RingelNotStretchable.lean` is a fact about Ringel's sign data, not about the definitions. -/
theorem ones_fwd_realizable : IsOnesRealization qMoment := by
  intro i j k hij hjk
  have hchi : chiOnes i j k = 1 := by simp [chiOnes, hij, hjk]
  have hgoal : (chiOnes i j k : ℝ) * br (qMoment i) (qMoment j) (qMoment k)
      = ((j.val : ℝ) - i.val) * ((k.val : ℝ) - i.val) * ((k.val : ℝ) - j.val) := by
    rw [hchi]; simp only [br, qMoment, Int.cast_one]; ring
  rw [hgoal]
  exact vandermonde_pos i j k hij hjk

#print axioms ones_rev_realizable
#print axioms ones_fwd_realizable
