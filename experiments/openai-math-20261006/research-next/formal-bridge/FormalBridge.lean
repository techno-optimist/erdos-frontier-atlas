import CubicStrip

namespace FormalBridge

def Q (u v : Int) : Int := u*(v-u)*(v-2*u)

theorem cancel_coprime (a b c : Int) (hg : Int.gcd a b = 1)
    (h : a ∣ b*c) : a ∣ c := by
  have hh := Int.dvd_gcd_mul_iff_dvd_mul.mpr h
  simpa [hg] using hh

theorem coprime_product (a b x : Int) (hg : Int.gcd a b = 1)
    (ha : a ∣ x) (hb : b ∣ x) : a*b ∣ x := by
  obtain ⟨k, hk⟩ := ha
  have hh : b ∣ a*k := by rw [← hk]; exact hb
  have hc : b ∣ k := cancel_coprime b a k (by simpa [Int.gcd_comm] using hg) hh
  obtain ⟨l, hl⟩ := hc
  exact ⟨l, by grind⟩

theorem q_even (u v : Int) : 2 ∣ Q u v := by
  apply Int.dvd_of_emod_eq_zero
  have hu : u % 2 = 0 ∨ u % 2 = 1 := by omega
  have hv : v % 2 = 0 ∨ v % 2 = 1 := by omega
  rcases hu with hu | hu <;> rcases hv with hv | hv
  all_goals simp [Q, Int.mul_emod, Int.sub_emod, hu, hv]

theorem q_three (u v : Int) (hv3 : ¬ 3 ∣ v) : 3 ∣ Q u v := by
  apply Int.dvd_of_emod_eq_zero
  have hu : u % 3 = 0 ∨ u % 3 = 1 ∨ u % 3 = 2 := by omega
  have hv : v % 3 = 1 ∨ v % 3 = 2 := by
    have hh : v % 3 ≠ 0 := fun h => hv3 (Int.dvd_of_emod_eq_zero h)
    omega
  rcases hu with hu | hu | hu <;> rcases hv with hv | hv
  all_goals simp [Q, Int.mul_emod, Int.sub_emod, hu, hv]

/-- Aggregated positional conditions with the omitted small factors supplied explicitly. -/
theorem restore_cubic (n u v B C D : Int)
    (hB : B ∣ u*(v-u)) (hC : C ∣ 4*Q u v)
    (hC4 : Int.gcd C 4 = 1) (hBC : Int.gcd B C = 1)
    (hD : D = 2 ∨ D = 6) (hDBC : Int.gcd D (B*C) = 1)
    (h3 : D = 6 → ¬ 3 ∣ v)
    (hfactor : (n-1)*(n-2) = D*(B*C)) : (n-1)*(n-2) ∣ Q u v := by
  have hb : B ∣ Q u v := by
    obtain ⟨k, hk⟩ := hB
    exact ⟨k*(v-2*u), by simp only [Q]; grind⟩
  have hc := cancel_coprime C 4 (Q u v) hC4 hC
  have hbc := coprime_product B C (Q u v) hBC hb hc
  have hd : D ∣ Q u v := by
    rcases hD with hD | hD
    · simpa [hD] using q_even u v
    · have ht := coprime_product 2 3 (Q u v) (by decide) (q_even u v) (q_three u v (h3 hD))
      simpa [hD] using ht
  rw [hfactor]
  exact coprime_product D (B*C) (Q u v) hDBC hd hbc

/-- Positional congruences transport through n*u=v*j without inverting g. -/
theorem local_linear (n j u v M t r : Int) (he : n*u=v*j)
    (hn : M ∣ n-t) (hj : M ∣ j-r) : M ∣ t*u-r*v := by
  obtain ⟨a, ha⟩ := hn
  obtain ⟨b, hb⟩ := hj
  exact ⟨v*b-u*a, by grind⟩

