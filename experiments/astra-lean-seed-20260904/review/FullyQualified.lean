import AdjacentBinomialGcd

set_option autoImplicit false

example : ∀ j k : _root_.Nat,
    _root_.Eq
      (_root_.Nat.mul (_root_.Nat.add k 1)
        (_root_.Nat.gcd (_root_.Nat.choose j k)
          (_root_.Nat.choose (_root_.Nat.add j 1) (_root_.Nat.add k 1))))
      (_root_.Nat.mul (_root_.Nat.choose j k)
        (_root_.Nat.gcd (_root_.Nat.add k 1) (_root_.Nat.add j 1))) :=
  AdjacentBinomialGcd.adjacent_binomial_gcd

example : ∀ U A B C j : _root_.Nat,
    @_root_.Dvd.dvd _root_.Nat _root_.Nat.instDvd U B →
    _root_.Eq (_root_.Nat.gcd U A) 1 →
    _root_.Eq (_root_.Nat.mul A C) (_root_.Nat.mul (_root_.Nat.add j 1) B) →
    @_root_.Dvd.dvd _root_.Nat _root_.Nat.instDvd U C :=
  AdjacentBinomialGcd.divisor_transfer

set_option pp.all true in
#check @AdjacentBinomialGcd.adjacent_binomial_gcd
set_option pp.all true in
#check @AdjacentBinomialGcd.divisor_transfer
