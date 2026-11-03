"""
tests/test_trajectory_filter.py — Unit tests for trajectory smoothing and outlier filtering.
"""

import numpy as np
import pytest

from src.geometry.transforms import make_pose, is_valid_pose
from src.odometry.filter import (
    smooth_positions_moving_average,
    smooth_trajectory_poses,
    filter_outlier_steps,
)


@pytest.fixture
def synthetic_noisy_trajectory():
    n_poses = 30
    poses = []
    rng = np.random.default_rng(42)

    for i in range(n_poses):
        t = np.array([i * 0.1, 0.0, 0.0]) + rng.normal(0, 0.02, 3)
        R = np.eye(3)
        poses.append(make_pose(R, t))

    return poses


def test_smooth_positions_reduces_noise():
    pts = np.zeros((20, 3))
    pts[:, 0] = np.linspace(0, 10, 20)
    noise = np.random.default_rng(0).normal(0, 0.5, (20, 3))
    noisy_pts = pts + noise

    smoothed = smooth_positions_moving_average(noisy_pts, window_size=5)

    # Difference from ground truth should decrease
    err_noisy = np.mean(np.linalg.norm(noisy_pts - pts, axis=1))
    err_smooth = np.mean(np.linalg.norm(smoothed - pts, axis=1))
    assert err_smooth < err_noisy


def test_smooth_trajectory_poses_preserves_validity(synthetic_noisy_trajectory):
    smoothed = smooth_trajectory_poses(synthetic_noisy_trajectory, window_size=5)
    assert len(smoothed) == len(synthetic_noisy_trajectory)
    for p in smoothed:
        assert is_valid_pose(p)


def test_filter_outlier_steps():
    poses = [make_pose(np.eye(3), np.array([float(i), 0.0, 0.0])) for i in range(5)]
    # Inject large outlier at frame 2
    poses[2] = make_pose(np.eye(3), np.array([100.0, 0.0, 0.0]))

    filtered = filter_outlier_steps(poses, max_step_distance=2.0)
    assert len(filtered) == 5
    # The jump of 100m should be rejected
    assert filtered[2][0, 3] < 10.0


def test_filter_short_trajectory():
    short = [make_pose(np.eye(3), np.zeros(3))]
    res = smooth_trajectory_poses(short, window_size=5)
    assert len(res) == 1

