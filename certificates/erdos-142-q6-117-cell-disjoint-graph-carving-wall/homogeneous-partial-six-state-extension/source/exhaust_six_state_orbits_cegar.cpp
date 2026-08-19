#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <vector>

// Exact six-state S6-orbit census with product-first CEGAR.  Expensive exact
// Perron comparison is performed only when some singleton product goal is
// unreachable.  Thus no rate-above table can be skipped by a numerical filter.

using Table = std::array<std::int8_t, 12>;
using Hist = std::array<std::uint8_t, 6>;
using Transitions = std::array<std::array<std::int16_t, 8>, 792>;
using Big = __int128_t;

constexpr int U = -1;

std::uint64_t accessible_rooted = 0;
std::uint64_t strong_rooted = 0;
std::uint64_t strong_orbits = 0;
std::uint64_t fully_screened_orbits = 0;
std::uint64_t incomplete_product_orbits = 0;
std::uint64_t incomplete_product_pairs = 0;
std::uint64_t incomplete_rate_above = 0;
std::uint64_t incomplete_rate_equal = 0;
std::uint64_t incomplete_rate_below = 0;
std::uint64_t incomplete_checksum = 1469598103934665603ULL;
std::uint64_t incomplete_code_sum = 0;
std::uint64_t witnessed_pairs = 0;
std::uint64_t max_product_reached = 0;
int maximum_horizon = 0;
std::map<int, std::uint64_t> horizon_histogram;
std::ostream* boundary_output = nullptr;

std::vector<Hist> histograms;
std::array<int, 1 << 18> histogram_index;
std::array<int, 6> pure_index;

int histogram_code(const Hist& histogram) {
    int code = 0;
    for (int state = 0; state < 6; ++state)
        code |= int(histogram[state]) << (3*state);
    return code;
}

void build_histograms() {
    histogram_index.fill(-1);
    for (int a = 0; a <= 7; ++a)
    for (int b = 0; b <= 7-a; ++b)
    for (int c = 0; c <= 7-a-b; ++c)
    for (int d = 0; d <= 7-a-b-c; ++d)
    for (int e = 0; e <= 7-a-b-c-d; ++e) {
        Hist histogram = {std::uint8_t(a), std::uint8_t(b), std::uint8_t(c),
                          std::uint8_t(d), std::uint8_t(e),
                          std::uint8_t(7-a-b-c-d-e)};
        int index = static_cast<int>(histograms.size());
        histograms.push_back(histogram);
        histogram_index[histogram_code(histogram)] = index;
    }
    assert(histograms.size() == 792);
    for (int state = 0; state < 6; ++state) {
        Hist pure{};
        pure[state] = 7;
        pure_index[state] = histogram_index[histogram_code(pure)];
        assert(pure_index[state] >= 0);
    }
}

bool strongly_connected(const Table& table) {
    for (int start = 0; start < 6; ++start) {
        std::array<bool, 6> seen{};
        std::array<int, 6> stack{};
        int size = 0;
        stack[size++] = start;
        seen[start] = true;
        while (size) {
            int state = stack[--size];
            for (int bit = 0; bit < 2; ++bit) {
                int target = table[2*state+bit];
                if (target >= 0 && !seen[target]) {
                    seen[target] = true;
                    stack[size++] = target;
                }
            }
        }
        for (bool value : seen) if (!value) return false;
    }
    return true;
}

Table canonical_from_root(const Table& table, int root) {
    std::array<int, 6> new_name;
    new_name.fill(-1);
    std::array<int, 6> old_state{};
    new_name[root] = 0;
    old_state[0] = root;
    int discovered = 1;
    Table canonical{};
    for (int new_state = 0; new_state < 6; ++new_state) {
        assert(new_state < discovered);
        int source = old_state[new_state];
        for (int bit = 0; bit < 2; ++bit) {
            int target = table[2*source+bit];
            if (target < 0) {
                canonical[2*new_state+bit] = U;
            } else {
                if (new_name[target] < 0) {
                    assert(discovered < 6);
                    new_name[target] = discovered;
                    old_state[discovered++] = target;
                }
                canonical[2*new_state+bit] = static_cast<std::int8_t>(
                    new_name[target]);
            }
        }
    }
    assert(discovered == 6);
    return canonical;
}

