"""Exact q=6 dilation wall for arbitrary bounded physical potentials.

On the fixed 117-cell union, write any candidate as

    H(x)=2||x||^2 + h(x)/36.

For bounded H, the correction h is bounded as well.  No affinity,
continuity, one-sided trace, or piecewise description is assumed.  The two
strict-interior modular midpoint families below force a positive dilation
increment of h at every scale; finite telescoping contradicts boundedness.
"""
from fractions import Fraction as F
from hashlib import sha256

Q=6
S0=((3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2))
D=((0,4),(1,4),(1,5),(2,1),(2,3),(3,5),(4,0),(4,4),(4,5),
   (5,0),(5,1),(5,2),(5,3))
U=tuple((a,b,(a+da)%Q,(b+db)%Q) for a,b in S0 for da,db in D)
A=93; B=91

def family(t,s=F(1,2)):
    """Rows in x,y,z order; all residuals are physical for 0<t<1/3."""
    return (
        # R1 has cells (A,B,B), carry/error (0,0,-1,-1).
        ((A,B,B), ((s,s,t,t), (s,s,1-t,1-t), (s,s,1-3*t,1-3*t)),
         (0,0,-1,-1)),
        # R2 has cells (A,A,B), carry/error (0,0,1,1).
        ((A,A,B), ((s,s,3*t,3*t), (s,s,t,t), (s,s,1-t,1-t)),
         (0,0,1,1)),
    )

def carry_cost(cells,residuals,errors):
    """Reconstruct q^2-scaled raw carry contribution coordinate by coordinate."""
    x,y,z=cells; rx,ry,rz=residuals; costs=[]; carries=[]
    for j,e in enumerate(errors):
        a,b,c=U[x][j],U[y][j],U[z][j]
        assert (a+c-2*b+e) % Q == 0
        k=(a+c-2*b+e)//Q
        assert k in (-1,0,1)
        assert rx[j]+rz[j]-2*ry[j]==e
        costs.append(-2*Q*k*(F(a+c,2)+b+2*ry[j]+F(e,2)))
        carries.append(k)
    return tuple(carries),tuple(costs),sum(costs)

def check_family():
    # All identities are affine in t; two values prove the displayed formulas.
    for s in (F(1,3),F(1,2)):
        for t in (F(1,10),F(1,5)):
            assert 0<t<F(1,3)
            data=family(t,s)
            for cells,residuals,errors in data:
                assert all(F(0)<r<F(1) for v in residuals for r in v)
                carries,costs,total=carry_cost(cells,residuals,errors)
                if cells==(A,B,B):
                    assert carries==(0,0,-1,-1) and total==216-48*t
                else:
                    assert carries==(0,0,1,1) and total==-72-48*t
            assert sum(carry_cost(*r)[2] for r in data)==144-96*t

def finite_telescoping(N,T=F(1,4)):
    """Exact bound obtained by summing t_n=T/3^n, n=1,...,N."""
    assert N>=1 and 0<T<F(1,3)
    ts=tuple(T/F(3**n) for n in range(1,N+1))
    # Each row pair gives D(3t)-D(t) >= 144-96t.
    rhs=sum(144-96*t for t in ts)
    closed=144*N-48*T*(1-F(1,3**N))
    assert rhs==closed
    return ts,rhs

check_family()
# Planted semantic corruption: removing the -1 carry error is not a legal
# modular midpoint witness, and must fail before any telescoping algebra.
cells,residuals,errors=family(F(1,10))[0]
try: carry_cost(cells,residuals,(0,0,0,-1))
except AssertionError: pass
else: raise AssertionError("planted invalid carry/error passed")
ts,rhs=finite_telescoping(7)
assert rhs==F(1008) - F(12)*(1-F(1,3**7))

# If |h|<=M then |D(u)-D(v)|<=4M.  The finite-N choice below is the
# contradiction criterion, not a numerical limiting argument.
def contradiction_bound(M):
    M=F(M)
    N=(4*M+12)//144+1
    _ts,lower=finite_telescoping(N)
    assert lower>4*M
    return N,lower

for M in (F(0),F(1),F(1000,1)):
    contradiction_bound(M)

payload=repr((U,A,B,family(F(1,10)),finite_telescoping(7))).encode()
print("PASS_BOUNDED_POTENTIAL_DILATION_WALL")
print({"cells":117,"active_cells":(A,B),"parameter_range":"0<t<1/3, 0<s<1",
       "families":((A,B,B),(A,A,B)),"carries":((0,0,-1,-1),(0,0,1,1)),
       "row_rhs":("216-48t","-72-48t"),"dilation_increment":"D(3t)-D(t)>=144-96t",
       "finite_N_bound":"D(T)-D(T/3^N)>=144N-48T(1-3^-N)",
       "scope":"no bounded physical potential on this fixed q=6 117-cell union satisfying every stated coercivity row",
       "sha256":sha256(payload).hexdigest()})
