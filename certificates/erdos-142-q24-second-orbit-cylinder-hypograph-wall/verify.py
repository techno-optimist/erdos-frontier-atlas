#!/usr/bin/env python3
"""Pure-stdlib semantic replay for the compact q=24 B-orbit Farkas packet."""
import argparse, copy, hashlib, itertools, json
from pathlib import Path

Q=24; NG=2445; N=2820
DEFAULT_PACKET=Path(__file__).with_name("certificate.json")
EXPECTED_SHA256="AB7F047034CD9287ECE048CA56B78F2F1D32F2E2C2E102AE3B10AB05523A1E29"
VERDICT="PASS_Q24_D4_SECOND_ORBIT_CYLINDER_HYPOGRAPH_EXACT_FARKAS"
ROLES=("P1","P2","P3","B","K")
WORDS=(("P1","K","B"),("B","K","P1"),("P2","B","P2"),("P3","B","B"),("B","B","P3"))
ASSIGN=(7,6,7,6,7)
def tv(a,b,c,i): return NG+3*((a*5+b)*5+c)+i
def tile():
 s=set()
 for x in range(Q):
  for y in range(Q):
   sm=x+y
   if (x>=12 and 17<=sm<=28) or (x>=12 and y<=11 and 29<=sm<=34) or (x<=11 and y>=12 and 29<=sm<=34 and 4*x+2*y>=74): s.add((x,y))
 assert len(s)==163
 return s
def d4(s,k):
 out=set()
 for x,y in s:
  if k&1: x,y=23-x,y
  if k&2: x,y=x,23-y
  if k&4: x,y=y,x
  out.add((x,y))
 return out
def mass(support):
 total=0
 for n in range(1,6):
  for chosen in itertools.combinations(WORDS,n):
   p=1
   for j in range(3):
    common=set(support[chosen[0][j]])
    for w in chosen[1:]: common &= support[w[j]]
    p*=len(common)
   total += p if n%2 else -p
 return total
def expected_orbit(images,assignment):
 syms=[]
 for p in itertools.permutations(range(3)):
  for rp in itertools.permutations(ROLES):
   rho=dict(zip(ROLES,rp))
   if {tuple(rho[w[p[j]]] for j in range(3)) for w in WORDS}==set(WORDS): syms.append((p,rho))
 assert len(syms)==2
 comp={}
 for k in range(8):
  for j in range(8): comp[k,j]=next(i for i,s in enumerate(images) if s==d4(images[j],k))
 ri={r:i for i,r in enumerate(ROLES)}; orbit=set()
 for k in range(8):
  for _p,rho in syms:
   y=[None]*5
   for r in ROLES: y[ri[rho[r]]]=comp[k,assignment[ri[r]]]
   orbit.add(tuple(y))
 assert len(orbit)==8
 return sorted(map(list,orbit))
def maximum_assignments(images):
 intersections={}
 for mask in range(1,1<<8):
  chosen=[images[i] for i in range(8) if mask&(1<<i)]; common=set(chosen[0])
  for image in chosen[1:]: common &= image
  intersections[mask]=len(common)
 ri={r:i for i,r in enumerate(ROLES)}; terms=[]
 for size in range(1,6):
  for chosen in itertools.combinations(range(5),size):
   masks=[]
   for position in range(3):
    role_mask=0
    for word_index in chosen: role_mask |= 1<<ri[WORDS[word_index][position]]
    masks.append(role_mask)
   terms.append((1 if size&1 else -1,masks))
 maximum=-1; maximizers=[]
 for assignment in itertools.product(range(8),repeat=5):
  role_intersections={}
  for role_mask in range(1,1<<5):
   image_mask=0
   for role_index in range(5):
    if role_mask&(1<<role_index): image_mask |= 1<<assignment[role_index]
   role_intersections[role_mask]=intersections[image_mask]
  count=sum(sign*role_intersections[m[0]]*role_intersections[m[1]]*role_intersections[m[2]] for sign,m in terms)
  if count>maximum: maximum=count; maximizers=[assignment]
  elif count==maximum: maximizers.append(assignment)
 return maximum,sorted(map(list,maximizers))
