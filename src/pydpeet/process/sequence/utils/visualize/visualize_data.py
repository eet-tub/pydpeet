import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk

from pydpeet.citations import citeme
from pydpeet.process.sequence.utils.console_prints.log_time import log_time

# -------------------------------------------------------------------
# Compute screen dimensions once
# -------------------------------------------------------------------
_root = tk.Tk()
_root.withdraw()
_root.update_idletasks()
_SCREEN_DIMS = (_root.winfo_screenwidth(), _root.winfo_screenheight())
try:
    _root.destroy()
except tk.TclError:
    pass


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
    show_grid: bool = False
):
    """
    Visualizes the given dataframe by plotting all columns over time.

    Parameters:
        dataframe (pd.DataFrame): The dataframe to be visualized.
        start_time (float, optional): The start time of the visualization. Defaults to 0.0.
        end_time (float, optional): The end time of the visualization. Defaults to 1e50.
        segment_id_cols (list[str], optional): The columns of the dataframe to be used as segment IDs. Defaults to None.
        segment_colors (dict[str, str] | list[str], optional): The colors to be used for the segments. Defaults to None.
        segment_alpha (float, optional): The alpha value of the segment backgrounds. Defaults to 0.3.
        columns_to_visualize (list[str], optional): The columns of the dataframe to be visualized. Defaults to ['Voltage[V]', 'Current[A]', 'Power[W]'].
        line_colors (dict[str, str], optional): The colors to be used for the lines. Defaults to None.
        y_axis_ranges (dict[str, tuple[float, float]], optional): The ranges of the y-axis. Defaults to None.
        use_lines_for_segments (bool, optional): Whether to use lines for the segments. Defaults to True.
        show_column_names (bool, optional): Whether to show the column names. Defaults to True.
        show_time (bool, optional): Whether to show the time. Defaults to True.
        show_id (bool, optional): Whether to show the ID. Defaults to True.
        width_height_ratio (list[float, float], optional): The ratio of the width to the height of the figure. Defaults to [1.0, 0.3].
        show_runtime (bool, optional): Whether to show the runtime. Defaults to True.
        show_grid (bool, optional): Whether to show the grid. Defaults to False.

    Returns:
        None
    """
    # 1) Filter by time
    with log_time("filtering by time", show_runtime):
        mask = pd.Series(True, index=dataframe.index)
        if start_time is not None:
            mask &= dataframe['Testtime[s]'] >= start_time
        if end_time is not None:
            mask &= dataframe['Testtime[s]'] <= end_time
        df = dataframe.loc[mask]

    # 2) Normalize line colors and y-axis ranges
    with log_time("normalizing colors and y-axis ranges", show_runtime):
        line_colors = line_colors or {}
        y_axis_ranges = y_axis_ranges or {}

    # 3) Map segment colors to `Variable` values
    with log_time("mapping segment colors", show_runtime):
        segment_colors = {var: col for var, col in zip(segment_id_cols, segment_colors)}

    # 4) Set up figure
    with log_time("setting up figure", show_runtime):
        screen_w, screen_h = _SCREEN_DIMS
        dpi = plt.rcParams['figure.dpi']
        fig_w, fig_h = (screen_w * width_height_ratio[0])/ dpi, (screen_h * width_height_ratio[1]) / dpi

        plt.ioff()
        fig, ax_base = plt.subplots(figsize=(fig_w, fig_h))
        axes = {}
        offset = 0.02

        for idx, col in enumerate(columns_to_visualize):
            if idx == 0:
                ax = ax_base
            elif idx == 1:
                ax = ax_base.twinx()
            else:
                ax = ax_base.twinx()
                ax.spines["right"].set_position(("axes", 1 + offset))
                ax.spines["right"].set_visible(True)
                ax.yaxis.set_label_position('right')
                ax.yaxis.set_ticks_position('right')
                offset += 0.05

            ax.set_ylabel(col, color=line_colors.get(col))
            ax.tick_params(axis='y', labelcolor=line_colors.get(col))
            if col in y_axis_ranges:
                ax.set_ylim(*y_axis_ranges[col])
            axes[col] = ax
            fig.subplots_adjust(right=1 + offset + 0.05)

    # 5) Plot data
    with log_time("plotting data", show_runtime):
        t = df['Testtime[s]']
        for col in columns_to_visualize:
            if col in df.columns:
                axes[col].plot(t, df[col], label=col, color=line_colors.get(col))

    # 6) Group segments by ID + Variable
    with log_time("grouping segments by ID + Variable", show_runtime):
        stats = (
            df.groupby(['ID', 'Variable'])['Testtime[s]']
            .agg(tmin='min', tmax='max')
            .reset_index()
        )

    y0, y1 = ax_base.get_ylim()
    height = y1 - y0

    # 7) Draw segment backgrounds and labels
    with log_time("drawing segment backgrounds and labels", show_runtime):
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

        # Draw all backgrounds at once
        ax_base.broken_barh(intervals, (y0, height), facecolors=colors, alpha=segment_alpha)

        # Draw all vertical lines at once
        if use_lines_for_segments and vline_positions:
            ax_base.vlines(vline_positions, y0, y1, colors='k', alpha=segment_alpha)

        # Draw text labels (still per segment, this is usually okay)
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
                         size=10)


    # 8) Adding grid and legend
    with log_time("adding grid and legend", show_runtime):
        #TODO power labels multiple times shown fix?
        ax_base.set_xlabel('Testtime [s]')
        handles, labels = [], []
        for ax in axes.values():
            h, l = ax.get_legend_handles_labels()
            handles += h; labels += l
        if handles:
            ax_base.legend(handles, labels, loc='upper left')
        if show_grid:
            ax_base.grid()
        plt.tight_layout()


