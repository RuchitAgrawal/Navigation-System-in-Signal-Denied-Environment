# evaluation/drift.py -- Scale drift analysis utilities

from __future__ import annotations
import numpy as np
from typing import List, Optional


def compute_scale_over_time(
    est_poses: List[np.ndarray],
    gt_poses: List[Optional[np.ndarray]],
    window: int = 10,
) -> np.ndarray:
    '''Compute local scale (est/gt) in a sliding window along the trajectory.

    For each frame i with valid GT, compute the ratio of cumulative
    estimated path length to GT path length over the preceding window frames.
    Returns (N,) array of local scale estimates.
    '''
    scales = []
    for i in range(window, len(est_poses)):
        est_dists, gt_dists = [], []
        for j in range(i - window, i):
            if gt_poses[j] is None or gt_poses[j+1] is None:
                continue
            gt_dists.append(np.linalg.norm(gt_poses[j+1][:3,3] - gt_poses[j][:3,3]))
            est_dists.append(np.linalg.norm(est_poses[j+1][:3,3] - est_poses[j][:3,3]))
        if sum(gt_dists) > 1e-8:
            scales.append(sum(est_dists) / sum(gt_dists))
        else:
            scales.append(float('nan'))
    return np.array(scales, dtype=np.float64)


