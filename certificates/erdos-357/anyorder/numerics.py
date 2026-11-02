import mpmath as mp, itertools, random, sys
mp.mp.dps=50
def admissible(x):
    S=set()
    for u in range(len(x)):
        t=0
        for v in range(u,len(x)):
            t+=x[v]
            if t in S: return False
            S.add(t)
    return True
def check(x, verbose=False):
    k=len(x); s=[0]
    for v in x: s.append(s[-1]+v)
    u=[mp.expj(3*mp.pi*(mp.mpf(s[j])/k - j)) for j in range(k+1)]
    Q=mp.mpf(0)
    for i in range(0,k-7):
        Q+=abs(sum(u[i+j] for j in range(9)))**2
    c=lambda r,t: mp.cos(3*mp.pi*(mp.mpf(s[t+r]-s[t])/k - r))
    C={r: sum(c(r,t) for t in range(0,k-r+1)) for r in range(1,9)}
    diag=9*(k-7); cross=mp.mpf(0); worst=-mp.inf
    for r in range(1,9):
        for a in range(0,9-r):
            p=sum(c(r,t) for t in range(a,k-8+a+1))
            cross+=p
            worst=max(worst,p-(C[r]+(8-r)))
    ident=abs(Q-(diag+2*cross))
    bound=9*k+2*sum((9-r)*C[r] for r in range(1,9))+273
    if verbose:
        print(" k=%d N=%d admissible=%s"%(k,max(x),admissible(x)))
        print(" Q=%s  |Q-(9(k-7)+2cross)|=%s"%(mp.nstr(Q,15),mp.nstr(ident,3)))
        print(" max_{r,a} [partial - (C_r+8-r)] = %s (must be <=0)"%mp.nstr(worst,10))
        print(" Q <= 9k+2sum(9-r)C_r+273 = %s : %s"%(mp.nstr(bound,12), Q<=bound+mp.mpf(10)**-20))
        print(" C_r/k:", [mp.nstr(C[r]/k,4) for r in range(1,9)])
    return ident<mp.mpf(10)**-20, worst<=mp.mpf(10)**-20, Q<=bound+mp.mpf(10)**-20
w=[4,1,2,10,22,15,21,24,28,29,27,16,26,20,18,23,25,19,11]
print("Witness k=19:"); r=check(w,True); print(" all:",r)
# exhaustive admissible rows at N=a(k) for k=9..12 (DFS)
A={9:12,10:13,11:14,12:17}
for k,N in A.items():
    rows=[]
    def dfs(cur,used,sums):
        if len(rows)>=3000: return
        if len(cur)==k: rows.append(list(cur)); return
        for v in range(1,N+1):
            if v in used: continue
            # new suffix sums ending at v
            new=[];t=0;okk=True
            for y in [v]+cur[::-1]:
                t+=y
                if t in sums or t in new: okk=False;break
                new.append(t)
            if okk:
                cur.append(v);used.add(v);sums.update(new)
                dfs(cur,used,sums)
                cur.pop();used.discard(v);sums.difference_update(new)
    dfs([],set(),set())
    mp.mp.dps=30
    res=[check(x) for x in rows]
    print("k=%d N=%d rows checked=%d (cap 3000) identity ok=%s partial-bound ok=%s Q-bound ok=%s"%(k,N,len(rows),all(a for a,_,_ in res),all(b for _,b,_ in res),all(c for _,_,c in res)))
# random larger admissible rows (greedy random), k up to 60
random.seed(1); cnt=0; allok=True
for trial in range(400):
    N=random.randint(40,200); k=0; cur=[]; sums=set(); used=set()
    vals=list(range(1,N+1)); random.shuffle(vals)
    for v in vals:
        new=[];t=0;okk=True
        for y in [v]+cur[::-1]:
            t+=y
            if t in sums or t in new: okk=False;break
            new.append(t)
        if okk: cur.append(v); sums.update(new)
    if len(cur)>=9:
        a,b,c=check(cur); cnt+=1; allok&=a and b and c
print("random admissible rows (k>=9) checked=%d all identities/bounds ok=%s"%(cnt,allok))
