"""Solver-free exact Farkas certificate for a q=6 117-cell subledger.

Potential class (independent slopes in every cell):
  H(x)=2||x||^2 + (h[cell(x)] + sum_j p[cell(x),j] r_j(x))/36.
There is one deterministic base-cost closure row per compatible cell triple
(98,167 rows), not an all-vertex continuous closure enumeration.  The two
selected rows are necessary closure inequalities.  Scalar closed faces are
one-sided closures of half-open cells r in [0,1)^4; affine validity inside a
fixed cell implies validity on that closure.
"""
from fractions import Fraction as F
from itertools import product
from hashlib import sha256

Q=6
S0=((3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2))
D=((0,4),(1,4),(1,5),(2,1),(2,3),(3,5),(4,0),(4,4),(4,5),(5,0),(5,1),(5,2),(5,3))
U=tuple((a,b,(a+da)%Q,(b+db)%Q) for a,b in S0 for da,db in D)
RAY_IDS=(89333,89473)
WEIGHTS=(1,1) # doubles the normalized direct-dual weights (1/2,1/2)

def vertices(a,b,c):
    """Exact scalar closure vertices, in the source's deterministic order."""
    ans=[]; d=a+c-2*b
    for k in (-1,0,1):
        e=Q*k-d
        if e not in (-1,0,1): continue
        for i,j in ((0,1),(0,2),(1,2)):
            for vi in (F(0),F(1)):
                for vj in (F(0),F(1)):
                    v=[None,None,None]; v[i]=vi; v[j]=vj
                    f=next(n for n in range(3) if n not in (i,j))
                    co=(1,1,-2)
                    v[f]=(F(e)-co[i]*v[i]-co[j]*v[j])/co[f]
                    if F(0)<=v[f]<=F(1):
                        cost=-2*Q*k*(F(a+c,2)+b+2*v[2]+F(e,2))
                        ans.append((tuple(v),k,e,cost))
    return tuple(ans)

def row(x,y,z):
    choice=[]
    for j in range(4):
        vs=T[U[x][j]][U[y][j]][U[z][j]]
        if not vs: return None
        # JS reduce(a,b => a.c>=b.c?a:b): first maximum in enumeration order.
        choice.append(max(vs,key=lambda v:v[3]))
    return (x,y,z,tuple(choice),sum(v[3] for v in choice))

T=tuple(tuple(tuple(vertices(a,b,c) for c in range(Q)) for b in range(Q)) for a in range(Q))
ledger=[]
for x,y,z in product(range(len(U)),repeat=3):
    r=row(x,y,z)
    if r is not None: ledger.append(r)
assert len(U)==117 and len(ledger)==98167

selected=[ledger[i] for i in RAY_IDS]
assert tuple((r[0],r[1],r[2]) for r in selected)==((105,91,91),(105,105,91))
assert tuple(r[4] for r in selected)==(F(216),F(-72))
expected_choices=(
    (((0,0,0),0,0,0),((0,0,F(1,2)),0,-1,0),((0,1,1),-1,-1,108),((0,1,1),-1,-1,108)),
    (((0,0,0),0,0,0),((0,1,0),0,1,0),((0,1,0),1,1,-36),((0,1,0),1,1,-36)),
)
assert tuple(tuple((v,k,e,c) for v,k,e,c in r[3]) for r in selected)==expected_choices

def validate_choice_geometry(x,y,z,choice):
    """Validate residual range, carry equation, residual equation, and cost."""
    for j,(v,k,e,cost) in enumerate(choice):
        rx,rz,ry=v; a,b,c=U[x][j],U[y][j],U[z][j]
        assert all(F(0)<=r<=F(1) for r in v), (x,y,z,j,v)
        assert a+c-2*b+e==Q*k, (x,y,z,j,a,b,c,k,e)
        assert rx+rz-2*ry==e, (x,y,z,j,v,e)
        assert cost==-2*Q*k*(F(a+c,2)+b+2*ry+F(e,2)), (x,y,z,j,v,k,e,cost)
        assert (v,k,e,cost) in T[a][b][c], (x,y,z,j,v,k,e,cost)

for x,y,z,choice,cost in selected:
    validate_choice_geometry(x,y,z,choice)

def incidence(rows,weights):
    """Return the exact coefficients of all 585 free h,p features and RHS."""
    out={('h',cell):F(0) for cell in range(117)}
    out.update({('p',cell,j):F(0) for cell in range(117) for j in range(4)})
    rhs=F(0)
    for w,(x,y,z,choice,c) in zip(weights,rows):
        for cell,coef in ((x,1),(y,-2),(z,1)): out[('h',cell)]+=w*coef
        for j,(v,k,e,cost) in enumerate(choice):
            out[('p',x,j)]+=w*v[0]
            out[('p',z,j)]+=w*v[1]
            out[('p',y,j)]-=2*w*v[2]
        rhs+=w*c
    return out,rhs

coef,rhs=incidence(selected,WEIGHTS)
assert len(coef)==585
assert all(v==0 for v in coef.values()),[(k,v) for k,v in coef.items() if v]
assert rhs==144

# Planted failures: omit one positive row (coefficient cancellation) and
# alter a residual while retaining carry/cost (semantic geometry rejection).
one,_=incidence((selected[0],),(1,))
assert any(v for v in one.values())
bad=list(selected[1][3]); v,k,e,cost=bad[1]; bad[1]=((F(0),F(0),F(0)),k,e,cost)
altered=(selected[1][0],selected[1][1],selected[1][2],tuple(bad),selected[1][4])
try:
    validate_choice_geometry(altered[0],altered[1],altered[2],altered[3])
except AssertionError:
    pass
else:
    raise AssertionError('planted invalid residual passed semantic geometry validation')

payload='\n'.join(
    f'{x},{y},{z},'+','.join(f'{v[0]}/{v[1]}/{v[2]}|{v[1+1]}|{v[2+1]}|{v[3]}' for v in ch)+f',{rhs}'
    for x,y,z,ch,rhs in ledger).encode()
print('PASS_PERCELL_AFFINE_FARKAS')
print({'cells':117,'ledger_rows':len(ledger),'ray_rows':2,'weights':WEIGHTS,
       'row_ids':RAY_IDS,'weighted_rhs':rhs,'features_cancelled':len(coef),
       'ledger_sha256':sha256(payload).hexdigest(),
       'planted_missing_row_rejected':True,'planted_semantic_residual_rejected':True,
       'scope':'two necessary rows of the deterministic per-cell residual-affine base-cost closure subledger'})
