"""Independent, compact exact check of the two-row q=6 per-cell ray.

This does not enumerate the subledger or import the replay script.  It checks
the raw cell/carry/residual data used by the two selected necessary closure
rows.  It makes no inference about arbitrary physical potentials.
"""
from fractions import Fraction as F

Q=6
S0=((3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2))
D=((0,4),(1,4),(1,5),(2,1),(2,3),(3,5),(4,0),(4,4),(4,5),(5,0),(5,1),(5,2),(5,3))
U=tuple((a,b,(a+da)%Q,(b+db)%Q) for a,b in S0 for da,db in D)

# (triple, ((rx,rz,ry), carry k, error e) for its four coordinates)
RAYS=(
 ((105,91,91), (((0,0,0),0,0),((0,0,F(1,2)),0,-1),((0,1,1),-1,-1),((0,1,1),-1,-1))),
 ((105,105,91), (((0,0,0),0,0),((0,1,0),0,1),((0,1,0),1,1),((0,1,0),1,1))),
)

def feature_sum():
    inc={('h',i):F(0) for i in range(117)}
    inc.update({('p',i,j):F(0) for i in range(117) for j in range(4)})
    total=F(0)
    for (x,y,z),coords in RAYS:
        for i,m in ((x,1),(y,-2),(z,1)): inc[('h',i)]+=m
        rhs=F(0)
        for j,((rx,rz,ry),k,e) in enumerate(coords):
            a,b,c=U[x][j],U[y][j],U[z][j]
            assert a+c-2*b+e==Q*k, (x,y,z,j,a,b,c,k,e)
            assert rx+rz-2*ry==e, (x,y,z,j,rx,rz,ry,e)
            assert all(F(0)<=r<=F(1) for r in (rx,rz,ry))
            cost=-2*Q*k*(F(a+c,2)+b+2*ry+F(e,2))
            inc[('p',x,j)]+=rx; inc[('p',z,j)]+=rz; inc[('p',y,j)]-=2*ry
            rhs+=cost
        total+=rhs
    return inc,total

inc,total=feature_sum()
assert all(v==0 for v in inc.values())
assert total==144
assert any(r==1 for _,coords in RAYS for ((rx,rz,ry),_,_) in coords for r in (rx,rz,ry))
print('PASS_INDEPENDENT_PERCELL_AFFINE_CROSSCHECK')
print({'rows':2,'cell_triples':tuple(t for t,_ in RAYS),'all_585_features_cancel':True,
       'weighted_rhs':total,'closure_faces_used':True,
       'half_open_justification':'affine inequalities extend by one-sided continuity',
       'scope_fence':'no inference about arbitrary physical potentials'})
