"""
test_metrics.py — Unit tests for RPE computation and metrics utilities.
"""
import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from src.evaluation.rpe import compute_rpe
from src.geometry.transforms import make_pose, invert_pose


def _constant_drift_trajectory(n: int, drift_per_frame: float = 0.01):
    """Trajectory with constant positive-X drift per frame."""
    poses = []
    for i in range(n):
        t = np.array([i * 0.1 + i * drift_per_frame, 0.0, 0.0])
        poses.append(make_pose(np.eye(3), t))
    return poses


class TestRPE:
    def test_zero_rpe_identical(self, straight_trajectory):
        """RPE should be 0 for estimated = ground truth."""
        result = compute_rpe(straight_trajectory, straight_trajectory, delta=1)
        np.testing.assert_allclose(result.trans_rmse, 0.0, atol=1e-8)
        np.testing.assert_allclose(result.rot_rmse_deg, 0.0, atol=1e-8)

    def test_rpe_detects_constant_drift(self):
        """RPE should be non-zero and constant for constant per-frame drift."""
        n = 50
        gt_poses  = [make_pose(np.eye(3), np.array([i * 0.1, 0.0, 0.0])) for i in range(n)]
        est_poses = [make_pose(np.eye(3), np.array([i * 0.11, 0.0, 0.0])) for i in range(n)]
        result = compute_rpe(est_poses, gt_poses, delta=1)
        assert result.trans_rmse > 0.0
        # Each step the estimated moves 0.11 instead of 0.10 → ~0.01 relative error
        np.testing.assert_allclose(result.trans_mean, 0.01, rtol=0.05)

    def test_rpe_delta_affects_n_pairs(self, straight_trajectory):
        n = len(straight_trajectory)
        r1 = compute_rpe(straight_trajectory, straight_trajectory, delta=1)
        r5 = compute_rpe(straight_trajectory, straight_trajectory, delta=5)
        assert r1.n_pairs == n - 1
        assert r5.n_pairs == n - 5

    def test_rpe_raises_no_valid_pairs(self):
        """Should raise ValueError when no valid pairs exist (all GT is None)."""
        poses = [make_pose(np.eye(3), np.zeros(3))] * 10
        gt = [None] * 10
        with pytest.raises(ValueError):
            compute_rpe(poses, gt, delta=1)

    def test_rpe_rotation_error(self):
        """RPE should detect a constant per-frame rotation error."""
        n = 30
        R_err = Rotation.from_euler("z", 1, degrees=True).as_matrix()
        gt_poses  = [make_pose(np.eye(3), np.zeros(3))] * n
        est_poses = [make_pose(np.linalg.matrix_power(R_err, i), np.zeros(3))
                     for i in range(n)]
        result = compute_rpe(est_poses, gt_poses, delta=1)
        # Each step adds 1 deg of rotation error
        np.testing.assert_allclose(result.rot_mean_deg, 1.0, atol=0.01)
