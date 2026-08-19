#include <algorithm>
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

static bool is_self_core(const int *points,int n) {
    int incoming[8]={};
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) {
        int middle=midpoint[points[i]][points[j]];
        for(int k=0;k<n;k++) if(points[k]==middle) { incoming[k]++; break; }
    }
    for(int i=0;i<n;i++) if(incoming[i]==0) return false;
    return true;
}

static bool strips_to_empty(const int *points,int n) {
    bool alive[8]={}; int incoming[8]={};
    for(int i=0;i<n;i++) alive[i]=true;
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) {
        int middle=midpoint[points[i]][points[j]];
        for(int k=0;k<n;k++) if(points[k]==middle) { incoming[k]++; break; }
    }
    int queue[8],head=0,tail=0;
    for(int i=0;i<n;i++) if(incoming[i]==0) queue[tail++]=i;
    while(head<tail) {
        int removed=queue[head++];
        if(!alive[removed]) continue;
        alive[removed]=false;
        for(int other=0;other<n;other++) if(alive[other]&&other!=removed) {
            int middle=midpoint[points[removed]][points[other]];
            for(int k=0;k<n;k++) if(alive[k]&&points[k]==middle) {
                if(--incoming[k]==0) queue[tail++]=k;
                break;
            }
        }
    }
    for(int i=0;i<n;i++) if(alive[i]) return false;
    return true;
}

static bool deletion_minimal(const int *points) {
    int subset[7];
    for(int drop=0;drop<8;drop++) {
        int at=0;
        for(int i=0;i<8;i++) if(i!=drop) subset[at++]=points[i];
        if(!strips_to_empty(subset,7)) return false;
    }
    return true;
}

int main() {
    const auto started=std::chrono::steady_clock::now();
    for(int a=0;a<81;a++) for(int b=0;b<81;b++)
        midpoint[a][b]=(unsigned char)(9*((5*(a/9+b/9))%9)+(5*(a%9+b%9))%9);

    std::vector<std::string> chunks(75);
    std::vector<uint64_t> tested(75,0),self_count(75,0),minimal_count(75,0);
    #pragma omp parallel for schedule(dynamic,1)
    for(int b=1;b<=75;b++) {
        int p[8]; p[0]=0; p[1]=b;
        std::ostringstream out;
        for(p[2]=b+1;p[2]<76;p[2]++)
        for(p[3]=p[2]+1;p[3]<77;p[3]++)
        for(p[4]=p[3]+1;p[4]<78;p[4]++)
        for(p[5]=p[4]+1;p[5]<79;p[5]++)
        for(p[6]=p[5]+1;p[6]<80;p[6]++)
        for(p[7]=p[6]+1;p[7]<81;p[7]++) {
            tested[b-1]++;
            if(!is_self_core(p,8)) continue;
            self_count[b-1]++;
            if(!deletion_minimal(p)) continue;
            minimal_count[b-1]++;
            for(int i=0;i<8;i++) out << p[i] << (i==7?'\n':' ');
        }
        chunks[b-1]=out.str();
    }
    uint64_t combinations=0,self_total=0,minimal_total=0;
    for(int i=0;i<75;i++) {
        combinations+=tested[i];
        self_total+=self_count[i]; minimal_total+=minimal_count[i];
    }

    std::ifstream ledger("minimal_core8.txt");
    std::set<std::array<int,8>> expected,actual;
    std::array<int,8> row;
    while(ledger >> row[0] >> row[1] >> row[2] >> row[3] >> row[4]
                 >> row[5] >> row[6] >> row[7]) if(row[0]==0) expected.insert(row);
    for(const std::string &chunk:chunks) {
        std::istringstream anchor(chunk);
        while(anchor >> row[0] >> row[1] >> row[2] >> row[3] >> row[4]
                     >> row[5] >> row[6] >> row[7]) actual.insert(row);
    }
    if(expected!=actual || actual.size()!=1728) {
        std::cerr << "ANCHORED_LEDGER_MISMATCH\n"; return 2;
    }
    if(combinations!=3176716400ULL || self_total!=145832 || minimal_total!=1728) {
        std::cerr << "ANCHORED_CENSUS_MISMATCH\n"; return 2;
    }
    const double seconds=std::chrono::duration<double>(
        std::chrono::steady_clock::now()-started).count();
    int threads=1;
    #ifdef _OPENMP
    threads=omp_get_max_threads();
    #endif
    std::cout << "PASS_ANCHORED_CORE8 combinations=" << combinations
              << " self=" << self_total << " minimal=" << minimal_total
              << " ledger_match=true threads=" << threads
              << " seconds=" << seconds << "\n";
    std::cout << "DOUBLE_COUNT full_self=" << (self_total*81/8)
              << " full_minimal=" << (minimal_total*81/8) << "\n";
}
