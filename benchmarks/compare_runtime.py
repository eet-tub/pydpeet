"""Compare two JUnit XML runtime reports (baseline vs current) and emit a markdown table + plots.

Baseline is a report produced from a reference git ref (typically origin/main); current is a
report produced from the working tree. Per-test runtimes are compared and a regression is
flagged when the current time is slower than ``--threshold`` percent (default 25) relative
to the baseline.

This differs from ``scripts/compare_benchmarks.py`` (which compares pytest-benchmark *JSON*
reports) by working directly on the ``--junitxml`` output the local benchmark helper produces.

* Tables are written to stdout.
* Optionally a bar chart comparing every matched benchmark is saved as PNG (use
  ``--plot-benchmarks`` to restrict which are drawn). In addition to the overall chart,
  one plot per test file (e.g. ``..._test_add_capacity.py.png``) is written into the
  same directory.
* ``--refined`` accepts a JSON override of per-test timings (used after outlier reruns);
  this file may carry a UTF-8 BOM (PowerShell 5.1 ``Set-Content -Encoding utf8``) and is
  read with ``utf-8-sig`` accordingly.

Stdlib + matplotlib only.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def load_report(path: Path) -> dict[str, float]:
    """Return {test fullname: runtime in seconds} from a JUnit XML report."""
    tree = ET.parse(path)
    root = tree.getroot()
    suite = root.find("testsuite") if root.tag == "testsuites" else root

    result: dict[str, float] = {}
    for case in suite.findall("testcase"):
        if case.find("skipped") is not None:
            continue
        time = case.get("time")
        if time is None:
            continue
        classname = case.get("classname", "")
        name = case.get("name", "")
        fullname = f"{classname}::{name}" if classname else name
        result[fullname] = float(time)
    return result


def make_filter_matcher(expr: str):
    """Compile a pytest ``-k``-style filter expression into a matcher callable.

    Supported subset: whitespace-separated words are AND-ed together, ``or`` joins
    alternatives and ``not`` negates (binding tighter than ``and``). Matching is
    case-insensitive substring matching, like pytest's ``-k``.
    """
    tokens = re.findall(r"\bnot\b|\bor\b|\b\S+\b", expr.strip() or " ")
    if not tokens:
        return lambda text: True

    # Build a small expression tree with precedence: not > and > or
    i = 0

    def parse_or():
        nonlocal i
        node = parse_and()
        while i < len(tokens) and tokens[i] == "or":
            i += 1
            rhs = parse_and()
            node = ("or", node, rhs)
        return node

    def parse_and():
        nonlocal i
        node = parse_not()
        while i < len(tokens) and tokens[i] in ("and", "not"):
            if tokens[i] == "and":
                i += 1
            rhs = parse_not()
            node = ("and", node, rhs)
        return node

    def parse_not():
        nonlocal i
        if i < len(tokens) and tokens[i] == "not":
            i += 1
            node = parse_not()
            return ("not", node)
        token = tokens[i]
        i += 1
        return ("word", token.lower())

    tree = parse_or()

    def evaluate(node, text):
        kind = node[0]
        if kind == "word":
            return node[1] in text.lower()
        if kind == "not":
            return not evaluate(node[1], text)
        if kind == "and":
            return evaluate(node[1], text) and evaluate(node[2], text)
        if kind == "or":
            return evaluate(node[1], text) or evaluate(node[2], text)
        return True

    return lambda text: evaluate(tree, text)


def format_time(value: float) -> str:
    for factor, label in ((1e-6, "us"), (1e-3, "ms")):
        if abs(value) < factor * 1000:
            return f"{value / factor:>9.2f} {label}"
    return f"{value:>8.3f} s"


def plot_comparison(
    names: list[str],
    baseline_times: list[float],
    current_times: list[float],
    pct: list[float | None],
    out_path: Path,
    title: str,
) -> None:
    """Render a grouped horizontal bar chart for every benchmark in the filtered set."""
    fig, ax = plt.subplots(figsize=(max(10, len(names) * 0.35), max(4, len(names) * 0.22)))
    y = list(range(len(names)))[::-1]
    height = 0.35

    ax.barh([v + height / 2 for v in y], baseline_times, height=height, label="baseline", color="#4C72B0")
    ax.barh([v - height / 2 for v in y], current_times, height=height, label="current", color="#DD8452")

    for i, v in enumerate(y):
        p = pct[i]
        if p is None:
            continue
        ax.text(
            max(baseline_times[i], current_times[i]) * 1.02,
            v,
            f"{p:+.1f}%",
            va="center",
            ha="left",
            fontsize=8,
            color="#C44E52" if p > 0 else "#55A868",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("Runtime (seconds)", fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def short_label(path: Path) -> str:
    return path.name.replace(".xml", "").replace("report_", "")


def to_short_name(fullname: str) -> str:
    """Convert a JUnit fullname to 'test_function_parameter_testcase'.

    Input:  'test.api_accessible.test_add_capacity.Test_add_capacity_df::test_valid'
    Output: 'test_add_capacity_df_valid'

    The class name (Test_<function>_<parameter>) and method (test_<testcase>) are
    recombined into a single descriptive label.
    """
    if "::" not in fullname:
        return fullname
    cname, method = fullname.split("::")
    class_ = cname.rsplit(".", 1)[-1]
    code = class_[len("Test_") :] if class_.startswith("Test_") else class_
    case = method[len("test_") :] if method.startswith("test_") else method
    return f"test_{code}_{case}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("baseline", type=Path, help="JUnit XML report from the baseline run")
    parser.add_argument("current", type=Path, help="JUnit XML report from the current run")
    parser.add_argument(
        "--baseline-label",
        default="",
        help="Human-readable description of the baseline (e.g. git branch@hash) shown in the header.",
    )
    parser.add_argument(
        "--current-label",
        default="",
        help="Human-readable description of the current (e.g. git branch@hash) shown in the header.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=25.0,
        help="Relative slowdown in percent above which a regression is flagged (default: 25)",
    )
    parser.add_argument(
        "--filter",
        default="",
        help="Limit comparison to tests matching a pytest -k style expression (whitespace = AND, "
        "'or', 'not'). Applied to both reports. Empty = all tests.",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=None,
        help="Limit comparison to tests whose module filename matches exactly (e.g. 'test_write.py'). "
        "Repeatable; an exact file match is immune to substring collisions like test_write vs "
        "test_write_to_bibtex.",
    )
    parser.add_argument(
        "--plot-benchmarks",
        default="",
        help="Comma-separated substrings (matched case-insensitively against full test names). "
        "Only these tests are drawn on the plots. Empty = all matched tests are plotted.",
    )
    parser.add_argument(
        "--plots",
        nargs="?",
        const=".",
        default=None,
        help="Directory to write comparison plots into. When given without a value, plots are "
        "written to the current directory. Use the flag alone to plot; omit it to disable "
        "plotting. Plots are named '<dir>/runtime_comparison_<n>.png'.",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Optional path to write the comparison data as JSON (for reuse by other tools). "
        "Includes an 'outliers' list of test fullnames whose delta exceeds --threshold.",
    )
    parser.add_argument(
        "--refined",
        type=Path,
        default=None,
        help="Optional JSON mapping test fullname -> {'baseline': seconds, 'current': seconds}. "
        "When provided, these timings override the raw report values for those tests (used after "
        "the tests were re-run to confirm/refute outliers).",
    )
    args = parser.parse_args()

    baseline = load_report(args.baseline)
    current = load_report(args.current)

    refined: dict[str, tuple[float, float]] = {}
    if args.refined is not None and args.refined.exists():
        with args.refined.open(encoding="utf-8-sig") as fh:
            data = json.load(fh)
        for fullname, pair in data.items():
            refined[fullname] = (float(pair["baseline"]), float(pair["current"]))

    def module_filename(name: str) -> str | None:
        if "::" not in name:
            return None
        module = name.split("::")[0].rsplit(".", 1)[0]
        return module.rsplit(".", 1)[-1] + ".py"

    matcher = make_filter_matcher(args.filter) if args.filter else (lambda text: True)
    plot_tests: list[str] | None = (
        [s.strip().lower() for s in args.plot_benchmarks.split(",") if s.strip()] if args.plot_benchmarks else None
    )

    def matches_display(name: str) -> bool:
        if args.file and module_filename(name) not in args.file:
            return False
        return matcher(to_short_name(name))

    common = sorted(n for n in set(baseline) & set(current) if matches_display(n))
    only_current = sorted(n for n in set(current) - set(baseline) if matches_display(n))
    only_baseline = sorted(n for n in set(baseline) - set(current) if matches_display(n))

    rows: list[tuple[float, str]] = []
    regressions: list[str] = []
    improvements: list[str] = []
    pct_map: dict[str, float | None] = {}
    for name in common:
        b, c = refined.get(name, (baseline[name], current[name]))
        pct = (c - b) / b * 100.0 if b > 0 else float("nan")
        pct_map[name] = pct if not math.isnan(pct) else None
        refined_suffix = " (rerun)" if name in refined else ""

        if not math.isnan(pct) and pct > args.threshold:
            cat = "regression" + refined_suffix
            regressions.append(name)
        elif not math.isnan(pct) and pct < -args.threshold:
            cat = "faster" + refined_suffix
            improvements.append(name)
        else:
            cat = refined_suffix.strip()

        pct_str = "n/a" if math.isnan(pct) else f"{pct:+.2f}%"
        name_short = to_short_name(name)
        rows.append(
            (
                pct if not math.isnan(pct) else 0.0,
                f"| {name_short} | {format_time(b)} | {format_time(c)} | {pct_str} | {cat} |",
            )
        )

    rows.sort(key=lambda item: -item[0])

    lines: list[str] = []
    baseline_label = args.baseline_label or args.baseline.name
    current_label = args.current_label or args.current.name
    lines.append(f"runtime comparison: {baseline_label} vs {current_label}")
    if args.filter:
        lines.append(f"filter: {args.filter}")
    lines.append(f"compared: {len(common)} tests")
    if only_current:
        lines.append(f"new (no baseline): {len(only_current)}")
    if only_baseline:
        lines.append(f"removed: {len(only_baseline)}")

    if regressions:
        lines.append(
            f"regressions (>{args.threshold:.0f}%): {len(regressions)} "
            + ", ".join(to_short_name(n) for n in regressions)
        )
    if improvements:
        lines.append(
            f"faster (<-{args.threshold:.0f}%): {len(improvements)} "
            + ", ".join(to_short_name(n) for n in improvements)
        )
    if not regressions and not improvements:
        lines.append(f"no regression beyond +{args.threshold:.0f}%")
    lines.append("")

    # --- Plotting ---
    if args.plots is not None:
        plot_dir = Path(args.plots if args.plots else ".")
        plot_dir.mkdir(parents=True, exist_ok=True)

        to_plot = [n for n in common if plot_tests is None or any(t in to_short_name(n).lower() for t in plot_tests)]
        if not to_plot:
            lines.append("no tests matched the plot filter")
            lines.append("")
        else:

            def _plot(names: list[str], out_path: Path, title: str) -> None:
                labels = [to_short_name(n) for n in names]
                b_times = [refined.get(n, (baseline[n], current[n]))[0] for n in names]
                c_times = [refined.get(n, (baseline[n], current[n]))[1] for n in names]
                pcts = [pct_map.get(n) for n in names]
                plot_comparison(labels, b_times, c_times, pcts, out_path, title)

            base_name = f"runtime_comparison_{short_label(args.baseline)}_{short_label(args.current)}"
            _plot(
                to_plot,
                plot_dir / f"{base_name}.png",
                f"Runtime comparison ({baseline_label} vs {current_label})",
            )
            lines.append(f"plot: {plot_dir / f'{base_name}.png'}")

            # One plot per test file (grouped by the module filename, e.g. test_add_capacity.py).
            by_file: dict[str, list[str]] = {}
            for n in to_plot:
                module = n.split("::")[0].rsplit(".", 1)[0] if "::" in n else n
                file_key = module.split(".")[-1] + ".py"
                by_file.setdefault(file_key, []).append(n)
            for file_key, names in sorted(by_file.items()):
                per_out = plot_dir / f"{base_name}_{file_key}.png"
                _plot(
                    names,
                    per_out,
                    f"{file_key} — runtime comparison ({baseline_label} vs {current_label})",
                )
            lines.append(f"per-file plots: {len(by_file)} -> {plot_dir}")
            lines.append("")

    if args.out_json is not None:
        payload = {
            "baseline": str(args.baseline),
            "current": str(args.current),
            "threshold": args.threshold,
            "filter": args.filter,
            "outliers": sorted(set(regressions) | set(improvements)),
            "results": [],
        }
        for _, row in rows:
            payload["results"].append(row)
        args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
