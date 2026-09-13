from fractions import Fraction as F
from math import prod
from pathlib import Path
import json
from audit import psi
ROOT=Path(__file__).resolve().parent

def rho_r(P,r):
    return prod((1-F(1,p**r) for p in P),start=F(1))

def W_r(P,r,t):
    out=[(1,F(1))]
    for p in P:
        out=[(d,a*(1-F(2,p**r))) for d,a in out]+[(d*p,a) for d,a in out]
    return sum((a*psi(F(t,d**r)) for d,a in out),start=F(0))

def direct_r(P,r,H):
    L=prod(P)**r
    f=[int(all(n%(p**r) for p in P)) for n in range(L)]
    rho=rho_r(P,r)
    k,h=divmod(H,L)
    S=k*sum(f)+sum(f[j%L] for j in range(1,h+1))
    sumsquares=(S-rho*H)**2
    for n in range(1,L):
        S+=f[(n+H)%L]-f[n%L]
        sumsquares+=(S-rho*H)**2
    return sumsquares/L

results=[]
for r in range(2,6):
    count=0; real_count=0
    for P in [(),(2,),(3,),(2,3)]:
        L=prod(P)**r
        for H in sorted({0,1,2,3,7,8,26,L-1,L,L+1,2*L+1}):
            v=W_r(P,r,H)
            assert v==direct_r(P,r,H)
            assert v**r<=F(r,r-1)**r*F(4)**(1-r)*H
            count+=1
        for p in [2,3,5]:
            if p in P: continue
            for i in range(121):
                t=F(i,7); q=p**r; rho=rho_r(P,r)
                v=W_r(P,r,t); vv=W_r(P+(p,),r,t)
                assert vv==(1-F(2,q))*v+W_r(P,r,t/q)
                assert vv/rho_r(P+(p,),r)>=v/rho
                assert vv/rho_r(P+(p,),r)**2>=v/rho**2
                assert vv**r<=F(r,r-1)**r*F(4)**(1-r)*t
                h=t.numerator//t.denominator; th=t-h
                assert v==(1-th)*W_r(P,r,h)+th*W_r(P,r,h+1)+rho**2*psi(th)
                real_count+=1
    results.append({'r':r,'direct_checks':count,'real_checks':real_count,'bound_constant_power_r':str(F(r,r-1)**r*F(4)**(1-r))})
out={'results':results,'r3_raw_decrease':{'P':[3],'Q':[2,3],'H':8,'old':str(W_r((3,),3,8)),'new':str(W_r((2,3),3,8))}}
(ROOT/'r-free-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
