"""
src/visualization/scale_plot.py — Scale drift visualization.

Plots the local scale ratio (estimated/GT) as a function of frame index,
with a horizontal reference at scale=1.0 and fill-between shading.
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_scale_drift(
    scales: np.ndarray,
    config_id: str,
    dataset_name: str,
    save_path,
    window: int = 10,
) -> None:
    """Save a scale drift plot.

    Parameters
    ----------
    scales      : (N,) array of local scale estimates (may contain NaN).
    config_id   : feature config label for the title.
    dataset_name: dataset name for the title.
    save_path   : file path to save the PNG figure.
    window      : window size used during computation (shown in title).
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    frames = np.arange(len(scales))
    finite = np.isfinite(scales)

    if np.any(finite):
        ax.plot(frames[finite], scales[finite], color="#0d6efd", linewidth=1.2, label="Local Scale")
        ax.fill_between(frames[finite], scales[finite], 1.0, alpha=0.2, color="#0d6efd")

        # Add moving average trendline
        if len(scales[finite]) >= 5:
            kernel = np.ones(5) / 5
            trend = np.convolve(scales[finite], kernel, mode="same")
            ax.plot(frames[finite], trend, color="#dc3545", linestyle=":", linewidth=1.5, label="Trend (MA-5)")

        mean_val = float(np.mean(scales[finite]))
        std_val = float(np.std(scales[finite]))
        stats_txt = f"Mean: {mean_val:.3f}\nStd:  {std_val:.3f}"
        ax.text(
            0.02,
            0.95,
            stats_txt,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8),
        )

    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0, label="Scale=1.0 (ideal)")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Local Scale (est / GT)")
    ax.set_title(
        f"Scale Drift — {config_id.upper()} | {dataset_name} | window={window}"
    )
    ax.legend()
    ax.grid(True, alpha=0.35)
    plt.tight_layout()

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
