// Ford clean-room: Erdős #1109 decision search. Usage: sqc N target  -> prints FOUND set or NONE, nodes
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXV 1024
#define W (MAXV/64)
typedef struct { uint64_t w[W]; } bs;
static int nv, nw; static bs adj[MAXV]; static int lab[MAXV];
static long long nodes; static int target; static int cur[MAXV], best[MAXV]; static int found=0;
static int sqf(long x){ for(long p=2;p*p<=x;p++) if(x%(p*p)==0) return 0; return 1; }
static int popc(const bs*s){int c=0;for(int i=0;i<nw;i++)c+=__builtin_popcountll(s->w[i]);return c;}
static void expand(bs *P, int depth){
  nodes++;
  if(found) return;
  if(depth>=target){ found=1; memcpy(best,cur,sizeof(int)*depth); return; }
  // greedy colouring of P in index order (vertices pre-sorted by degree desc)
  int order[MAXV], col[MAXV], n=0;
  bs U=*P; int c=0;
  while(popc(&U)){
    c++; bs Q=U;
    for(int i=0;i<nw;i++) while(Q.w[i]){
      int b=__builtin_ctzll(Q.w[i]); int v=i*64+b;
      U.w[i]&=~(1ULL<<b); Q.w[i]&=~(1ULL<<b);
      for(int j=0;j<nw;j++) Q.w[j]&=~adj[v].w[j];
      order[n]=v; col[n]=c; n++;
    }
  }
  for(int k=n-1;k>=0;k--){
    if(depth+col[k]<target) return;
    int v=order[k];
    bs NP; for(int j=0;j<nw;j++) NP.w[j]=P->w[j]&adj[v].w[j];
    cur[depth]=v; expand(&NP,depth+1); if(found) return;
    P->w[v/64]&=~(1ULL<<(v%64));
  }
}
int main(int argc,char**argv){
  long N=atol(argv[1]); target=atoi(argv[2]);
  if(!sqf(2*N)){ printf("N %ld t %d NONE nodes 0 nv 0 (2N not squarefree)\n",N,target); return 0; }
  int raw[MAXV], m=0;
  for(long a=1;a<N;a++) if(sqf(2*a)&&sqf(a+N)){ if(m>=MAXV){fprintf(stderr,"MAXV\n");return 2;} raw[m++]=a; }
  // degrees in G_N
  int deg[MAXV]; for(int i=0;i<m;i++){deg[i]=0;for(int j=0;j<m;j++) if(i!=j&&sqf(raw[i]+raw[j])) deg[i]++;}
  int idx[MAXV]; for(int i=0;i<m;i++) idx[i]=i;
  for(int i=0;i<m;i++) for(int j=i+1;j<m;j++) if(deg[idx[j]]>deg[idx[i]]||(deg[idx[j]]==deg[idx[i]]&&raw[idx[j]]>raw[idx[i]])){int t=idx[i];idx[i]=idx[j];idx[j]=t;}
  nv=m; nw=(m+63)/64; if(nw==0) nw=1;
  for(int i=0;i<m;i++){lab[i]=raw[idx[i]]; memset(&adj[i],0,sizeof(bs));}
  for(int i=0;i<m;i++) for(int j=0;j<m;j++) if(i!=j&&sqf(lab[i]+lab[j])) adj[i].w[j/64]|=1ULL<<(j%64);
  bs P; memset(&P,0,sizeof P); for(int i=0;i<m;i++) P.w[i/64]|=1ULL<<(i%64);
  if(target<=0){ found=1; } else expand(&P,0);
  printf("N %ld t %d %s nodes %lld nv %d", N, target, found?"FOUND":"NONE", nodes, m);
  if(found){ printf(" set"); for(int i=0;i<target;i++) printf(" %d",lab[best[i]]); printf(" %ld",N);} 
  printf("\n"); return 0;
}
