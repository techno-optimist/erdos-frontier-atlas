#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

// Hostile independent replay for the five-state census.  In contrast to the
// frozen implementation, orbit representatives are deduplicated by the least
// code among all 120 simultaneous conjugates, and determinants are evaluated
// by recursive Laplace expansion rather than a signed-permutation sum.

using i128 = __int128_t;
using Table = std::array<int, 10>;
using Histogram = std::array<unsigned char, 5>;

constexpr int STATES = 5;
constexpr int UNDEFINED = -1;
constexpr long long BLUE = 263277;
constexpr long long RED = 17640;
constexpr long long GATE_NUM = 1058841;
constexpr long long GATE_DEN = 4;

static std::vector<std::array<int, 5>> permutations5;
static std::vector<Histogram> histograms;
static std::array<int, 32768> histogram_index;
static std::array<int, 5> pure_histogram;
static std::unordered_set<std::uint64_t> orbit_keys;

static std::uint64_t accessible_rooted = 0;
static std::uint64_t strong_rooted = 0;
static std::uint64_t strong_orbits = 0;
static std::uint64_t above_blue_orbits = 0;
static std::uint64_t above_gate_orbits = 0;
static std::uint64_t pair_checks = 0;
static std::uint64_t rooted_class_checksum = 0;
static std::uint64_t labeled_strong_checksum = 0;
static std::uint64_t ordered_symbol_checks = 0;
static int maximum_reached = 0;
static int maximum_horizon = 0;
static std::map<int, std::uint64_t> horizon_histogram;
static std::map<int, std::uint64_t> automorphism_histogram;

[[noreturn]] static void fail(const std::string& message) {
    std::cerr << "FAIL_INDEPENDENT_FIVE_STATE " << message << '\n';
    std::exit(2);
}

static void require(bool condition, const std::string& message) {
    if (!condition) fail(message);
}

static void build_permutations() {
    std::array<int, 5> p{{0, 1, 2, 3, 4}};
    do permutations5.push_back(p); while (std::next_permutation(p.begin(), p.end()));
    require(permutations5.size() == 120, "S5 permutation count");
}

static Table conjugate(const Table& delta, const std::array<int, 5>& sigma) {
    Table result{};
    result.fill(UNDEFINED);
    for (int source = 0; source < 5; ++source) {
        const int new_source = sigma[source];
        for (int bit = 0; bit < 2; ++bit) {
            const int target = delta[2 * source + bit];
            result[2 * new_source + bit] =
                target == UNDEFINED ? UNDEFINED : sigma[target];
        }
    }
    return result;
}

static std::uint64_t table_code(const Table& delta) {
    std::uint64_t code = 0;
    for (int value : delta) code = 6 * code + std::uint64_t(value + 1);
    return code;
}

static std::uint64_t all_permutation_key(const Table& delta) {
    std::uint64_t answer = UINT64_MAX;
    for (const auto& sigma : permutations5)
        answer = std::min(answer, table_code(conjugate(delta, sigma)));
    return answer;
}

static bool strongly_connected(const Table& delta) {
    std::array<unsigned, 5> reach{};
    for (int source = 0; source < 5; ++source) {
        reach[source] = 1u << source;
        for (int bit = 0; bit < 2; ++bit) {
            int target = delta[2 * source + bit];
            if (target >= 0) reach[source] |= 1u << target;
        }
    }
    for (int middle = 0; middle < 5; ++middle)
        for (int source = 0; source < 5; ++source)
            if ((reach[source] >> middle) & 1u) reach[source] |= reach[middle];
    for (unsigned value : reach) if (value != 31u) return false;
    return true;
}

static int find_root(int parent[5], int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    return x;
}

static std::pair<int, int> symmetry_data(const Table& delta) {
    int parent[5] = {0, 1, 2, 3, 4};
    int automorphisms = 0;
    for (const auto& sigma : permutations5) {
        if (conjugate(delta, sigma) != delta) continue;
        ++automorphisms;
        for (int state = 0; state < 5; ++state) {
            int a = find_root(parent, state);
            int b = find_root(parent, sigma[state]);
            if (a != b) parent[a] = b;
        }
    }
    int vertex_orbits = 0;
    for (int state = 0; state < 5; ++state)
        vertex_orbits += find_root(parent, state) == state;
    require(automorphisms > 0 && 120 % automorphisms == 0,
            "automorphism divisor");
    return {automorphisms, vertex_orbits};
}

