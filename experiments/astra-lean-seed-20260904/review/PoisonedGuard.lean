import AdjacentBinomialGcd

set_option autoImplicit false

namespace ReviewPoison
axiom poison (n : Nat) : n = n

theorem poisoned_adjacent_binomial_gcd (j k : Nat) :
    (k + 1) * Nat.gcd (Nat.choose j k) (Nat.choose (j + 1) (k + 1)) =
      Nat.choose j k * Nat.gcd (k + 1) (j + 1) :=
  Eq.trans (AdjacentBinomialGcd.adjacent_binomial_gcd j k)
    (poison (Nat.choose j k * Nat.gcd (k + 1) (j + 1)))

/-- info: 'ReviewPoison.poisoned_adjacent_binomial_gcd' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms ReviewPoison.poisoned_adjacent_binomial_gcd
end ReviewPoison
