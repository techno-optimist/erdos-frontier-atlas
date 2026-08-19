#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
#include <vector>

// Independent exact six-state replay.  Rooted canonical forms are encoded as
// base-7 integers, and exact determinants use a subset dynamic program rather
// than the producer's recursive Laplace expansion.

using Table = std::array<std::int8_t, 12>;
using Histogram = std::array<std::uint8_t, 6>;
using Transitions = std::array<std::array<std::int16_t, 8>, 792>;
using i128 = __int128_t;

constexpr int Q = 6;
constexpr int UNDEFINED = -1;

static std::vector<Histogram> histograms;
static std::array<int, 1 << 18> histogram_index;
static std::array<int, 6> pure_index;

static std::uint64_t accessible_rooted = 0;
static std::uint64_t strong_rooted = 0;
static std::uint64_t strong_orbits = 0;
static std::uint64_t fully_witnessed_orbits = 0;
static std::uint64_t incomplete_orbits = 0;
static std::uint64_t incomplete_pairs = 0;
static std::uint64_t incomplete_rate_below = 0;
static std::uint64_t incomplete_rate_equal = 0;
static std::uint64_t incomplete_rate_above = 0;
static std::uint64_t incomplete_checksum = 1469598103934665603ULL;
static std::uint64_t incomplete_code_sum = 0;
static std::uint64_t witnessed_pairs = 0;
static std::uint64_t rooted_class_checksum = 0;
static std::uint64_t labeled_strong_checksum = 0;
static int maximum_reached = 0;
static int maximum_horizon = 0;
static Table maximum_table{};
static int maximum_start = -1;
static int maximum_target = -1;
static std::map<int, std::uint64_t> horizon_histogram;
static std::map<int, std::uint64_t> root_class_histogram;

[[noreturn]] static void fail(const char* message) {
    std::cerr << "FAIL_INDEPENDENT_SIX_STATE " << message << '\n';
    std::exit(2);
}

static void require(bool condition, const char* message) {
    if (!condition) fail(message);
}

static int histogram_code(const Histogram& h) {
    int code = 0;
    for (int state = 0; state < 6; ++state)
        code |= int(h[state]) << (3 * state);
    return code;
}

static void build_histograms() {
    histogram_index.fill(-1);
    std::map<int, int> orbit_sizes;
    std::uint64_t ordered_total = 0;
    const int factorial[8] = {1, 1, 2, 6, 24, 120, 720, 5040};
    for (int a = 0; a <= 7; ++a)
    for (int b = 0; b <= 7 - a; ++b)
    for (int c = 0; c <= 7 - a - b; ++c)
    for (int d = 0; d <= 7 - a - b - c; ++d)
    for (int e = 0; e <= 7 - a - b - c - d; ++e) {
        Histogram h{{static_cast<std::uint8_t>(a), static_cast<std::uint8_t>(b),
                     static_cast<std::uint8_t>(c), static_cast<std::uint8_t>(d),
                     static_cast<std::uint8_t>(e),
                     static_cast<std::uint8_t>(7 - a - b - c - d - e)}};
        histogram_index[histogram_code(h)] = static_cast<int>(histograms.size());
        histograms.push_back(h);
        int orbit = factorial[7];
        for (int count : h) orbit /= factorial[count];
        ++orbit_sizes[orbit];
        ordered_total += orbit;
    }
    const std::map<int, int> expected = {
        {1,6}, {7,30}, {21,30}, {35,30}, {42,60}, {105,120},
        {140,60}, {210,120}, {420,180}, {630,60}, {840,30},
        {1260,60}, {2520,6}
    };
    require(histograms.size() == 792 && ordered_total == 279936,
            "six-state occupancy quotient size");
    require(orbit_sizes == expected, "S7 occupancy orbit-size histogram");
    for (int state = 0; state < 6; ++state) {
        Histogram h{};
        h[state] = 7;
        pure_index[state] = histogram_index[histogram_code(h)];
        require(pure_index[state] >= 0, "pure histogram lookup");
    }
    std::cout << "INDEPENDENT_SIX_OCCUPANCIES count=792 ordered=279936 active_bound=1584";
    for (const auto& item : expected)
        std::cout << ' ' << item.first << ':' << item.second;
    std::cout << '\n';
}