theorem position_one (n j u v M : Int) (he : n*u=v*j)
    (hn : M ∣ n-1) (hj : ∃ r : Int, 0 ≤ r ∧ r ≤ 1 ∧ M ∣ j-r) :
    M ∣ u*(v-u) := by
  obtain ⟨r, hr0, hr1, hr⟩ := hj
  have hl := local_linear n j u v M 1 r he hn hr
  have hcases : r=0 ∨ r=1 := by omega
  rcases hcases with rfl | rfl
  · obtain ⟨a, ha⟩ := hl
    exact ⟨a*(v-u), by grind⟩
  · obtain ⟨a, ha⟩ := hl
    exact ⟨-u*a, by grind⟩

theorem position_two (n j u v M : Int) (he : n*u=v*j)
    (hn : M ∣ n-2) (hj : ∃ r : Int, 0 ≤ r ∧ r ≤ 2 ∧ M ∣ j-r) :
    M ∣ 4*Q u v := by
  obtain ⟨r, hr0, hr2, hr⟩ := hj
  have hl := local_linear n j u v M 2 r he hn hr
  have hcases : r=0 ∨ r=1 ∨ r=2 := by omega
  rcases hcases with rfl | rfl | rfl
  · obtain ⟨a, ha⟩ := hl
    exact ⟨a*(2*u-v)*(2*u-2*v), by simp only [Q]; grind⟩
  · obtain ⟨a, ha⟩ := hl
    exact ⟨(2*u)*a*(2*u-2*v), by simp only [Q]; grind⟩
  · obtain ⟨a, ha⟩ := hl
    exact ⟨(2*u)*(2*u-v)*a, by simp only [Q]; grind⟩

/-- Each block is coprime to the product of later blocks. -/
def CoprimeBlocks : List Int → Prop
  | [] => True
  | a :: xs => Int.gcd a xs.prod = 1 ∧ CoprimeBlocks xs

def LocalAt (n j t : Int) (xs : List Int) : Prop :=
  ∀ M ∈ xs, M ∣ n-t ∧ ∃ r : Int, 0 ≤ r ∧ r ≤ t ∧ M ∣ j-r

/-- The usual least-residue formulation supplies the explicit local congruence data. -/
theorem localAt_of_residues (n j t : Int) (xs : List Int)
    (h : ∀ M ∈ xs, 0 < M ∧ M ∣ n-t ∧ j % M ≤ t) : LocalAt n j t xs := by
  intro M hM
  have hh := h M hM
  exact ⟨hh.2.1, j % M, Int.emod_nonneg j (by omega), hh.2.2, Int.dvd_self_sub_emod⟩

theorem blocks_product_dvd (xs : List Int) (x : Int) (hc : CoprimeBlocks xs)
    (hd : ∀ M ∈ xs, M ∣ x) : xs.prod ∣ x := by
  induction xs with
  | nil => simp
  | cons a xs ih =>
    have hh : a ∣ x := hd a (by simp)
    have ht : xs.prod ∣ x := ih hc.2 (by intro M hM; exact hd M (by simp [hM]))
    exact coprime_product a xs.prod x hc.1 hh ht

theorem positional_products (n j u v : Int) (bs cs : List Int)
    (he : n*u=v*j) (hb : CoprimeBlocks bs) (hc : CoprimeBlocks cs)
    (hlb : LocalAt n j 1 bs) (hlc : LocalAt n j 2 cs) :
    bs.prod ∣ u*(v-u) ∧ cs.prod ∣ 4*Q u v ∧ Int.gcd bs.prod cs.prod = 1 := by
  have hB : bs.prod ∣ u*(v-u) := blocks_product_dvd bs _ hb (by
    intro M hM
    exact position_one n j u v M he (hlb M hM).1 (hlb M hM).2)
  have hC : cs.prod ∣ 4*Q u v := blocks_product_dvd cs _ hc (by
    intro M hM
    exact position_two n j u v M he (hlc M hM).1 (hlc M hM).2)
  have hbN : bs.prod ∣ n-1 := blocks_product_dvd bs _ hb (by
    intro M hM; exact (hlb M hM).1)
  have hcN : cs.prod ∣ n-2 := blocks_product_dvd cs _ hc (by
    intro M hM; exact (hlc M hM).1)
  refine ⟨hB, hC, Int.gcd_eq_one_iff.mpr ?_⟩
  intro c hcb hcc
  have h1 := Int.dvd_trans hcb hbN
  have h2 := Int.dvd_trans hcc hcN
  have hh := Int.dvd_sub h1 h2
  have hi : (n-1)-(n-2) = 1 := by omega
  simpa [hi] using hh

