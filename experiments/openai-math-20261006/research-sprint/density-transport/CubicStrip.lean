import Std

namespace CubicStrip

/-- Exact sum-of-squares expansion for the strip obstruction. -/
theorem obstruction_identity (n d : Int) :
    4 * ((n-1)*(n-2) - d*(3*n-d*d-2)) =
    (2*n-3*d-3)*(2*n-3*d-3) + 4*(d-4)*(d-4)*(d-4) +
      39*(d-4)*(d-4) + 110*(d-4) + 71 := by
  grind

/-- The obstruction is strictly positive for every integer n and d >= 4. -/
theorem obstruction_positive (n d : Int) (hd : 4 ≤ d) :
    0 < (n-1)*(n-2) - d*(3*n-d*d-2) := by
  have hx : 0 ≤ d-4 := by omega
  have hs : 0 ≤ (2*n-3*d-3)*(2*n-3*d-3) := by
    simpa [Int.pow_succ] using Int.sq_nonneg (2*n-3*d-3)
  have hsq : 0 ≤ (d-4)*(d-4) := Int.mul_nonneg hx hx
  have hc : 0 ≤ (d-4)*(d-4)*(d-4) := Int.mul_nonneg hsq hx
  have hi := obstruction_identity n d
  grind

/-- Explicit-hypothesis algebraic core; the quotient identity must be supplied. -/
theorem quotient_negative (n d m : Int) (hn : 3 ≤ n) (hd : 4 ≤ d)
    (he : m*((n-1)*(n-2)) = d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) : m ≤ -1 := by
  have hp : 0 < (n-1)*(n-2) := Int.mul_pos (by omega) (by omega)
  have hf := obstruction_positive n d hd
  have hm : m < 1 := by
    by_cases h : m < 1
    · exact h
    have hm1 : 1 ≤ m := by omega
    have hmul : (n-1)*(n-2) ≤ m*((n-1)*(n-2)) := by
      have hh := Int.mul_le_mul_of_nonneg_right hm1 (Int.le_of_lt hp)
      simpa using hh
    omega
  have hm0 : m ≠ 0 := by
    intro h
    have hz : d*(3*n-d*d-2) = 0 := by simpa [h] using he.symm
    have hh := Int.mul_eq_zero.mp hz
    rcases hh with hh | hh
    · omega
    · omega
  omega

/-- A nonzero quotient forces a cubic strip beyond n², with an explicit margin. -/
theorem growing_strip (n d m : Int) (hn : 3 ≤ n) (hd : 4 ≤ d)
    (he : m*((n-1)*(n-2)) = d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) :
    n*n + (d-1)*(3*n-2) ≤ d*d*d ∧ n*n < d*d*d := by
  have hm := quotient_negative n d m hn hd he hne
  have hp : 0 ≤ (n-1)*(n-2) := Int.mul_nonneg (by omega) (by omega)
  have hmul := Int.mul_le_mul_of_nonneg_right hm hp
  have hmargin : 0 < (d-1)*(3*n-2) := Int.mul_pos (by omega) (by omega)
  constructor
  · grind
  · grind

/-- Any supplied lower magnitude for the negative quotient strengthens the strip. -/
theorem quotient_bound (n d m r : Int) (hn : 3 ≤ n)
    (he : m*((n-1)*(n-2)) = d*(3*n-d*d-2)) (hm : m ≤ -r) :
    r*(n*n) + (d-r)*(3*n-2) ≤ d*d*d := by
  have hp : 0 ≤ (n-1)*(n-2) := Int.mul_nonneg (by omega) (by omega)
  have hmul := Int.mul_le_mul_of_nonneg_right hm hp
  grind

/-- The zero obstruction cannot occur when n is a multiple of four and d is even. -/
theorem parity_nonzero (n d : Int) (hn4 : ∃ a : Int, n = 4*a)
    (hd2 : ∃ b : Int, d = 2*b) : d*d ≠ 3*n-2 := by
  obtain ⟨a, rfl⟩ := hn4
  obtain ⟨b, rfl⟩ := hd2
  have hi : (2*b)*(2*b) = 4*(b*b) := by grind
  rw [hi]
  omega

/-- An even quotient gives the coefficient-two growing strip. -/
theorem even_quotient_strip (n d m : Int) (hn : 3 ≤ n) (hd : 4 ≤ d)
    (he : m*((n-1)*(n-2)) = d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) (hme : ∃ q : Int, m = 2*q) :
    2*(n*n) + (d-2)*(3*n-2) ≤ d*d*d ∧ 2*(n*n) < d*d*d := by
  have hm := quotient_negative n d m hn hd he hne
  obtain ⟨q, hq⟩ := hme
  have hm2 : m ≤ -2 := by omega
  have hb := quotient_bound n d m 2 hn he hm2
  have hh : 0 < (d-2)*(3*n-2) := Int.mul_pos (by omega) (by omega)
  exact ⟨hb, by omega⟩

/-- A quotient divisible by four gives the coefficient-four bound.
At d=4 the margin is zero, so the conclusion is deliberately non-strict. -/
theorem four_quotient_strip (n d m : Int) (hn : 3 ≤ n) (hd : 4 ≤ d)
    (he : m*((n-1)*(n-2)) = d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) (hm4 : ∃ q : Int, m = 4*q) :
    4*(n*n) + (d-4)*(3*n-2) ≤ d*d*d := by
  have hm := quotient_negative n d m hn hd he hne
  obtain ⟨q, hq⟩ := hm4
  have hm4 : m ≤ -4 := by omega
  exact quotient_bound n d m 4 hn he hm4

/-- The arithmetic application may separately supply m=4g³k-d and k>=1. -/
theorem gcd_gap (n d m g k : Int) (hn : 3 ≤ n) (hd : 4 ≤ d)
    (he : m*((n-1)*(n-2)) = d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) (hg : 0 ≤ g) (hk : 1 ≤ k)
    (hmdef : m = (4*g*g*g)*k-d) : 4*g*g*g < d := by
  have hm := quotient_negative n d m hn hd he hne
  have hb : 0 ≤ 4*g*g*g :=
    Int.mul_nonneg (Int.mul_nonneg (Int.mul_nonneg (by decide) hg) hg) hg
  have hh := Int.mul_le_mul_of_nonneg_left hk hb
  simp only [Int.mul_one] at hh
  omega

/-- Without the nonzero assumption the quotient-zero case really can occur. -/
theorem zero_quotient_control :
    (3 : Int) ≤ 6 ∧ (4 : Int) ≤ 4 ∧
    (0 : Int)*((6-1)*(6-2)) = 4*(3*6-4*4-2) ∧
    ¬ ((6 : Int)*6 + (4-1)*(3*6-2) ≤ 4*4*4) := by
  decide

#print axioms obstruction_identity
#print axioms obstruction_positive
#print axioms quotient_negative
#print axioms growing_strip
#print axioms quotient_bound
#print axioms parity_nonzero
#print axioms even_quotient_strip
#print axioms four_quotient_strip
#print axioms gcd_gap
#print axioms zero_quotient_control
end CubicStrip
