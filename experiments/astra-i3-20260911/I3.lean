/-
i=3 slice of P699 in gcd form.

For 4 ≤ j and 2*j ≤ n, gcd(binom n 3, binom n j) ≥ 2.
If n % 4 = 3 then that gcd is odd, hence ≥ 3. Not a solution of #699.
-/
import Init.Data.Nat.Gcd
import Init.Data.Nat.Coprime
import Init.Data.Nat.Dvd
import Init.Data.Nat.Lemmas
import Init.Omega

namespace P699I3

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

theorem two_dvd_pred (n : Nat) : 2 ∣ n * (n - 1) := by
  match n with
  | 0 => exact ⟨0, by simp⟩
  | n + 1 =>
    simpa [Nat.mul_comm] using two_dvd_mul_succ n

theorem three_mod_cases (n : Nat) : n % 3 = 0 ∨ n % 3 = 1 ∨ n % 3 = 2 := by
  have h := Nat.mod_lt n (by decide : 0 < (3 : Nat))
  match n % 3, h with
  | 0, _ => exact Or.inl rfl
  | 1, _ => exact Or.inr (Or.inl rfl)
  | 2, _ => exact Or.inr (Or.inr rfl)
  | k + 3, hk =>
    have : 3 ≤ k + 3 := Nat.le_add_left 3 k
    exact absurd hk (Nat.not_lt_of_ge this)

theorem three_dvd_three_consec (n : Nat) : 3 ∣ n * (n - 1) * (n - 2) := by
  have h := three_mod_cases n
  rcases h with h | h | h
  · have hd : 3 ∣ n := Nat.dvd_of_mod_eq_zero h
    exact Nat.dvd_mul_right_of_dvd (Nat.dvd_mul_right_of_dvd hd _) _
  · have hn : 1 ≤ n := by
      apply Nat.pos_of_ne_zero
      intro hz; simp [hz] at h
    have : n = n - 1 + 1 := (Nat.sub_add_cancel hn).symm
    have hmod : (n - 1 + 1) % 3 = 1 := by
      rw [← this, h]
    have : ((n - 1) % 3 + 1) % 3 = 1 := by
      simpa [Nat.add_mod] using hmod
    have hr : (n - 1) % 3 = 0 := by omega
    have hd : 3 ∣ n - 1 := Nat.dvd_of_mod_eq_zero hr
    exact Nat.dvd_mul_right_of_dvd (Nat.dvd_mul_left_of_dvd hd _) _
  · have hn : 2 ≤ n := by omega
    have hr : (n - 2) % 3 = 0 := by omega
    have hd : 3 ∣ n - 2 := Nat.dvd_of_mod_eq_zero hr
    exact Nat.dvd_mul_left_of_dvd hd _

theorem six_dvd_three_consec (n : Nat) : 6 ∣ n * (n - 1) * (n - 2) := by
  have h2 : 2 ∣ n * (n - 1) * (n - 2) :=
    Nat.dvd_mul_right_of_dvd (two_dvd_pred n) _
  have h3 := three_dvd_three_consec n
  have hc : Nat.Coprime 2 3 := by decide
  exact hc.mul_dvd_of_dvd_of_dvd h2 h3

theorem six_mul_binom_three : ∀ n, 6 * binom n 3 = n * (n - 1) * (n - 2)
  | 0 => rfl
  | 1 => rfl
  | 2 => rfl
  | n + 3 => by
    change 6 * (binom (n + 2) 2 + binom (n + 2) 3) = (n + 3) * (n + 2) * (n + 1)
    rw [Nat.mul_add]
    have h2 : 2 * binom (n + 2) 2 = (n + 2) * (n + 1) := by
      rw [binom_two]
      exact Nat.mul_div_cancel' (two_dvd_pred (n + 2))
    have hleft : 6 * binom (n + 2) 2 = 3 * ((n + 2) * (n + 1)) := by
      have : (6 : Nat) = 3 * 2 := rfl
      rw [this, Nat.mul_assoc, h2]
    have ih := six_mul_binom_three (n + 2)
    have : 6 * binom (n + 2) 3 = (n + 2) * (n + 1) * n := ih
    rw [hleft, this]
    calc
      3 * ((n + 2) * (n + 1)) + (n + 2) * (n + 1) * n
          = (n + 2) * (n + 1) * 3 + (n + 2) * (n + 1) * n := by ac_rfl
      _ = (n + 2) * (n + 1) * (3 + n) := by rw [← Nat.mul_add]
      _ = (n + 2) * (n + 1) * (n + 3) := by rw [Nat.add_comm 3 n]
      _ = (n + 3) * (n + 2) * (n + 1) := by ac_rfl

