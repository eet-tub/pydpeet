import numpy as np
from matplotlib import pyplot as plt


def plot_data(x, y, x_min, x_max, tol, plot_fit_line=True, plot_fitted_points=True,
              plot_first_last_fitted_points=True, plot_segments_1=False, plot_segments_2=False,
              fit_start_end_color='red'):
    """
    Plot data points and a fitted line over the range [x_min, x_max].
    Optionally plot tolerance lines, first and last fitted points, and segments.
    """
    # --- Select range for fitting ---
    mask = (x >= x_min) & (x <= x_max)

    x_fit_data = x[mask]
    y_fit_data = y[mask]

    # Fit line to the selected range
    slope, intercept = np.polyfit(x_fit_data, y_fit_data, 1)
    print(f"Fit over [{x_min}, {x_max}]: y = {slope:.3f}x + {intercept:.3f}")

    # Generate regression line over full domain for plotting
    x_fit_line = np.linspace(min(x), max(x), 200)
    y_fit_line = slope * x_fit_line + intercept

    # --- Tolerance band ---
    y_upper = y_fit_line + tol
    y_lower = y_fit_line - tol

    # --- Plot ---
    plt.scatter(x, y, color='blue', label='Datenpunkte', s=100)
    plt.plot(x, y, color='blue', linestyle='--')

    if plot_fit_line:
        plt.plot(x_fit_line, y_fit_line, color='red', linewidth=2,
                 label=f'Fit [{x_min}-{x_max}]')

    if plot_fitted_points:
        plt.scatter(x_fit_data, y_fit_data, color='orange', s=120,
                    edgecolor='black', zorder=5, label='Fit Punkte')

    if plot_first_last_fitted_points:
        plt.scatter(x_fit_data[0], y_fit_data[0], color=fit_start_end_color, s=200,
                    edgecolor='black', zorder=6, label='Fit Start', alpha=0.5)
        plt.scatter(x_fit_data[-1], y_fit_data[-1], color=fit_start_end_color, s=200,
                    edgecolor='black', zorder=6, label='Fit Ende', alpha=0.5)

    if plot_segments_1:
        plt.scatter(x[0:6], y[0:6], color='grey', s=200,
                    edgecolor='black', zorder=6, label='Segment_1', alpha=1)
        plt.axvspan(x[0], x[5], facecolor='grey', alpha=0.4, zorder=-1, label='Segment_1')
    if plot_segments_2:
        plt.scatter(x[6:], y[6:], color='green', s=200,
                    edgecolor='black', zorder=6, label='Segment_2', alpha=1)
        plt.axvspan(x[6], x[-1], facecolor='green', alpha=0.4, zorder=-1, label='Segment_2')

    # Tolerance lines
    if plot_fit_line:
        plt.plot(x_fit_line, y_upper, color='green', linestyle='--', label=f'+/- {tol}')
        plt.plot(x_fit_line, y_lower, color='green', linestyle='--')
        plt.fill_between(x_fit_line, y_lower, y_upper, color='green', alpha=0.1)

    plt.ylim(0, 7)
    plt.xlabel('X-Achse')
    plt.ylabel('Y-Achse')
    plt.legend(loc='lower right', bbox_to_anchor=(1, 0))
    plt.show()

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
y = np.array([1, 2.3, 3, 4, 4.8, 5, 4.9, 5, 5])
tol = 0.4

plot_data(x, y, 1, 1, tol, plot_fit_line=False, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=False, fit_start_end_color='green')
plot_data(x, y, 1, 2, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=False, fit_start_end_color='green')
plot_data(x, y, 1, 3, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=False, fit_start_end_color='green')
plot_data(x, y, 1, 4, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=False, fit_start_end_color='green')
plot_data(x, y, 1, 5, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=False, fit_start_end_color='green')
plot_data(x, y, 1, 6, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=False, fit_start_end_color='green')
plot_data(x, y, 1, 7, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=False, fit_start_end_color='red'  )
plot_data(x, y, 7, 8, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=True,  fit_start_end_color='green')
plot_data(x, y, 7, 9, tol, plot_fit_line=True, plot_fitted_points=True, plot_first_last_fitted_points=True, plot_segments_1=True, fit_start_end_color='green')
plot_data(x, y, 7, 9, tol, plot_fit_line=False, plot_fitted_points=False, plot_first_last_fitted_points=False, plot_segments_1=True, fit_start_end_color='green', plot_segments_2=True)