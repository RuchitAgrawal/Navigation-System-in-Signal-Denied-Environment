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
    config : FeatureConfig  Validated detector/descriptor configuration.
    """

    def __init__(self, config: FeatureConfig) -> None:
        self.config = config

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

        if fc.is_joint_orb:
            # ORB+ORB: single detectAndCompute
            t0 = time.perf_counter()
            kps, descs = fc.detector.detectAndCompute(gray, None)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            kps = list(kps) if kps is not None else []
            return ExtractionResult(
                keypoints=kps,
                descriptors=descs,
                detect_ms=elapsed_ms / 2,    # approximate split
                describe_ms=elapsed_ms / 2,
            )

        # Separate detect + describe
        t0 = time.perf_counter()
        kps = fc.detector.detect(gray, None)
        detect_ms = (time.perf_counter() - t0) * 1000.0

        if not kps:
            return ExtractionResult(
                keypoints=[],
                descriptors=None,
                detect_ms=detect_ms,
                describe_ms=0.0,
            )

        t0 = time.perf_counter()
        if isinstance(fc.descriptor, ManualBRIEF):
            kps, descs = fc.descriptor.compute(gray, kps)
        else:
            kps, descs = fc.descriptor.compute(gray, kps)
        describe_ms = (time.perf_counter() - t0) * 1000.0

        return ExtractionResult(
            keypoints=list(kps) if kps is not None else [],
            descriptors=descs,
            detect_ms=detect_ms,
            describe_ms=describe_ms,
        )