bool unrooted_representative(const Table& table) {
    assert(canonical_from_root(table, 0) == table);
    for (int root = 1; root < 6; ++root)
        if (canonical_from_root(table, root) < table) return false;
    return true;
}

Transitions build_transitions(const Table& table) {
    Transitions transitions{};
    for (int index = 0; index < 792; ++index) {
        const Hist& histogram = histograms[index];
        for (int label = 0; label < 8; ++label) {
            Hist image{};
            bool valid = true;
            if (label < 2) {
                for (int state = 0; state < 6; ++state) if (histogram[state]) {
                    int target = table[2*state+label];
                    if (target < 0) { valid = false; break; }
                    image[target] += histogram[state];
                }
            } else {
                int selected = label-2;
                if (!histogram[selected]) valid = false;
                int red_target = valid ? table[2*selected+1] : U;
                if (red_target < 0) valid = false;
                if (valid) {
                    ++image[red_target];
                    for (int state = 0; state < 6; ++state) {
                        int amount = histogram[state] - (state == selected ? 1 : 0);
                        if (!amount) continue;
                        int blue_target = table[2*state];
                        if (blue_target < 0) { valid = false; break; }
                        image[blue_target] += static_cast<std::uint8_t>(amount);
                    }
                }
            }
            transitions[index][label] = valid
                ? static_cast<std::int16_t>(histogram_index[histogram_code(image)])
                : static_cast<std::int16_t>(-1);
            if (valid) assert(transitions[index][label] >= 0);
        }
    }
    return transitions;
}

struct ProductResult {
    std::uint64_t missing_pairs = 0;
    std::uint64_t missing_mask = 0;
    int first_missing_start = -1;
    int first_missing_target = -1;
};

ProductResult product_screen(const Table& table) {
    Transitions transitions = build_transitions(table);
    ProductResult result;
    std::array<int, 1584> stamp{};
    std::array<std::uint16_t, 1584> distance{};
    std::array<std::int16_t, 1584> queue{};
    int generation = 0;
    for (int start = 0; start < 6; ++start) {
        ++generation;
        int head = 0, tail = 0, targets_found = 0;
        int initial = pure_index[start];
        queue[tail++] = static_cast<std::int16_t>(initial);
        stamp[initial] = generation;
        distance[initial] = 0;
        std::array<int, 6> target_distance;
        target_distance.fill(-1);
        while (head < tail && targets_found < 6) {
            int node = queue[head++];
            bool active = node >= 792;
            int histogram = node % 792;
            if (active) {
                for (int target = 0; target < 6; ++target) {
                    if (histogram == pure_index[target]
                        && target_distance[target] < 0) {
                        target_distance[target] = distance[node];
                        ++targets_found;
                    }
                }
            }
            for (int label = 0; label < 8; ++label) {
                int next_histogram = transitions[histogram][label];
                if (next_histogram < 0) continue;
                int next = next_histogram + ((active || label >= 2) ? 792 : 0);
                if (stamp[next] == generation) continue;
                stamp[next] = generation;
                distance[next] = static_cast<std::uint16_t>(distance[node]+1);
                queue[tail++] = static_cast<std::int16_t>(next);
            }
        }
        max_product_reached = std::max<std::uint64_t>(max_product_reached, tail);
        for (int target = 0; target < 6; ++target) {
            int horizon = target_distance[target];
            if (horizon < 0) {
                ++result.missing_pairs;
                result.missing_mask |= std::uint64_t(1) << (6*start+target);
                if (result.first_missing_start < 0) {
                    result.first_missing_start = start;
                    result.first_missing_target = target;
                }
            } else {
                ++witnessed_pairs;
                ++horizon_histogram[horizon];
                maximum_horizon = std::max(maximum_horizon, horizon);
            }
        }
    }
    return result;
}

