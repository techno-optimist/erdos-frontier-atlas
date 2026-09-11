/-
Kernel-checked infinite P699 subfamily: i = 2 and n = 2 * j + 3.

Pascal binomials plus Init gcd/coprime. The kernel theorem produces a
divisor m ≥ 3 of both binomials. The remaining sentence “every natural
≥ 3 has a prime factor ≥ 3 ≥ i” is the unique unformalized Init-gap;
it is not EEES and not the rest of #699.
-/
import Init.Data.Nat.Gcd
import Init.Data.Nat.Coprime
import Init.Data.Nat.Dvd
import Init.Data.Nat.Lemmas
import Init.Omega

namespace P699I2

def fac : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * fac n

theorem fac_pos : ∀ n, 0 < fac n
  | 0 => Nat.zero_lt_succ 0
  | n + 1 => Nat.mul_pos (Nat.succ_pos n) (fac_pos n)

theorem fac_succ (n : Nat) : fac (n + 1) = (n + 1) * fac n := rfl

def binom : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => binom n k + binom n (k + 1)

@[simp] theorem binom_zero_right (n : Nat) : binom n 0 = 1 := by
  cases n <;> rfl

theorem binom_succ_succ (n k : Nat) :
    binom (n + 1) (k + 1) = binom n k + binom n (k + 1) := rfl

