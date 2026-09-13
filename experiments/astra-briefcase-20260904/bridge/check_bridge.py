#!/usr/bin/env python3
"""Exact P687 -> P854 endpoint-constrained CRT bridge, stdlib only.
Independent oracles: period gcd scan; residue-assignment union DP;
and inclusion-exclusion for smaller gaps. No repo writes.
"""
from collections import Counter
from itertools import combinations
from math import gcd, prod
import json
from pathlib import Path

PRIMES = [2, 3, 5, 7, 11, 13]

def wheel(primes):
    P = prod(primes)
    units = [a for a in range(1, P) if gcd(a, P) == 1]
    gaps = [b-a for a,b in zip(units, units[1:]+[P+1])]
    return P, units, gaps

def constrained_count(primes, t, endpoints=True):
    """Each tuple of residues equals one start mod P by CRT."""
    target = (1 << (t-1))-1
    states = {0: 1}
    for p in primes:
        masks = []
        for r in range(p):
            if endpoints and r in {0, t % p}:
                continue
            mask = sum(1 << (i-1) for i in range(1,t) if i % p == r)
            masks.append(mask)
        nxt = Counter()
        for s,c in states.items():
            for mask in masks:
                nxt[s|mask] += c
        states = nxt
    return states.get(target,0)

def inclusion_exclusion(primes,t):
    ans = 0
    interior = range(1,t)
    for size in range(t):
        for S in combinations(interior,size):
            value = prod(p-len({x%p for x in (0,t)+S}) for p in primes)
            ans += (-1)**size * value
    return ans

def verify_start(primes,t,a):
    P = prod(primes)
    return (gcd(a,P)==gcd(a+t,P)==1
            and all(gcd(a+i,P)>1 for i in range(1,t)))

def main():
    rows=[]
    summaries=[]
    ie_checks=0
    recurrence_checks=0
    for k in range(2,7):
        primes=PRIMES[:k]
        P,units,gaps=wheel(primes)
        hist=Counter(gaps)
        for t in range(1,31):
            observed=hist[t]
            counted=constrained_count(primes,t)
            assert observed==counted,(primes,t,observed,counted)
            if t<=12:
                ie=inclusion_exclusion(primes,t)
                assert ie==observed
                ie_checks+=1
            rows.append({'k':k,'P':P,'t':t,'period_count':observed,'crt_cover_count':counted})
        missing=next(t for t in range(2,32,2) if not hist[t])
        summaries.append({'k':k,'P':P,'max_gap':max(hist),'first_missing_even':missing,'gap_counts':dict(sorted(hist.items()))})
        if k<6:
            q=PRIMES[k]
            newhist=Counter(wheel(PRIMES[:k+1])[2])
            # If max old gap < 2q, deletions cannot be adjacent:
            # exactly q-2 copies survive, plus one merge per adjacent pair.
            assert max(gaps)<2*q
            merged=Counter(a+b for a,b in zip(gaps,gaps[1:]+gaps[:1]))
            for t in set(hist)|set(merged)|set(newhist):
                assert newhist[t] == (q-2)*hist[t]+merged[t]
                recurrence_checks+=1
    primes=PRIMES
    P,units,gaps=wheel(primes)
    a=next(a for a,d in zip(units,gaps) if d==22)
    assert verify_start(primes,22,a)
    assert not verify_start(primes,20,a) # actual negative control, same gate
    assert constrained_count(primes,20)==0
    assert constrained_count(primes,20,endpoints=False)>0
    report={
        'crt_vs_period_cells':len(rows), 'inclusion_exclusion_cells':ie_checks,
        'wheel_recurrence_coefficients':recurrence_checks,
        'tables':summaries,
        'gap22_witness':{'a':a,'b':a+22,'residues':{p:(-a)%p for p in primes},
                         'interior_gcds':[gcd(a+i,P) for i in range(1,22)]},
        'obstruction_t20':{'endpoint_constrained_count':constrained_count(primes,20),
                           'unrestricted_cover_count':constrained_count(primes,20,False)},
        'negative_control_rejected':True,
        'scope':'Periodic gaps, including wrap gap 2. No asymptotic or novelty claim.',
        'checks':rows,
    }
    output=Path(__file__).with_name('checks.json')
    # JSON roundtrip normalizes integer dictionary keys to their stored form.
    expected=json.loads(json.dumps(report))
    assert json.loads(output.read_text())==expected, 'receipt differs from recomputation'
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
    print('PASS: independent exact oracles and planted endpoint mutation')

if __name__=='__main__':
    main()
