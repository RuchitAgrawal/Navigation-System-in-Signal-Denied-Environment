"""
pose.py — Pose accumulation and trajectory management.

Maintains a list of T_wc poses (camera-to-world) as the VO pipeline
processes frames. Provides serialization to TUM trajectory format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

import numpy as np

from src.geometry.transforms import (
    pose_identity,
    invert_pose,
    compose_poses,
    make_pose,
    quat_to_rotation,
    rotation_to_quat,
    is_valid_pose,
)


class FrameStatus(Enum):
    SUCCESS = auto()
    FAILED_FEATURES = auto()    # too few keypoints detected
    FAILED_MATCHES = auto()     # too few descriptor matches
    FAILED_RANSAC = auto()      # RANSAC inlier ratio below threshold
    FAILED_POSE = auto()        # recoverPose returned degenerate result
    SKIPPED = auto()            # first frame (no relative pose yet)


@dataclass
class FrameDiagnostics:
    """Per-frame diagnostic record saved to CSV."""
    frame_idx: int
    status: FrameStatus
    n_keypoints_prev: int = 0
    n_keypoints_curr: int = 0
    n_raw_matches: int = 0
    n_filtered_matches: int = 0
    n_ransac_inliers: int = 0
    ransac_inlier_ratio: float = 0.0
    detect_time_ms: float = 0.0
    describe_time_ms: float = 0.0
    match_time_ms: float = 0.0
    pose_time_ms: float = 0.0
    total_time_ms: float = 0.0


@dataclass
class PoseAccumulator:
    """Accumulates per-frame SE(3) poses and diagnostics.

    Poses are stored as T_wc (camera-to-world, 4×4 float64).
    The first frame is always set to the identity pose.
    """

    poses: List[np.ndarray] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)
    diagnostics: List[FrameDiagnostics] = field(default_factory=list)

    def initialize(self, timestamp: float = 0.0) -> None:
        """Set the first pose to the world origin."""
        self.poses = [pose_identity()]
        self.timestamps = [timestamp]
        self.diagnostics = []

    @property
    def current_pose(self) -> np.ndarray:
        """Return the most recent accumulated T_wc."""
        if not self.poses:
            raise RuntimeError("PoseAccumulator has not been initialized.")
        return self.poses[-1]

    def add_relative_pose(
        self,
        R_rel: np.ndarray,
        t_rel: np.ndarray,
        timestamp: float,
        diag: FrameDiagnostics,
    ) -> None:
        """Accumulate a relative camera-to-camera transform into the trajectory.

        Parameters
        ----------
        R_rel : (3, 3) ndarray   Rotation from prev to curr camera frame.
        t_rel : (3,)  ndarray   Translation direction (unit vector, scale unknown).
        timestamp : float        Timestamp of the current frame.
        diag : FrameDiagnostics  Per-frame diagnostics to store.

        Note
        ----
        For monocular VO, ``t_rel`` is a *direction* vector only (unit norm).
        The accumulated translation is therefore in arbitrary scale units.
        Do NOT interpret accumulated positions as metric distances.
        """
        T_rel = make_pose(R_rel, t_rel)           # T_{c(t-1) -> c(t)}
        # T_wc[t] = T_wc[t-1] @ T_{c(t-1)->w} @ T_{w->c(t)}
        # Equivalently: T_wc[t] = T_wc[t-1] @ inv(T_{c(t)->c(t-1)})
        # But recoverPose gives us T_{c(t-1)->c(t)}, i.e.
        #   p_{c(t)} = R_rel @ p_{c(t-1)} + t_rel
        # So T_{c(t-1)->c(t)} takes points from prev-cam to curr-cam.
        # T_wc[t] = T_wc[t-1] @ inv(T_{c(t-1)->c(t)})
        #          = T_wc[t-1] @ T_{c(t)->c(t-1)}
        T_delta_inv = invert_pose(T_rel)
        new_pose = compose_poses(self.current_pose, T_delta_inv)
        self.poses.append(new_pose)
        self.timestamps.append(timestamp)
        self.diagnostics.append(diag)

    def add_failed_pose(self, timestamp: float, diag: FrameDiagnostics) -> None:
        """On tracking failure, carry the previous pose forward."""
        self.poses.append(self.current_pose.copy())
        self.timestamps.append(timestamp)
        self.diagnostics.append(diag)

    def get_positions(self) -> np.ndarray:
        """Return (N, 3) array of world-frame camera positions."""
        return np.array([T[:3, 3] for T in self.poses], dtype=np.float64)

    def save_tum_format(self, path: str | Path) -> None:
        """Save trajectory to a TUM-format text file.

        Format per line:
            timestamp tx ty tz qx qy qz qw
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for ts, T in zip(self.timestamps, self.poses):
                t = T[:3, 3]
                q = rotation_to_quat(T[:3, :3])  # (x, y, z, w)
                f.write(f"{ts:.6f} {t[0]:.6f} {t[1]:.6f} {t[2]:.6f} "
                        f"{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}\n")

    @staticmethod
    def load_tum_format(path: str | Path) -> "PoseAccumulator":
        """Load a TUM-format trajectory file into a new PoseAccumulator."""
        acc = PoseAccumulator()
        acc.poses = []
        acc.timestamps = []
        acc.diagnostics = []
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
                acc.timestamps.append(ts)
                acc.poses.append(T)
        return acc
