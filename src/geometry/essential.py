"""
essential.py — Essential matrix estimation and pose recovery.

Implements calibrated monocular two-view geometry:
    1. Estimate the essential matrix E from matched point correspondences
       using RANSAC (OpenCV's cv2.findEssentialMat).
    2. Decompose E to recover (R, t) via cv2.recoverPose.
    3. Validate the result and classify failure modes.

Scale note
----------
cv2.recoverPose returns a unit-norm translation vector t. For monocular VO
the absolute translation scale is not recoverable from the Essential matrix
alone. All downstream code must treat ||t|| = 1 as arbitrary scale.

References
----------
- Nister, D. (2004). An efficient solution to the five-point relative pose problem.
  IEEE TPAMI 26(6), 756-770.
- Hartley & Zisserman, MVG, Chapter 9.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np

from src.geometry.transforms import is_valid_rotation


@dataclass
class EssentialResult:
    """Result of Essential matrix estimation and pose recovery."""
    success: bool
    R: Optional[np.ndarray] = None           # (3, 3) rotation
    t: Optional[np.ndarray] = None           # (3,) unit translation direction
    E: Optional[np.ndarray] = None           # (3, 3) essential matrix
    inlier_mask: Optional[np.ndarray] = None # (N,) uint8 mask
    n_inliers: int = 0
    inlier_ratio: float = 0.0
    failure_reason: str = ""


def estimate_pose(
    pts_prev: np.ndarray,
    pts_curr: np.ndarray,
    K: np.ndarray,
    ransac_threshold: float = 1.0,
    ransac_confidence: float = 0.999,
    ransac_max_iter: int = 2000,
    min_inlier_ratio: float = 0.10,
) -> EssentialResult:
    """Estimate relative pose from matched 2-D point correspondences.

    Parameters
    ----------
    pts_prev : (N, 2) float32   Keypoint positions in the previous frame.
    pts_curr : (N, 2) float32   Keypoint positions in the current frame.
    K        : (3, 3) float64   Camera intrinsic matrix.
    ransac_threshold : float    Pixel threshold for RANSAC inlier classification.
    ransac_confidence : float   RANSAC confidence level (0, 1).
    ransac_max_iter : int       Maximum RANSAC iterations.
    min_inlier_ratio : float    Minimum inlier ratio to consider the result valid.

    Returns
    -------
    EssentialResult
    """
    n_pts = len(pts_prev)
    if n_pts < 5:
        return EssentialResult(
            success=False,
            failure_reason=f"Too few correspondences for Essential matrix: {n_pts} < 5",
        )

    try:
        E, mask = cv2.findEssentialMat(
            pts_prev.astype(np.float32),
            pts_curr.astype(np.float32),
            K,
            method=cv2.RANSAC,
            prob=ransac_confidence,
            threshold=ransac_threshold,
            maxIters=ransac_max_iter,
        )
    except cv2.error as e:
        return EssentialResult(success=False, failure_reason=f"findEssentialMat error: {e}")

    if E is None or E.shape != (3, 3):
        return EssentialResult(success=False, failure_reason="findEssentialMat returned None or bad shape")

    if mask is None:
        mask = np.ones((n_pts, 1), dtype=np.uint8)

    inlier_mask = mask.ravel().astype(np.uint8)
    n_inliers = int(inlier_mask.sum())
    inlier_ratio = n_inliers / n_pts if n_pts > 0 else 0.0

    if inlier_ratio < min_inlier_ratio:
        return EssentialResult(
            success=False,
            E=E,
            inlier_mask=inlier_mask,
            n_inliers=n_inliers,
            inlier_ratio=inlier_ratio,
            failure_reason=f"Inlier ratio {inlier_ratio:.3f} < threshold {min_inlier_ratio:.3f}",
        )

    # Recover pose from E
    try:
        n_pos, R, t, pose_mask = cv2.recoverPose(
            E,
            pts_prev.astype(np.float32),
            pts_curr.astype(np.float32),
            K,
            mask=inlier_mask.copy(),
        )
    except cv2.error as e:
        return EssentialResult(
            success=False,
            E=E,
            inlier_mask=inlier_mask,
            n_inliers=n_inliers,
            inlier_ratio=inlier_ratio,
            failure_reason=f"recoverPose error: {e}",
        )

    if R is None or t is None:
        return EssentialResult(
            success=False,
            E=E,
            inlier_mask=inlier_mask,
            n_inliers=n_inliers,
            inlier_ratio=inlier_ratio,
            failure_reason="recoverPose returned None R or t",
        )

    if not is_valid_rotation(R):
        return EssentialResult(
            success=False,
            E=E,
            inlier_mask=inlier_mask,
            n_inliers=n_inliers,
            inlier_ratio=inlier_ratio,
            failure_reason="recoverPose returned invalid rotation matrix",
        )

    return EssentialResult(
        success=True,
        R=R.astype(np.float64),
        t=t.flatten().astype(np.float64),
        E=E,
        inlier_mask=inlier_mask,
        n_inliers=n_inliers,
        inlier_ratio=inlier_ratio,
    )


def build_intrinsic_matrix(fx: float, fy: float, cx: float, cy: float) -> np.ndarray:
    """Construct a 3×3 camera intrinsic matrix K."""
    return np.array([
        [fx, 0.0, cx],
        [0.0, fy, cy],
        [0.0, 0.0, 1.0],
    ], dtype=np.float64)
