"""
tracker.py — Tracking health monitor and recovery utilities.

Provides aggregate tracking statistics from a completed PoseAccumulator
and detects degenerate runs (>50 % failure rate).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from src.geometry.pose import FrameDiagnostics, FrameStatus


@dataclass
class TrackingReport:
    """Aggregate tracking statistics for one VO run."""
    total_frames: int
    success_frames: int
    failed_features_frames: int
    failed_matches_frames: int
    failed_ransac_frames: int
    failed_pose_frames: int
    skipped_frames: int

    @property
    def failed_frames(self) -> int:
        return (self.failed_features_frames + self.failed_matches_frames +
                self.failed_ransac_frames + self.failed_pose_frames)

    @property
    def success_rate(self) -> float:
        denom = self.total_frames - self.skipped_frames
        return self.success_frames / denom if denom > 0 else 0.0

    @property
    def is_degenerate(self) -> bool:
        """True if more than 50 % of processable frames failed."""
        return self.success_rate < 0.5

    def summary_dict(self) -> dict:
        return {
            "total_frames": self.total_frames,
            "success_frames": self.success_frames,
            "failed_frames": self.failed_frames,
            "failed_features": self.failed_features_frames,
            "failed_matches": self.failed_matches_frames,
            "failed_ransac": self.failed_ransac_frames,
            "failed_pose": self.failed_pose_frames,
            "tracking_success_pct": round(self.success_rate * 100, 2),
            "is_degenerate": self.is_degenerate,
        }


def compute_tracking_report(diagnostics: List[FrameDiagnostics]) -> TrackingReport:
    """Compute aggregate tracking statistics from per-frame diagnostics."""
    counts = {s: 0 for s in FrameStatus}
    for d in diagnostics:
        counts[d.status] = counts.get(d.status, 0) + 1

    return TrackingReport(
        total_frames=len(diagnostics),
        success_frames=counts.get(FrameStatus.SUCCESS, 0),
        failed_features_frames=counts.get(FrameStatus.FAILED_FEATURES, 0),
        failed_matches_frames=counts.get(FrameStatus.FAILED_MATCHES, 0),
        failed_ransac_frames=counts.get(FrameStatus.FAILED_RANSAC, 0),
        failed_pose_frames=counts.get(FrameStatus.FAILED_POSE, 0),
        skipped_frames=counts.get(FrameStatus.SKIPPED, 0),
    )


def compute_fps_stats(diagnostics: List[FrameDiagnostics]) -> dict:
    """Compute runtime statistics (mean, median, p95 FPS) from diagnostics."""
    times_ms = np.array(
        [d.total_time_ms for d in diagnostics if d.status != FrameStatus.SKIPPED],
        dtype=np.float64,
    )
    if len(times_ms) == 0:
        return {"mean_fps": 0.0, "median_fps": 0.0, "p95_frame_time_ms": 0.0}

    fps_vals = 1000.0 / np.where(times_ms > 0, times_ms, 1e-6)
    return {
        "mean_frame_time_ms": float(np.mean(times_ms)),
        "median_frame_time_ms": float(np.median(times_ms)),
        "p95_frame_time_ms": float(np.percentile(times_ms, 95)),
        "mean_fps": float(np.mean(fps_vals)),
        "median_fps": float(np.median(fps_vals)),
    }
