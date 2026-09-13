from fractions import Fraction as F
from itertools import combinations
from math import prod, gcd, lcm
from pathlib import Path
import json
from audit import rho, W, psi

ROOT = Path(__file__).resolve().parent

def signed_divisors(P):
    ds=[(1,1)]
    for p in P:
        ds+= [(d*p,-s) for d,s in list(ds)]
    return ds

def count_residue(A,X,q,r):
    return (A+X-1-r)//q-(A-1-r)//q

def indicator(P,n):
    return int(all(n%(p*p) for p in P))

def crt_pair(d,e,i,j):
    a,b=d*d,e*e; g=gcd(a,b)
    if (i-j)%g: return None
    q=lcm(a,b)
    k=0 if b//g==1 else (((i-j)//g)*pow(a//g,-1,b//g))%(b//g)
    return q,(-i+a*k)%q

def finite_variance(P,A,X,H):
    return sum((sum(indicator(P,n+j) for j in range(1,H+1))-rho(P)*H)**2 for n in range(A,A+X))/X

def floor_discrepancy(P,A,X,H):
    ds=signed_divisors(P)
    single=F(0); pair=F(0)
    for i in range(1,H+1):
        for d,mu in ds:
            single+=mu*(count_residue(A,X,d*d,-i)-F(X,d*d))
        for j in range(1,H+1):
            for d,mu in ds:
                for e,nu in ds:
                    solution=crt_pair(d,e,i,j)
                    if solution is not None:
                        q,r=solution
                        pair+=mu*nu*(count_residue(A,X,q,r)-F(X,q))
    return (pair-2*rho(P)*H*single)/X

def main():
    floor_checks=0; real_phase_checks=0; martingale_fibers=0
    for P in [(),(2,),(3,),(2,3)]:
        for A,X in [(1,1),(1,2),(3,7),(9,12),(33,4),(50,37)]:
            for H in [0,1,3,4,7,12]:
                b=finite_variance(P,A,X,H)
                err=floor_discrepancy(P,A,X,H)
                assert b-W(P,H)==err,(P,A,X,H)
                k=len(P); L=prod(P)**2; r=X%L
                assert abs(err)<=F(H*H*r,X)
                assert abs(err)<=F(H*H*(4**k+2*rho(P)*2**k),X)
                floor_checks+=1
                for theta in [F(1,3),F(1,2)]:
                    t=H+theta
                    direct=sum((1-theta)*(sum(indicator(P,n+j) for j in range(1,H+1))-rho(P)*t)**2+theta*(sum(indicator(P,n+j) for j in range(1,H+2))-rho(P)*t)**2 for n in range(A,A+X))/X
                    endpoint=F(sum(indicator(P,n+H+1) for n in range(A,A+X)),X)
                    mixed=(1-theta)*b+theta*finite_variance(P,A,X,H+1)+rho(P)**2*psi(theta)+2*rho(P)*psi(theta)*(endpoint-rho(P))
                    assert direct==mixed
                    real_phase_checks+=1
        for p in [2,3,5]:
            if p in P: continue
            Q=P+(p,); L=prod(P)**2
            for H in [1,3,7,12]:
                for n in range(L):
                    old=F(sum(indicator(P,n+j) for j in range(1,H+1)))/rho(P)-H
                    new_avg=sum(F(sum(indicator(Q,n+r*L+j) for j in range(1,H+1)))/rho(Q)-H for r in range(p*p))/(p*p)
                    assert old==new_avg
                    martingale_fibers+=1
    result={'floor_discrepancy_checks':floor_checks,'finite_real_phase_endpoint_checks':real_phase_checks,'conditional_martingale_fibers':martingale_fibers,'finite_X_normalized_counterexample':{'A':1,'X':2,'H':3,'P':[3],'Q':[2,3],'P_value':str(finite_variance((3,),1,2,3)/rho((3,))**2),'Q_value':str(finite_variance((2,3),1,2,3)/rho((2,3))**2)}}
    (ROOT/'endpoint-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
