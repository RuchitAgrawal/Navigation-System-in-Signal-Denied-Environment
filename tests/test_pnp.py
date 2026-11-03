"""
tests/test_pnp.py — Unit tests for RGB-D PnP pose estimation.
"""

import cv2
import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from src.geometry.pnp import backproject_2d_to_3d, estimate_pose_pnp, hybrid_estimate_pose


K = np.array([[480.0, 0.0, 320.0], [0.0, 480.0, 240.0], [0.0, 0.0, 1.0]], dtype=np.float64)


class TestBackproject2Dto3D:
    def test_backproject_center_pixel(self):
        depth = np.full((480, 640), 2.0, dtype=np.float32)
        pts_2d = np.array([[320.0, 240.0]], dtype=np.float32)

        pts_3d, valid = backproject_2d_to_3d(pts_2d, depth, K, depth_scale=1.0)
        assert valid[0]
        # (320, 240) is principal point, so X=0, Y=0, Z=2.0
        np.testing.assert_allclose(pts_3d[0], [0.0, 0.0, 2.0], atol=1e-5)

    def test_invalid_depth_masked_out(self):
        depth = np.full((480, 640), 0.0, dtype=np.float32)  # 0.0 is invalid
        pts_2d = np.array([[100.0, 100.0]], dtype=np.float32)
        pts_3d, valid = backproject_2d_to_3d(pts_2d, depth, K, depth_scale=1.0)
        assert not valid[0]


class TestEstimatePosePnP:
    def test_pnp_recovers_known_metric_transform(self):
        rng = np.random.default_rng(42)
        n_pts = 40
        # 3D points in front of camera 1
        pts_3d_1 = np.zeros((n_pts, 3), dtype=np.float64)
        pts_3d_1[:, 0] = rng.uniform(-1.0, 1.0, n_pts)
        pts_3d_1[:, 1] = rng.uniform(-1.0, 1.0, n_pts)
        pts_3d_1[:, 2] = rng.uniform(2.0, 5.0, n_pts)

        # Ground truth transformation: small rotation and 0.2m translation
        R_gt = Rotation.from_euler("y", 5.0, degrees=True).as_matrix()
        t_gt = np.array([0.15, -0.05, 0.20], dtype=np.float64).reshape(3, 1)

        # Transform to camera 2: P_2 = R_gt @ P_1 + t_gt
        pts_3d_2 = (R_gt @ pts_3d_1.T + t_gt).T

        # Project to camera 2
        fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]
        pts_2d_2 = np.zeros((n_pts, 2), dtype=np.float32)
        pts_2d_2[:, 0] = (fx * pts_3d_2[:, 0] / pts_3d_2[:, 2] + cx).astype(np.float32)
        pts_2d_2[:, 1] = (fy * pts_3d_2[:, 1] / pts_3d_2[:, 2] + cy).astype(np.float32)

        res = estimate_pose_pnp(pts_3d_1, pts_2d_2, K)
        assert res.R is not None
        assert res.is_metric
        assert res.n_inliers >= 30

        # Check rotation accuracy (< 0.5 degrees)
        R_err = res.R.T @ R_gt
        angle_err = np.degrees(np.arccos(np.clip((np.trace(R_err) - 1) / 2.0, -1.0, 1.0)))
        assert angle_err < 0.5

        # Check translation vector metric accuracy (< 1 cm)
        np.testing.assert_allclose(res.t.flatten(), t_gt.flatten(), atol=0.01)

    def test_insufficient_points_handled_safely(self):
        pts_3d = np.zeros((3, 3), dtype=np.float64)
        pts_2d = np.zeros((3, 2), dtype=np.float32)
        res = estimate_pose_pnp(pts_3d, pts_2d, K)
        assert res.R is None


class TestHybridEstimatePose:
    def test_fallback_when_no_depth(self):
        rng = np.random.default_rng(7)
        pts_prev = rng.uniform(50, 400, (30, 2)).astype(np.float32)
        pts_curr = pts_prev + rng.uniform(-2, 2, (30, 2)).astype(np.float32)

        res = hybrid_estimate_pose(pts_prev, pts_curr, K, depth_prev=None)
        assert res.mode == "essential_fallback"
        assert not res.is_metric

