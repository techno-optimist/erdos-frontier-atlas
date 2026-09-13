"""Independent exact exponent audit; no claims about actual zeta values.
Run this file in isolated scratch. Only its sibling results.json is written.
All polynomial positivity certificates hold on 0 < epsilon <= 1/100.
The scalar concentration model is a negative control on summary bounds,
NOT an example of a Dirichlet polynomial or of the Riemann zeta function.
"""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import json


def p(*xs):
    r = [F(x) for x in xs]
    while len(r) > 1 and not r[-1]:
        r.pop()
    return tuple(r)


def add(a, b):
    return p(*(sum((v[i] if i < len(v) else F(0)) for v in (a, b))
               for i in range(max(len(a), len(b)))))


def scale(a, s):
    return p(*(x * F(s) for x in a))


def sub(a, b):
    return add(a, scale(b, -1))


def mul(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] += x * y
    return p(*r)


def positive_open(a):
    """Prove strict positivity via Bernstein coefficients after factoring e^k."""
    k = 0
    while k < len(a) and a[k] == 0:
        k += 1
    if k == len(a):
        return False, {"reason": "identically zero"}
    q = a[k:]
    n = len(q) - 1
    # epsilon = u/100, 0<=u<=1; power to degree-n Bernstein basis.
    power = [x / F(100)**i for i, x in enumerate(q)]
    bern = [sum(power[i] * F(comb(j, i), comb(n, i)) for i in range(j + 1))
            for j in range(n + 1)]
    ok = min(bern) > 0
    return ok, {"epsilon_factor": k, "power_coefficients": list(map(str, a)),
                "bernstein_coefficients_after_factor": list(map(str, bern)),
                "positive_lower_bound_after_factor": str(min(bern))}


E = p(0, 1)
HMAX = p(F(4, 7), -1)
loss = scale(E, F(3, 100))
tail_saving = scale(E, F(1, 4))
final_saving = scale(E, F(1, 16))
polys = {
    "high_H_domain_nonempty": sub(HMAX, E),
    "Prop1_H_upper": sub(p(F(2, 3), -1), HMAX),
    "Prop1_z_lower_exponent_in_H": p(F(1, 4)),
    "Prop1_z_upper_X_over_H": sub(p(1), mul(p(F(7, 4), 2), HMAX)),
    "Prop1_z_upper_sqrtX_times_H": sub(p(F(1, 2)), mul(p(F(3, 4), 2), HMAX)),
    "z_less_than_X": sub(p(1), mul(p(F(5, 4), 1), HMAX)),
    "T_at_least_H_power_3over4_plus_3epsilon": sub(p(1), mul(p(F(7, 4), 3), HMAX)),
    "low_H_original_Theorem1_range": sub(p(F(6, 11), -1), E),
    "tail_low_levels_after_all_losses": sub(p(F(1, 8), F(1, 2)), add(loss, tail_saving)),
    "tail_Weyl_after_all_losses": sub(scale(E, 2), add(loss, tail_saving)),
    "tail_GM_middle_after_all_losses": sub(scale(E, F(8, 5)), add(loss, tail_saving)),
    "tail_GM_T_after_all_losses": sub(scale(E, F(2, 5)), add(loss, tail_saving)),
    "main_piece_error_vs_final": sub(scale(E, F(1, 10)), final_saving),
    "CS_cross_error_vs_final": sub(scale(tail_saving, F(1, 2)), final_saving),
    "tail_error_vs_final": sub(tail_saving, final_saving),
    "centering_cross_slack_in_X": sub(p(F(1, 2)), mul(HMAX, p(F(3, 4), F(1, 16)))),
    "centering_square_slack_in_X": sub(p(1), mul(HMAX, p(F(3, 2), F(1, 16)))),
    "boundary_H_over_X_is_small": sub(p(1), HMAX),
    "boundary_H_cubed_over_X_squared_is_small": sub(p(2), scale(HMAX, 3)),
    "far_tail_log_absorption_leaves_decay": sub(p(F(1, 3)), scale(mul(E, E), F(1, 100))),
    "tail_target_power_is_positive": sub(p(F(1, 2)), tail_saving),
}
certificates = {}
for name, poly in polys.items():
    ok, cert = positive_open(poly)
    assert ok, (name, cert)
    certificates[name] = cert

# Independently substitute U=D*V in GM and then apply fourth moment.
# Vectors are exponents of (D,V,T), with the outside H not included.
gm_raw = [(F(2), F(-2), F(0)), (F(18, 5), F(-4), F(0)),
          (F(12, 5), F(-4), F(1))]
level = [(a + b, b, c) for a, b, c in gm_raw]
fourth = [(a / 2, 2 + b / 2, (c - 1) / 2) for a, b, c in level]
assert level == [(F(0), F(-2), F(0)), (F(-2, 5), F(-4), F(0)),
                 (F(-8, 5), F(-4), F(1))]
assert fourth[1:] == [(F(-1, 5), F(0), F(-1, 2)),
                      (F(-4, 5), F(0), F(0))]

# Exact report-ceiling tests use a fixed scalar majorant, not a lower bound.
def exponents(h, a):
    d, t = a / 2, 1 - h
    target = h / 2
    return {"low": h-d, "Weyl": h-F(2, 3)*t,
            "GM_middle": h-d/5-t/2, "GM_T": h-F(4, 5)*d,
            "Prop12_critical": h-d/2-t/4, "target": target}


