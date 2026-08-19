// Exact fixed-order coverage replay for a forbidden-support hypergraph.
//
// Input:
//   q target vertex_count edge_count
//   edge_size vertex_1 ... vertex_edge_size
//
// Every recursion node branches on one fixed-order vertex.  An include branch
// is pruned exactly when it completes an edge whose last vertex is the current
// one.  Cardinality pruning is exact.  There is no SAT/MIP/LP dependency.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <unordered_set>
#include <vector>

using U64 = std::uint64_t;

int nvertices;
int target;
std::vector<int> order;
std::vector<std::vector<U64>> blockers;
std::uint64_t nodes = 0;
std::uint64_t edge_prunes = 0;
std::uint64_t cardinality_prunes = 0;
U64 witness = 0;

bool find_uncovered(int place, U64 selected, int count) {
  ++nodes;
  if (count == target) {
    witness = selected;
    return true;
  }
  if (count + nvertices - place < target) {
    ++cardinality_prunes;
    return false;
  }
  if (place == nvertices) return false;

  bool completes_edge = false;
  for (U64 rest : blockers[place]) {
    if ((rest & selected) == rest) {
      completes_edge = true;
      break;
    }
  }
  U64 bit = U64{1} << order[place];
  if (!completes_edge) {
    if (find_uncovered(place + 1, selected | bit, count + 1)) return true;
  } else {
    ++edge_prunes;
  }
  return find_uncovered(place + 1, selected, count);
}

int main() {
  std::ios::sync_with_stdio(false);
  int q, edge_count;
  if (!(std::cin >> q >> target >> nvertices >> edge_count)) {
    std::cerr << "bad header\n";
    return 2;
  }
  if (q <= 0 || q * q != nvertices || nvertices > 63 || target <= 0 ||
      target > nvertices || edge_count <= 0) {
    std::cerr << "invalid header\n";
    return 2;
  }
  std::vector<U64> edges;
  std::vector<int> degree(nvertices, 0);
  std::unordered_set<U64> unique;
  for (int edge_number = 0; edge_number < edge_count; ++edge_number) {
    int size;
    if (!(std::cin >> size) || size <= 0 || size > nvertices) {
      std::cerr << "bad edge size\n";
      return 2;
    }
    U64 edge = 0;
    for (int j = 0; j < size; ++j) {
      int vertex;
      if (!(std::cin >> vertex) || vertex < 0 || vertex >= nvertices) {
        std::cerr << "bad edge vertex\n";
        return 2;
      }
      U64 bit = U64{1} << vertex;
      if (edge & bit) {
        std::cerr << "repeated edge vertex\n";
        return 2;
      }
      edge |= bit;
      ++degree[vertex];
    }
    if (!unique.insert(edge).second) {
      std::cerr << "duplicate edge\n";
      return 2;
    }
    edges.push_back(edge);
  }
  std::string trailing;
  if (std::cin >> trailing) {
    std::cerr << "trailing data\n";
    return 2;
  }

  order.resize(nvertices);
  std::iota(order.begin(), order.end(), 0);
  std::sort(order.begin(), order.end(), [&](int left, int right) {
    return degree[left] == degree[right] ? left < right
                                        : degree[left] > degree[right];
  });
  std::vector<int> position(nvertices);
  for (int place = 0; place < nvertices; ++place) position[order[place]] = place;
  blockers.assign(nvertices, {});
  for (U64 edge : edges) {
    int last_vertex = -1;
    int last_place = -1;
    for (int vertex = 0; vertex < nvertices; ++vertex) {
      if (((edge >> vertex) & 1) && position[vertex] > last_place) {
        last_vertex = vertex;
        last_place = position[vertex];
      }
    }
    blockers[last_place].push_back(edge & ~(U64{1} << last_vertex));
  }

  if (find_uncovered(0, 0, 0)) {
    std::cout << "FAIL uncovered target support";
    for (int vertex = 0; vertex < nvertices; ++vertex) {
      if ((witness >> vertex) & 1) std::cout << ' ' << vertex;
    }
    std::cout << '\n';
    return 1;
  }
  std::cout << "HYPERGRAPH_EDGES " << edges.size() << '\n';
  std::cout << "SEARCH_NODES " << nodes << '\n';
  std::cout << "EDGE_PRUNES " << edge_prunes << '\n';
  std::cout << "CARDINALITY_PRUNES " << cardinality_prunes << '\n';
  std::cout << "CAPACITY_AT_MOST " << target - 1 << '\n';
  std::cout << "PASS fixed-order exhaustive Boolean wall\n";
  return 0;
}