static bool strongly_connected(const Table& table) {
    std::array<unsigned, 6> reach{};
    for (int source = 0; source < 6; ++source) {
        reach[source] = 1u << source;
        for (int bit = 0; bit < 2; ++bit) {
            const int target = table[2 * source + bit];
            if (target >= 0) reach[source] |= 1u << target;
        }
    }
    for (int middle = 0; middle < 6; ++middle)
        for (int source = 0; source < 6; ++source)
            if ((reach[source] >> middle) & 1u) reach[source] |= reach[middle];
    for (unsigned value : reach) if (value != 63u) return false;
    return true;
}

static std::uint64_t rooted_code(const Table& table, int root) {
    std::array<int, 6> renamed;
    renamed.fill(-1);
    std::array<int, 6> old_by_new{};
    renamed[root] = 0;
    old_by_new[0] = root;
    int discovered = 1;
    std::uint64_t code = 0;
    for (int new_source = 0; new_source < 6; ++new_source) {
        require(new_source < discovered, "rooted accessibility");
        const int old_source = old_by_new[new_source];
        for (int bit = 0; bit < 2; ++bit) {
            const int target = table[2 * old_source + bit];
            int canonical = UNDEFINED;
            if (target >= 0) {
                if (renamed[target] < 0) {
                    require(discovered < 6, "rooted discovery overflow");
                    renamed[target] = discovered;
                    old_by_new[discovered++] = target;
                }
                canonical = renamed[target];
            }
            code = 7 * code + std::uint64_t(canonical + 1);
        }
    }
    require(discovered == 6, "rooted canonical state count");
    return code;
}

static std::uint64_t direct_code(const Table& table) {
    std::uint64_t code = 0;
    for (int value : table) code = 7 * code + std::uint64_t(value + 1);
    return code;
}

struct CanonicalData {
    bool representative = false;
    int rooted_classes = 0;
};

static CanonicalData canonical_data(const Table& table) {
    std::array<std::uint64_t, 6> codes{};
    const std::uint64_t direct = direct_code(table);
    codes[0] = rooted_code(table, 0);
    require(codes[0] == direct, "restricted-growth root code");
    for (int root = 1; root < 6; ++root) {
        codes[root] = rooted_code(table, root);
        if (codes[root] < direct) return {false, 0};
    }
    std::sort(codes.begin(), codes.end());
    const int classes = static_cast<int>(
        std::unique(codes.begin(), codes.end()) - codes.begin());
    return {true, classes};
}

static i128 determinant_dp(const std::array<std::array<i128, 6>, 6>& matrix,
                           int size) {
    std::array<i128, 64> dp{};
    dp[0] = 1;
    const int full = (1 << size) - 1;
    for (int mask = 0; mask < full; ++mask) {
        const int row = __builtin_popcount(static_cast<unsigned>(mask));
        for (int column = 0; column < size; ++column) {
            if ((mask >> column) & 1) continue;
            const int greater = __builtin_popcount(
                static_cast<unsigned>(mask >> (column + 1)));
            const i128 term = dp[mask] * matrix[row][column];
            dp[mask | (1 << column)] += (greater & 1) ? -term : term;
        }
    }
    return dp[full];
}

static int exact_rate_compare_blue(const Table& table) {
    // Divide B I-W by 441: B/441=597 and R/441=40.
    std::array<std::array<i128, 6>, 6> shifted{};
    for (int source = 0; source < 6; ++source) {
        shifted[source][source] = 597;
        const int blue = table[2 * source];
        const int red = table[2 * source + 1];
        if (blue >= 0) shifted[source][blue] -= 597;
        if (red >= 0) shifted[source][red] -= 40;
    }
    i128 full_determinant = 1;
    for (int mask = 1; mask < 64; ++mask) {
        std::array<int, 6> states{};
        int count = 0;
        for (int state = 0; state < 6; ++state)
            if ((mask >> state) & 1) states[count++] = state;
        std::array<std::array<i128, 6>, 6> principal{};
        for (int row = 0; row < count; ++row)
            for (int column = 0; column < count; ++column) {
                principal[row][column] = shifted[states[row]][states[column]];
                if (row != column)
                    require(principal[row][column] <= 0, "Z-matrix sign");
            }
        const i128 value = determinant_dp(principal, count);
        if (value < 0) return 1;
        if (mask == 63) full_determinant = value;
    }
    return full_determinant == 0 ? 0 : -1;
}

