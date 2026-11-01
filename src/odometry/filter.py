"""
filter.py — Trajectory post-processing and kinematic smoothing filters.

Applies moving-average and outlier rejection filtering to raw visual odometry
trajectories to suppress high-frequency epipolar noise while preserving vehicle motion.
"""

from __future__ import annotations

from typing import List, Optional
import numpy as np
from scipy.spatial.transform import Rotation

from src.geometry.transforms import make_pose


def smooth_positions_moving_average(positions: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Apply moving average smoothing to an (N, 3) position array.

    Parameters
    ----------
    positions : (N, 3) float array
    window_size : Odd integer window size (default: 5)

    Returns
    -------
    smoothed : (N, 3) float array
    """
    n_pts = len(positions)
    if n_pts < window_size or window_size <= 1:
        return positions.copy()

    smoothed = np.zeros_like(positions)
    half_w = window_size // 2

    for i in range(n_pts):
        start = max(0, i - half_w)
        end = min(n_pts, i + half_w + 1)
        smoothed[i] = np.mean(positions[start:end], axis=0)

    return smoothed


def smooth_trajectory_poses(
    poses: List[np.ndarray],
    window_size: int = 5,
) -> List[np.ndarray]:
    """Smooth both positions and rotations of a list of 4x4 SE(3) poses.

    Translations are smoothed via moving average; rotations are smoothed
    via moving average of rotation vectors (Rodrigues).
    """
    if len(poses) < window_size or window_size <= 1:
        return [p.copy() for p in poses]

    n_poses = len(poses)
    positions = np.array([p[:3, 3] for p in poses])
    rotations = [p[:3, :3] for p in poses]

    # Convert rotations to rotation vectors
    rot_vecs = np.array([Rotation.from_matrix(R).as_rotvec() for R in rotations])

    # Smooth positions and rotvecs
    smooth_pos = smooth_positions_moving_average(positions, window_size)
    smooth_rot = smooth_positions_moving_average(rot_vecs, window_size)

    smoothed_poses = []
    for i in range(n_poses):
        R_smooth = Rotation.from_rotvec(smooth_rot[i]).as_matrix()
        t_smooth = smooth_pos[i]
        smoothed_poses.append(make_pose(R_smooth, t_smooth))

    return smoothed_poses


def filter_outlier_steps(
    poses: List[np.ndarray],
    max_step_distance: float = 2.0,
) -> List[np.ndarray]:
    """Filter sudden single-frame spikes exceeding max_step_distance."""
    if len(poses) <= 2:
        return [p.copy() for p in poses]

    filtered = [poses[0].copy()]
    for i in range(1, len(poses)):
        curr_p = poses[i]
        prev_p = filtered[-1]
        step = np.linalg.norm(curr_p[:3, 3] - prev_p[:3, 3])
        if step > max_step_distance:
            # Outlier jump: carry previous pose forward
            filtered.append(prev_p.copy())
        else:
            filtered.append(curr_p.copy())

    return filtered
