#!/usr/bin/env python3
"""Exact tools for pancyclic chord systems C_n + k chords (Erdős #1016).

Standard library only; integers only.  A pancyclic graph on n vertices has a
Hamilton cycle, so it is C_n plus some chords, and m(n) = n + h(n) where h(n)
is the least number of chords making C_n pancyclic.

Layers
------
1. Skeletons.  Put the t chord endpoints in cyclic order along C_n.  A system
   of k chords is then a set of k distinct pairs of {0..t-1} using every
   point, plus the t arc lengths x_0..x_{t-1} (arc i runs from endpoint i to
   endpoint i+1 mod t), with sum n.  ``skeleton_classes`` lists one skeleton
   per orbit of the dihedral group of the cyclic order.
2. Cycle forms.  An interior arc vertex has degree 2, so a cycle uses an arc
   entirely or not at all; each cycle is a connected 2-regular sub-multigraph
   of the skeleton with length (#chords used) + (sum of the arcs used).  For a
   chord subset S with endpoint degrees d_i, evenness forces the arc
   indicator to satisfy r_i = r_{i-1} xor (d_i mod 2), which leaves r and its
   complement; ``cycle_forms`` keeps those that are connected with every
   degree in {0, 2}.
3. Search.  ``Search`` decides exactly whether some integer arc lengths
   (x_i >= 1, and x_i >= 2 when a chord joins the two ends of arc i, else
   that chord would duplicate a cycle edge) with sum n realise every length
   3..n.  Its two exclusion rules and its branching rule are stated in the
   class docstring; together they are exhaustive.
4. ``graph_cycle_lengths`` walks the actual graph C_n + chords by DFS.  It
   shares no code with layers 1-3 and is used to re-check every witness.
"""
from __future__ import annotations

from math import comb


# ------------------------------------------------------------- skeletons

def covering_chord_sets(t, k):
    """All sets of k distinct pairs of {0..t-1} (as sorted tuples of sorted
    pairs, in lexicographic order) whose union is all of {0..t-1}."""
    pairs = [(a, b) for a in range(t) for b in range(a + 1, t)]
    full = (1 << t) - 1
    out = []

    def rec(start, chosen, used, left):
        if left == 0:
            if used == full:
                out.append(tuple(chosen))
            return
        if t - bin(used).count("1") > 2 * left:
            return
        u = 0                                  # least point not yet used
        while u < t and used >> u & 1:
            u += 1
        for idx in range(start, len(pairs)):
            a, b = pairs[idx]
            if u < t and a > u:                # later pairs cannot contain u
                break
            chosen.append((a, b))
            rec(idx + 1, chosen, used | (1 << a) | (1 << b), left - 1)
            chosen.pop()

    rec(0, [], 0, k)
    return out


def labeled_count_formula(t, k):
    """Inclusion-exclusion count of k-sets of pairs of {0..t-1} covering it."""
    return sum((-1) ** j * comb(t, j) * comb(comb(t - j, 2), k)
               for j in range(t + 1))


def dihedral_canon(chords, t):
    """Lexicographically least image of a chord set under the dihedral group
    of the cyclic order of its t endpoints."""
    best = None
    for s in range(t):
        for sign in (1, -1):
            img = []
            for a, b in chords:
                a2, b2 = (sign * a + s) % t, (sign * b + s) % t
                img.append((a2, b2) if a2 < b2 else (b2, a2))
            img = tuple(sorted(img))
            if best is None or img < best:
                best = img
    return best


def skeleton_classes(k):
    """(classes, labeled): classes = sorted list of (t, chords), one per
    dihedral orbit; labeled = {t: number of labeled covering chord sets}."""
    seen = set()
    labeled = {}
    for t in range(2, 2 * k + 1):
        sets = covering_chord_sets(t, k)
        if sets:
            labeled[t] = len(sets)
        for chords in sets:
            seen.add((t, dihedral_canon(chords, t)))
    return sorted(seen), labeled


def arc_lower_bounds(t, chords):
    """x_i >= 2 if some chord joins the ends of arc i, otherwise x_i >= 1."""
    lb = [1] * t
    for a, b in chords:
        for i in range(t):
            if {a, b} == {i, (i + 1) % t}:
                lb[i] = 2
    return lb


# ----------------------------------------------------------- cycle forms

def _connected(t, chords, sub, mask):
    parent = list(range(t))

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    touched = 0
    for idx, (a, b) in enumerate(chords):
        if sub >> idx & 1:
            parent[find(a)] = find(b)
            touched |= (1 << a) | (1 << b)
    for i in range(t):
        if mask >> i & 1:
            j = (i + 1) % t
            parent[find(i)] = find(j)
            touched |= (1 << i) | (1 << j)
    roots = {find(u) for u in range(t) if touched >> u & 1}
    return touched != 0 and len(roots) == 1