def visualize_phases(
    dataframe: pd.DataFrame,
    start_time: float = None,
    end_time: float = None,
    visualize_phases_config: list(tuple[str, str]) = [
        ("V", "blue"),
        ("I", "red"),
        ("P", "green"),
    ],
    segment_alpha: float = 0.3,
    line_visualization_config: list(tuple[str, str, tuple[float, float]]) = [
        ("Voltage[V]", "blue", (2.3, 4.3)),
        ("Current[A]", "red", (-10, 10)),
        #("Power[W]", "green", (-40, 40)),
    ],
    use_lines_for_segments: bool = True,
    show_column_names: bool = True,
    show_time: bool = True,
    show_id: bool = True,
    width_height_ratio: float = [1.0, 0.3],
    show_runtime: bool = True
):
    if start_time is None:
        print("\033[94m    Input Warning: start_time is None - setting it to 0.0 \033[0m")
        start_time = 0.0
    if end_time is None:
        print("\033[94m    Input Warning: end_time is None - setting it to the biggest possible float \033[0m")
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

    if start_time is None:
        start_time = dataframe['Testtime[s]'].min()
    if end_time is None:
        end_time = dataframe['Testtime[s]'].max()

    segment_id_cols = [col for col, _ in visualize_phases_config]
    segment_colors = [color for _, color in visualize_phases_config]
    columns_to_visualize = [col for col, _, _ in line_visualization_config]
    line_colors = {col: color for col, color, _ in line_visualization_config}
    y_axis_ranges = {col: y_range for col, _, y_range in line_visualization_config}

    if not isinstance(segment_id_cols, list):
        raise TypeError("segment_id_cols must be a list of strings")
    if not isinstance(segment_colors, (list, dict)):
        raise TypeError("segment_colors must be a list or dict")
    if isinstance(segment_colors, list) and len(segment_id_cols) != len(segment_colors):
        raise ValueError("segment_id_cols and segment_colors must have the same length")
    if not isinstance(columns_to_visualize, list):
        raise TypeError("columns_to_visualize must be a list")

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
        show_runtime=show_runtime
    )