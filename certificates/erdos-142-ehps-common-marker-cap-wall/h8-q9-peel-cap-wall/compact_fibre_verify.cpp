#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using U64 = std::uint64_t;

struct Edge {
  U64 mask;
  int fibre_mask;
};

struct Instance {
  int template_index;
  std::vector<int> allowed;
  std::array<int, 81> where;
  std::array<int, 54> vertex_fibre;
  std::array<std::vector<int>, 6> fibres;
  std::vector<Edge> edges;
  std::array<int, 7> histogram;
};

struct Prepared {
  std::array<int, 6> order;
  std::array<int, 6> completed_counts;
  std::array<std::vector<U64>, 6> completed;
  std::array<std::array<std::vector<U64>, 5>, 6> configs;
};

struct SearchResult {
  bool satisfiable = false;
  U64 witness = 0;
  std::uint64_t nodes = 0;
  std::uint64_t profiles = 0;
};

static int point_id(int x, int y) { return 9 * x + y; }

static void require(bool condition, const std::string &message) {
  if (!condition) throw std::runtime_error(message);
}

static int parse_digit(const std::string &text) {
  require(text.size() == 1 && std::isdigit(static_cast<unsigned char>(text[0])),
          "coordinate is not one canonical digit");
  int value = text[0] - '0';
  require(0 <= value && value < 9, "coordinate outside 0..8");
  return value;
}

static int parse_point(const std::string &token) {
  const std::size_t comma = token.find(',');
  require(comma != std::string::npos && token.find(',', comma + 1) == std::string::npos,
          "malformed coordinate token");
  return point_id(parse_digit(token.substr(0, comma)),
                  parse_digit(token.substr(comma + 1)));
}

static std::array<std::pair<int, int>, 12> template_points(int index) {
  if (index == 0) return {{{0,3},{0,6},{1,3},{1,6},{2,0},{2,3},
                            {3,0},{4,0},{4,3},{5,0},{5,3},{6,0}}};
  return {{{0,0},{0,3},{1,0},{1,6},{2,3},{2,6},
            {3,3},{4,0},{4,3},{5,0},{5,3},{6,0}}};
}

