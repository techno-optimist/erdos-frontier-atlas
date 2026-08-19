#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <queue>
#include <string>
#include <unordered_map>
#include <vector>

constexpr int N = 15;
constexpr int COPIES = 7;
constexpr int LABELS = N + 2;
constexpr int U = -1;
using Map = std::array<std::int8_t, N>;
using Hist = std::array<std::uint8_t, N>;

std::vector<Hist> histograms;
std::unordered_map<std::uint64_t, int> histogram_index;
std::array<int, N> pure_index{};

std::uint64_t code(const Hist& histogram) {
    std::uint64_t answer = 0;
    for (int state = 0; state < N; ++state)
        answer |= std::uint64_t(histogram[state]) << (4*state);
    return answer;
}

void build_histograms_rec(int state, int left, Hist& histogram) {
    if (state == N-1) {
        histogram[state] = static_cast<std::uint8_t>(left);
        int index = static_cast<int>(histograms.size());
        histogram_index.emplace(code(histogram), index);
        histograms.push_back(histogram);
        return;
    }
    for (int amount = 0; amount <= left; ++amount) {
        histogram[state] = static_cast<std::uint8_t>(amount);
        build_histograms_rec(state+1, left-amount, histogram);
    }
}

void build_histograms() {
    Hist histogram{};
    histogram_index.reserve(150000);
    build_histograms_rec(0, COPIES, histogram);
    assert(histograms.size() == 116280); // C(21,7)
    for (int state = 0; state < N; ++state) {
        Hist pure{};
        pure[state] = COPIES;
        pure_index[state] = histogram_index.at(code(pure));
    }
}

struct Product {
    std::vector<std::array<int, LABELS>> transitions;

    Product(const Map& blue, const Map& red)
        : transitions(histograms.size()) {
        for (int index = 0; index < static_cast<int>(histograms.size()); ++index) {
            const Hist& histogram = histograms[index];
            for (int label = 0; label < LABELS; ++label) {
                Hist image{};
                bool valid = true;
                if (label < 2) {
                    const Map& transition = label == 0 ? blue : red;
                    for (int source = 0; source < N; ++source) {
                        int amount = histogram[source];
                        if (!amount) continue;
                        int target = transition[source];
                        if (target < 0) { valid = false; break; }
                        image[target] += static_cast<std::uint8_t>(amount);
                    }
                } else {
                    int selected = label-2;
                    if (!histogram[selected] || red[selected] < 0) {
                        valid = false;
                    } else {
                        ++image[red[selected]];
                        for (int source = 0; source < N; ++source) {
                            int amount = histogram[source] - (source == selected);
                            if (!amount) continue;
                            if (blue[source] < 0) { valid = false; break; }
                            image[blue[source]] += static_cast<std::uint8_t>(amount);
                        }
                    }
                }
                transitions[index][label] = valid
                    ? histogram_index.at(code(image)) : -1;
            }
        }
    }

    std::vector<int> missing_by_start(int start, int& max_horizon,
                                      int& max_reached, bool verbose) const {
        const int H = static_cast<int>(histograms.size());
        std::vector<int> distance(2*H, -1);
        std::vector<int> parent(2*H, -1);
        std::vector<std::int8_t> parent_label(2*H, -1);
        std::vector<int> queue(2*H);
        int head = 0, tail = 0;
        int initial = pure_index[start];
        queue[tail++] = initial;
        distance[initial] = 0;
        while (head < tail) {
            int node = queue[head++];
            bool active = node >= H;
            int histogram = node % H;
            for (int label = 0; label < LABELS; ++label) {
                int image = transitions[histogram][label];
                if (image < 0) continue;
                int next = image + ((active || label >= 2) ? H : 0);
                if (distance[next] >= 0) continue;
                distance[next] = distance[node]+1;
                parent[next] = node;
                parent_label[next] = static_cast<std::int8_t>(label);
                queue[tail++] = next;
            }
        }
        max_reached = std::max(max_reached, tail);
        std::vector<int> missing;
        for (int target = 0; target < N; ++target) {
            int d = distance[H+pure_index[target]];
            if (d < 0) missing.push_back(target);
            else max_horizon = std::max(max_horizon, d);
        }
        if (verbose)
            std::cout << "START " << start << " reached=" << tail
                      << " missing=" << missing.size() << "\n";
        if (verbose && start == 0 && missing.empty()) {
            for (int target : {0, 14}) {
                int node = H+pure_index[target];
                std::vector<int> labels;
                while (parent[node] >= 0) {
                    labels.push_back(parent_label[node]);
                    node = parent[node];
                }
                std::reverse(labels.begin(), labels.end());
                std::cout << "WITNESS 0->" << target << " labels=";
                for (int label : labels) std::cout << label << ',';
                std::cout << "\n";
            }
        }
        return missing;
    }
};

