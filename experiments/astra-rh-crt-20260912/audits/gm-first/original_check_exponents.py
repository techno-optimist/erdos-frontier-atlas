"""Exact, bounded parameter audit, not numerical evidence for RH.
All exponent operations use fractions. Inequalities are powers of X with
positive epsilon margins suppressed, as documented in audit.md.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json

# Constraint tuple (A, B, C, label) means A*h + B*a <= C;
# H=X^h, z=X^a, D=X^(a/2), T_min=X^(1-h).
def c(a,b,v,label): return (Q(a),Q(b),Q(v),label)
common=[c(-1,0,0,'h>=0'),c(0,-1,0,'a>=0'),
        c(1,-1,0,'Prop1 lower a>=h'),c(Q(1,2),1,1,'Prop1 a<=1-h/2'),
        c(Q(-1,2),1,Q(1,2),'Prop1 a<=1/2+h/2'),
        c(1,0,Q(2,3),'Prop1 and deterministic tail h<=2/3'),
        c(1,0,Q(4,7),'Weyl term h<=4/7')]
old=common+[c(Q(4,3),-1,0,'Classical bulk a>=4h/3')]
new=common+[c(Q(5,4),-1,0,'GM T-term a>=5h/4'),
            c(10,-1,5,'GM N^(18/5) term a>=10h-5')]
def solve(cons):
    vertices=set()
    for (a,b,c1,_),(d,e,f,_) in combinations(cons,2):
        det=a*e-b*d
        if not det: continue
        h=(c1*e-b*f)/det; z=(a*f-c1*d)/det
        if all(A*h+B*z<=C for A,B,C,_ in cons): vertices.add((h,z))
    optimum=max(vertices,key=lambda x:x[0])
    active=[label for A,B,C,label in cons if A*optimum[0]+B*optimum[1]==C]
    return {'max_h':str(optimum[0]),'z_exponent':str(optimum[1]),
            'vertices':[[str(x),str(y)] for x,y in sorted(vertices)],'active':active}

def powers(h,a,t=None):
    d=a/2
    if t is None:t=1-h
    target=h/2
    terms={'small M':h-d,'Weyl':h-Q(2,3)*t,
           'GM middle':h-d/5-t/2,'GM T term':h-Q(4,5)*d,
           'classical bulk':h-Q(3,4)*d,
           'Prop1 off-diagonal zH/X':a+h-1}
    return {'h':str(h),'a':str(a),'d':str(d),'t':str(t),'d/t':str(d/t),
            'target':str(target),'terms':{k:{'power':str(v),'saving_vs_target':str(target-v)} for k,v in terms.items()}}

# Reproduce coefficient normalization: U=D*V.
# Records are exponents of (D,V,T), first R then H/T*V^2*(T*R)^1/2.
raw={'N^2 U^-2':(2,-2,0),'N^(18/5) U^-4':(Q(18,5),-4,0),'T N^(12/5) U^-4':(Q(12,5),-4,1)}
normal={name:(Q(a)+Q(b),Q(b),Q(t)) for name,(a,b,t) in raw.items()}
after_fourth={name:(a/2,2+b/2,Q(-1,2)+t/2) for name,(a,b,t) in normal.items()}
assert normal['N^(18/5) U^-4']==(Q(-2,5),Q(-4),Q(0))
assert after_fourth['T N^(12/5) U^-4']==(Q(-4,5),Q(0),Q(0))
assert after_fourth['N^(18/5) U^-4']==(Q(-1,5),Q(0),Q(-1,2))
assert solve(old)['max_h']=='6/11'
assert solve(new)['max_h']=='4/7'
# Delete Weyl to show that the Theorem 1.1/Prop1 overlap remains a wall.
assert solve([x for x in new if 'Weyl' not in x[3]])['max_h']=='4/7'

# Explicit epsilon witness: eta in (0,1/100), h<=4/7-eta,
# a=(5/4+eta)*h, so D>=H^(5/8+eta/2), T>=H^(3/4+3eta).
# Polynomial identities below are exact, coefficient order 1,eta,eta^2.
# Slack: 1-(7/4+2eta)(4/7-eta) = 17eta/28+2eta^2.
first_overlap=(Q(1)-Q(7,4)*Q(4,7), Q(7,4)-2*Q(4,7),Q(2))
assert first_overlap==(0,Q(17,28),2)
# Slack: 1/2-(3/4+2eta)(4/7-eta) = 1/14-11eta/28+2eta^2.
second_overlap=(Q(1,2)-Q(3,4)*Q(4,7),Q(3,4)-2*Q(4,7),Q(2))
assert second_overlap==(Q(1,14),Q(-11,28),2)
assert second_overlap[0]+second_overlap[1]/100>0
# Slack: 1-(7/4+3eta)(4/7-eta) = eta/28+3eta^2.
height=(Q(1)-Q(7,4)*Q(4,7),Q(7,4)-3*Q(4,7),Q(3))
assert height==(0,Q(1,28),3)
epsilon_savings={'Weyl':Q(2,3)*3,'GM middle':Q(1,5)*Q(1,2)+Q(1,2)*3,'GM T term':Q(4,5)*Q(1,2)}
assert epsilon_savings=={'Weyl':2,'GM middle':Q(8,5),'GM T term':Q(2,5)}

# Negative control: h = 4/7 + 1/1000 fails even at maximal Prop1 z.
hbad=Q(4,7)+Q(1,1000); abad=1-hbad/2
failed=[label for A,B,C,label in new if A*hbad+B*abad>C]
assert set(failed)=={'Weyl term h<=4/7','GM T-term a>=5h/4','GM N^(18/5) term a>=10h-5'}
# GM Proposition 12.1 at U=D^(3/4), D in [T^(5/6),T],
# yields R <= X^o(1) T^(1/2). Retaining zeta's fourth moment
# gives H D^(-1/2) T^(-1/4), hence a>=3h-1.
refined=[x for x in common if 'Weyl' not in x[3]]+[
    c(3,-1,1,'GM Prop12.1 sigma=3/4 bulk a>=3h-1'),
    c(Q(-5,3),-1,Q(-5,3),'Prop12.1 D>=T^(5/6)'),
    c(2,1,2,'Prop12.1 D<=T')]
assert solve(refined)['max_h']=='4/7'
result={'old_constraints':solve(old),'new_constraints':solve(new),
        'refined_Prop12_1_without_Weyl':solve(refined),
        'new_without_Weyl':solve([x for x in new if 'Weyl' not in x[3]]),
        'old_endpoint':powers(Q(6,11),Q(8,11)),
        'new_endpoint':powers(Q(4,7),Q(5,7)),
        'improvement_in_h':str(Q(4,7)-Q(6,11)),
        'normalized_GM_R':{k:list(map(str,v)) for k,v in normal.items()},
        'after_fourth_powers_D_V_T':{k:list(map(str,v)) for k,v in after_fourth.items()},
        'epsilon_overlap_slack_polynomials':{'first':list(map(str,first_overlap)), 'second':list(map(str,second_overlap)), 'height':list(map(str,height))},
        'epsilon_savings_in_H_before_losses':{k:str(v) for k,v in epsilon_savings.items()},
        'negative_control':{'h':str(hbad),'a':str(abad),'violated':failed},
        'all_assertions_passed':True}
Path(__file__).with_name('exponent-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
