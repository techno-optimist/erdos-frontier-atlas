#!/usr/bin/env python3
"""Stdlib-only independent replay of the q24 cylinder-position certificate."""
import argparse, hashlib, itertools, json, math
from pathlib import Path

Q=24; ROLES=("P1","P2","P3","B","K")
WORDS=(("P1","K","B"),("B","K","P1"),("P2","B","P2"),("P3","B","B"),("B","B","P3"))
ASSIGN=(7,7,7,6,7)
def tile():
 return frozenset((x,y) for x in range(Q) for y in range(Q) if (x>=12 and x+y>=17 and x+y<=28) or (x>=12 and y<=11 and x+y>=29 and x+y<=34) or (x<=11 and y>=12 and x+y>=29 and x+y<=34 and 4*x+2*y>=74))
def d4(s,k):
 out=[]
 for x,y in s:
  if k&1:x=Q-1-x
  if k&2:y=Q-1-y
  if k&4:x,y=y,x
  out.append((x,y))
 return frozenset(out)
def mids(x,z):
 out=[]
 for a in range(Q):
  for b in range(Q):
   if (2*a-x[0]-z[0])%Q==0 and (2*b-x[1]-z[1])%Q==0:out.append((a,b))
 return tuple(out)
def cost(x,z):return (x[0]-z[0])**2+(x[1]-z[1])**2
def mass(supp):
 total=0
 for mask in range(1,32):
  chosen=[WORDS[i] for i in range(5) if mask>>i&1]; n=1
  for j in range(3):
   common=set(supp[chosen[0][j]])
   for w in chosen[1:]:common &= set(supp[w[j]])
   n*=len(common)
  total += n if len(chosen)%2 else -n
 return total
def main():
 ap=argparse.ArgumentParser();ap.add_argument('packet',nargs='?',default=str(Path(__file__).with_name('certificate.json'))); args=ap.parse_args(); p=Path(args.packet);j=json.loads(p.read_text())
 base=tile(); ims=[]
 for k in range(8):
  s=d4(base,k)
  if s not in ims:ims.append(s)
 supp={r:ims[ASSIGN[i]] for i,r in enumerate(ROLES)}; assert len(base)==163 and len(ims)==8 and mass(supp)==21653735
 # Independent cylinder disjointness.
 for a,b in itertools.combinations(WORDS,2):assert not all(set(supp[a[i]])&set(supp[b[i]]) for i in range(3))
 labels=[];vid={}
 for c,w in enumerate(WORDS):
  for i in range(3):
   for pt in sorted(supp[w[i]]):vid[c,i,pt]=len(labels);labels.append([c,i,list(pt)])
 assert len(labels)==2445 and labels==j.get('g_variable_labels',labels)
 locals_=j['local_rows']; sums=j['triple_sum_rows']; assert len(locals_)==662 and len(sums)==125
 for row in locals_:
  pr=row['provenance'];A,B,C=map(int,pr['word_indices']);i=int(pr['position']);w=pr['witness'];x,y,z=map(tuple,(w['x'],w['y'],w['z']))
  assert x in supp[WORDS[A][i]] and y in supp[WORDS[B][i]] and z in supp[WORDS[C][i]] and y in mids(x,z)
  assert tuple(w['carry'])==((x[0]+z[0]-2*y[0])//Q,(x[1]+z[1]-2*y[1])//Q) and int(w['raw_cost_numerator'])==cost(x,z)
  t=2445+(((A*5+B)*5+C)*3+i); co={t:1}
  for q,v in ((vid[A,i,x],-1),(vid[C,i,z],-1),(vid[B,i,y],2)):co[q]=co.get(q,0)+v
  assert row['coefficients']==[[q,v] for q,v in sorted(co.items()) if v] and int(row['rhs_num'])==-cost(x,z)
 for row in sums:
  A,B,C=map(int,row['provenance']['word_indices']); ex=[[2445+(((A*5+B)*5+C)*3+i),-1] for i in range(3)];assert row['coefficients']==ex and row['rhs_num']==0
 rows=locals_+sums; agg=[0]*2820;rhs=0
 for fr in j['farkas_rows']:
  assert int(fr['multiplier'])>0; idx=int(fr['index'])+(0 if fr['kind']=='local' else len(locals_)); m=int(fr['multiplier']); rhs+=m*int(rows[idx]['rhs_num'])
  for q,v in rows[idx]['coefficients']:agg[q]+=m*int(v)
 assert len(j['farkas_rows'])==771 and all(v==0 for v in agg) and rhs<0
 summary={'packet_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'q':Q,'tile_points':163,'d4_images':8,'assignment':list(ASSIGN),'g_variables':2445,'t_variables':375,'selected_local_rows':662,'selected_sum_rows':125,'farkas_rows':771,'union_mass_count':21653735,'farkas_rhs':str(rhs),'scope':j.get('scope',{}),'verdict':'PASS_INDEPENDENT_Q24_D4_CYLINDER_POSITION_REPLAY'}
 print('PASS_INDEPENDENT_Q24_D4_CYLINDER_POSITION_REPLAY');print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
