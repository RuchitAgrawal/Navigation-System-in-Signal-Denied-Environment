"""
matcher.py — Feature matching with Lowe ratio filtering and cross-check support.

All supported descriptor types in this pipeline are binary (BRIEF, ORB, BRISK),
so Hamming distance is always used.

Matching strategy
-----------------
1. BFMatcher with Hamming distance.
2. knnMatch(k=2) for Lowe ratio test (default, recommended).
   OR crossCheck=True BFMatcher for strict bidirectional matching.
3. Optional minimum match count guard.

Reference
---------
Lowe, D.G. (2004). Distinctive image features from scale-invariant keypoints.
International Journal of Computer Vision, 60(2), 91–110.
"""

from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


def create_matcher(norm_type: int = cv2.NORM_HAMMING,
                   cross_check: bool = False) -> cv2.BFMatcher:
    """Create a brute-force matcher.

    Parameters
    ----------
    norm_type   : int   cv2.NORM_HAMMING for binary descriptors.
    cross_check : bool  Enable strict bidirectional matching.
                        Mutually exclusive with ratio filtering.
    """
    return cv2.BFMatcher(norm_type, crossCheck=cross_check)


def match_and_filter(
    desc_prev: np.ndarray,
    desc_curr: np.ndarray,
    norm_type: int = cv2.NORM_HAMMING,
    ratio_threshold: float = 0.75,
    cross_check: bool = False,
) -> Tuple[List[cv2.DMatch], List[cv2.DMatch]]:
    """Match descriptors and apply quality filtering.

    Parameters
    ----------
    desc_prev : (N, D) uint8   Descriptors from the previous frame.
    desc_curr : (M, D) uint8   Descriptors from the current frame.
    norm_type : int             Distance norm (cv2.NORM_HAMMING).
    ratio_threshold : float     Lowe ratio test threshold (0.0–1.0).
    cross_check : bool          Use cross-check instead of ratio test.

    Returns
    -------
    raw_matches : list of cv2.DMatch      All candidate matches.
    good_matches : list of cv2.DMatch     Matches passing the filter.
    """
    if desc_prev is None or desc_curr is None:
        return [], []
    if len(desc_prev) == 0 or len(desc_curr) == 0:
        return [], []

    if cross_check:
        matcher = create_matcher(norm_type, cross_check=True)
        raw = matcher.match(desc_prev, desc_curr)
        return list(raw), list(raw)  # cross-check is self-filtering

    # Ratio test (Lowe 2004)
    matcher = create_matcher(norm_type, cross_check=False)
    knn = matcher.knnMatch(desc_prev, desc_curr, k=2)

    raw_matches = [m for pair in knn for m in pair]

    good_matches: List[cv2.DMatch] = []
    for pair in knn:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < ratio_threshold * n.distance:
            good_matches.append(m)

    return raw_matches, good_matches


def matches_to_point_arrays(
    matches: List[cv2.DMatch],
    kps_prev: List[cv2.KeyPoint],
    kps_curr: List[cv2.KeyPoint],
) -> Tuple[np.ndarray, np.ndarray]:
    """Extract (N, 2) float32 point arrays from a list of DMatch objects.

    Parameters
    ----------
    matches  : list of cv2.DMatch
    kps_prev : list of cv2.KeyPoint   from the previous frame
    kps_curr : list of cv2.KeyPoint   from the current frame

    Returns
    -------
    pts_prev : (N, 2) float32
    pts_curr : (N, 2) float32
    """
    if not matches:
        return np.zeros((0, 2), dtype=np.float32), np.zeros((0, 2), dtype=np.float32)

    pts_prev = np.array([kps_prev[m.queryIdx].pt for m in matches],
                        dtype=np.float32)
    pts_curr = np.array([kps_curr[m.trainIdx].pt for m in matches],
                        dtype=np.float32)
    return pts_prev, pts_curr
