#!/usr/bin/env python3
"""Exact hostile replay of the minimum-rank-idempotent sandwich wall."""
from collections import Counter, deque
from fractions import Fraction as F
from itertools import product
from math import factorial

Q=42
BASE=((3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2))
OFF=((0,4),(1,4),(1,5),(2,1),(2,3),(3,5),(4,0),(4,4),(4,5),
     (5,0),(5,1),(5,2),(5,3))
SHAPE=((2,29),(8,41),(14,11),(20,23),(26,35),(32,5),(38,17))
PLAN=((1,0,6),(0,1,2),(0,2,4),(1,3,5),(3,4,5),(4,5,6),(2,6,3))

def need(c,m):
    if not c:raise AssertionError(m)

def compose(f,g):
    """First f, then g."""
    return tuple(g[f[x]] for x in range(len(f)))

def power(f,n):
    out=tuple(range(len(f)))
    for _ in range(n):out=compose(out,f)
    return out

def rank(f):return len(set(f))
def idempotent(f):return compose(f,f)==f

def packet():
    roles=tuple((21,14,(21+x)%Q,(14+y)%Q) for x,y in SHAPE)
    coeff=Counter();cost=F(0);raw=F(0)
    for x,y,z in PLAN:
        need(all((roles[x][j]+roles[z][j]-2*roles[y][j])%Q==0 for j in range(4)),
             'packet midpoint')
        coeff[x]+=1;coeff[z]+=1;coeff[y]-=2
        for j in range(4):
            d=(roles[x][j]-roles[z][j])%Q;d=min(d,Q-d)
            cost+=F(d*d,Q*Q)
            raw+=F((roles[x][j]-roles[z][j])**2,Q*Q)
    need(set(coeff)==set(range(7)) and not any(coeff.values()),'balanced incidence')
    need(cost==F(11,7),'packet cost')
    need(raw==F(16,7),'raw packet cost')
    return roles,cost,raw

def closure(seed,funcs,index,table,identity):
    members=set(seed);members.add(identity);changed=True
    while changed:
        changed=False;old=tuple(members)
        for f in old:
            for g in old:
                for h in (table[f][g],table[g][f]):
                    if h not in members:members.add(h);changed=True
    return frozenset(members)

def enumerate_t3_monoids():
    funcs=tuple(product(range(3),repeat=3));index={f:i for i,f in enumerate(funcs)}
    identity=index[(0,1,2)]
    table=tuple(tuple(index[compose(f,g)] for g in funcs) for f in funcs)
    start=frozenset((identity,));seen={start};queue=deque((start,))
    while queue:
        monoid=queue.popleft()
        for generator in range(len(funcs)):
            if generator in monoid:continue
            enlarged=closure((*monoid,generator),funcs,index,table,identity)
            if enlarged not in seen:seen.add(enlarged);queue.append(enlarged)
    need(len(seen)==699,'T3 monoid census')
    return funcs,table,tuple(seen)

def restriction_order(t,I):
    current={x:x for x in I}
    for order in range(1,factorial(len(I))+1):
        current={x:t[current[x]] for x in I}
        if all(current[x]==x for x in I):return order
    raise AssertionError('permutation order bound')

def audit_all_t3_monoids():
    funcs,table,monoids=enumerate_t3_monoids()
    rank_hist=Counter();sandwiches=0;idempotents_seen=0;order_hist=Counter()
    for monoid in monoids:
        r=min(rank(funcs[i]) for i in monoid);rank_hist[r]+=1
        es=tuple(i for i in monoid if rank(funcs[i])==r and idempotent(funcs[i]))
        need(es,'minimum-rank idempotent exists')
        idempotents_seen+=len(es)
        for ei in es:
            e=funcs[ei];I=frozenset(e);need(len(I)==r,'idempotent image size')
            need(all(e[x]==x for x in I),'e fixes its image')
            for ai in monoid:
                # e a e, in word order: e first, then a, then e.
                ti=table[table[ei][ai]][ei];t=funcs[ti]
                need(ti in monoid,'sandwich belongs to monoid')
                need(frozenset(t[x] for x in I)==I,'sandwich restriction surjective')
                need(rank(t)==r,'sandwich has minimum rank')
                order=restriction_order(t,I)
                need(all(power(t,factorial(r))[x]==x for x in I),'r! kills restriction')
                order_hist[order]+=1;sandwiches+=1
    print('T3_ALL_MONOIDS',len(monoids),'MINRANK_HIST',dict(sorted(rank_hist.items())),
          'MIN_IDEMPOTENTS',idempotents_seen,'SANDWICHES',sandwiches,
          'RESTRICTION_ORDER_HIST',dict(sorted(order_hist.items())))

def alphabet_and_roles():
    coarse=tuple((a,b,(a+dx)%6,(b+dy)%6) for a,b in BASE for dx,dy in OFF)
    need(len(coarse)==len(set(coarse))==117,'coarse census')
    codes=tuple(tuple(7*c[j]+r[j] for j in range(4))
                for c in coarse for r in product(range(7),repeat=4))
    need(len(codes)==len(set(codes))==280917,'fine alphabet census')
    roles,_cost,_raw=packet();need(set(roles)<=set(codes),'roles in alphabet')
    return codes,roles

