# datasets/synthetic.py -- Synthetic dataset generator for unit testing
'''''Generates synthetic frame sequences with known ground-truth poses.'''''
from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Tuple
import cv2
import numpy as np
from src.datasets.base_dataset import BaseDataset, CameraIntrinsics, DatasetFrame
from src.geometry.transforms import make_pose

class SyntheticDataset(BaseDataset):
    '''''A minimal in-memory dataset for unit testing and smoke tests.'''''

    def __init__(self, n_frames: int = 10, image_size: Tuple[int,int] = (480, 640),
                 seed: int = 0) -> None:
        self._n = n_frames
        rng = np.random.default_rng(seed)
        self._images = [
            rng.integers(0, 255, image_size, dtype=np.uint8)
            for _ in range(n_frames)
        ]
        self._camera = CameraIntrinsics(fx=320, fy=320, cx=320, cy=240,
                                        width=image_size[1], height=image_size[0])
        self._poses = [
            make_pose(np.eye(3), np.array([i*0.1, 0.0, 0.0]))
            for i in range(n_frames)
        ]
        self._frames = [
            DatasetFrame(index=i, timestamp=float(i)/30,
                         image_path=Path(f'synthetic_{i:04d}.png'),
                         gt_pose=self._poses[i])
            for i in range(n_frames)
        ]

    @property
    def name(self): return 'synthetic'
    @property
    def sequence(self): return 'straight_line'
    @property
    def camera(self): return self._camera
    def __len__(self): return self._n
    def __getitem__(self, idx): return self._frames[idx]
    def get_ground_truth_poses(self): return self._poses

    def load_image_gray(self, idx: int) -> np.ndarray:
        return self._images[idx]


