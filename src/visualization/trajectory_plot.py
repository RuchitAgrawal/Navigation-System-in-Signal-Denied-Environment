"""
trajectory_plot.py — Trajectory visualization utilities.

Generates:
1. Top-down (X-Z plane) trajectory comparison (estimated vs. ground truth).
2. Per-frame ATE error bar plot.
3. 3D trajectory plot.

All figures are saved to the results/figures/ directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless/script use
import matplotlib.pyplot as plt
import numpy as np

from src.evaluation.ate import ATEResult


COLORS = {
    "gt": "#6c757d",       # grey for ground truth
    "est": "#0d6efd",      # blue for estimated
    "aligned": "#198754",  # green for aligned estimated
    "error": "#dc3545",    # red for error
}


def plot_trajectory_2d(
    ate_result: ATEResult,
    est_positions_raw: np.ndarray,
    config_id: str,
    dataset_name: str,
    sequence_name: str,
    save_path: str | Path,
    show: bool = False,
) -> None:
    """Plot top-down trajectory comparison (X-Z plane).

    Parameters
    ----------
    ate_result         : ATEResult from compute_ate().
    est_positions_raw  : (N, 3) unaligned estimated positions for reference.
    config_id          : Feature config label (e.g., 'orb_orb').
    dataset_name       : e.g., 'icl_nuim'.
    sequence_name      : e.g., 'living_room_traj1_loop'.
    save_path          : Output file path (.png or .pdf).
    show               : If True, call plt.show() (disable in scripts).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f"Trajectory Comparison — {config_id.upper()} | {dataset_name} / {sequence_name}",
        fontsize=13, fontweight="bold",
    )

    gt  = ate_result.gt_positions
    est = ate_result.aligned_est_positions

    for ax, (x_idx, z_idx, xlabel, ylabel) in zip(
        axes,
        [(0, 2, "X (m)", "Z (m)"), (0, 1, "X (m)", "Y (m)")],
    ):
        ax.plot(gt[:, x_idx], gt[:, z_idx],
                color=COLORS["gt"], linewidth=1.5, label="Ground Truth", zorder=3)
        ax.plot(est[:, x_idx], est[:, z_idx],
                color=COLORS["aligned"], linewidth=1.2, linestyle="--",
                label=f"Estimated ({ate_result.alignment.upper()} aligned)", zorder=2)
        ax.scatter(gt[0, x_idx], gt[0, z_idx],
                   color="black", s=60, zorder=5, label="Start")
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.35)
        ax.set_aspect("equal", adjustable="box")

    # Annotation box
    stats_txt = (
        f"ATE RMSE: {ate_result.rmse:.4f} m\n"
        f"ATE mean: {ate_result.mean:.4f} m\n"
        f"Scale:    {ate_result.scale:.4f}\n"
        f"N frames: {ate_result.n_frames}"
    )
    axes[0].text(
        0.02, 0.98, stats_txt,
        transform=axes[0].transAxes,
        fontsize=8, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_ate_over_time(
    ate_result: ATEResult,
    config_id: str,
    save_path: str | Path,
    show: bool = False,
) -> None:
    """Plot per-frame ATE error over frame index."""
    fig, ax = plt.subplots(figsize=(10, 4))
    frames = np.arange(len(ate_result.per_frame_errors))
    ax.fill_between(frames, ate_result.per_frame_errors, alpha=0.35,
                    color=COLORS["error"])
    ax.plot(frames, ate_result.per_frame_errors,
            color=COLORS["error"], linewidth=1.0)
    ax.axhline(ate_result.rmse, color="black", linestyle="--",
               linewidth=1.0, label=f"RMSE = {ate_result.rmse:.4f} m")
    ax.set_xlabel("Frame Index", fontsize=11)
    ax.set_ylabel("Translation Error (m)", fontsize=11)
    ax.set_title(f"ATE over Time — {config_id.upper()} "
                 f"({ate_result.alignment.upper()} aligned)", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.35)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_benchmark_comparison(
    summary_rows: list,
    dataset_name: str,
    save_path: str | Path,
    show: bool = False,
) -> None:
    """Bar chart comparing ATE RMSE, FPS, and tracking success across configs."""
    import pandas as pd
    df = pd.DataFrame(summary_rows)
    df = df[df["dataset"] == dataset_name].reset_index(drop=True)
    if df.empty:
        return

    configs = df["config_id"].tolist()
    x = np.arange(len(configs))
    width = 0.25

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"Benchmark Comparison — {dataset_name}", fontsize=13, fontweight="bold")

    # ATE RMSE
    axes[0].bar(x, df["ate_rmse_m"], width=0.5, color=COLORS["error"], alpha=0.8)
    axes[0].set_xticks(x); axes[0].set_xticklabels(configs, rotation=20, ha="right")
    axes[0].set_ylabel("ATE RMSE (m)"); axes[0].set_title("ATE RMSE")
    axes[0].grid(axis="y", alpha=0.4)

    # Mean FPS
    axes[1].bar(x, df["mean_fps"], width=0.5, color=COLORS["aligned"], alpha=0.8)
    axes[1].set_xticks(x); axes[1].set_xticklabels(configs, rotation=20, ha="right")
    axes[1].set_ylabel("Mean FPS"); axes[1].set_title("Runtime (Mean FPS)")
    axes[1].grid(axis="y", alpha=0.4)

    # Tracking success %
    axes[2].bar(x, df["tracking_success_pct"], width=0.5,
                color=COLORS["est"], alpha=0.8)
    axes[2].set_xticks(x); axes[2].set_xticklabels(configs, rotation=20, ha="right")
    axes[2].set_ylabel("Success (%)"); axes[2].set_title("Tracking Success Rate")
    axes[2].set_ylim(0, 105)
    axes[2].grid(axis="y", alpha=0.4)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
