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
    out_path = Path(save_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=150, bbox_inches="tight")
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
    out_path = Path(save_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_trajectory_3d(
    ate_result: ATEResult,
    config_id: str,
    dataset_name: str,
    sequence_name: str,
    save_path: str | Path,
    show: bool = False,
) -> None:
    """Plot full 3D trajectory comparison with start/end markers and error vectors."""
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure(figsize=(10, 8), dpi=150)
    ax = fig.add_subplot(111, projection="3d")

    gt = ate_result.gt_positions
    est = ate_result.aligned_est_positions

    # Plot trajectories in 3D
    ax.plot(gt[:, 0], gt[:, 1], gt[:, 2], color=COLORS["gt"], linewidth=2.0, label="Ground Truth", zorder=3)
    ax.plot(
        est[:, 0],
        est[:, 1],
        est[:, 2],
        color=COLORS["aligned"],
        linewidth=1.8,
        linestyle="--",
        label=f"Estimated ({ate_result.alignment.upper()} aligned)",
        zorder=4,
    )

    # Start and terminus points
    ax.scatter(gt[0, 0], gt[0, 1], gt[0, 2], color="black", s=80, marker="o", label="Start (GT)")
    ax.scatter(gt[-1, 0], gt[-1, 1], gt[-1, 2], color="red", s=80, marker="^", label="End (GT)")
    ax.scatter(est[-1, 0], est[-1, 1], est[-1, 2], color="blue", s=80, marker="^", label="End (Est)")

    # Draw subset of error vectors
    step = max(1, len(gt) // 20)
    for i in range(0, len(gt), step):
        ax.plot(
            [gt[i, 0], est[i, 0]],
            [gt[i, 1], est[i, 1]],
            [gt[i, 2], est[i, 2]],
            color=COLORS["error"],
            alpha=0.6,
            linewidth=0.8,
        )

    ax.set_title(
        f"3D Trajectory — {config_id.upper()} | {dataset_name} ({sequence_name})\n"
        f"ATE RMSE: {ate_result.rmse:.4f} m | Scale: {ate_result.scale:.4f}",
        fontsize=11,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("X (m)", fontsize=10)
    ax.set_ylabel("Y (m)", fontsize=10)
    ax.set_zlabel("Z (m)", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_benchmark_comparison(
    summary_rows: list,
    dataset_name: str,
    save_path: str | Path,
    show: bool = False,
) -> None:
    """Grouped bar chart comparing ATE RMSE, FPS, and tracking success across configs with zero label overlap."""
    import pandas as pd
    df = pd.DataFrame(summary_rows)
    df = df[df["dataset"] == dataset_name].reset_index(drop=True)
    if df.empty:
        return

    configs = list(df["config_id"].unique())
    sequences = list(df["sequence"].unique())
    n_configs = len(configs)
    n_seq = len(sequences)

    x = np.arange(n_configs)
    bar_width = 0.7 / max(n_seq, 1)

    seq_colors = ["#2b5c8f", "#e06666", "#2ca02c", "#ff7f0e"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=200)
    fig.suptitle(f"Benchmark Multi-Sequence Comparison — {dataset_name.upper()}", fontsize=14, fontweight="bold", y=0.98)

    metrics = [
        ("ate_rmse_m", "ATE RMSE (m)", "Trajectory Error (ATE RMSE)", axes[0], None),
        ("mean_fps", "Mean FPS", "Processing Speed (FPS)", axes[1], None),
        ("tracking_success_pct", "Success Rate (%)", "Tracking Robustness (%)", axes[2], (0, 105)),
    ]

    for col_name, ylabel, title, ax, ylim in metrics:
        for s_idx, seq in enumerate(sequences):
            seq_df = df[df["sequence"] == seq]
            vals = []
            for cfg in configs:
                match = seq_df[seq_df["config_id"] == cfg]
                if not match.empty and not pd.isna(match[col_name].values[0]):
                    vals.append(float(match[col_name].values[0]))
                else:
                    vals.append(0.0)

            offset = (s_idx - n_seq / 2 + 0.5) * bar_width
            seq_label = (
                seq.replace("_Easy_P000", "")
                .replace("_traj1_loop", " (Living)")
                .replace("_traj0_loop", " (Office)")
                .replace("ocean", "Ocean")
                .replace("abandonedfactory", "Factory")
            )
            ax.bar(
                x + offset,
                vals,
                width=bar_width,
                label=seq_label,
                color=seq_colors[s_idx % len(seq_colors)],
                edgecolor="black",
                linewidth=0.6,
                alpha=0.9,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(configs, rotation=15, ha="right", fontsize=9, fontweight="medium")
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        if ylim:
            ax.set_ylim(ylim)
        ax.legend(title="Sequence", fontsize=8, title_fontsize=8, loc="upper right")

    plt.tight_layout()
    out_path = Path(save_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
