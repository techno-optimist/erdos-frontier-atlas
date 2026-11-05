# independent verifier: own sieve, no sympy; checks the gap-620 witness
from math import gcd
ps=[p for p in range(2,300) if all(p%q for q in range(2,int(p**.5)+1))][:45]
assert ps[-1]==197 and len(ps)==45
P=1
for p in ps: P*=p
W={620:21324538953688689386201692152877021532742357109890761003674083154109358235557941,
   618:9071970817249978978218585063273478726825229548839054196727279383708216887235033}  # one of two fresh 618s
def isgap(x,t): return gcd(x,P)==1 and gcd(x+t,P)==1 and all(gcd(y,P)>1 for y in range(x+1,x+t))
for t,x in W.items():
    xr=x%P
    print(t,'gap_ok',isgap(x,t),'reduced_ok',isgap(xr,t),'x mod 197#=',xr)
    print('  planted x+2 rejected:',not isgap(x+2,t),' planted t-2 rejected:',not isgap(x,t-2))