static Instance load_instance(const std::string &root, int template_index) {
  require(template_index == 0 || template_index == 1, "template index must be 0 or 1");
  const std::string path = root + "/data/template" +
                           std::to_string(template_index) + "_blockers.txt";
  std::ifstream input(path);
  require(static_cast<bool>(input), "cannot open blocker ledger: " + path);

  std::vector<std::vector<int>> rows;
  std::vector<int> previous;
  std::string line;
  while (std::getline(input, line)) {
    require(!line.empty(), "blank line in blocker ledger");
    std::istringstream stream(line);
    std::vector<int> row;
    std::array<bool, 81> seen{};
    std::string token;
    while (stream >> token) {
      int point = parse_point(token);
      require(!seen[point], "duplicate point within blocker");
      seen[point] = true;
      row.push_back(point);
    }
    require(!row.empty() && row.size() <= 6, "invalid blocker size");
    require(std::is_sorted(row.begin(), row.end()), "blocker points are not sorted");
    if (!previous.empty()) {
      require(std::make_pair(previous.size(), previous) <
              std::make_pair(row.size(), row),
              "blocker ledger is not strictly canonical");
    }
    previous = row;
    rows.push_back(row);
  }

  Instance instance{};
  instance.template_index = template_index;
  instance.where.fill(-1);
  instance.histogram.fill(0);
  for (const auto &row : rows) ++instance.histogram[row.size()];
  const std::array<int, 7> expected0{{0,15,0,297,3177,11619,0}};
  const std::array<int, 7> expected1{{0,15,0,297,3798,9,27}};
  require(instance.histogram == (template_index == 0 ? expected0 : expected1),
          "blocker histogram mismatch");

  std::array<bool, 81> fixed{};
  for (const auto &xy : template_points(template_index)) {
    int point = point_id(xy.first, xy.second);
    require(!fixed[point], "duplicate template point");
    fixed[point] = true;
  }
  std::array<bool, 81> singleton{};
  for (const auto &row : rows) if (row.size() == 1) {
    require(!fixed[row[0]], "singleton blocker lies in template");
    singleton[row[0]] = true;
  }
  for (int point = 0; point < 81; ++point) {
    if (!fixed[point] && !singleton[point]) {
      instance.where[point] = static_cast<int>(instance.allowed.size());
      instance.allowed.push_back(point);
    }
  }
  require(instance.allowed.size() == 54, "allowed-point census is not 54");

  std::map<std::pair<int,int>, std::vector<int>> groups;
  for (int local = 0; local < 54; ++local) {
    int point = instance.allowed[local];
    groups[{(point / 9) % 3, (point % 9) % 3}].push_back(local);
  }
  require(groups.size() == 6, "remaining fibre census is not six");
  int fibre = 0;
  for (const auto &entry : groups) {
    require(entry.second.size() == 9, "remaining fibre size is not nine");
    instance.fibres[fibre] = entry.second;
    for (int local : entry.second) instance.vertex_fibre[local] = fibre;
    ++fibre;
  }

  std::set<U64> encoded;
  for (const auto &row : rows) if (row.size() >= 2) {
    U64 mask = 0;
    int fibre_mask = 0;
    for (int point : row) {
      int local = instance.where[point];
      require(local >= 0, "nonsingleton blocker uses forbidden point");
      mask |= U64(1) << local;
      fibre_mask |= 1 << instance.vertex_fibre[local];
    }
    require(encoded.insert(mask).second, "duplicate encoded blocker");
    instance.edges.push_back({mask, fibre_mask});
  }
  const std::size_t expected_edges = template_index == 0 ? 15093u : 4131u;
  require(instance.edges.size() == expected_edges, "nonsingleton blocker census mismatch");
  return instance;
}

static Prepared prepare(const Instance &instance, const std::vector<Edge> &edges,
                        bool require_normal_domains) {
  Prepared result{};
  std::array<int, 6> permutation{{0,1,2,3,4,5}};
  std::array<int, 6> best_score{{-1,-1,-1,-1,-1,-1}};
  do {
    std::array<int, 6> position{};
    for (int i = 0; i < 6; ++i) position[permutation[i]] = i;
    std::array<int, 6> score{};
    for (const Edge &edge : edges) {
      int last = -1;
      for (int f = 0; f < 6; ++f)
        if ((edge.fibre_mask >> f) & 1) last = std::max(last, position[f]);
      require(last >= 0, "edge has empty fibre mask");
      ++score[last];
    }
    if (score > best_score) {
      best_score = score;
      result.order = permutation;
    }
  } while (std::next_permutation(permutation.begin(), permutation.end()));

  std::array<int, 6> position{};
  for (int i = 0; i < 6; ++i) position[result.order[i]] = i;
  std::uint64_t assigned = 0;
  for (const Edge &edge : edges) {
    int last = -1;
    for (int f = 0; f < 6; ++f)
      if ((edge.fibre_mask >> f) & 1) last = std::max(last, position[f]);
    result.completed[last].push_back(edge.mask);
    ++result.completed_counts[last];
    ++assigned;
  }
  require(assigned == edges.size(), "not every blocker assigned exactly once");

  for (int f = 0; f < 6; ++f) {
    std::vector<U64> internal;
    for (const Edge &edge : edges)
      if (edge.fibre_mask == (1 << f)) internal.push_back(edge.mask);
    const int n = static_cast<int>(instance.fibres[f].size());
    require(n == 9, "configuration fibre size drift");
    for (int bits = 0; bits < (1 << n); ++bits) {
      int count = __builtin_popcount(static_cast<unsigned>(bits));
      if (count > 4) continue;
      U64 mask = 0;
      for (int i = 0; i < n; ++i)
        if ((bits >> i) & 1) mask |= U64(1) << instance.fibres[f][i];
      bool forbidden = false;
      for (U64 edge : internal) if ((mask & edge) == edge) {
        forbidden = true;
        break;
      }
      if (!forbidden) result.configs[f][count].push_back(mask);
    }
    if (require_normal_domains) {
      const std::array<std::size_t, 5> expected{{1,9,36,72,54}};
      for (int size = 0; size <= 4; ++size)
        require(result.configs[f][size].size() == expected[size],
                "internal-valid configuration census mismatch");
    }
  }
  return result;
}

