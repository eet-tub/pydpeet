import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from pydpeet.process.sequence.utils.console_prints.log_time import log_time

# -------------------------------------------------------------------
# Screen dimensions
# -------------------------------------------------------------------
_root = tk.Tk()
_root.withdraw()
_root.update_idletasks()
_SCREEN_DIMS = (_root.winfo_screenwidth(), _root.winfo_screenheight())
try:
    _root.destroy()
except tk.TclError:
    pass

# -------------------------------------------------------------------
# Configurable Display Settings
# -------------------------------------------------------------------
DEFAULT_Y_LABEL_FONT_SIZE = 40
DEFAULT_TICK_LABEL_FONT_SIZE = 40
DEFAULT_TEXT_LABEL_FONT_SIZE = 40
DEFAULT_LEGEND_FONT_SIZE = 40
DEFAULT_X_LABEL_FONT_SIZE = 40
DEFAULT_LINE_WIDTH = 3.0
DEFAULT_SEGMENT_LINE_WIDTH = 2.0
DEFAULT_SHOW_PHASES = True
SHOW_GRID = False
NUM_Y_TICKS = 9
Y_TICK_DECIMALS = 2  # New variable to set the maximum number of decimal places for y-ticks
segment_Line_alpha = 0.3

# -------------------------------------------------------------------
# Core Visualization Function
# -------------------------------------------------------------------
def _visualize_phases(
    dataframe: pd.DataFrame,
    start_time: float = 0.0,
    end_time: float = 1e50,
    segment_id_cols: list[str] = None,
    segment_colors: (dict[str, str] | list[str]) = None,
    segment_alpha: float = 0.3,
    columns_to_visualize: list[str] = ['Voltage[V]', 'Current[A]', 'Power[W]'],
    line_colors: dict[str, str] = None,
    y_axis_ranges: dict[str, tuple[float, float]] = None,
    use_lines_for_segments: bool = True,
    show_column_names: bool = True,
    show_time: bool = True,
    show_id: bool = True,
    width_height_ratio: list[float, float] = [1.0, 0.3],
    show_runtime: bool = True,
    show_grid: bool = SHOW_GRID,
    y_label_font_size: int = DEFAULT_Y_LABEL_FONT_SIZE,
    tick_label_font_size: int = DEFAULT_TICK_LABEL_FONT_SIZE,
    text_label_font_size: int = DEFAULT_TEXT_LABEL_FONT_SIZE,
    legend_font_size: int = DEFAULT_LEGEND_FONT_SIZE,
    x_label_font_size: int = DEFAULT_X_LABEL_FONT_SIZE,
    line_width: float = DEFAULT_LINE_WIDTH,
    segment_line_width: float = DEFAULT_SEGMENT_LINE_WIDTH,
    show_phases: bool = DEFAULT_SHOW_PHASES,
    NUM_Y_TICKS = NUM_Y_TICKS,
    Y_TICK_DECIMALS: int = Y_TICK_DECIMALS
):

    with log_time("filter by time", show_runtime):
        mask = pd.Series(True, index=dataframe.index)
        if start_time is not None:
            mask &= dataframe['Testtime[s]'] >= start_time
        if end_time is not None:
            mask &= dataframe['Testtime[s]'] <= end_time
        df = dataframe.loc[mask]

    with log_time("normalize colors and y-axis ranges", show_runtime):
        line_colors = line_colors or {}
        y_axis_ranges = y_axis_ranges or {}

    with log_time("map segment colors", show_runtime):
        segment_colors = {var: col for var, col in zip(segment_id_cols, segment_colors)}

    with log_time("set up figure", show_runtime):
        screen_w, screen_h = _SCREEN_DIMS
        dpi = plt.rcParams['figure.dpi']
        fig_w, fig_h = (screen_w * width_height_ratio[0]) / dpi, (screen_h * width_height_ratio[1]) / dpi

        plt.ioff()
        fig, ax_base = plt.subplots(figsize=(fig_w, fig_h))
        axes = {}

        # ax_base.plot([10400, 10800], [-0.0019, -0.0019], color='r', linestyle='--', label='Beispielhafter Schwellenwert', linewidth=2.0)

        offset = 0.07
        from matplotlib.ticker import MaxNLocator, FuncFormatter

        def pixel_to_axis_coords(fig, ax, pixels, side='left'):
            fig_w_px = fig.get_size_inches()[0] * fig.dpi
            bbox = ax.get_position()
            ax_w_frac = bbox.width
            axis_offset = pixels / fig_w_px / ax_w_frac
            return -axis_offset if side == 'left' else 1 + axis_offset

        offset_pixels_left = 150
        offset_pixels_right = 200

        for idx, col in enumerate(columns_to_visualize):
            if idx == 0:
                ax = ax_base
                ax.yaxis.set_label_position('left')
                ax.yaxis.set_ticks_position('left')
                ax.yaxis.set_major_locator(MaxNLocator(prune='both'))
                ax.set_ylabel(col, color=line_colors.get(col), fontsize=y_label_font_size)
                x_pos = pixel_to_axis_coords(fig, ax, offset_pixels_left, side='left')
                ax.yaxis.set_label_coords(x_pos, 0.5)
            else:
                ax = ax_base.twinx()
                ax.yaxis.set_label_position('right')
                ax.yaxis.set_ticks_position('right')
                ax.yaxis.set_major_locator(MaxNLocator(prune='both'))
                ax.set_ylabel(col, color=line_colors.get(col), fontsize=y_label_font_size)
                x_pos = pixel_to_axis_coords(fig, ax, offset_pixels_right, side='right')
                ax.yaxis.set_label_coords(x_pos, 0.5)

            ax.set_ylabel(col, color=line_colors.get(col), fontsize=y_label_font_size)
            ax.tick_params(axis='y', labelcolor=line_colors.get(col), labelsize=tick_label_font_size)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.{Y_TICK_DECIMALS}f}'))

            if col in y_axis_ranges:
                ax.set_ylim(*y_axis_ranges[col])
            axes[col] = ax
            fig.subplots_adjust(right=1 + offset + 0.05)

    from matplotlib.ticker import LinearLocator

    for ax in axes.values():
        ax.yaxis.set_major_locator(LinearLocator(NUM_Y_TICKS))

    with log_time("plot data", show_runtime):
        t = df['Testtime[s]']
        for col in columns_to_visualize:
            if col in df.columns:
                axes[col].plot(t, df[col], label=col, color=line_colors.get(col), linewidth=line_width)

    if show_phases:
        with log_time("group segments by ID + Variable", show_runtime):
            stats = (
                df.groupby(['ID', 'Variable'])['Testtime[s]']
                .agg(tmin='min', tmax='max')
                .reset_index()
            )

        y0, y1 = ax_base.get_ylim()
        height = y1 - y0

        with log_time("draw segment backgrounds and labels", show_runtime):
            intervals = []
            colors = []
            vline_positions = []
            mid_y = (y0 + y1) / 2

            for _, row in stats.iterrows():
                tmin, tmax = row['tmin'], row['tmax']
                duration = tmax - tmin
                variable = row['Variable']
                color = segment_colors.get(variable, 'gray')

                intervals.append((tmin, duration))
                colors.append(color)

                if use_lines_for_segments:
                    vline_positions.append(tmin)

            ax_base.broken_barh(intervals, (y0, height), facecolors=colors, alpha=segment_alpha)

            if use_lines_for_segments and vline_positions:
                ax_base.vlines(vline_positions, y0, y1, colors='k', alpha=segment_Line_alpha, linewidth=segment_line_width)

            for _, row in stats.iterrows():
                tmin, tmax = row['tmin'], row['tmax']
                duration = tmax - tmin
                x_center = tmin + duration / 2
                variable = row['Variable']
                id = row['ID']

                label_parts = []
                if show_id:
                    label_parts.append(f"ID:{id}")
                if show_column_names:
                    label_parts.append(f"{variable}")
                if show_time:
                    label_parts.append(f"{duration:.1f}s")

                label = "  ".join(label_parts)

                ax_base.text(x_center,
                             mid_y,
                             label,
                             ha='center',
                             va='center',
                             rotation=90,
                             fontsize=text_label_font_size)

    ax_base.tick_params(axis='x', labelsize=tick_label_font_size)

    with log_time("add grid and legend", show_runtime):
        ax_base.set_xlabel('Testtime [s]', fontsize=x_label_font_size)
        handles, labels = [], []
        for ax in axes.values():
            h, l = ax.get_legend_handles_labels()
            handles += h; labels += l
        if handles:
            # power_handle, = ax_base.plot([], [], label='Power[W]', color='green', linewidth=3)
            # handles.append(power_handle)
            # labels.append('Power[W]')
            ax_base.legend(handles, labels, loc='upper right', fontsize=legend_font_size)
        if show_grid:
            ax_base.grid(linewidth=2.0)
        plt.tight_layout()


