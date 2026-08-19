#include <algorithm>
#include <array>
#include <cassert>
#include <cstdlib>
#include <cstdint>
#include <iostream>
#include <map>
#include <queue>
#include <string>
#include <vector>

using Table = std::array<int, 10>;
using Hist = std::array<unsigned char, 5>;
using HistTransitions = std::array<std::array<int, 7>, 330>;
using i128 = __int128_t;

constexpr int U = -1;
constexpr long long BLUE = 263277;
constexpr long long RED = 17640;
constexpr long long GNUM = 1058841;
constexpr long long GDEN = 4;

static uint64_t accessible_count = 0;
static uint64_t rooted_strong_count = 0;
static uint64_t orbit_count = 0;
static uint64_t above_blue_count = 0;
static uint64_t above_gate_count = 0;
static uint64_t pair_count = 0;
static uint64_t max_product_reached = 0;
static std::map<int, uint64_t> horizon_histogram;
static int maximum_horizon = -1;
static Table maximum_table{};
static int maximum_start = -1;
static int maximum_target = -1;
static bool counterexample = false;
static Table counterexample_table{};
static int counterexample_start = -1;
static int counterexample_target = -1;

static std::vector<Hist> histograms;
static std::array<int, 32768> histogram_index;
static std::array<int, 5> pure_histogram;

int histogram_code(const Hist& h) {
    int code = 0;
    for (int i = 0; i < 5; ++i) code |= int(h[i]) << (3*i);
    return code;
}
void build_histograms() {
    histogram_index.fill(-1);
    Hist h{};
    for (int a = 0; a <= 7; ++a)
    for (int b = 0; b <= 7-a; ++b)
    for (int c = 0; c <= 7-a-b; ++c)
    for (int d = 0; d <= 7-a-b-c; ++d) {
        int e = 7-a-b-c-d;
        h = {static_cast<unsigned char>(a), static_cast<unsigned char>(b),
             static_cast<unsigned char>(c), static_cast<unsigned char>(d),
             static_cast<unsigned char>(e)};
        int index = static_cast<int>(histograms.size());
        histograms.push_back(h);
        histogram_index[histogram_code(h)] = index;
    }
    assert(histograms.size() == 330);
    for (int q = 0; q < 5; ++q) {
        Hist p{};
        p[q] = 7;
        pure_histogram[q] = histogram_index[histogram_code(p)];
        assert(pure_histogram[q] >= 0);
    }
}

int wrapped_square(int a, int b) {
    int difference = std::abs(a-b);
    difference = std::min(difference, 42-difference);
    return difference*difference;
}

void verify_physical_role_geometry() {
    const int points[7][2] = {
        {2,29}, {8,41}, {14,11}, {20,23}, {26,35}, {32,5}, {38,17}
    };
    const int rows[7][3] = {
        {1,0,6}, {0,1,2}, {0,2,4}, {1,3,5},
        {3,4,5}, {4,5,6}, {2,6,3}
    };
    int incidence[7]{};
    for (const auto& row : rows) {
        int x = row[0], middle = row[1], z = row[2];
        for (int coordinate = 0; coordinate < 2; ++coordinate)
            assert((points[x][coordinate]+points[z][coordinate]
                    -2*points[middle][coordinate]) % 42 == 0);
        ++incidence[x];
        ++incidence[z];
        incidence[middle] -= 2;
    }
    for (int value : incidence) assert(value == 0);
    const int expected_raw[7] = {4032, 5544, 5040, 6048, 5544, 4536, 4536};
    for (int shift = 0; shift < 7; ++shift) {
        int codes[7][4]{};
        for (int role = 0; role < 7; ++role) {
            codes[role][0] = 21;
            codes[role][1] = 14;
            codes[role][2] = (points[role][0]+21) % 42;
            codes[role][3] = (points[role][1]+14) % 42;
        }
        int raw = 0, torus = 0;
        for (const auto& row : rows) {
            int x = (row[0]+shift) % 7;
            int middle = (row[1]+shift) % 7;
            int z = (row[2]+shift) % 7;
            for (int coordinate = 0; coordinate < 4; ++coordinate) {
                assert((codes[x][coordinate]+codes[z][coordinate]
                        -2*codes[middle][coordinate]) % 42 == 0);
                int difference = codes[x][coordinate]-codes[z][coordinate];
                raw += difference*difference;
                torus += wrapped_square(codes[x][coordinate], codes[z][coordinate]);
            }
        }
        assert(raw == expected_raw[shift]);
        assert(torus == 2772);  // 2772/42^2 = 11/7.
    }
    assert(BLUE+RED == 280917);
    assert(GNUM-4*BLUE == 5733);
    std::cout << "PASS_Q42_SIZE7_PHYSICAL_ROLE_GEOMETRY "
              << "raw=16/7,22/7,20/7,24/7,22/7,18/7,18/7 "
              << "torus=11/7\n";
}

