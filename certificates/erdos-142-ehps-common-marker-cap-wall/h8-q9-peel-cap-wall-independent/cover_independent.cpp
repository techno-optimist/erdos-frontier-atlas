#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Mask = std::uint64_t;

static void need(bool ok, const std::string &why) {
  if (!ok) throw std::runtime_error(why);
}

static int point_id(int x, int y) { return 9*x+y; }

static int one_digit(const std::string &text) {
  need(text.size() == 1 && text[0] >= '0' && text[0] <= '8',
       "coordinate is not a canonical digit in 0..8");
  return text[0]-'0';
}

static int parse_point(const std::string &token) {
  const std::size_t comma = token.find(',');
  need(comma != std::string::npos && token.find(',', comma+1) == std::string::npos,
       "malformed coordinate token");
  return point_id(one_digit(token.substr(0, comma)),
                  one_digit(token.substr(comma+1)));
}

static unsigned count_bits(Mask value) {
  unsigned result = 0;
  while (value) {
    value &= value-1;
    ++result;
  }
  return result;
}

static std::array<std::pair<int,int>,12> fixed_template(int index) {
  if (index == 0) return {{{0,3},{0,6},{1,3},{1,6},{2,0},{2,3},
                           {3,0},{4,0},{4,3},{5,0},{5,3},{6,0}}};
  return {{{0,0},{0,3},{1,0},{1,6},{2,3},{2,6},
            {3,3},{4,0},{4,3},{5,0},{5,3},{6,0}}};
}

struct Edge {
  Mask vertices = 0;
  unsigned fibre_set = 0;
};

struct Instance {
  int index = -1;
  std::vector<int> allowed;
  std::array<int,81> local_of_point;
  std::array<int,54> fibre_of_local;
  std::array<std::vector<int>,6> fibres;
  std::vector<Edge> edges;
  std::array<int,7> histogram;
};

static Instance load_instance(const std::string &root, int index) {
  need(index == 0 || index == 1, "template index must be 0 or 1");
  const std::string path = root+"/data/template"+std::to_string(index)+"_blockers.txt";
  std::ifstream stream(path, std::ios::binary);
  need(bool(stream), "cannot open blocker ledger");
  const std::string bytes((std::istreambuf_iterator<char>(stream)),
                          std::istreambuf_iterator<char>());
  need(!bytes.empty() && bytes.back() == '\n' && bytes.find('\r') == std::string::npos,
       "ledger is not nonempty LF-only text");

  std::vector<std::vector<int>> rows;
  std::istringstream lines(bytes);
  std::string line;
  while (std::getline(lines, line)) {
    need(!line.empty(), "blank blocker line");
    std::istringstream tokens(line);
    std::vector<int> row;
    std::array<bool,81> seen{};
    std::string token;
    while (tokens >> token) {
      const int point = parse_point(token);
      need(!seen[point], "duplicate point in blocker");
      seen[point] = true;
      row.push_back(point);
    }
    need(!row.empty() && row.size() <= 6, "bad blocker size");
    need(std::is_sorted(row.begin(), row.end()), "unsorted blocker points");
    if (!rows.empty()) {
      need(std::make_pair(rows.back().size(), rows.back()) <
           std::make_pair(row.size(), row), "noncanonical blocker ledger");
    }
    rows.push_back(row);
  }

  Instance out;
  out.index = index;
  out.local_of_point.fill(-1);
  out.histogram.fill(0);
  for (const auto &row : rows) ++out.histogram[row.size()];
  const std::array<int,7> h0{{0,15,0,297,3177,11619,0}};
  const std::array<int,7> h1{{0,15,0,297,3798,9,27}};
  need(out.histogram == (index == 0 ? h0 : h1), "blocker histogram drift");

  std::array<bool,81> fixed{};
  for (const auto &xy : fixed_template(index)) {
    const int point = point_id(xy.first, xy.second);
    need(!fixed[point], "duplicate template point");
    fixed[point] = true;
  }
  std::array<bool,81> singleton{};
  for (const auto &row : rows) if (row.size() == 1) {
    need(!fixed[row.front()], "singleton intersects template");
    singleton[row.front()] = true;
  }
  for (int point = 0; point < 81; ++point) {
    if (!fixed[point] && !singleton[point]) {
      out.local_of_point[point] = int(out.allowed.size());
      out.allowed.push_back(point);
    }
  }
  need(out.allowed.size() == 54, "allowed census is not 54");

  std::map<std::pair<int,int>,std::vector<int>> residue_groups;
  for (int local = 0; local < 54; ++local) {
    const int point = out.allowed[local];
    residue_groups[{(point/9)%3,(point%9)%3}].push_back(local);
  }
  need(residue_groups.size() == 6, "allowed points do not form six fibres");
  int f = 0;
  for (const auto &entry : residue_groups) {
    need(entry.second.size() == 9, "allowed fibre does not have nine points");
    out.fibres[f] = entry.second;
    for (int local : entry.second) out.fibre_of_local[local] = f;
    ++f;
  }

  for (const auto &row : rows) if (row.size() >= 2) {
    Edge edge;
    for (int point : row) {
      const int local = out.local_of_point[point];
      need(local >= 0, "nonsingleton blocker contains unavailable point");
      edge.vertices |= Mask(1) << local;
      edge.fibre_set |= unsigned(1) << out.fibre_of_local[local];
    }
    out.edges.push_back(edge);
  }
  need(out.edges.size() == (index == 0 ? 15093u : 4131u),
       "nonsingleton blocker count drift");
  return out;
}

static int midpoint_id(int a, int b) {
  const int ax = a/9, ay = a%9, bx = b/9, by = b%9;
  return point_id((5*(ax+bx))%9, (5*(ay+by))%9);
}

