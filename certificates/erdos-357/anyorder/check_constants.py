from fractions import Fraction as F
import math
eps=F(1,10**10); eta=F(1,10**4); K=10**22; sK=10**11
assert sK*sK==K
ok=lambda name,c: print(("PASS " if c else "FAIL ")+name) or c
res=[]
# Astra's five listed inequalities
res.append(ok("A1 eps+2/sqrtK+1/(2K)<=2eps", eps+F(2,sK)+F(1,2*K)<=2*eps))
res.append(ok("A2 eta-2/sqrtK-1/(2K)>=eta/2", eta-F(2,sK)-F(1,2*K)>=eta/2))
res.append(ok("A3 28/K+36/250000<=1/6000", F(28,K)+F(36,250000)<=F(1,6000)))
res.append(ok("A4 36eps+8eta+17/12000+22/K<=9/4000", 36*eps+8*eta+F(17,12000)+F(22,K)<=F(9,4000)))
res.append(ok("A5 90/4000+2/6000+2/10000+82/K<=1/40", F(90,4000)+F(2,6000)+F(2,10000)+F(82,K)<=F(1,40)))
# Hidden steps
res.append(ok("q bound: 2*(2eps k^2)/(eta k) = 4eps/eta k = k/250000", 4*eps/eta==F(1,250000)))
# 17/12000 = (h+1/2)*(1/6000) with h=8
res.append(ok("(8+1/2)/6000 == 17/12000", F(17,2)/6000==F(17,12000)))
res.append(ok("(T+h)/2 =22 for h=8", F(36+8,2)==22))
# 10*Delta/k^2 <= 10*9/4000 = 90/4000 ; 2d/k<=2/6000 ; 2eta = 2/10000; 80/k+2/k = 82/k
res.append(ok("2eta == 2/10000", 2*eta==F(2,10000)))
# pi bounds: 3pi<10 and 2/(3pi)>1/5 using pi in (333/106, 355/113)
plo,phi=F(333,106),F(355,113)
assert plo< F(math.pi).limit_denominator(10**9) <phi
res.append(ok("3*pi<10 (pi<355/113)", 3*phi<10))
res.append(ok("2/(3pi)>1/5 (pi<355/113)", F(2)/(3*phi)>F(1,5)))
res.append(ok("-1/5+1/20 == -3/20", -F(1,5)+F(1,20)==-F(3,20)))
res.append(ok("sum(9-r)=36", sum(9-r for r in range(1,9))==36))
res.append(ok("sum(9-r)(8-r)=168", sum((9-r)*(8-r) for r in range(1,9))==168))
res.append(ok("-63+2*168 == 273", -63+2*168==273))
res.append(ok("9-72*3/20 == -9/5", 9-72*F(3,20)==-F(9,5)))
res.append(ok("-9/5 K + 273 < 0", -F(9,5)*K+273<0))
# monotonicity: each 'k-dependent' term is c/sqrt(k) or c/k with c>0 on the small side; check symbolic sign
print("Monotonicity: each constraint has the form const +/- (positive)*k^{-1/2} or k^{-1}; the k-dependent terms only shrink as k grows,")
print(" so validity at K implies validity for all k>=K. Spot-check at k=K*10^j:")
for j in range(0,6):
    k=K*10**(2*j); s=sK*10**j
    c=[eps+F(2,s)+F(1,2*k)<=2*eps, eta-F(2,s)-F(1,2*k)>=eta/2, F(28,k)+F(36,250000)<=F(1,6000),
       36*eps+8*eta+F(17,12000)+F(22,k)<=F(9,4000), F(90,4000)+F(2,6000)+F(2,10000)+F(82,k)<=F(1,40)]
    print("  k=1e%d"%(22+2*j), all(c))
# Step 1 chain: S >= m(m+1)/(h(h+1)) >= k^2-2k^{3/2}+k for h=floor(sqrt k), checked exactly for many k
bad=0
for k in list(range(1,20001))+[10**12+7, 10**15+3]:
    h=math.isqrt(k); m=h*k-h*(h-1)//2
    lhs=F(m*(m+1),h*(h+1))
    # need lhs >= k^2 - 2 k^{3/2} + k  <=> (k^2+k-lhs) <= 2k^{3/2}; compare squares if positive
    d=k*k+k-lhs
    if d>0 and d*d>4*k**3: bad+=1
res.append(ok("Step1 S-bound exact for k<=20000 and two huge k", bad==0))
# Corollary slack for k<K: (3/2+eps)k-12sqrt k <= 3k/2-2sqrt k+1/2  <=> eps*k <= 10 sqrt k + 1/2
res.append(ok("Corollary slack at k=K: eps*K<=10*sqrtK+1/2", eps*K<=10*sK+F(1,2)))
print("ALL PASS" if all(res) else "SOME FAIL")
