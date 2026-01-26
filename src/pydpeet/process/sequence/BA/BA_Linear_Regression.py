import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Random data generation (linear with noise)
np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y_true = 3 * X + 2
y = y_true + np.random.randn(100, 1) *0.7 # add some noise

# Fit linear model
model = LinearRegression()
model.fit(X, y)

# Extract parameters
a = model.coef_[0][0]
b = model.intercept_[0]

# Predict using linear model
X_fit = np.linspace(0, 2, 200).reshape(-1, 1)
y_pred = a * X_fit + b

# Plot
plt.figure(figsize=(16, 12))
plt.scatter(X, y, color='blue', label='Datenpunkte', s=100)
plt.plot(X_fit, y_pred, color='red', label = 'Regressionslinie', linewidth=5)

plt.xlabel('X-Wert', fontsize=40)
plt.ylabel('Y-Wert', fontsize=40)
# plt.title('Lineare Regression', fontsize=40)
plt.legend(fontsize=40)
plt.grid(True)
plt.xticks(fontsize=30)
plt.yticks(fontsize=30)
plt.tight_layout()
plt.show()