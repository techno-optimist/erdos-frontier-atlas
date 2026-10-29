/* Ford clean-room search for distinct segment sums (Erdos #357; OEIS A364132 / A364153).
   Written from the OEIS definition only. No atlas code read or reused.
   Usage: ss_cleanroom MODE n N [part parts]
     MODE m: increasing n-sequence in {1..N}; MODE a: any order (distinct terms), no symmetry breaking.
   Prints FOUND s_1..s_n or NONE, plus node count. Branches at depth 2 are dealt round-robin to parts. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define W 40               /* 2560 bits: max segment sum n*N must be < 2560 */
typedef struct { uint64_t w[W]; } bs;
static int n, N, part = 0, parts = 1; static char mode;
static long long nodes = 0, deal = 0; static int seq[64];
static inline int getb(const bs *b, int i){ return (b->w[i>>6] >> (i&63)) & 1; }
static inline void setb(bs *b, int i){ b->w[i>>6] |= 1ULL << (i&63); }
static void shl(const bs *a, int k, bs *r){ int q=k>>6, s=k&63; for(int i=W-1;i>=0;i--){ uint64_t v=0; int j=i-q; if(j>=0){ v=a->w[j]<<s; if(s && j>0) v|=a->w[j-1]>>(64-s);} r->w[i]=v; } }
static int hits(const bs *a, const bs *b){ for(int i=0;i<W;i++) if(a->w[i]&b->w[i]) return 1; return 0; }
/* T: segment sums ending at last term, plus 0. D: all segment sums so far. */
static int dfs(int j, const bs *T, const bs *D){
  nodes++;
  if(j==n) return 1;
  int need = n-j, lo = (mode=='m' && j>0) ? seq[j-1]+1 : 1;
  int avail = 0; for(int v=lo; v<=N; v++) if(!getb(D,v)) avail++;
  if(avail < need) return 0;            /* each remaining term is itself a new segment sum */
  for(int x=lo; x<=N; x++){
    if(getb(D,x)) continue;
    bs S; shl(T,x,&S);
    if(hits(&S,D)) continue;
    if(j==1){ long long id = deal++; if(id % parts != part) continue; }
    bs T2=S, D2=*D; setb(&T2,0); for(int i=0;i<W;i++) D2.w[i]|=S.w[i];
    seq[j]=x;
    if(dfs(j+1,&T2,&D2)) return 1;
  }
  return 0;
}
int main(int c, char **v){
  if(c<4){ fprintf(stderr,"usage\n"); return 2; }
  mode=v[1][0]; n=atoi(v[2]); N=atoi(v[3]); if(c>=6){ part=atoi(v[4]); parts=atoi(v[5]); }
  if((long)n*N >= 64*W){ fprintf(stderr,"too big\n"); return 2; }
  bs T, D; memset(&T,0,sizeof T); memset(&D,0,sizeof D); setb(&T,0);
  int f = dfs(0,&T,&D);
  printf("%c %d %d part %d/%d ", mode, n, N, part, parts);
  if(f){ printf("FOUND"); for(int i=0;i<n;i++) printf(" %d", seq[i]); } else printf("NONE");
  printf(" nodes %lld\n", nodes); return 0;
}
