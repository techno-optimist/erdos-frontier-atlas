import FormalBridge

namespace WeightedFormal

open FormalBridge

/-- Restore the denominator while retaining the explicit small-prime factor A. -/
theorem restore_weighted (n u v A B C : Int)
    (hB : B ∣ u*(v-u)) (hC : C ∣ 4*Q u v)
    (hC4 : Int.gcd C 4 = 1) (hBC : Int.gcd B C = 1)
    (h2BC : Int.gcd 2 (B*C) = 1)
    (hfactor : (n-1)*(n-2) = 2*A*(B*C)) :
    (n-1)*(n-2) ∣ A*Q u v := by
  have hb : B ∣ Q u v := by
    obtain ⟨k, hk⟩ := hB
    exact ⟨k*(v-2*u), by simp only [Q]; grind⟩
  have hc := cancel_coprime C 4 (Q u v) hC4 hC
  have hbc := coprime_product B C (Q u v) hBC hb hc
  have hfull := coprime_product 2 (B*C) (Q u v) h2BC (q_even u v) hbc
  obtain ⟨k, hk⟩ := hfull
  exact ⟨k, by grind⟩

/-- Positivity certificate with no square roots or division. -/
theorem obstruction_identity (n d A : Int) :
    4*((n-1)*(n-2)-A*d*(3*n-d*d-2)) =
    (2*n-3*A*d-3)*(2*n-3*A*d-3) +
      4*A*d*d*(d-4*A) + 7*(A*d-4)*(A*d-4) + 46*(A*d-4) + 71 := by
  grind

/-- The completed square is strictly positive once d >= 4A and A >= 1. -/
theorem obstruction_positive (n d A : Int) (hA : 1 ≤ A) (hd : 4*A ≤ d) :
    0 < (n-1)*(n-2)-A*d*(3*n-d*d-2) := by
  have hd0 : 0 ≤ d := by omega
  have hx : 0 ≤ d-4*A := by omega
  have had := Int.mul_le_mul_of_nonneg_right hA hd0
  have hy : 0 ≤ A*d-4 := by omega
  have hs : 0 ≤ (2*n-3*A*d-3)*(2*n-3*A*d-3) := by
    simpa [Int.pow_succ] using Int.sq_nonneg (2*n-3*A*d-3)
  have ht : 0 ≤ 4*A*d*d*(d-4*A) :=
    Int.mul_nonneg
      (Int.mul_nonneg (Int.mul_nonneg (Int.mul_nonneg (by decide) (by omega)) hd0) hd0) hx
  have hu : 0 ≤ (A*d-4)*(A*d-4) := Int.mul_nonneg hy hy
  have hi := obstruction_identity n d A
  grind

/-- An explicit nonzero premise excludes the exceptional quotient zero. -/
theorem quotient_negative (n d A m : Int) (hn : 3 ≤ n)
    (hA : 1 ≤ A) (hd : 4*A ≤ d)
    (he : m*((n-1)*(n-2)) = A*d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) : m ≤ -1 := by
  have hp : 0 < (n-1)*(n-2) := Int.mul_pos (by omega) (by omega)
  have hf := obstruction_positive n d A hA hd
  have hm : m < 1 := by
    by_cases h : m < 1
    · exact h
    have hm1 : 1 ≤ m := by omega
    have hh := Int.mul_le_mul_of_nonneg_right hm1 (Int.le_of_lt hp)
    simp only [Int.one_mul] at hh
    omega
  have hm0 : m ≠ 0 := by
    intro h
    have hz : A*d*(3*n-d*d-2) = 0 := by simpa [h] using he.symm
    have had : 0 < A*d := Int.mul_pos (by omega) (by omega)
    rcases Int.mul_eq_zero.mp hz with hh | hh
    · omega
    · omega
  omega

/-- Every lower bound for the magnitude of the negative quotient transfers. -/
theorem quotient_bound (n d A m r : Int) (hn : 3 ≤ n)
    (he : m*((n-1)*(n-2)) = A*d*(3*n-d*d-2)) (hm : m ≤ -r) :
    r*(n*n)+(A*d-r)*(3*n-2) ≤ A*d*d*d := by
  have hp : 0 ≤ (n-1)*(n-2) := Int.mul_nonneg (by omega) (by omega)
  have hh := Int.mul_le_mul_of_nonneg_right hm hp
  grind

/-- Weighted coefficient-two bound, with its positive margin. -/
theorem even_quotient_strip (n d A m : Int) (hn : 3 ≤ n)
    (hA : 1 ≤ A) (hd : 4*A ≤ d)
    (he : m*((n-1)*(n-2)) = A*d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) (hme : ∃ q : Int, m = 2*q) :
    2*(n*n)+(A*d-2)*(3*n-2) ≤ A*d*d*d ∧ 2*(n*n) < A*d*d*d := by
  have hm := quotient_negative n d A m hn hA hd he hne
  obtain ⟨q, hq⟩ := hme
  have hm2 : m ≤ -2 := by omega
  have hb := quotient_bound n d A m 2 hn he hm2
  have had := Int.mul_le_mul_of_nonneg_right hA (show 0 ≤ d by omega)
  have hh : 0 < (A*d-2)*(3*n-2) := Int.mul_pos (by omega) (by omega)
  exact ⟨hb, by omega⟩