static bool contains_edge(U64 selected, const std::vector<Edge> &edges) {
  for (const Edge &edge : edges)
    if ((selected & edge.mask) == edge.mask) return true;
  return false;
}

static SearchResult search(const Instance &instance, const std::vector<Edge> &edges,
                           bool require_normal_domains, int target) {
  require(0 <= target && target <= 24, "target outside fibre-cap range");
  const Prepared prepared = prepare(instance, edges, require_normal_domains);
  std::vector<std::array<int, 6>> profiles;
  for (int code = 0; code < 15625; ++code) {
    int value = code;
    int sum = 0;
    std::array<int, 6> profile{};
    for (int f = 0; f < 6; ++f) {
      profile[f] = value % 5;
      value /= 5;
      sum += profile[f];
    }
    if (sum == target) profiles.push_back(profile);
  }
  const std::size_t expected_profiles = target == 20 ? 126u :
                                        target == 19 ? 246u : profiles.size();
  require(profiles.size() == expected_profiles, "size-profile census mismatch");
  std::sort(profiles.begin(), profiles.end(),
            [](const std::array<int,6> &left, const std::array<int,6> &right) {
    int left_fours = std::count(left.begin(), left.end(), 4);
    int right_fours = std::count(right.begin(), right.end(), 4);
    if (left_fours != right_fours) return left_fours > right_fours;
    return left > right;
  });

  SearchResult result;
  std::array<int, 6> sizes{};
  std::function<bool(int,U64)> dfs = [&](int depth, U64 selected) {
    ++result.nodes;
    if (depth == 6) {
      result.witness = selected;
      return true;
    }
    int fibre = prepared.order[depth];
    for (U64 candidate : prepared.configs[fibre][sizes[fibre]]) {
      U64 trial = selected | candidate;
      bool forbidden = false;
      for (U64 edge : prepared.completed[depth])
        if ((trial & edge) == edge) {
          forbidden = true;
          break;
        }
      if (!forbidden && dfs(depth + 1, trial)) return true;
    }
    return false;
  };

  for (const auto &profile : profiles) {
    ++result.profiles;
    sizes = profile;
    if (dfs(0, 0)) {
      result.satisfiable = true;
      require(__builtin_popcountll(result.witness) == target,
              "returned witness has wrong size");
      require(!contains_edge(result.witness, edges),
              "returned witness contains a blocker");
      return result;
    }
  }
  return result;
}

static std::vector<Edge> internal_edges(const std::vector<Edge> &edges) {
  std::vector<Edge> result;
  for (const Edge &edge : edges)
    if ((edge.fibre_mask & (edge.fibre_mask - 1)) == 0) result.push_back(edge);
  return result;
}

static std::vector<Edge> all_singletons(const Instance &instance) {
  std::vector<Edge> result;
  for (int local = 0; local < 54; ++local)
    result.push_back({U64(1) << local, 1 << instance.vertex_fibre[local]});
  return result;
}

template <std::size_t N>
static std::string integer_tuple(const std::array<int, N> &values) {
  std::ostringstream out;
  for (std::size_t i = 0; i < N; ++i) {
    if (i) out << ',';
    out << values[i];
  }
  return out.str();
}

