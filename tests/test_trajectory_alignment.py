"""
test_trajectory_alignment.py — Unit tests for Umeyama trajectory alignment.

Validates that the alignment correctly recovers a known transform applied
to a synthetic trajectory, under both Sim(3) and SE(3) modes.
"""
import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from src.evaluation.ate import compute_ate, umeyama_alignment
from src.geometry.transforms import make_pose


def _make_gt_poses(positions: np.ndarray) -> list:
    """Wrap (N, 3) positions as identity-rotation T_wc poses."""
    return [make_pose(np.eye(3), p) for p in positions]


class TestUmeyamaAlignment:
    def test_identity_alignment(self):
        """Aligning a trajectory against itself should give scale=1, no error."""
        pts = np.random.default_rng(0).uniform(-5, 5, (50, 3))
        s, R, t = umeyama_alignment(pts, pts, with_scale=True)
        np.testing.assert_allclose(s, 1.0, atol=1e-8)
        np.testing.assert_allclose(R, np.eye(3), atol=1e-8)
        np.testing.assert_allclose(t, np.zeros(3), atol=1e-8)

    def test_known_scale_recovery(self):
        """Alignment should recover a known scale factor."""
        rng = np.random.default_rng(1)
        pts_gt = rng.uniform(-3, 3, (80, 3))
        known_scale = 2.5
        pts_est = pts_gt / known_scale  # estimated is scaled-down

        s, R, t = umeyama_alignment(pts_est, pts_gt, with_scale=True)
        np.testing.assert_allclose(s, known_scale, rtol=1e-6)

    def test_known_rotation_recovery(self):
        """Alignment should recover a known rotation."""
        rng = np.random.default_rng(2)
        pts_gt = rng.uniform(-5, 5, (60, 3))
        R_known = Rotation.from_euler("y", 37, degrees=True).as_matrix()
        t_known = np.array([1.5, -0.5, 2.0])
        pts_est = (R_known.T @ (pts_gt - t_known).T).T  # inverse transform

        s, R_rec, t_rec = umeyama_alignment(pts_est, pts_gt, with_scale=False)
        np.testing.assert_allclose(s, 1.0, atol=1e-6)
        np.testing.assert_allclose(R_rec, R_known, atol=1e-6)

    def test_se3_mode_fixed_scale(self):
        """SE(3) alignment must return scale = 1.0 regardless of true scale."""
        pts_gt = np.random.default_rng(3).uniform(-4, 4, (40, 3))
        pts_est = pts_gt * 3.0  # different scale
        s, _, _ = umeyama_alignment(pts_est, pts_gt, with_scale=False)
        assert s == 1.0


class TestComputeATE:
    def test_zero_ate_identical_trajectories(self, straight_trajectory):
        """ATE should be 0 when estimated = ground truth."""
        gt_poses = straight_trajectory
        est_poses = [T.copy() for T in straight_trajectory]
        result = compute_ate(est_poses, gt_poses, alignment="se3")
        np.testing.assert_allclose(result.rmse, 0.0, atol=1e-8)

    def test_sim3_removes_global_scale(self, straight_trajectory):
        """Sim(3) alignment should yield near-zero ATE for a scaled trajectory.

        Umeyama aligns src→dst: s * R * src + t ≈ dst.
        Here src=est (scaled 2×), dst=gt → s = 0.5 to map est back to gt scale.
        """
        gt_poses = straight_trajectory
        # Scale estimated trajectory by 2x (simulates monocular scale ambiguity)
        est_poses = [make_pose(T[:3, :3], T[:3, 3] * 2.0) for T in straight_trajectory]
        result = compute_ate(est_poses, gt_poses, alignment="sim3")
        np.testing.assert_allclose(result.rmse, 0.0, atol=1e-6)
        # Umeyama recovers s=0.5 to bring est (2× too large) down to gt scale
        np.testing.assert_allclose(result.scale, 0.5, rtol=1e-5)

    def test_ate_nonzero_for_drifted_trajectory(self, straight_trajectory):
        """Adding random noise should produce non-zero ATE."""
        rng = np.random.default_rng(42)
        gt_poses = straight_trajectory
        est_poses = [make_pose(T[:3, :3], T[:3, 3] + rng.normal(0, 0.1, 3))
                     for T in straight_trajectory]
        result = compute_ate(est_poses, gt_poses, alignment="sim3")
        assert result.rmse > 0.0

    def test_ate_n_frames_count(self, straight_trajectory):
        """n_frames in ATEResult should match the number of paired poses."""
        n = len(straight_trajectory)
        result = compute_ate(straight_trajectory, straight_trajectory, alignment="se3")
        assert result.n_frames == n

    def test_ate_raises_with_too_few_poses(self):
        """Should raise ValueError when fewer than 3 pose pairs are available."""
        poses = [make_pose(np.eye(3), np.zeros(3))] * 2
        with pytest.raises(ValueError, match="at least 3"):
            compute_ate(poses, poses, alignment="se3")