/-- A multiple-of-four quotient supplies the stronger non-strict bound. -/
theorem four_quotient_strip (n d A m : Int) (hn : 3 ≤ n)
    (hA : 1 ≤ A) (hd : 4*A ≤ d)
    (he : m*((n-1)*(n-2)) = A*d*(3*n-d*d-2))
    (hne : d*d ≠ 3*n-2) (hm4 : ∃ q : Int, m = 4*q) :
    4*(n*n)+(A*d-4)*(3*n-2) ≤ A*d*d*d := by
  have hm := quotient_negative n d A m hn hA hd he hne
  obtain ⟨q, hq⟩ := hm4
  exact quotient_bound n d A m 4 hn he (by omega)

/-- Positivity of the arithmetic quotient is derived, not postulated. -/
theorem quotient_from_weighted (n j d g u v A : Int)
    (hn : 3 ≤ n) (hu : 0 < u) (hvu : 2*u < v) (hA : 1 ≤ A)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hdiv : (n-1)*(n-2) ∣ A*Q u v) :
    ∃ k : Int, 1 ≤ k ∧ A*Q u v = (n-1)*(n-2)*k ∧
      ((4*g*g*g)*k-A*d)*((n-1)*(n-2)) = A*d*(3*n-d*d-2) := by
  obtain ⟨k, hk⟩ := hdiv
  have hp : 0 < (n-1)*(n-2) := Int.mul_pos (by omega) (by omega)
  have hq : 0 < Q u v := Int.mul_pos (Int.mul_pos hu (by omega)) (by omega)
  have haq : 0 < A*Q u v := Int.mul_pos (by omega) hq
  have hkpos : 1 ≤ k := by
    have hh : 0 < (n-1)*(n-2)*k := by rw [← hk]; exact haq
    have hh := Int.pos_of_mul_pos_right hh hp
    omega
  refine ⟨k, hkpos, hk, ?_⟩
  have hid : 4*g*g*g*Q u v = d*(n*n-d*d) := by
    simp only [Q]
    grind
  have hs := congrArg (fun x : Int => 4*g*g*g*x) hk
  have ht := congrArg (fun x : Int => A*x) hid
  grind

/-- A real row normalization supplies all positivity conditions on u and v. -/
theorem normalized_positive (n j g u v : Int) (hg : 0 < g)
    (hj : 0 < j) (hjn : 2*j < n) (hnv : n = g*v) (hju : j = g*u) :
    0 < u ∧ 2*u < v := by
  have hu : 0 < u := Int.pos_of_mul_pos_right (by rw [← hju]; exact hj) hg
  have hh : g*(2*u) < g*v := by grind
  exact ⟨hu, Int.lt_of_mul_lt_mul_left hh (Int.le_of_lt hg)⟩

/-- End-to-end weighted bound from a genuine row normalization and weighted divisor. -/
theorem strip_from_weighted (n j d g u v A : Int)
    (hn : 3 ≤ n) (hj : 0 < j) (hjn : 2*j < n) (hg : 0 < g)
    (hA : 1 ≤ A) (hdA : 4*A ≤ d)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a)
    (hdiv : (n-1)*(n-2) ∣ A*Q u v) :
    2*(n*n)+(A*d-2)*(3*n-2) ≤ A*d*d*d ∧
      2*(n*n) < A*d*d*d ∧ 4*g*g*g < A*d := by
  have hpos := normalized_positive n j g u v hg hj hjn hnv hju
  obtain ⟨k, hk, hq, he⟩ := quotient_from_weighted n j d g u v A
    hn hpos.1 hpos.2 hA hnv hju hd hdiv
  obtain ⟨a, ha⟩ := hn4
  have hde : ∃ b : Int, d = 2*b := ⟨2*a-j, by omega⟩
  have hne := CubicStrip.parity_nonzero n d ⟨a, ha⟩ hde
  have hme : ∃ q : Int, (4*g*g*g)*k-A*d = 2*q := by
    exact ⟨2*g*g*g*k-A*(2*a-j), by grind⟩
  have hs := even_quotient_strip n d A ((4*g*g*g)*k-A*d) hn hA hdA he hne hme
  have hm := quotient_negative n d A ((4*g*g*g)*k-A*d) hn hA hdA he hne
  have hg0 := Int.le_of_lt hg
  have hb : 0 ≤ 4*g*g*g :=
    Int.mul_nonneg (Int.mul_nonneg (Int.mul_nonneg (by decide) hg0) hg0) hg0
  have hh := Int.mul_le_mul_of_nonneg_left hk hb
  simp only [Int.mul_one] at hh
  exact ⟨hs.1, hs.2, by omega⟩

