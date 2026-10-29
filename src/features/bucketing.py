"""
bucketing.py — Spatial keypoint distribution and bucketing algorithms.

Provides:
1. Recursive Quadtree spatial bucketer (ORB-SLAM2 style) for optimal uniform distribution.
2. Grid bucketer (Perez-Grau 2017 style) dividing the image into fixed NxM buckets.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import cv2
import numpy as np


@dataclass
class QuadtreeNode:
    """A node in the spatial partitioning Quadtree."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    keypoints: List[cv2.KeyPoint] = field(default_factory=list)
    children: List["QuadtreeNode"] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def n_points(self) -> int:
        return len(self.keypoints)

    def contains(self, pt: Tuple[float, float]) -> bool:
        x, y = pt
        return (self.x_min <= x < self.x_max) and (self.y_min <= y < self.y_max)
