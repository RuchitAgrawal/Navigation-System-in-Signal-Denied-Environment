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

    def divide(self) -> List["QuadtreeNode"]:
        """Subdivide node into four equal quadrants and distribute points."""
        x_mid = (self.x_min + self.x_max) / 2.0
        y_mid = (self.y_min + self.y_max) / 2.0

        q_nw = QuadtreeNode(self.x_min, self.y_min, x_mid, y_mid)
        q_ne = QuadtreeNode(x_mid, self.y_min, self.x_max, y_mid)
        q_sw = QuadtreeNode(self.x_min, y_mid, x_mid, self.y_max)
        q_se = QuadtreeNode(x_mid, y_mid, self.x_max, self.y_max)

        for kp in self.keypoints:
            x, y = kp.pt
            if x < x_mid:
                if y < y_mid:
                    q_nw.keypoints.append(kp)
                else:
                    q_sw.keypoints.append(kp)
            else:
                if y < y_mid:
                    q_ne.keypoints.append(kp)
                else:
                    q_se.keypoints.append(kp)

        non_empty = [q for q in [q_nw, q_ne, q_sw, q_se] if q.n_points > 0]
        self.children = non_empty
        return non_empty


def distribute_quadtree(
    keypoints: List[cv2.KeyPoint],
    width: int,
    height: int,
    max_features: int = 2000,
    min_cell_size: float = 12.0,
) -> List[cv2.KeyPoint]:
    """Distribute keypoints uniformly across the image using a recursive Quadtree.

    Parameters
    ----------
    keypoints : List[cv2.KeyPoint]
        Initial pool of detected keypoints.
    width, height : int
        Dimensions of the image frame.
    max_features : int
        Maximum number of distributed keypoints to retain.
    min_cell_size : float
        Smallest allowable node width/height before stopping subdivision.

    Returns
    -------
    List[cv2.KeyPoint]
        Uniformly distributed subset of keypoints with highest local response.
    """
    if len(keypoints) <= max_features:
        return keypoints

    # 1. Initialize root node with all keypoints
    root = QuadtreeNode(0.0, 0.0, float(width), float(height), list(keypoints))
    active_nodes = [root]

    # 2. Iteratively divide nodes until we reach target count or minimum cell size
    while len(active_nodes) < max_features:
        divided_any = False
        new_active = []

        # Sort nodes by number of points descending so dense nodes are divided first
        active_nodes.sort(key=lambda n: n.n_points, reverse=True)

        for node in active_nodes:
            cell_w = node.x_max - node.x_min
            cell_h = node.y_max - node.y_min

            if (
                len(new_active) + len(active_nodes) - active_nodes.index(node) <= max_features
                and node.n_points > 1
                and cell_w > min_cell_size * 2
                and cell_h > min_cell_size * 2
            ):
                children = node.divide()
                if children:
                    new_active.extend(children)
                    divided_any = True
                else:
                    new_active.append(node)
            else:
                new_active.append(node)

        active_nodes = new_active
        if not divided_any or len(active_nodes) >= max_features:
            break

    # 3. For each leaf node, select the single keypoint with highest response score
    selected: List[cv2.KeyPoint] = []
    for node in active_nodes:
        if node.keypoints:
            best_kp = max(node.keypoints, key=lambda kp: kp.response)
            selected.append(best_kp)
            if len(selected) >= max_features:
                break

    # 4. If we still have capacity, fill with remaining highest-response points
    if len(selected) < max_features:
        selected_set = {id(kp) for kp in selected}
        remaining = [kp for kp in keypoints if id(kp) not in selected_set]
        remaining.sort(key=lambda kp: kp.response, reverse=True)
        selected.extend(remaining[: max_features - len(selected)])

    return selected