def cycle_forms(t, chords):
    """Every cycle of the skeleton as a distinct (chord_count, arc_mask)."""
    k = len(chords)
    full = (1 << t) - 1
    forms = {(0, full)}                        # the Hamilton cycle
    for sub in range(1, 1 << k):
        deg = [0] * t
        for idx, (a, b) in enumerate(chords):
            if sub >> idx & 1:
                deg[a] += 1
                deg[b] += 1
        if max(deg) > 2:
            continue
        mask, r = 0, 0                         # r_{-1} = r_{t-1} = 0
        for i in range(t):
            r ^= deg[i] & 1
            if r:
                mask |= 1 << i
        if mask >> (t - 1) & 1:
            raise AssertionError("parity recurrence inconsistent")
        for m in (mask, full ^ mask):
            if all(deg[i] + (m >> ((i - 1) % t) & 1) + (m >> i & 1) in (0, 2)
                   for i in range(t)) and _connected(t, chords, sub, m):
                forms.add((bin(sub).count("1"), m))
    return sorted(forms)


def evaluate(forms, x):
    """Set of cycle lengths realised by the arc lengths x."""
    out = set()
    for c, mask in forms:
        s, i = c, 0
        while mask:
            if mask & 1:
                s += x[i]
            mask >>= 1
            i += 1
        out.add(s)
    return out


def realise(t, chords, x):
    """(n, chords on C_n) for skeleton chords with arc lengths x; endpoint 0
    is placed at vertex 0."""
    pos = [0] * t
    for i in range(1, t):
        pos[i] = pos[i - 1] + x[i - 1]
    n = pos[-1] + x[-1]
    return n, sorted(tuple(sorted((pos[a], pos[b]))) for a, b in chords)


def skeleton_of(n, chords):
    """Inverse of ``realise``: (t, skeleton chords, arc lengths) of C_n + chords."""
    ends = sorted({u for c in chords for u in c})
    t = len(ends)
    idx = {e: i for i, e in enumerate(ends)}
    sk = tuple(sorted(tuple(sorted((idx[u], idx[v]))) for u, v in chords))
    x = [(ends[(i + 1) % t] - ends[i]) % n or n for i in range(t)]
    return t, sk, x


# --------------------------------------------------------------- search

def _weak_compositions(s, m):
    if m == 1:
        yield (s,)
        return
    for first in range(s + 1):
        for rest in _weak_compositions(s - first, m - 1):
            yield (first,) + rest


class Search:
    """Exact decision for one skeleton at order n.

    State: tuple of arc lengths, 0 meaning "free".  A free arc i will carry
    x_i = lb_i + y_i with y_i >= 0, and the y's of the free arcs sum to the
    slack R.  Given a state, a form whose free arcs are none or all of the
    free arcs has a known value (constant); any other form can take exactly
    the values a..a+R (put the remainder on a free arc outside the form).

    Exclusion (each discards only states with no pancyclic completion):
      capacity - a non-constant form realises one value in any completion, so
                 fewer distinct non-constant forms that can reach an uncovered
                 length than uncovered lengths means no completion;
      domain   - some uncovered length is reachable by no form.
    Branching (exhaustive): pick an uncovered length l.  In a pancyclic
      completion some non-constant form equals l, i.e. the y's on its free
      arcs sum to q = l - a.  For each such form enumerate either every
      assignment of those arcs with sum q or every assignment of the other
      free arcs with sum R - q (these describe the same completions because
      the total is R).  Each child fixes at least one more arc, so the
      recursion terminates.  Children may overlap; that costs time, not
      soundness.  The choice of l only affects speed.
    """

    def __init__(self, t, chords, n, forms=None):
        self.t, self.chords, self.n = t, tuple(chords), n
        self.forms = forms if forms is not None else cycle_forms(t, chords)
        self.fidx = [(c, tuple(i for i in range(t) if m >> i & 1), m)
                     for c, m in self.forms]
        self.lb = arc_lower_bounds(t, chords)
        self.dead = set()
        self.nodes = 0
        self.W = [[1 if s == 0 else 0 for s in range(n + 1)]] + \
                 [[comb(s + m - 1, m - 1) for s in range(n + 1)]
                  for m in range(1, t + 1)]

    def covers(self, x):
        vals = evaluate(self.forms, x)
        return all(l in vals for l in range(3, self.n + 1))

    def run(self):
        if sum(self.lb) > self.n:
            return None
        return self._dfs(tuple([0] * self.t))

    def _dfs(self, state):
        if state in self.dead:
            return None
        self.nodes += 1
        t, n, lb = self.t, self.n, self.lb
        free = [i for i in range(t) if state[i] == 0]
        R = n - sum(state) - sum(lb[i] for i in free)
        if R < 0:
            self.dead.add(state)
            return None
        if len(free) <= 1:
            x = list(state)
            if free:
                x[free[0]] = lb[free[0]] + R
            if self.covers(x):
                return x
            self.dead.add(state)
            return None
        free_mask = 0
        for i in free:
            free_mask |= 1 << i
        nfree = len(free)
        base = [state[i] or lb[i] for i in range(t)]
        covered = bytearray(n + 2)
        resid = set()
        for c, idx, mask in self.fidx:
            a = c
            for i in idx:
                a += base[i]
            mf = mask & free_mask
            if mf == 0:
                if a <= n:
                    covered[a] = 1
            elif mf == free_mask:
                if a + R <= n:
                    covered[a + R] = 1
            else:
                resid.add((a, mf))
        need = [l for l in range(3, n + 1) if not covered[l]]
        if not need:
            x = list(base)
            x[free[0]] += R
            if not self.covers(x):
                raise AssertionError("constant forms cover but evaluation disagrees")
            return x
        lo, hi = need[0], need[-1]
        useful = [(a, mf) for (a, mf) in resid if a <= hi and a + R >= lo]
        if len(useful) < len(need):                          # capacity
            self.dead.add(state)
            return None
        diff = [0] * (n + 3)
        for a, _ in useful:
            s, e = max(a, 3), min(a + R, n)
            if s <= e:
                diff[s] += 1
                diff[e + 1] -= 1
        ncand, run = [0] * (n + 1), 0
        for l in range(n + 1):
            run += diff[l]
            ncand[l] = run
        if any(ncand[l] == 0 for l in need):                 # domain
            self.dead.add(state)
            return None
        # speed only: cost the fewest-candidate lengths and both extremes
        short = sorted(need, key=lambda l: (ncand[l], l))[:4]
        for l in (need[0], need[-1]):
            if l not in short:
                short.append(l)
        W = self.W
        best = None
        for l in short:
            cost = 0
            for a, mf in useful:
                if a <= l <= a + R:
                    k1 = bin(mf).count("1")
                    q = l - a
                    c1, c2 = W[k1][q], W[nfree - k1][R - q]
                    cost += c1 if c1 < c2 else c2
            if best is None or cost < best[0]:
                best = (cost, l)
        l = best[1]
        for a, mf in sorted(u for u in useful if u[0] <= l <= u[0] + R):
            k1 = bin(mf).count("1")
            q = l - a
            if W[k1][q] <= W[nfree - k1][R - q]:
                side, total = mf, q
            else:
                side, total = free_mask ^ mf, R - q
            idx = [i for i in free if side >> i & 1]
            for comp in _weak_compositions(total, len(idx)):
                child = list(state)
                for i, y in zip(idx, comp):
                    child[i] = lb[i] + y
                res = self._dfs(tuple(child))
                if res is not None:
                    return res
        self.dead.add(state)
        return None


