#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>

// Independent S6-orbit completeness check by Burnside's lemma.  This does
// not use the primary replay's min-over-six-rooted-codes representative test.

using Map = std::array<std::int8_t, 6>;
using Table = std::array<std::int8_t, 12>;
using Perm = std::array<int, 6>;

constexpr int U = -1;
std::uint64_t independent_accessible_rooted = 0;
std::uint64_t independent_strong_rooted = 0;

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

void generate_rooted(Table& table, int position, int introduced) {
    if (position == 12) {
        if (introduced != 6) return;
        ++independent_accessible_rooted;
        independent_strong_rooted += strongly_connected(table);
        return;
    }
    if (position/2 >= introduced) return;
    for (int target = U; target < introduced; ++target) {
        table[position] = static_cast<std::int8_t>(target);
        generate_rooted(table, position+1, introduced);
    }
    if (introduced < 6) {
        table[position] = static_cast<std::int8_t>(introduced);
        generate_rooted(table, position+1, introduced+1);
    }
}

std::vector<std::vector<int>> cycles_of(const Perm& permutation) {
    std::array<bool, 6> seen{};
    std::vector<std::vector<int>> cycles;
    for (int start = 0; start < 6; ++start) if (!seen[start]) {
        std::vector<int> cycle;
        int state = start;
        do {
            cycle.push_back(state);
            seen[state] = true;
            state = permutation[state];
        } while (state != start);
        cycles.push_back(cycle);
    }
    return cycles;
}

int iterate(const Perm& permutation, int state, int power) {
    while (power--) state = permutation[state];
    return state;
}

void generate_maps_recursive(const Perm& permutation,
                             const std::vector<std::vector<int>>& cycles,
                             int cycle_index, Map& map,
                             std::vector<Map>& output) {
    if (cycle_index == static_cast<int>(cycles.size())) {
        output.push_back(map);
        return;
    }
    const std::vector<int>& cycle = cycles[cycle_index];
    for (int state : cycle) map[state] = U;
    generate_maps_recursive(permutation, cycles, cycle_index+1, map, output);
    for (int target = 0; target < 6; ++target) {
        if (iterate(permutation, target, static_cast<int>(cycle.size())) != target)
            continue;
        int image = target;
        for (int source : cycle) {
            map[source] = static_cast<std::int8_t>(image);
            image = permutation[image];
        }
        generate_maps_recursive(permutation, cycles, cycle_index+1, map, output);
    }
}

std::vector<Map> equivariant_partial_maps(const Perm& permutation) {
    Map map{};
    std::vector<Map> output;
    auto cycles = cycles_of(permutation);
    generate_maps_recursive(permutation, cycles, 0, map, output);
    for (const Map& candidate : output) {
        for (int state = 0; state < 6; ++state) {
            int left = candidate[permutation[state]];
            int right = candidate[state] < 0 ? U : permutation[candidate[state]];
            assert(left == right);
        }
    }
    return output;
}

std::uint64_t fixed_strong_tables(const Perm& permutation) {
    std::vector<Map> maps = equivariant_partial_maps(permutation);
    std::uint64_t strong = 0;
    Table table{};
    for (const Map& blue : maps) {
        for (const Map& red : maps) {
            for (int state = 0; state < 6; ++state) {
                table[2*state] = blue[state];
                table[2*state+1] = red[state];
            }
            strong += strongly_connected(table);
        }
    }
    return strong;
}

Perm permutation_with_cycles(const std::vector<int>& lengths) {
    Perm permutation{};
    int first = 0;
    for (int length : lengths) {
        for (int offset = 0; offset < length; ++offset)
            permutation[first+offset] = first+(offset+1)%length;
        first += length;
    }
    assert(first == 6);
    return permutation;
}

int main() {
    struct Type { std::vector<int> cycles; int class_size; const char* name; };
    const std::vector<Type> types = {
        {{1,1,1,1,1,1},1,"1^6"}, {{2,1,1,1,1},15,"2,1^4"},
        {{2,2,1,1},45,"2^2,1^2"}, {{2,2,2},15,"2^3"},
        {{3,1,1,1},40,"3,1^3"}, {{3,2,1},120,"3,2,1"},
        {{3,3},40,"3^2"}, {{4,1,1},90,"4,1^2"},
        {{4,2},90,"4,2"}, {{5,1},144,"5,1"}, {{6},120,"6"}
    };
    int class_total = 0;
    std::uint64_t burnside_sum = 0;
    std::map<std::string, std::uint64_t> fixed_counts;
    Table rooted_table{};
    generate_rooted(rooted_table, 0, 1);
    assert(independent_accessible_rooted == 23836540);
    assert(independent_strong_rooted == 12346720);
    for (const Type& type : types) {
        class_total += type.class_size;
        std::uint64_t fixed;
        if (type.class_size == 1) {
            // Independent rooted generation gives 12,346,720 strong rooted
            // codes. Accessibility makes the stabilizer of a fixed root
            // trivial, hence 5! labeled tables per rooted code.
            fixed = independent_strong_rooted*120;
        } else {
            fixed = fixed_strong_tables(permutation_with_cycles(type.cycles));
        }
        fixed_counts[type.name] = fixed;
        burnside_sum += std::uint64_t(type.class_size)*fixed;
        std::cout << "BURNSIDE_TYPE " << type.name
                  << " class=" << type.class_size
                  << " fixed_strong=" << fixed << "\n";
    }
    assert(class_total == 720);
    assert(burnside_sum % 720 == 0);
    assert(burnside_sum/720 == 2058472);
    std::cout << "INDEPENDENT_ROOTED accessible="
              << independent_accessible_rooted
              << " strong=" << independent_strong_rooted << "\n";
    std::cout << "BURNSIDE_SUM " << burnside_sum
              << " S6_ORBITS " << burnside_sum/720 << "\n";
    std::cout << "PASS_INDEPENDENT_SIX_STATE_BURNSIDE_ORBIT_COUNT\n";
    return 0;
}
