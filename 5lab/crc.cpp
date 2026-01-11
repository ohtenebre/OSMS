#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <ctime>
#include <fstream>
#include <vector>
#include <string>

using namespace std;

int verify(const int16_t *bits, const int16_t *G_x, int16_t N, int16_t r) {
    int16_t *temp = (int16_t*)calloc(N + r, sizeof(int16_t));
    if (!temp) return -1;

    for (size_t i = 0; i < (size_t)(N + r); i++) {
        temp[i] = bits[i];
    }

    for (size_t i = 0; i < (size_t)N; i++) {
        if (temp[i] == 1) {
            for (size_t j = 0; j <= (size_t)r; j++) {
                if (i + j < (size_t)(N + r)) {
                    temp[i + j] ^= G_x[j];
                }
            }
        }
    }

    for (size_t i = N; i < (size_t)(N + r); i++) {
        if (temp[i] != 0) {
            free(temp);
            return 1;
        }
    }
    free(temp);
    return 0;
}

void run_experiment(int16_t N, const vector<int16_t>& G_vec, int16_t r, ofstream &out) {
    const int16_t* G_x = G_vec.data();
    int16_t *bits = (int16_t*)calloc(N + r, sizeof(int16_t));
    if (!bits) return;

    for (size_t i = 0; i < (size_t)N; i++) {
        bits[i] = rand() % 2;
    }

    int16_t *temp = (int16_t*)calloc(N + r, sizeof(int16_t));
    for (size_t i = 0; i < (size_t)N; i++) temp[i] = bits[i];

    for (size_t i = 0; i < (size_t)N; i++) {
        if (temp[i] == 1) {
            for (size_t j = 0; j <= (size_t)r; j++) {
                temp[i + j] ^= G_x[j];
            }
        }
    }
    for (size_t i = 0; i < (size_t)r; i++) {
        bits[N + i] = temp[N + i];
    }
    free(temp);

    int16_t detected = 0, missed = 0;
    int16_t total_bits = N + r;
    int max_pairs = min(3000, total_bits * (total_bits - 1) / 2);

    for (int count = 0; count < max_pairs; count++) {
        int pos1 = rand() % total_bits;
        int pos2 = rand() % total_bits;
        if (pos1 == pos2) continue;

        bits[pos1] ^= 1;
        bits[pos2] ^= 1;

        int res = verify(bits, G_x, N, r);
        if (res == 1) {
            detected++;
        } else {
            missed++;
        }

        bits[pos1] ^= 1;
        bits[pos2] ^= 1;
    }

    double p_miss = (double)missed / max_pairs;
    out << N << " " << p_miss << endl;
    free(bits);
}

int main() {
    srand(time(0));\

    int16_t N = 1024;

    struct CRCConfig {
        int16_t r;
        vector<int16_t> G;
        int16_t max_N;
        string name;
    };

    vector<CRCConfig> configs = {
        {2, {1, 1, 1}, N, "crc2"},
        {3, {1, 0, 1, 1}, N, "crc3"},
        {4, {1, 0, 0, 1, 1}, N, "crc4"},
        {7, {1, 0, 0, 0, 1, 0, 0, 1}, N, "crc7"}
    };

    for (const auto& cfg : configs) {
        string filename = cfg.name + "_results.txt";
        ofstream outfile(filename);
        if (!outfile.is_open()) {
            cerr << "Не удалось открыть " << filename << endl;
            continue;
        }

        outfile << "# N P_undetected\n";
        for (int16_t N = 1; N <= cfg.max_N; N += (cfg.max_N > 100 ? 5 : 1)) {
            run_experiment(N, cfg.G, cfg.r, outfile);
        }
        outfile.close();
        cout << "Сгенерировано: " << filename << endl;
    }

    return 0;
}