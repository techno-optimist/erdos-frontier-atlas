"""Exact arithmetic checks supplementing the analytic proof; not a proof by testing."""
from fractions import Fraction as Q
from math import comb, factorial
import json
from pathlib import Path

out = {}
for K in range(1,17):
    c = {m: Q((-1)**(m+1)*comb(K,m),m) for m in range(1,K+1)}
    moments = {j: sum(c[m]*m**j for m in c) for j in range(1,K+2)}
    assert moments[1] == 1
    assert all(moments[j] == 0 for j in range(2,K+1))
    leading = Q((-1)**(K+2),factorial(K+1))*moments[K+1]
    assert leading == -Q(1,K+1)
    # The stencil differentiates all monomials through degree K exactly.
    x, h = Q(101,7), Q(2,5)
    for degree in range(K+1):
        stencil = sum(c[m]*(x**degree-(x-m*h)**degree) for m in c)/h
        derivative = 0 if degree == 0 else degree*x**(degree-1)
        assert stencil == derivative
out['stencil'] = 'K=1..16: moments, monomials, leading error all passed'

rows = []
for theta in (Q(1,10),Q(1,2),Q(2,3),Q(8,9),Q(9,10),Q(19,20),Q(99,100)):
    a = 1-Q(3,4)*theta
    K = 1 + int(max(Q(0),(Q(1,2)-a)/(1-theta)))
    delta = Q(1,1000)
    sigma = a+delta
    nu = min(Q(1),delta/theta)
    first = 1-sigma-theta*Q(3,4)+theta*nu/2
    second = Q(1,2)-sigma-K*(1-theta)
    assert first <= -delta/2 and second < -delta
    assert (a<Q(1,3)) == (theta>Q(8,9))
    assert 2*a == 2-Q(3,2)*theta
    assert 2-4*a == 3*theta-2
    # Exact integer powers avoid floating-point admissibility checks.
    p,q = theta.numerator,theta.denominator
    n=8
    X=2**(1+q*n)
    cutoff=2**(p*n)  # (X/2)^theta, exactly
    h=cutoff//K
    assert h>=1 and K*h<=cutoff<=X//2
    assert 2*K*h>=cutoff
    assert all(1<=m*h<=cutoff for m in range(1,K+1))
    rows.append(dict(theta=str(theta),a=str(a),K=K,nu=str(nu),main_exponent=str(first),remainder_exponent=str(second)))
out['parameters'] = rows
out['threshold'] = str((1-Q(1,3))/Q(3,4))

for a in (Q(251,1000),Q(13,50),Q(3,10),Q(333,1000)):
    L,U=2*a,2-4*a
    T=lambda b: 1-b/2
    assert T(U)==L
    assert U-T(L)==1-3*a>0
    assert L<Q(2,3)<U
    for r in (Q(1,1000),Q(1,4),Q(1,2),Q(3,4),Q(999,1000)):
        beta=L+r*(U-L)
        gamma=Q(17)
        b,g=beta,gamma
        for n in range(40):
            assert L<b<U
            assert b==Q(2,3)+(-Q(1,2))**n*(beta-Q(2,3))
            assert g==gamma/2**n
            b,g=T(b),g/2
out['invariant_strip'] = 'exact endpoint and 40-step orbit checks passed'

for beta in (Q(501,1000),Q(3,5),Q(2,3),Q(4,5),Q(999,1000)):
    threshold=max((4-2*beta)/3,(beta+2)/3)
    theta=(threshold+1)/2
    assert Q(8,9)<=threshold<theta<1
    assert 2-Q(3,2)*theta<beta<3*theta-2
out['RH_choice'] = 'theta > max((4-2 beta)/3,(beta+2)/3), always possible for 1/2<beta<1'

for theta in (Q(2,3),Q(8,9),Q(9,10),Q(99,100)):
    a=1-Q(3,4)*theta
    assert a<=Q(1,2)
    assert 2*a-2==-Q(3,2)*theta
out['sharpness'] = 'E(x)=x^a_theta meets abstract nu=0 variance for theta>=2/3 and has a Mellin pole at a_theta'

# Symbolic Fourier-antiderivative coefficients for x*sin^2(2*pi*x).
# For k=4*pi, differentiate a*x^2 + b*x*sin(k*x)/k + c*cos(k*x)/k^2.
a,b,c = Q(1,4),-Q(1,2),-Q(1,2)
assert 2*a==Q(1,2) and b==-Q(1,2) and b-c==0
# At integer endpoints sin(k*x)=0 and cos(k*x)=1, so the cosine terms cancel.
assert a*(Q(2)**2-Q(1)**2)==Q(3,4)
out['analytic_only_L2_countercheck'] = 'Fourier antiderivative verified: integral_X^(2X) x*sin^2(2*pi*x) dx = 3X^2/4 for integer X'

Path(__file__).with_name('verified_arithmetic.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