Big determinant(const std::array<std::array<Big, 6>, 6>& matrix, int size) {
    if (size == 0) return 1;
    if (size == 1) return matrix[0][0];
    Big answer = 0;
    for (int column = 0; column < size; ++column) {
        std::array<std::array<Big, 6>, 6> minor{};
        for (int row = 1; row < size; ++row) {
            int output = 0;
            for (int source_column = 0; source_column < size; ++source_column)
                if (source_column != column)
                    minor[row-1][output++] = matrix[row][source_column];
        }
        Big term = matrix[0][column]*determinant(minor, size-1);
        answer += (column & 1) ? -term : term;
    }
    return answer;
}

int exact_rate_compare_blue(const Table& table) {
    // B=441*597 and R=441*40, so this is a positive rescaling of B I-W.
    std::array<std::array<Big, 6>, 6> z{};
    for (int state = 0; state < 6; ++state) {
        z[state][state] = 597;
        int blue = table[2*state];
        int red = table[2*state+1];
        if (blue >= 0) z[state][blue] -= 597;
        if (red >= 0) z[state][red] -= 40;
    }
    Big full_determinant = 1;
    for (int mask = 1; mask < 64; ++mask) {
        std::array<int, 6> states{};
        int count = 0;
        for (int state = 0; state < 6; ++state)
            if (mask & (1 << state)) states[count++] = state;
        std::array<std::array<Big, 6>, 6> principal{};
        for (int row = 0; row < count; ++row)
            for (int column = 0; column < count; ++column)
                principal[row][column] = z[states[row]][states[column]];
        Big value = determinant(principal, count);
        if (value < 0) return 1;
        if (mask == 63) full_determinant = value;
    }
    return full_determinant == 0 ? 0 : -1;
}

std::uint64_t table_code(const Table& table) {
    std::uint64_t code = 0;
    for (int entry : table) code = 7*code + std::uint64_t(entry+1);
    return code;
}

void print_table(const Table& table) {
    std::cout << "(";
    for (int i = 0; i < 12; ++i) {
        if (i) std::cout << ",";
        std::cout << int(table[i]);
    }
    std::cout << ")";
}

void process_orbit(const Table& table) {
    ++strong_orbits;
    ProductResult product = product_screen(table);
    if (product.missing_pairs == 0) {
        ++fully_screened_orbits;
    } else {
        ++incomplete_product_orbits;
        incomplete_product_pairs += product.missing_pairs;
        std::uint64_t code = table_code(table);
        incomplete_code_sum += code;
        incomplete_checksum ^= code;
        incomplete_checksum *= 1099511628211ULL;
        incomplete_checksum ^= product.missing_mask;
        incomplete_checksum *= 1099511628211ULL;
        int rate_comparison = exact_rate_compare_blue(table);
        if (boundary_output)
            *boundary_output << code << '\t' << product.missing_mask
                             << '\t' << rate_comparison << '\n';
        if (rate_comparison > 0) {
            ++incomplete_rate_above;
            std::cout << "EXACT_SIX_STATE_COUNTEREXAMPLE table=";
            print_table(table);
            std::cout << " start=" << product.first_missing_start
                      << " target=" << product.first_missing_target << "\n";
            std::exit(2);
        }
        if (rate_comparison == 0) ++incomplete_rate_equal;
        if (rate_comparison < 0) ++incomplete_rate_below;
    }
    if (strong_orbits % 100000 == 0) {
        std::cerr << "PROGRESS orbits=" << strong_orbits
                  << " incomplete=" << incomplete_product_orbits
                  << " max_h=" << maximum_horizon << "\n";
    }
}

