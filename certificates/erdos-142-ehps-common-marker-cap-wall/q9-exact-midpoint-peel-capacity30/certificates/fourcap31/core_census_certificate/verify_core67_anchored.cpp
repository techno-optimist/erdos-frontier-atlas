#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

static unsigned char midpoint[81][81];

static bool self_core(const int *p,int n) {
    int incoming[7]={};
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) {
        int m=midpoint[p[i]][p[j]];
        for(int k=0;k<n;k++) if(p[k]==m) { incoming[k]++; break; }
    }
    for(int i=0;i<n;i++) if(incoming[i]==0) return false;
    return true;
}

static bool peels(const int *p,int n) {
    bool alive[7]={}; int incoming[7]={};
    for(int i=0;i<n;i++) alive[i]=true;
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) {
        int m=midpoint[p[i]][p[j]];
        for(int k=0;k<n;k++) if(p[k]==m) { incoming[k]++; break; }
    }
    int queue[7],head=0,tail=0;
    for(int i=0;i<n;i++) if(incoming[i]==0) queue[tail++]=i;
    while(head<tail) {
        int v=queue[head++]; if(!alive[v]) continue; alive[v]=false;
        for(int u=0;u<n;u++) if(alive[u]&&u!=v) {
            int m=midpoint[p[v]][p[u]];
            for(int k=0;k<n;k++) if(alive[k]&&p[k]==m) {
                if(--incoming[k]==0) queue[tail++]=k;
                break;
            }
        }
    }
    for(int i=0;i<n;i++) if(alive[i]) return false;
    return true;
}

static bool minimal(const int *p,int n) {
    int sub[7];
    for(int drop=0;drop<n;drop++) {
        int z=0; for(int i=0;i<n;i++) if(i!=drop) sub[z++]=p[i];
        if(!peels(sub,n-1)) return false;
    }
    return true;
}

int main() {
    const auto started=std::chrono::steady_clock::now();
    for(int a=0;a<81;a++) for(int b=0;b<81;b++)
        midpoint[a][b]=(unsigned char)(9*((5*(a/9+b/9))%9)+(5*(a%9+b%9))%9);

    std::vector<std::string> chunk6(76);
    std::vector<uint64_t> test6(76),self6(76),min6(76);
    #pragma omp parallel for schedule(dynamic,1)
    for(int b=1;b<=76;b++) {
        int p[6]={0,b,0,0,0,0}; std::ostringstream out;
        for(p[2]=b+1;p[2]<78;p[2]++)
        for(p[3]=p[2]+1;p[3]<79;p[3]++)
        for(p[4]=p[3]+1;p[4]<80;p[4]++)
        for(p[5]=p[4]+1;p[5]<81;p[5]++) {
            test6[b-1]++;
            if(!self_core(p,6)) continue; self6[b-1]++;
            if(!minimal(p,6)) continue; min6[b-1]++;
            for(int i=0;i<6;i++) out << p[i] << (i==5?'\n':' ');
        }
        chunk6[b-1]=out.str();
    }
    uint64_t c6=0,s6=0,m6=0;
    for(int i=0;i<76;i++) { c6+=test6[i]; s6+=self6[i]; m6+=min6[i]; }

    std::vector<uint64_t> test7(75),self7(75),min7(75);
    #pragma omp parallel for schedule(dynamic,1)
    for(int b=1;b<=75;b++) {
        int p[7]={0,b,0,0,0,0,0};
        for(p[2]=b+1;p[2]<77;p[2]++)
        for(p[3]=p[2]+1;p[3]<78;p[3]++)
        for(p[4]=p[3]+1;p[4]<79;p[4]++)
        for(p[5]=p[4]+1;p[5]<80;p[5]++)
        for(p[6]=p[5]+1;p[6]<81;p[6]++) {
            test7[b-1]++;
            if(!self_core(p,7)) continue; self7[b-1]++;
            if(minimal(p,7)) min7[b-1]++;
        }
    }
    uint64_t c7=0,s7=0,m7=0;
    for(int i=0;i<75;i++) { c7+=test7[i]; s7+=self7[i]; m7+=min7[i]; }

    std::set<std::array<int,6>> expected,actual; std::array<int,6> row;
    std::ifstream ledger("minimal_core6.txt");
    while(ledger>>row[0]>>row[1]>>row[2]>>row[3]>>row[4]>>row[5])
        if(row[0]==0) expected.insert(row);
    for(const std::string &chunk:chunk6) {
        std::istringstream anchor(chunk);
        while(anchor>>row[0]>>row[1]>>row[2]>>row[3]>>row[4]>>row[5]) actual.insert(row);
    }

    if(c6!=24040016ULL||s6!=1088||m6!=216||expected!=actual||actual.size()!=216) {
        std::cerr<<"CORE6_ANCHORED_MISMATCH\n"; return 2;
    }
    if(c7!=300500200ULL||s7!=11200||m7!=0) {
        std::cerr<<"CORE7_ANCHORED_MISMATCH\n"; return 2;
    }
    const double seconds=std::chrono::duration<double>(
        std::chrono::steady_clock::now()-started).count();
    int threads=1;
    #ifdef _OPENMP
    threads=omp_get_max_threads();
    #endif
    std::cout<<"PASS_ANCHORED_CORE6 combinations="<<c6<<" self="<<s6
             <<" minimal="<<m6<<" ledger_match=true full_self="<<s6*81/6
             <<" full_minimal="<<m6*81/6<<"\n";
    std::cout<<"PASS_ANCHORED_CORE7 combinations="<<c7<<" self="<<s7
             <<" minimal="<<m7<<" full_self="<<s7*81/7
             <<" full_minimal="<<m7*81/7<<" threads="<<threads
             <<" seconds="<<seconds<<"\n";
}
