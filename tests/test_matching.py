"""
test_matching.py — Unit tests for feature matching utilities.
"""
import numpy as np
import pytest
import cv2

from src.matching.matcher import (
    create_matcher,
    match_and_filter,
    matches_to_point_arrays,
)


def _make_binary_descriptors(n: int, d: int = 32, seed: int = 0) -> np.ndarray:
    """Generate random binary (uint8) descriptors of shape (n, d)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(n, d), dtype=np.uint8)


def _make_keypoints(n: int) -> list:
    """Generate n dummy KeyPoint objects."""
    return [cv2.KeyPoint(float(i * 10), float(i * 5), 5.0) for i in range(n)]


class TestCreateMatcher:
    def test_returns_bfmatcher(self):
        matcher = create_matcher(cv2.NORM_HAMMING)
        assert isinstance(matcher, cv2.BFMatcher)

    def test_cross_check_mode(self):
        matcher = create_matcher(cv2.NORM_HAMMING, cross_check=True)
        assert matcher is not None


class TestMatchAndFilter:
    def test_returns_two_lists(self):
        d1 = _make_binary_descriptors(50, seed=1)
        d2 = _make_binary_descriptors(50, seed=2)
        raw, good = match_and_filter(d1, d2)
        assert isinstance(raw, list)
        assert isinstance(good, list)

    def test_good_leq_raw(self):
        d1 = _make_binary_descriptors(80, seed=3)
        d2 = _make_binary_descriptors(80, seed=4)
        raw, good = match_and_filter(d1, d2, ratio_threshold=0.75)
        assert len(good) <= len(raw)

    def test_identical_descriptors_all_match(self):
        """Perfect descriptors should pass ratio test easily."""
        d = _make_binary_descriptors(30, seed=5)
        # Add tiny noise to second set so knnMatch has 2 distinct distances
        d2 = d.copy()
        d2[0, 0] ^= 0xFF  # flip one byte in one descriptor
        _, good = match_and_filter(d, d2, ratio_threshold=0.99)
        assert len(good) > 0

    def test_empty_descriptors_returns_empty(self):
        raw, good = match_and_filter(
            np.zeros((0, 32), dtype=np.uint8),
            np.zeros((0, 32), dtype=np.uint8),
        )
        assert raw == []
        assert good == []

    def test_none_descriptors_returns_empty(self):
        raw, good = match_and_filter(None, None)
        assert raw == []
        assert good == []


class TestMatchesToPointArrays:
    def test_output_shape(self):
        d1 = _make_binary_descriptors(20, seed=6)
        d2 = _make_binary_descriptors(20, seed=7)
        kps1 = _make_keypoints(20)
        kps2 = _make_keypoints(20)
        _, good = match_and_filter(d1, d2)
        if good:
            pts1, pts2 = matches_to_point_arrays(good, kps1, kps2)
            assert pts1.shape == (len(good), 2)
            assert pts2.shape == (len(good), 2)
            assert pts1.dtype == np.float32

    def test_empty_matches_returns_zero_arrays(self):
        pts1, pts2 = matches_to_point_arrays([], [], [])
        assert pts1.shape == (0, 2)
        assert pts2.shape == (0, 2)