Map blue_chain() {
    Map blue{};
    for (int state = 0; state < N; ++state)
        blue[state] = static_cast<std::int8_t>(state+1 < N ? state+1 : U);
    return blue;
}

Map parse_red(const std::string& mode) {
    Map red{};
    if (mode == "reset") {
        red.fill(0);
    } else if (mode == "identity") {
        for (int state = 0; state < N; ++state) red[state] = state;
    } else if (mode == "tail-reset") {
        for (int state = 0; state < N; ++state) red[state] = state;
        red[N-1] = 0;
    } else if (mode == "head-reset") {
        for (int state = 0; state < N; ++state) red[state] = (state+1)%N;
        red[0] = 0;
    } else if (mode == "reverse") {
        for (int state = 0; state < N; ++state) red[state] = N-1-state;
    } else if (mode == "cycle") {
        for (int state = 0; state < N; ++state) red[state] = (state+1)%N;
    } else if (mode.rfind("one1-", 0) == 0) {
        red.fill(0);
        int source = std::stoi(mode.substr(5));
        assert(source >= 0 && source < N);
        red[source] = 1;
    } else {
        std::cerr << "unknown red mode\n";
        std::exit(1);
    }
    return red;
}

int main(int argc, char** argv) {
    assert(argc == 2);
    build_histograms();
    Map blue = blue_chain();
    if (std::string(argv[1]) == "all-critical") {
        int total_missing = 0, global_horizon = 0, global_reached = 0;
        std::uint64_t reached_sum = 0;
        for (int kind = -1; kind < N; ++kind) {
            Map red{};
            red.fill(0);
            std::string name = "reset";
            if (kind >= 0) {
                red[kind] = 1;
                name = "one1-" + std::to_string(kind);
            }
            Product product(blue, red);
            int missing = 0, max_horizon = 0, max_reached = 0;
            for (int start = 0; start < N; ++start)
                missing += static_cast<int>(product.missing_by_start(
                    start, max_horizon, max_reached, false).size());
            total_missing += missing;
            global_horizon = std::max(global_horizon, max_horizon);
            global_reached = std::max(global_reached, max_reached);
            reached_sum += max_reached;
            std::cout << "CRITICAL_TABLE mode=" << name
                      << " missing_pairs=" << missing
                      << " max_horizon=" << max_horizon
                      << " max_reached=" << max_reached << "\n";
        }
        assert(total_missing == 0);
        assert(global_horizon == 18);
        assert(global_reached == 65107);
        assert(reached_sum == 920075);
        std::cout << "FIFTEEN_CHAIN_CRITICAL tables=16 pairs=3600"
                  << " missing=0 max_horizon=" << global_horizon
                  << " max_reached=" << global_reached
                  << " reached_sum=" << reached_sum << "\n";
        std::cout << "PASS_EXACT_FIFTEEN_CHAIN_CRITICAL_PRODUCT_SCREEN\n";
        return 0;
    }
    Map red = parse_red(argv[1]);
    Product product(blue, red);
    int missing_pairs = 0, max_horizon = 0, max_reached = 0;
    for (int start = 0; start < N; ++start)
        missing_pairs += static_cast<int>(
            product.missing_by_start(start, max_horizon, max_reached, true).size());
    std::cout << "CHAIN_PRODUCT mode=" << argv[1]
              << " missing_pairs=" << missing_pairs
              << " max_horizon=" << max_horizon
              << " max_reached=" << max_reached << "\n";
    return missing_pairs ? 2 : 0;
}