theorem binom_eq_zero_of_lt : ∀ n k, n < k → binom n k = 0
  | 0, _ + 1, _ => rfl
  | n + 1, k + 1, h => by
    have hn : n < k := Nat.lt_of_succ_lt_succ h
    have hn' : n < k + 1 := Nat.lt_trans hn (Nat.lt_succ_self k)
    rw [binom_succ_succ, binom_eq_zero_of_lt n k hn, binom_eq_zero_of_lt n (k + 1) hn']

theorem binom_one : ∀ n, binom n 1 = n
  | 0 => rfl
  | n + 1 => by
    change binom n 0 + binom n 1 = n + 1
    rw [binom_zero_right, binom_one n, Nat.add_comm]

theorem two_dvd_mul_succ (n : Nat) : 2 ∣ n * (n + 1) := by
  rcases Nat.mod_two_eq_zero_or_one n with h | h
  · exact Nat.dvd_mul_right_of_dvd (Nat.dvd_of_mod_eq_zero h) _
  · have : (n + 1) % 2 = 0 := by
      rw [Nat.add_mod n 1 2, h]
    exact Nat.dvd_mul_left_of_dvd (Nat.dvd_of_mod_eq_zero this) _

theorem binom_two : ∀ n, binom n 2 = n * (n - 1) / 2
  | 0 => rfl
  | 1 => rfl
  | n + 2 => by
    have ih := binom_two (n + 1)
    change binom (n + 1) 1 + binom (n + 1) 2 = (n + 2) * (n + 1) / 2
    rw [binom_one, ih]
    have h2 : 2 ∣ (n + 1) * n := by
      simpa [Nat.mul_comm] using two_dvd_mul_succ n
    have hcancel : 2 * ((n + 1) * n / 2) = (n + 1) * n := Nat.mul_div_cancel' h2
    have hmul : 2 * ((n + 1) + (n + 1) * n / 2) = (n + 2) * (n + 1) := by
      rw [Nat.mul_add, hcancel, Nat.mul_comm (n + 1) n, ← Nat.add_mul, Nat.add_comm 2 n]
    have hmul' : (n + 2) * (n + 1) = ((n + 1) + (n + 1) * n / 2) * 2 := by
      rw [Nat.mul_comm _ 2]
      exact hmul.symm
    exact (Nat.div_eq_of_eq_mul_left (by decide : 0 < (2 : Nat)) hmul').symm

theorem binom_mul_fac : ∀ n k, k ≤ n → binom n k * fac k * fac (n - k) = fac n
  | 0, k, h => by
    cases Nat.eq_zero_of_le_zero h
    rfl
  | n + 1, 0, _ => by
    simp [binom_zero_right, fac]
  | n + 1, k + 1, h => by
    have hk : k ≤ n := Nat.le_of_succ_le_succ h
    rw [Nat.succ_sub_succ, binom_succ_succ, fac_succ k]
    rw [Nat.add_mul, Nat.add_mul]
    have h1 : binom n k * ((k + 1) * fac k) * fac (n - k) = (k + 1) * fac n := by
      have ih := binom_mul_fac n k hk
      calc
        binom n k * ((k + 1) * fac k) * fac (n - k)
            = (k + 1) * (binom n k * fac k * fac (n - k)) := by ac_rfl
        _ = (k + 1) * fac n := by rw [ih]
    have h2 : binom n (k + 1) * ((k + 1) * fac k) * fac (n - k) = (n - k) * fac n := by
      cases Nat.lt_or_eq_of_le hk with
      | inl hlt =>
        have hle : k + 1 ≤ n := Nat.succ_le_of_lt hlt
        have ih := binom_mul_fac n (k + 1) hle
        have hnk : n - k = n - (k + 1) + 1 := by omega
        have hfacnk : fac (n - k) = (n - k) * fac (n - (k + 1)) := by
          rw [hnk]; rfl
        calc
          binom n (k + 1) * ((k + 1) * fac k) * fac (n - k)
              = binom n (k + 1) * fac (k + 1) * fac (n - k) := by
                rw [fac_succ k]
          _ = binom n (k + 1) * fac (k + 1) * ((n - k) * fac (n - (k + 1))) := by
                rw [hfacnk]
          _ = (n - k) * (binom n (k + 1) * fac (k + 1) * fac (n - (k + 1))) := by ac_rfl
          _ = (n - k) * fac n := by rw [ih]
      | inr heq =>
        rw [heq, binom_eq_zero_of_lt n (n + 1) (Nat.lt_succ_self n)]
        simp
    rw [h1, h2, ← Nat.add_mul]
    have : k + 1 + (n - k) = n + 1 := by omega
    rw [this]
    rfl

theorem mul_binom_eq (n k : Nat) (hk1 : 1 ≤ k) (hkn : k ≤ n) :
    k * binom n k = n * binom (n - 1) (k - 1) := by
  have hpos : 0 < fac (k - 1) * fac (n - k) := Nat.mul_pos (fac_pos _) (fac_pos _)
  have hfac_k : fac k = k * fac (k - 1) := by
    cases k with
    | zero => cases hk1
    | succ _ => rfl
  have hL : k * binom n k * (fac (k - 1) * fac (n - k)) = fac n := by
    have ih := binom_mul_fac n k hkn
    calc
      k * binom n k * (fac (k - 1) * fac (n - k))
          = binom n k * (k * fac (k - 1)) * fac (n - k) := by ac_rfl
      _ = binom n k * fac k * fac (n - k) := by rw [hfac_k]
      _ = fac n := ih
  have hR : n * binom (n - 1) (k - 1) * (fac (k - 1) * fac (n - k)) = fac n := by
    have hn1 : 1 ≤ n := Nat.le_trans hk1 hkn
    have hle : k - 1 ≤ n - 1 := Nat.pred_le_pred hkn
    have ih := binom_mul_fac (n - 1) (k - 1) hle
    have hfac_n : fac n = n * fac (n - 1) := by
      cases n with
      | zero => cases hn1
      | succ _ => rfl
    have hsub : (n - 1) - (k - 1) = n - k := by omega
    calc
      n * binom (n - 1) (k - 1) * (fac (k - 1) * fac (n - k))
          = n * (binom (n - 1) (k - 1) * fac (k - 1) * fac ((n - 1) - (k - 1))) := by
            rw [hsub]; ac_rfl
      _ = n * fac (n - 1) := by rw [ih]
      _ = fac n := hfac_n.symm
  exact Nat.eq_of_mul_eq_mul_right hpos (hL.trans hR.symm)

theorem gcd_line (j : Nat) : (2 * j + 3).gcd j = (3 : Nat).gcd j := by
  have h := Nat.gcd_add_mul_left_right j 3 2
  rw [Nat.gcd_comm, Nat.add_comm, Nat.mul_comm] at h
  exact h.trans (Nat.gcd_comm j 3)

theorem n_dvd_binom_two_of_line (j : Nat) :
    (2 * j + 3) ∣ binom (2 * j + 3) 2 := by
  have hodd : 2 * j + 3 - 1 = 2 * (j + 1) := by omega
  rw [binom_two]
  have : 2 ∣ 2 * j + 3 - 1 := ⟨j + 1, hodd⟩
  rw [Nat.mul_div_assoc _ this, hodd,
      Nat.mul_div_cancel_left _ (by decide : 0 < (2 : Nat))]
  exact ⟨j + 1, rfl⟩

theorem m_ge_three (j : Nat) (hj : 3 ≤ j) :
    3 ≤ (2 * j + 3) / (2 * j + 3).gcd j := by
  rw [gcd_line]
  have hpos : 0 < (3 : Nat).gcd j := Nat.gcd_pos_of_pos_left _ (by decide)
  have hle : (3 : Nat).gcd j ≤ 3 := Nat.le_of_dvd (by decide) (Nat.gcd_dvd_left 3 j)
  have hmono : (2 * j + 3) / 3 ≤ (2 * j + 3) / (3 : Nat).gcd j :=
    Nat.div_le_div_left hle hpos
  have hn : 9 ≤ 2 * j + 3 := by omega
  have h3 : 3 ≤ (2 * j + 3) / 3 :=
    (Nat.le_div_iff_mul_le (by decide : 0 < (3 : Nat))).2 hn
  exact Nat.le_trans h3 hmono

theorem i2_m_divides (j : Nat) (hj : 3 ≤ j) :
    let n := 2 * j + 3
    let m := n / n.gcd j
    3 ≤ m ∧ m ∣ binom n 2 ∧ m ∣ binom n j := by
  intro n m
  refine ⟨m_ge_three j hj, ?_, ?_⟩
  · exact Nat.dvd_trans (Nat.div_dvd_of_dvd (Nat.gcd_dvd_left n j)) (n_dvd_binom_two_of_line j)
  · have hj1 : 1 ≤ j := by omega
    have hjn : j ≤ n := by omega
    have hid := mul_binom_eq n j hj1 hjn
    have hgcdpos : 0 < n.gcd j := Nat.gcd_pos_of_pos_right _ (by omega)
    have hcop : (n / n.gcd j).Coprime (j / n.gcd j) := Nat.coprime_div_gcd_div_gcd hgcdpos
    have hjdiv : n.gcd j ∣ j := Nat.gcd_dvd_right _ _
    have hndiv : n.gcd j ∣ n := Nat.gcd_dvd_left _ _
    have hgj : j = n.gcd j * (j / n.gcd j) := (Nat.mul_div_cancel' hjdiv).symm
    have hgn : n = n.gcd j * m := (Nat.mul_div_cancel' hndiv).symm
    have hmul : (j / n.gcd j) * binom n j = m * binom (n - 1) (j - 1) := by
      apply Nat.mul_left_cancel hgcdpos
      calc
        n.gcd j * ((j / n.gcd j) * binom n j)
            = (n.gcd j * (j / n.gcd j)) * binom n j := by rw [Nat.mul_assoc]
        _ = j * binom n j := by rw [← hgj]
        _ = n * binom (n - 1) (j - 1) := hid
        _ = (n.gcd j * m) * binom (n - 1) (j - 1) := by rw [← hgn]
        _ = n.gcd j * (m * binom (n - 1) (j - 1)) := by rw [Nat.mul_assoc]
    have : m ∣ (j / n.gcd j) * binom n j := by
      rw [hmul]; exact Nat.dvd_mul_right _ _
    have hcop' : m.Coprime (j / n.gcd j) := hcop
    exact hcop'.dvd_of_dvd_mul_left this

theorem erdos699_i2_divisor (j : Nat) (hj : 3 ≤ j) :
    ∃ m, 3 ≤ m ∧ m ∣ binom (2 * j + 3) 2 ∧ m ∣ binom (2 * j + 3) j :=
  ⟨_, i2_m_divides j hj⟩

end P699I2
