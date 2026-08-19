#!/usr/bin/env python3
"""Independent no-import replay of the q6/M7 orbit-free selector."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from pathlib import Path

Q = 6
HERE = Path(__file__).resolve().parent
BASE = {(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)}
MIRROR = {(5-x,y) for x,y in BASE}


def color(p):
    return (p[0]+p[1]) % 2


def orient(p):
    if p in BASE: return 0
    if p in MIRROR: return 1
    return None


def mass(word, residue):
    coefficient = [1]
    for j in range(6):
        tile = MIRROR if (word>>j)&1 else BASE
        counts = [sum(color(p)==e for p in tile) for e in (0,1)]
        new = [0]*(len(coefficient)+1)
        for k, value in enumerate(coefficient):
            new[k] += value*counts[0]; new[k+1] += value*counts[1]
        coefficient = new
    return coefficient[residue]


def derive_local_channels():
    channels = {bits:set() for bits in product((0,1), repeat=3)}
    semantic_rows = 0
    for dx,dy in product((0,2,4), repeat=2):
        for p in BASE|MIRROR:
            orbit = tuple(((p[0]+k*dx)%6,(p[1]+k*dy)%6) for k in range(3))
            labels = tuple(orient(x) for x in orbit)
            if None in labels: continue
            channels[labels].add((color(p), (dx,dy)!=(0,0)))
            semantic_rows += 1
    assert semantic_rows == 42
    return channels


def has_orbit(words, residue, channels):
    possible = {(0,False)}
    for coordinate in range(6):
        labels = tuple((w>>coordinate)&1 for w in words)
        possible = {(s+p, active or nz) for s,active in possible for p,nz in channels[labels]}
    return (residue,True) in possible


def main():
    raw = HERE.joinpath("selector.cells").read_text(encoding="ascii").splitlines()
    cells = [tuple(map(int,line.split(":"))) for line in raw if line]
    assert len(cells)==len(set(cells))==28
    channels = derive_local_channels()
    residue_counts=[]; tested=0; witnesses=[]
    for r in range(7):
        words = [w for w,rr in cells if rr==r]
        residue_counts.append(len(words))
        for triple in product(words, repeat=3):
            tested += 1
            if has_orbit(triple,r,channels): witnesses.append((*triple,r))
    assert not witnesses
    total=sum(mass(w,r) for w,r in cells)
    normalized=Fraction(total,6**12); benchmark=Fraction(7,24)**6
    assert total==1_405_512 and normalized==Fraction(241,373248)
    assert normalized-benchmark==Fraction(5743,191102976)>0
    print("PASS_INDEPENDENT_Q6_M7_ORBIT_FREE_SELECTOR")
    print(json.dumps({"cells":len(cells),"residue_counts":residue_counts,
                      "local_semantic_rows":42,"ordered_triples_tested":tested,
                      "order3_orbits":len(witnesses),"box_count":total,
                      "mass":str(normalized),"exact_margin":str(normalized-benchmark)},sort_keys=True))


if __name__=="__main__": main()