static i128 laplace_determinant(const std::vector<std::vector<i128>>& matrix) {
    const int n = static_cast<int>(matrix.size());
    if (n == 1) return matrix[0][0];
    i128 answer = 0;
    for (int excluded = 0; excluded < n; ++excluded) {
        if (matrix[0][excluded] == 0) continue;
        std::vector<std::vector<i128>> minor;
        minor.reserve(n - 1);
        for (int row = 1; row < n; ++row) {
            std::vector<i128> line;
            line.reserve(n - 1);
            for (int column = 0; column < n; ++column)
                if (column != excluded) line.push_back(matrix[row][column]);
            minor.push_back(std::move(line));
        }
        const i128 term = matrix[0][excluded] * laplace_determinant(minor);
        answer += (excluded & 1) ? -term : term;
    }
    return answer;
}

static bool rate_above(const Table& delta, long long numerator,
                       long long denominator) {
    std::array<std::array<i128, 5>, 5> shifted{};
    for (int source = 0; source < 5; ++source) {
        shifted[source][source] = numerator;
        for (int bit = 0; bit < 2; ++bit) {
            int target = delta[2 * source + bit];
            if (target >= 0)
                shifted[source][target] -= i128(denominator)
                    * (bit ? RED : BLUE);
        }
    }
    for (int mask = 1; mask < 32; ++mask) {
        std::vector<int> states;
        for (int state = 0; state < 5; ++state)
            if ((mask >> state) & 1) states.push_back(state);
        std::vector<std::vector<i128>> minor(
            states.size(), std::vector<i128>(states.size()));
        for (int row = 0; row < static_cast<int>(states.size()); ++row)
            for (int column = 0; column < static_cast<int>(states.size()); ++column) {
                minor[row][column] = shifted[states[row]][states[column]];
                if (row != column)
                    require(minor[row][column] <= 0, "Z-matrix off diagonal");
            }
        if (laplace_determinant(minor) < 0) return true;
    }
    return false;
}

static int histogram_code(const Histogram& histogram) {
    int code = 0;
    for (int state = 0; state < 5; ++state)
        code |= int(histogram[state]) << (3 * state);
    return code;
}

static void build_histograms() {
    histogram_index.fill(-1);
    std::map<int, int> orbit_size_histogram;
    std::uint64_t ordered_total = 0;
    const int factorial[8] = {1, 1, 2, 6, 24, 120, 720, 5040};
    for (int a = 0; a <= 7; ++a)
    for (int b = 0; b <= 7 - a; ++b)
    for (int c = 0; c <= 7 - a - b; ++c)
    for (int d = 0; d <= 7 - a - b - c; ++d) {
        const int e = 7 - a - b - c - d;
        Histogram h{{static_cast<unsigned char>(a), static_cast<unsigned char>(b),
                     static_cast<unsigned char>(c), static_cast<unsigned char>(d),
                     static_cast<unsigned char>(e)}};
        histogram_index[histogram_code(h)] = static_cast<int>(histograms.size());
        histograms.push_back(h);
        int orbit_size = factorial[7];
        for (int count : h) orbit_size /= factorial[count];
        ++orbit_size_histogram[orbit_size];
        ordered_total += orbit_size;
    }
    require(histograms.size() == 330 && ordered_total == 78125,
            "S7 occupancy quotient cardinality");
    const std::map<int, int> expected = {
        {1,5}, {7,20}, {21,20}, {35,20}, {42,30}, {105,60},
        {140,30}, {210,50}, {420,60}, {630,20}, {840,5}, {1260,10}
    };
    require(orbit_size_histogram == expected, "S7 orbit-size histogram");
    for (int state = 0; state < 5; ++state) {
        Histogram pure{};
        pure[state] = 7;
        pure_histogram[state] = histogram_index[histogram_code(pure)];
        require(pure_histogram[state] >= 0, "pure histogram lookup");
    }
    std::cout << "INDEPENDENT_S7_OCCUPANCIES count=330 ordered=78125 active_bound=660";
    for (const auto& item : expected)
        std::cout << ' ' << item.first << ':' << item.second;
    std::cout << '\n';
}

using Transitions = std::array<std::array<short, 7>, 330>;

static short histogram_step(const Table& delta, const Histogram& h, int label) {
    Histogram output{};
    if (label < 2) {
        for (int source = 0; source < 5; ++source) if (h[source]) {
            const int target = delta[2 * source + label];
            if (target < 0) return -1;
            output[target] += h[source];
        }
    } else {
        const int selected = label - 2;
        if (!h[selected]) return -1;
        const int red_target = delta[2 * selected + 1];
        if (red_target < 0) return -1;
        ++output[red_target];
        for (int source = 0; source < 5; ++source) {
            int count = int(h[source]) - (source == selected);
            if (!count) continue;
            const int blue_target = delta[2 * source];
            if (blue_target < 0) return -1;
            output[blue_target] += static_cast<unsigned char>(count);
        }
    }
    const int index = histogram_index[histogram_code(output)];
    require(index >= 0, "histogram transition lookup");
    return static_cast<short>(index);
}