static std::int16_t histogram_step(const Table& table, const Histogram& h,
                                   int label) {
    Histogram image{};
    if (label < 2) {
        for (int source = 0; source < 6; ++source) if (h[source]) {
            const int target = table[2 * source + label];
            if (target < 0) return -1;
            image[target] += h[source];
        }
    } else {
        const int selected = label - 2;
        if (!h[selected]) return -1;
        const int red_target = table[2 * selected + 1];
        if (red_target < 0) return -1;
        ++image[red_target];
        for (int source = 0; source < 6; ++source) {
            const int amount = int(h[source]) - (source == selected);
            if (!amount) continue;
            const int blue_target = table[2 * source];
            if (blue_target < 0) return -1;
            image[blue_target] += static_cast<std::uint8_t>(amount);
        }
    }
    const int index = histogram_index[histogram_code(image)];
    require(index >= 0, "histogram transition lookup");
    return static_cast<std::int16_t>(index);
}

static Transitions build_transitions(const Table& table) {
    Transitions transitions{};
    for (int h = 0; h < 792; ++h)
        for (int label = 0; label < 8; ++label)
            transitions[h][label] = histogram_step(table, histograms[h], label);
    return transitions;
}

struct ProductResult {
    std::uint64_t missing = 0;
    std::uint64_t missing_mask = 0;
};

static ProductResult product_screen(const Table& table) {
    const Transitions transitions = build_transitions(table);
    ProductResult result;
    std::array<int, 1584> stamp{};
    std::array<std::uint16_t, 1584> distance{};
    std::array<std::int16_t, 1584> queue{};
    int generation = 0;
    for (int start = 0; start < 6; ++start) {
        ++generation;
        int head = 0, tail = 0, found = 0;
        const int initial = 2 * pure_index[start];
        stamp[initial] = generation;
        distance[initial] = 0;
        queue[tail++] = static_cast<std::int16_t>(initial);
        std::array<int, 6> target_horizon;
        target_horizon.fill(-1);
        while (head < tail && found < 6) {
            const int node = queue[head++];
            const int h = node / 2;
            const bool active = node & 1;
            if (active) {
                for (int target = 0; target < 6; ++target) {
                    if (h == pure_index[target] && target_horizon[target] < 0) {
                        target_horizon[target] = distance[node];
                        ++found;
                    }
                }
            }
            for (int label = 0; label < 8; ++label) {
                const int next_h = transitions[h][label];
                if (next_h < 0) continue;
                const int next = 2 * next_h + (active || label >= 2);
                if (stamp[next] == generation) continue;
                stamp[next] = generation;
                distance[next] = static_cast<std::uint16_t>(distance[node] + 1);
                queue[tail++] = static_cast<std::int16_t>(next);
            }
        }
        maximum_reached = std::max(maximum_reached, tail);
        for (int target = 0; target < 6; ++target) {
            const int horizon = target_horizon[target];
            if (horizon < 0) {
                ++result.missing;
                result.missing_mask |= std::uint64_t(1) << (6 * start + target);
            } else {
                ++witnessed_pairs;
                ++horizon_histogram[horizon];
                if (horizon > maximum_horizon) {
                    maximum_horizon = horizon;
                    maximum_table = table;
                    maximum_start = start;
                    maximum_target = target;
                }
            }
        }
    }
    return result;
}

