"""Erdős #357: sequences all of whose segment sums are distinct (OEIS A364132, A364153).

A segment of (s_1, ..., s_n) is a run s_i + ... + s_j of consecutive terms.

  mode "m": increasing n-sequences from {1..N}; a(n) = A364132(n) is the least such N
  mode "a": n-sequences of distinct values from {1..N} in any order; a(n) = A364153(n)

``segment_sums_distinct`` is the definition, checked by brute force.  ``Search`` is the
reference search that segsum.c ports node for node.
"""


def segment_sums_distinct(seq):
    """True iff the n(n+1)/2 segment sums of seq are pairwise distinct."""
    sums = [sum(seq[i:j]) for i in range(len(seq)) for j in range(i + 1, len(seq) + 1)]
    return len(sums) == len(set(sums))


def is_valid(mode, seq, N):
    """seq is an admissible sequence for (mode, len(seq), N), checked from the definition."""
    if not seq or any(type(x) is not int or not 1 <= x <= N for x in seq):
        return False
    if mode == "m" and any(a >= b for a, b in zip(seq, seq[1:])):
        return False
    return segment_sums_distinct(seq)


class Search:
    """Depth-first search for an n-sequence in mode "m" or "a" with every term <= N.

    The sequence is built left to right.  T is the set of sums of the segments ending at
    the last term, 0 included, and D the set of all segment sums so far, both as Python
    ints used as bitsets.  A next term x is admissible iff (T << x) & D == 0; then
    T <- (T << x) | 1 and D <- D | (T << x).

    Pruning: the n - j terms still to come are distinct values of [lo, N] outside D, since
    each is itself a segment sum (lo = s_j + 1 in mode "m", 1 in mode "a").  Mode "m" caps
    the next term at N - (n - j - 1).  Mode "a" keeps only sequences with s_1 < s_n.

    run() returns True with the first sequence found (in search order) in self.seq, or
    False.  self.nodes counts every call of dfs, the root included.
    """

    def __init__(self, mode, n, N):
        assert mode in ("m", "a") and n >= 1 and N >= 1
        self.mode, self.n, self.N = mode, n, N
        self.nodes = 0
        self.seq = []

    def run(self):
        return self.dfs(1, 0)

    def dfs(self, T, D):
        self.nodes += 1
        seq, n, N = self.seq, self.n, self.N
        j = len(seq)
        if j == n:
            return True
        lo = seq[-1] + 1 if self.mode == "m" and j else 1
        hi = N - (n - j - 1) if self.mode == "m" else N
        if lo <= N:
            window = ((1 << (N + 1)) - 1) >> lo << lo
            avail = N - lo + 1 - bin(D & window).count("1")
        else:
            avail = 0
        if avail < n - j:
            return False
        for x in range(lo, hi + 1):
            if D >> x & 1:
                continue
            if self.mode == "a" and j == n - 1 and n > 1 and x < seq[0]:
                continue
            new = T << x
            if new & D:
                continue
            seq.append(x)
            if self.dfs(new | 1, D | new):
                return True
            seq.pop()
        return False


def least(mode, n, start=1):
    """Least N >= start with an admissible n-sequence, by the reference search."""
    N = start
    while not Search(mode, n, N).run():
        N += 1
    return N