/-- Aggregated retained blocks suffice; no abstract quotient premise remains. -/
theorem strip_from_products (n j d g u v A B C : Int)
    (hn : 3 ≤ n) (hj : 0 < j) (hjn : 2*j < n) (hg : 0 < g)
    (hA : 1 ≤ A) (hdA : 4*A ≤ d)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a)
    (hB : B ∣ u*(v-u)) (hC : C ∣ 4*Q u v)
    (hC4 : Int.gcd C 4 = 1) (hBC : Int.gcd B C = 1)
    (h2BC : Int.gcd 2 (B*C) = 1)
    (hfactor : (n-1)*(n-2) = 2*A*(B*C)) :
    2*(n*n)+(A*d-2)*(3*n-2) ≤ A*d*d*d ∧
      2*(n*n) < A*d*d*d ∧ 4*g*g*g < A*d := by
  have hh := restore_weighted n u v A B C hB hC hC4 hBC h2BC hfactor
  exact strip_from_weighted n j d g u v A hn hj hjn hg hA hdA hnv hju hd hn4 hh

/-- Finite positional block data imply the weighted central obstruction.
Prime-power extraction and binomial valuations are deliberately outside this statement. -/
theorem strip_from_blocks (n j d g u v A : Int) (bs cs : List Int)
    (hn : 3 ≤ n) (hj : 0 < j) (hjn : 2*j < n) (hg : 0 < g)
    (hA : 1 ≤ A) (hdA : 4*A ≤ d)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a)
    (hb : CoprimeBlocks bs) (hc : CoprimeBlocks cs)
    (hlb : LocalAt n j 1 bs) (hlc : LocalAt n j 2 cs)
    (hC4 : Int.gcd cs.prod 4 = 1)
    (h2BC : Int.gcd 2 (bs.prod*cs.prod) = 1)
    (hfactor : (n-1)*(n-2) = 2*A*(bs.prod*cs.prod)) :
    2*(n*n)+(A*d-2)*(3*n-2) ≤ A*d*d*d ∧
      2*(n*n) < A*d*d*d ∧ 4*g*g*g < A*d := by
  have he : n*u=v*j := by grind
  have hh := positional_products n j u v bs cs he hb hc hlb hlc
  exact strip_from_products n j d g u v A bs.prod cs.prod
    hn hj hjn hg hA hdA hnv hju hd hn4 hh.1 hh.2.1 hC4 hh.2.2 h2BC hfactor

/-- A multiple-of-four gap yields the coefficient-four bound from the same divisor. -/
theorem four_strip_from_weighted (n j d g u v A : Int)
    (hn : 3 ≤ n) (hj : 0 < j) (hjn : 2*j < n) (hg : 0 < g)
    (hA : 1 ≤ A) (hdA : 4*A ≤ d)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a) (hd4 : ∃ b : Int, d = 4*b)
    (hdiv : (n-1)*(n-2) ∣ A*Q u v) :
    4*(n*n)+(A*d-4)*(3*n-2) ≤ A*d*d*d := by
  have hpos := normalized_positive n j g u v hg hj hjn hnv hju
  obtain ⟨k, hk, hq, he⟩ := quotient_from_weighted n j d g u v A
    hn hpos.1 hpos.2 hA hnv hju hd hdiv
  obtain ⟨b, hb⟩ := hd4
  have hde : ∃ c : Int, d = 2*c := ⟨2*b, by omega⟩
  have hne := CubicStrip.parity_nonzero n d hn4 hde
  have hm4 : ∃ q : Int, (4*g*g*g)*k-A*d = 4*q := by
    exact ⟨g*g*g*k-A*b, by grind⟩
  exact four_quotient_strip n d A ((4*g*g*g)*k-A*d) hn hA hdA he hne hm4

/-- Concrete two-position data fail both tempting strengthened conclusions. -/
theorem defect_threshold_control :
    (210 : Int) ∣ 15*Q 7 16 ∧ ¬ (210 : Int) ∣ Q 7 16 ∧
    (15 : Int)*Q 7 16 = 210*9 ∧
    (4 : Int)*9-15*2 = 6 ∧ 0 < (6 : Int) ∧ ¬ (4 : Int)*15 ≤ 2 ∧
    (6 : Int)*210 = 15*2*(3*16-2*2-2) := by
  decide

/-- The quotient-zero obstruction survives if row parity is removed. -/
theorem parity_control :
    (1 : Int) ≤ 1 ∧ (4 : Int)*1 ≤ 4 ∧
    (0 : Int)*((6-1)*(6-2)) = 1*4*(3*6-4*4-2) ∧
    ¬ ((0 : Int) ≤ -1) ∧ ¬ ((2 : Int)*(6*6) < 1*4*4*4) := by
  decide

#print axioms restore_weighted
#print axioms obstruction_identity
#print axioms obstruction_positive
#print axioms quotient_negative
#print axioms quotient_bound
#print axioms even_quotient_strip
#print axioms four_quotient_strip
#print axioms quotient_from_weighted
#print axioms normalized_positive
#print axioms strip_from_weighted
#print axioms strip_from_products
#print axioms strip_from_blocks
#print axioms four_strip_from_weighted
#print axioms defect_threshold_control
#print axioms parity_control

end WeightedFormal
