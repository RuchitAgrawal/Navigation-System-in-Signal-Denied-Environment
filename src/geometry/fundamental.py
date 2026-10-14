"""
src/geometry/fundamental.py — Fundamental matrix utilities.

The Fundamental matrix F relates corresponding points in two uncalibrated views:
    x'^T F x = 0

The Essential matrix E is the calibrated version:
    E = K'^T F K

This module provides:
1. Fundamental matrix estimation via RANSAC.
2. Conversion between F and E.
3. Epipolar line visualization utility.

Usage in this pipeline
----------------------
The main VO loop uses the Essential matrix directly (calibrated cameras).
Fundamental matrix estimation is provided here for:
- Cross-validation with Essential matrix.
- Experiments without known intrinsics (uncalibrated case).
- Visualization of epipolar geometry.

References
----------
- Hartley & Zisserman, MVG, Chapter 11.
- OpenCV: cv2.findFundamentalMat documentation.
"""

from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np


def estimate_fundamental(
    pts_prev: np.ndarray,
    pts_curr: np.ndarray,
    ransac_threshold: float = 1.0,
    confidence: float = 0.999,
    method: int = cv2.FM_RANSAC,
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Estimate Fundamental matrix from 2-D point correspondences.

    Parameters
    ----------
    pts_prev : (N, 2) float32   Points in previous frame.
    pts_curr : (N, 2) float32   Points in current frame.
    ransac_threshold : float     Pixel distance threshold for inlier classification.
    confidence : float           RANSAC confidence.
    method : int                 cv2.FM_RANSAC | cv2.FM_LMEDS | cv2.FM_8POINT.

    Returns
    -------
    F    : (3, 3) float64 Fundamental matrix, or None.
    mask : (N,)   uint8   Inlier mask, or None.
    """
    if len(pts_prev) < 8:
        return None, None

    F, mask = cv2.findFundamentalMat(
        pts_prev.astype(np.float32),
        pts_curr.astype(np.float32),
        method,
        ransacReprojThreshold=ransac_threshold,
        confidence=confidence,
    )
    if F is None:
        return None, None
    if mask is not None:
        mask = mask.ravel().astype(np.uint8)
    return F, mask


def fundamental_to_essential(
    F: np.ndarray,
    K: np.ndarray,
) -> np.ndarray:
    """Convert Fundamental matrix to Essential matrix.

    E = K^T @ F @ K
    """
    return K.T @ F @ K


def compute_epipolar_lines(
    pts: np.ndarray,
    F: np.ndarray,
    which_image: int = 2,
) -> np.ndarray:
    """Compute epipolar lines in one image for points in the other.

    Parameters
    ----------
    pts         : (N, 2) float32   Points in image 1 (if which_image=2) or image 2.
    F           : (3, 3) float64   Fundamental matrix.
    which_image : int   1 or 2. If 2, compute lines in image 2 for points in image 1.

    Returns
    -------
    lines : (N, 3) float64   Epipolar lines ax + by + c = 0.
    """
    pts_h = np.hstack([pts, np.ones((len(pts), 1))]).astype(np.float64)
    if which_image == 2:
        return (F @ pts_h.T).T
    else:
        return (F.T @ pts_h.T).T
