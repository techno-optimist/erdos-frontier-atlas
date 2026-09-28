"""Reference code for the Erdős #1109 certificate: records of OEIS A392164.

f(N) = A392164(N) is the size of the largest S in {1..N} such that every
element of S + S (including a + a) is squarefree; A392165 lists the N at which
f(N) reaches a new record.

A record at N forces N into S, so 2N is squarefree: N is odd and squarefree,
and so is every element of S (a + a = 2a).  Two odd numbers sum to a squarefree
number only if they agree mod 4, so S sits in one class mod 4.  Hence f(N) =
f(N - 1) + 1 exactly when the graph on
  V_N = { a < N : 2a and a + N squarefree },  a ~ b  iff  a + b squarefree,
has a clique of size f(N - 1); otherwise f(N) = f(N - 1).

Clique is the search; the C engine sqclique.c is its port, node for node.
Both colour the candidates greedily (lowest vertex first) and branch from the
last colour class, pruning when |R| + colour < target.
"""


def squarefree_table(M):
    sqf = bytearray([1]) * (M + 1)
    sqf[0] = 0
    p = 2
    while p * p <= M:
        for m in range(p * p, M + 1, p * p):
            sqf[m] = 0
        p += 1
    return sqf


def is_squarefree(m):
    if m < 1:
        return False
    p = 2
    while p * p <= m:
        if m % (p * p) == 0:
            return False
        p += 1
    return True


def sumset_squarefree(S):
    """Every a + b with a <= b in S (a = b included) is squarefree: checked by trial division."""
    S = sorted(S)
    return len(set(S)) == len(S) and all(is_squarefree(a + b) for i, a in enumerate(S) for b in S[i:])


def candidate_graph(N, sqf):
    V = [a for a in range(1, N) if sqf[2 * a] and sqf[a + N]]
    adj = [0] * len(V)
    for i, a in enumerate(V):
        m = 0
        for j, b in enumerate(V):
            if i != j and sqf[a + b]:
                m |= 1 << j
        adj[i] = m
    return V, adj


class Clique:
    """Decision search: is there a clique of size `target`?  (MCQ-style colouring bound.)"""

    def __init__(self, adj, target):
        self.adj, self.target = adj, target
        self.R, self.nodes, self.found = [], 0, None

    def expand(self, P):
        self.nodes += 1
        order, color, U, col = [], [], P, 0
        while U:
            col += 1
            Q = U
            while Q:
                low = Q & -Q
                v = low.bit_length() - 1
                Q &= ~low
                U &= ~low
                Q &= ~self.adj[v]
                order.append(v)
                color.append(col)
        for k in range(len(order) - 1, -1, -1):
            if len(self.R) + color[k] < self.target:
                return False
            v = order[k]
            self.R.append(v)
            if len(self.R) == self.target:
                self.found = list(self.R)
                return True
            NP = P & self.adj[v]
            if NP and self.expand(NP):
                return True
            self.R.pop()
            P &= ~(1 << v)
        return False

    def run(self):
        if self.target == 0:
            self.found = []
            return True
        return self.expand((1 << len(self.adj)) - 1)


def records(nmax):
    """[(k, N, |V_N|, nodes, witness or None)] for every candidate N <= nmax, in order;
    witness is the record set when N is a record."""
    sqf = squarefree_table(2 * nmax + 2)
    f, out = 0, []
    for N in range(1, nmax + 1):
        if not sqf[2 * N]:
            continue
        V, adj = candidate_graph(N, sqf)
        c = Clique(adj, f)
        if c.run():
            f += 1
            out.append((f, N, len(V), c.nodes, sorted([V[i] for i in c.found] + [N])))
        else:
            out.append((f + 1, N, len(V), c.nodes, None))
    return out