static Transitions build_transitions(const Table& delta) {
    Transitions transitions{};
    for (int h = 0; h < 330; ++h)
        for (int label = 0; label < 7; ++label)
            transitions[h][label] = histogram_step(delta, histograms[h], label);
    return transitions;
}

static void validate_ordered_witness(
        const Table& delta, int start, int target, int goal,
        const std::array<int, 660>& previous,
        const std::array<int, 660>& previous_label,
        const std::array<int, 660>& distance) {
    std::vector<int> labels;
    for (int node = goal; previous[node] != -1; node = previous[node]) {
        require(previous[node] >= 0, "broken witness predecessor");
        labels.push_back(previous_label[node]);
    }
    std::reverse(labels.begin(), labels.end());
    require(static_cast<int>(labels.size()) == distance[goal],
            "ordered witness shortest distance");
    std::array<int, 7> states{};
    states.fill(start);
    bool active = false;
    for (int label : labels) {
        std::array<int, 7> column{};
        if (label < 2) {
            column.fill(label);
        } else {
            const int selected_state = label - 2;
            int selected_role = -1;
            for (int role = 0; role < 7; ++role)
                if (states[role] == selected_state) {
                    selected_role = role;
                    break;
                }
            require(selected_role >= 0, "ordered unit-column representative");
            column[selected_role] = 1;
            active = true;
        }
        int weight = 0;
        for (int role = 0; role < 7; ++role) {
            weight += column[role];
            const int next = delta[2 * states[role] + column[role]];
            require(next >= 0, "ordered witness defined transition");
            states[role] = next;
        }
        require(weight == 0 || weight == 1 || weight == 7,
                "ordered witness column weight");
    }
    require(active, "ordered witness nondegeneracy");
    for (int state : states) require(state == target, "ordered witness target");
    ordered_symbol_checks += 7 * labels.size();
}

static void audit_all_start_target_pairs(const Table& delta) {
    const Transitions transitions = build_transitions(delta);
    std::array<int, 660> visit_stamp{};
    std::array<int, 660> distance{};
    std::array<int, 660> previous{};
    std::array<int, 660> previous_label{};
    std::array<int, 660> queue{};
    int generation = 0;
    for (int start = 0; start < 5; ++start) {
        ++generation;
        int head = 0, tail = 0;
        const int initial = 2 * pure_histogram[start];
        visit_stamp[initial] = generation;
        distance[initial] = 0;
        previous[initial] = -1;
        previous_label[initial] = -1;
        queue[tail++] = initial;
        std::array<int, 5> target_horizon;
        target_horizon.fill(-1);
        std::array<int, 5> target_node;
        target_node.fill(-1);
        while (head < tail) {
            const int node = queue[head++];
            const int h = node / 2;
            const int active = node & 1;
            if (active) {
                for (int target = 0; target < 5; ++target) {
                    if (h == pure_histogram[target] && target_horizon[target] < 0) {
                        target_horizon[target] = distance[node];
                        target_node[target] = node;
                    }
                }
            }
            for (int label = 0; label < 7; ++label) {
                const int next_h = transitions[h][label];
                if (next_h < 0) continue;
                const int next = 2 * next_h + (active || label >= 2);
                if (visit_stamp[next] == generation) continue;
                visit_stamp[next] = generation;
                distance[next] = distance[node] + 1;
                previous[next] = node;
                previous_label[next] = label;
                queue[tail++] = next;
            }
        }
        maximum_reached = std::max(maximum_reached, tail);
        for (int target = 0; target < 5; ++target) {
            require(target_horizon[target] > 0, "missing start/target witness");
            validate_ordered_witness(delta, start, target, target_node[target],
                                     previous, previous_label, distance);
            ++pair_checks;
            ++horizon_histogram[target_horizon[target]];
            maximum_horizon = std::max(maximum_horizon, target_horizon[target]);
        }
    }
}

static void validate_horizon_25_control() {
    const Table delta{{-1,1, 2,-1, 3,-1, 4,-1, 1,0}};
    const std::string exceptional = "1000110001100011000110001";
    const std::string repeated = "1000000000000000000000001";
    require(exceptional.size() == 25 && repeated.size() == 25,
            "horizon-25 word lengths");
    std::array<std::string, 7> words;
    words[0] = exceptional;
    for (int role = 1; role < 7; ++role) words[role] = repeated;
    bool active = false;
    for (int coordinate = 0; coordinate < 25; ++coordinate) {
        int weight = 0;
        for (const auto& word : words) weight += word[coordinate] - '0';
        require(weight == 0 || weight == 1 || weight == 7,
                "horizon-25 column weight");
        active = active || weight == 1;
    }
    require(active, "horizon-25 nondegeneracy");
    for (const auto& word : words) {
        int state = 0;
        for (char symbol : word) {
            state = delta[2 * state + (symbol - '0')];
            require(state >= 0, "horizon-25 defined path");
        }
        require(state == 0, "horizon-25 singleton target");
    }
}

