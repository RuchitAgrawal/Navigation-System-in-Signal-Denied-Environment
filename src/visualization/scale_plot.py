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
        ax.plot(frames[finite], scales[finite], color="#0d6efd", linewidth=1.2)
        ax.fill_between(frames[finite], scales[finite], 1.0, alpha=0.2, color="#0d6efd")

    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0, label="Scale=1 (ideal)")
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
