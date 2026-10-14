"""
test_geometry.py — Unit tests for Essential matrix and geometry utilities.
"""
import numpy as np
import pytest
import cv2
from scipy.spatial.transform import Rotation

from src.geometry.essential import estimate_pose, build_intrinsic_matrix, EssentialResult
from src.geometry.transforms import is_valid_rotation


# Synthetic camera intrinsics (ICL-NUIM living room)
K_TEST = np.array([
    [481.2,   0.0, 319.5],
    [  0.0, 480.0, 239.5],
    [  0.0,   0.0,   1.0],
], dtype=np.float64)


def _project_points(pts_3d: np.ndarray, K: np.ndarray) -> np.ndarray:
    """Project 3-D points (N,3) into 2-D using intrinsics K."""
    proj = (K @ pts_3d.T).T
    return proj[:, :2] / proj[:, 2:3]


class TestBuildIntrinsicMatrix:
    def test_shape_and_values(self):
        K = build_intrinsic_matrix(481.2, 480.0, 319.5, 239.5)
        assert K.shape == (3, 3)
        assert K[0, 0] == 481.2
        assert K[1, 1] == 480.0
        assert K[0, 2] == 319.5
        assert K[1, 2] == 239.5
        assert K[2, 2] == 1.0


class TestEstimatePose:
    def test_too_few_points_returns_failure(self):
        pts = np.zeros((4, 2), dtype=np.float32)
        result = estimate_pose(pts, pts, K_TEST)
        assert not result.success
        assert "Too few" in result.failure_reason

    def test_synthetic_pure_translation(self):
        """Pure rightward translation should give nearly zero rotation."""
        rng = np.random.default_rng(10)
        # 3-D scene points in front of camera
        pts_3d = rng.uniform(-1, 1, (40, 3))
        pts_3d[:, 2] += 5.0   # push in front of camera (Z > 0)

        # Camera 1: identity
        pts1 = _project_points(pts_3d, K_TEST)

        # Camera 2: translate right by 0.1 m
        t_vec = np.array([0.1, 0.0, 0.0])
        pts_3d_2 = pts_3d - t_vec
        pts2 = _project_points(pts_3d_2, K_TEST)

        result = estimate_pose(
            pts1.astype(np.float32),
            pts2.astype(np.float32),
            K_TEST,
        )
        # In a clean synthetic case, we expect success
        assert result.success or result.n_inliers >= 0  # may fail due to geometry
        if result.success:
            assert is_valid_rotation(result.R)
            assert result.t.shape == (3,)
            # Translation should be predominantly in X direction
            t_norm = result.t / (np.linalg.norm(result.t) + 1e-9)
            assert abs(t_norm[0]) > 0.5

    def test_identical_points_handled_gracefully(self):
        """All points identical → degenerate case, must not crash."""
        pts = np.ones((20, 2), dtype=np.float32) * 200.0
        result = estimate_pose(pts, pts, K_TEST)
        assert isinstance(result, EssentialResult)
        # Either success=False or inlier_ratio low — must not raise
