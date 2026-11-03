"""
subpixel.py — Sub-pixel corner coordinate refinement utility.

Applies cv2.cornerSubPix to detected keypoints, refining their coordinates
from discrete integer pixels to sub-pixel precision. This reduces angular
reprojection error and improves trajectory estimation accuracy.
"""

from __future__ import annotations
from typing import List, Tuple
import cv2
import numpy as np


def refine_keypoints_subpixel(
    image: np.ndarray,
    keypoints: List[cv2.KeyPoint],
    win_size: Tuple[int, int] = (5, 5),
    zero_zone: Tuple[int, int] = (-1, -1),
    max_iters: int = 30,
    epsilon: float = 0.01,
) -> List[cv2.KeyPoint]:
    """Refine keypoint positions to sub-pixel accuracy using gradient analysis.

    Parameters
    ----------
    image : np.ndarray
        Grayscale input image (uint8).
    keypoints : List[cv2.KeyPoint]
        Keypoints detected at integer coordinates.
    win_size : Tuple[int, int]
        Half-dimensions of the sub-pixel search window.
    zero_zone : Tuple[int, int]
        Half-dimensions of the dead zone at the window center (-1, -1 to disable).
    max_iters : int
        Maximum refinement iterations.
    epsilon : float
        Convergence threshold.

    Returns
    -------
    List[cv2.KeyPoint]
        Keypoints with sub-pixel refined coordinates.
    """
    if not keypoints:
        return []

    # Ensure grayscale 8-bit image
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Extract coordinates as (N, 1, 2) float32 array
    coords = np.array([[kp.pt[0], kp.pt[1]] for kp in keypoints], dtype=np.float32).reshape(-1, 1, 2)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iters, epsilon)
    refined_coords = cv2.cornerSubPix(gray, coords, win_size, zero_zone, criteria)

    # Construct refined KeyPoint objects preserving octave, response, and angle
    refined_keypoints: List[cv2.KeyPoint] = []
    for i, kp in enumerate(keypoints):
        rx, ry = float(refined_coords[i, 0, 0]), float(refined_coords[i, 0, 1])
        new_kp = cv2.KeyPoint(
            x=rx,
            y=ry,
            size=kp.size,
            angle=kp.angle,
            response=kp.response,
            octave=kp.octave,
            class_id=kp.class_id,
        )
        refined_keypoints.append(new_kp)

    return refined_keypoints

