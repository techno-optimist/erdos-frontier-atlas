#!/usr/bin/env python3
"""Exact replay of the q6/M7 candidate-22 unit-k8 deletion fence."""

from __future__ import annotations

import argparse
import copy
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
Q = 6
BASE = frozenset({(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)})
REFLECTED = frozenset((5-x,y) for x,y in BASE)
LOCAL_SUPPORT = BASE | REFLECTED
EXPECTED_CANDIDATE = (
    (7,0),(25,0),(45,0),(49,0),(62,0),(27,1),(45,1),(54,1),
    (7,2),(56,2),(30,3),(33,3),(21,4),(42,4),(9,5),(20,5),
    (34,5),(4,6),(19,6),(26,6),(41,6),(48,6),
)
EXPECTED_TEMPLATE = ((2,3),(5,6),(5,7),(6,7),(0,1),(2,4),(3,4),(0,1))
EXPECTED_CELLS = (
    ((33,3),(33,3),(49,0),(45,0),(45,0),(49,0),(45,0),(49,0)),
    ((45,1),(45,1),(26,6),(19,6),(26,6),(26,6),(19,6),(19,6)),
    ((30,3),(30,3),(34,5),(20,5),(34,5),(34,5),(20,5),(20,5)),
)
EXPECTED_COSTS = (
    (24,36,24,36,12,48,24,12),
    (20,20,28,16,8,16,28,8),
    (28,52,44,32,16,32,68,16),
)
EXPECTED_TOTALS = (216,144,288)
EXPECTED_SUPPORTS = (
    frozenset({(33,3),(45,0),(49,0)}),
    frozenset({(45,1),(19,6),(26,6)}),
    frozenset({(30,3),(20,5),(34,5)}),
)


def parse_candidate():
    cells = tuple(
        tuple(map(int,line.split(":")))
        for line in (HERE/"candidate.cells").read_text(encoding="ascii").splitlines()
        if line.strip()
    )
    assert cells == EXPECTED_CANDIDATE and len(set(cells)) == 22
    return cells


def parity(point):
    return (point[0]+point[1]) & 1


def orientation(point):
    if point in BASE:
        return 0
    if point in REFLECTED:
        return 1
    raise AssertionError("point outside the local support")


def physical_cell(vertex):
    return (
        sum(orientation(point) << i for i,point in enumerate(vertex)),
        sum(parity(point) for point in vertex),
    )


def cell_mass(word,residue):
    polynomial = [1]
    for i in range(6):
        even,odd = (3,6) if ((word>>i)&1) == 0 else (6,3)
        nxt = [0]*(len(polynomial)+1)
        for j,value in enumerate(polynomial):
            nxt[j] += even*value
            nxt[j+1] += odd*value
        polynomial = nxt
    return polynomial[residue]


