"""
match_plot.py — Feature match and RANSAC inlier/outlier visualizations.

Generates side-by-side images showing:
- All candidate matches (blue)
- RANSAC inliers (green)
- RANSAC outliers (red)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def draw_matches_inliers_outliers(
    img_prev: np.ndarray,
    img_curr: np.ndarray,
    kps_prev: List[cv2.KeyPoint],
    kps_curr: List[cv2.KeyPoint],
    matches: List[cv2.DMatch],
    inlier_mask: Optional[np.ndarray],
    save_path: str | Path,
    frame_idx: int = 0,
    max_draw: int = 200,
) -> None:
    """Draw matches coloured by RANSAC inlier / outlier status.

    Parameters
    ----------
    img_prev, img_curr : (H, W) uint8 greyscale images.
    kps_prev, kps_curr : keypoint lists.
    matches            : filtered match list (before RANSAC).
    inlier_mask        : (N,) uint8 array from RANSAC (1=inlier, 0=outlier).
                         If None, all matches are drawn as inliers.
    save_path          : output file path.
    frame_idx          : used in figure title.
    max_draw           : maximum number of matches to render (for speed).
    """
    h, w = img_prev.shape[:2]
    canvas = np.zeros((h, w * 2, 3), dtype=np.uint8)
    canvas[:, :w]  = cv2.cvtColor(img_prev, cv2.COLOR_GRAY2BGR)
    canvas[:, w:]  = cv2.cvtColor(img_curr, cv2.COLOR_GRAY2BGR)

    if inlier_mask is None:
        inlier_mask = np.ones(len(matches), dtype=np.uint8)

    drawn = 0
    for i, m in enumerate(matches[:max_draw]):
        if i >= len(inlier_mask):
            break
        pt1 = tuple(map(int, kps_prev[m.queryIdx].pt))
        pt2 = (int(kps_curr[m.trainIdx].pt[0]) + w,
                int(kps_curr[m.trainIdx].pt[1]))
        color = (0, 220, 0) if inlier_mask[i] else (0, 0, 220)   # BGR
        cv2.line(canvas, pt1, pt2, color, 1, cv2.LINE_AA)
        cv2.circle(canvas, pt1, 3, color, -1)
        cv2.circle(canvas, pt2, 3, color, -1)
        drawn += 1

    n_inliers = int(inlier_mask.sum())
    n_total   = len(matches)
    title_txt = (f"Frame {frame_idx} | "
                 f"Inliers: {n_inliers}/{n_total} "
                 f"({100*n_inliers/max(n_total,1):.1f}%)")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    ax.set_title(title_txt, fontsize=11)
    ax.axis("off")

    from matplotlib.patches import Patch
    legend = [Patch(color=(0, 220/255, 0), label="Inlier"),
              Patch(color=(0, 0, 220/255), label="Outlier")]
    ax.legend(handles=legend, loc="lower right", fontsize=9)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
