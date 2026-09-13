"""Exact finite algebra and exponent checks; not a proof of moments."""
from fractions import Fraction as F
from pathlib import Path
from collections import Counter
from math import gcd
import json
ROOT=Path(__file__).resolve().parent

def mobius(nmax):
    mu=[1]*(nmax+1); primes=[]; composite=[False]*(nmax+1)
    mu[0]=0
    for n in range(2,nmax+1):
        if not composite[n]: primes.append(n); mu[n]=-1
        for p in primes:
            if n*p>nmax: break
            composite[n*p]=True
            if n%p==0:
                mu[n*p]=0; break
            mu[n*p]=-mu[n]
    return mu

def jordan2(n):
    out=n*n; m=n; p=2
    while p*p<=m:
        if m%p==0:
            out=out//(p*p)*(p*p-1)
            while m%p==0: m//=p
        p+=1
    if m>1: out=out//(m*m)*(m*m-1)
    return out

checks=[]
for D in [2,3,5,8,12,20,32]:
    mu=mobius(2*D)
    q=sum((F(mu[d]*mu[e]*gcd(d,e)**2,d*d*e*e) for d in range(D,2*D) for e in range(D,2*D)),F(0))
    gram=sum((jordan2(r)*sum((F(mu[d],d*d) for d in range(D,2*D) if d%r==0),F(0))**2 for r in range(1,2*D)),F(0))
    lower=sum((F(mu[r]**2*jordan2(r),r**4) for r in range(D,2*D)),F(0))
    assert q==gram and q>=lower and lower>0
    N=12
    entries=[(n,d) for n in range(1,N+1) for d in range(D,2*D)]
    direct=F(0); param=F(0); count_direct=0; count_param=0
    # On a collision sqrt(n1*n2)=ell*a*b, so every value is rational.
    groups={}
    for n,d in entries: groups.setdefault(n*d*d,[]).append((n,d))
    for values in groups.values():
        for n,d in values:
            for m,e in values:
                count_direct+=1
                g=gcd(d,e); a=d//g; b=e//g; ell=n//(b*b)
                assert n==ell*b*b and m==ell*a*a
                direct+=F(mu[d]*mu[e],g*g*a*a*b*b*ell)
    for d in range(D,2*D):
        for e in range(D,2*D):
            g=gcd(d,e); a=d//g; b=e//g
            for ell in range(1,N//max(a*a,b*b)+1):
                count_param+=1; param+=F(mu[d]*mu[e],g*g*a*a*b*b*ell)
    assert direct==param and count_direct==count_param
    checks.append(dict(D=D,Q_exact=str(q),D_times_Q=float(D*q),Jordan_identity=True,positive_lower_bound=str(lower),collision_count=count_direct,diagonal_parametrization=True))

alpha=F(5,6); n=F(1,2)
ex={
 'D':alpha,'square_index_length':2*alpha,'AFE_n':n,'product_index_length':n+2*alpha,
 'mixed_baseline':F(1,3),
 'GM_term_three':F(1,2)-alpha/5,
 'GM_term_four':1-F(4,5)*alpha,'diagonal':1-alpha,'H_over_T':F(1,3),'variance_baseline':F(2,3),
 'AFE_error':F(-2,3)+max(1-alpha,F(0)),
 'near_gap':n+2*alpha-1,'number_of_entries':n+alpha,
 'unsigned_core_count_lower':2*n+2*alpha-1,'exact_collision_count_upper':n+alpha,
 'kernel_coefficient':1-n-2*alpha,'signed_target_count_before_eta':n+2*alpha-F(2,3),
 'unsigned_majorant_lower':n,'saving_from_unsigned_before_eta':n-F(1,3),
 'signed_count_for_diagonal_scale':n+alpha,
 'BCR1_max_D':F(17,66),'BCR4_max_square_root_index_D':F(1,8),
 'BCR1_formal_error_out_of_range':F(3,20)+F(33,20)*2*alpha,
 'PR_Conrey_formal_error_out_of_range':max(F(7,4)*2*alpha,F(1,2)+F(7,8)*2*alpha),
 'BC_sparsity_only_term1':F(3,20)+F(23,10)*alpha,
 'BC_sparsity_only_term2':F(11,4)*alpha,
 'BCR_product_favorable_length':F(2,5)+F(1,5),
 'Tang_width_needed_individual_main_dominance':(1+2*alpha)/2,
 'BC_poisson_frequency_length':4*alpha-1,
}
assert all(x==1 for x in [F(1,2)+F(3,4)*F(2,5)+F(1,5), F(1,2)+F(2,5)+F(1,2)*F(1,5), F(7,4)*F(2,5)+F(3,2)*F(1,5)])
assert ex['square_index_length']==F(5,3)
assert ex['product_index_length']==F(13,6)
assert ex['diagonal']==F(1,6)
assert ex['AFE_error']==F(-1,2)
assert ex['near_gap']==F(7,6)
assert ex['signed_target_count_before_eta']==F(3,2)
assert ex['saving_from_unsigned_before_eta']==F(1,6)
# An explicit sufficient aggregate loss allocation.
eta=F(1,100); rho=eta/100
assert F(1,6)+rho < F(1,3)-eta
assert F(1,3)-2*eta+rho < F(1,3)-eta
out={'scope':'Exact arithmetic/finite identities only; no numerical evidence for an analytic moment theorem.', 'finite_checks':checks,'critical_exponents':{k:str(v) for k,v in ex.items()},'example_loss_budget':{'eta':str(eta),'aggregate_loss':str(rho),'all_strict':True},'status':'PASS'}
(ROOT/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
