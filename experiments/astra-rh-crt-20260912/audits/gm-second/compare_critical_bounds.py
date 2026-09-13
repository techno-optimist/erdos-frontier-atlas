"""Compare the critical-level numerical bounds; no arithmetic counterexample.
Also independently replay the parent parameter JSON's exposed arithmetic.
Only files in this isolated script directory are written.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
PARENT = Path(__file__).resolve().parents[1] / 'inputs' / 'gm_parameter_check.json'
raw_parent = PARENT.read_bytes()
parent = json.loads(raw_parent)


def q(*xs):
    xs = list(map(F, xs))
    while len(xs)>1 and xs[-1]==0:
        xs.pop()
    return tuple(xs)


def plus(a,b):
    return q(*(sum(v[i] if i<len(v) else F(0) for v in (a,b)) for i in range(max(len(a),len(b)))))


def times(a,b):
    v = [F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            v[i+j] += x*y
    return q(*v)


def minus(a,b):
    return plus(a,q(*(-x for x in b)))


h=q(F(4,7),-1)
expected=[
    minus(q(1),times(q(F(7,4),2),h)),
    minus(q(F(1,2)),times(q(F(3,4),2),h)),
    q(F(1,8), F(1,2)-F(1,3)-F(1,1000)),
    minus(q(F(2,3)),times(q(F(7,6), F(1,3)+F(1,1000)),h)),
    minus(q(F(1,2)),times(q(F(7,8), F(1,3)+F(1,1000)-F(1,10)),h)),
    q(0,F(2,5)-F(1,3)-F(1,1000)),
    minus(q(F(1,2)),times(q(F(3,4),F(1,16)),h)),
    minus(q(1),times(q(F(3,2),F(1,16)),h)),
]
assert len(expected)==len(parent['margins'])
margin_checks=[]
for calc,row in zip(expected,parent['margins']):
    k=0
    while calc[k]==0:
        k+=1
    coeffs=calc[k:]
    assert k==row['epsilon_factor_power']
    assert list(map(str,coeffs))==row['remaining_coefficients'],row['name']
    lower=coeffs[0]+sum(min(F(0),x)/F(100)**i for i,x in enumerate(coeffs[1:],1))
    assert lower==F(row['uniform_lower_bound_after_factoring'])>0
    margin_checks.append({'name':row['name'],'exact_coefficients_match':True,'lower_bound':str(lower)})

lp_checks=[]
for name,row in parent['epsilon_free_polytopes'].items():
    rows=[tuple(map(F,x)) for x in row['rows_Ah_plus_Ba_le_C']]
    vertices=set()
    for (a,b,c),(d,e,f) in combinations(rows,2):
        det=a*e-b*d
        if not det:
            continue
        point=((c*e-b*f)/det,(a*f-c*d)/det)
        if all(A*point[0]+B*point[1]<=C for A,B,C in rows):
            vertices.add(point)
    assert len(vertices)==row['feasible_vertex_count']
    maximum=max(point[0] for point in vertices)
    assert maximum==F(row['h_max'])
    assert (maximum,F(row['cutoff_exponent'])) in vertices
    lp_checks.append({'name':name,'verified_vertex_count':len(vertices),'verified_max_h':str(maximum)})

# Exponents of (D,T) in a measure majorant at U=D^(3/4).
# This table concerns T^(5/6)<=D<=T and suppresses subpower factors.
measure={'GM_1_1':(F(3,5),F(0)), 'Huxley_classical':(F(-1,2),F(1)),
         'GM_12_1':(F(0),F(1,2))}
raw_bounds={
    'GM_1_1':[(F(1,2),F(0)),(F(3,5),F(0)),(F(-3,5),F(1))],
    'Huxley_classical':[(F(1,2),F(0)),(F(-1,2),F(1))],
    'GM_12_1':[(F(1,2),F(0)),(F(0),F(1,2)),(F(1,5),F(3,10))],
}


def val(pair,alpha):
    return pair[0]*alpha+pair[1]


ends=(F(5,6),F(1))
comparison={}
for name,pair in measure.items():
    assert all(val(pair,a)>=val(raw,a) for a in ends for raw in raw_bounds[name])
    weyl=(pair[0]-F(1,2),pair[1]-F(2,3))
    fourth=(pair[0]/2-F(1,2),pair[1]/2-F(1,2))
    gap=min(val(weyl,a)-val(fourth,a) for a in ends)
    assert gap>=F(1,12)
    comparison[name]={'measure_majorant_D_T':list(map(str,pair)),
                      'Weyl_E_over_H_D_T':list(map(str,weyl)),
                      'fourth_E_over_H_D_T':list(map(str,fourth)),
                      'minimum_Weyl_minus_fourth_exponent_in_T':str(gap)}
    assert all(val(pair,a)>=F(1,2) for a in ends)
# Huxley and GM 1.1 switch at alpha=10/11; neither beats the refinement.
a=(measure['Huxley_classical'][1]-measure['GM_1_1'][1])/(measure['GM_1_1'][0]-measure['Huxley_classical'][0])
assert a==F(10,11)
# On the lower side of the transition, the GM T term dominates and fourth is H D^(-4/5).
lower_r=(F(-3,5),F(1))
assert (lower_r[0]/2-F(1,2),lower_r[1]/2-F(1,2))==(F(-4,5),F(0))

result={'scope':'Comparison of the displayed numerical majorants only; no lower bound and no genuine countermodel',
        'parent_input':str(PARENT),'parent_sha256':hashlib.sha256(raw_parent).hexdigest(),
        'parent_margin_checks':margin_checks,'parent_polytope_checks':lp_checks,
        'parent_barrier_scope':parent['barrier_scope'],
        'critical_range':'T^(5/6)<=D<=T, up to fixed-factor transition handling',
        'critical_comparison':comparison,'original_bound_switch_alpha':str(a),
        'best_of_listed_cardinality_bounds':'T^(1/2+o(1))',
        'best_of_listed_Weyl_and_fourth_treatments':'H D^(-1/2) T^(-1/4) X^o(1)',
        'all_checks_passed':True}
(OUT/'critical-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
