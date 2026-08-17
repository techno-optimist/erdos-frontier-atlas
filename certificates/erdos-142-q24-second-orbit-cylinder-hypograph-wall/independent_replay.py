"""Stdlib-only replay of Terra's q=24 B-orbit exact packet.

This deliberately does not import Terra code or its verifier.  It checks the
serialized row semantics, all 125 triple-sum rows, the 931 selected rows, and
replays the integer cancellation and positive RHS exactly.
"""
import argparse, hashlib, itertools, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
Q = 24
ASSIGN = [7, 6, 7, 6, 7]
WORDS = [("P1","K","B"),("B","K","P1"),("P2","B","P2"),("P3","B","B"),("B","B","P3")]

def tile():
    s=set()
    for x in range(Q):
        for y in range(Q):
            sm=x+y
            if (x>=12 and sm>=17 and sm<=28) or (x>=12 and y<=11 and 29<=sm<=34) or (x<=11 and y>=12 and 29<=sm<=34 and 4*x+2*y>=74): s.add((x,y))
    assert len(s)==163
    return s

def d4(s,k):
    out=set()
    for x,y in s:
        if k&1: x=Q-1-x
        if k&2: y=Q-1-y
        if k&4: x,y=y,x
        out.add((x,y))
    return out

def union_count(supports):
    total=0
    for n in range(1,6):
        for chosen in itertools.combinations(range(5),n):
            prod=1
            for j in range(3):
                common=set(supports[WORDS[chosen[0]][j]])
                for i in chosen[1:]: common &= set(supports[WORDS[i][j]])
                prod *= len(common)
            total += prod if n&1 else -prod
    return total

def check(mutate=False):
    packet=json.loads((ROOT/'certificate.json').read_text())
    assert packet['q']==Q and packet['assignment']==ASSIGN
    assert packet['cylinders']==["AAC","CAA","CCC","ACC","CCA"]
    orbit=packet['d4_orbit']; assert orbit['role_word_automorphisms']==2 and orbit['global_d4_elements']==8 and orbit['orbit_size']==8
    expected=[[0,1,0,1,0],[1,0,1,0,1],[2,3,2,3,2],[3,2,3,2,3],[4,5,4,5,4],[5,4,5,4,5],[6,7,6,7,6],[7,6,7,6,7]]
    assert orbit['assignments']==expected
    ims=[d4(tile(),k) for k in range(8)]
    supports={r:ims[ASSIGN[i]] for i,r in enumerate(('P1','P2','P3','B','K'))}
    mass=union_count(supports); assert mass==packet['union_mass_count']==21653735
    locals_=packet['local_rows']; sums=packet['triple_sum_rows']; assert len(locals_)==816 and len(sums)==125
    labels={tuple((int(c),int(i),tuple(p))):n for n,(c,i,p) in enumerate(packet['g_variable_labels'])}
    def tindex(a,b,c,pos): return 2445 + 3*((a*5+b)*5+c)+pos
    for row in locals_:
        s=row['semantic']; assert s['kind']=='local-hypograph'; a,b,c=s['word_indices']; i=int(s['position'])
        co={tindex(a,b,c,i):1}
        for wi,pt,sgn in ((a,tuple(s['x']),-1),(b,tuple(s['y']),2),(c,tuple(s['z']),-1)):
            j=labels[(wi,i,pt)]; co[j]=co.get(j,0)+sgn
        assert row['coefficients']==[[j,v] for j,v in sorted(co.items()) if v]
        assert int(row['rhs_num'])==-int(s['raw_cost_numerator'])
    for row in sums:
        s=row['semantic']; assert s['kind']=='triple-sum'; a,b,c=s['word_indices']
        assert row['coefficients']==[[tindex(a,b,c,i),-1] for i in range(3)] and int(row['rhs_num'])==0
    allrows=locals_+sums; agg={}; rhs=0
    selected=packet['farkas_rows']; assert len(selected)==931
    for item in selected:
        kind=item['kind']; idx=int(item['index'])
        row=(packet['local_rows'] if kind=='local' else packet['triple_sum_rows'])[idx]
        mult=int(item['multiplier']); assert mult>0
        rhs += mult*int(row['rhs_num'])
        for j,v in row['coefficients']: agg[int(j)]=agg.get(int(j),0)+mult*int(v)
    if mutate: rhs += 1
    assert not any(agg.values()), 'nonzero coefficient residue'
    assert -rhs==int(packet['ray']['positive_contradiction'])
    assert rhs<0 and int(packet['ray']['support'])==931
    return {'verdict':'PASS_INDEPENDENT_Q24_D4_SECOND_ORBIT_REPLAY','assignment':ASSIGN,'union_mass_count':mass,'local_rows':len(locals_),'sum_rows':len(sums),'selected_rows':len(selected),'nonzero_coefficient_residue':0,'positive_rhs':str(-rhs),'packet_rhs_match':True,'packet_sha256':hashlib.sha256((ROOT/'certificate.json').read_bytes()).hexdigest()}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true'); args=ap.parse_args()
    result=check(False)
    if args.self_test:
        try: check(True)
        except AssertionError: result['mutation_self_test']='PASS'
        else: raise SystemExit('mutation self-test unexpectedly passed')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
