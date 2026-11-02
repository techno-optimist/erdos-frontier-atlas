# Exact (Fraction) verification of the tightened per-h bookkeeping, at k=K and monotone for k>=K.
from fractions import Fraction as F
import mpmath as mp, math
K=10**22; sK=10**11
def verify(eps,eta,lam_hi,sig_lo,c,k=K,sk=sK):
    n=len(c)
    ep=eps+F(2,sk)+F(1,2*k); et=eta-F(2,sk)-F(1,2*k)
    assert et>0
    q=ep/et; assert q<1
    dl=[F(0)]
    for h in range(1,n):
        T=F(h*(h+1),2)
        d=F(h*(h-1),2*k)+T*q
        D=T*eps+h*eta+(h+F(1,2))*d+(T+h)/(2*k)
        dl.append(2*d+lam_hi*D+lam_hi*F(h,k)+2*eta+F(2,k))
    val=sum(x*x for x in c)
    for r in range(1,n):
        A=sum(c[a]*c[a+r] for a in range(n-r))
        rho=-sig_lo+dl[r]+dl[r-1]
        val+=2*A*rho+2*A*F(n-1-r,k)
    return val  # need < 0
# Case 1: Astra's template exactly (alpha=3pi, 9 equal weights); lam<=3*355/113, sigma>=2/(3*355/113)
pi_hi=F(355,113)
lam=3*pi_hi; sig=F(2)/(3*pi_hi)
for eps,eta in [(F(1,10**10),F(1,10**4)),(F(4,10**8),None)]:
    if eta is None:
        best=None
        for x in range(-200,-60):
            e=F(10**9*round(10**(x/40)*10**9),10**18) if False else F(round(10**(x/40)*10**12),10**12)
            v=verify(eps,e,lam,sig,[F(1)]*9)
            if best is None or v<best[0]: best=(v,e)
        v,eta=best
    v=verify(eps,eta,lam,sig,[F(1)]*9)
    print("3pi/ones9 eps=%s eta=%s  Q/k bound=%s  -> %s"%(eps,eta,float(v),"CONTRADICTION (valid)" if v<0 else "fails"))
    # monotonic in k: check also at 10^24,10^30
    for j in (1,4):
        print("   also k=1e%d:"%(22+2*j), verify(eps,eta,lam,sig,[F(1)]*9,k=K*10**(2*j),sk=sK*10**j)<0)
# Case 2: alpha=89/10, n=10 sine-like rational weights
mp.mp.dps=40
alpha=F(89,10)
with mp.workprec(200):
    s=mp.iv.sin(mp.iv.mpf(89)/20)   # sin(alpha/2), rigorous interval
sin_hi=F(str(mp.mpf(s.b)))  # upper end (negative number), so -2 sin/alpha >= -2*sin_hi/alpha
sin_hi=F(math.ceil(sin_hi*10**30),10**30)
sig2=-2*sin_hi/alpha
print("alpha=8.9: sigma >= %.12f (rigorous)"%float(sig2))
c=[F(round(1000*math.sin(math.pi*(j+1)/11)),1000) for j in range(10)]
best=None
for x in range(-200,-60):
    e=F(round(10**(x/40)*10**12),10**12)
    v=verify(F(6,10**8),e,alpha,sig2,c)
    if best is None or v<best[0]: best=(v,e)
print("alpha=8.9/n=10 sine weights", [str(w) for w in c], "eps=6e-8 eta=%s Q/k bound=%s -> %s"%(best[1],float(best[0]),"CONTRADICTION (valid)" if best[0]<0 else "fails"))
# Smallest K=10^(2j) for which eps=1e-10 closes in Astra's own template (tightened bookkeeping)
for j in range(5,12):
    k=10**(2*j); sk=10**j; ok=False
    for x in range(-240,-40):
        e=F(round(10**(x/40)*10**12),10**12)
        try:
            if verify(F(1,10**10),e,lam,sig,[F(1)]*9,k=k,sk=sk)<0: ok=True;eta_ok=e;break
        except AssertionError: pass
    print("eps=1e-10, K=1e%d: %s"%(2*j, ("closes, eta=%s"%eta_ok) if ok else "does not close"))
