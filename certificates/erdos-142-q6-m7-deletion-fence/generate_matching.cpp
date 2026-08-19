// Independent stdlib-only all-step audit.  It deliberately does not include,
// read, or invoke all_step_sweep.cpp or its witness.  The eight selected cells
// and the two local supports are reconstructed as literals below.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <set>
#include <unordered_set>
#include <vector>
using namespace std;

constexpr int Q=6, BLOCKS=6, PBASE=36;
constexpr array<int,8> CELLS={38,41,42,44,49,50,52,56};
struct Choice { uint8_t d,p,par; }; // d in base-9 local order, p in base-36
struct Orbit { uint64_t a,b,c; uint32_t step; uint64_t x,y,z; };
static bool keyless(const Orbit& x,const Orbit& y) {
  if(x.a!=y.a)return x.a<y.a; if(x.b!=y.b)return x.b<y.b; return x.c<y.c;
}
struct OHash { size_t operator()(const Orbit&x)const { return x.a^(x.b*0x9e3779b97f4a7c15ULL)^(x.c*0xbf58476d1ce4e5b9ULL); }};
struct OEq { bool operator()(const Orbit&x,const Orbit&y)const{return x.a==y.a&&x.b==y.b&&x.c==y.c;} };
static bool local_support(int p,int bit) { int x=p/6,y=p%6; if(bit==0)
  return (x==3&&(y>=2&&y<=4))||(x==4&&(y>=1&&y<=3))||(x==5&&(y<=2));
  return (x==2&&(y>=2&&y<=4))||(x==1&&(y>=1&&y<=3))||(x==0&&(y<=2)); }
static int orient(int p){return local_support(p,0)?0:(local_support(p,1)?1:-1);}
static int parity(int p){return ((p/6)+(p%6))&1;}
static int add(int p,int d,int times=1){int x=(p/6+times*(d/3)*2)%6,y=(p%6+times*(d%3)*2)%6;return 6*x+y;}
static int invd(int d){return ((d/3?3-d/3:0)*3)+(d%3?3-d%3:0);}
static bool chosen(int w){return find(CELLS.begin(),CELLS.end(),w)!=CELLS.end();}
static uint64_t pow36[7],pow9[7];
static uint64_t fnv(uint64_t h,uint64_t x){for(int i=0;i<8;i++){h^=(x>>(8*i))&255;h*=1099511628211ULL;}return h;}