theorem binom_three (n : Nat) : binom n 3 = n * (n - 1) * (n - 2) / 6 := by
  have h := six_mul_binom_three n
  have hd := six_dvd_three_consec n
  have : n * (n - 1) * (n - 2) = 6 * (n * (n - 1) * (n - 2) / 6) :=
    (Nat.mul_div_cancel' hd).symm
  have : 6 * binom n 3 = 6 * (n * (n - 1) * (n - 2) / 6) := h.trans this
  exact Nat.mul_left_cancel (by decide : 0 < (6 : Nat)) this


theorem fac_three_le (j : Nat) (h : 3 ≤ j) :
    fac j = j * (j - 1) * (j - 2) * fac (j - 3) := by
  match j with
  | 0 => omega
  | 1 => omega
  | 2 => omega
  | j + 3 =>
    simp [fac]
    ac_rfl

theorem binom_pred3_identity (n j : Nat) (hj : 3 ≤ j) (hjn : j ≤ n) :
    j * (j - 1) * (j - 2) * binom n j = n * (n - 1) * (n - 2) * binom (n - 3) (j - 3) := by
  have hpos : 0 < fac (j - 3) * fac (n - j) := Nat.mul_pos (fac_pos _) (fac_pos _)
  have hL : j * (j - 1) * (j - 2) * binom n j * (fac (j - 3) * fac (n - j)) = fac n := by
    have ih := binom_mul_fac n j hjn
    have hf := fac_three_le j hj
    calc
      j * (j - 1) * (j - 2) * binom n j * (fac (j - 3) * fac (n - j))
          = binom n j * fac j * fac (n - j) := by rw [hf]; ac_rfl
      _ = fac n := ih
  have hn3 : 3 ≤ n := Nat.le_trans hj hjn
  have hR : n * (n - 1) * (n - 2) * binom (n - 3) (j - 3) * (fac (j - 3) * fac (n - j)) = fac n := by
    have hle : j - 3 ≤ n - 3 := by omega
    have ih := binom_mul_fac (n - 3) (j - 3) hle
    have hsub : (n - 3) - (j - 3) = n - j := by omega
    have hfacn : fac n = n * (n - 1) * (n - 2) * fac (n - 3) := by
      match n with
      | 0 => omega
      | 1 => omega
      | 2 => omega
      | n + 3 =>
        simp [fac]
        ac_rfl
    calc
      n * (n - 1) * (n - 2) * binom (n - 3) (j - 3) * (fac (j - 3) * fac (n - j))
          = n * (n - 1) * (n - 2) * (binom (n - 3) (j - 3) * fac (j - 3) * fac ((n - 3) - (j - 3))) := by
            rw [hsub]; ac_rfl
      _ = n * (n - 1) * (n - 2) * fac (n - 3) := by rw [ih]
      _ = fac n := hfacn.symm
  exact Nat.eq_of_mul_eq_mul_right hpos (hL.trans hR.symm)



theorem i3_gcd_ge_two_of_gt (n j : Nat) (hj : 3 ≤ j) (hjn : j ≤ n)
    (hgt : j * (j - 1) * (j - 2) < binom n 3) :
    2 ≤ Nat.gcd (binom n 3) (binom n j) := by
  have hC : 0 < binom n 3 := Nat.zero_lt_of_lt hgt
  have hg : 0 < Nat.gcd (binom n 3) (binom n j) := Nat.gcd_pos_of_pos_left _ hC
  have hid := binom_pred3_identity n j hj hjn
  have h6 := six_mul_binom_three n
  have hdiv : binom n 3 ∣ j * (j - 1) * (j - 2) * binom n j := by
    rw [hid]
    refine ⟨6 * binom (n - 3) (j - 3), ?_⟩
    calc
      n * (n - 1) * (n - 2) * binom (n - 3) (j - 3)
          = (6 * binom n 3) * binom (n - 3) (j - 3) := by rw [h6]
      _ = binom n 3 * (6 * binom (n - 3) (j - 3)) := by ac_rfl
  have hone : 1 ≤ Nat.gcd (binom n 3) (binom n j) := Nat.succ_le_of_lt hg
  cases Nat.lt_or_eq_of_le hone with
  | inl hlt => exact hlt
  | inr heq =>
    have hcop : (binom n 3).Coprime (binom n j) :=
      Nat.coprime_iff_gcd_eq_one.2 heq.symm
    have : binom n 3 ∣ j * (j - 1) * (j - 2) := hcop.dvd_of_dvd_mul_right hdiv
    have jpos : 0 < j := Nat.lt_of_lt_of_le (by decide : (0 : Nat) < 3) hj
    have hjm : 1 ≤ j - 2 := Nat.le_sub_of_add_le (Nat.le_trans (by decide : (3 : Nat) ≤ 3) hj)
    have hposP : 0 < j * (j - 1) * (j - 2) :=
      Nat.mul_pos (Nat.mul_pos jpos (by omega : 0 < j - 1))
        (Nat.lt_of_lt_of_le (by decide : (0 : Nat) < 1) hjm)
    have hle := Nat.le_of_dvd hposP this
    exact (Nat.not_le_of_gt hgt hle).elim

theorem binom_three_odd_of_mod4 (n : Nat) (h : n % 4 = 3) : ¬ 2 ∣ binom n 3 := by
  have h6 := six_mul_binom_three n
  intro hd
  have hn : n = 4 * (n / 4) + 3 := by
    have := Nat.div_add_mod n 4
    rw [h] at this
    exact this.symm
  have h4 : 4 ∣ 6 * binom n 3 := by
    rcases hd with ⟨k, hk⟩
    refine ⟨3 * k, ?_⟩
    calc
      6 * binom n 3 = 6 * (2 * k) := by rw [hk]
      _ = 4 * (3 * k) := by
        have h63 : (6 : Nat) * 2 = 4 * 3 := rfl
        calc
          6 * (2 * k) = (6 * 2) * k := by rw [← Nat.mul_assoc]
          _ = (4 * 3) * k := by rw [h63]
          _ = 4 * (3 * k) := by rw [Nat.mul_assoc]
  have hL : (6 * binom n 3) % 4 = 0 := Nat.mod_eq_zero_of_dvd h4
  have hR : (n * (n - 1) * (n - 2)) % 4 = 2 := by
    have h1 : n - 1 = 4 * (n / 4) + 2 := by omega
    have h2 : n - 2 = 4 * (n / 4) + 1 := by omega
    rw [h1, h2, hn]
    simp [Nat.mul_add, Nat.add_mul, Nat.mul_mod, Nat.add_mod, Nat.mul_mod_right]
  have : (n * (n - 1) * (n - 2)) % 4 = 0 := by
    rw [← h6]; exact hL
  omega

theorem i3_gcd_ge_three_of_mod4_of_gt (n j : Nat) (hj : 3 ≤ j) (hjn : j ≤ n)
    (hgt : j * (j - 1) * (j - 2) < binom n 3) (hn : n % 4 = 3) :
    3 ≤ Nat.gcd (binom n 3) (binom n j) := by
  have h2 := i3_gcd_ge_two_of_gt n j hj hjn hgt
  have hodd := binom_three_odd_of_mod4 n hn
  cases Nat.lt_or_eq_of_le h2 with
  | inl hlt => exact hlt
  | inr heq =>
    have : 2 ∣ Nat.gcd (binom n 3) (binom n j) := by
      rw [← heq]; exact ⟨1, rfl⟩
    exact False.elim (hodd (Nat.dvd_trans this (Nat.gcd_dvd_left _ _)))

theorem fac_dvd_succ (k : Nat) : fac k ∣ fac (k + 1) :=
  ⟨k + 1, by rw [fac_succ, Nat.mul_comm]⟩

theorem fac_dvd_fac_of_le (a b : Nat) (h : a ≤ b) : fac a ∣ fac b := by
  induction h with
  | refl => exact Nat.dvd_refl _
  | step h ih => exact Nat.dvd_trans ih (fac_dvd_succ _)

theorem fac_three_n (n : Nat) (h : 3 ≤ n) :
    fac n = n * (n - 1) * (n - 2) * fac (n - 3) :=
  fac_three_le n h

theorem three_falling_dvd (n j : Nat) (hj : 3 ≤ j) (hjn : j ≤ n) :
    n * (n - 1) * (n - 2) ∣ binom n j * fac j := by
  have hn3 : 3 ≤ n := Nat.le_trans hj hjn
  have hmul := binom_mul_fac n j hjn
  have hfacn := fac_three_n n hn3
  have hle : n - j ≤ n - 3 := by omega
  rcases fac_dvd_fac_of_le (n - j) (n - 3) hle with ⟨k, hk⟩
  have hpos : 0 < fac (n - j) := fac_pos _
  have : binom n j * fac j * fac (n - j)
      = (n * (n - 1) * (n - 2) * k) * fac (n - j) := by
    calc
      binom n j * fac j * fac (n - j) = fac n := hmul
      _ = n * (n - 1) * (n - 2) * fac (n - 3) := hfacn
      _ = n * (n - 1) * (n - 2) * (k * fac (n - j)) := by
        rw [hk]; ac_rfl
      _ = (n * (n - 1) * (n - 2) * k) * fac (n - j) := by ac_rfl
  have : binom n j * fac j = n * (n - 1) * (n - 2) * k :=
    Nat.eq_of_mul_eq_mul_right hpos this
  exact ⟨k, this⟩

theorem cancel_coprime_fac (n j d : Nat) (hj : 3 ≤ j) (hjn : j ≤ n)
    (hd : d ∣ binom n 3) (hc : Nat.Coprime d (fac j)) :
    d ∣ binom n j := by
  have h6 := six_mul_binom_three n
  have hdN : d ∣ n * (n - 1) * (n - 2) := by
    rcases hd with ⟨t, ht⟩
    refine ⟨6 * t, ?_⟩
    calc
      n * (n - 1) * (n - 2) = 6 * binom n 3 := h6.symm
      _ = 6 * (d * t) := by rw [ht]
      _ = d * (6 * t) := by ac_rfl
  have hf := three_falling_dvd n j hj hjn
  have : d ∣ binom n j * fac j := Nat.dvd_trans hdN hf
  exact hc.dvd_of_dvd_mul_right this

theorem coprime_six_dvd_binom_three (n : Nat) (h : Nat.Coprime n 6) :
    n ∣ binom n 3 := by
  have h6 := six_mul_binom_three n
  have hn : n ∣ n * (n - 1) * (n - 2) :=
    ⟨(n - 1) * (n - 2), by ac_rfl⟩
  have : n ∣ 6 * binom n 3 := by
    rw [h6]; exact hn
  exact h.dvd_of_dvd_mul_left this

theorem coprime_six_cancel (n j : Nat) (hj : 3 ≤ j) (hjn : j < n)
    (h6 : Nat.Coprime n 6) (hf : Nat.Coprime n (fac j)) :
    n ∣ binom n j :=
  cancel_coprime_fac n j n hj (Nat.le_of_lt hjn)
    (coprime_six_dvd_binom_three n h6) hf

end P699I3


