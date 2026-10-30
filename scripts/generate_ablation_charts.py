#!/usr/bin/env python
"""
generate_ablation_charts.py — Publication-ready ablation analysis charts.

Parses benchmark_summary.csv to generate comparative bar charts and figures:
1. ATE RMSE comparison across configurations and environments (Indoor vs Outdoor).
2. Tracking stability and success rates under low-texture / high-rotation stress.
3. Computational throughput (FPS) and latency distributions.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_benchmark_data(csv_path: str | Path) -> pd.DataFrame:
    """Load benchmark summary CSV file and sanitize fields."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Benchmark summary file not found: {csv_path}")
    df = pd.read_csv(csv_path)
    # Ensure numeric columns are properly typed
    numeric_cols = [
        "ate_rmse_m", "ate_mean_m", "ate_median_m",
        "rpe_trans_rmse_m", "rpe_rot_rmse_deg",
        "tracking_success_pct", "mean_frame_time_ms",
        "median_frame_time_ms", "p95_frame_time_ms",
        "mean_fps", "median_fps",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def plot_ate_comparison(
    df: pd.DataFrame,
    save_path: str | Path,
    title: str = "Trajectory Estimation Error (ATE RMSE) Across Environments",
) -> Path:
    """Generate grouped bar chart comparing ATE RMSE across configurations and sequences."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    configs = df["config_id"].unique()
    sequences = df["sequence"].unique()

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    x = np.arange(len(configs))
    n_seq = len(sequences)
    bar_width = 0.8 / max(n_seq, 1)

    colors = ["#2b5c8f", "#4682b4", "#e06666", "#cc0000", "#6aa84f"]

    for i, seq in enumerate(sequences):
        seq_df = df[df["sequence"] == seq]
        values = []
        for cfg in configs:
            val = seq_df[seq_df["config_id"] == cfg]["ate_rmse_m"].values
            values.append(val[0] if len(val) > 0 and not np.isnan(val[0]) else 0.0)

        offset = (i - n_seq / 2 + 0.5) * bar_width
        ax.bar(
            x + offset,
            values,
            width=bar_width,
            label=seq.replace("_Easy_P000", "").replace("_loop", ""),
            color=colors[i % len(colors)],
            edgecolor="black",
            linewidth=0.5,
        )

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("ATE RMSE [m] (lower is better)", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=9, rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(title="Sequence", fontsize=8, loc="upper right")
    fig.tight_layout()

    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def plot_tracking_stability(
    df: pd.DataFrame,
    save_path: str | Path,
    title: str = "Tracking Stability (%) Across Configurations & Environments",
) -> Path:
    """Generate bar chart comparing tracking success percentages."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    configs = df["config_id"].unique()
    sequences = df["sequence"].unique()

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    x = np.arange(len(configs))
    n_seq = len(sequences)
    bar_width = 0.8 / max(n_seq, 1)

    palette = ["#1f77b4", "#aec7e8", "#ff7f0e", "#d62728"]

    for i, seq in enumerate(sequences):
        seq_df = df[df["sequence"] == seq]
        rates = []
        for cfg in configs:
            val = seq_df[seq_df["config_id"] == cfg]["tracking_success_pct"].values
            rates.append(val[0] if len(val) > 0 and not np.isnan(val[0]) else 0.0)

        offset = (i - n_seq / 2 + 0.5) * bar_width
        ax.bar(
            x + offset,
            rates,
            width=bar_width,
            label=seq.replace("_Easy_P000", "").replace("_loop", ""),
            color=palette[i % len(palette)],
            edgecolor="black",
            linewidth=0.5,
        )

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Tracking Success Rate [%] (higher is better)", fontsize=10)
    ax.set_ylim([0, 105])
    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=9, rotation=15)
    ax.axhline(100.0, color="gray", linestyle=":", linewidth=0.8)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(title="Sequence", fontsize=8, loc="center right")
    fig.tight_layout()

    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def plot_latency_throughput(
    df: pd.DataFrame,
    save_path: str | Path,
    title: str = "Computational Efficiency: Processing Speed (FPS) Across Configurations",
) -> Path:
    """Generate bar chart comparing mean processing throughput (FPS)."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Average FPS across indoor sequences where tracking succeeded
    indoor_df = df[df["dataset"] == "icl_nuim"]
    avg_fps = indoor_df.groupby("config_id")["mean_fps"].mean().reset_index()
    avg_latency = indoor_df.groupby("config_id")["mean_frame_time_ms"].mean().reset_index()

    merged = pd.merge(avg_fps, avg_latency, on="config_id")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # Subplot 1: FPS
    bars1 = ax1.bar(
        merged["config_id"],
        merged["mean_fps"],
        color="#2ca02c",
        edgecolor="black",
        linewidth=0.7,
        alpha=0.85,
    )
    ax1.set_title("Processing Throughput (Indoor)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Mean FPS (Frames per Second)", fontsize=10)
    ax1.set_xticks(range(len(merged)))
    ax1.set_xticklabels(merged["config_id"], fontsize=9, rotation=20)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    ax1.axhline(30.0, color="red", linestyle="--", linewidth=1.0, label="Real-time (30 FPS)")
    ax1.legend(fontsize=8)

    for bar in bars1:
        yval = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.5,
            f"{yval:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # Subplot 2: Latency (ms)
    bars2 = ax2.bar(
        merged["config_id"],
        merged["mean_frame_time_ms"],
        color="#1f77b4",
        edgecolor="black",
        linewidth=0.7,
        alpha=0.85,
    )
    ax2.set_title("Mean Per-Frame Latency (Indoor)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Latency [ms] (lower is better)", fontsize=10)
    ax2.set_xticks(range(len(merged)))
    ax2.set_xticklabels(merged["config_id"], fontsize=9, rotation=20)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)
    ax2.axhline(33.3, color="red", linestyle="--", linewidth=1.0, label="33.3 ms (30 Hz Budget)")
    ax2.legend(fontsize=8)

    for bar in bars2:
        yval = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 1.0,
            f"{yval:.1f}ms",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def generate_all_ablation_charts(
    csv_path: str | Path = "results/csv/benchmark_summary.csv",
    output_dir: str | Path = "results/figures",
) -> Dict[str, Path]:
    """Generate all ablation charts and return paths to saved figures."""
    df = load_benchmark_data(csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated = {}
    p1 = plot_ate_comparison(df, output_dir / "ablation_ate_comparison.png")
    generated["ate_comparison"] = p1

    p2 = plot_tracking_stability(df, output_dir / "ablation_tracking_stability.png")
    generated["tracking_stability"] = p2

    p3 = plot_latency_throughput(df, output_dir / "ablation_latency_throughput.png")
    generated["latency_throughput"] = p3

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate publication-ready ablation charts")
    parser.add_argument("--csv", default="results/csv/benchmark_summary.csv", help="Path to benchmark CSV")
    parser.add_argument("--out-dir", default="results/figures", help="Directory to save figures")
    args = parser.parse_args()

    print(f"Loading benchmark results from: {args.csv}")
    results = generate_all_ablation_charts(args.csv, args.out_dir)
    print("Generated ablation charts:")
    for key, path in results.items():
        print(f"  [{key}] -> {path}")


if __name__ == "__main__":
    main()
