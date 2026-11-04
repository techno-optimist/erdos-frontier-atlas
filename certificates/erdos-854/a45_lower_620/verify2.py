# independent verifier: own sieve, no sympy
from math import gcd
ps=[p for p in range(2,300) if all(p%q for q in range(2,int(p**.5)+1))][:45]
assert ps[-1]==197
P=1
for p in ps: P*=p
W={618:4187490031468636811376281325827914336433867976450182896893867463550608585639019,
   622:33235996984655520130876908051439546762433090773836057395875647973481039529190441}
def isgap(x,t): return gcd(x,P)==1 and gcd(x+t,P)==1 and all(gcd(y,P)>1 for y in range(x+1,x+t))
for t,x in W.items():
    xr=x%P
    print(t,'gap_ok',isgap(x,t),'reduced_ok',isgap(xr,t),'x mod 197#=',xr)
    print('  planted x+2 rejected:',not isgap(x+2,t),' planted t-2 rejected:',not isgap(x,t-2))
