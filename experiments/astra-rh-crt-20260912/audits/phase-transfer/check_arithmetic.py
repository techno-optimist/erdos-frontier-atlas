from fractions import Fraction as F
from itertools import combinations
from functools import lru_cache
from math import prod, floor, ceil
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1] / 'inputs'
OUT = Path(__file__).resolve().parent
records = []

def subsets(seq):
    return [tuple(c) for k in range(len(seq)+1) for c in combinations(seq, k)]

@lru_cache(None)
def pattern(P, r=2):
    L = prod(p**r for p in P)
    pref = [0]
    for n in range(1, L+1):
        pref.append(pref[-1] + int(all(n % p**r for p in P)))
    return L, tuple(pref), prod((1-F(1,p**r) for p in P), start=F(1))

def count(P, r, x, H):
    L, pref, _ = pattern(P,r)
    def ps(n):
        q,t = divmod(n,L)
        return q*pref[L]+pref[t]
    return ps(floor(x+H))-ps(floor(x))

def segments(a,b,H):
    cuts={a,b}
    for k in range(floor(a)-1,ceil(b)+2):
        if a < k < b:
            cuts.add(F(k))
    for k in range(floor(a+H)-1,ceil(b+H)+2):
        z=F(k)-H
        if a < z < b:
            cuts.add(z)
    cuts=sorted(cuts)
    return [(v-u,(v+u)/2) for u,v in zip(cuts,cuts[1:])]

def moments(P,r,H,a=F(0),X=None):
    L,_,rho=pattern(P,r)
    if X is None:
        X=F(L)
    e1=e2=F(0)
    for length,x in segments(a,a+X,H):
        n=count(P,r,x,H)
        e1+=length*n
        e2+=length*(n-rho*H)**2
    return e1/X,e2/X

@lru_cache(None)
def variance(P,r,H):
    return moments(P,r,H)[1]

def psi(x):
    a=x-floor(x)
    return a*(1-a)

def formula(P,r,H):
    ans=F(0)
    for D in subsets(P):
        d=prod(D)
        w=prod((1-F(2,p**r) for p in P if p not in D),start=F(1))
        ans+=w*psi(H/d**r)
    return ans

def note(kind,**kwargs):
    records.append(dict(kind=kind,**kwargs))

def Hs(L):
    return sorted(set(map(F,[0,1,3,4,9,25])) | {F(1,7),F(1,2),F(3,2),F(7,3),F(15,4),F(23,5),F(19,2),F(101,3),F(L)-F(1,3),F(L),F(L)+F(1,3),F(2*L)+F(3,4)})

# Direct rational piecewise integration, independent of divisor expansion.
for r, base in [(2,(2,3,5)),(3,(2,3)),(4,(2,3)),(5,(2,))]:
    for P in subsets(base):
        L,_,rho=pattern(P,r)
        for H in Hs(L):
            mean,actual=moments(P,r,H)
            expected=formula(P,r,H)
            assert mean==rho*H,(r,P,H,'mean',mean,rho*H)
            assert actual==expected,(r,P,H,'formula',actual,expected)
            m=floor(H); alpha=H-m
            interpolated=(1-alpha)*variance(P,r,F(m))+alpha*variance(P,r,F(m+1))+rho*rho*alpha*(1-alpha)
            assert actual==interpolated,(r,P,H,'interpolation')
            bound_to_r=F(r,r-1)**r * F(4)**(1-r)*H
            assert actual>=0 and actual**r<=bound_to_r,(r,P,H,'uniform_bound')
            note('direct_phase',r=r,P=P,H=str(H),variance=str(actual))

