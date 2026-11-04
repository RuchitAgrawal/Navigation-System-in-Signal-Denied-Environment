"""
src/features/extractor.py â€” Unified detect-and-describe wrapper.

Provides a single `FeatureExtractor` class that handles all
detector/descriptor combinations cleanly, including:
- Joint ORB (single detectAndCompute call)
- Separate detect + compute for FAST+ORB, FAST+BRIEF, ORB+BRISK
- ManualBRIEF fallback compute path

This wrapper ensures the pipeline never needs to handle branching
detector/descriptor logic inline.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np

from src.features.config import FeatureConfig
from src.features.descriptor import ManualBRIEF
from src.features.bucketing import distribute_quadtree, distribute_grid
from src.features.subpixel import refine_keypoints_subpixel


@dataclass
class ExtractionResult:
    """Result of feature detection and description for one frame."""
    keypoints: List[cv2.KeyPoint]
    descriptors: Optional[np.ndarray]   # None if no keypoints detected
    detect_ms: float
    describe_ms: float

    @property
    def n_keypoints(self) -> int:
        return len(self.keypoints)

    @property
    def has_descriptors(self) -> bool:
        return (self.descriptors is not None and
                self.descriptors.shape[0] > 0)


class FeatureExtractor:
    """Wraps a FeatureConfig and provides a single `extract(image)` interface.

    Parameters
    ----------
    config : FeatureConfig
        Validated detector/descriptor configuration.
    bucketing : str
        Spatial bucketing strategy: 'none', 'grid' (Perez-Grau 6-bucket), or 'quadtree' (proposed).
    subpixel : bool
        If True, apply sub-pixel refinement to keypoint coordinates before description.
    max_features : int
        Maximum number of keypoints to retain after bucketing.
    """

    def __init__(
        self,
        config: FeatureConfig,
        bucketing: str = "none",
        subpixel: bool = False,
        max_features: int = 2000,
        clahe: bool = False,
        clahe_clip_limit: float = 2.0,
        clahe_grid_size: Tuple[int, int] = (8, 8),
    ) -> None:
        self.config = config
        self.bucketing = bucketing.lower()
        self.subpixel = subpixel
        self.max_features = max_features
        self.clahe = clahe
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_grid_size = clahe_grid_size

    def _apply_bucketing_and_subpixel(self, gray: np.ndarray, kps: List[cv2.KeyPoint]) -> List[cv2.KeyPoint]:
        """Apply spatial bucketing and sub-pixel refinement if configured."""
        if not kps:
            return []

        h, w = gray.shape[:2]
        if self.bucketing == "quadtree":
            kps = distribute_quadtree(kps, width=w, height=h, max_features=self.max_features)
        elif self.bucketing == "grid":
            kps = distribute_grid(kps, width=w, height=h, n_buckets_x=3, n_buckets_y=2, max_features=self.max_features)

        if self.subpixel:
            kps = refine_keypoints_subpixel(gray, kps)

        return kps

    def extract(self, gray: np.ndarray) -> ExtractionResult:
        """Detect keypoints and compute descriptors for a greyscale image.

        Parameters
        ----------
        gray : (H, W) uint8 greyscale image.

        Returns
        -------
        ExtractionResult
        """
        fc = self.config

        if self.clahe:
            clahe_obj = cv2.createCLAHE(
                clipLimit=self.clahe_clip_limit,
                tileGridSize=self.clahe_grid_size,
            )
            gray = clahe_obj.apply(gray)

        if fc.is_joint_orb and self.bucketing == "none" and not self.subpixel:
            # Fast-path for baseline ORB+ORB without extra bucketing/subpixel
            t0 = time.perf_counter()
            kps, descs = fc.detector.detectAndCompute(gray, None)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            kps = list(kps) if kps is not None else []
            return ExtractionResult(
                keypoints=kps,
                descriptors=descs,
                detect_ms=elapsed_ms / 2,
                describe_ms=elapsed_ms / 2,
            )

        # Detect
        t0 = time.perf_counter()
        kps = fc.detector.detect(gray, None)
        kps = list(kps) if kps is not None else []

        # Apply spatial bucketing and sub-pixel refinement
        kps = self._apply_bucketing_and_subpixel(gray, kps)
        detect_ms = (time.perf_counter() - t0) * 1000.0

        if not kps:
            return ExtractionResult(
                keypoints=[],
                descriptors=None,
                detect_ms=detect_ms,
                describe_ms=0.0,
            )

        # Describe
        t0 = time.perf_counter()
        kps, descs = fc.descriptor.compute(gray, kps)
        describe_ms = (time.perf_counter() - t0) * 1000.0

        return ExtractionResult(
            keypoints=list(kps) if kps is not None else [],
            descriptors=descs,
            detect_ms=detect_ms,
            describe_ms=describe_ms,
        )


