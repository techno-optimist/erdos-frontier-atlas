/-
Complete i=2 case of P699 in gcd form.

For 3 ≤ j and 2*j ≤ n, gcd(binom n 2, binom n j) ≥ 2.
Prime-factor existence is the unique Init gap. Not a solution of #699.
-/
import Init.Data.Nat.Gcd
import Init.Data.Nat.Coprime
import Init.Data.Nat.Dvd
import Init.Data.Nat.Lemmas
import Init.Omega

namespace P699I2All

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

theorem fac_two_le (j : Nat) (h : 2 ≤ j) :
    fac j = j * (j - 1) * fac (j - 2) := by
  match j with
  | 0 => omega
  | 1 => omega
  | j + 2 =>
    simp [fac]
    ac_rfl

theorem binom_pred2_identity (n j : Nat) (hj : 2 ≤ j) (hjn : j ≤ n) :
    j * (j - 1) * binom n j = n * (n - 1) * binom (n - 2) (j - 2) := by
  have hpos : 0 < fac (j - 2) * fac (n - j) := Nat.mul_pos (fac_pos _) (fac_pos _)
  have hL : j * (j - 1) * binom n j * (fac (j - 2) * fac (n - j)) = fac n := by
    have ih := binom_mul_fac n j hjn
    have hf := fac_two_le j hj
    calc
      j * (j - 1) * binom n j * (fac (j - 2) * fac (n - j))
          = binom n j * fac j * fac (n - j) := by rw [hf]; ac_rfl
      _ = fac n := ih
  have hn2 : 2 ≤ n := Nat.le_trans hj hjn
  have hR : n * (n - 1) * binom (n - 2) (j - 2) * (fac (j - 2) * fac (n - j)) = fac n := by
    have hle : j - 2 ≤ n - 2 := by omega
    have ih := binom_mul_fac (n - 2) (j - 2) hle
    have hsub : (n - 2) - (j - 2) = n - j := by omega
    have hfacn : fac n = n * (n - 1) * fac (n - 2) := by
      match n with
      | 0 => omega
      | 1 => omega
      | n + 2 =>
        simp [fac]
        ac_rfl
    calc
      n * (n - 1) * binom (n - 2) (j - 2) * (fac (j - 2) * fac (n - j))
          = n * (n - 1) * (binom (n - 2) (j - 2) * fac (j - 2) * fac ((n - 2) - (j - 2))) := by
            rw [hsub]; ac_rfl
      _ = n * (n - 1) * fac (n - 2) := by rw [ih]
      _ = fac n := hfacn.symm
  exact Nat.eq_of_mul_eq_mul_right hpos (hL.trans hR.symm)

theorem two_mul_binom_two (n : Nat) (h : 2 ≤ n) : n * (n - 1) = 2 * binom n 2 := by
  have hd : 2 ∣ n * (n - 1) := by
    match n with
    | 0 => omega
    | n + 1 =>
      simpa [Nat.mul_comm] using two_dvd_mul_succ n
  rw [binom_two, Nat.mul_div_cancel' hd]

theorem binom_two_gt (n j : Nat) (hj : 3 ≤ j) (hjn : 2 * j ≤ n) :
    j * (j - 1) < binom n 2 := by
  have hn6 : 6 ≤ n := Nat.le_trans (Nat.mul_le_mul_left 2 hj) hjn
  have hn2 : 2 ≤ n := Nat.le_trans (by decide) hn6
  have hmul := two_mul_binom_two n hn2
  have jpos : 0 < j := Nat.lt_of_lt_of_le (by decide : (0 : Nat) < 3) hj
  have j_lt_2j : j < 2 * j := by
    have : j + 0 < j + j := Nat.add_lt_add_left jpos j
    simpa [Nat.two_mul] using this
  have j_lt_n : j < n := Nat.lt_of_lt_of_le j_lt_2j hjn
  have hj1 : 1 ≤ j := Nat.succ_le_of_lt jpos
  have hpred : j - 1 < n - 1 := Nat.sub_lt_sub_right hj1 j_lt_n
  have npos : 0 < n := Nat.lt_of_lt_of_le (by decide : (0 : Nat) < 2) hn2
  have hle : 2 * j * (j - 1) ≤ n * (j - 1) := Nat.mul_le_mul_right (j - 1) hjn
  have hlt' : n * (j - 1) < n * (n - 1) := Nat.mul_lt_mul_of_pos_left hpred npos
  have hassoc : 2 * (j * (j - 1)) = 2 * j * (j - 1) := by ac_rfl
  have hlt : 2 * (j * (j - 1)) < n * (n - 1) := by
    rw [hassoc]
    exact Nat.lt_of_le_of_lt hle hlt'
  have : 2 * (j * (j - 1)) < 2 * binom n 2 := by
    rw [← hmul]; exact hlt
  exact Nat.lt_of_mul_lt_mul_left this

theorem i2_gcd_ge_two (n j : Nat) (hj : 3 ≤ j) (hjn : 2 * j ≤ n) :
    2 ≤ Nat.gcd (binom n 2) (binom n j) := by
  have hgt := binom_two_gt n j hj hjn
  have hC : 0 < binom n 2 := Nat.zero_lt_of_lt hgt
  have hg : 0 < Nat.gcd (binom n 2) (binom n j) := Nat.gcd_pos_of_pos_left _ hC
  have hj2 : 2 ≤ j := Nat.le_trans (by decide) hj
  have jpos : 0 < j := Nat.lt_of_lt_of_le (by decide : (0 : Nat) < 3) hj
  have j_lt_2j : j < 2 * j := by
    have : j + 0 < j + j := Nat.add_lt_add_left jpos j
    simpa [Nat.two_mul] using this
  have hjn' : j ≤ n := Nat.le_of_lt (Nat.lt_of_lt_of_le j_lt_2j hjn)
  have hid := binom_pred2_identity n j hj2 hjn'
  have hn2 : 2 ≤ n := Nat.le_trans hj2 hjn'
  have h2eq := two_mul_binom_two n hn2
  have hdiv : binom n 2 ∣ j * (j - 1) * binom n j := by
    rw [hid, h2eq]
    exact ⟨2 * binom (n - 2) (j - 2), by ac_rfl⟩
  have hjm : 2 ≤ j - 1 := Nat.le_sub_of_add_le hj
  have hone : 1 ≤ Nat.gcd (binom n 2) (binom n j) := Nat.succ_le_of_lt hg
  cases Nat.lt_or_eq_of_le hone with
  | inl hlt => exact hlt
  | inr heq =>
    have hcop : (binom n 2).Coprime (binom n j) :=
      Nat.coprime_iff_gcd_eq_one.2 heq.symm
    have : binom n 2 ∣ j * (j - 1) := hcop.dvd_of_dvd_mul_right hdiv
    have hposjj : 0 < j * (j - 1) :=
      Nat.mul_pos jpos (Nat.lt_of_lt_of_le (by decide : (0 : Nat) < 2) hjm)
    have hle := Nat.le_of_dvd hposjj this
    exact (Nat.not_le_of_gt hgt hle).elim

end P699I2All