/-- Construct the positive quotient and its strip identity from reduced cubic divisibility. -/
theorem quotient_from_cubic (n j d g u v : Int)
    (hn : 3 ≤ n) (_hg : 0 < g) (hu : 0 < u) (hvu : 2*u < v)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hdiv : (n-1)*(n-2) ∣ Q u v) :
    ∃ k : Int, 1 ≤ k ∧ Q u v = (n-1)*(n-2)*k ∧
      ((4*g*g*g)*k-d)*((n-1)*(n-2)) = d*(3*n-d*d-2) := by
  obtain ⟨k, hk⟩ := hdiv
  have hp : 0 < (n-1)*(n-2) := Int.mul_pos (by omega) (by omega)
  have hq : 0 < Q u v := by
    exact Int.mul_pos (Int.mul_pos hu (by omega)) (by omega)
  have hkpos : 1 ≤ k := by
    by_cases hh : 1 ≤ k
    · exact hh
    have hkn : k ≤ 0 := by omega
    have hprod := Int.mul_nonpos_of_nonneg_of_nonpos (Int.le_of_lt hp) hkn
    omega
  refine ⟨k, hkpos, hk, ?_⟩
  have hid : 4*g*g*g*Q u v = d*(n*n-d*d) := by
    simp only [Q]
    grind
  have hs := congrArg (fun x : Int => 4*g*g*g*x) hk
  grind

/-- No abstract quotient or parity premise is needed once the cubic divisor is supplied. -/
theorem strip_from_cubic (n j d g u v : Int)
    (hn : 3 ≤ n) (hd4 : 4 ≤ d) (hg : 0 < g) (hu : 0 < u) (hvu : 2*u < v)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a)
    (hdiv : (n-1)*(n-2) ∣ Q u v) :
    2*(n*n)+(d-2)*(3*n-2) ≤ d*d*d ∧ 2*(n*n) < d*d*d ∧ 4*g*g*g < d := by
  obtain ⟨k, hk, hq, he⟩ := quotient_from_cubic n j d g u v hn hg hu hvu hnv hju hd hdiv
  obtain ⟨a, ha⟩ := hn4
  have hde : ∃ b : Int, d = 2*b := ⟨2*a-j, by omega⟩
  have hne := CubicStrip.parity_nonzero n d ⟨a, ha⟩ hde
  have hme : ∃ q : Int, (4*g*g*g)*k-d = 2*q := by
    refine ⟨2*g*g*g*k-2*a+j, ?_⟩
    grind
  have hs := CubicStrip.even_quotient_strip n d ((4*g*g*g)*k-d) hn hd4 he hne hme
  have hgap := CubicStrip.gcd_gap n d ((4*g*g*g)*k-d) g k hn hd4 he hne
    (Int.le_of_lt hg) hk rfl
  exact ⟨hs.1, hs.2, hgap⟩

/-- End-to-end strip from explicit aggregated positional divisibility and factor data. -/
theorem strip_from_positional_products (n j d g u v B C D : Int)
    (hn : 3 ≤ n) (hd4 : 4 ≤ d) (hg : 0 < g) (hu : 0 < u) (hvu : 2*u < v)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a)
    (hB : B ∣ u*(v-u)) (hC : C ∣ 4*Q u v)
    (hC4 : Int.gcd C 4 = 1) (hBC : Int.gcd B C = 1)
    (hD : D = 2 ∨ D = 6) (hDBC : Int.gcd D (B*C) = 1)
    (h3 : D = 6 → ¬ 3 ∣ v)
    (hfactor : (n-1)*(n-2) = D*(B*C)) :
    2*(n*n)+(d-2)*(3*n-2) ≤ d*d*d ∧ 2*(n*n) < d*d*d ∧ 4*g*g*g < d := by
  have hdiv := restore_cubic n u v B C D hB hC hC4 hBC hD hDBC h3 hfactor
  exact strip_from_cubic n j d g u v hn hd4 hg hu hvu hnv hju hd hn4 hdiv

