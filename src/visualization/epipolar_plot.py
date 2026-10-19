# visualization/epipolar_plot.py -- Epipolar geometry visualization
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import cv2

\ndef draw_epipolar_lines(
    img1: np.ndarray, img2: np.ndarray,
    pts1: np.ndarray, lines2: np.ndarray,
    save_path,
    n_draw: int = 20,
) -> None:
    '''Draw epipolar lines in img2 for points in img1.
    lines2: (N,3) epipolar line coefficients [a,b,c] for ax+by+c=0.
    '''
    h, w = img2.shape[:2]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.imshow(cv2.cvtColor(img1, cv2.COLOR_GRAY2RGB)); ax1.set_title('Frame t-1'); ax1.axis('off')
    ax2.imshow(cv2.cvtColor(img2, cv2.COLOR_GRAY2RGB)); ax2.set_title('Frame t (epipolar lines)'); ax2.axis('off')
    colors = list(mcolors.TABLEAU_COLORS.values())
    n = min(n_draw, len(pts1))
    for i in range(n):
        c = colors[i % len(colors)]
        ax1.plot(*pts1[i], 'o', color=c, markersize=5)
        a, b, cc = lines2[i]
        if abs(b) > 1e-6:
            xs = np.array([0, w], dtype=np.float32)
            ys = -(a * xs + cc) / b
            ax2.plot(xs, ys, color=c, linewidth=0.8, alpha=0.8)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.close(fig)

