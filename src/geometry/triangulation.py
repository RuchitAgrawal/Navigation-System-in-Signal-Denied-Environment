"""
src/geometry/triangulation.py â€” Optional 3-D point triangulation helper.

Provides triangulation of matched point pairs from two camera views.
This is NOT used in the main VO pipeline (which uses Essential matrix only)
but is useful for:
1. Visualizing 3-D structure.
2. Computing metric scale if a known baseline is available.
3. Future extensions with sliding-window BA.

Scale note
----------
For monocular VO, triangulated points are in an arbitrary coordinate system
with unit baseline ||t||=1 (from recoverPose). Absolute metric scale is
not recoverable without additional constraints (e.g., known object size,
stereo baseline, or depth sensor).
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np


def triangulate_points(
    pts_prev: np.ndarray,
    pts_curr: np.ndarray,
    K: np.ndarray,
    R: np.ndarray,
    t: np.ndarray,
) -> Optional[np.ndarray]:
    """Triangulate 3-D points from two calibrated views.

    Parameters
    ----------
    pts_prev : (N, 2) float32   2-D points in the previous (reference) frame.
    pts_curr : (N, 2) float32   2-D points in the current frame.
    K        : (3, 3) float64   Camera intrinsic matrix.
    R        : (3, 3) float64   Rotation from prev to curr camera frame.
    t        : (3,)   float64   Translation direction (unit norm, scale ambiguous).

    Returns
    -------
    pts_3d : (N, 3) float64   Triangulated 3-D points in prev-camera frame,
             or None if triangulation fails.

    Notes
    -----
    Only points with positive depth (z > 0 in both cameras) are physically
    meaningful. Filter by cheirality before using the output.
    """
    if len(pts_prev) < 4 or len(pts_curr) < 4:
        return None

    # Build projection matrices P1 = K[I|0], P2 = K[R|t]
    P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
    P2 = K @ np.hstack([R, t.reshape(3, 1)])

    pts_4d = cv2.triangulatePoints(
        P1.astype(np.float64),
        P2.astype(np.float64),
        pts_prev.T.astype(np.float64),
        pts_curr.T.astype(np.float64),
    )   # (4, N) homogeneous

    # Convert to Euclidean
    w = pts_4d[3]
    if np.any(np.abs(w) < 1e-9):
        return None

    pts_3d = (pts_4d[:3] / w).T   # (N, 3)
    return pts_3d


def count_positive_depth(
    pts_3d: np.ndarray,
    R: np.ndarray,
    t: np.ndarray,
) -> int:
    """Count points with positive depth in both camera views (cheirality check).

    Parameters
    ----------
    pts_3d : (N, 3) float64  Points in the reference (prev) camera frame.
    R      : (3, 3) float64  Rotation prevâ†’curr.
    t      : (3,)   float64  Translation prevâ†’curr.

    Returns
    -------
    int  Number of points visible from both cameras.
    """
    # Depth in reference camera
    depth_ref = pts_3d[:, 2]

    # Transform to current camera frame
    pts_curr = (R @ pts_3d.T).T + t
    depth_curr = pts_curr[:, 2]

    return int(np.sum((depth_ref > 0) & (depth_curr > 0)))

