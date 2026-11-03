# tests/test_scale_analysis.py -- Unit tests for scale drift utility
import numpy as np
import pytest
from src.evaluation.drift import compute_scale_over_time
from src.geometry.transforms import make_pose
def make_poses(n, scale=1.0):
    return [make_pose(np.eye(3), np.array([i*0.1*scale, 0.0, 0.0])) for i in range(n)]


class TestComputeScaleOverTime:
    def test_constant_scale_one_returns_ones(self):
        gt = make_poses(30, scale=1.0)
        est = make_poses(30, scale=1.0)
        scales = compute_scale_over_time(est, gt, window=5)
        finite = scales[np.isfinite(scales)]
        np.testing.assert_allclose(finite, 1.0, atol=0.01)

    def test_double_scale_returns_two(self):
        gt = make_poses(30, scale=1.0)
        est = make_poses(30, scale=2.0)  # estimated moves twice as fast
        scales = compute_scale_over_time(est, gt, window=5)
        finite = scales[np.isfinite(scales)]
        np.testing.assert_allclose(finite, 2.0, atol=0.01)

    def test_output_length(self):
        gt = make_poses(50)
        scales = compute_scale_over_time(gt, gt, window=10)
        assert len(scales) == 40  # n - window

    def test_none_gt_handled_gracefully(self):
        gt = [None] * 5 + make_poses(25)
        est = make_poses(30)
        scales = compute_scale_over_time(est, gt, window=10)
        assert len(scales) == 20

    def test_stationary_poses_return_nan(self):
        gt = [make_pose(np.eye(3), np.zeros(3)) for _ in range(20)]
        est = [make_pose(np.eye(3), np.zeros(3)) for _ in range(20)]
        scales = compute_scale_over_time(est, gt, window=5)
        # All differences are 0 -> returns NaN
        assert np.all(np.isnan(scales))

