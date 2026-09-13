#!/usr/bin/env python3
"""Exact algebra/exponent sanity checks; not an analytic moment verifier."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
import hashlib, json
ROOT = Path(__file__).resolve().parent

def conv(a,b,N):
    out=[0]*(N+1)
    for n in range(1,N+1):
        if a[n]:
            for m in range(1,N//n+1):
                if b[m]: out[n*m]+=a[n]*b[m]
    return out

def mobius(N):
    out=[0]*(N+1); out[1]=1
    for n in range(2,N+1):
        out[n]=-sum(out[d] for d in range(1,n) if n%d==0)
    return out

def identity(U,k,N):
    mu=mobius(N); A=[mu[n] if n<=U else 0 for n in range(N+1)]
    one=[0]+[1]*N; unit=[0]*(N+1); unit[1]=1
    rhs=[0]*(N+1); Apow=unit; Zpow=unit
    for j in range(1,k+1):
        Apow=conv(Apow,A,N)
        if j>1: Zpow=conv(Zpow,one,N)
        term=conv(Apow,Zpow,N)
        for n in range(1,N+1): rhs[n]+=(-1)**(j-1)*comb(k,j)*term[n]
    B=conv(one,A,N); B=[unit[n]-B[n] for n in range(N+1)]
    Bpow=unit
    for _ in range(k): Bpow=conv(Bpow,B,N)
    remainder=conv(mu,Bpow,N)
    assert all(rhs[n]+remainder[n]==mu[n] for n in range(1,N+1))
    return mu,rhs,remainder

finite=[]
for U in range(2,6):
    for k in range(1,5):
        N=U**k
        mu,rhs,rem=identity(U,k,N)
        assert rhs==mu and all(v==0 for v in rem)
        finite.append({'U':U,'k':k,'checked_through':N,'pass':True})
mu,rhs,rem=identity(2,2,9)
assert rhs[9]!=mu[9] and rhs[9]+rem[9]==mu[9]
negative={'U':2,'k':2,'n':9,'mu':mu[9],'truncated_rhs':rhs[9],'remainder':rem[9], 'insufficient_cutoff_rejected': True}

d=F(5,6); eta=F(1,120); c=F(7,12)+eta; r=d-c; ell=1-c; product=r+ell
assert r==F(1,4)-eta
assert ell==F(5,12)-eta
assert product==F(2,3)-2*eta
# I <= T^(-1/2) (T+P^2)^(1/2) L/R.
short_dual=ell-r
long_dual=-F(1,2)+product+ell-r
assert short_dual==1-d and long_dual==F(3,2)-2*c
assert long_dual==F(1,3)-2*eta
assert max(short_dual,long_dual)+eta==F(1,3)-eta
# The exact Type II regrouping lemma depends only on a maximum size.
max_factor=F(7,12)+eta
assert d/3>=F(1,4)-eta
assert d-max_factor==F(1,4)-eta
assert d/2==F(5,12)
# Baseline and the critical level-set calculation.
baseline=[1-d,F(1,3),F(1,2)-d/5,1-4*d/5]
assert baseline==[F(1,6),F(1,3),F(1,3),F(1,3)]
v=-d/4
R=max(-2*v,-2*d/5-4*v,1-8*d/5-4*v)
assert R==F(1,2)
mixed=2*v+(1+R)/2
assert mixed==F(1,3)
# Positive loss controls: the Type I bound has no saving at c=7/12,
# and spending the full 2 eta saving must fail a strict-saving test.
assert F(3,2)-2*F(7,12)==F(1,3)
assert not (long_dual+2*eta<F(1,3))
# Fixed-size support and physical/mixed frequencies must not be confused.
assert 2*d==F(5,3)
assert F(1,2)+2*d==F(13,6)
assert F(1,3)+d==F(7,6)
# Variance-neighborhood path at the maximal formal small-divisor cutoff.
h0=F(4,7); h1=h0+F(1,1000)
def corner(h):
    a=1-h/2
    dt=(a/2)/(1-h)
    ht=h/(1-h)
    assert ht==4*dt-2
    return {'h_X':h,'a_X':a,'d_T':dt,'h_T':ht,'required_moment_exponent':1-ht/2}
assert corner(h0)['d_T']==d
assert corner(h0)['h_T']==F(4,3)
assert corner(h1)['d_T']>d
assert corner(h1)['required_moment_exponent']<F(1,3)

results={
 'scope':'Exact finite identity and rational exponent checks only; no numerical zeta experiment and no proof of a missing joint moment.',
 'identity_cases':finite,'identity_case_count':len(finite),
 'coefficient_checks':sum(row['checked_through'] for row in finite),
 'negative_cutoff_control':negative,
 'critical':{'d':d,'k2_U':d/2,'k3_U':d/3,'baseline_exponents':baseline,'critical_V':v,'critical_measure_exponent':R,'mixed_exponent':mixed},
 'type_I_example':{'eta':eta,'C':c,'R':r,'dual_L':ell,'product_P':product,'raw_exponents':[short_dual,long_dual],'after_aggregate_eta_loss':max(short_dual,long_dual)+eta,'saving':eta},
 'type_II_region':{'short_min':F(1,4)-eta,'short_max':d/2,'long_max':F(7,12)+eta},
 'lengths':{'standalone_polynomial':d,'ordinary_twist_index':2*d,'with_zeta_AFE':F(1,2)+2*d,'critical_half_normalized_joint_target':d+F(1,3)},
 'neighborhood_corners':[corner(h0),corner(h1)],
 'negative_saving_controls':{'C_at_7_over_12_not_strict':True,'aggregate_loss_2_eta_not_strict':True},
}
manifest=json.loads((ROOT/'source-manifest.json').read_text())
unchanged=[]
external_updates=[]
for row in manifest:
    original=row.get('original')
    if original and not original.startswith('<excluded-cache>/'):
        current=Path(original).read_bytes()
        digest=hashlib.sha256(current).hexdigest()
        if digest==row['sha256']:
            unchanged.append({'original':original,'sha256':digest,'unchanged':True})
        else:
            # Fail closed except for the exact externally observed citation append.
            update=json.loads((ROOT/'external-baseline-update.json').read_text())
            assert original==update['original']
            assert row['sha256']==update['initial_sha256']
            assert digest==update['observed_sha256']
            archived=(ROOT/'sources'/row['file']).read_bytes()
            assert current==archived+update['exact_append'].encode()
            (ROOT/'sources'/update['archive_file']).write_bytes(current)
            external_updates.append(update)
results['supplied_inputs_unchanged']=unchanged
results['externally_updated_inputs']=external_updates
text=json.dumps(results,indent=2,default=str)+'\n'
(ROOT/'checks.json').write_text(text)
print(text)
print('PASS: exact identities, rational ledger, fail-closed controls, and supplied-file hashes.')
