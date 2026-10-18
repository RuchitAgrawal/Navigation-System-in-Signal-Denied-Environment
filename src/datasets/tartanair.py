"""
tartanair.py â€” TartanAir dataset loader.

Official page: https://tartanair.org/
Tools repo:    https://github.com/castacks/tartanair_tools

Dataset structure
-----------------
<root>/<environment>/<difficulty>/<trajectory>/
    image_left/    000000.png, 000001.png, ...
    pose_left.txt  (one pose per line: x y z qx qy qz qw)

Ground-truth pose convention
-----------------------------
TartanAir ``pose_left.txt`` provides poses in **NED (North-East-Down) body frame**:
    x forward, y right, z down
Each line: tx ty tz qx qy qz qw

The internal pipeline convention is camera-to-world T_wc with:
    x right, y down, z forward (OpenCV/camera convention)

Conversion is applied in the loader via ``ned_body_to_camera_pose()``.

Camera intrinsics
-----------------
Standard TartanAir left camera (same for all environments):
    fx = 320.0, fy = 320.0, cx = 320.0, cy = 240.0
    Image size: 640 Ã— 480, no distortion.
Source: TartanAir documentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import numpy as np

from src.datasets.base_dataset import (
    BaseDataset,
    CameraIntrinsics,
    DatasetFrame,
)
from src.geometry.transforms import ned_body_to_camera_pose


# Standard TartanAir left camera intrinsics
_TARTANAIR_INTRINSICS = CameraIntrinsics(
    fx=320.0, fy=320.0, cx=320.0, cy=240.0,
    k1=0.0, k2=0.0, p1=0.0, p2=0.0,
    width=640, height=480,
)


class TartanAirDataset(BaseDataset):
    """Loader for one TartanAir trajectory.

    Parameters
    ----------
    root : str | Path
        Path to the trajectory directory
        (e.g., data/tartanair/ocean/Easy/P000).
    sequence_name : str
        Human-readable label (e.g., 'ocean_Easy_P000').
    camera_cfg : dict | None
        Camera intrinsics dict (overrides default TartanAir values).
    frame_start, frame_end, frame_step : int | None
        Frame range selection.
    """

    def __init__(
        self,
        root: str | Path,
        sequence_name: str = "tartanair_seq",
        camera_cfg: Optional[dict] = None,
        frame_start: Optional[int] = None,
        frame_end: Optional[int] = None,
        frame_step: int = 1,
    ) -> None:
        self._root = Path(root)
        self._sequence_name = sequence_name

        if camera_cfg:
            self._camera = CameraIntrinsics(**{
                k: camera_cfg[k] for k in camera_cfg
                if k in CameraIntrinsics.__dataclass_fields__
            })
        else:
            self._camera = _TARTANAIR_INTRINSICS

        # Discover image files
        img_dir = self._root / "image_left"
        if not img_dir.exists():
            raise FileNotFoundError(f"image_left directory not found: {img_dir}")
        img_paths = sorted(img_dir.glob("*.png"))
        if not img_paths:
            raise FileNotFoundError(f"No PNG images found in: {img_dir}")

        # Parse ground-truth poses
        pose_file = self._root / "pose_left.txt"
        gt_poses = self._parse_poses(pose_file) if pose_file.exists() else None

        # Build frame list
        frames_raw: List[DatasetFrame] = []
        for i, img_path in enumerate(img_paths):
            gt_pose = gt_poses[i] if (gt_poses is not None and i < len(gt_poses)) else None
            frames_raw.append(DatasetFrame(
                index=i,
                timestamp=float(i),   # TartanAir has no explicit timestamps; use frame index
                image_path=img_path,
                gt_pose=gt_pose,
            ))

        # Apply frame range
        start = frame_start or 0
        end   = frame_end   or len(frames_raw)
        self._frames = frames_raw[start:end:frame_step]
        for j, f in enumerate(self._frames):
            f.index = j

    # ------------------------------------------------------------------ #
    # BaseDataset interface
    # ------------------------------------------------------------------ #

    @property
    def name(self) -> str:
        return "tartanair"

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
    def _parse_poses(path: Path) -> List[np.ndarray]:
        """Parse pose_left.txt (NED body frame) â†’ list of T_wc (4Ã—4)."""
        poses = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                tx, ty, tz = float(parts[0]), float(parts[1]), float(parts[2])
                qx, qy, qz, qw = (float(parts[3]), float(parts[4]),
                                   float(parts[5]), float(parts[6]))
                T_wc = ned_body_to_camera_pose(
                    t_ned=np.array([tx, ty, tz]),
                    q_ned=np.array([qx, qy, qz, qw]),
                )
                poses.append(T_wc)
        return poses


def load_tartanair_from_config(dataset_cfg: dict) -> TartanAirDataset:
    """Construct a TartanAirDataset from a parsed dataset YAML dict."""
    env   = dataset_cfg["environment"]
    diff  = dataset_cfg["difficulty"]
    traj  = dataset_cfg["trajectory"]
    root  = Path(dataset_cfg["root"]) / env / diff / traj
    seq   = f"{env}_{diff}_{traj}"
    return TartanAirDataset(
        root=root,
        sequence_name=seq,
        camera_cfg=dataset_cfg.get("camera"),
        frame_start=dataset_cfg.get("frame_start"),
        frame_end=dataset_cfg.get("frame_end"),
        frame_step=int(dataset_cfg.get("frame_step", 1)),
    )

