"""
descriptor.py — Feature descriptor factory.

Supported descriptors
---------------------
* BRIEF  — Binary Robust Independent Elementary Features (Calonder et al., 2010).
            NOT rotation-invariant by design.
            Preferred source: cv2.xfeatures2d.BriefDescriptorExtractor_create()
            Fallback: ManualBRIEF (Gaussian-sampled pairs, documented below).

* ORB    — Oriented FAST and Rotated BRIEF (Rublee et al., 2011).
            Rotation-invariant (keypoint orientation assigned by intensity centroid).
            Implemented via cv2.ORB_create().

* BRISK  — Binary Robust Invariant Scalable Keypoints (Leutenegger et al., 2011).
            Scale- and rotation-invariant binary descriptor.
            Implemented via cv2.BRISK_create().

BRIEF availability note
-----------------------
BRIEF via ``cv2.xfeatures2d`` requires ``opencv-contrib-python``. If this
package is not installed, this module automatically falls back to
``ManualBRIEF``, which is a genuine implementation of the Calonder et al.
sampling scheme (256 binary tests, Gaussian sampling pattern, no orientation).
This fallback is labeled clearly in logs and result tables; it is NOT
equivalent to ORB.
"""

from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Manual BRIEF implementation (fallback when contrib is unavailable)
# ---------------------------------------------------------------------------

class ManualBRIEF:
    """Pure-NumPy BRIEF descriptor extractor.

    Implements the Gaussian-sampled test-pair scheme from:
        Calonder, M., et al. (2010). BRIEF: Binary Robust Independent
        Elementary Features. ECCV 2010.

    Properties
    ----------
    - 256 binary tests → 32-byte descriptor
    - Pairs sampled from N(0, s²/25) where s = patch_size
    - NOT rotation-invariant (axis-aligned patch, no orientation correction)
    - Hamming distance should be used for matching

    Parameters
    ----------
    bytes_ : int   Descriptor length in bytes (default 32 → 256 tests).
    patch_size : int  Pixel radius of the sampling patch (default 48).
    seed : int   Random seed for reproducible pair sampling.
    """

    _IMPLEMENTATION = "ManualBRIEF-Gaussian-256"

    def __init__(self, bytes_: int = 32, patch_size: int = 48, seed: int = 42) -> None:
        self.bytes_ = bytes_
        self.n_tests = bytes_ * 8          # 256 for 32 bytes
        self.patch_size = patch_size
        rng = np.random.default_rng(seed)
        sigma = patch_size / 5.0
        # Sample n_tests pairs of (x1, y1) and (x2, y2)
        pts = rng.normal(0, sigma, size=(4, self.n_tests))
        pts = np.clip(pts, -patch_size // 2, patch_size // 2).astype(np.int32)
        self.x1 = pts[0]
        self.y1 = pts[1]
        self.x2 = pts[2]
        self.y2 = pts[3]

    def compute(
        self,
        image: np.ndarray,
        keypoints: List[cv2.KeyPoint],
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Compute BRIEF descriptors for a list of keypoints.

        Parameters
        ----------
        image : (H, W) uint8 greyscale image.
        keypoints : list of cv2.KeyPoint

        Returns
        -------
        valid_kps : list of cv2.KeyPoint  (keypoints near borders are dropped)
        descriptors : (N, bytes_) uint8 ndarray
        """
        if len(keypoints) == 0:
            return [], np.zeros((0, self.bytes_), dtype=np.uint8)

        H, W = image.shape[:2]
        half = self.patch_size // 2

        valid_kps = []
        desc_list = []

        for kp in keypoints:
            cx, cy = int(round(kp.pt[0])), int(round(kp.pt[1]))
            # Reject keypoints too close to the border
            if (cx - half < 0 or cx + half >= W or
                    cy - half < 0 or cy + half >= H):
                continue

            # Extract patch
            patch = image[cy - half: cy + half + 1,
                          cx - half: cx + half + 1].astype(np.int16)

            # Apply 256 binary tests
            p1_vals = patch[self.y1 + half, self.x1 + half]
            p2_vals = patch[self.y2 + half, self.x2 + half]
            bits = (p1_vals < p2_vals).astype(np.uint8)

            # Pack bits into bytes
            desc = np.packbits(bits).astype(np.uint8)
            desc_list.append(desc)
            valid_kps.append(kp)

        if not desc_list:
            return [], np.zeros((0, self.bytes_), dtype=np.uint8)

        return valid_kps, np.stack(desc_list, axis=0)

    def detectAndCompute(self, image, mask=None):
        """Not supported — BRIEF is a descriptor-only extractor."""
        raise NotImplementedError("ManualBRIEF is a descriptor only. Use detect() separately.")


# ---------------------------------------------------------------------------
# Descriptor factory
# ---------------------------------------------------------------------------

def create_descriptor(config: dict):
    """Instantiate a descriptor extractor from a configuration dictionary.

    Parameters
    ----------
    config : dict
        Must contain ``name`` (str). Additional keys are descriptor-specific.

    Returns
    -------
    extractor : cv2.Feature2D or ManualBRIEF

    Raises
    ------
    ValueError
        If the descriptor name is unknown or incompatible.
    """
    name = config.get("name", "").upper()

    if name == "BRIEF":
        bytes_ = int(config.get("bytes", 32))
        # Try contrib first
        try:
            extractor = cv2.xfeatures2d.BriefDescriptorExtractor_create(
                bytes=bytes_,
                use_orientation=bool(config.get("use_orientation", False)),
            )
            extractor._implementation = "BRIEF-xfeatures2d"
            return extractor
        except (AttributeError, cv2.error):
            # Fallback to genuine manual implementation
            import warnings
            warnings.warn(
                "opencv-contrib-python not available. Falling back to ManualBRIEF "
                "(genuine Gaussian-sampled BRIEF, not rotation-invariant). "
                "Results will be labeled 'ManualBRIEF' in output tables.",
                RuntimeWarning,
                stacklevel=2,
            )
            return ManualBRIEF(bytes_=bytes_)

    elif name == "ORB":
        nfeatures = int(config.get("nfeatures", config.get("max_keypoints", 2000)))
        return cv2.ORB_create(nfeatures=nfeatures)

    elif name == "BRISK":
        thresh = int(config.get("thresh", 30))
        octaves = int(config.get("octaves", 3))
        pattern_scale = float(config.get("pattern_scale", 1.0))
        return cv2.BRISK_create(
            thresh=thresh,
            octaves=octaves,
            patternScale=pattern_scale,
        )

    else:
        raise ValueError(
            f"Unknown descriptor: '{name}'. "
            "Supported descriptors: BRIEF, ORB, BRISK."
        )


def get_implementation_label(descriptor) -> str:
    """Return a human-readable label for the descriptor implementation."""
    if isinstance(descriptor, ManualBRIEF):
        return ManualBRIEF._IMPLEMENTATION
    if hasattr(descriptor, "_implementation"):
        return descriptor._implementation
    return type(descriptor).__name__