bool strongly_connected(const Table& delta) {
    for (int start = 0; start < 5; ++start) {
        std::array<bool, 5> seen{};
        std::array<int, 5> stack{};
        int top = 0;
        stack[top++] = start;
        seen[start] = true;
        while (top) {
            int q = stack[--top];
            for (int bit = 0; bit < 2; ++bit) {
                int target = delta[2*q+bit];
                if (target != U && !seen[target]) {
                    seen[target] = true;
                    stack[top++] = target;
                }
            }
        }
        if (!std::all_of(seen.begin(), seen.end(), [](bool x){ return x; }))
            return false;
    }
    return true;
}

Table canonical_from_root(const Table& delta, int root) {
    std::array<int, 5> rename;
    rename.fill(-1);
    std::array<int, 5> old_by_new{};
    int discovered = 1;
    rename[root] = 0;
    old_by_new[0] = root;
    Table answer{};
    for (int new_state = 0; new_state < 5; ++new_state) {
        assert(new_state < discovered);
        int old_state = old_by_new[new_state];
        for (int bit = 0; bit < 2; ++bit) {
            int target = delta[2*old_state+bit];
            if (target == U) {
                answer[2*new_state+bit] = U;
            } else {
                if (rename[target] == -1) {
                    assert(discovered < 5);
                    rename[target] = discovered;
                    old_by_new[discovered++] = target;
                }
                answer[2*new_state+bit] = rename[target];
            }
        }
    }
    assert(discovered == 5);
    return answer;
}

bool is_unrooted_canonical(const Table& delta) {
    assert(canonical_from_root(delta, 0) == delta);
    for (int root = 1; root < 5; ++root)
        if (canonical_from_root(delta, root) < delta) return false;
    return true;
}

i128 determinant_subset(const std::array<std::array<long long, 5>, 5>& matrix,
                        int mask) {
    std::array<int, 5> rows{};
    int size = 0;
    for (int i = 0; i < 5; ++i) if (mask >> i & 1) rows[size++] = i;
    std::array<int, 5> permutation = rows;
    i128 answer = 0;
    do {
        int inversions = 0;
        for (int i = 0; i < size; ++i)
            for (int j = i+1; j < size; ++j)
                inversions += permutation[i] > permutation[j];
        i128 term = 1;
        for (int i = 0; i < size; ++i)
            term *= i128(matrix[rows[i]][permutation[i]]);
        answer += (inversions & 1) ? -term : term;
    } while (std::next_permutation(permutation.begin(), permutation.begin()+size));
    return answer;
}

bool rate_above(const Table& delta, long long numerator, long long denominator) {
    std::array<std::array<long long, 5>, 5> shifted{};
    for (int q = 0; q < 5; ++q) {
        shifted[q][q] = numerator;
        for (int bit = 0; bit < 2; ++bit) {
            int target = delta[2*q+bit];
            if (target != U)
                shifted[q][target] -= denominator*(bit ? RED : BLUE);
        }
    }
    for (int mask = 1; mask < 32; ++mask)
        if (determinant_subset(shifted, mask) < 0) return true;
    return false;
}

int histogram_transition(const Table& delta, const Hist& h, int label) {
    // labels 0,1 are constant blue/red; label 2+s is a unit column whose
    // selected copy currently occupies source state s.
    Hist out{};
    if (label < 2) {
        for (int state = 0; state < 5; ++state) if (h[state]) {
            int target = delta[2*state+label];
            if (target == U) return -1;
            out[target] += h[state];
        }
    } else {
        int selected = label-2;
        if (!h[selected]) return -1;
        for (int state = 0; state < 5; ++state) {
            int count = h[state];
            if (state == selected) {
                int red_target = delta[2*state+1];
                if (red_target == U) return -1;
                ++out[red_target];
                --count;
            }
            if (count) {
                int blue_target = delta[2*state];
                if (blue_target == U) return -1;
                out[blue_target] += count;
            }
        }
    }
    int index = histogram_index[histogram_code(out)];
    assert(index >= 0);
    return index;
}

