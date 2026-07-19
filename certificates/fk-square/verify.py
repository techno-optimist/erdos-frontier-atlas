#!/usr/bin/env python3
"""Independent, dependency-free verifier for the Furstenberg-Katznelson
axis-aligned-square table D(N).

Problem: D(N) = max |A|, A a subset of the grid [N]^2, such that A contains
NO axis-aligned square {(x,y), (x+d,y), (x,y+d), (x+d,y+d)} with d >= 1
(all four corners in A).  The Furstenberg-Katznelson multidimensional
Szemeredi theorem (1978) says any A of positive density contains such a
square once N is sufficiently large -- with no threshold from the ergodic
proof.  This certificate is the exact finite table, which the theorem does
not give.  The finite values coincide with OEIS A227133.

Checks, all exact:
  1. every stored witness lies in [1,N]^2, has the claimed size D(N), and
     passes an O(N^3) square-free scan;
  2. planted-square negative controls: witness + a planted square, and the
     full grid, are both flagged by the same scan (the scan can fail);
  3. D(N) is recomputed for N <= 4 by EXHAUSTIVE enumeration -- all 2^(N^2)
     subsets of the grid are checked, no pruning, no shortcuts;
  3b. D(N) is recomputed for N <= 6 by a structurally different cell-level
     DFS (include/exclude per cell, square-completion pruning + the trivial
     count bound only -- no row model, no symmetry breaking, no pair caps);
  4. D(N) is recomputed for every certified N by branch-and-bound over rows:
     a search at target D(N) must find a square-free configuration of that
     size (re-checked by the scan), and a search at target D(N)+1 must
     exhaust with no configuration found;
  5. sanity: D is non-decreasing and D(N+1) <= D(N) + 2N + 1;
  6. the density fence table (last N with D(N) >= ceil(c*N^2) for
     c = 1/2, 1/3, 1/4) is recomputed and must match the stored one.
Exit 0 iff everything holds.

Runtime: dominated by the branch-and-bound replay of the largest N
(the same computation that produced the table; see README).
"""
import json
import sys
import time
from pathlib import Path


# ----------------------------------------------------------------------
# square-free scan (the simple, independent check used on witnesses)
# ----------------------------------------------------------------------

def contains_square(cells, N):
    """O(N^3) scan: True iff the cell set contains an axis-aligned square."""
    s = set(map(tuple, cells))
    for (x, y) in s:
        for d in range(1, N):
            if x + d <= N and y + d <= N \
                    and (x + d, y) in s and (x, y + d) in s \
                    and (x + d, y + d) in s:
                return True
    return False


# ----------------------------------------------------------------------
# exhaustive enumeration for N <= 4: all 2^(N^2) subsets, no pruning
# ----------------------------------------------------------------------

def brute_force_max(N):
    """Max square-free subset size by checking every subset of [N]^2."""
    idx = {}
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            idx[(x, y)] = len(idx)
    quads = []
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            for d in range(1, N):
                if x + d <= N and y + d <= N:
                    quads.append((1 << idx[(x, y)]) |
                                 (1 << idx[(x + d, y)]) |
                                 (1 << idx[(x, y + d)]) |
                                 (1 << idx[(x + d, y + d)]))
    best = 0
    for mask in range(1 << (N * N)):
        ok = True
        for q in quads:
            if mask & q == q:
                ok = False
                break
        if ok:
            c = bin(mask).count("1")
            if c > best:
                best = c
    return best


# ----------------------------------------------------------------------
# independent cell-level DFS for N <= 6 (a second, different method)
# ----------------------------------------------------------------------

def cell_dfs_max(N):
    """Max square-free subset size by include/exclude DFS over cells in
    row-major order.  Prunes only on square completion and on
    chosen + remaining <= best.  Shares no code or model with FKSolver."""
    cells = [(x, y) for y in range(1, N + 1) for x in range(1, N + 1)]
    n = len(cells)
    idx = {c: i for i, c in enumerate(cells)}
    completions = [[] for _ in range(n)]
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            for d in range(1, N):
                if x + d <= N and y + d <= N:
                    quad = [idx[(x, y)], idx[(x + d, y)],
                            idx[(x, y + d)], idx[(x + d, y + d)]]
                    last = max(quad)  # decided last in row-major order
                    completions[last].append(
                        tuple(q for q in quad if q != last))
    best = [0]
    chosen = bytearray(n)

    def dfs(i, cnt):
        if cnt + (n - i) <= best[0]:
            return
        if i == n:
            best[0] = cnt
            return
        ok = True
        for (a, b, c) in completions[i]:
            if chosen[a] and chosen[b] and chosen[c]:
                ok = False
                break
        if ok:
            chosen[i] = 1
            dfs(i + 1, cnt + 1)
            chosen[i] = 0
        dfs(i + 1, cnt)

    dfs(0, 0)
    return best[0]


