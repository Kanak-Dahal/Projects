#include <iostream>
#include <cmath>
#include <random>
#include <map>
#include <vector>
#include <tuple>
#include <algorithm>  
# include <chrono>
using namespace std;
using namespace std::chrono;

tuple<int, double, double> play_game(int flips_total=201) {
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> distr(0.0, 1.0);

    int heads = 0;
    int tails = 0;
    int still_playing = 1;

    double probability_heads = 0.0;
    double probability_tails = 0.0;

    for (int i=0; i<flips_total; i++) {
        if (still_playing == 0) break;

        double r = distr(gen);
        int head_or_tail = (r < 0.5) ? 1 : 0;

        if (head_or_tail == 1) heads++;
        else tails++;

        probability_heads = (double)heads / (heads + tails);
        probability_tails = (double)tails / (heads + tails);

        double abs_diff = abs(heads - tails);
        still_playing = (abs_diff < 3) ? 1 : 0;
    }

    int flips_played = heads + tails;
    int payoff = 8 - flips_played;

    return make_tuple(payoff, probability_heads, probability_tails);
}

int main() {

    auto start = high_resolution_clock::now();
    int n = 100000;
    vector<tuple<int, double, double>> results;
    results.reserve(n);

    for (int i = 0; i < n; i++) {
        results.push_back(play_game());
    }

    vector<int> payoffs;
    vector<double> heads_probs;
    vector<double> tails_probs;

    payoffs.reserve(n);
    heads_probs.reserve(n);
    tails_probs.reserve(n);

    for (auto &result : results) {
        payoffs.push_back(get<0>(result));
        heads_probs.push_back(get<1>(result));
        tails_probs.push_back(get<2>(result));
    }

    // average payoff
    double total_payoff = 0.0;
    for (int p : payoffs) total_payoff += p;
    double average_payoff = total_payoff / n;

    // min and max payoff
    int min_payoff = *min_element(payoffs.begin(), payoffs.end());
    int max_payoff = *max_element(payoffs.begin(), payoffs.end());

    // standard deviation of payoff
    double variance = 0.0;
    for (int p : payoffs) {
        variance += (p - average_payoff) * (p - average_payoff);
    }
    variance /= n;
    double std_dev = sqrt(variance);

    // expectation (like your Python code)
    double expectation = 0.0;
    for (int i = 0; i < n; i++) {
        expectation += payoffs[i] * heads_probs[i];
        expectation += payoffs[i] * tails_probs[i];
    }
    expectation /= n;

    // cumulative head/tail probabilities
    double cumm_heads_p = 0.0, cumm_tails_p = 0.0;
    for (int i = 0; i < n; i++) {
        cumm_heads_p += heads_probs[i];
        cumm_tails_p += tails_probs[i];
    }
    cumm_heads_p /= n;
    cumm_tails_p /= n;

    // Print 
    cout << "Average payoff: " << average_payoff << endl;
    cout << "Min payoff: " << min_payoff << endl;
    cout << "Max payoff: " << max_payoff << endl;
    cout << "Standard deviation of payoff: " << std_dev << endl;
    cout << "Expectation: " << expectation << endl;
    cout << "Cumulative heads probability: " << cumm_heads_p << endl;
    cout << "Cumulative tails probability: " << cumm_tails_p << endl;

    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<milliseconds>(stop - start);
    cout << "Time taken: " << duration.count()/1000 << " seconds" << endl;

    return 0;
}