HistTransitions build_histogram_transitions(const Table& delta) {
    HistTransitions transitions{};
    for (int h = 0; h < 330; ++h)
        for (int label = 0; label < 7; ++label)
            transitions[h][label] = histogram_transition(delta, histograms[h], label);
    return transitions;
}

bool check_all_pairs(const Table& delta) {
    HistTransitions transitions = build_histogram_transitions(delta);

    std::array<int, 660> stamp{};
    std::array<int, 660> distance{};
    int generation = 0;
    std::array<int, 660> queue{};
    for (int start = 0; start < 5; ++start) {
        ++generation;
        int head = 0, tail = 0;
        int initial = pure_histogram[start];
        queue[tail++] = initial;
        stamp[initial] = generation;
        distance[initial] = 0;
        std::array<int, 5> target_distance;
        target_distance.fill(-1);
        while (head < tail) {
            int node = queue[head++];
            int active = node >= 330;
            int h = node % 330;
            if (active) {
                for (int target = 0; target < 5; ++target) {
                    if (h == pure_histogram[target] && target_distance[target] < 0) {
                        target_distance[target] = distance[node];
                    }
                }
            }
            for (int label = 0; label < 7; ++label) {
                int target_hist = transitions[h][label];
                if (target_hist < 0) continue;
                int target_active = active || label >= 2;
                int next = target_hist + (target_active ? 330 : 0);
                if (stamp[next] != generation) {
                    stamp[next] = generation;
                    distance[next] = distance[node]+1;
                    queue[tail++] = next;
                }
            }
        }
        max_product_reached = std::max<uint64_t>(max_product_reached, tail);
        for (int target = 0; target < 5; ++target) {
            if (target_distance[target] < 0) {
                counterexample = true;
                counterexample_table = delta;
                counterexample_start = start;
                counterexample_target = target;
                return false;
            }
            ++pair_count;
            ++horizon_histogram[target_distance[target]];
            if (target_distance[target] > maximum_horizon) {
                maximum_horizon = target_distance[target];
                maximum_table = delta;
                maximum_start = start;
                maximum_target = target;
            }
        }
    }
    return true;
}

std::array<std::string, 7> extract_witness(const Table& delta,
                                           int start, int target) {
    HistTransitions transitions = build_histogram_transitions(delta);
    std::array<int, 660> previous;
    std::array<int, 660> previous_label;
    std::array<int, 660> distance{};
    previous.fill(-2);
    previous_label.fill(-1);
    std::array<int, 660> queue{};
    int head = 0, tail = 0;
    int initial = pure_histogram[start];
    int goal = pure_histogram[target]+330;
    previous[initial] = -1;
    queue[tail++] = initial;
    while (head < tail && previous[goal] == -2) {
        int node = queue[head++];
        int active = node >= 330;
        int h = node % 330;
        for (int label = 0; label < 7; ++label) {
            int target_hist = transitions[h][label];
            if (target_hist < 0) continue;
            int next = target_hist + ((active || label >= 2) ? 330 : 0);
            if (previous[next] == -2) {
                previous[next] = node;
                previous_label[next] = label;
                distance[next] = distance[node]+1;
                queue[tail++] = next;
            }
        }
    }
    assert(previous[goal] != -2);
    std::vector<int> labels;
    for (int node = goal; previous[node] != -1; node = previous[node])
        labels.push_back(previous_label[node]);
    std::reverse(labels.begin(), labels.end());
    assert(static_cast<int>(labels.size()) == distance[goal]);

    std::array<int, 7> states{};
    states.fill(start);
    std::array<std::string, 7> words{};
    bool active = false;
    for (int label : labels) {
        std::array<int, 7> column{};
        if (label < 2) {
            column.fill(label);
        } else {
            int selected_state = label-2;
            int selected_role = -1;
            for (int role = 0; role < 7; ++role)
                if (states[role] == selected_state) {
                    selected_role = role;
                    break;
                }
            assert(selected_role >= 0);
            column[selected_role] = 1;
            active = true;
        }
        for (int role = 0; role < 7; ++role) {
            words[role].push_back(char('0'+column[role]));
            int next = delta[2*states[role]+column[role]];
            assert(next != U);
            states[role] = next;
        }
    }
    assert(active);
    for (int state : states) assert(state == target);
    return words;
}

