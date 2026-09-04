import Mathlib.Data.Nat.Choose.Basic
import Init.Data.Nat.Gcd

set_option autoImplicit false

namespace AdjacentBinomialGcd

/-- Homogeneous gcd identity; valid even when one or more parameters vanish. -/
theorem mul_gcd_of_mul_eq_mul (a b c d : Nat) (h : a * c = b * d) :
    a * Nat.gcd b c = b * Nat.gcd a d := by
  calc
    a * Nat.gcd b c = Nat.gcd (a * b) (a * c) := (Nat.gcd_mul_left a b c).symm
    _ = Nat.gcd (b * a) (b * d) := by rw [h, Nat.mul_comm a b]
    _ = b * Nat.gcd a d := Nat.gcd_mul_left b a d

/-- The adjacent-binomial gcd identity, without any bound on the lower index. -/
theorem adjacent_binomial_gcd (j k : Nat) :
    (k + 1) * Nat.gcd (Nat.choose j k) (Nat.choose (j + 1) (k + 1)) =
      Nat.choose j k * Nat.gcd (k + 1) (j + 1) := by
  apply mul_gcd_of_mul_eq_mul
  calc
    (k + 1) * Nat.choose (j + 1) (k + 1) =
        Nat.choose (j + 1) (k + 1) * (k + 1) := Nat.mul_comm _ _
    _ = (j + 1) * Nat.choose j k := (Nat.add_one_mul_choose_eq j k).symm
    _ = Nat.choose j k * (j + 1) := Nat.mul_comm _ _

/-- Coprimality transfers a divisor through the adjacent-binomial product relation. -/
theorem divisor_transfer (U A B C j : Nat) (hUB : U ∣ B)
    (hUA : Nat.gcd U A = 1) (hprod : A * C = (j + 1) * B) : U ∣ C := by
  have hUC : U ∣ A * C := by
    rw [hprod]
    exact Nat.dvd_mul_left_of_dvd hUB (j + 1)
  have hg : U ∣ Nat.gcd U (A * C) := Nat.dvd_gcd (Nat.dvd_refl U) hUC
  rw [Nat.gcd_mul_right_right_of_gcd_eq_one hUA] at hg
  exact Nat.dvd_trans hg (Nat.gcd_dvd_right U C)

end AdjacentBinomialGcd