def midpoint_carry(left,right,center):
    result = []
    for x,z,y in zip(left,right,center):
        delta = (x[0]+z[0]-2*y[0],x[1]+z[1]-2*y[1])
        assert delta[0] % Q == delta[1] % Q == 0
        result.append((delta[0]//Q,delta[1]//Q))
    return tuple(result)


def raw_cost(left,right):
    return sum((x[d]-z[d])**2 for x,z in zip(left,right) for d in range(2))


def load_packet():
    return json.loads((HERE/"witnesses.json").read_text(encoding="ascii"))


def check_hashes():
    constants=json.loads((HERE/"constants.json").read_text(encoding="utf-8"))
    assert constants["scope"]=={
        "finite_q":6,
        "arbitrary_physical_potential":True,
        "strict_common_offset_torus":True,
        "whole_cell_subcollections_only":True,
        "ordinary_euclidean_claim":False,
        "erdos142_solved":False,
        "new_r3_bound":False,
    }
    assert constants["candidate_mass_boxes"]==1_370_520
    assert constants["gate_boxes"]=="85766121/64"
    assert constants["packet_raw_totals"]==[216,144,288]
    assert constants["packet_normalized_totals"]==["6","4","8"]
    assert constants["disjoint_minimum_deletions"]==[5_832,5_832,69_984]
    assert constants["minimum_deleted_mass"]==81_648
    assert constants["maximum_packet_free_subset_mass"]==1_288_872
    assert constants["maximum_minus_gate_numerator"]==-3_278_313
    for name,expected in constants["sha256"].items():
        actual=hashlib.sha256((HERE/name).read_bytes()).hexdigest().upper()
        assert actual==expected,(name,actual,expected)


def packet_audit(packet, candidate=EXPECTED_CANDIDATE, delta=Fraction(1,12)):
    assert int(packet["q"]) == Q
    rows = tuple(tuple(map(int,row)) for row in packet["template"])
    assert rows == EXPECTED_TEMPLATE
    assert Counter(label for row in rows for label in row) == Counter({i:2 for i in range(8)})
    assert Fraction(0) < delta < Fraction(1,Q)

    reports = []
    supports = []
    for wi,witness in enumerate(packet["witnesses"]):
        vertices = tuple(tuple(tuple(map(int,p)) for p in vertex) for vertex in witness["vertices"])
        assert len(vertices) == 8 and len(set(vertices)) == 8
        assert all(len(vertex) == 6 for vertex in vertices)
        assert all(point in LOCAL_SUPPORT for vertex in vertices for point in vertex)
        cells = tuple(physical_cell(vertex) for vertex in vertices)
        assert cells == EXPECTED_CELLS[wi]
        assert all(cell in set(candidate) for cell in cells)

        coefficients = [0]*8
        carries = []
        costs = []
        for center,(left,right) in enumerate(rows):
            coefficients[left] += 1
            coefficients[right] += 1
            coefficients[center] -= 2
            carry = midpoint_carry(vertices[left],vertices[right],vertices[center])
            cost = raw_cost(vertices[left],vertices[right])
            assert cost > 0
            carries.append(carry)
            costs.append(cost)
        assert coefficients == [0]*8
        assert tuple(costs) == EXPECTED_COSTS[wi]
        assert sum(costs) == EXPECTED_TOTALS[wi]
        assert any(kappa != (0,0) for carry in carries for kappa in carry)

        # Common strict-interior lift: digit/q + delta remains in the same
        # half-open q6 box.  The common delta cancels from each midpoint row
        # and every endpoint difference, so carries and costs are unchanged.
        lifted = tuple(
            tuple(tuple(Fraction(d,Q)+delta for d in point) for point in vertex)
            for vertex in vertices
        )
        for vertex,lifted_vertex in zip(vertices,lifted):
            for point,lifted_point in zip(vertex,lifted_vertex):
                for digit,value in zip(point,lifted_point):
                    assert Fraction(digit,Q) < value < Fraction(digit+1,Q)
        for center,(left,right) in enumerate(rows):
            for x,z,y,kappa in zip(lifted[left],lifted[right],lifted[center],carries[center]):
                assert tuple(x[d]+z[d]-2*y[d] for d in range(2)) == tuple(Fraction(k) for k in kappa)
            lifted_cost = sum(
                (x[d]-z[d])**2
                for x,z in zip(lifted[left],lifted[right])
                for d in range(2)
            )
            assert lifted_cost == Fraction(costs[center],Q*Q)

        support = frozenset(cells)
        assert support == EXPECTED_SUPPORTS[wi]
        supports.append(support)
        reports.append({
            "name": witness["name"],
            "cells": [list(cell) for cell in cells],
            "support": [list(cell) for cell in sorted(support)],
            "coefficient_vector": coefficients,
            "raw_costs": costs,
            "raw_total": sum(costs),
            "normalized_total": str(Fraction(sum(costs),Q*Q)),
            "carries": carries,
        })

    assert tuple(supports) == EXPECTED_SUPPORTS
    assert all(not supports[i] & supports[j] for i in range(3) for j in range(i))
    return tuple(supports),reports


def deletion_fence(supports, candidate=EXPECTED_CANDIDATE, gate=Fraction(7,24)**6):
    assert BASE.isdisjoint(REFLECTED) and len(BASE) == len(REFLECTED) == 9
    assert tuple((sum(parity(p)==0 for p in s),sum(parity(p)==1 for p in s)) for s in (BASE,REFLECTED)) == ((3,6),(6,3))
    total = sum(cell_mass(*cell) for cell in candidate)
    assert total == 1_370_520
    assert Fraction(total,Q**12) == Fraction(235,373248)
    assert gate == Fraction(7,24)**6
    gate_boxes = gate*Q**12
    assert gate_boxes == Fraction(85_766_121,64)
    minima = tuple(min(cell_mass(*cell) for cell in support) for support in supports)
    assert minima == (5_832,5_832,69_984)
    minimum_deleted = sum(minima)
    assert minimum_deleted == 81_648
    maximum = total-minimum_deleted
    assert maximum == 1_288_872
    assert Fraction(maximum,Q**12) == Fraction(221,373248)
    assert maximum*64-85_766_121 == -3_278_313 < 0
    return {
        "candidate_mass_boxes": total,
        "candidate_normalized_mass": str(Fraction(total,Q**12)),
        "gate": str(gate),
        "candidate_gate_excess": str(Fraction(total,Q**12)-gate),
        "disjoint_minimum_deletions": list(minima),
        "minimum_deleted_mass": minimum_deleted,
        "maximum_packet_free_subset_mass": maximum,
        "maximum_packet_free_normalized_mass": str(Fraction(maximum,Q**12)),
        "maximum_minus_gate": str(Fraction(maximum,Q**12)-gate),
        "maximum_minus_gate_numerator": maximum*64-85_766_121,
    }


def audit(packet=None,candidate=None,delta=Fraction(1,12),gate=Fraction(7,24)**6):
    packet = load_packet() if packet is None else packet
    candidate = parse_candidate() if candidate is None else candidate
    supports,reports = packet_audit(packet,candidate,delta)
    return {
        "verdict": "PASS_Q6_M7_UNIT_K8_DELETION_FENCE",
        "packets": reports,
        "normalized_raw_totals": [str(Fraction(total,Q*Q)) for total in EXPECTED_TOTALS],
        "strict_offset": "delta=1/12 in each scalar coordinate",
        "fence": deletion_fence(supports,candidate,gate),
    }


def rejected(label,callback):
    try:
        callback()
    except AssertionError:
        return label
    raise AssertionError(label+" corruption accepted")


def self_test():
    packet = load_packet()
    bad = copy.deepcopy(packet)
    bad["witnesses"][1]["vertices"][0][0] = [3,2]
    point = rejected("point",lambda: packet_audit(bad))
    bad = copy.deepcopy(packet)
    bad["template"][0] = [2,2]
    template = rejected("template",lambda: packet_audit(bad))
    bad = tuple(cell for cell in EXPECTED_CANDIDATE if cell != (49,0))
    missing_cell = rejected("missing_cell",lambda: packet_audit(packet,bad))
    offset = rejected("boundary_offset",lambda: packet_audit(packet,EXPECTED_CANDIDATE,Fraction(0)))
    gate = rejected("gate",lambda: deletion_fence(EXPECTED_SUPPORTS,EXPECTED_CANDIDATE,Fraction(1,2)))
    return {label:"rejected" for label in (point,template,missing_cell,offset,gate)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args = parser.parse_args()
    check_hashes()
    report = audit()
    if args.self_test:
        report["planted_failures"] = self_test()
    print("PASS_Q6_M7_UNIT_K8_DELETION_FENCE")
    print(json.dumps(report,sort_keys=True))
