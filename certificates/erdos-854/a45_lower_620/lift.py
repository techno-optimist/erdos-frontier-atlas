from math import gcd
from sympy import primorial, prime
rows={}
for l in open('../p854_1104/a048670_6.txt'):
    p=l.split()
    if len(p)>=3: rows[int(p[0])]=(int(p[1]),int(p[2]))
P45=primorial(45)
def lift(n, extra):
    g,s=rows[n]; Pn=primorial(n); W=700
    lo=s-1-W; hi=s-1+g+W
    base=[d for d in range(lo,hi+1) if gcd(d,Pn)==1]  # coprime to p_n#
    found={}
    import itertools
    for ks in itertools.product(*[range(q) for q in extra]):
        # shift x = s + K*Pn with K chosen per CRT so residues mod extra primes vary; use K = sum over combos directly
        pass
    return base
# simpler exact approach: residues of shift mod each extra prime fully enumerate lifts
def run(n, extra):
    g,s=rows[n]; Pn=primorial(n); W=700
    lo=s-1-W; hi=s-1+g+W
    base=[d for d in range(lo,hi+1) if gcd(d,Pn)==1]
    M=1
    for q in extra: M*=q
    found={}
    for K in range(M):
        off=K*Pn
        keep=[d for d in base if all((d+off)%q for q in extra)]
        for a,b in zip(keep,keep[1:]):
            t=b-a
            if t>=618:
                x=a+off
                found.setdefault(t,x)
    return found
out=[]
for n,extra in ((44,[197]),(43,[193,197])):
    f=run(n,extra)
    for t,x in sorted(f.items()):
        # direct verification at 197#
        ok=gcd(x,P45)==1 and gcd(x+t,P45)==1 and all(gcd(y,P45)!=1 for y in range(x+1,x+t))
        out.append((n,t,ok,x))
        print('from n=%d lift: gap %d verified=%s start_endpoint=%d'%(n,t,ok,x))
    if not f: print('from n=%d lift: no gap >= 618 in any of %d lifts'%(n, eval('*'.join(map(str,extra)))))