void process_table(const Table& delta) {
    ++orbit_count;
    bool above_blue = rate_above(delta, BLUE, 1);
    bool above_gate = rate_above(delta, GNUM, GDEN);
    above_blue_count += above_blue;
    above_gate_count += above_gate;
    if (above_blue && !check_all_pairs(delta)) return;
    if (orbit_count % 10000 == 0) {
        std::cerr << "PROGRESS orbits=" << orbit_count
                  << " above_gate=" << above_gate_count
                  << " max_h=" << maximum_horizon << "\n";
    }
}

void generate(Table& delta, int position, int maximum_label) {
    if (counterexample) return;
    if (position == 10) {
        if (maximum_label != 4) return;
        ++accessible_count;
        if (!strongly_connected(delta)) return;
        ++rooted_strong_count;
        if (!is_unrooted_canonical(delta)) return;
        process_table(delta);
        return;
    }
    int row = position/2;
    if (row > maximum_label) return;
    for (int value = U; value <= maximum_label; ++value) {
        delta[position] = value;
        generate(delta, position+1, maximum_label);
        if (counterexample) return;
    }
    if (maximum_label < 4) {
        delta[position] = maximum_label+1;
        generate(delta, position+1, maximum_label+1);
    }
}

void print_table(const Table& delta) {
    std::cout << "(";
    for (int i = 0; i < 10; ++i) {
        if (i) std::cout << ",";
        std::cout << delta[i];
    }
    std::cout << ")";
}

int main() {
    build_histograms();
    verify_physical_role_geometry();
    Table delta{};
    generate(delta, 0, 0);
    std::cout << "ACCESSIBLE_ROOTED " << accessible_count << "\n";
    std::cout << "STRONG_ROOTED " << rooted_strong_count << "\n";
    std::cout << "STRONG_S5_ORBITS " << orbit_count << "\n";
    std::cout << "ABOVE_BLUE_ORBITS " << above_blue_count << "\n";
    std::cout << "ABOVE_GATE_ORBITS " << above_gate_count << "\n";
    if (counterexample) {
        std::cout << "COUNTEREXAMPLE table=";
        print_table(counterexample_table);
        std::cout << " start=" << counterexample_start
                  << " target=" << counterexample_target << "\n";
        std::cout << "EXPLICIT_SAFE_ABOVE_GATE_COUNTEREXAMPLE\n";
        return 2;
    }
    const std::map<int, uint64_t> expected_horizons = {
        {1,26426}, {2,141451}, {3,344137}, {4,399252}, {5,264911},
        {6,120113}, {7,38799}, {8,12029}, {9,4009}, {10,1510},
        {11,682}, {12,376}, {13,277}, {14,181}, {15,139}, {16,98},
        {17,60}, {18,35}, {19,32}, {20,27}, {21,23}, {22,14},
        {23,10}, {24,6}, {25,3}
    };
    const Table expected_maximum = {U,1,2,U,3,U,4,U,1,0};
    assert(accessible_count == 632700);
    assert(rooted_strong_count == 320253);
    assert(orbit_count == 64057);
    assert(above_blue_count == 54184);
    assert(above_gate_count == 49047);
    assert(pair_count == 1354600);
    assert(max_product_reached == 335);
    assert(horizon_histogram == expected_horizons);
    assert(maximum_horizon == 25);
    assert(maximum_table == expected_maximum);
    assert(maximum_start == 0 && maximum_target == 0);
    std::cout << "PAIRS " << pair_count << "\n";
    std::cout << "MAX_PRODUCT_REACHABLE " << max_product_reached << "\n";
    std::cout << "HORIZONS";
    for (const auto& entry : horizon_histogram)
        std::cout << " " << entry.first << ":" << entry.second;
    std::cout << "\n";
    std::cout << "MAX_HORIZON " << maximum_horizon << " table=";
    print_table(maximum_table);
    std::cout << " start=" << maximum_start << " target=" << maximum_target << "\n";
    std::array<std::string, 7> witness = extract_witness(
        maximum_table, maximum_start, maximum_target);
    assert(witness[0] == "1000110001100011000110001");
    for (int role = 1; role < 7; ++role)
        assert(witness[role] == "1000000000000000000000001");
    std::cout << "MAX_WITNESS";
    for (const std::string& word : witness) std::cout << " " << word;
    std::cout << "\n";
    std::cout << "PASS_FIVE_STATE_STRONG_ORBIT_WALL\n";
    return 0;
}
