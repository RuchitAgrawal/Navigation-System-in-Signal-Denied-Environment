# tests/test_fundamental.py -- Fundamental matrix unit tests
import numpy as np
import pytest
import cv2
from src.geometry.fundamental import estimate_fundamental, fundamental_to_essential, compute_epipolar_lines

K = np.float64([[481.2, 0, 319.5], [0, 480, 239.5], [0, 0, 1]])

\nclass TestEstimateFundamental:
    def test_returns_none_for_too_few(self):
        pts = np.zeros((5, 2), dtype=np.float32)
        F, mask = estimate_fundamental(pts, pts)
        assert F is None

    def test_shape_on_valid_input(self):
        rng = np.random.default_rng(0)
        pts1 = rng.uniform(100, 400, (30, 2)).astype(np.float32)
        pts2 = pts1 + rng.normal(0, 2, pts1.shape).astype(np.float32)
        F, mask = estimate_fundamental(pts1, pts2, ransac_threshold=3.0)
        if F is not None:
            assert F.shape == (3, 3)

\nclass TestFundamentalToEssential:
    def test_output_shape(self):
        F = np.eye(3, dtype=np.float64)
        E = fundamental_to_essential(F, K)
        assert E.shape == (3, 3)

\nclass TestEpipolarLines:
    def test_output_shape(self):
        F = np.eye(3, dtype=np.float64)
        pts = np.array([[100, 200], [150, 250], [200, 300]], dtype=np.float32)
        lines = compute_epipolar_lines(pts, F, which_image=2)
        assert lines.shape == (3, 3)


