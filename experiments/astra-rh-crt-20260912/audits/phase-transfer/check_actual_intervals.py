from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import combinations
from math import floor,ceil,prod,isqrt
from pathlib import Path
import json,hashlib

OUT=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[1] / 'inputs'

def dec(f):
    f=F(f)
    return Decimal(f.numerator)/Decimal(f.denominator)

def atan(z):
    z2=z*z; a=z; s=z; k=1
    while True:
        a=-a*z2
        term=a/Decimal(2*k+1)
        s+=term
        if abs(term)<Decimal('1e-78'):return s
        k+=1

def phase_formula(P,H):
    out=F(0)
    for k in range(len(P)+1):
        for D in combinations(P,k):
            d=prod(D)
            a=H/(d*d); a-=floor(a)
            w=prod((1-F(2,p*p) for p in P if p not in D),start=F(1))
            out+=w*a*(1-a)
    return out

def counts(P,N):
    sf=[1]*(N+1); sf[0]=0
    fp=[1]*(N+1); fp[0]=0
    for d in range(2,isqrt(N)+1):
        for n in range(d*d,N+1,d*d):sf[n]=0
    for p in P:
        for n in range(p*p,N+1,p*p):fp[n]=0
    for n in range(1,N+1):sf[n]+=sf[n-1];fp[n]+=fp[n-1]
    return fp,sf

records=[]
with localcontext() as ctx:
    ctx.prec=70
    pi=16*atan(Decimal(1)/5)-4*atan(Decimal(1)/239)
    rho=6/(pi*pi)
    for P in [(),(2,),(2,3),(2,3,5)]:
        L=prod(p*p for p in P)
        rp=prod((1-F(1,p*p) for p in P),start=F(1))
        for X in [F(1,10),F(1,2),F(1),F(7,3),F(4),F(13,2),F(25),F(36),F(37),F(900),F(2701,3)]:
            for H in sorted({F(0),F(1,3),F(1),F(7,3),F(4),F(25),F(37,2),F(L)+F(1,3),F(2*L)}):
                fp,sf=counts(P,ceil(2*X+H)+1)
                cuts={X,2*X}
                for n in range(floor(X),ceil(2*X)+1):
                    if X<n<2*X:cuts.add(F(n))
                for n in range(floor(X+H),ceil(2*X+H)+1):
                    y=F(n)-H
                    if X<y<2*X:cuts.add(y)
                vv=dd=cc=Decimal(0)
                cuts=sorted(cuts)
                for u,v in zip(cuts,cuts[1:]):
                    x=(u+v)/2
                    lo,hi=floor(x),floor(x+H)
                    filt=Decimal(fp[hi]-fp[lo])-dec(rp*H)
                    true=Decimal(sf[hi]-sf[lo])-rho*dec(H)
                    defect=Decimal(fp[hi]-fp[lo]-sf[hi]+sf[lo])-(dec(rp)-rho)*dec(H)
                    assert abs(filt-defect-true)<Decimal('1e-60')
                    wt=dec((v-u)/X)
                    vv+=wt*true*true;dd+=wt*defect*defect;cc+=wt*filt*filt
                B=dec(F(L*ceil(X/L),1)/X * phase_formula(P,H))
                gap=abs(vv.sqrt()-dd.sqrt())
                tol=Decimal('1e-55')
                assert cc<=B+tol,(P,X,H,'periodic_bound')
                assert gap<=B.sqrt()+tol,(P,X,H,'norm_transfer')
                if L<=X:
                    assert gap<=Decimal(2).sqrt()*dec(H).sqrt().sqrt()+tol,(P,X,H,'local_deflation')
                    assert dd<=2*vv+4*dec(H).sqrt()+tol,(P,X,H,'energy_direction_D')
                    assert vv<=2*dd+4*dec(H).sqrt()+tol,(P,X,H,'energy_direction_V')
                records.append({'P':P,'X':str(X),'H':str(H),'period_at_most_X':L<=X,'norm_gap':str(gap),'bound':str(B.sqrt())})
    numeric={'rho':str(rho),'precision':ctx.prec,'arithmetic_assertion_tolerance':'1e-55','actual_squarefree_cases':len(records),'cases_L_le_X':sum(t['period_at_most_X'] for t in records)}

# Rational Mellin ledger and both-direction energy absorption coefficients.
ledger=[]
for theta in [F(6,11),F(2,3),F(3,4),F(4,5),F(8,9),F(9,10),F(19,20)]:
    a=1-F(3,4)*theta
    lo,hi=2*a,2-4*a
    ledger.append({'theta':str(theta),'a':str(a),'zero_strip':[str(lo),str(hi)] if F(1,4)<a<F(1,3) else None})
assert F(2)*F(2)==4
summary={'passed':True,'numeric_actual_squarefree_checks':numeric,'mellin_table':ledger,'input_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['RESULT.md','MELLIN_TRANSFER.md']}}
(OUT/'actual_interval_records.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'actual_interval_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
