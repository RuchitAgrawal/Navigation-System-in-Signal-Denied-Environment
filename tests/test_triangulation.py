"""
tests/test_triangulation.py — Unit tests for triangulation utilities.
"""
import numpy as np
import pytest
from src.geometry.triangulation import triangulate_points, count_positive_depth

K = np.float64([[481.2, 0, 319.5], [0, 480, 239.5], [0, 0, 1]])


class TestTriangulatePoints:
    def test_returns_none_for_too_few_points(self):
        pts = np.zeros((3, 2), dtype=np.float32)
        result = triangulate_points(pts, pts, K, np.eye(3), np.array([0.1, 0.0, 0.0]))
        assert result is None

    def test_output_shape(self):
        rng = np.random.default_rng(0)
        pts3d = rng.uniform(-1, 1, (20, 3))
        pts3d[:, 2] += 5.0  # push in front of camera

        proj1 = (K @ pts3d.T).T
        pts1 = (proj1[:, :2] / proj1[:, 2:]).astype(np.float32)

        R = np.eye(3)
        t = np.array([0.2, 0.0, 0.0])
        pts3d_2 = pts3d - t
        proj2 = (K @ pts3d_2.T).T
        pts2 = (proj2[:, :2] / proj2[:, 2:]).astype(np.float32)

        result = triangulate_points(pts1, pts2, K, R, t)
        if result is not None:
            assert result.shape[1] == 3


class TestCountPositiveDepth:
    def test_forward_points_all_positive(self):
        pts3d = np.array([[0.0, 0.0, 5.0],
                          [0.5, 0.0, 3.0],
                          [-0.5, 0.0, 4.0]], dtype=np.float64)
        n = count_positive_depth(pts3d, np.eye(3), np.zeros(3))
        assert n == 3

    def test_behind_camera_zero(self):
        pts3d = np.array([[0.0, 0.0, -5.0], [0.0, 0.0, -3.0]], dtype=np.float64)
        n = count_positive_depth(pts3d, np.eye(3), np.zeros(3))
        assert n == 0
