"""
rpe.py — Relative Pose Error (RPE) computation.

RPE measures the drift of the estimated trajectory relative to ground truth
over a fixed frame interval delta. It is independent of global alignment.

For each valid frame pair (i, i+delta):
    Q_est = inv(T_est[i]) @ T_est[i+delta]
    Q_gt  = inv(T_gt[i])  @ T_gt[i+delta]
    E_i   = inv(Q_est) @ Q_gt          (relative error transform)

    trans_error[i] = ||E_i[:3, 3]||₂   (translation component of error)
    rot_error[i]   = arccos((trace(E_i[:3,:3]) - 1) / 2)   (rotation angle)

Reference
---------
Sturm, J., et al. (2012). A benchmark for the evaluation of RGB-D SLAM systems.
IROS 2012.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from src.geometry.transforms import invert_pose, rotation_angle_rad


@dataclass
class RPEResult:
    """Result of RPE computation."""
    delta: int               # frame interval used
    n_pairs: int             # number of valid (i, i+delta) pairs
    trans_rmse: float        # translation RMSE
    trans_mean: float
    trans_median: float
    rot_rmse_deg: float      # rotation RMSE in degrees
    rot_mean_deg: float
    rot_median_deg: float
    per_pair_trans: np.ndarray   # (N,) per-pair translation errors
    per_pair_rot_deg: np.ndarray # (N,) per-pair rotation errors (degrees)


def compute_rpe(
    est_poses: List[np.ndarray],
    gt_poses: List[Optional[np.ndarray]],
    delta: int = 1,
) -> RPEResult:
    """Compute Relative Pose Error.

    Parameters
    ----------
    est_poses : list of (4, 4) float64  Estimated T_wc poses.
    gt_poses  : list of (4, 4) | None   Ground-truth T_wc poses.
    delta     : int   Frame interval between pairs.

    Returns
    -------
    RPEResult
    """
    assert len(est_poses) == len(gt_poses), "pose lists must be the same length"

    trans_errors = []
    rot_errors_deg = []

    for i in range(len(est_poses) - delta):
        j = i + delta

        T_est_i = est_poses[i]
        T_est_j = est_poses[j]
        T_gt_i  = gt_poses[i]
        T_gt_j  = gt_poses[j]

        if T_gt_i is None or T_gt_j is None:
            continue

        # Relative transforms
        Q_est = invert_pose(T_est_i) @ T_est_j
        Q_gt  = invert_pose(T_gt_i)  @ T_gt_j

        # Error transform
        E = invert_pose(Q_est) @ Q_gt

        trans_err = float(np.linalg.norm(E[:3, 3]))
        rot_err_rad = rotation_angle_rad(E[:3, :3])
        rot_err_deg = float(np.degrees(rot_err_rad))

        trans_errors.append(trans_err)
        rot_errors_deg.append(rot_err_deg)

    if not trans_errors:
        raise ValueError("No valid (i, i+delta) pairs found for RPE computation.")

    t_arr = np.array(trans_errors, dtype=np.float64)
    r_arr = np.array(rot_errors_deg, dtype=np.float64)

    return RPEResult(
        delta=delta,
        n_pairs=len(trans_errors),
        trans_rmse=float(np.sqrt(np.mean(t_arr ** 2))),
        trans_mean=float(np.mean(t_arr)),
        trans_median=float(np.median(t_arr)),
        rot_rmse_deg=float(np.sqrt(np.mean(r_arr ** 2))),
        rot_mean_deg=float(np.mean(r_arr)),
        rot_median_deg=float(np.median(r_arr)),
        per_pair_trans=t_arr,
        per_pair_rot_deg=r_arr,
    )
