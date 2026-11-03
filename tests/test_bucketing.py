"""
tests/test_bucketing.py — Unit tests for spatial keypoint bucketing algorithms.
"""

import cv2
import numpy as np
import pytest
from src.features.bucketing import QuadtreeNode, distribute_quadtree, distribute_grid


class TestQuadtreeNode:
    def test_node_contains(self):
        node = QuadtreeNode(0.0, 0.0, 100.0, 100.0)
        assert node.contains((50.0, 50.0))
        assert not node.contains((150.0, 50.0))

    def test_node_divide_creates_quadrants(self):
        node = QuadtreeNode(0.0, 0.0, 100.0, 100.0)
        node.keypoints = [
            cv2.KeyPoint(x=25.0, y=25.0, size=1.0),
            cv2.KeyPoint(x=75.0, y=25.0, size=1.0),
            cv2.KeyPoint(x=25.0, y=75.0, size=1.0),
            cv2.KeyPoint(x=75.0, y=75.0, size=1.0),
        ]
        children = node.divide()
        assert len(children) == 4
        assert not node.is_leaf


class TestDistributeQuadtree:
    def test_empty_keypoints_returns_empty(self):
        result = distribute_quadtree([], width=640, height=480, max_features=100)
        assert len(result) == 0

    def test_fewer_than_max_returns_all(self):
        kps = [cv2.KeyPoint(x=float(i * 10), y=50.0, size=1.0) for i in range(10)]
        result = distribute_quadtree(kps, width=640, height=480, max_features=50)
        assert len(result) == 10

    def test_distribute_caps_at_max_features(self):
        rng = np.random.default_rng(42)
        kps = [
            cv2.KeyPoint(
                x=float(rng.uniform(0, 640)),
                y=float(rng.uniform(0, 480)),
                size=1.0,
                response=float(rng.uniform(1, 100)),
            )
            for _ in range(500)
        ]
        result = distribute_quadtree(kps, width=640, height=480, max_features=100)
        assert len(result) == 100

    def test_distributes_across_quadrants(self):
        # Cluster 200 points in top-left, 10 points in bottom-right
        kps = [
            cv2.KeyPoint(x=float(i % 100), y=float(i % 100), size=1.0, response=10.0)
            for i in range(200)
        ]
        kps += [
            cv2.KeyPoint(x=float(500 + i * 5), y=float(400 + i * 5), size=1.0, response=10.0)
            for i in range(10)
        ]
        result = distribute_quadtree(kps, width=640, height=480, max_features=20)
        # Bottom right points must still be represented
        br_points = [kp for kp in result if kp.pt[0] > 320 and kp.pt[1] > 240]
        assert len(br_points) > 0


class TestDistributeGrid:
    def test_grid_bucketing_distributes_across_cells(self):
        rng = np.random.default_rng(123)
        kps = [
            cv2.KeyPoint(
                x=float(rng.uniform(0, 640)),
                y=float(rng.uniform(0, 480)),
                size=1.0,
                response=float(rng.uniform(1, 100)),
            )
            for _ in range(300)
        ]
        result = distribute_grid(kps, width=640, height=480, n_buckets_x=3, n_buckets_y=2, max_features=60)
        assert len(result) == 60

