from fractions import Fraction as F
from itertools import combinations
from math import prod
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def rho(P):
    return prod((1-F(1,p*p) for p in P), start=F(1))

def terms(P):
    out=[(1,F(1))]
    for p in P:
        out=[(d,a*(1-F(2,p*p))) for d,a in out]+[(d*p,a) for d,a in out]
    return out

def psi(t):
    r=t-t.numerator//t.denominator
    return r*(1-r)

def W(P,t):
    return sum((a*psi(F(t,d*d)) for d,a in terms(P)),start=F(0))

def direct(P,H):
    L=prod(P)**2
    f=[int(all(n%(p*p) for p in P)) for n in range(L)]
    r=rho(P)
    S=sum(f[j%L] for j in range(1,H+1))
    s2=(S-r*H)**2
    for n in range(1,L):
        S+=f[(n+H)%L]-f[n%L]
        s2+=(S-r*H)**2
    return s2/L

def main():
    checks=0
    for P in [(),(2,),(3,),(2,3),(3,5),(2,3,5)]:
        L=prod(P)**2
        for H in sorted(set(range(min(L+2,60)))|{L,L+1,2*L-1,2*L,2*L+1}):
            assert W(P,H)==direct(P,H),(P,H,W(P,H),direct(P,H))
            assert W(P,H)**2<=H
            checks+=1
    recurrence_checks=0
    for P in [(),(2,),(3,),(2,3),(3,5)]:
        for p in (2,3,5,7):
            if p in P: continue
            for i in range(601):
                t=F(i,7)
                old=W(P,t); new=W(P+(p,),t)
                assert new==(1-F(2,p*p))*old+W(P,t/(p*p))
                assert new/rho(P+(p,))**2>=old/rho(P)**2
                assert new/rho(P+(p,))>=old/rho(P)
                assert new*new<=t
                h=i//7; theta=t-h
                assert old==(1-theta)*W(P,h)+theta*W(P,h+1)+rho(P)**2*theta*(1-theta)
                recurrence_checks+=1
    decreases=[]
    primes=(2,3,5,7)
    for k in range(1,4):
        for P in combinations(primes,k):
            for p in primes:
                if p in P: continue
                for H in range(1,min(10000,(prod(P)*p)**2)):
                    old=W(P,H); new=W(P+(p,),H)
                    if new<old:
                        decreases.append({'P':P,'p_added':p,'H':H,'old':str(old),'new':str(new)})
                        break
    result={'direct_exact_checks':checks,'real_recurrence_and_monotonicity_checks':recurrence_checks,'raw_variance_decreases':decreases}
    (ROOT/'audit-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