/-- The full checked bridge from finite positional block data to the cubic strip.
The input blocks need not be prime powers; their factorization and coprimality
are explicit hypotheses. Kummer's derivation of these data is not assumed here. -/
theorem strip_from_blocks (n j d g u v D : Int) (bs cs : List Int)
    (hn : 3 ≤ n) (hd4 : 4 ≤ d) (hg : 0 < g) (hu : 0 < u) (hvu : 2*u < v)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a)
    (hb : CoprimeBlocks bs) (hc : CoprimeBlocks cs)
    (hlb : LocalAt n j 1 bs) (hlc : LocalAt n j 2 cs)
    (hC4 : Int.gcd cs.prod 4 = 1)
    (hD : D = 2 ∨ D = 6) (hDBC : Int.gcd D (bs.prod*cs.prod) = 1)
    (h3 : D = 6 → ¬ 3 ∣ n)
    (hfactor : (n-1)*(n-2) = D*(bs.prod*cs.prod)) :
    2*(n*n)+(d-2)*(3*n-2) ≤ d*d*d ∧ 2*(n*n) < d*d*d ∧ 4*g*g*g < d := by
  have he : n*u=v*j := by grind
  have hh := positional_products n j u v bs cs he hb hc hlb hlc
  have h3v : D = 6 → ¬ 3 ∣ v := by
    intro hD hdiv
    obtain ⟨k, hk⟩ := hdiv
    apply h3 hD
    exact ⟨g*k, by grind⟩
  exact strip_from_positional_products n j d g u v bs.prod cs.prod D
    hn hd4 hg hu hvu hnv hju hd hn4 hh.1 hh.2.1 hC4 hh.2.2 hD hDBC h3v hfactor

/-- When the stripped factor is two, no modulo-three premise is needed. -/
theorem strip_from_blocks_two (n j d g u v : Int) (bs cs : List Int)
    (hn : 3 ≤ n) (hd4 : 4 ≤ d) (hg : 0 < g) (hu : 0 < u) (hvu : 2*u < v)
    (hnv : n = g*v) (hju : j = g*u) (hd : d = n-2*j)
    (hn4 : ∃ a : Int, n = 4*a)
    (hb : CoprimeBlocks bs) (hc : CoprimeBlocks cs)
    (hlb : LocalAt n j 1 bs) (hlc : LocalAt n j 2 cs)
    (hC4 : Int.gcd cs.prod 4 = 1) (h2BC : Int.gcd 2 (bs.prod*cs.prod) = 1)
    (hfactor : (n-1)*(n-2) = 2*(bs.prod*cs.prod)) :
    2*(n*n)+(d-2)*(3*n-2) ≤ d*d*d ∧ 2*(n*n) < d*d*d ∧ 4*g*g*g < d := by
  exact strip_from_blocks n j d g u v 2 bs cs hn hd4 hg hu hvu hnv hju hd hn4
    hb hc hlb hlc hC4 (Or.inl rfl) h2BC (by omega) hfactor

#print axioms cancel_coprime
#print axioms coprime_product
#print axioms q_even
#print axioms q_three
#print axioms restore_cubic
#print axioms local_linear
#print axioms position_one
#print axioms position_two
#print axioms localAt_of_residues
#print axioms blocks_product_dvd
#print axioms positional_products
#print axioms quotient_from_cubic
#print axioms strip_from_cubic
#print axioms strip_from_positional_products
#print axioms strip_from_blocks
#print axioms strip_from_blocks_two
end FormalBridge