static std::array<std::string, 7> extract_maximum_witness() {
    const Transitions transitions = build_transitions(maximum_table);
    std::array<int, 1584> previous;
    std::array<int, 1584> previous_label;
    previous.fill(-2);
    previous_label.fill(-1);
    std::array<std::int16_t, 1584> queue{};
    int head = 0, tail = 0;
    const int initial = 2 * pure_index[maximum_start];
    const int goal = 2 * pure_index[maximum_target] + 1;
    previous[initial] = -1;
    queue[tail++] = static_cast<std::int16_t>(initial);
    while (head < tail && previous[goal] == -2) {
        const int node = queue[head++];
        const int h = node / 2;
        const bool active = node & 1;
        for (int label = 0; label < 8; ++label) {
            const int next_h = transitions[h][label];
            if (next_h < 0) continue;
            const int next = 2 * next_h + (active || label >= 2);
            if (previous[next] != -2) continue;
            previous[next] = node;
            previous_label[next] = label;
            queue[tail++] = static_cast<std::int16_t>(next);
        }
    }
    require(previous[goal] != -2, "maximum witness goal");
    std::vector<int> labels;
    for (int node = goal; previous[node] != -1; node = previous[node])
        labels.push_back(previous_label[node]);
    std::reverse(labels.begin(), labels.end());
    require(static_cast<int>(labels.size()) == maximum_horizon,
            "maximum witness shortest length");

    std::array<int, 7> states{};
    states.fill(maximum_start);
    std::array<std::string, 7> words{};
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
            require(selected_role >= 0, "maximum witness selected role");
            column[selected_role] = 1;
            active = true;
        }
        int weight = 0;
        for (int role = 0; role < 7; ++role) {
            weight += column[role];
            words[role].push_back(char('0' + column[role]));
            const int next = maximum_table[2 * states[role] + column[role]];
            require(next >= 0, "maximum witness defined transition");
            states[role] = next;
        }
        require(weight == 0 || weight == 1 || weight == 7,
                "maximum witness column weight");
    }
    require(active, "maximum witness activity");
    for (int state : states)
        require(state == maximum_target, "maximum witness singleton target");
    return words;
}

static void process_orbit(const Table& table, int rooted_classes) {
    ++strong_orbits;
    rooted_class_checksum += rooted_classes;
    ++root_class_histogram[rooted_classes];
    const ProductResult product = product_screen(table);
    if (product.missing == 0) {
        ++fully_witnessed_orbits;
    } else {
        ++incomplete_orbits;
        incomplete_pairs += product.missing;
        const std::uint64_t code = direct_code(table);
        incomplete_code_sum += code;
        incomplete_checksum ^= code;
        incomplete_checksum *= 1099511628211ULL;
        incomplete_checksum ^= product.missing_mask;
        incomplete_checksum *= 1099511628211ULL;
        const int comparison = exact_rate_compare_blue(table);
        incomplete_rate_below += comparison < 0;
        incomplete_rate_equal += comparison == 0;
        incomplete_rate_above += comparison > 0;
    }
}

static void generate(Table& table, int position, int introduced) {
    if (position == 12) {
        if (introduced != 6) return;
        ++accessible_rooted;
        if (!strongly_connected(table)) return;
        ++strong_rooted;
        const CanonicalData canonical = canonical_data(table);
        if (canonical.representative)
            process_orbit(table, canonical.rooted_classes);
        return;
    }
    const int source = position / 2;
    if (source >= introduced) return;
    for (int target = UNDEFINED; target < introduced; ++target) {
        table[position] = static_cast<std::int8_t>(target);
        generate(table, position + 1, introduced);
    }
    if (introduced < 6) {
        table[position] = static_cast<std::int8_t>(introduced);
        generate(table, position + 1, introduced + 1);
    }
}

