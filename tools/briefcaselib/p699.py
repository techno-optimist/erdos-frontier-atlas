"""Erdős #699 operators: decide a whole row (n, i) by positional localization.

#699 asks whether, for 1 <= i < j <= n/2, some prime p >= i divides both C(n,i) and C(n,j).
These operators implement the proved reduction in
experiments/claude-699-general-i-20260928/README.md (Lemma 1, Theorem 2), for every i >= 3.

Split x = S * R: R holds the prime powers q^e || x with q > i, or q = i and e >= 2; S is the
rest. Write n - t = S_t R_t for t < i. The primes p >= i of C(n, i) are the primes of the R_t.
A counterexample (n, i, j) forces:
  j = R_0 m with 1 <= m <= S_0 / 2,
  R_t | P_t(m) = prod_{r <= t} (t m - r S_0) for 1 <= t < i (this is (*) itself),
  (c) 4(n-1) <= S_0^2 S_1, and for j < n/2 (d) 108((n-1)(n-2))^2 <= (S_0^3 S_1 S_2)^2,
  for j = n/2: R_t = 1 at every odd t < i.
So most rows need no factoring at all: three smooth parts and one inequality settle every j.
`certify_row` records that argument as a small JSON certificate; `verify_row` rechecks it with
nothing but division, primality tests of the recorded factors, and modular arithmetic.
"""
from itertools import product

from . import nt

MIN_I = 3


def _primes(i):
    return nt.primes_upto(i)


def split(x, i, primes=None):
    """(S, R) for x >= 1, by trial division by the primes <= i only."""
    if x < 1:
        raise ValueError("split needs x >= 1")
    primes = _primes(i) if primes is None else primes
    s, y = 1, x
    for p in primes:
        if y % p == 0:
            e, pe = 0, 1
            while y % p == 0:
                y //= p
                pe *= p
                e += 1
            if not (p == i and e >= 2):
                s *= pe
    return s, x // s


def blocks(n, i, factorize=nt.factor):
    """[(M, t, p)]: every prime p >= i of C(n, i), its position t and M = p^v_p(n - t)."""
    out = []
    for t in range(i):
        for p, e in factorize(n - t).items():
            if p > i or (p == i and e >= 2):
                out.append((p ** e, t, p))
    return out


def passes(n, j, blk):
    """The positional condition (*): j mod M <= t at every block."""
    return all(j % M <= t for M, t, _ in blk)


def common_prime(n, j, blk):
    """Least prime p >= i dividing both C(n, i) and C(n, j), or None. Exact (Kummer)."""
    for p in sorted(p for _, _, p in blk):
        if nt.carries(j, n - j, p):
            return p
    return None


def cond_c(n, S0, S1):
    return 4 * (n - 1) <= S0 * S0 * S1


def cond_d(n, S0, S1, S2):
    L = (n - 1) * (n - 2)
    return 108 * L * L <= (S0 ** 3 * S1 * S2) ** 2


def P(t, m, S0):
    out = 1
    for r in range(t + 1):
        out *= t * m - r * S0
    return out


def residue_options(M, t, S0):
    """The m mod M allowed by one block at position t >= 1."""
    inv = pow(t, -1, M)
    return sorted({(r * S0 * inv) % M for r in range(t + 1)})


def m_candidates(S0, blocks12):
    """All m in [1, S0/2) meeting the (M, t) blocks, by CRT over the largest blocks."""
    hi = (S0 - 1) // 2
    use = sorted(blocks12, reverse=True)
    k, W = 0, 1
    while k < len(use) and W <= hi:
        W *= use[k][0]
        k += 1
    head, tail = use[:k], use[k:]
    tail_ok = [(M, set(residue_options(M, t, S0))) for M, t in tail]
    out = set()
    for choice in product(*[residue_options(M, t, S0) for M, t in head]):
        r, W = nt.crt(list(zip(choice, (M for M, _ in head))))
        m = r if r > 0 else W
        while m <= hi:
            if all(m % M in ok for M, ok in tail_ok):
                out.add(m)
            m += W
    return sorted(out)