static bool is_local_cap(const Instance &instance, Mask chosen) {
  std::vector<int> points;
  for (int local = 0; local < 54; ++local)
    if ((chosen >> local) & 1) points.push_back(instance.allowed[local]);
  for (std::size_t i = 0; i < points.size(); ++i)
    for (std::size_t j = i+1; j < points.size(); ++j) {
      const int middle_local = instance.local_of_point[midpoint_id(points[i],points[j])];
      if (middle_local >= 0 && ((chosen >> middle_local) & 1)) return false;
    }
  return true;
}

struct Search {
  const Instance &instance;
  std::array<int,6> order;
  std::array<std::array<std::vector<Mask>,5>,6> domains;
  std::array<std::vector<Mask>,6> completed;
  std::array<int,6> completed_counts{};
  std::uint64_t nodes = 0;
  Mask witness = 0;

  explicit Search(const Instance &source) : instance(source) {
    order = (instance.index == 0 ? std::array<int,6>{{4,1,2,3,0,5}}
                                 : std::array<int,6>{{3,2,4,5,0,1}});
    std::array<int,6> position{};
    for (int depth = 0; depth < 6; ++depth) position[order[depth]] = depth;
    for (const Edge &edge : instance.edges) {
      int last = -1;
      for (int f = 0; f < 6; ++f)
        if ((edge.fibre_set >> f) & 1u) last = std::max(last, position[f]);
      need(last >= 0, "empty blocker fibre set");
      completed[last].push_back(edge.vertices);
      ++completed_counts[last];
    }

    for (int f = 0; f < 6; ++f) {
      for (int bits = 0; bits < 512; ++bits) {
        const int size = int(count_bits(unsigned(bits)));
        if (size > 4) continue;
        Mask chosen = 0;
        for (int j = 0; j < 9; ++j)
          if ((bits >> j) & 1) chosen |= Mask(1) << instance.fibres[f][j];
        if (is_local_cap(instance, chosen)) domains[f][size].push_back(chosen);
      }
      const std::array<std::size_t,5> expected{{1,9,36,72,54}};
      for (int size = 0; size <= 4; ++size)
        need(domains[f][size].size() == expected[size], "local cap-domain drift");
    }
  }

  bool dfs(int depth, int selected, int target, Mask chosen) {
    ++nodes;
    if (depth == 6) {
      if (selected == target) {
        witness = chosen;
        return true;
      }
      return false;
    }
    const int future = 5-depth;
    const int least = std::max(0, target-selected-4*future);
    const int most = std::min(4, target-selected);
    const int fibre = order[depth];
    for (int size = least; size <= most; ++size) {
      for (Mask candidate : domains[fibre][size]) {
        const Mask trial = chosen | candidate;
        bool blocked = false;
        for (Mask edge : completed[depth]) if ((trial & edge) == edge) {
          blocked = true;
          break;
        }
        if (!blocked && dfs(depth+1, selected+size, target, trial)) return true;
      }
    }
    return false;
  }

  bool run(int target) {
    nodes = 0;
    witness = 0;
    return dfs(0, 0, target, 0);
  }
};

template <std::size_t N>
static std::string join(const std::array<int,N> &items) {
  std::ostringstream out;
  for (std::size_t i = 0; i < N; ++i) {
    if (i) out << ',';
    out << items[i];
  }
  return out.str();
}

int main(int argc, char **argv) {
  try {
    need(argc == 3, "usage: cover_independent ROOT TEMPLATE_INDEX");
    const int index = one_digit(argv[2]);
    need(index <= 1, "template index must be 0 or 1");
    const Instance instance = load_instance(argv[1], index);
    Search search(instance);

    int profile_count = 0;
    for (int code = 0; code < 15625; ++code) {
      int value = code, sum = 0;
      for (int f = 0; f < 6; ++f) { sum += value%5; value /= 5; }
      if (sum == 20) ++profile_count;
    }
    need(profile_count == 126, "target20 profile census drift");

    const bool relaxed19 = search.run(19);
    const std::uint64_t nodes19 = search.nodes;
    const Mask witness19 = search.witness;
    need(relaxed19 && count_bits(witness19) == 19,
         "relaxed target19 positive control failed");
    for (const Edge &edge : instance.edges)
      need((witness19 & edge.vertices) != edge.vertices,
           "relaxed target19 witness contains blocker");

    const bool theorem20 = search.run(20);
    const std::uint64_t nodes20 = search.nodes;
    need(!theorem20, "target20 blocker master is satisfiable");
    const std::uint64_t expected19 = index == 0 ? 261597ULL : 67782ULL;
    const std::uint64_t expected20 = index == 0 ? 1624151ULL : 1192358ULL;
    const Mask expected_witness19 =
        index == 0 ? Mask(0x2092080ab4d945ULL) : Mask(0x11638c01264c7ULL);
    need(nodes19 == expected19 && nodes20 == expected20 &&
         witness19 == expected_witness19,
         "deterministic independent search fingerprint drift");

    std::cout << "PASS_INDEPENDENT_TEMPLATE" << index << "_COVER\n";
    std::cout << "ORDER " << join(search.order)
              << " completed=" << join(search.completed_counts) << "\n";
    std::cout << "RELAXED_TARGET19 nodes=" << nodes19
              << " witness_mask=" << std::hex << witness19 << std::dec
              << " not_a_peelability_claim=true\n";
    std::cout << "THEOREM_TARGET20 profiles=126 nodes=" << nodes20
              << " result=UNSAT\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "FAIL " << error.what() << "\n";
    return 2;
  }
}
