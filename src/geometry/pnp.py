"""
pnp.py — Perspective-n-Point (PnP) pose estimation using RGB-D data.

Provides:
1. 3D point back-projection from 2D keypoints and depth maps.
2. PnP RANSAC pose solver (cv2.solvePnPRansac) delivering true metric scale.
3. Hybrid solver falling back to Monocular Essential Matrix when depth is invalid.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import cv2
import numpy as np

from src.geometry.essential import estimate_pose as estimate_pose_essential, PoseResult


@dataclass
class PnPResult:
    """Result of PnP pose estimation."""
    R: Optional[np.ndarray]           # (3, 3) rotation from prev to curr camera
    t: Optional[np.ndarray]           # (3, 1) translation direction / metric vector
    inlier_mask: Optional[np.ndarray] # (N,) uint8 inlier mask (1=inlier, 0=outlier)
    n_inliers: int
    inlier_ratio: float
    is_metric: bool                   # True if solved via metric PnP, False if unit Essential fallback
    mode: str                         # 'pnp' or 'essential_fallback'


def backproject_2d_to_3d(
    pts_2d: np.ndarray,
    depth_image: np.ndarray,
    K: np.ndarray,
    depth_scale: float = 1.0,
    min_depth: float = 0.2,
    max_depth: float = 10.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Back-project 2D keypoint coordinates to 3D metric coordinates using a depth map.

    Parameters
    ----------
    pts_2d : (N, 2) float32
        2D image pixel coordinates (u, v).
    depth_image : (H, W) ndarray
        Registered depth image (float in meters, or uint16 with depth_scale).
    K : (3, 3) ndarray
        Camera intrinsic matrix.
    depth_scale : float
        Multiplier to convert raw depth pixel values to meters (e.g. 1/5000 for TUM).
    min_depth, max_depth : float
        Valid sensor depth range in meters.

    Returns
    -------
    pts_3d : (N, 3) float64
        3D coordinates in the previous camera frame.
    valid_mask : (N,) bool
        Boolean mask indicating which points had valid, non-zero depth within bounds.
    """
    n_pts = len(pts_2d)
    pts_3d = np.zeros((n_pts, 3), dtype=np.float64)
    valid_mask = np.zeros(n_pts, dtype=bool)

    if n_pts == 0 or depth_image is None:
        return pts_3d, valid_mask

    h, w = depth_image.shape[:2]
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    for i, (u, v) in enumerate(pts_2d):
        u_int = int(round(u))
        v_int = int(round(v))

        if 0 <= u_int < w and 0 <= v_int < h:
            d_raw = depth_image[v_int, u_int]
            z = float(d_raw) * depth_scale

            if min_depth <= z <= max_depth and not np.isnan(z) and not np.isinf(z):
                pts_3d[i, 0] = (u - cx) * z / fx
                pts_3d[i, 1] = (v - cy) * z / fy
                pts_3d[i, 2] = z
                valid_mask[i] = True

    return pts_3d, valid_mask
