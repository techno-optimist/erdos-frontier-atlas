#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <unordered_map>
#include <vector>

// Independent hostile replay.  In contrast with the producer's
// min-over-five-rooted-codes test, this replay maps every generated rooted
// strong table to the minimum of all 120 simultaneous S5 conjugates.

using Table = std::array<std::int8_t, 10>;
using Perm = std::array<std::int8_t, 5>;
using Hist = std::array<std::uint8_t, 5>;
using Big = __int128_t;

constexpr int U = -1;
constexpr std::int64_t B = 263277;
constexpr std::int64_t R = 17640;
constexpr std::int64_t GNUM = 1058841;
constexpr std::int64_t GDEN = 4;

std::vector<Perm> permutations5;
std::unordered_map<std::uint32_t, int> root_multiplicity;
std::uint64_t accessible_root_codes = 0;
std::uint64_t strong_root_codes = 0;

std::vector<Hist> histograms;
std::array<int, 32768> histogram_index;
std::array<int, 5> pure_index;

std::uint32_t encode_table(const Table& table) {
    std::uint32_t code = 0;
    for (int entry : table) code = 6*code + std::uint32_t(entry+1);
    return code;
}

Table decode_table(std::uint32_t code) {
    Table table{};
    for (int i = 9; i >= 0; --i) {
        table[i] = static_cast<std::int8_t>(code % 6) - 1;
        code /= 6;
    }
    assert(code == 0);
    return table;
}

Table conjugate(const Table& table, const Perm& old_to_new) {
    Table image{};
    for (int old_state = 0; old_state < 5; ++old_state) {
        int new_state = old_to_new[old_state];
        for (int bit = 0; bit < 2; ++bit) {
            int target = table[2*old_state+bit];
            image[2*new_state+bit] = static_cast<std::int8_t>(
                target == U ? U : old_to_new[target]);
        }
    }
    return image;
}

std::uint32_t full_s5_key(const Table& table) {
    std::uint32_t key = UINT32_MAX;
    for (const Perm& permutation : permutations5)
        key = std::min(key, encode_table(conjugate(table, permutation)));
    return key;
}