def decide(t, chords, n, forms=None):
    """(arc lengths or None, nodes) for one skeleton at order n."""
    s = Search(t, chords, n, forms)
    return s.run(), s.nodes


def decide_task(task):
    """Picklable worker: task = (t, chords, forms, n) -> (x or None, nodes)."""
    t, chords, forms, n = task
    return decide(t, chords, n, forms)


def forms_task(task):
    """Picklable worker: task = (t, chords) -> cycle forms."""
    t, chords = task
    return cycle_forms(t, chords)


def family_f(n):
    """The 6-chord family of Pinckard et al. (2026), pancyclic for 41 <= n <= 67
    by their Lean check; re-checked here by DFS, never assumed."""
    return [(0, 2), (0, n - 7), (1, 13), (3, n - 6), (4, 31), (n - 8, n - 5)]


# ------------------------------------------------- independent graph check

def graph_cycle_lengths(n, chords):
    """Cycle lengths of C_n + chords by DFS over simple cycles of the graph.

    Every cycle contains a chord endpoint (the Hamilton cycle contains all of
    them, any other cycle uses a chord), so each cycle is rooted at its least
    chord endpoint s; the DFS passes freely through other vertices but only
    through endpoints larger than s.  Raises on loops, out-of-range vertices
    and duplicate edges (a chord equal to a cycle edge or to another chord).
    """
    if n < 3:
        raise ValueError("need n >= 3")
    adj = [set() for _ in range(n)]
    for v in range(n):
        adj[v].add((v + 1) % n)
        adj[(v + 1) % n].add(v)
    for u, v in chords:
        if not (0 <= u < n and 0 <= v < n) or u == v or v in adj[u]:
            raise ValueError(f"chord {(u, v)} is a loop, out of range, or a duplicate edge")
        adj[u].add(v)
        adj[v].add(u)
    if not chords:
        return {n}
    adj = [sorted(a) for a in adj]
    ends = sorted({u for c in chords for u in c})
    is_end = [False] * n
    for u in ends:
        is_end[u] = True
    lengths = set()
    for s in ends:
        stack = [(s, 1, 1 << s)]
        while stack:
            v, length, seen = stack.pop()
            for w in adj[v]:
                if w == s:
                    if length >= 3:
                        lengths.add(length)
                elif not (seen >> w & 1) and (not is_end[w] or w > s):
                    stack.append((w, length + 1, seen | (1 << w)))
    return lengths


def is_pancyclic(n, chords):
    lens = graph_cycle_lengths(n, chords)
    return all(l in lens for l in range(3, n + 1))
