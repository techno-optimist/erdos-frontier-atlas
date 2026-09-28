"""Erdős #864: sets whose pairwise sums are distinct except for at most one value (OEIS A389182).

A389182(N) is the largest A in {1..N} such that among the sums a + b (a <= b in A) at most
one value occurs more than once.

``one_exception`` is the definition, checked by brute force.  ``Search`` is the reference
search that onesum.c ports node for node, and ``table`` runs it along N.
"""
from collections import Counter


def one_exception(A):
    """True iff at most one value occurs more than once among the sums a + b, a <= b in A."""
    A = sorted(A)
    sums = Counter(A[i] + A[j] for i in range(len(A)) for j in range(i, len(A)))
    return sum(1 for c in sums.values() if c > 1) <= 1


def is_valid(A, N):
    """A is a set of distinct integers in 1..N with the one-exception property."""
    return (len(A) >= 1 and all(type(x) is int and 1 <= x <= N for x in A)
            and len(set(A)) == len(A) and one_exception(A))


class Search:
    """Is there a K-set in {1..N} containing 1 and N with the one-exception property?

    1 and N are placed first, then the inner elements in increasing order.  cnt counts the
    representations of each sum, exc is the repeated value (-1 while none).  A new x is
    admissible iff each new sum x + a (a in A, and 2x) is unused, equal to exc, or -- while
    exc = -1 -- the first used one, which becomes exc.  Each node keeps the candidates still
    admissible (admissibility only shrinks as A grows).  Of a set and its reflection
    x -> N + 1 - x only the one whose first inner element s has s - 1 <= N - t (t the last
    inner element) is searched: every later inner element is at most N + 1 - s.  A node is
    dropped when fewer candidates remain than elements to place.

    run() returns True with the set in self.A; self.nodes counts every call of dfs.
    """

    def __init__(self, N, K):
        assert N >= 1 and K >= 1
        self.N, self.K = N, K
        self.nodes = 0
        self.cnt = Counter()
        self.exc = -1
        self.A = []

    def admit(self, x):
        e = self.exc
        for a in self.A + [x]:
            s = x + a
            if self.cnt[s] and s != e:
                if e != -1:
                    return -2
                e = s
        return e

    def place(self, x, sign):
        for a in self.A:
            self.cnt[x + a] += sign
        self.cnt[2 * x] += sign
        if sign > 0:
            self.A.append(x)

    def unplace(self, x):
        self.A.pop()
        self.place(x, -1)

    def run(self):
        N, K = self.N, self.K
        self.place(1, 1)
        if K >= 2 and N > 1:
            self.place(N, 1)
        if K <= len(self.A):
            self.nodes = 1
            return K == len(self.A)
        if N <= 1:
            self.nodes = 1
            return False
        cand = [y for y in range(2, N) if self.admit(y) != -2]
        return self.dfs(cand)

    def dfs(self, cand):
        self.nodes += 1
        d = len(self.A)
        if d == self.K:
            return True
        need = self.K - d
        if len(cand) < need:
            return False
        for i in range(len(cand) - need + 1):
            x = cand[i]
            e, save = self.admit(x), self.exc
            self.place(x, 1)
            self.exc = e
            hi = self.N + 1 - x if d == 2 else self.N
            sub = [y for y in cand[i + 1:] if y <= hi and self.admit(y) != -2]
            if self.dfs(sub):
                return True
            self.unplace(x)
            self.exc = save
        return False


def table(nmax):
    """A389182(1..nmax) by the reference search: [(N, a(N), nodes, set or None)]."""
    rows, a = [], 0
    for N in range(1, nmax + 1):
        s = Search(N, a + 1)
        found = s.run()
        if found:
            a += 1
        rows.append((N, a, s.nodes, sorted(s.A) if found else None))
    return rows
