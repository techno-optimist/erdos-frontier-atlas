"""Stdlib-only exact replay of Terra's q=6 pair-coordinate packets."""
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent; Q=6
ROLES=('P1','P2','P3','B','K'); WORDS=(('P1','K','B'),('B','K','P1'),('P2','B','P2'),('P3','B','B'),('B','B','P3'))
ASS={'certificate_A.json':(7,7,7,6,7),'certificate_B.json':(7,6,7,6,7)}
def support():
 # EHPS q=6, exact half-open inequalities (9 points).
 return {(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)}
def d4(s,k):
 o=set()
 for x,y in s:
  if k&1:x=Q-1-x
  if k&2:y=Q-1-y
  if k&4:x,y=y,x
  o.add((x,y))
 return o
def midpoint(x,y,z): return all((x[i]+z[i]-2*y[i])%Q==0 for i in range(2))
def union_count(supp):
 t=0
 for n in range(1,6):
  for cs in itertools.combinations(range(5),n):
   p=1
   for i in range(3):
    a=set(supp[WORDS[cs[0]][i]])
    for c in cs[1:]:a &= supp[WORDS[c][i]]
    p*=len(a)
   t += p if n&1 else -p
 return t
def run(name,mutate=False):
 p=json.loads((ROOT/name).read_text()); ass=ASS[name]; rep='A' if name.endswith('_A.json') else 'B'
 assert p.get('packet_format')=='erdos-142-q6-pair-coordinate-semantic-farkas-v1'
 assert p.get('scope')=={'finite_q':6,'continuum_claim':False,'potential_ansatz':'separate H[c,01], H[c,02], H[c,12] for each of five codeword cylinders','ordered_word_triples_in_model':125,'all_even_q_midpoint_branches':True,'cost':'raw canonical endpoint squared Euclidean cost / q^2'}
 assert p.get('representative_label')==rep
 assert tuple(p['assignment'])==ass and int(p.get('variable_count',1215))==1215 and p['selected_rows']
 s0=support(); assert len(s0)==9
 ims=[d4(s0,k) for k in range(8)]; supp={r:ims[ass[i]] for i,r in enumerate(ROLES)}
 assert union_count(supp)==3645 and 3645*24**3 > 7**3*6**6
 # Pair indexer: 5 cylinders x 3 coordinate pairs x 9x9 ordered support points.
 dims=((0,1),(0,2),(1,2)); ranks={(c,i):{pt:j for j,pt in enumerate(sorted(supp[WORDS[c][i]]))} for c in range(5) for i in range(3)}
 def var(c,pair,pts):
  i,j=dims[pair]
  v,w=pts[i],pts[j]
  if v not in ranks[(c,i)] or w not in ranks[(c,j)]: raise AssertionError(('badpoint',c,pair,v,w))
  return c*243+pair*81+ranks[(c,i)][v]*9+ranks[(c,j)][w]
 n=1215; assert int(p['variable_count'])==n
 assert len(p['selected_rows'])==len(p['integer_multipliers'])==len(p['source_row_indices'])
 assert len(set(map(int,p['source_row_indices'])))==len(p['source_row_indices'])
 for row in p['selected_rows']:
  pr=row['provenance']; a,b,c=pr['triple']; ws=pr['witnesses']; assert len(ws)==3
  co={}; raw=0
  for pair,w in enumerate(ws):
   x,y,z=map(tuple,(w['x'],w['y'],w['z'])); assert midpoint(x,y,z)
   carry=((x[0]+z[0]-2*y[0])//Q,(x[1]+z[1]-2*y[1])//Q); assert list(carry)==w['carry'] and all(-1<=u<=1 for u in carry)
   cost=sum((x[i]-z[i])**2 for i in range(2)); assert cost==w['raw_cost_numerator']; raw+=cost
  assert raw==int(row['rhs_numerator'])
  co={}; X=[tuple(w['x']) for w in ws]; Y=[tuple(w['y']) for w in ws]; Z=[tuple(w['z']) for w in ws]
  for pair,w in enumerate(ws):
   for cyl,pts,sgn in ((a,X,1),(b,Y,-2),(c,Z,1)):
    j=var(cyl,pair,pts); co[j]=co.get(j,0)+sgn
  if row['coefficients']!=[[j,v] for j,v in sorted(co.items()) if v]: raise AssertionError(('coeff',row['coefficients'],[[j,v] for j,v in sorted(co.items()) if v]))
 # Replay cancellation using supplied exact multipliers; independently verify each row's own coefficient structure via endpoint pair index.
 agg={}; rhs=0
 for row,mult in zip(p['selected_rows'],p['integer_multipliers']):
  mult=int(mult); assert mult>0; rhs += mult*int(row['rhs_numerator'])
  for j,v in row['coefficients']: agg[int(j)]=agg.get(int(j),0)+mult*int(v)
 if mutate: rhs+=1
 if any(agg.values()) or rhs!=int(p['positive_contradiction_raw']) or rhs<=0: raise AssertionError(('cancel',sum(v!=0 for v in agg.values()),rhs,int(p['positive_contradiction_raw'])))
 return {'assignment':list(ass),'scope':'q6 finite certificate; selected even-q midpoint branches; raw canonical endpoint cost','union_mass_reconstructed':union_count(supp),'mass_gate_ratio':'1080/343','ordered_word_triples_in_model':125,'selected_rows':len(p['selected_rows']),'variable_count':n,'positive_contradiction_raw':str(rhs),'mutation_self_test':None,'packet_sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}
def main():
 out=[]
 for name in ASS:
  r=run(name)
  try: run(name,True)
  except AssertionError:r['mutation_self_test']='PASS'
  out.append(r)
 print(json.dumps({'verdict':'PASS_INDEPENDENT_Q6_PAIR_COORDINATE_REPLAY','runs':out},indent=2))
if __name__=='__main__':main()