def semantic_coeff(row,ix):
 s=row["semantic"]
 if s["kind"]=="triple-sum":
  a,b,c=s["word_indices"]; assert row["rhs_num"]==0 and s["scaled_form"]=="-t0-t1-t2 <= 0"
  return {tv(a,b,c,i):-1 for i in range(3)}
 assert s["kind"]=="local-hypograph" and s["scaled_form"]=="t-Gx-Gz+2Gy <= -raw_cost_numerator"
 a,b,c=s["word_indices"]; i=s["position"]; assert 0<=i<3
 x,y,z=map(tuple,(s["x"],s["y"],s["z"]))
 assert s["roles"]==[WORDS[a][i],WORDS[b][i],WORDS[c][i]]
 assert all((x[j]+z[j]-2*y[j])%Q==0 for j in range(2))
 carry=[(x[j]+z[j]-2*y[j])//Q for j in range(2)]
 assert carry==s["carry"] and all(v in (-1,0,1) for v in carry)
 cost=sum((x[j]-z[j])**2 for j in range(2)); assert cost==s["raw_cost_numerator"] and row["rhs_num"]==-cost
 co={}
 for j,v in ((tv(a,b,c,i),1),(ix[a,i,x],-1),(ix[c,i,z],-1),(ix[b,i,y],2)): co[j]=co.get(j,0)+v
 return {j:v for j,v in co.items() if v}
def check(d):
 assert d["format"]=="erdos142-q24-cylinder-position-hypograph-farkas-v1"
 assert d["q"]==Q and d["assignment"]==list(ASSIGN) and d["cylinders"]==["AAC","CAA","CCC","ACC","CCA"]
 assert d["union_mass_count"]==21653735 and d["finite_q_only"] is True and d["continuum_claim"] is False and d["r3_claim"] is False
 assert d["no_gauge_in_certificate_rows"] is True
 images=[d4(tile(),k) for k in range(8)]; assert len({tuple(sorted(s)) for s in images})==8
 support={r:images[6 if r=="B" else 7] for r in ROLES}; assert set(support["B"]).isdisjoint(support["P1"]) and mass(support)==21653735
 expected=[]
 for a,w in enumerate(WORDS):
  for i,r in enumerate(w): expected.extend([[a,i,list(p)] for p in sorted(support[r])])
 labels=d["g_variable_labels"]; assert labels==expected and len(labels)==NG
 ix={(a,b,tuple(p)):i for i,(a,b,p) in enumerate(labels)}
 local=d["local_rows"]; sums=d["triple_sum_rows"]; assert len(sums)==125
 seen_sums=set()
 for row in local+sums:
  co=semantic_coeff(row,ix); assert row["coefficients"]==[[j,v] for j,v in sorted(co.items())]
  if row["semantic"]["kind"]=="triple-sum": seen_sums.add(tuple(row["semantic"]["word_indices"]))
 assert seen_sums==set(itertools.product(range(5),repeat=3))
 assert d["d4_orbit"]["role_word_automorphisms"]==2 and d["d4_orbit"]["global_d4_elements"]==8 and d["d4_orbit"]["orbit_size"]==8
 orbit_a=expected_orbit(images,(7,7,7,6,7)); orbit_b=expected_orbit(images,ASSIGN)
 assert d["d4_orbit"]["assignments"]==orbit_b and d["d4_orbit"]["scope"]=="this D4/word-symmetry orbit only"
 maximum,maximizers=maximum_assignments(images)
 assert maximum==21653735 and len(maximizers)==16
 assert maximizers==sorted(orbit_a+orbit_b) and not ({tuple(x) for x in orbit_a}&{tuple(x) for x in orbit_b})
 seen=set(); bal=[0]*N; rhs=0
 for e in d["farkas_rows"]:
  kind=e["kind"]; index=e["index"]; m=int(e["multiplier"]); assert kind in ("local","sum") and m>0 and (kind,index) not in seen; seen.add((kind,index))
  rows=local if kind=="local" else sums; assert 0<=index<len(rows); row=rows[index]
  co=semantic_coeff(row,ix); rhs+=m*row["rhs_num"]
  for j,v in co.items(): bal[j]+=m*v
 assert not any(bal) and rhs<0 and -rhs==d["ray"]["positive_contradiction"]
 assert d["ray"]["support"]==len(d["farkas_rows"]) and d["ray"]["exact_nullspace_dimension"]==1
 return {"local_rows":len(local),"sum_rows":len(sums),"farkas_rows":len(seen),"positive_contradiction":str(-rhs),"maximum_mass_assignments":len(maximizers),"second_orbit_assignments":len(orbit_b),"self_test":"pass"}
def rejected(base, mutate):
 x=copy.deepcopy(base); mutate(x)
 try: check(x); raise AssertionError("planted corruption escaped")
 except AssertionError: pass
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("packet",type=Path,nargs="?",default=DEFAULT_PACKET)
 ap.add_argument("--self-test",action="store_true")
 args=ap.parse_args()
 raw=args.packet.read_bytes(); sha=hashlib.sha256(raw).hexdigest().upper()
 if args.packet.resolve()==DEFAULT_PACKET.resolve(): assert sha==EXPECTED_SHA256
 d=json.loads(raw); out=check(d)
 if args.self_test:
  rejected(d,lambda z:z["farkas_rows"][0].__setitem__("multiplier","0"))
  rejected(d,lambda z:z["local_rows"][0]["semantic"].__setitem__("carry",[9,9]))
  rejected(d,lambda z:z["local_rows"][0]["semantic"].__setitem__("raw_cost_numerator",0))
  rejected(d,lambda z:z["local_rows"][0]["semantic"]["roles"].__setitem__(0,"B"))
  rejected(d,lambda z:z["triple_sum_rows"].pop())
  rejected(d,lambda z:z.__setitem__("assignment",[7,7,7,6,7]))
  rejected(d,lambda z:z.__setitem__("union_mass_count",0))
  rejected(d,lambda z:z["d4_orbit"]["assignments"].pop())
  out["planted_corruptions"]="all rejected"
 out["certificate_sha256"]=sha
 out["erdos142_solved"]=False
 out["new_r3_bound"]=False
 out["continuum_certificate"]=False
 print(VERDICT)
 print(f"certificate_sha256 {sha}")
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
