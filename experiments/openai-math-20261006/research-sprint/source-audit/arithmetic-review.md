# Independent arithmetic cross-review

**Verdict: PASS as an informal proof** of the reduced-denominator cubic and the seven stated infinite diagonals in [the arithmetic note](../arithmetic/README.md). This is model review, not formal verification or a novelty assessment. No duplicate graph edge is added.

The positional localization follows from carry-free base-p addition whenever the relevant prime divides binomial(n,3). At positions 1 and 2 the identity nu=vj gives the products u(u−v) and 4u(v−u)(v−2u), respectively. Coprimality of B and C and oddness of C give BC dividing Q.

The restoration of the omitted small factors is sound: BC is odd, while Q is even. If D=6, n is prime to 3 and hence so is v; the three factors in Q cover every residue class for u modulo 3. In that case BC has no factor 3. Consequently DBC divides Q. No position-0 assumption is used in this cubic step.

The exact identity 4g³Q=d(n²−d²) yields the necessary inequality. On 0<x<1/2, the maximum of x(1−x)(1−2x) is 1/(6√3), yielding both displayed bounds in v. The n≡2 modulo4 argument correctly uses position0; its central-case exclusion and the remaining B dividing5 or8 reduction are valid.

For d=4,8,...,28 and 4|n, j is even and g≥2. Substituting n=x+d+8 into 32(n−1)(n−2)−d(n²−d²) gives exactly the three coefficients displayed in the note. Each is strictly positive for the seven specified values of d, so the infinite assertion follows from the inequality contradiction. The d=32 illustration is only a failure of this size exclusion, as the note explicitly says.

This review did not rely on finite enumerations as proof of the infinite families and does not establish that the full i=3 slice or P699 is solved.

## Growing strip and parity refinement

**PASS:** under the residual assumptions 4|n, j<n/2 and even d=n−2j≥4, write Q=kP with P=(n−1)(n−2)>0 and integer k≥1. The exact formula 4g³Q=d(n²−d²) gives integer m=4g³k−d and mP=d(3n−d²−2).

If m≥1 then P≤d(3n−d²−2), contradicting the exact identity

    4[P−d(3n−d²−2)]
      =(2n−3d−3)²+4(d−4)³+39(d−4)²+110(d−4)+71 > 0.

If m=0 then d²=3n−2, impossible modulo4 because d is even and 4|n. Thus m≤−1, yielding d³≥n²+(d−1)(3n−2)>n² exactly as the strengthened note claims.

This review found an additional parity refinement, communicated to the parent and arithmetic author: m is even, so actually m≤−2. Therefore

    d³≥2n²+(d−2)(3n−2)>2n².

If 4|d then 4|m, yielding the still stronger

    d³≥4n²+(d−4)(3n−2).

Also m<0 gives d>4g³k≥4g³. For 4|d, j is even and g≥2, hence d>32. This disposes of the entire d=32 diagonal along with d=4,8,...,28 in the residual branch; the already proved n≡2 mod4 branch covers its other cases. No new prime-factor or probabilistic premise is used.

The central d=0 argument applies to every even n. For d=2 in the residual branch, Q=(n²−4)/(2g³)≤(n²−4)/2<P, since their difference is (n−2)(n−4)/2>0 when j>3. Thus the small omitted distances do not leave a gap in the near-central strip.