int main(int argc, char **argv) {
  try {
    require(argc == 3, "usage: compact_fibre_verify ROOT TEMPLATE_INDEX");
    int template_index = parse_digit(argv[2]);
    require(template_index <= 1, "template index must be 0 or 1");
    const Instance instance = load_instance(argv[1], template_index);

    const std::vector<Edge> local = internal_edges(instance.edges);
    const SearchResult sat_control = search(instance, local, true, 20);
    require(sat_control.satisfiable, "SAT control did not find a witness");
    const SearchResult unsat_control = search(instance, all_singletons(instance), false, 20);
    require(!unsat_control.satisfiable, "UNSAT control unexpectedly found a witness");
    const SearchResult boundary_control = search(instance, instance.edges, true, 19);
    require(boundary_control.satisfiable,
            "full-ledger target-19 boundary control did not find a witness");

    const Prepared audit = prepare(instance, instance.edges, true);
    const std::array<int,6> expected_order0{{1,4,2,3,0,5}};
    const std::array<int,6> expected_order1{{2,3,4,5,0,1}};
    const std::array<int,6> expected_completed0{{12,183,597,1668,3855,8778}};
    const std::array<int,6> expected_completed1{{12,111,228,660,1101,2019}};
    require(audit.order == (template_index == 0 ? expected_order0 : expected_order1),
            "deterministic fibre order drift");
    require(audit.completed_counts ==
            (template_index == 0 ? expected_completed0 : expected_completed1),
            "last-fibre blocker census drift");
    const auto started = std::chrono::steady_clock::now();
    const SearchResult theorem = search(instance, instance.edges, true, 20);
    const double elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    require(!theorem.satisfiable, "template extension master is SAT");
    require(theorem.profiles == 126, "not all 126 profiles were exhausted");
    require(sat_control.nodes == 7 && unsat_control.nodes == 127,
            "control node ledger drift");
    const std::uint64_t expected_boundary_nodes =
        template_index == 0 ? 1589725ULL : 971715ULL;
    const std::uint64_t expected_boundary_profiles =
        template_index == 0 ? 77ULL : 17ULL;
    const U64 expected_boundary_mask =
        template_index == 0 ? U64(0x8249a6f861c) : U64(0x9e88a829374);
    require(boundary_control.nodes == expected_boundary_nodes &&
            boundary_control.profiles == expected_boundary_profiles &&
            boundary_control.witness == expected_boundary_mask,
            "full-ledger target-19 control ledger drift");
    const std::uint64_t expected_nodes =
        template_index == 0 ? 3017764ULL : 1989055ULL;
    require(theorem.nodes == expected_nodes, "theorem node ledger drift");

    std::cout << "PASS_COMPACT_TEMPLATE" << template_index << "_UNSAT\n";
    std::cout << "PARSER blockers=" << instance.edges.size()
              << " histogram=" << integer_tuple(instance.histogram) << "\n";
    std::cout << "FIBRES count=6 size_each=9 domains=1,9,36,72,54\n";
    std::cout << "ORDER " << integer_tuple(audit.order)
              << " completed=" << integer_tuple(audit.completed_counts) << "\n";
    std::cout << "CONTROL_SAT nodes=" << sat_control.nodes
              << " witness_size=" << __builtin_popcountll(sat_control.witness) << "\n";
    std::cout << "CONTROL_UNSAT nodes=" << unsat_control.nodes << "\n";
    std::cout << "CONTROL_RELAXED_BLOCKER_MASTER_TARGET19_SAT nodes=" << boundary_control.nodes
              << " profiles_visited=" << boundary_control.profiles
              << " witness_mask=" << std::hex << boundary_control.witness
              << std::dec << " not_a_peelability_witness=true\n";
    std::cout << "THEOREM profiles=" << theorem.profiles
              << " nodes=" << theorem.nodes << " seconds=" << elapsed << "\n";
    std::cout << "DOWNWARD_CLOSURE target_at_least_20_reduces_to_exactly_20\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "FAIL " << error.what() << "\n";
    return 2;
  }
}
