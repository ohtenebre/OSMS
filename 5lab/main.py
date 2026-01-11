import numpy as np
import matplotlib.pyplot as plt
import glob

crc_info = {
    'crc2': {'r': 2, 'color': 'blue', 'label': 'CRC-2'},
    'crc3': {'r': 3, 'color': 'green', 'label': 'CRC-3'},
    'crc4': {'r': 4, 'color': 'orange', 'label': 'CRC-4'},
    'crc7': {'r': 7, 'color': 'red', 'label': 'CRC-7'}
}

plt.figure(figsize=(12, 7))

for file in glob.glob("crc*_results.txt"):
    prefix = file.split('_')[0]
    if prefix not in crc_info:
        continue

    try:
        data = np.loadtxt(file, comments="#")
        N_vals = data[:, 0]
        p_undetected = data[:, 1]

        info = crc_info[prefix]
        r = info['r']
        color = info['color']
        label = info['label']

        plt.plot(N_vals, p_undetected, 'o-', color=color, markersize=3, linewidth=1.5, label=label)

        plt.axhline(y=2**(-r), color=color, linestyle=':', linewidth=1.2)

        plt.axvline(x=2**r - 1, color=color, linestyle='--', linewidth=1.2)

    except Exception as e:
        print(f"Ошибка при чтении {file}: {e}")

plt.title("Вероятность необнаружения двойных ошибок для разных CRC")
plt.xlabel("Длина сообщения N")
plt.ylabel("Вероятность необнаружения")
plt.grid(True)
plt.legend()
plt.tight_layout()
# plt.savefig("crc.png")
plt.show()