static void process_orbit(const Table& delta) {
    ++strong_orbits;
    const auto symmetry = symmetry_data(delta);
    ++automorphism_histogram[symmetry.first];
    labeled_strong_checksum += 120 / symmetry.first;
    rooted_class_checksum += symmetry.second;
    const bool high_blue = rate_above(delta, BLUE, 1);
    const bool high_gate = rate_above(delta, GATE_NUM, GATE_DEN);
    require(!high_gate || high_blue, "gate orbit below blue");
    above_blue_orbits += high_blue;
    above_gate_orbits += high_gate;
    if (high_blue) audit_all_start_target_pairs(delta);
}

static void generate_rooted(Table& delta, int position, int discovered) {
    if (position == 10) {
        if (discovered != 5) return;
        ++accessible_rooted;
        if (!strongly_connected(delta)) return;
        ++strong_rooted;
        const std::uint64_t key = all_permutation_key(delta);
        if (orbit_keys.insert(key).second) process_orbit(delta);
        return;
    }
    const int source_row = position / 2;
    if (source_row >= discovered) return;
    for (int target = UNDEFINED; target < discovered; ++target) {
        delta[position] = target;
        generate_rooted(delta, position + 1, discovered);
    }
    if (discovered < 5) {
        delta[position] = discovered;
        generate_rooted(delta, position + 1, discovered + 1);
    }
}

static void check_results() {
    const std::map<int, std::uint64_t> expected_horizons = {
        {1,26426}, {2,141451}, {3,344137}, {4,399252}, {5,264911},
        {6,120113}, {7,38799}, {8,12029}, {9,4009}, {10,1510},
        {11,682}, {12,376}, {13,277}, {14,181}, {15,139}, {16,98},
        {17,60}, {18,35}, {19,32}, {20,27}, {21,23}, {22,14},
        {23,10}, {24,6}, {25,3}
    };
    require(accessible_rooted == 632700, "accessible rooted count");
    require(strong_rooted == 320253, "strong rooted count");
    require(strong_orbits == 64057 && orbit_keys.size() == 64057,
            "all-permutation S5 orbit count");
    require(rooted_class_checksum == strong_rooted,
            "rooted classes equal vertex-orbit checksum");
    require(automorphism_histogram ==
                std::map<int, std::uint64_t>{{1, 64049}, {5, 8}},
            "S5 automorphism multiplicity histogram");
    require(above_blue_orbits == 54184, "above-blue orbit count");
    require(above_gate_orbits == 49047, "above-gate orbit count");
    require(pair_checks == 1354600, "all start/target pair count");
    require(ordered_symbol_checks == 38001782,
            "all ordered witness symbol checks");
    require(maximum_reached == 335, "maximum quotient reachability");
    require(maximum_horizon == 25, "maximum witness horizon");
    require(horizon_histogram == expected_horizons, "witness horizon histogram");
    validate_horizon_25_control();

    std::cout << "INDEPENDENT_FIVE_STATE accessible_rooted=" << accessible_rooted
              << " strong_rooted=" << strong_rooted
              << " strong_orbits=" << strong_orbits
              << " above_B=" << above_blue_orbits
              << " above_G=" << above_gate_orbits
              << " pairs=" << pair_checks
              << " max_reached=" << maximum_reached
              << " max_horizon=" << maximum_horizon
              << " ordered_symbols=" << ordered_symbol_checks
              << " rooted_checksum=" << rooted_class_checksum
              << " labeled_strong_checksum=" << labeled_strong_checksum << '\n';
    std::cout << "INDEPENDENT_AUTOMORPHISMS";
    for (const auto& item : automorphism_histogram)
        std::cout << ' ' << item.first << ':' << item.second;
    std::cout << '\n';
    std::cout << "INDEPENDENT_FIVE_HORIZONS";
    for (const auto& item : horizon_histogram)
        std::cout << ' ' << item.first << ':' << item.second;
    std::cout << "\nPASS_INDEPENDENT_FIVE_STATE_ALL_PAIRS\n";
}

int main() {
    const i128 determinant_bound = i128(120) * 1123668 * 1123668
        * 1123668 * 1123668 * 1123668;
    require(determinant_bound > 0 && determinant_bound < (i128(1) << 126),
            "signed i128 determinant bound");
    build_permutations();
    build_histograms();
    orbit_keys.reserve(70000);
    Table delta{};
    generate_rooted(delta, 0, 1);
    check_results();
    return 0;
}
