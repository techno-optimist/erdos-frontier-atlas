"""Reference code for the Erdős #131 certificate: thresholds of OEIS A068063.

A068063(n) is the largest nondividing subset of {1..n}: no element divides the
sum of any nonempty subset of the other elements.  T_k is the least n with a
nondividing k-subset, so A068063(n) = max{k : T_k <= n}.

Search (the C engine nondiv.c is its port, node for node): a k-set with
maximum N is built in decreasing order.  Subsets of nondividing sets are
nondividing, so after choosing x the remaining k - d - 1 smaller elements form
a nondividing set below x, which forces x > T_{k-d-1}.  A new smaller element
x is admissible iff (a) x divides no nonempty subset sum of the chosen set and
(b) for every chosen e, no subset sum of the others (the empty one included)
is congruent to -x mod e.  Subset sums are kept as a bitset, and for each e
the residues mod e of the subset sums of the other chosen elements.
"""
from itertools import combinations


def is_nondividing(S):
    """No element divides the sum of any nonempty subset of the others (brute force)."""
    S = list(S)
    if len(set(S)) != len(S) or any(x < 1 for x in S):
        return False
    for e in S:
        others = [x for x in S if x != e]
        for r in range(1, len(others) + 1):
            for c in combinations(others, r):
                if sum(c) % e == 0:
                    return False
    return True


class Search:
    def __init__(self, k, T):
        self.k, self.T = k, T
        self.S, self.nodes = [], 0

    def run(self, N):
        self.S, self.nodes = [N], 0
        self.SS, self.maxsum, self.R = 1 | (1 << N), N, [1]       # R[0]: residues mod N of {0}
        return self.dfs(N)

    def ok(self, x):
        for m in range(x, self.maxsum + 1, x):
            if (self.SS >> m) & 1:
                return False
        for e, R in zip(self.S, self.R):
            if (R >> ((e - x % e) % e)) & 1:
                return False
        return True

    def push(self, x):
        state = (self.SS, self.maxsum, list(self.R))
        Rx = 0
        ss, m = self.SS, 0
        while ss:
            if ss & 1:
                Rx |= 1 << (m % x)
            ss >>= 1
            m += 1
        newR = []
        for e, R in zip(self.S, self.R):
            s, mask = x % e, (1 << e) - 1
            rot = ((R << s) | (R >> (e - s))) & mask if s else R
            newR.append(R | rot)
        self.R = newR + [Rx]
        self.SS = self.SS | (self.SS << x)
        self.maxsum += x
        self.S.append(x)
        return state

    def pop(self, state):
        self.SS, self.maxsum, self.R = state
        self.S.pop()

    def dfs(self, prev):
        self.nodes += 1
        if len(self.S) == self.k:
            return True
        need = self.k - len(self.S) - 1
        for x in range(prev - 1, self.T[need], -1):
            if not self.ok(x):
                continue
            state = self.push(x)
            if self.dfs(x):
                return True
            self.pop(state)
        return False


def thresholds(kmax, nmax):
    """[(k, T_k, nodes of the successful search, witness)] and per-N node counts."""
    T, out, per_n = [0], [], []
    for k in range(1, kmax + 1):
        for N in range(T[-1] + 1, nmax + 1):
            s = Search(k, T)
            if s.run(N):
                T.append(N)
                out.append((k, N, s.nodes, sorted(s.S, reverse=True)))
                per_n.append((k, N, s.nodes, True))
                break
            per_n.append((k, N, s.nodes, False))
        else:
            return out, per_n
    return out, per_n
