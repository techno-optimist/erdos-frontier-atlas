#include <stdio.h>
#include <stdlib.h>
#include <math.h>
int P[45],np=0;
int main(int argc,char**argv){int t=atoi(argv[1]);long iters=atol(argv[2]);unsigned seed=atoi(argv[3]);srand(seed);
for(int n=2;n<=197;n++){int q=1;for(int d=2;d*d<=n;d++)if(n%d==0)q=0;if(q)P[np++]=n;}
int r[45];int cov[700]={0};
FILE*sf=argc>4?fopen(argv[4],"r"):0;for(int k=0;k<np;k++){int p=P[k];if(sf){fscanf(sf,"%d",&r[k]);if(r[k]==0||r[k]==t%p)do{r[k]=rand()%p;}while(r[k]==0||r[k]==t%p);}else do{r[k]=rand()%p;}while(r[k]==0||r[k]==t%p);for(int i=r[k];i<=t;i+=p)cov[i]++;}
int cost=0;for(int i=1;i<t;i++)if(!cov[i])cost++;int best=cost;double T=argc>5?atof(argv[5]):2.0;double T0=T;
for(long it=0;it<iters;it++){
 /* pick uncovered interior pos */
 int i;if(cost==0)break; do{i=1+rand()%(t-1);}while(cov[i]);
 int k=rand()%np,p=P[k],nr=i%p;if(nr==r[k]||nr==0||nr==t%p)continue;
 int d=0;for(int j=r[k];j<=t;j+=p)if(j>0&&j<t&&cov[j]==1)d++;for(int j=nr;j<=t;j+=p)if(j>0&&j<t&&cov[j]==0)d--;
 /* careful overlap: positions in both classes impossible since nr!=r */
 if(d<=0||exp(-d/T)>(double)rand()/RAND_MAX){for(int j=r[k];j<=t;j+=p)cov[j]--;for(int j=nr;j<=t;j+=p)cov[j]++;r[k]=nr;cost+=d;if(cost<best)best=cost;}
 if(it%100000==0){T*=0.995;if(T<0.1)T=T0;}
}
printf("t=%d seed=%u best=%d final=%d",t,seed,best,cost);if(cost==0){printf(" WITNESS");for(int k=0;k<np;k++)printf(" %d",r[k]);}printf("\n");}
