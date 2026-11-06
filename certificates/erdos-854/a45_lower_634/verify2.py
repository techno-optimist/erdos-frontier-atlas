# independent verifier: own sieve + CRT rebuild from batch.txt; trial-division uncovered count
# Replay: python3 -I verify2.py | diff - verify2.txt
import re, math
def primes(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]:
            s[i * i :: i] = bytearray(len(s[i * i :: i]))
    return [i for i in range(n + 1) if s[i]]
P = primes(197); assert len(P) == 45 and P[-1] == 197
M = math.prod(P)
def crt(res):
    x = 0
    for p, r in zip(P, res):
        m = M // p; x = (x + (-r) % p * m * pow(m, -1, p)) % M
    return x
for line in open('batch.txt'):
    if 'WITNESS' not in line:
        continue
    t = int(re.search(r't=(\d+)', line).group(1))
    res = list(map(int, line.split('WITNESS')[1].split()))
    x = crt(res)
    seed_ok = all((x + r) % p == 0 for p, r in zip(P, res))
    uncovered = sum(1 for i in range(1, t) if all((x + i) % p for p in P))
    print(f't={t} seed_line_ok={seed_ok} uncovered={uncovered} x={x}')