def block_mid(x,y,z):return all((x[j]+z[j]-2*y[j])%Q==0 for j in range(4))
def block_cost(x,z):
    total=F(0)
    for a,b in zip(x,z):
        d=(a-b)%Q;d=min(d,Q-d);total+=F(d*d,Q*Q)
    return total

def concrete_rank2_wall():
    codes,roles=alphabet_and_roles();Ecode=next(c for c in codes if c not in roles)
    e=(0,0,2);swap=(2,2,0);other=(1,1,2)
    rolemaps=(e,swap,other,e,swap,other,swap)
    generated={tuple(range(3)),e,swap,other}
    changed=True
    while changed:
        changed=False
        for f in tuple(generated):
            for g in tuple(generated):
                h=compose(f,g)
                if h not in generated:generated.add(h);changed=True
    need(min(map(rank,generated))==2 and idempotent(e),'rank-two monoid')
    need(all(any(f[source]==target for f in generated) for source in range(3)
             for target in range(3)),'rank-two monoid transitive')
    I=frozenset(e);q=e[0];L=factorial(len(I));need(L==2,'rank-two exponent')
    for a in rolemaps:
        t=compose(compose(e,a),e)
        need(all(power(t,L)[x]==x for x in I),'sandwich return')

    # Physical words u(p_i u)^L, where u is the one-block Ecode word.
    words=tuple((Ecode,)+sum(((roles[i],Ecode) for _ in range(L)),()) for i in range(7))
    for i,a in enumerate(rolemaps):
        state=0;state=e[state]
        for _ in range(L):state=a[state];state=e[state]
        need(state==q,'accepted return to q')
    incidence=Counter();cost=F(0);rawcost=F(0)
    for x,y,z in PLAN:
        need(all(block_mid(words[x][b],words[y][b],words[z][b])
                 for b in range(len(words[x]))),'whole-word midpoint')
        incidence[x]+=1;incidence[z]+=1;incidence[y]-=2
        cost+=sum((block_cost(words[x][b],words[z][b]) for b in range(len(words[x]))),F(0))
        rawcost+=sum((sum(F((words[x][b][j]-words[z][b][j])**2,Q*Q) for j in range(4))
                      for b in range(len(words[x]))),F(0))
    need(not any(incidence.values()) and cost==L*F(11,7) and rawcost==L*F(16,7),
         'whole-word Farkas plan')

    # All ordered physical midpoint rows: seven diagonals plus 42 positive rows.
    ordered=[]
    for x,y,z in product(range(7),repeat=3):
        if all(block_mid(words[x][b],words[y][b],words[z][b]) for b in range(len(words[x]))):
            c=sum((block_cost(words[x][b],words[z][b]) for b in range(len(words[x]))),F(0))
            ordered.append((x,y,z,c))
    need(len(ordered)==49 and sum(x==z and y!=x for x,y,z,_ in ordered)==0,
         'ordered midpoint and x=z audit')
    print('CONCRETE_RANK2_WALL','states=3','L',L,'word_blocks',len(words[0]),
          'ordered_rows',len(ordered),'balanced_geo_cost',cost,'balanced_raw_cost',rawcost)

def assumption_seams():
    # Complete but untrimmed: every packet role goes to a dead sink.  The
    # minimum-rank idempotent exists, but e(start) has no accepting suffix.
    identity=(0,1);dead=(1,1);monoid=(identity,dead)
    e=dead;need(idempotent(e) and min(map(rank,monoid))==1,'dead min idempotent')
    start=accept=0;q=e[start];need(q==1,'idempotent reaches dead state')
    need(all(power(dead,n)[start]!=accept for n in range(1,5)),'no accepting suffix')
    # Removing the sink leaves one live state but makes every role undefined.
    live=frozenset((0,));need(any(dead[x] not in live for x in live),'trim makes roles partial')

    # A tiny genuinely trimmed partial automaton: x:0->1 and y:1->0 make both
    # states accessible/coaccessible from start=accept=0, while alternating
    # role ownership means no common state admits all seven role symbols.
    partial_aux=({'x':{0:1}},{'y':{1:0}})
    x=partial_aux[0]['x'];y=partial_aux[1]['y']
    need(x[0]==1 and y[1]==0,'partial auxiliary transitions')
    partial_start=partial_accept=0
    accessible={partial_start,x[partial_start]}
    coaccessible={partial_accept,1 if y[1]==partial_accept else -1}
    need(accessible=={0,1} and coaccessible=={0,1},
         'partial states accessible and coaccessible')
    domains={i:(frozenset((0,)) if i%2==0 else frozenset((1,))) for i in range(7)}
    need(set().union(*domains.values())=={0,1},'partial role coverage')
    need(not any(all(s in domains[i] for i in range(7)) for s in (0,1)),
         'no common state owns every role')
    print('ASSUMPTION_SEAMS','complete_untrimmed_min_idempotent_is_dead',
          'trimmed_partial_states_accessible_coaccessible',
          'trimmed_partial_has_no_seven_role_transformation_code')

def main():
    roles,cost,raw=packet();print('PACKET','roles',len(roles),'rows',len(PLAN),
                                  'geo_cost',cost,'raw_cost',raw)
    audit_all_t3_monoids()
    concrete_rank2_wall()
    assumption_seams()
    print('PASS_MINRANK_IDEMPOTENT_SANDWICH_AUDIT')

if __name__=='__main__':main()
