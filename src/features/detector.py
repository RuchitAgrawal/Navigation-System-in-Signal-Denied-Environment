"""
detector.py — Feature detector factory.

Supported detectors
-------------------
* FAST  — Features from Accelerated Segment Test (Rosten & Drummond, 2006).
           Configured via cv2.FastFeatureDetector_create.
           Not rotation-invariant; no scale pyramid.

* ORB   — Oriented FAST and Rotated BRIEF (Rublee et al., 2011).
           Configured via cv2.ORB_create.
           Rotation-invariant due to keypoint orientation assignment.

FASTER note
-----------
FASTER (Rosten, Porter & Drummond, 2010) selects the FAST threshold using
a machine-learning approach on training images. It is not exposed as a
standalone detector in the standard OpenCV Python package. Implementing it
correctly requires training-data-driven threshold selection and is therefore
left as a future extension. Do not alias FAST as FASTER.
"""

from __future__ import annotations

from typing import List

import cv2
import numpy as np


def create_detector(config: dict) -> cv2.Feature2D:
    """Instantiate a feature detector from a configuration dictionary.

    Parameters
    ----------
    config : dict
        Must contain ``name`` (str). Additional keys are detector-specific.

    Returns
    -------
    detector : cv2.Feature2D compatible object

    Raises
    ------
    ValueError
        If the detector name is unknown or not supported.
    """
    name = config.get("name", "").upper()

    if name == "FAST":
        threshold = int(config.get("threshold", 20))
        nonmax = bool(config.get("nonmax_suppression", True))
        detector = cv2.FastFeatureDetector_create(
            threshold=threshold,
            nonmaxSuppression=nonmax,
        )
        # Wrap FAST so we can limit max keypoints (FAST has no built-in limit)
        max_kp = int(config.get("max_keypoints", 2000))
        return _LimitedDetector(detector, max_kp)

    elif name == "ORB":
        nfeatures = int(config.get("nfeatures", config.get("max_keypoints", 2000)))
        scale_factor = float(config.get("scale_factor", 1.2))
        nlevels = int(config.get("nlevels", 8))
        edge_threshold = int(config.get("edge_threshold", 31))
        first_level = int(config.get("first_level", 0))
        wta_k = int(config.get("wta_k", 2))
        patch_size = int(config.get("patch_size", 31))
        fast_threshold = int(config.get("fast_threshold", 20))
        return cv2.ORB_create(
            nfeatures=nfeatures,
            scaleFactor=scale_factor,
            nlevels=nlevels,
            edgeThreshold=edge_threshold,
            firstLevel=first_level,
            WTA_K=wta_k,
            patchSize=patch_size,
            fastThreshold=fast_threshold,
        )

    elif name == "FASTER":
        raise NotImplementedError(
            "FASTER detector is not implemented in this version. "
            "FASTER requires machine-learning threshold selection on training data "
            "and is not equivalent to FAST with a renamed threshold. "
            "See docs/hso_comparison.md for future extension notes."
        )

    else:
        raise ValueError(
            f"Unknown detector: '{name}'. "
            "Supported detectors: FAST, ORB. (FASTER: future extension)"
        )


class _LimitedDetector:
    """Wraps a cv2.Feature2D detector to cap the number of returned keypoints.

    FAST does not support an ``nfeatures`` parameter natively. This wrapper
    retains only the strongest ``max_keypoints`` by response value.
    """

    def __init__(self, detector: cv2.Feature2D, max_keypoints: int) -> None:
        self._detector = detector
        self._max_kp = max_keypoints

    def detect(self, image: np.ndarray, mask=None) -> List[cv2.KeyPoint]:
        kps = self._detector.detect(image, mask)
        if len(kps) > self._max_kp:
            kps = sorted(kps, key=lambda k: k.response, reverse=True)
            kps = kps[: self._max_kp]
        return kps

    def detectAndCompute(self, image: np.ndarray, mask=None):
        kps = self.detect(image, mask)
        return kps, None  # No descriptors from a pure detector

    # Delegate attribute access so it behaves like a cv2.Feature2D
    def __getattr__(self, name):
        return getattr(self._detector, name)
