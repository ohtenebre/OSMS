import random
import numpy as np
from matplotlib import pyplot as plt

def compute_CRC(bits, G_x):
    r = len(G_x) - 1
    temp = bits + [0] * r

    for i in range(len(bits)):
        if temp[i] == 1:
            for j in range(len(G_x)):
                temp[i + j] ^= G_x[j]

    return temp[len(bits):]

def verify(bits_with_crc, G_x, N):
    r = len(G_x) - 1
    temp = bits_with_crc.copy()

    for i in range(N):
        if temp[i] == 1:
            for j in range(len(G_x)):
                temp[i + j] ^= G_x[j]

    return all(bit == 0 for bit in temp[N:])

def inject_errors(bits, k):
    idx = random.sample(range(len(bits)), k)
    for i in idx:
        bits[i] ^= 1

def experiment(N, G_x):
    r = len(G_x) - 1
    prob = []

    for k in range(0, 16):
        detected = 0
        for i in range(0 , 100):
            bits = [random.randint(0, 1) for i in range(N)]
            crc = compute_CRC(bits, G_x)
            packet = bits + crc

            inject_errors(packet, k)

            if not verify(packet, G_x, N):
                detected += 1
        prob.append(detected / 100)

    return prob

N_list = [32, 64, 128, 256, 512, 1024, 2048, 4096]

G_list = {
    2: [1, 0, 1],
    3: [1, 0, 1, 1],
    4: [1, 0, 0, 1, 1],
    5: [1, 0, 0, 1, 0, 1],
    6: [1, 0, 0, 0, 0, 1, 1],
    7: [1, 1, 1, 0, 1, 1, 1, 0]
}

for r, G in G_list.items():
    plt.figure()
    for N in N_list:
        exp = experiment(N, G)
        plt.plot(np.arange(len(exp)), exp, label=f'N={N}')

    plt.title(f"Вероятность обнаружения ошибок (r={r})")
    plt.xlabel("Количество ошибок")
    plt.ylabel("Вероятность обнаружения")
    plt.grid(True)
    plt.legend()
    # plt.savefig(f'Polynome {r}')

plt.show()