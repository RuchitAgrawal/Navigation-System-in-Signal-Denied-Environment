"""
icl_nuim.py — ICL-NUIM dataset loader.

Official page: https://www.doc.ic.ac.uk/~ahanda/VaFRIC/iclnuim.html

Dataset format (TUM RGB-D compatible)
--------------------------------------
<sequence_root>/
    rgb/           0000.png, 0001.png, ...
    depth/         (optional, not used for monocular VO)
    rgb.txt        # timestamp filename  (one entry per line)
    groundtruth.txt # timestamp tx ty tz qx qy qz qw

Ground-truth convention
-----------------------
Poses in groundtruth.txt follow the TUM convention:
    timestamp  tx ty tz  qx qy qz qw
where the transform represents the camera-to-world pose T_wc.
Units: metres. The world frame is right-handed, Y-up.

Camera intrinsics (living room sequences)
-----------------------------------------
    fx = 481.20,  fy = 480.00
    cx = 319.50,  cy = 239.50
    No lens distortion (synthetic data).
Source: https://www.doc.ic.ac.uk/~ahanda/VaFRIC/codes.html

Timestamp association
---------------------
RGB timestamps and ground-truth timestamps are not necessarily identical.
Association is performed by nearest-neighbour timestamp matching within
a configurable tolerance (default 0.02 s).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.datasets.base_dataset import (
    BaseDataset,
    CameraIntrinsics,
    DatasetFrame,
)
from src.geometry.transforms import make_pose, quat_to_rotation


# Default intrinsics for ICL-NUIM living room sequences
_LIVING_ROOM_INTRINSICS = CameraIntrinsics(
    fx=481.20, fy=480.00, cx=319.50, cy=239.50,
    k1=0.0, k2=0.0, p1=0.0, p2=0.0,
    width=640, height=480,
)


class ICLNUIMDataset(BaseDataset):
    """Loader for one ICL-NUIM sequence in TUM RGB-D compatible format.

    Parameters
    ----------
    root : str | Path
        Path to the sequence directory (containing rgb/, rgb.txt, groundtruth.txt).
    sequence_name : str
        Human-readable sequence name (used in result labels).
    camera_cfg : dict | None
        Camera intrinsics dict (overrides default living-room values).
    assoc_tolerance : float
        Maximum timestamp difference (seconds) for GT association.
    frame_start, frame_end, frame_step : int | None
        Frame range selection (inclusive start, exclusive end).
    """

    def __init__(
        self,
        root: str | Path,
        sequence_name: str = "living_room_traj1_loop",
        camera_cfg: Optional[dict] = None,
        assoc_tolerance: float = 0.02,
        frame_start: Optional[int] = None,
        frame_end: Optional[int] = None,
        frame_step: int = 1,
    ) -> None:
        self._root = Path(root)
        self._sequence_name = sequence_name
        self._assoc_tolerance = assoc_tolerance

        # Load camera intrinsics
        if camera_cfg:
            self._camera = CameraIntrinsics(**{
                k: camera_cfg[k] for k in camera_cfg
                if k in CameraIntrinsics.__dataclass_fields__
            })
        else:
            self._camera = _LIVING_ROOM_INTRINSICS

        # Parse rgb.txt
        rgb_entries = self._parse_tum_list(self._root / "rgb.txt")

        # Parse groundtruth.txt
        gt_entries = self._parse_groundtruth(self._root / "groundtruth.txt")

        # Associate by nearest timestamp
        frames_raw = self._associate(rgb_entries, gt_entries, assoc_tolerance)

        # Apply frame range
        start = frame_start or 0
        end   = frame_end   or len(frames_raw)
        self._frames: List[DatasetFrame] = frames_raw[start:end:frame_step]

        # Re-index
        for i, f in enumerate(self._frames):
            f.index = i

    # ------------------------------------------------------------------ #
    # BaseDataset interface
    # ------------------------------------------------------------------ #

    @property
    def name(self) -> str:
        return "icl_nuim"

    @property
    def sequence(self) -> str:
        return self._sequence_name

    @property
    def camera(self) -> CameraIntrinsics:
        return self._camera

    def __len__(self) -> int:
        return len(self._frames)

    def __getitem__(self, idx: int) -> DatasetFrame:
        return self._frames[idx]

    def get_ground_truth_poses(self) -> List[np.ndarray]:
        return [f.gt_pose for f in self._frames]

    # ------------------------------------------------------------------ #
    # Parsing helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_tum_list(path: Path) -> List[Tuple[float, Path]]:
        """Parse a TUM-format list file: ``timestamp filename``."""
        entries = []
        if not path.exists():
            raise FileNotFoundError(f"TUM list file not found: {path}")
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                ts = float(parts[0])
                img_path = path.parent / parts[1]
                entries.append((ts, img_path))
        entries.sort(key=lambda x: x[0])
        return entries

    @staticmethod
    def _parse_groundtruth(path: Path) -> Dict[float, np.ndarray]:
        """Parse groundtruth.txt → {timestamp: T_wc (4×4)}."""
        poses: Dict[float, np.ndarray] = {}
        if not path.exists():
            raise FileNotFoundError(f"Ground truth file not found: {path}")
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                ts = float(parts[0])
                tx, ty, tz = float(parts[1]), float(parts[2]), float(parts[3])
                qx, qy, qz, qw = (float(parts[4]), float(parts[5]),
                                   float(parts[6]), float(parts[7]))
                R = quat_to_rotation(qx, qy, qz, qw)
                T = make_pose(R, np.array([tx, ty, tz]))
                poses[ts] = T
        return poses

    @staticmethod
    def _associate(
        rgb_entries: List[Tuple[float, Path]],
        gt_poses: Dict[float, np.ndarray],
        tolerance: float,
    ) -> List[DatasetFrame]:
        """Associate RGB frames with ground-truth poses by nearest timestamp."""
        gt_timestamps = np.array(sorted(gt_poses.keys()))
        frames = []
        for i, (ts_rgb, img_path) in enumerate(rgb_entries):
            diffs = np.abs(gt_timestamps - ts_rgb)
            best_idx = int(np.argmin(diffs))
            best_diff = float(diffs[best_idx])
            gt_pose = None
            if best_diff <= tolerance:
                gt_pose = gt_poses[gt_timestamps[best_idx]]
            frame = DatasetFrame(
                index=i,
                timestamp=ts_rgb,
                image_path=img_path,
                gt_pose=gt_pose,
            )
            frames.append(frame)
        return frames


def load_icl_nuim_from_config(dataset_cfg: dict) -> ICLNUIMDataset:
    """Construct an ICLNUIMDataset from a parsed dataset YAML dict."""
    root = Path(dataset_cfg["root"]) / dataset_cfg["sequence"]
    return ICLNUIMDataset(
        root=root,
        sequence_name=dataset_cfg["sequence"],
        camera_cfg=dataset_cfg.get("camera"),
        assoc_tolerance=float(dataset_cfg.get("assoc_tolerance", 0.02)),
        frame_start=dataset_cfg.get("frame_start"),
        frame_end=dataset_cfg.get("frame_end"),
        frame_step=int(dataset_cfg.get("frame_step", 1)),
    )
