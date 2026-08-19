// Solver-independent exhaustive verifier for a certified forbidden hypergraph.
//
// Input format:
//   q target vertex_count edge_count
//   edge_size vertex_1 ... vertex_edge_size
//   ...
//
// The search partitions all Boolean assignments into include/exclude branches.
// Unit propagation excludes the last unchosen vertex of a forbidden edge.
// Cardinality leaves and completed-edge leaves are exact.  No SAT/MIP library
// or floating-point arithmetic is used.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <unordered_set>
#include <vector>

using U64 = std::uint64_t;

struct State {
  U64 selected;
  U64 undecided;
  bool operator==(State const& other) const {
    return selected == other.selected && undecided == other.undecided;
  }
};

struct StateHash {
  std::size_t operator()(State const& state) const {
    U64 x = state.selected + 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    x ^= x >> 31;
    return static_cast<std::size_t>(x ^ (state.undecided * 0x9e3779b97f4a7c15ULL));
  }
};

int vertex_count;
int target;
std::vector<U64> edges;
std::vector<std::vector<int>> incidence;
std::unordered_set<State, StateHash> proved_dead;
std::uint64_t nodes = 0;
std::uint64_t conflict_leaves = 0;
std::uint64_t cardinality_leaves = 0;
std::uint64_t memo_leaves = 0;
std::uint64_t unit_exclusions = 0;
U64 witness = 0;

static inline int popcount(U64 value) { return __builtin_popcountll(value); }
static inline int trailing_zeroes(U64 value) { return __builtin_ctzll(value); }

bool search(U64 selected, U64 undecided) {
  ++nodes;
  for (;;) {
    U64 alive = selected | undecided;
    U64 forced_out = 0;
    for (U64 edge : edges) {
      if (edge & ~alive) continue;  // An excluded vertex already satisfies it.
      U64 residual = edge & ~selected;
      if (!residual) {
        ++conflict_leaves;
        return false;
      }
      if (!(residual & (residual - 1))) forced_out |= residual;
    }
    forced_out &= undecided;
    if (!forced_out) break;
    unit_exclusions += static_cast<std::uint64_t>(popcount(forced_out));
    undecided &= ~forced_out;
  }

  // Conflict propagation precedes this test, so selected is edge-free.
  if (popcount(selected) >= target) {
    witness = selected;
    return true;
  }
  if (popcount(selected) + popcount(undecided) < target) {
    ++cardinality_leaves;
    return false;
  }

  State state{selected, undecided};
  if (proved_dead.find(state) != proved_dead.end()) {
    ++memo_leaves;
    return false;
  }
  // Recursion always decreases undecided, so this state cannot be revisited
  // before its proof finishes.  It is safe to memoize it at entry.
  proved_dead.insert(state);

  U64 alive = selected | undecided;
  int best_vertex = -1;
  int best_score = std::numeric_limits<int>::min();
  U64 remaining = undecided;
  while (remaining) {
    int vertex = trailing_zeroes(remaining);
    remaining &= remaining - 1;
    int score = 0;
    for (int edge_number : incidence[vertex]) {
      U64 edge = edges[edge_number];
      if (edge & ~alive) continue;
      int residual_size = popcount(edge & ~selected);
      score += 1 << std::max(0, 10 - residual_size);
    }
    if (score > best_score) {
      best_score = score;
      best_vertex = vertex;
    }
  }
  if (best_vertex < 0) {
    std::cerr << "internal error: no branch vertex\n";
    std::exit(2);
  }
  U64 bit = U64{1} << best_vertex;
  if (search(selected | bit, undecided & ~bit)) return true;
  if (search(selected, undecided & ~bit)) return true;
  return false;
}

int main() {
  std::ios::sync_with_stdio(false);
  int q, edge_count;
  if (!(std::cin >> q >> target >> vertex_count >> edge_count)) {
    std::cerr << "bad hypergraph header\n";
    return 2;
  }
  if (q <= 0 || q * q != vertex_count || vertex_count > 64 || target <= 0 ||
      target > vertex_count || edge_count <= 0) {
    std::cerr << "invalid hypergraph parameters\n";
    return 2;
  }
  std::unordered_set<U64> unique;
  for (int edge_number = 0; edge_number < edge_count; ++edge_number) {
    int size;
    if (!(std::cin >> size) || size <= 0 || size > vertex_count) {
      std::cerr << "bad edge size\n";
      return 2;
    }
    U64 edge = 0;
    for (int j = 0; j < size; ++j) {
      int vertex;
      if (!(std::cin >> vertex) || vertex < 0 || vertex >= vertex_count) {
        std::cerr << "bad edge vertex\n";
        return 2;
      }
      U64 bit = U64{1} << vertex;
      if (edge & bit) {
        std::cerr << "repeated vertex in edge\n";
        return 2;
      }
      edge |= bit;
    }
    if (!unique.insert(edge).second) {
      std::cerr << "duplicate edge\n";
      return 2;
    }
    edges.push_back(edge);
  }
  std::string trailing;
  if (std::cin >> trailing) {
    std::cerr << "trailing hypergraph data\n";
    return 2;
  }

  std::sort(edges.begin(), edges.end(), [](U64 left, U64 right) {
    int a = popcount(left), b = popcount(right);
    return a == b ? left < right : a < b;
  });
  incidence.assign(vertex_count, {});
  for (int edge_number = 0; edge_number < static_cast<int>(edges.size()); ++edge_number) {
    for (int vertex = 0; vertex < vertex_count; ++vertex) {
      if ((edges[edge_number] >> vertex) & 1) incidence[vertex].push_back(edge_number);
    }
  }

  U64 all_vertices = (vertex_count == 64)
      ? ~U64{0}
      : (U64{1} << vertex_count) - 1;
  bool found = search(0, all_vertices);
  if (found) {
    std::cout << "FAIL uncovered target support";
    for (int vertex = 0; vertex < vertex_count; ++vertex) {
      if ((witness >> vertex) & 1) std::cout << ' ' << vertex;
    }
    std::cout << "\n";
    return 1;
  }
  std::cout << "HYPERGRAPH_EDGES " << edges.size() << "\n";
  std::cout << "SEARCH_NODES " << nodes << "\n";
  std::cout << "PROVED_DEAD_STATES " << proved_dead.size() << "\n";
  std::cout << "CONFLICT_LEAVES " << conflict_leaves << "\n";
  std::cout << "CARDINALITY_LEAVES " << cardinality_leaves << "\n";
  std::cout << "MEMO_LEAVES " << memo_leaves << "\n";
  std::cout << "UNIT_EXCLUSIONS " << unit_exclusions << "\n";
  std::cout << "CAPACITY_AT_MOST " << target - 1 << "\n";
  std::cout << "PASS solver-independent exhaustive Boolean wall\n";
  return 0;
}
