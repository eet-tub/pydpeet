import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Input sizes
n = np.arange(1, 100)

# Truncated x-values for fast-growing functions
n_2n = n[:20]
n_fact = n[:10]

# Define time complexity functions
functions = [
    (np.ones_like(n), "O(1)"),
    (np.log2(n), "O(log n)"),
    (n, "O(n)"),
    (n * np.log2(n), "O(n log n)"),
    (n**2, "O(n²)"),
    (2**n_2n, "O(2ⁿ)"),
    (np.array([np.math.factorial(i) for i in n_fact]), "O(n!)")
]

# Create a custom green-yellow-red gradient
colors = ["green", "yellow", "red"]
cmap = LinearSegmentedColormap.from_list("green_yellow_red", colors, N=len(functions))
gradient_colors = [cmap(i / (len(functions) - 1)) for i in range(len(functions))]

# Plotting
plt.figure(figsize=(16, 12))
for i, (f, label) in enumerate(functions):
    if label == "O(2ⁿ)":
        plt.plot(n_2n, f, label=label, color=gradient_colors[i], linewidth=5)
    elif label == "O(n!)":
        plt.plot(n_fact, f, label=label, color=gradient_colors[i], linewidth=5)
    else:
        plt.plot(n, f, label=label, color=gradient_colors[i], linewidth=5)

# Final plot adjustments
plt.ylim(0, 100)
plt.xlabel("Eingabegröße (n)", fontsize=30)
plt.ylabel("Menge Operationen/Speicher", fontsize=30)
#plt.title("Visualisierung verschiedener Funktionen und derer O-Notationen", fontsize=30)
plt.legend(fontsize=30)
plt.grid(True)
plt.xticks(fontsize=30)
plt.yticks(fontsize=30)
plt.tight_layout()
plt.show()