# ----------------------------------------------------------------------
# branch and bound (row model) -- the recompute engine
# ----------------------------------------------------------------------
# A configuration is (S_1..S_N), S_y = bitmask of columns chosen in row y.
# It contains an axis-aligned square iff for some rows y < y' at distance
# d = y' - y the intersection T = S_y & S_y' has two columns exactly d
# apart, i.e. T & (T >> d) != 0.  The decision search "is there a
# square-free configuration of total size >= m" assigns rows top to
# bottom, keeping for each unassigned row the set of still-feasible masks
# as one big integer (bit i <=> mask i feasible).
#
# Exactness-preserving reductions (they preserve the YES/NO answer):
#  * column flip and vertical flip map square-free configurations to
#    square-free configurations of the same size, so the search may
#    restrict row 1 to masks M >= reverse(M) and require
#    popcount(S_N) <= popcount(S_1): any solution's orbit under the two
#    flips contains a representative satisfying both;
#  * pair cap: rows at distance d intersect in a set with no two columns
#    exactly d apart, whose max size is alpha_d(N), so
#    |S_a| + |S_b| <= N + alpha_d(N) -- used only to prune bounds.

def alpha_d(N, d):
    """Max size of a subset of {0..N-1} with no two elements exactly d apart."""
    return sum((len(range(r, N, d)) + 1) // 2 for r in range(d))


class FKSolver:
    def __init__(self, N):
        self.N = N
        nm = 1 << N
        self.pc = [bin(m).count("1") for m in range(nm)]
        rev = [0] * nm
        for m in range(nm):
            v = 0
            for i in range(N):
                if (m >> i) & 1:
                    v |= 1 << (N - 1 - i)
            rev[m] = v
        self.level = [0] * (N + 1)
        for m in range(nm):
            self.level[self.pc[m]] |= 1 << m
        acc = 0
        self.level_le = [0] * (N + 1)
        for k in range(N + 1):
            acc |= self.level[k]
            self.level_le[k] = acc
        self.all_set = acc
        self.row0_set = 0
        for m in range(nm):
            if m >= rev[m]:
                self.row0_set |= 1 << m
        self.compat = [None] * N
        self.cap = [0] * N
        for d in range(1, N):
            self.cap[d] = N + alpha_d(N, d)
        self.nodes = 0

    def _compat_row(self, d):
        c = self.compat[d]
        if c is None:
            nm = 1 << self.N
            c = [0] * nm
            for M in range(nm):
                v = 0
                for m2 in range(nm):
                    t = M & m2
                    if not (t & (t >> d)):
                        v |= 1 << m2
                c[M] = v
            self.compat[d] = c
        return c

    def _pair_capped_sum(self, first, ub):
        """Upper bound on sum(ub[first:]) using the pair caps on adjacent
        rows (two disjoint pairings, take the smaller bound)."""
        N = self.N
        cap1 = self.cap[1] if N > 1 else 0
        best = None
        for off in (0, 1):
            tot = 0
            i = first
            if off == 1 and i < N:
                tot = ub[i]
                i += 1
            while i + 1 < N:
                s = ub[i] + ub[i + 1]
                if s > cap1:
                    s = cap1
                tot += s
                i += 2
            if i < N:
                tot += ub[i]
            if best is None or tot < best:
                best = tot
        return best

    def try_reach(self, m):
        """Return row masks with total >= m, or None if none exists."""
        N = self.N
        if m <= 0:
            return [0] * N
        self.cand_stack = [[0] * N for _ in range(N + 1)]
        self.ub_stack = [[0] * N for _ in range(N + 1)]
        for row in range(N):
            self.cand_stack[0][row] = self.all_set
            self.ub_stack[0][row] = N
        self.cand_stack[0][0] = self.row0_set
        self.assigned = [-1] * N
        self.m = m
        if self._dfs(0, 0):
            return list(self.assigned)
        return None

    def _dfs(self, row, placed):
        N = self.N
        if row == N:
            return placed >= self.m
        self.nodes += 1
        cand = self.cand_stack[row]
        ub = self.ub_stack[row]
        ncand = self.cand_stack[row + 1]
        nub = self.ub_stack[row + 1]
        level = self.level
        m = self.m
        others = self._pair_capped_sum(row + 1, ub)
        need = m - placed - others
        if need > ub[row]:
            return None
        lo = max(need, 0)
        rem_data = [(r2, self._compat_row(r2 - row))
                    for r2 in range(row + 1, N)]
        sym_last = (row == 0 and N >= 2)
        level_le = self.level_le
        assigned = self.assigned
        cand_row = cand[row]
        for k in range(ub[row], lo - 1, -1):
            x = cand_row & level[k]
            while x:
                b = x & -x
                x ^= b
                M = b.bit_length() - 1
                ok = True
                tot_rest = 0
                for r2, crow in rem_data:
                    c = cand[r2] & crow[M]
                    if sym_last and r2 == N - 1:
                        c &= level_le[k]
                    u = ub[r2]
                    while u >= 0 and not (c & level[u]):
                        u -= 1
                    if u < 0:
                        ok = False
                        break
                    ncand[r2] = c
                    nub[r2] = u
                    tot_rest += u
                if not ok or placed + k + tot_rest < m:
                    continue
                if placed + k + self._pair_capped_sum(row + 1, nub) < m:
                    continue
                assigned[row] = M
                if self._dfs(row + 1, placed + k):
                    return True
                assigned[row] = -1
        return None


def rows_to_cells(rowmasks):
    return sorted((x + 1, y + 1)
                  for y, mask in enumerate(rowmasks)
                  for x in range(mask.bit_length())
                  if (mask >> x) & 1)


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def ceil_div(a, b):
    return -(-a // b)


def main():
    doc = json.loads((Path(__file__).parent / "table.json").read_text())
    D = doc["D"]
    n_max = doc["n_max"]
    assert len(D) == n_max and n_max >= 4, "table shape"

    # 1. witnesses: in-grid, claimed size, square-free by the scan
    for N in range(1, n_max + 1):
        w = [tuple(c) for c in doc["witnesses"][str(N)]]
        assert len(w) == len(set(w)) == D[N - 1], f"witness size at N={N}"
        assert all(1 <= x <= N and 1 <= y <= N for x, y in w), \
            f"witness out of grid at N={N}"
        assert not contains_square(w, N), f"witness has a square at N={N}"

    # 2. negative controls: the scan must FLAG a planted square
    for N in range(2, n_max + 1):
        w = set(map(tuple, doc["witnesses"][str(N)]))
        planted = w | {(1, 1), (1, 2), (2, 1), (2, 2)}
        assert contains_square(planted, N), \
            f"negative control failed (planted square unflagged) at N={N}"
        full = [(x, y) for x in range(1, N + 1) for y in range(1, N + 1)]
        assert contains_square(full, N), \
            f"negative control failed (full grid unflagged) at N={N}"

    # 3. exhaustive cross-check for N <= 4 (independent method: ALL subsets)
    for N in range(1, 5):
        assert brute_force_max(N) == D[N - 1], f"brute-force mismatch at N={N}"

    # 3b. cell-level DFS cross-check for N <= 6 (second independent method)
    for N in range(1, 7):
        assert cell_dfs_max(N) == D[N - 1], f"cell-DFS mismatch at N={N}"

    # 4. branch-and-bound recompute for every N
    t0 = time.time()
    for N in range(2, n_max + 1):
        sol = FKSolver(N)
        found = sol.try_reach(D[N - 1])
        assert found is not None, f"B&B could not reach D({N})={D[N-1]}"
        cells = rows_to_cells(found)
        assert len(cells) >= D[N - 1] and not contains_square(cells, N), \
            f"B&B returned an invalid configuration at N={N}"
        assert sol.try_reach(D[N - 1] + 1) is None, \
            f"B&B found a configuration BEATING the table at N={N}"
        print(f"  recomputed D({N}) = {D[N-1]}  "
              f"[{time.time()-t0:.1f}s cumulative]", file=sys.stderr)

    # 5. sanity invariants
    assert D[0] == 1, "D(1) != 1"
    for N in range(2, n_max + 1):
        assert D[N - 1] >= D[N - 2], f"D not monotone at N={N}"
        assert D[N - 1] <= D[N - 2] + 2 * (N - 1) + 1, \
            f"D grows too fast at N={N}"

    # 6. fence recompute
    fence = {}
    for label, p, q in (("1/2", 1, 2), ("1/3", 1, 3), ("1/4", 1, 4)):
        last = None
        for N in range(1, n_max + 1):
            if D[N - 1] >= ceil_div(p * N * N, q):
                last = N
        stored = doc["fence"][label]
        assert stored["last_N_with_D_ge_ceil_c_N2"] == last, \
            f"fence mismatch at c={label}"
        assert stored["crossed_within_computed_range"] == \
            (last is not None and last < n_max), f"fence flag at c={label}"
        fence[label] = last

    print(json.dumps({
        "valid": True,
        "n_max": n_max,
        "D": D,
        "fence_last_N_with_density_at_least_c": fence,
        "note": ("certifies the computed range 1..%d ONLY; the "
                 "Furstenberg-Katznelson threshold itself is not certified "
                 "by any finite table -- larger exceptions are not excluded"
                 % n_max),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