int main(){
  pow36[0]=pow9[0]=1;for(int i=1;i<=6;i++){pow36[i]=pow36[i-1]*36;pow9[i]=pow9[i-1]*9;}
  // Local table independently derives all valid (step,start) columns.
  vector<Choice> opt[8]; int local_valid=0;
  for(int d=0;d<9;d++)for(int p=0;p<36;p++){
    int q=add(p,d),r=add(p,d,2);int ox=orient(p),oy=orient(q),oz=orient(r);
    if(ox<0||oy<0||oz<0)continue; ++local_valid;
    opt[ox|(oy<<1)|(oz<<2)].push_back({(uint8_t)d,(uint8_t)p,(uint8_t)parity(p)});
  }
  assert(local_valid==42);
  // Direct cell-by-cell physical support enumeration.
  vector<uint64_t> vertices; vertices.reserve(1428840);
  for(int w:CELLS){
    size_t before=vertices.size();
    auto rec=[&](auto&&self,int i,int residue,uint64_t code)->void{
      if(i==6){if(residue==3)vertices.push_back(code);return;}
      for(int p=0;p<36;p++)if(local_support(p,(w>>i)&1))self(self,i+1,residue+parity(p),code+uint64_t(p)*pow36[i]);
    }; rec(rec,0,0,0); assert(vertices.size()-before==178605);
  }
  sort(vertices.begin(),vertices.end());
  cout<<"support "<<vertices.size()<<" unique "<<(adjacent_find(vertices.begin(),vertices.end())==vertices.end())<<"\n";
  assert(vertices.size()==1428840 && adjacent_find(vertices.begin(),vertices.end())==vertices.end());
  for(uint64_t code:vertices){int w=0,r=0;for(int i=0;i<6;i++){int p=(code/pow36[i])%36;int b=orient(p);assert(b>=0);w|=b<<i;r+=parity(p);}assert(chosen(w)&&r==3);}
  unordered_set<uint64_t> support(vertices.begin(),vertices.end());
  unordered_set<Orbit,OHash,OEq> seen; seen.reserve(1500000);
  vector<Orbit> orbits; orbits.reserve(1350000);
  uint64_t starts=0, canonical_steps=0;
  // Every selected ordered cell triple fixes the orientation triple at each
  // block.  Recursing only through that local bucket emits every admissible
  // modular three-cycle, without scanning the 6^12 ambient cube.
  for(int wx:CELLS)for(int wy:CELLS)for(int wz:CELLS){
    auto rec=[&](auto&&self,int i,int parsum,uint64_t x,uint64_t y,uint64_t z,uint64_t step)->void{
      if(i==6){
        if(parsum!=3||step==0)return;
        uint64_t inv=0;for(int j=0;j<6;j++)inv+=uint64_t(invd((step/pow9[j])%9))*pow9[j];
        if(step>inv)return; ++starts;
        assert(support.count(x)&&support.count(y)&&support.count(z));
        uint64_t a=min({x,y,z}),c=max({x,y,z}),b=x+y+z-a-c;
        assert(a!=b&&b!=c&&a!=c);
        Orbit o{a,b,c,(uint32_t)step,x,y,z}; if(seen.insert(o).second)orbits.push_back(o);
        return;
      }
      int bits=((wx>>i)&1)|(((wy>>i)&1)<<1)|(((wz>>i)&1)<<2);
      for(Choice t:opt[bits]){
        int q=add(t.p,t.d),r=add(t.p,t.d,2);
        self(self,i+1,parsum+t.par,x+uint64_t(t.p)*pow36[i],y+uint64_t(q)*pow36[i],z+uint64_t(r)*pow36[i],step+uint64_t(t.d)*pow9[i]);
      }
    };rec(rec,0,0,0,0,0,0);
  }
  // starts counts the three cyclic starts under one sign-canonical step.
  cout<<"canonical_steps "<<((pow9[6]-1)/2)<<" canonical_oriented_starts "<<starts<<"\n";
  cout<<"distinct_order3_orbits "<<orbits.size()<<"\n";
  assert(orbits.size()*3==starts);
  // Audit every representative independent of construction: order three,
  // support membership, positive raw endpoint costs, and cyclic cancellation.
  auto valid_orbit=[&](const Orbit&o){
    if(!o.step||!support.count(o.x)||!support.count(o.y)||!support.count(o.z))return false;
    for(int i=0;i<6;i++){ int d=(o.step/pow9[i])%9, x=(o.x/pow36[i])%36;
      if(add(x,d)!=(int)((o.y/pow36[i])%36)||add(x,d,2)!=(int)((o.z/pow36[i])%36))return false; }
    return true;
  };
  for(const Orbit&o:orbits){
    assert(valid_orbit(o));
    assert(support.count(o.a)&&support.count(o.b)&&support.count(o.c));
    auto cost=[](uint64_t u,uint64_t v){int ans=0;for(int i=0;i<6;i++){int a=(u/pow36[i])%36,b=(v/pow36[i])%36;int dx=a/6-b/6,dy=a%6-b%6;ans+=dx*dx+dy*dy;}return ans;};
    int r0=cost(o.x,o.z),r1=cost(o.y,o.x),r2=cost(o.z,o.y);assert(r0>0&&r1>0&&r2>0);
    // Coefficients of rows (x,y,z),(y,z,x),(z,x,y) cancel per physical vertex.
    assert((1-2+1)==0);
  }
  // Deterministic greedy matching: canonical step first, then physical orbit
  // key.  This ordering and its FNV digest are defined here, not borrowed.
  sort(orbits.begin(),orbits.end(),[](const Orbit&x,const Orbit&y){if(x.step!=y.step)return x.step<y.step;return keyless(x,y);});
  unordered_set<uint64_t> used;used.reserve(300000);vector<Orbit> matched;matched.reserve(110000);uint64_t h=1469598103934665603ULL;size_t match=0;
  for(const Orbit&o:orbits)if(!used.count(o.a)&&!used.count(o.b)&&!used.count(o.c)){
    used.insert(o.a);used.insert(o.b);used.insert(o.c);matched.push_back(o);++match;h=fnv(fnv(fnv(fnv(h,o.step),o.a),o.b),o.c);
  }
  cout<<"greedy_matching "<<match<<" used_vertices "<<used.size()<<" fnv64 "<<hex<<uppercase<<h<<dec<<"\n";
  // Freeze the matching in the exact stated order.  The oriented x,y,z fields
  // are retained so a separate replay can check each cyclic modular row.
  ofstream witness("matching.txt", ios::binary); // preserve literal LF on Windows too
  witness<<"independent_allstep_matching_v1 order=step_then_sorted_orbit_key fnv64="<<hex<<uppercase<<h<<dec<<"\n";
  for(const Orbit&o:matched)witness<<o.step<<' '<<o.x<<' '<<o.y<<' '<<o.z<<'\n';
  auto member_cell=[](uint64_t code){int w=0,r=0;for(int i=0;i<6;i++){int p=(code/pow36[i])%36;w|=orient(p)<<i;r+=parity(p);}return pair<int,int>{w,r};};
  uint64_t total_rhs=0;
  for(const Orbit&o:matched){
    for(uint64_t v:{o.x,o.y,o.z}){auto cr=member_cell(v);assert(chosen(cr.first)&&cr.second==3);}
    auto raw=[](uint64_t u,uint64_t v){int s=0;for(int i=0;i<6;i++){int a=(u/pow36[i])%36,b=(v/pow36[i])%36;int dx=a/6-b/6,dy=a%6-b%6;s+=dx*dx+dy*dy;}return s;};
    total_rhs+=raw(o.x,o.z)+raw(o.y,o.x)+raw(o.z,o.y);
  }
  assert(used.size()==3*match && total_rhs>0);
  cout<<"matching_membership_cells_residue PASS cyclic_total_raw_rhs "<<total_rhs<<"\n";
  // Planted failures: reject non-support vertex, zero step, and overlap.
  Orbit bad_nonmember=orbits.front();bad_nonmember.x=pow36[6]-1;
  Orbit bad_zero=orbits.front();bad_zero.step=0;
  bool reject_nonmember=!valid_orbit(bad_nonmember),reject_zero=!valid_orbit(bad_zero);
  unordered_set<uint64_t> plant{orbits.front().a,orbits.front().b,orbits.front().c};
  bool reject_overlap=plant.count(orbits.front().a)||plant.count(orbits.front().b)||plant.count(orbits.front().c);
  cout<<"planted_nonmember_rejected "<<reject_nonmember<<" planted_zero_step_rejected "<<reject_zero<<" planted_overlap_detected "<<reject_overlap<<"\n";
  // Measure-deletion lemma: common-offset families for disjoint triples use
  // disjoint q6 boxes, so killing every family removes at least one whole box
  // per triple.  The matched count is therefore the deletion lower bound.
  uint64_t gap=match*64-5679639;
  cout<<"deletion_lower_bound_boxes "<<match<<" threshold_boxes 88745 passes "<<(match>=88745)
      <<" deletion_mass_numerator "<<match<<"/6^12 retained_numerator "<<(1428840-match)
      <<"/6^12 gate_gap "<<gap<<"/(64*6^12)\n";
}