static void check_results() {
    const std::map<int, std::uint64_t> expected_horizons = {
        {1,1039342}, {2,5549208}, {3,14760193}, {4,20572215},
        {5,16572268}, {6,9322764}, {7,3925069}, {8,1420590},
        {9,492627}, {10,189898}, {11,82032}, {12,41471}, {13,24250},
        {14,16173}, {15,11379}, {16,7507}, {17,4770}, {18,3233},
        {19,2182}, {20,1678}, {21,1239}, {22,1017}, {23,841},
        {24,709}, {25,581}, {26,433}, {27,318}, {28,306}, {29,304},
        {30,282}, {31,234}, {32,163}, {33,133}, {34,99}, {35,75},
        {36,63}, {37,50}, {38,43}, {39,33}, {40,22}, {41,17},
        {42,14}, {43,13}, {44,12}, {45,12}, {46,16}, {47,16},
        {48,10}, {49,8}, {50,4}
    };
    require(accessible_rooted == 23836540, "accessible rooted count");
    require(strong_rooted == 12346720, "strong rooted count");
    require(strong_orbits == 2058472, "strong S6 orbit count");
    require(fully_witnessed_orbits == 2056831, "fully witnessed orbit count");
    require(incomplete_orbits == 1641, "incomplete orbit count");
    require(incomplete_pairs == 59076, "incomplete pair count");
    require(incomplete_rate_below == 1640, "incomplete below-blue count");
    require(incomplete_rate_equal == 1, "incomplete equal-blue count");
    require(incomplete_rate_above == 0, "incomplete above-blue case");
    require(incomplete_checksum == 9776710376808584319ULL,
            "incomplete boundary checksum");
    require(incomplete_code_sum == 1041120840919ULL,
            "incomplete boundary code sum");
    require(witnessed_pairs == 74045916, "witnessed pair count");
    require(rooted_class_checksum == strong_rooted,
            "rooted-class multiplicity checksum");
    labeled_strong_checksum = 120 * strong_rooted;
    require(labeled_strong_checksum == 1481606400,
            "labeled strong checksum");
    require(maximum_reached == 798, "maximum reached quotient states");
    require(maximum_horizon == 50, "maximum witness horizon");
    require(horizon_histogram == expected_horizons, "horizon histogram");
    require(witnessed_pairs + incomplete_pairs == 36 * strong_orbits,
            "all start-target pairs partitioned");
    const auto maximum_words = extract_maximum_witness();

    std::cout << "INDEPENDENT_SIX rooted_accessible=" << accessible_rooted
              << " rooted_strong=" << strong_rooted
              << " strong_orbits=" << strong_orbits
              << " full=" << fully_witnessed_orbits
              << " incomplete=" << incomplete_orbits
              << " witnessed_pairs=" << witnessed_pairs
              << " missing_pairs=" << incomplete_pairs
              << " incomplete_below_B=" << incomplete_rate_below
              << " incomplete_equal_B=" << incomplete_rate_equal
              << " incomplete_above_B=" << incomplete_rate_above
              << " boundary_checksum=" << incomplete_checksum
              << " boundary_code_sum=" << incomplete_code_sum
              << " root_checksum=" << rooted_class_checksum
              << " labeled_strong=" << labeled_strong_checksum
              << " max_reached=" << maximum_reached
              << " max_horizon=" << maximum_horizon << '\n';
    std::cout << "INDEPENDENT_SIX_ROOT_CLASSES";
    for (const auto& item : root_class_histogram)
        std::cout << ' ' << item.first << ':' << item.second;
    std::cout << "\nINDEPENDENT_SIX_HORIZONS";
    for (const auto& item : horizon_histogram)
        std::cout << ' ' << item.first << ':' << item.second;
    std::cout << "\nINDEPENDENT_SIX_MAX table=";
    for (int index = 0; index < 12; ++index) {
        if (index) std::cout << ',';
        std::cout << int(maximum_table[index]);
    }
    std::cout << " start=" << maximum_start << " target=" << maximum_target;
    for (const auto& word : maximum_words) std::cout << ' ' << word;
    std::cout << "\nPASS_INDEPENDENT_SIX_STATE_PRODUCT_FIRST_WALL\n";
}

int main() {
    i128 bound = 720;
    for (int i = 0; i < 6; ++i) bound *= 637;
    require(bound > 0 && bound < (i128(1) << 126),
            "signed i128 determinant bound");
    build_histograms();
    Table blue_cycle{};
    for (int state = 0; state < 6; ++state) {
        blue_cycle[2 * state] = static_cast<std::int8_t>((state + 1) % 6);
        blue_cycle[2 * state + 1] = UNDEFINED;
    }
    require(exact_rate_compare_blue(blue_cycle) == 0,
            "blue-cycle equality control");
    blue_cycle[1] = 0;
    require(exact_rate_compare_blue(blue_cycle) > 0,
            "strict red-edge rate control");
    Table table{};
    generate(table, 0, 1);
    check_results();
    return 0;
}