def majorant_gate(h, a, names):
    x = exponents(h, a)
    return all(x[n] <= x["target"] for n in names), x


endpoint_h, endpoint_a = F(4, 7), F(5, 7)
assert majorant_gate(endpoint_h, endpoint_a,
                      ["Weyl", "GM_middle", "GM_T", "Prop12_critical"])[0]
hbad = endpoint_h + F(1, 1000)
abad = 1 - hbad/2
negative_bound_gate, bad_powers = majorant_gate(
    hbad, abad, ["Weyl", "GM_middle", "GM_T", "Prop12_critical"])
assert not negative_bound_gate
assert all(bad_powers[n] > bad_powers["target"]
           for n in ["Weyl", "GM_middle", "GM_T", "Prop12_critical"])

# A single upper-bound term exceeding target does NOT force a quantity above target.
# The same admissibility gate accepts zero and a large mixed integral.
def scalar_admissible(alpha, r, zeta_amplitude):
    """All exponents are relative to T; r=log_T |S|, D=T^alpha."""
    sigma = F(3, 4)
    gm1 = max(alpha*(2-2*sigma), alpha*(F(18,5)-4*sigma),
              1+alpha*(F(12,5)-4*sigma))
    prop12 = max(alpha*(2-2*sigma), F(1,2)+alpha*(3-4*sigma),
                 (30*sigma-21)/5+alpha*(46-60*sigma)/5)
    classical = max(alpha/2, 1-alpha/2)
    inequalities = {
        "GM1": r <= gm1,
        "Prop12": r <= prop12,
        "classical": r <= classical,
        "zeta_fourth": r+4*zeta_amplitude <= 1,
        "zeta_second": r+2*zeta_amplitude <= 1,
        "Weyl": zeta_amplitude <= F(1,6),
        "M_second": r-alpha/2 <= max(0, 1-alpha),
    }
    return all(inequalities.values()), inequalities


# Endpoint and a strictly beyond-endpoint, largest-allowed-cutoff test.
scalar_cases = []
for h, a in [(endpoint_h, endpoint_a), (hbad, abad)]:
    d, t = a/2, 1-h
    alpha = d/t
    assert F(5,6) <= alpha <= 1
    ok, checks = scalar_admissible(alpha, F(1,2), F(1,8))
    assert ok, checks
    mixed = h-d/2-t/4
    scalar_cases.append({"h":str(h), "a":str(a), "D_exponent_relative_to_T":str(alpha),
                         "set_measure_exponent_relative_to_T":"1/2",
                         "zeta_amplitude_exponent_relative_to_T":"1/8",
                         "mixed_integral_exponent_in_X":str(mixed),
                         "target_exponent_in_X":str(h/2),
                         "excess_over_target":str(mixed-h/2),
                         "all_scalar_upper_bounds_pass":ok, "checks":checks})

# Negative control: any epsilon loss budget .4e exhausts the worst GM saving.
# Passing this would show our margin checker is fail-open.
exhausted_poly = sub(scale(E, F(2, 5)), add(scale(E, F(2, 5)), tail_saving))
exhausted_ok, exhausted_cert = positive_open(exhausted_poly)
assert not exhausted_ok

# Stronger subconvexity can matter if used beyond the old Weyl branch:
# |S|=T^(1/2), pointwise zeta=T^theta yields E=H D^(-1/2) T^(-1/2+2theta).
# This beats fourth moment's T^(-1/4) exactly when theta<1/8.
assert -F(1,2)+2*F(1,8) == -F(1,4)

result = {
    "scope":"Exact algebra of stated inequalities, not analytic source verification or an arithmetic counterexample",
    "all_positive_certificates_pass":True,
    "positive_certificate_count":len(certificates),
    "epsilon_polynomial_certificates":certificates,
    "normalization_level_vectors_D_V_T":[list(map(str,x)) for x in level],
    "fourth_moment_vectors_D_V_T":[list(map(str,x)) for x in fourth],
    "epsilon_budget":{"GM_time_loss":"epsilon^2/100", "T_at_most":"4 X^2",
                      "polylog_budget_in_X":"epsilon^2/100", "aggregate_loss_in_H":"3 epsilon/100",
                      "weakest_raw_saving_in_H":"2 epsilon/5", "certified_tail_saving":"epsilon/4"},
    "endpoint":{k:str(v) for k,v in exponents(endpoint_h,endpoint_a).items()},
    "negative_majorant_gate":{"h":str(hbad),"a":str(abad), "gate_result":negative_bound_gate,
                              "powers":{k:str(v) for k,v in bad_powers.items()}},
    "negative_epsilon_loss_budget":{"gate_result":exhausted_ok,"certificate":exhausted_cert},
    "scalar_concentration_models_NOT_arithmetic_examples":scalar_cases,
    "zero_also_satisfies_all_upper_bounds":True,
    "far_tail_X_exponent":str(F(1)+2*F(-2,3)),
    "CS_tail_saving_in_H":str(F(1,4)/2),
    "high_H_truncated_centering_saving_available_in_H":"epsilon/10",
    "weaker_global_saving_requested_in_H":"epsilon/16",
}
Path(__file__).with_name("results.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
