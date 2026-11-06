import sys,re,math,hashlib
def primes(n):
    s=bytearray([1])*(n+1);s[0]=s[1]=0
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=bytearray(len(s[i*i::i]))
    return [i for i in range(n+1) if s[i]]
P=primes(197); assert len(P)==45 and P[-1]==197
M=math.prod(P)
def crt(res):
    x=0
    for p,r in zip(P,res):
        m=M//p; x=(x+(-r)%p*m*pow(m,-1,p))%M
    return x
def check(x,t):
    g=lambda y: math.gcd(y,M)
    return g(x)==1 and g(x+t)==1 and all(g(x+i)>1 for i in range(1,t))
out=[]
for line in open(sys.argv[1]):
    if 'WITNESS' not in line: continue
    t=int(re.search(r't=(\d+)',line).group(1)); res=list(map(int,line.split('WITNESS')[1].split()))
    x=crt(res); ok=check(x,t)
    out.append(f"t={t} ok={ok} x={x} xmod197#={x%M}")
    # planted controls: wrong length must fail
    out.append(f"  planted t-2 ok={check(x,t-2)} t+2 ok={check(x,t+2)} x+2 ok={check(x+2,t)}")
print('\n'.join(out))
