/* Complete 0-1 base-3 search for Erdős #376 / A030979.
 * Usage: search_base3 [max_digits] [mask_start] [mask_end]
 * Mask range is half-open [start, end). Defaults: start=0, end=2^D.
 * Not a solution of #376.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int ok57(uint64_t n) {
    uint64_t x = n;
    while (x) {
        if (x % 5 > 2) return 0;
        x /= 5;
    }
    x = n;
    while (x) {
        if (x % 7 > 3) return 0;
        x /= 7;
    }
    return 1;
}

int main(int argc, char **argv) {
    int D = 24;
    if (argc > 1) D = atoi(argv[1]);
    if (D < 0 || D > 63) return 2;
    uint64_t pow3[64];
    pow3[0] = 1;
    for (int i = 1; i < D; i++) {
        pow3[i] = pow3[i - 1] * 3ULL;
        if (pow3[i] / 3ULL != pow3[i - 1]) return 3; /* overflow */
    }
    uint64_t limit = (D == 0) ? 1ULL : (1ULL << D);
    uint64_t start = 0;
    uint64_t end = limit;
    if (argc > 2) start = strtoull(argv[2], NULL, 10);
    if (argc > 3) end = strtoull(argv[3], NULL, 10);
    if (start > end) return 4;
    if (end > limit) end = limit;
    for (uint64_t mask = start; mask < end; mask++) {
        uint64_t n = 0, m = mask;
        int i = 0;
        while (m) {
            if (m & 1ULL) n += pow3[i];
            m >>= 1;
            i++;
        }
        if (ok57(n)) printf("%llu\n", (unsigned long long)n);
    }
    return 0;
}
