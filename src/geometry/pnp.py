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

from src.geometry.essential import estimate_pose as estimate_pose_essential, EssentialResult


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


def estimate_pose_pnp(
    pts_3d_prev: np.ndarray,
    pts_2d_curr: np.ndarray,
    K: np.ndarray,
    dist_coeffs: Optional[np.ndarray] = None,
    ransac_threshold: float = 2.0,
    confidence: float = 0.999,
    max_iter: int = 2000,
    min_inlier_ratio: float = 0.20,
) -> PnPResult:
    """Estimate metric camera pose from 3D-to-2D correspondences using PnP RANSAC.

    Parameters
    ----------
    pts_3d_prev : (N, 3) float64
        3D point coordinates in the previous camera frame.
    pts_2d_curr : (N, 2) float32
        Projected 2D pixel coordinates in the current camera frame.
    K : (3, 3) ndarray
        Camera intrinsics matrix.
    dist_coeffs : Optional ndarray
        Lens distortion coefficients (None for rectified/synthetic data).
    ransac_threshold : float
        RANSAC pixel reprojection error threshold.
    confidence : float
        RANSAC confidence level.
    max_iter : int
        Maximum RANSAC iterations.
    min_inlier_ratio : float
        Minimum inlier ratio required to accept the pose.

    Returns
    -------
    PnPResult
    """
    n = len(pts_3d_prev)
    if n < 6:
        return PnPResult(None, None, None, 0, 0.0, False, "pnp_insufficient_points")

    if dist_coeffs is None:
        dist_coeffs = np.zeros(4, dtype=np.float64)

    success, rvec, tvec, inliers = cv2.solvePnPRansac(
        objectPoints=pts_3d_prev.astype(np.float64),
        imagePoints=pts_2d_curr.astype(np.float64),
        cameraMatrix=K.astype(np.float64),
        distCoeffs=dist_coeffs,
        reprojectionError=float(ransac_threshold),
        confidence=float(confidence),
        iterationsCount=int(max_iter),
        flags=cv2.SOLVEPNP_EPNP,
    )

    if not success or inliers is None:
        return PnPResult(None, None, None, 0, 0.0, False, "pnp_failed")

    inlier_indices = inliers.flatten()
    n_inliers = len(inlier_indices)
    inlier_ratio = n_inliers / float(n)

    if inlier_ratio < min_inlier_ratio or n_inliers < 6:
        return PnPResult(None, None, None, n_inliers, inlier_ratio, False, "pnp_low_inliers")

    inlier_mask = np.zeros(n, dtype=np.uint8)
    inlier_mask[inlier_indices] = 1

    R_rel, _ = cv2.Rodrigues(rvec)
    t_rel = tvec.reshape(3, 1)

    return PnPResult(
        R=R_rel,
        t=t_rel,
        inlier_mask=inlier_mask,
        n_inliers=n_inliers,
        inlier_ratio=inlier_ratio,
        is_metric=True,
        mode="pnp",
    )


def hybrid_estimate_pose(
    pts_prev: np.ndarray,
    pts_curr: np.ndarray,
    K: np.ndarray,
    depth_prev: Optional[np.ndarray] = None,
    depth_scale: float = 1.0,
    ransac_threshold: float = 2.0,
    min_depth_inliers: int = 10,
) -> PnPResult:
    """Hybrid motion solver: attempts metric PnP, falls back to Essential matrix.

    Parameters
    ----------
    pts_prev, pts_curr : (N, 2) float32
        Matched 2D point arrays.
    K : (3, 3) ndarray
        Camera intrinsic matrix.
    depth_prev : Optional[np.ndarray]
        Registered depth image for the previous frame.
    depth_scale : float
        Depth units to meters scale factor.
    ransac_threshold : float
        RANSAC pixel error threshold.
    min_depth_inliers : int
        Minimum PnP inliers required to accept metric pose.

    Returns
    -------
    PnPResult
    """
    n = len(pts_prev)
    if n < 8:
        return PnPResult(None, None, None, 0, 0.0, False, "failed_insufficient_matches")

    # 1. Attempt metric PnP if depth is available
    if depth_prev is not None:
        pts_3d_prev, valid_depth = backproject_2d_to_3d(pts_prev, depth_prev, K, depth_scale=depth_scale)
        n_valid = int(valid_depth.sum())

        if n_valid >= min_depth_inliers:
            pnp_res = estimate_pose_pnp(
                pts_3d_prev[valid_depth],
                pts_curr[valid_depth],
                K,
                ransac_threshold=ransac_threshold,
            )
            if pnp_res.R is not None and pnp_res.n_inliers >= min_depth_inliers:
                full_mask = np.zeros(n, dtype=np.uint8)
                valid_idx = np.where(valid_depth)[0]
                if pnp_res.inlier_mask is not None:
                    full_mask[valid_idx[pnp_res.inlier_mask == 1]] = 1
                pnp_res.inlier_mask = full_mask
                return pnp_res

    # 2. Fallback to monocular Essential matrix decomposition
    ess_res: EssentialResult = estimate_pose_essential(pts_prev, pts_curr, K, ransac_threshold=ransac_threshold)
    return PnPResult(
        R=ess_res.R,
        t=ess_res.t,
        inlier_mask=ess_res.inlier_mask,
        n_inliers=ess_res.n_inliers,
        inlier_ratio=ess_res.inlier_ratio,
        is_metric=False,
        mode="essential_fallback",
    )
