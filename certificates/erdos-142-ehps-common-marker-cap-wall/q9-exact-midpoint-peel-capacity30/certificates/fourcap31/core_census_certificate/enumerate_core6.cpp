#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

static unsigned char midpt[81][81];

static inline bool is_core(const int *s,int n) {
    uint64_t witnessed=0;
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) {
        int m=midpt[s[i]][s[j]];
        for(int k=0;k<n;k++) if(s[k]==m) { witnessed|=uint64_t(1)<<k; break; }
    }
    return witnessed==(uint64_t(1)<<n)-1;
}

static inline bool has_midpoint_core(const int *s,int n) {
    bool alive[6]={}; int incoming[6]={};
    for(int i=0;i<n;i++) alive[i]=true;
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) {
        int m=midpt[s[i]][s[j]];
        for(int k=0;k<n;k++) if(s[k]==m) { incoming[k]++; break; }
    }
    int queue[6],head=0,tail=0;
    for(int i=0;i<n;i++) if(incoming[i]==0) queue[tail++]=i;
    while(head<tail) {
        int v=queue[head++]; if(!alive[v]) continue; alive[v]=false;
        for(int u=0;u<n;u++) if(alive[u]&&u!=v) {
            int m=midpt[s[u]][s[v]];
            for(int k=0;k<n;k++) if(alive[k]&&s[k]==m) {
                if(--incoming[k]==0) queue[tail++]=k;
                break;
            }
        }
    }
    for(int i=0;i<n;i++) if(alive[i]) return true;
    return false;
}

static inline bool deletion_minimal6(const int *s) {
    int sub[5];
    for(int drop=0;drop<6;drop++) {
        int z=0; for(int i=0;i<6;i++) if(i!=drop) sub[z++]=s[i];
        if(has_midpoint_core(sub,5)) return false;
    }
    return true;
}

int main() {
    for(int a=0;a<81;a++) for(int b=0;b<81;b++)
        midpt[a][b]=(unsigned char)(9*((5*(a/9+b/9))%9)+(5*(a%9+b%9))%9);
    std::vector<std::string> chunks(76);
    std::vector<uint64_t> self_counts(76,0),minimal_counts(76,0),tested(76,0);
    #pragma omp parallel for schedule(dynamic,1)
    for(int a=0;a<=75;a++) {
        std::ostringstream out;
        int s[6]; s[0]=a;
        for(s[1]=a+1;s[1]<77;s[1]++)
        for(s[2]=s[1]+1;s[2]<78;s[2]++)
        for(s[3]=s[2]+1;s[3]<79;s[3]++)
        for(s[4]=s[3]+1;s[4]<80;s[4]++)
        for(s[5]=s[4]+1;s[5]<81;s[5]++) {
            tested[a]++;
            if(is_core(s,6)) {
                self_counts[a]++;
                if(!deletion_minimal6(s)) continue;
                minimal_counts[a]++;
                for(int i=0;i<6;i++) out << s[i] << (i==5?'\n':' ');
            }
        }
        chunks[a]=out.str();
    }
    std::ofstream out("minimal_core6.txt",std::ios::binary);
    uint64_t self_total=0,minimal_total=0,tries=0;
    for(int a=0;a<=75;a++) {
        out << chunks[a]; self_total+=self_counts[a];
        minimal_total+=minimal_counts[a]; tries+=tested[a];
    }
    out.close();
    std::cout << "COMBINATIONS " << tries << "\nSELF_CORE6 " << self_total
              << "\nDELETION_MINIMAL_CORE6 " << minimal_total << "\n";
}