def row(n, i):
    """Decide the whole row (n, i): every j with i < j <= n/2. Returns a report dict.

    report["holds"] is True when every such j has a common prime p >= i.
    """
    if i < MIN_I:
        raise ValueError("the reduction needs i >= 3 (i = 1, 2 are settled separately)")
    if n < 2 * i + 2:
        return {"n": n, "i": i, "holds": True, "vacuous": True, "stages": ["no j with i < j <= n/2"]}
    primes = _primes(i)
    S = [split(n - t, i, primes)[0] for t in range(3)]
    R = [(n - t) // S[t] for t in range(3)]
    rep = {"n": n, "i": i, "S": S, "R": R, "vacuous": False, "stages": [], "survivors": []}
    # central j = n/2
    if n % 2 == 0:
        if R[1] != 1:
            rep["stages"].append("central j = n/2: n - 1 is not smooth (R_1 > 1), so j = n/2 has a common prime")
            rep["central"] = "excluded by (e)"
        else:
            blk = blocks(n, i)
            j = n // 2
            if passes(n, j, blk):
                p = common_prime(n, j, blk)
                rep["survivors"].append({"j": j, "common_prime": p})
                rep["stages"].append(f"central j = n/2 passes (*); exact common prime: {p}")
            else:
                rep["stages"].append("central j = n/2 fails (*) at some block")
            rep["central"] = "tested"
    # non-central j
    if S[0] < 2:
        rep["special"] = False
        rep["stages"].append("S_0 = 1: no multiple of R_0 = n lies in (0, n/2)")
    elif not cond_c(n, S[0], S[1]):
        rep["special"] = False
        rep["stages"].append("(c) fails: 4(n-1) > S_0^2 S_1, so no j can fail")
    elif not cond_d(n, S[0], S[1], S[2]):
        rep["special"] = False
        rep["stages"].append("(d) fails: 6*sqrt(3)(n-1)(n-2) > S_0^3 S_1 S_2, so no j < n/2 can fail")
    else:
        rep["special"] = True
        blk12 = ([(M, 1) for M in _prime_powers(R[1])] + [(M, 2) for M in _prime_powers(R[2])])
        ms = m_candidates(S[0], blk12)
        rep["candidates"] = ms
        rep["stages"].append(f"special: (c) and (d) hold; {len(ms)} m pass positions 1 and 2")
        Rt = {t: split(n - t, i, primes)[1] for t in range(3, i)}
        full = None
        for m in ms:
            bad = next((t for t in range(3, i) if P(t, m, S[0]) % Rt[t]), None)
            j = R[0] * m
            if bad is None and j > i:
                full = blocks(n, i) if full is None else full
                p = common_prime(n, j, full)
                rep["survivors"].append({"j": j, "common_prime": p})
    rep["holds"] = all(s["common_prime"] is not None for s in rep["survivors"])
    return rep


def _prime_powers(x):
    return [p ** e for p, e in nt.factor(x).items()]


def special(n, i):
    """True when n satisfies (c) and (d): the only n where some j < n/2 can fail."""
    if n < 2 * i + 2:
        return False
    primes = _primes(i)
    S0, S1, S2 = (split(n - t, i, primes)[0] for t in range(3))
    return S0 >= 2 and cond_c(n, S0, S1) and cond_d(n, S0, S1, S2)


def special_upto(i, X):
    """Every special n <= X, via the (S_0, S_1) progressions (a reference; slow for i >= 8)."""
    primes = _primes(i)
    SM = nt.smooth_numbers(i, X)
    out = []
    for S0 in SM:
        if S0 < 2:
            continue
        for S1 in SM:
            if nt.math.gcd(S0, S1) != 1 or (S0 % 2 and S1 % 2):
                continue
            top = min(X, S0 * S0 * S1 // 4 + 1)
            r, L = nt.crt([(0, S0), (1, S1)])
            n = r if r > 0 else L
            while n <= top:
                if n >= 2 * i + 2:
                    s = [split(n - t, i, primes)[0] for t in range(3)]
                    if s[0] == S0 and s[1] == S1 and cond_d(n, S0, S1, s[2]):
                        out.append(n)
                n += L
    return sorted(out)


# ---------------------------------------------------------------- certificates

CERT_SCHEMA = "briefcase-p699-row-v1"


def certify_row(n, i):
    """A JSON-able certificate that every j in (i, n/2] has a common prime p >= i.

    Raises ValueError if the row does not hold (that would be a counterexample)."""
    rep = row(n, i)
    if not rep["holds"]:
        raise ValueError(f"row ({n}, {i}) has a counterexample: {rep['survivors']}")
    cert = {"schema": CERT_SCHEMA, "n": str(n), "i": i}
    if rep["vacuous"]:
        cert["kind"] = "vacuous"
        return cert
    S0, S1, S2 = rep["S"]
    cert["S"] = [str(S0), str(S1), str(S2)]
    if n % 2 == 0:
        if rep["R"][1] != 1:
            cert["central"] = {"kind": "n-1 not smooth"}
        else:
            cert["central"] = {"kind": "tested", "survivors": [
                {"j": str(s["j"]), "p": s["common_prime"]} for s in rep["survivors"] if 2 * s["j"] == n]}
    if not rep["special"]:
        cert["kind"] = "not special"
        return cert
    cert["kind"] = "special"
    cert["factors"] = {str(t): {str(p): e for p, e in nt.factor(rep["R"][t]).items()} for t in (1, 2)}
    elim = []
    primes = _primes(i)
    for m in rep["candidates"]:
        j = rep["R"][0] * m
        bad = next((t for t in range(3, i) if P(t, m, S0) % split(n - t, i, primes)[1]), None)
        entry = {"m": str(m)}
        if bad is not None:
            entry["fails_at"] = bad
        elif j <= i:
            entry["trivial"] = True
        else:
            entry["common_prime"] = next(s["common_prime"] for s in rep["survivors"] if s["j"] == j)
        elim.append(entry)
    cert["candidates"] = elim
    return cert


def verify_row(cert):
    """Independently recheck a certificate from `certify_row`. Returns (ok, message)."""
    try:
        return _verify(cert)
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
        return False, f"malformed certificate: {exc!r}"


def _verify(cert):
    if cert.get("schema") != CERT_SCHEMA:
        return False, "unknown schema"
    n, i = int(cert["n"]), int(cert["i"])
    if i < MIN_I:
        return False, "i < 3"
    if cert["kind"] == "vacuous":
        return (n < 2 * i + 2), "vacuous row" if n < 2 * i + 2 else "row is not vacuous"
    primes = _primes(i)
    S = [int(s) for s in cert["S"]]
    if [split(n - t, i, primes)[0] for t in range(3)] != S:
        return False, "smooth parts do not match n"
    R = [(n - t) // S[t] for t in range(3)]
    if n % 2 == 0:
        c = cert["central"]
        if c["kind"] == "n-1 not smooth":
            if R[1] == 1:
                return False, "n - 1 is smooth; the central j needs a test"
        elif c["kind"] == "tested":
            blk = blocks(n, i)
            j = n // 2
            if passes(n, j, blk) and common_prime(n, j, blk) is None:
                return False, "central j = n/2 is a counterexample"
        else:
            return False, "unknown central kind"
    if cert["kind"] == "not special":
        if S[0] >= 2 and cond_c(n, S[0], S[1]) and cond_d(n, S[0], S[1], S[2]):
            return False, "n is special; the certificate must list candidates"
        return True, "not special: every j < n/2 is settled by (c)/(d)" + (
            "; central settled" if n % 2 == 0 else "")
    if cert["kind"] != "special":
        return False, "unknown kind"
    # the factorizations of R_1, R_2: products must match and factors must be prime
    blk12 = []
    for t in (1, 2):
        fac = {int(p): int(e) for p, e in cert["factors"][str(t)].items()}
        prod_ = 1
        for p, e in fac.items():
            if not nt.is_prime(p) or p < i or (p == i and e < 2):
                return False, f"bad factor {p} at position {t}"
            prod_ *= p ** e
        if prod_ != R[t]:
            return False, f"factors do not multiply to R_{t}"
        blk12 += [(p ** e, t) for p, e in fac.items()]
    listed = [int(c["m"]) for c in cert["candidates"]]
    if listed != m_candidates(S[0], blk12):
        return False, "candidate list is not the full CRT solution set"
    for c in cert["candidates"]:
        m = int(c["m"])
        j = R[0] * m
        if "fails_at" in c:
            t = int(c["fails_at"])
            if not 3 <= t < i or P(t, m, S[0]) % split(n - t, i, primes)[1] == 0:
                return False, f"m = {m} does not fail at position {t}"
        elif c.get("trivial"):
            if j > i:
                return False, f"m = {m} gives j > i"
        else:
            blk = blocks(n, i)
            if common_prime(n, j, blk) != c["common_prime"] or c["common_prime"] is None:
                return False, f"m = {m}: common prime mismatch"
    return True, f"special: {len(listed)} candidates, each eliminated"
