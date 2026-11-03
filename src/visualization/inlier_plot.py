"""
inlier_plot.py — RANSAC inlier ratio and correspondence tracking visualization.

Plots the number of matched features, RANSAC inliers, and inlier ratio
over the flight trajectory to diagnose tracking health.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.geometry.pose import FrameDiagnostics


def plot_inlier_history(
    diagnostics: List[FrameDiagnostics],
    config_id: str,
    dataset_name: str,
    save_path: str | Path,
    show: bool = False,
) -> Path:
    """Plot inlier count and inlier ratio over frame index."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    frames = [d.frame_idx for d in diagnostics]
    n_kps = [d.n_keypoints_curr for d in diagnostics]
    n_matches = [d.n_filtered_matches for d in diagnostics]
    n_inliers = [d.n_ransac_inliers for d in diagnostics]
    ratios = [d.ransac_inlier_ratio * 100.0 for d in diagnostics]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, dpi=150)

    # Subplot 1: Feature Counts
    ax1.plot(frames, n_kps, label="Keypoints", color="#6c757d", linestyle="--", linewidth=1.0)
    ax1.plot(frames, n_matches, label="Matches (Ratio Filtered)", color="#0d6efd", linewidth=1.2)
    ax1.plot(frames, n_inliers, label="RANSAC Inliers", color="#198754", linewidth=1.8)
    ax1.set_ylabel("Count", fontsize=10)
    ax1.set_title(f"Correspondence & Inlier History — {config_id.upper()} | {dataset_name}", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(fontsize=8, loc="upper right")

    # Subplot 2: Inlier Ratio %
    ax2.plot(frames, ratios, color="#ff7f0e", linewidth=1.5, label="Inlier Ratio (%)")
    ax2.axhline(50.0, color="gray", linestyle=":", linewidth=0.8, label="50% Threshold")
    ax2.axhline(20.0, color="red", linestyle="--", linewidth=1.0, label="Degeneracy Warning (20%)")
    ax2.set_xlabel("Frame Index", fontsize=10)
    ax2.set_ylabel("Inlier Ratio [%]", fontsize=10)
    ax2.set_ylim([0, 105])
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(fontsize=8, loc="lower right")

    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return save_path

