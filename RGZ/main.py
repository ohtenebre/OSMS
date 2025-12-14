from matplotlib import pyplot as plt
import numpy as np

def str_in_askii(str_fi, type):
    if type == 0:
        askii = []
        bits = []

        for i in str_fi:
            askii.append(ord(i))
        for i in askii:
            bin_num = bin(int(i))
            bin_num = bin_num[2:]
            bin_num = bin_num.zfill(8)

            bits += (int(char) for char in bin_num)
        return bits
    else:
        words = []
        for i in range(0, len(str_fi), 8):
            one_char_bits = str_fi[i:i+8]
            one_char_str = ''.join(str(b) for b in one_char_bits)
            words.append(chr(int(one_char_str, 2)))
        return ''.join(words)

def CRC_generator(bits):
    M = 7
    G_x = [1, 1, 1, 0, 1, 1, 1, 0]
    n = len(bits)
    
    temp = bits[:] + [0] * M

    
    for i in range(n):
        if temp[i] == 1:
            for j in range(8):
                temp[i + j] ^= G_x[j]

    CRC = temp[n:n + M]
    codeword = bits + CRC
    return codeword, CRC, M

def generate_gold_seq():
    rex_x = [1, 0, 1, 0, 0]
    rex_y = [1, 1, 0, 1, 1]

    G = 2**5 - 1
    m = 5

    out = []

    for i in range (0, G):
        out.append(rex_x[4] ^ rex_y[4])

        temp1 = rex_x[2] ^ rex_x[4]
        temp2 = rex_y[2] ^ rex_y[4]

        for j in range(m-1, 0, -1):
            rex_x[j] = rex_x[j-1]
            rex_y[j] = rex_y[j-1]

        rex_x[0] = temp1
        rex_y[0] = temp2

    return out, G

def bpsk(bits):
    A = 100
    symbols = []
    for i in bits:
        if i == 0:
            symbols.append(A)
        else:
            symbols.append(-A)
    return symbols

def upsampling(symbols, N):
    symbols_L = np.zeros(len(symbols) * N)
    imp = np.ones(N)
    for i in range(0, len(symbols)):
        symbols_L[i*N] = symbols[i]

    symbols_L = np.convolve(symbols_L, imp)
    symbols_L = symbols_L[:len(symbols)*N]

    return symbols_L

def norm_corr(arr1, arr2):
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)
    return np.sum(arr1 * arr2) / np.sqrt(np.sum(arr1**2) * np.sum(arr2**2))

def corr_sync(signal, gold_seq, G, N):
    cors = []
    window = np.zeros(G*N)
    gold_seq_syms = bpsk(gold_seq)
    window = upsampling(gold_seq_syms, N)

    for i in range(0, len(signal) - G*N):
        cors.append(norm_corr(window, signal[i:i + G*N]))

    return cors

def bits_recovery(signal, N):
    imp = np.ones(N)

    filtered_signal = np.convolve(signal, imp)

    bits = []

    for i in range(0, len(signal), N):
        symbols = filtered_signal[i]
        if symbols > 50:
            bits.append(0)
        elif symbols < -50:
            bits.append(1)

    return bits

def verify(bits):
    G_x = [1, 1, 1, 0, 1, 1, 1, 0]
    N = len(bits) - (len(G_x) - 1)
    M = len(G_x) - 1

    temp = bits[:]

    for i in range(N):
        if temp[i] == 1:
            for j in range(M+1):
                temp[i+j] ^= G_x[j]

    res_temp = temp[N:N+M]

    print(res_temp)

    if any(res_temp):
        return 1
    return 0

def signal_N(bits, N):
    symbols = bpsk(bits)
    symbols = upsampling(symbols, N)
    signal = np.zeros(2 * len(symbols))
    signal[:len(symbols)] = symbols
    return signal

def get_spectrum(signal):
    amp = np.fft.fftshift(np.fft.fft(signal))
    freq = np.fft.fftshift(np.fft.fftfreq(len(signal), d=1))
    return freq, np.abs(amp)

## 1) Введите с клавиатуры ваши имя и фамилию латиницей
print("Введите ваше имя и фамилию")
FI = input()

print(f'Ваши имя и фамилия: {FI}')

## 2) Сформируйте битовую последовательность, состоящую из L
# битов, кодирующих ваши имя и фамилию латинице ASCII-символов.
# Результат: массив нулей и единиц с данными и разработанный ASCII-кодер.
# Визуализируйте последовательность на графике

bits = str_in_askii(FI, 0)
L = len(bits)

# print(f'Биты: {bits}\nДлина {L}')

plt.figure()
plt.plot(np.arange(L), bits)
plt.title("Битовая последовательность")
plt.xlabel("Индекс")
plt.ylabel("Значение")
# plt.savefig("bit_sequence.png")

## 3) Вычислите CRC длиной M бит для данной последовательности,
# используя входные данные для своего варианта из работы №5 и добавьте к
# битовой последовательности. Результат: CRC-генератор и выведенный в
# терминал CRC.

bits_w_crc, CRC, M = CRC_generator(bits)

# print(f'CRC: {CRC}')

## 4) Для того, чтобы приемник смог корректно принимать такой сигнал
# и находить моменты начала, нужно реализовать синхронизацию. Для этого
# перед отправкой полученной последовательности добавьте
# последовательность Голда, которую вы реализовывали в работе №4, длиной
# G-бит. Результат: функция генерации последовательности Голда и массив с
# битами данных, CRC и синхронизации. Визуализируйте последовательность
# на графике

gold_seq, G = generate_gold_seq()

# print(f'Последовательность голда: {gold_seq}')

plt.figure()
plt.plot(np.arange(G), gold_seq)
plt.title("Последовательность голда")
plt.xlabel("Индекс")
plt.ylabel("Значение")
# plt.savefig("gold_seq.png")