# -------------------------------------------------------------------
# External Interface Function
# -------------------------------------------------------------------
def visualize_phases(
    dataframe: pd.DataFrame,
    start_time: float = None,
    end_time: float = None,
    visualize_phases_config: list[tuple[str, str]] = [
        ("V", "blue"),
        ("I", "red"),
        ("P", "green"),
    ],
    segment_alpha: float = 0.3,
    line_visualization_config: list[tuple[str, str, tuple[float, float]]] = [
        ("Voltage[V]", "blue", (0, 10)),
        ("Current[A]", "red", (-10, 15)),
        ("Power[W]", "green", (-40, 40)),
    ],
    use_lines_for_segments: bool = True,
    show_column_names: bool = True,
    show_time: bool = True,
    show_id: bool = True,
    width_height_ratio: list[float] = [1.0, 0.3],
    show_runtime: bool = True,
    y_label_font_size: int = DEFAULT_Y_LABEL_FONT_SIZE,
    tick_label_font_size: int = DEFAULT_TICK_LABEL_FONT_SIZE,
    text_label_font_size: int = DEFAULT_TEXT_LABEL_FONT_SIZE,
    legend_font_size: int = DEFAULT_LEGEND_FONT_SIZE,
    x_label_font_size: int = DEFAULT_X_LABEL_FONT_SIZE,
    line_width: float = DEFAULT_LINE_WIDTH,
):
    if start_time is None:
        print("\033[91m Warning: start_time is None - setting it to 0.0 \033[0m")
        start_time = 0.0
    if end_time is None:
        print("\033[91m Warning: end_time is None - setting it to the biggest possible float \033[0m")
        end_time = float('inf')
    if dataframe is None:
        raise ValueError("dataframe is None")
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("dataframe must be a pandas DataFrame")
    if not (isinstance(width_height_ratio, (list, tuple)) and len(width_height_ratio) == 2):
        raise ValueError("width_height_ratio must be a list or tuple of length 2")
    if "Testtime[s]" not in dataframe.columns:
        raise ValueError("dataframe needs to have at least column 'Testtime[s]'")
    if "ID" not in dataframe.columns:
        raise ValueError("dataframe needs to have at least column 'ID'")
    if not isinstance(visualize_phases_config, list):
        raise TypeError("visualize_phases_config must be a list")
    if not isinstance(line_visualization_config, list):
        raise TypeError("line_visualization_config must be a list")
    if start_time >= end_time:
        raise ValueError(f"start_time ({start_time}) must be less than end_time ({end_time})")
    if not (0 <= segment_alpha <= 1):
        print("\033[91m Warning: segment_alpha must be between 0 and 1 - resetting it now to 0.3 \033[0m")
        segment_alpha = 0.3

    segment_id_cols = [col for col, _ in visualize_phases_config]
    segment_colors = [color for _, color in visualize_phases_config]
    columns_to_visualize = [col for col, _, _ in line_visualization_config]
    line_colors = {col: color for col, color, _ in line_visualization_config}
    y_axis_ranges = {col: y_range for col, _, y_range in line_visualization_config}

    _visualize_phases(
        dataframe=dataframe,
        start_time=start_time,
        end_time=end_time,
        segment_id_cols=segment_id_cols,
        segment_colors=segment_colors,
        segment_alpha=segment_alpha,
        columns_to_visualize=columns_to_visualize,
        line_colors=line_colors,
        y_axis_ranges=y_axis_ranges,
        use_lines_for_segments=use_lines_for_segments,
        show_column_names=show_column_names,
        show_time=show_time,
        show_id=show_id,
        width_height_ratio=width_height_ratio,
        show_runtime=show_runtime,
        y_label_font_size=y_label_font_size,
        tick_label_font_size=tick_label_font_size,
        text_label_font_size=text_label_font_size,
        legend_font_size=legend_font_size,
        x_label_font_size=x_label_font_size,
        line_width=line_width
    )