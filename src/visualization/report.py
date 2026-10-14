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
    """Save a Markdown table of all summary rows."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        f.write(f"# {title}\n\n")
        if not rows:
            f.write("*No results.*\n")
            return

        # Header
        keys = list(rows[0].keys())
        f.write("| " + " | ".join(keys) + " |\n")
        f.write("|" + "|".join(["---"] * len(keys)) + "|\n")

        # Rows
        for row in rows:
            vals = [_fmt(row.get(k)) for k in keys]
            f.write("| " + " | ".join(vals) + " |\n")

        f.write(f"\n*Generated automatically. ATE uses Sim(3) alignment unless noted.*\n")