bool strongly_connected(const Table& table) {
    for (int start = 0; start < 5; ++start) {
        std::array<bool, 5> seen{};
        std::array<int, 5> stack{};
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

void generate_root_code(Table& table, int position, int introduced) {
    if (position == 10) {
        if (introduced != 5) return;
        ++accessible_root_codes;
        if (!strongly_connected(table)) return;
        ++strong_root_codes;
        ++root_multiplicity[full_s5_key(table)];
        return;
    }
    const int source = position/2;
    if (source >= introduced) return;
    for (int target = U; target < introduced; ++target) {
        table[position] = static_cast<std::int8_t>(target);
        generate_root_code(table, position+1, introduced);
    }
    if (introduced < 5) {
        table[position] = static_cast<std::int8_t>(introduced);
        generate_root_code(table, position+1, introduced+1);
    }
}

std::uint64_t integer_power(std::uint64_t base, int exponent) {
    std::uint64_t value = 1;
    while (exponent--) value *= base;
    return value;
}

std::uint64_t binomial(int n, int k) {
    if (k < 0 || k > n) return 0;
    std::uint64_t value = 1;
    for (int i = 1; i <= k; ++i) value = value*(n-k+i)/i;
    return value;
}

void independent_accessible_formula() {
    // A_n counts labeled n-state partial binary tables accessible from a
    // fixed root.  Partition all tables by the root's reachable subset.
    std::array<std::uint64_t, 6> accessible{};
    for (int n = 1; n <= 5; ++n) {
        std::uint64_t value = integer_power(n+1, 2*n);
        for (int k = 1; k < n; ++k)
            value -= binomial(n-1, k-1)*accessible[k]
                     *integer_power(n+1, 2*(n-k));
        accessible[n] = value;
    }
    assert(accessible[5] == 15184800);
    // A rooted accessible deterministic table has no nontrivial automorphism
    // fixing its root, so division by 4! gives rooted canonical codes.
    assert(accessible[5]/24 == 632700);
}

Big determinant(const std::array<std::array<Big, 5>, 5>& matrix, int size) {
    if (size == 0) return 1;
    if (size == 1) return matrix[0][0];
    Big answer = 0;
    for (int column = 0; column < size; ++column) {
        std::array<std::array<Big, 5>, 5> minor{};
        for (int row = 1; row < size; ++row) {
            int out_column = 0;
            for (int source_column = 0; source_column < size; ++source_column) {
                if (source_column == column) continue;
                minor[row-1][out_column++] = matrix[row][source_column];
            }
        }
        Big term = matrix[0][column]*determinant(minor, size-1);
        answer += (column & 1) ? -term : term;
    }
    return answer;
}

bool rate_above(const Table& table, bool gate) {
    std::array<std::array<Big, 5>, 5> z{};
    const std::int64_t numerator = gate ? GNUM : 597;
    z[0][0] = z[1][1] = z[2][2] = z[3][3] = z[4][4] = numerator;
    for (int state = 0; state < 5; ++state) {
        int blue = table[2*state];
        int red = table[2*state+1];
        if (blue >= 0) z[state][blue] -= gate ? GDEN*B : 597;
        if (red >= 0) z[state][red] -= gate ? GDEN*R : 40;
    }
    for (int mask = 1; mask < 32; ++mask) {
        std::array<int, 5> states{};
        int count = 0;
        for (int state = 0; state < 5; ++state)
            if (mask & (1 << state)) states[count++] = state;
        std::array<std::array<Big, 5>, 5> principal{};
        for (int row = 0; row < count; ++row)
            for (int column = 0; column < count; ++column)
                principal[row][column] = z[states[row]][states[column]];
        if (determinant(principal, count) < 0) return true;
    }
    return false;
}

int find_root(std::array<int, 5>& parent, int state) {
    while (parent[state] != state) {
        parent[state] = parent[parent[state]];
        state = parent[state];
    }
    return state;
}

void join(std::array<int, 5>& parent, int left, int right) {
    left = find_root(parent, left);
    right = find_root(parent, right);
    if (left != right) parent[right] = left;
}

int audit_automorphisms(const Table& table, int rooted_multiplicity) {
    int automorphisms = 0;
    std::array<int, 5> parent = {0,1,2,3,4};
    for (const Perm& permutation : permutations5) {
        if (conjugate(table, permutation) == table) {
            ++automorphisms;
            for (int state = 0; state < 5; ++state)
                join(parent, state, permutation[state]);
        }
    }
    int vertex_orbits = 0;
    for (int state = 0; state < 5; ++state)
        vertex_orbits += find_root(parent, state) == state;
    assert(vertex_orbits == rooted_multiplicity);
    assert(120 % automorphisms == 0);
    return automorphisms;
}

int histogram_code(const Hist& histogram) {
    int code = 0;
    for (int state = 0; state < 5; ++state)
        code |= int(histogram[state]) << (3*state);
    return code;
}

void build_histograms() {
    histogram_index.fill(-1);
    for (int a = 0; a <= 7; ++a)
    for (int b = 0; b <= 7-a; ++b)
    for (int c = 0; c <= 7-a-b; ++c)
    for (int d = 0; d <= 7-a-b-c; ++d) {
        Hist histogram = {std::uint8_t(a), std::uint8_t(b), std::uint8_t(c),
                          std::uint8_t(d), std::uint8_t(7-a-b-c-d)};
        int index = static_cast<int>(histograms.size());
        histograms.push_back(histogram);
        histogram_index[histogram_code(histogram)] = index;
    }
    assert(histograms.size() == 330);
    for (int state = 0; state < 5; ++state) {
        Hist pure{};
        pure[state] = 7;
        pure_index[state] = histogram_index[histogram_code(pure)];
        assert(pure_index[state] >= 0);
    }
}

using Transitions = std::array<std::array<std::int16_t, 7>, 330>;

Transitions product_transitions(const Table& table) {
    Transitions transitions{};
    for (int index = 0; index < 330; ++index) {
        const Hist& histogram = histograms[index];
        for (int label = 0; label < 7; ++label) {
            Hist image{};
            bool valid = true;
            if (label < 2) {
                for (int state = 0; state < 5; ++state) if (histogram[state]) {
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
                    for (int state = 0; state < 5; ++state) {
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

void lift_and_check(const Table& table, int start, int target, int goal,
                    int initial, const std::array<std::int16_t, 660>& previous,
                    const std::array<std::int8_t, 660>& previous_label,
                    int expected_distance) {
    std::vector<int> labels;
    for (int node = goal; node != initial; node = previous[node]) {
        assert(node >= 0 && previous[node] >= 0);
        labels.push_back(previous_label[node]);
    }
    std::reverse(labels.begin(), labels.end());
    assert(static_cast<int>(labels.size()) == expected_distance);
    std::array<int, 7> states{};
    states.fill(start);
    bool active = false;
    for (int label : labels) {
        std::array<int, 7> bits{};
        if (label < 2) {
            bits.fill(label);
        } else {
            int selected_state = label-2;
            int role = 0;
            while (role < 7 && states[role] != selected_state) ++role;
            assert(role < 7);
            bits[role] = 1;
            active = true;
        }
        int red_count = 0;
        for (int role = 0; role < 7; ++role) {
            red_count += bits[role];
            int next = table[2*states[role]+bits[role]];
            assert(next >= 0);
            states[role] = next;
        }
        assert(red_count == 0 || red_count == 1 || red_count == 7);
    }
    assert(active);
    for (int state : states) assert(state == target);
}

struct ProductTotals {
    std::uint64_t pairs = 0;
    std::uint64_t witness_symbols = 0;
    int max_reached = 0;
    int max_horizon = 0;
    std::map<int, std::uint64_t> horizons;
};

void audit_all_pairs(const Table& table, ProductTotals& totals) {
    Transitions transitions = product_transitions(table);
    std::array<int, 660> stamp{};
    std::array<std::uint8_t, 660> distance{};
    std::array<std::int16_t, 660> previous{};
    std::array<std::int8_t, 660> previous_label{};
    std::array<std::int16_t, 660> queue{};
    int generation = 0;
    for (int start = 0; start < 5; ++start) {
        ++generation;
        int head = 0, tail = 0;
        int initial = pure_index[start];
        queue[tail++] = static_cast<std::int16_t>(initial);
        stamp[initial] = generation;
        distance[initial] = 0;
        previous[initial] = -1;
        while (head < tail) {
            int node = queue[head++];
            int active = node >= 330;
            int histogram = node % 330;
            for (int label = 0; label < 7; ++label) {
                int next_histogram = transitions[histogram][label];
                if (next_histogram < 0) continue;
                int next = next_histogram + ((active || label >= 2) ? 330 : 0);
                if (stamp[next] == generation) continue;
                stamp[next] = generation;
                distance[next] = static_cast<std::uint8_t>(distance[node]+1);
                previous[next] = static_cast<std::int16_t>(node);
                previous_label[next] = static_cast<std::int8_t>(label);
                queue[tail++] = static_cast<std::int16_t>(next);
            }
        }
        totals.max_reached = std::max(totals.max_reached, tail);
        for (int target = 0; target < 5; ++target) {
            int goal = pure_index[target]+330;
            assert(stamp[goal] == generation);
            int horizon = distance[goal];
            ++totals.pairs;
            totals.witness_symbols += std::uint64_t(7*horizon);
            ++totals.horizons[horizon];
            totals.max_horizon = std::max(totals.max_horizon, horizon);
            lift_and_check(table, start, target, goal, initial,
                           previous, previous_label, horizon);
        }
    }
}

void check_published_maximum_witness() {
    const Table table = {U,1,2,U,3,U,4,U,1,0};
    const std::array<const char*, 7> words = {
        "1000110001100011000110001",
        "1000000000000000000000001",
        "1000000000000000000000001",
        "1000000000000000000000001",
        "1000000000000000000000001",
        "1000000000000000000000001",
        "1000000000000000000000001"
    };
    bool active = false;
    std::array<int, 7> state{};
    for (int coordinate = 0; coordinate < 25; ++coordinate) {
        int red_count = 0;
        for (int role = 0; role < 7; ++role)
            red_count += words[role][coordinate]-'0';
        assert(red_count == 0 || red_count == 1 || red_count == 7);
        active = active || red_count == 1;
        for (int role = 0; role < 7; ++role) {
            int bit = words[role][coordinate]-'0';
            int next = table[2*state[role]+bit];
            assert(next >= 0);
            state[role] = next;
        }
    }
    assert(active);
    for (int value : state) assert(value == 0);
}

int main() {
    Perm identity = {0,1,2,3,4};
    do permutations5.push_back(identity);
    while (std::next_permutation(identity.begin(), identity.end()));
    assert(permutations5.size() == 120);
    independent_accessible_formula();
    build_histograms();

    Table table{};
    generate_root_code(table, 0, 1);
    assert(accessible_root_codes == 632700);
    assert(strong_root_codes == 320253);
    assert(root_multiplicity.size() == 64057);

    std::map<int, std::uint64_t> rooted_multiplicity_histogram;
    std::map<int, std::uint64_t> automorphism_histogram;
    std::uint64_t labeled_strong = 0;
    std::uint64_t above_blue = 0, above_gate = 0;
    ProductTotals products;
    for (const auto& entry : root_multiplicity) {
        Table representative = decode_table(entry.first);
        assert(strongly_connected(representative));
        int automorphisms = audit_automorphisms(representative, entry.second);
        ++rooted_multiplicity_histogram[entry.second];
        ++automorphism_histogram[automorphisms];
        labeled_strong += 120/automorphisms;

        bool blue = rate_above(representative, false);
        bool gate = rate_above(representative, true);
        assert(!gate || blue);
        above_blue += blue;
        above_gate += gate;
        if (blue) audit_all_pairs(representative, products);
    }

    const std::map<int, std::uint64_t> expected_horizons = {
        {1,26426}, {2,141451}, {3,344137}, {4,399252}, {5,264911},
        {6,120113}, {7,38799}, {8,12029}, {9,4009}, {10,1510},
        {11,682}, {12,376}, {13,277}, {14,181}, {15,139}, {16,98},
        {17,60}, {18,35}, {19,32}, {20,27}, {21,23}, {22,14},
        {23,10}, {24,6}, {25,3}
    };
    assert(rooted_multiplicity_histogram ==
           (std::map<int, std::uint64_t>{{1,8},{5,64049}}));
    assert(automorphism_histogram ==
           (std::map<int, std::uint64_t>{{1,64049},{5,8}}));
    assert(labeled_strong == 7686072);
    assert(labeled_strong == 24*strong_root_codes);
    assert(above_blue == 54184);
    assert(above_gate == 49047);
    assert(products.pairs == 1354600);
    assert(products.max_reached == 335);
    assert(products.max_horizon == 25);
    assert(products.horizons == expected_horizons);
    check_published_maximum_witness();

    std::cout << "INDEPENDENT_ROOTED accessible=" << accessible_root_codes
              << " strong=" << strong_root_codes << "\n";
    std::cout << "INDEPENDENT_S5 orbits=" << root_multiplicity.size()
              << " root_multiplicity=1:8,5:64049"
              << " automorphisms=1:64049,5:8"
              << " labeled_strong=" << labeled_strong << "\n";
    std::cout << "INDEPENDENT_RATES above_blue=" << above_blue
              << " above_gate=" << above_gate << "\n";
    std::cout << "INDEPENDENT_PRODUCTS pairs=" << products.pairs
              << " max_reached=" << products.max_reached
              << " max_horizon=" << products.max_horizon
              << " ordered_witness_symbols=" << products.witness_symbols << "\n";
    std::cout << "INDEPENDENT_HORIZONS";
    for (const auto& item : products.horizons)
        std::cout << " " << item.first << ":" << item.second;
    std::cout << "\n";
    std::cout << "PASS_INDEPENDENT_FIVE_STATE_S5_ORBIT_AND_PRODUCT_AUDIT\n";
    return 0;
}
