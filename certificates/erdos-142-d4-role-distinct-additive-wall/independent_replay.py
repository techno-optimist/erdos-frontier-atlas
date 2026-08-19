import hashlib, json, itertools
from pathlib import Path

ROOT=Path(__file__).resolve().parent
Q=24
ROLES=('P1','P2','P3','B','K')
WORDS=(('P1','K','B'),('B','K','P1'),('P2','B','P2'),('P3','B','B'),('B','B','P3'))

def tile_independent():
    s=set()
    for x in range(Q):
      for y in range(Q):
        sm=x+y
        a=(x>=12 and sm>=17 and sm<=28)
        b=(x>=12 and y<=11 and sm>=29 and sm<=34)
        c=(x<=11 and y>=12 and sm>=29 and sm<=34 and 4*x+2*y>=74)
        if a or b or c: s.add((x,y))
    assert len(s)==163
    return s

def d4(s,k):
    z=[]
    for x,y in s:
      if k&1: x,y=23-x,y
      if k&2: x,y=x,23-y
      if k&4: x,y=y,x
      z.append((x,y))
    return frozenset(z)

def union_ie(supp):
    total=0
    for n in range(1,6):
      for chosen in itertools.combinations(WORDS,n):
        prod=1
        for j in range(3):
          common=set(supp[chosen[0][j]])
          for w in chosen[1:]: common &= supp[w[j]]
          prod*=len(common)
        total += prod if n%2 else -prod
    return total

def main():
    packet=json.loads((ROOT/'certificate.json').read_text())
    frozen=json.loads((ROOT/'role_distinct_ipm_rows.json').read_text())['rows']
    base=tile_independent(); ims=[]
    for k in range(8):
      im=d4(base,k)
      assert im not in ims; ims.append(im)
    assert all(len(x)==163 for x in ims)
    assignment=(7,7,7,6,7)
    supp={r:ims[assignment[i]] for i,r in enumerate(ROLES)}
    assert union_ie(supp)==21653735
    labels=[]; idx={}
    for r in ROLES:
      for p in sorted(supp[r]): idx[(r,p)]=len(labels); labels.append((r,p))
    assert len(labels)==815 and [ [r,list(p)] for r,p in labels]==packet['variable_labels']
    aggregate={}; rhs=0; seen=set(); rows=packet['selected_rows']
    assert len(rows)==622
    for row in rows:
      fi=row['frozen_row_index']; assert fi not in seen and 0<=fi<len(frozen); seen.add(fi)
      m=int(row['multiplier']); assert m>0
      a,b,c=row['word_indices']; ws=(WORDS[a],WORDS[b],WORDS[c]); coeff={}; rr=0
      assert len(row['witnesses'])==3
      for j,wit in enumerate(row['witnesses']):
        roles=tuple(w[j] for w in ws); assert tuple(wit['role_triple'])==roles
        x,y,z=map(tuple,(wit['x'],wit['y'],wit['z']))
        assert x in supp[roles[0]] and y in supp[roles[1]] and z in supp[roles[2]]
        carry=tuple((x[t]+z[t]-2*y[t])//Q for t in range(2))
        assert all((2*y[t]-x[t]-z[t])%Q==0 for t in range(2))
        assert list(carry)==wit['carry'] and all(v in (-1,0,1) for v in carry)
        cost=sum((x[t]-z[t])**2 for t in range(2)); assert cost==wit['raw_cost_numerator']; rr+=cost
        for r,p,v in ((roles[0],x,1),(roles[1],y,-2),(roles[2],z,1)):
          q=idx[(r,p)]; coeff[q]=coeff.get(q,0)+v
      expected=[[q,v] for q,v in sorted(coeff.items()) if v]
      assert frozen[fi]['coefficients']==expected and frozen[fi]['rhs_num']==rr
      rhs += m*rr
      for q,v in coeff.items(): aggregate[q]=aggregate.get(q,0)+m*v
    assert not any(aggregate.values())
    assert rhs==int(packet['positive_rhs_num']) and rhs>0
    report={'tile_points':len(base),'d4_images':len(ims),'variables':len(labels),'selected_rows':len(rows),'union_mass':union_ie(supp),'threshold':packet['threshold_count'],'rhs':rhs,'frozen_rows':len(frozen),'source_hash':hashlib.sha256((ROOT/'role_distinct_ipm_rows.json').read_bytes()).hexdigest()}
    print('PASS_INDEPENDENT_Q24_D4_ROLE_DISTINCT_REPLAY')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
