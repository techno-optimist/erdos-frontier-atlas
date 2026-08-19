#!/usr/bin/env python3
"""Exact arithmetic replay for the conditional literal h=8 corollary."""

from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def gap(epsilon):
    section = Fraction(30, 81)
    sigma = Fraction(4, 3)*epsilon-2*epsilon**2
    beta = Fraction(30, 2916)+2*sigma
    return (Fraction(7, 24)-epsilon)**2-8*beta


def polynomial(epsilon):
    return (129-1022544*epsilon+1539648*epsilon**2)/46656


def main():
    source = Path(__file__).read_bytes()
    section = Fraction(30, 81)
    need(section == Fraction(10, 27), "q9 section normalization")
    marker0 = 2*Fraction(1, 72)*section
    need(marker0 == Fraction(30, 2916) == Fraction(5, 486),
         "exceptional-plane normalization")
    zero_gap = Fraction(7, 24)**2-8*marker0
    need(zero_gap == Fraction(43, 15552) == Fraction(129, 46656),
         "zero-epsilon gap")

    probes = (Fraction(0), Fraction(1, 7926), Fraction(1, 7925),
              Fraction(1, 4000), Fraction(7, 12345))
    for epsilon in probes:
        formula = (Fraction(43, 15552)-Fraction(263, 12)*epsilon+
                   33*epsilon**2)
        need(gap(epsilon) == formula == polynomial(epsilon),
             "gap polynomial identity")

    discriminant = 1022544**2-4*1539648*129
    need(discriminant == 1044801773568 == 5184**2*38878,
         "root discriminant")
    # For a*x^2-b*x+c, rationalization gives the smaller root
    # 2*c/(b+sqrt(D)); dividing numerator and denominator by six gives
    # 43/(170424+864*sqrt(38878)).
    need(2*129 == 258 and 1022544//6 == 170424 and
         5184//6 == 864 and 258//6 == 43,
         "equivalent radical forms")

    inside = Fraction(1, 7926)
    outside = Fraction(1, 7925)
    inside_gap = polynomial(inside)
    outside_gap = polynomial(outside)
    need(inside_gap == Fraction(7651, 27138877632) > 0,
         "reciprocal inside endpoint")
    need(outside_gap == -Fraction(65309, 976753080000) < 0,
         "reciprocal outside endpoint")
    # G is strictly decreasing throughout the relevant EHPS domain.
    need(-Fraction(263, 12)+66*Fraction(1, 4000) < 0,
         "small-interval monotonicity")
    # The sign bracket and monotonicity put the first root strictly between
    # 1/7926 and 1/7925, itself below 1/4000.
    need(inside < outside < Fraction(1, 4000),
         "exceptional-domain containment")

    getcontext().prec = 50
    radical_root = (Decimal(258) /
                    (Decimal(1022544)+Decimal(discriminant).sqrt()))
    need(str(radical_root).startswith(
         "0.000126179913339958487458124229320654243766"),
         "root decimal")
    need(Path(__file__).read_bytes() == source, "source mutation")

    print("PASS_H8_C9_30_ARITHMETIC")
    print("H8_SECTION 30/81=10/27 marker0=30/2916 zero_gap=43/15552")
    print("H8_GAP (129-1022544*epsilon+1539648*epsilon^2)/46656")
    print("H8_MAXIMAL_SMALL_INTERVAL "
          "root=258/(1022544+sqrt(1044801773568)) endpoint_included")
    print("H8_RECIPROCAL_STRICT n>=7926 inside_gap=7651/27138877632 "
          "outside_gap=-65309/976753080000")
    print("PASS_H8_SOURCE_NONMUTATION")


if __name__ == "__main__":
    main()