# Conditional expectation on k mod L_P AND the retained fractional phase.
# Compute each conditional fiber explicitly rather than invoking independence.
for Q in [(),(2,),(2,3),(2,3,5)]:
    Lq,_,rhoq=pattern(Q)
    for P in subsets(Q):
        Lp,_,rhop=pattern(P)
        for H in map(F,[0,1,3,F(1,2),F(7,3),F(19,2)]):
            alpha=H-floor(H)
            phase_segments=[(F(1),F(1,2))] if not alpha else [(1-alpha,(1-alpha)/2),(alpha,1-alpha/2)]
            cross=inc=defect=F(0)
            for weight,u in phase_segments:
                for k in range(Lp):
                    cp=F(count(P,2,F(k)+u,H))-rhop*H
                    sp=cp/rhop
                    conditional=F(0)
                    for j in range(Lq//Lp):
                        x=F(k+j*Lp)+u
                        cq=F(count(Q,2,x,H))-rhoq*H
                        sq=cq/rhoq
                        conditional+=sq/F(Lq//Lp)
                        cross+=weight*cp*cq/Lq
                        inc+=weight*(sq-sp)**2/Lq
                        defect+=weight*(cp-cq)**2/Lq
                    assert conditional==sp,(Q,P,H,k,u,'conditional',conditional,sp)
                    note('conditional_fiber',Q=Q,P=P,H=str(H),k=k,u=str(u))
            vp=variance(P,2,H); vq=variance(Q,2,H)
            assert cross==rhoq/rhop*vp,(Q,P,H,'cross')
            assert inc==vq/rhoq**2-vp/rhop**2 and inc>=0,(Q,P,H,'normalized_increment')
            assert defect==vq+(1-2*rhoq/rhop)*vp,(Q,P,H,'unnormalized_defect')
            assert 0<=defect<=vq and defect*defect<=H,(Q,P,H,'defect_bound')
            note('refinement_and_defect',Q=Q,P=P,H=str(H),increment=str(inc),defect=str(defect))

# Arbitrary starts, negative starts, real lengths, exact multiples and residuals.
for P in [(),(2,),(2,3),(2,3,5)]:
    L,_,_=pattern(P)
    for H in [F(0),F(1,3),F(1),F(7,3),F(L)+F(1,2)]:
        v=variance(P,2,H)
        for a in [F(-7,3),F(0),F(1,7),F(L)-F(1,5)]:
            for X in sorted({F(1,7),F(L)-F(1,3),F(L),F(L)+F(1,3),F(2*L),F(5*L,2)}):
                empirical=moments(P,2,H,a,X)[1]
                cost=F(L*ceil(X/L),1)/X
                assert empirical<=cost*v,(P,H,a,X,'period_cost')
                if L<=X:
                    assert cost<2 or cost==1,(P,H,a,X,'cost_le_two')
                note('arbitrary_interval',P=P,H=str(H),a=str(a),X=str(X),cost=str(cost))

# Exact periodic-prime norm-transfer tests using rational surrogate densities.
# The reverse triangle inequality itself does not require that the target be periodic.
for P,Q in [((),(2,)),((2,),(2,3)),((2,3),(2,3,5))]:
    Lp,_,rhop=pattern(P); _,_,rhoq=pattern(Q)
    for X in [F(1,5),F(5,2),F(Lp),F(Lp)+F(1,3)]:
        for H in [F(0),F(1,3),F(1),F(7,3),F(11)]:
            a=X; true=defect=filtered=F(0)
            for length,x in segments(a,a+X,H):
                c=F(count(P,2,x,H))-rhop*H
                e=F(count(Q,2,x,H))-rhoq*H
                d=c-e
                true+=length*e*e/X
                defect+=length*d*d/X
                filtered+=length*c*c/X
            B=F(Lp*ceil(X/Lp),1)/X*variance(P,2,H)
            assert filtered<=B
            # |sqrt(true)-sqrt(defect)| <= sqrt(B), without floating roots.
            excess=true+defect-B
            assert excess<=0 or excess*excess<=4*true*defect,(P,Q,X,H,'norm_transfer')
            note('norm_transfer_exact',P=P,Q=Q,X=str(X),H=str(H))

# Negative controls for invalid shortcuts (not counterexamples to RESULT.md).
P=(); H=F(1,2)
negative_controls={
    'floor_only_noninteger':{'correct':str(variance(P,2,H)),'incorrect_floor_only':str(variance(P,2,F(0)))},
    'drop_fractional_conditioning':{'P':[],'Q':[2],'H':'1/2','u':'1/4','S_P':str(F(count(P,2,F(1,4),H))-H),'conditional_on_integer_phase_only':'0'},
}
assert variance(P,2,H)!=variance(P,2,F(0))
negative_controls['unnormalized_variance_difference']={
    'P':[2],'Q':[2,3],'H':'1','correct':str(variance((2,3),2,F(1))+(1-2*pattern((2,3))[2]/pattern((2,))[2])*variance((2,),2,F(1))),
    'incorrect_VQ_minus_VP':str(variance((2,3),2,F(1))-variance((2,),2,F(1)))
}
assert negative_controls['unnormalized_variance_difference']['correct']!=negative_controls['unnormalized_variance_difference']['incorrect_VQ_minus_VP']
a=F(547); P=(2,3,5); H=F(3); rho=pattern(P)[2]
spike=(count(P,2,a,H)-rho*H)**2
assert spike==F(2304,625) and spike*spike>H
negative_controls['pointwise_phase_bound']={'P':P,'x':str(a),'H':str(H),'squared_error':str(spike),'exceeds_sqrt_H':spike*spike>H}
negative_controls['remove_periodicity_cost']={'P':[2],'H':'1','interval':['3','7/2'],'energy':str(moments((2,),2,F(1),F(3),F(1,2))[1]),'phase_variance':str(variance((2,),2,F(1)))}
assert moments((2,),2,F(1),F(3),F(1,2))[1]>variance((2,),2,F(1))

counts={k:sum(1 for t in records if t['kind']==k) for k in sorted({t['kind'] for t in records})}
summary={'passed':True,'counts':counts,'total_records':len(records),'negative_controls':negative_controls,'input_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['RESULT.md','MELLIN_TRANSFER.md']}}
(OUT/'check_records.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'check_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
