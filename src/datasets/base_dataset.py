"""
base_dataset.py — Abstract base class for all dataset loaders.

All dataset loaders must implement the BaseDataset interface so the
VO pipeline can be dataset-agnostic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

import numpy as np


@dataclass
class CameraIntrinsics:
    """Pinhole camera intrinsic parameters and optional distortion coefficients."""
    fx: float
    fy: float
    cx: float
    cy: float
    k1: float = 0.0
    k2: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    width: int = 640
    height: int = 480

    @property
    def K(self) -> np.ndarray:
        """Return 3×3 intrinsic matrix."""
        return np.array([
            [self.fx,    0.0,  self.cx],
            [   0.0,  self.fy,  self.cy],
            [   0.0,    0.0,     1.0],
        ], dtype=np.float64)

    @property
    def dist_coeffs(self) -> np.ndarray:
        """Return (4,) distortion coefficient array [k1, k2, p1, p2]."""
        return np.array([self.k1, self.k2, self.p1, self.p2], dtype=np.float64)


@dataclass
class DatasetFrame:
    """A single dataset frame with image, timestamp, and optional ground truth."""
    index: int
    timestamp: float
    image_path: Path
    gt_pose: Optional[np.ndarray] = None   # (4, 4) T_wc or None


class BaseDataset(ABC):
    """Abstract interface for VO dataset loaders."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Dataset name (e.g., 'icl_nuim', 'tartanair')."""

    @property
    @abstractmethod
    def sequence(self) -> str:
        """Sequence identifier within the dataset."""

    @property
    @abstractmethod
    def camera(self) -> CameraIntrinsics:
        """Camera intrinsics for this sequence."""

    @abstractmethod
    def __len__(self) -> int:
        """Total number of frames in the sequence."""

    @abstractmethod
    def __getitem__(self, idx: int) -> DatasetFrame:
        """Return the DatasetFrame at the given index."""

    def __iter__(self) -> Iterator[DatasetFrame]:
        for i in range(len(self)):
            yield self[i]

    @abstractmethod
    def get_ground_truth_poses(self) -> List[np.ndarray]:
        """Return the list of ground-truth T_wc poses (one per frame)."""

    def load_image_gray(self, idx: int) -> np.ndarray:
        """Load and return the greyscale image for frame ``idx``."""
        import cv2
        frame = self[idx]
        img = cv2.imread(str(frame.image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not read image: {frame.image_path}")
        return img
