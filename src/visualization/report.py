"""
report.py — Console and file summary report utilities.

Formats experiment results as readable tables for terminal output
and exports them as Markdown summary files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


def _fmt(val: Any, decimals: int = 4) -> str:
    """Format a value for display."""
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:.{decimals}f}"
    if isinstance(val, bool):
        return "Yes" if val else "No"
    return str(val)


def print_summary_table(rows: List[Dict[str, Any]]) -> None:
    """Print a formatted benchmark summary table to stdout."""
    if not rows:
        print("No results to display.")
        return

    # Column widths
    cols = [
        ("config_id",              18),
        ("dataset",                12),
        ("ate_rmse_m",             12),
        ("rpe_trans_rmse_m",       18),
        ("rpe_rot_rmse_deg",       18),
        ("tracking_success_pct",   18),
        ("mean_fps",               10),
    ]

    header = "  ".join(f"{name:<{w}}" for name, w in cols)
    sep    = "  ".join("-" * w for _, w in cols)
    print("\n" + sep)
    print(header)
    print(sep)

    for row in rows:
        line = "  ".join(
            f"{_fmt(row.get(name, 'N/A')):<{w}}"
            for name, w in cols
        )
        print(line)

    print(sep + "\n")


def save_markdown_summary(
    rows: List[Dict[str, Any]],
    path: str | Path,
    title: str = "Benchmark Results",
) -> None:
    """Save a Markdown table of all summary rows with executive and detailed breakdowns."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        if not rows:
            f.write("*No results.*\n")
            return

        # 1. Executive Summary Table
        f.write("## 1. Executive Summary\n\n")
        exec_cols = [
            ("config_id", "Configuration"),
            ("descriptor_label", "Descriptor"),
            ("dataset", "Dataset"),
            ("sequence", "Sequence"),
            ("ate_rmse_m", "ATE RMSE (m)"),
            ("rpe_trans_rmse_m", "RPE Trans (m)"),
            ("rpe_rot_rmse_deg", "RPE Rot (deg)"),
            ("tracking_success_pct", "Tracking %"),
            ("mean_fps", "FPS"),
        ]
        f.write("| " + " | ".join(label for _, label in exec_cols) + " |\n")
        f.write("|" + "|".join(["---"] * len(exec_cols)) + "|\n")
        for r in rows:
            line = "| " + " | ".join(_fmt(r.get(key, "N/A")) for key, _ in exec_cols) + " |"
            f.write(line + "\n")
        f.write("\n")

        # 2. Timing and Computational Efficiency Breakdown
        f.write("## 2. Computational Latency and Throughput\n\n")
        timing_cols = [
            ("config_id", "Configuration"),
            ("sequence", "Sequence"),
            ("mean_frame_time_ms", "Mean Latency (ms)"),
            ("median_frame_time_ms", "Median Latency (ms)"),
            ("p95_frame_time_ms", "P95 Latency (ms)"),
            ("mean_fps", "Mean FPS"),
            ("total_frames", "Total Frames"),
            ("failed_frames", "Dropped Frames"),
        ]
        f.write("| " + " | ".join(label for _, label in timing_cols) + " |\n")
        f.write("|" + "|".join(["---"] * len(timing_cols)) + "|\n")
        for r in rows:
            line = "| " + " | ".join(_fmt(r.get(key, "N/A")) for key, _ in timing_cols) + " |"
            f.write(line + "\n")
        f.write("\n")

        # 3. Complete Raw Data
        f.write("## 3. Complete Benchmark Raw Data\n\n")
        keys = list(rows[0].keys())
        f.write("| " + " | ".join(keys) + " |\n")
        f.write("|" + "|".join(["---"] * len(keys)) + "|\n")

        for row in rows:
            vals = [_fmt(row.get(k)) for k in keys]
            f.write("| " + " | ".join(vals) + " |\n")

        f.write(f"\n*Generated automatically. ATE uses Sim(3) alignment unless noted.*\n")