## 5) Преобразуйте биты с данными во временные отсчеты сигналов,
# так чтобы на каждый бит приходилось N-отсчетов. Результат: массив длиной
# Nx(L+M+G) нулей и единиц – но это уже временные отсчеты сигнала (пример
# амплитудной модуляции). Визуализируйте последовательность на графике

N = 8
total_bits = gold_seq + bits_w_crc

symbols = bpsk(total_bits)
symbols = upsampling(symbols, N)

B = N * (L + M + G)

# print(f'Символы BPSK: {symbols}\nДлина: {B}')

plt.figure()
plt.plot(np.arange(B), symbols)
plt.title("Символы BPSK")
plt.xlabel("Индекс")
plt.ylabel("Значение")
# plt.savefig("bpsk_symbols.png")

## 6) Создайте нулевой массив длиной 2хNx(L+M+G). Введите с
# клавиатуры число от 0 до Nx(L+M+G) и в соответствие с введенным
# значением вставьте в него массив значений из п.5. Результат – массив Signal –
# визуализируйте на графике.

signal = np.zeros(2*B)

print(f'Введите сдвиг от 0 до {B}')
shift = int(input())

if shift > B:
    print(f'Shift: {B}')
    shift = B
elif shift < 0:
    print('Shift: 0')
    shift = 0

signal[shift : shift + len(symbols)] = symbols

# print(f'Сигнал: {signal}')

plt.figure()
plt.plot(np.arange(2*B), signal)
plt.title("Сигнал")
plt.xlabel("Индекс")
plt.ylabel("Значение")
# plt.savefig("signal.png")

## 7) Добавление шумов

print("Введите стандратное отклонения")
sigma = float(input())

noise = np.random.normal(0, sigma, size=len(signal))

received_signal = signal + noise

plt.figure()
plt.plot(np.arange(2*B), received_signal)
plt.title("Принятый сигнал")
plt.xlabel("Индекс")
plt.ylabel("Значение")
# plt.savefig("received_signal.png")

## 8) Реализуйте функцию корреляционного приема и определите, начиная
# с какого отсчета (семпла) начинается синхросигнал в полученном
# массиве, удалите лишние биты до этого массива, выведите значение
# в терминал. Результат: функция корреляционного приемника.

cors = corr_sync(received_signal, gold_seq, G, N)

start_index = np.argmax(cors)

print(f'Start index: {start_index}')

received_signal = received_signal[start_index :]# start_index + N*(G + L + M)

plt.figure()
plt.plot(np.arange(len(received_signal)), received_signal)
plt.title("Принятый сигнал без лишних битов")
plt.xlabel("Индекс")
plt.ylabel("Значение")
# plt.savefig("received_signal_without_bits.png")

## 9) Зная длительность в отсчетах N каждого символа, разберите
# оставшиеся символы. Накапливайте по N отсчетов и сравнивайте их
# с пороговым значением P (подумайте, какое значение порога следует
# выбрать, чтобы интерпретировать полученные семплы нулями или
# единицами). Напишите функцию, которая будет принимать решение
# по каждым N отсчетам – 0 передавался или 1, на выходе которой
# должно быть (L+M+G) битов данных. Лишние отсчеты можно отбросить. 

received_bits = bits_recovery(received_signal, N)

## 10) Удалите из полученного массива G-бит последовательности синхронизации.

received_bits = received_bits[G+1:]

plt.figure()
plt.subplot(2, 1, 1)
plt.plot(np.arange(len(received_bits)), received_bits)
plt.title("Mathed filtered сигнал")
plt.xlabel("Индекс")
plt.ylabel("Значение")
plt.subplot(2, 1, 2)
plt.plot(np.arange(len(bits_w_crc)), bits_w_crc)
plt.title("Mathed filtered сигнал")
plt.xlabel("Индекс")
plt.ylabel("Значение")
# plt.savefig("Mathed filtered_signal.png")

## 11) Проверьте корректность приема бит, посчитав CRC. Выведите в терминал информацию о факте наличия или отсутствия ошибки

result = verify(received_bits)

## 12) Если ошибок в данных нет, то удалит биты CRC и оставшиеся
# данные подайте на ASCII-декодер, чтобы восстановить посимвольно
# текст. Выведите результат на экран.

if result == 0:
    print("Биты совпали")
    received_bits = received_bits[:len(received_bits) - M]
    words = str_in_askii(received_bits, 1)
    print(f'Принятый текст: {words}')
else:
    print("Биты не совпали")
    words = str_in_askii(received_bits, 1)
    print(f'Принятый текст: {words}')

## 13) Визуализируйте спектр передаваемого и принимаемого
# (зашумленного) сигналов. Измените длительность символа,
# уменьшите ее в два раза и увеличьте тоже вдвое. Выведите на одном
# графике спектры всех трех сигналов (с короткими, средними и
# длинными символами).

N_short = N // 2
N_mid = N
N_long = 2 * N

signal_short = signal_N(total_bits, N_short)
signal_mid = signal_N(total_bits, N_mid)
signal_long = signal_N(total_bits, N_long)

f_s, A_s = get_spectrum(signal_short)
f_m, A_m = get_spectrum(signal_mid)
f_l, A_l = get_spectrum(signal_long)

plt.figure()
plt.plot(f_s, A_s, label=f"N = {N_short}")
plt.plot(f_m, A_m, label=f"N = {N_mid}")
plt.plot(f_l, A_l, label=f"N = {N_long}")
plt.title("Спектры сигналов при разной длительности символа")
plt.xlabel("Частота")
plt.ylabel("Амплитуда")
plt.legend()
plt.grid()
plt.show()