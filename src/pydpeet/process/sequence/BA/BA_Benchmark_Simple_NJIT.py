import time
import numpy as np
import matplotlib.pyplot as plt
from numba import njit


# Simple function: compute factorial-like product


def factorial(n):
    result = 1.0
    for i in range(1, n + 1):
        result *= i
    return result


@njit
def factorial_njit(n):
    result = 1.0
    for i in range(1, n + 1):
        result *= i
    return result


# Prepare input sizes for comparison: 10^7 and 10^8
sizes = [10 ** 8]
labels = ["10⁸"]
python_times = []
numba_times = []

# Warm up JIT compilation (first call compiles)
factorial_njit(10)

for n_1 in sizes:
    # Time pure Python function
    start = time.time()
    factorial(n_1)
    end = time.time()
    python_times.append(end - start)

    # Time JIT-compiled version
    start = time.time()
    factorial_njit(n_1)
    end = time.time()
    numba_times.append(end - start)

# Bar plot comparison
x = np.arange(len(labels))
width = 0.35

plt.figure(figsize=(3, 8))
bar1 = plt.bar(x - width / 2, python_times, width, label='Ohne @njit')
bar2 = plt.bar(x + width / 2, numba_times, width, label='Mit @njit')

# Add percentage improvement annotations
for i_1 in range(len(labels)):
    if numba_times[i_1] > 0:
        improvement = 100 * (python_times[i_1] - numba_times[i_1]) / python_times[i_1]
        #plt.text(x[i_1], max(python_times[i_1], numba_times[i_1]), f"{improvement:.1f}% faster",
        #         ha='center', va='bottom', fontsize=14, rotation=0)

plt.xticks(x, labels, fontsize=14)
plt.yticks(fontsize=14)
plt.yscale("log")
plt.ylabel("Laufzeit (s)", fontsize=14)
plt.xlabel("Anzahl Iterationen", fontsize=14)
plt.title("Laufzeitvergleich von factorial() mit/ohne @njit", fontsize=14)
plt.legend(fontsize = 14)
plt.grid(True, axis="y", linestyle="--", linewidth=0.5)
plt.show()