void planted_controls() {
    Table blue_cycle{};
    for (int state = 0; state < 6; ++state) {
        blue_cycle[2*state] = static_cast<std::int8_t>((state+1)%6);
        blue_cycle[2*state+1] = U;
    }
    ProductResult incomplete = product_screen(blue_cycle);
    assert(incomplete.missing_pairs == 36);
    assert(exact_rate_compare_blue(blue_cycle) == 0);

    Table above = blue_cycle;
    above[1] = 0;
    ProductResult complete = product_screen(above);
    assert(complete.missing_pairs == 0);
    assert(exact_rate_compare_blue(above) > 0);

    // Controls must not enter the exhaustive census statistics.
    witnessed_pairs = 0;
    max_product_reached = 0;
    maximum_horizon = 0;
    horizon_histogram.clear();
}

void generate(Table& table, int position, int introduced) {
    if (position == 12) {
        if (introduced != 6) return;
        ++accessible_rooted;
        if (!strongly_connected(table)) return;
        ++strong_rooted;
        if (unrooted_representative(table)) process_orbit(table);
        return;
    }
    int source = position/2;
    if (source >= introduced) return;
    for (int target = U; target < introduced; ++target) {
        table[position] = static_cast<std::int8_t>(target);
        generate(table, position+1, introduced);
    }
    if (introduced < 6) {
        table[position] = static_cast<std::int8_t>(introduced);
        generate(table, position+1, introduced+1);
    }
}

int main(int argc, char** argv) {
    assert(argc == 1 || argc == 2);
    std::ofstream boundary_file;
    if (argc == 2) {
        boundary_file.open(argv[1], std::ios::out | std::ios::trunc);
        assert(boundary_file.good());
        boundary_output = &boundary_file;
    }
    build_histograms();
    planted_controls();
    Table table{};
    generate(table, 0, 1);
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
    assert(accessible_rooted == 23836540);
    assert(strong_rooted == 12346720);
    assert(strong_orbits == 2058472);
    assert(fully_screened_orbits == 2056831);
    assert(incomplete_product_orbits == 1641);
    assert(incomplete_product_pairs == 59076);
    assert(witnessed_pairs == 74045916);
    assert(incomplete_rate_above == 0);
    assert(incomplete_rate_below == 1640);
    assert(incomplete_rate_equal == 1);
    assert(incomplete_checksum == 9776710376808584319ULL);
    assert(incomplete_code_sum == 1041120840919ULL);
    assert(max_product_reached == 798);
    assert(maximum_horizon == 50);
    assert(horizon_histogram == expected_horizons);
    assert(fully_screened_orbits + incomplete_product_orbits == strong_orbits);
    assert(witnessed_pairs + incomplete_product_pairs == 36*strong_orbits);

    std::cout << "SIX_ROOTED accessible=" << accessible_rooted
              << " strong=" << strong_rooted << "\n";
    std::cout << "SIX_S6_ORBITS strong=" << strong_orbits
              << " fully_product_screened=" << fully_screened_orbits
              << " incomplete_product=" << incomplete_product_orbits << "\n";
    std::cout << "SIX_PAIRS witnessed=" << witnessed_pairs
              << " missing=" << incomplete_product_pairs
              << " incomplete_above_blue=" << incomplete_rate_above << "\n";
    std::cout << "SIX_INCOMPLETE_RATES below=" << incomplete_rate_below
              << " equal=" << incomplete_rate_equal
              << " checksum=" << incomplete_checksum
              << " code_sum=" << incomplete_code_sum << "\n";
    std::cout << "SIX_PRODUCT max_reached=" << max_product_reached
              << " max_horizon=" << maximum_horizon << "\n";
    std::cout << "SIX_HORIZONS";
    for (const auto& item : horizon_histogram)
        std::cout << " " << item.first << ":" << item.second;
    std::cout << "\n";
    std::cout << "PASS_EXACT_SIX_STATE_S6_ORBIT_CEGAR_WALL\n";
    if (boundary_output) {
        boundary_file.flush();
        assert(boundary_file.good());
    }
    return 0;
}
