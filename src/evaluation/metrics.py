"""
metrics.py — Aggregate metrics utilities and CSV export.

Consolidates ATE, RPE, tracking, and runtime results into summary dicts
and Pandas DataFrames for CSV export.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.evaluation.ate import ATEResult
from src.evaluation.rpe import RPEResult
from src.geometry.pose import FrameDiagnostics, FrameStatus
from src.odometry.tracker import TrackingReport, compute_fps_stats


def build_summary_row(
    config_id: str,
    dataset_name: str,
    sequence_name: str,
    descriptor_label: str,
    ate: ATEResult,
    rpe: RPEResult,
    tracking: TrackingReport,
    diagnostics: List[FrameDiagnostics],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a single summary-table row from all experiment results."""
    fps_stats = compute_fps_stats(diagnostics)
    row = {
        "config_id": config_id,
        "descriptor_label": descriptor_label,
        "dataset": dataset_name,
        "sequence": sequence_name,
        # ATE
        "ate_alignment": ate.alignment,
        "ate_scale": round(ate.scale, 6),
        "ate_rmse_m": round(ate.rmse, 6),
        "ate_mean_m": round(ate.mean, 6),
        "ate_median_m": round(ate.median, 6),
        "ate_std_m": round(ate.std, 6),
        "ate_n_frames": ate.n_frames,
        # RPE
        "rpe_delta_frames": rpe.delta,
        "rpe_trans_rmse_m": round(rpe.trans_rmse, 6),
        "rpe_trans_mean_m": round(rpe.trans_mean, 6),
        "rpe_trans_median_m": round(rpe.trans_median, 6),
        "rpe_rot_rmse_deg": round(rpe.rot_rmse_deg, 4),
        "rpe_rot_mean_deg": round(rpe.rot_mean_deg, 4),
        "rpe_n_pairs": rpe.n_pairs,
        # Tracking
        "total_frames": tracking.total_frames,
        "success_frames": tracking.success_frames,
        "failed_frames": tracking.failed_frames,
        "tracking_success_pct": round(tracking.success_rate * 100, 2),
        "is_degenerate": tracking.is_degenerate,
        # Runtime
        "mean_frame_time_ms": round(fps_stats["mean_frame_time_ms"], 3),
        "median_frame_time_ms": round(fps_stats["median_frame_time_ms"], 3),
        "p95_frame_time_ms": round(fps_stats["p95_frame_time_ms"], 3),
        "mean_fps": round(fps_stats["mean_fps"], 2),
        "median_fps": round(fps_stats["median_fps"], 2),
    }
    if extra:
        row.update(extra)
    return row


def diagnostics_to_dataframe(diagnostics: List[FrameDiagnostics]) -> pd.DataFrame:
    """Convert per-frame diagnostics to a Pandas DataFrame."""
    rows = []
    for d in diagnostics:
        rows.append({
            "frame_idx": d.frame_idx,
            "status": d.status.name,
            "n_keypoints_prev": d.n_keypoints_prev,
            "n_keypoints_curr": d.n_keypoints_curr,
            "n_raw_matches": d.n_raw_matches,
            "n_filtered_matches": d.n_filtered_matches,
            "n_ransac_inliers": d.n_ransac_inliers,
            "ransac_inlier_ratio": round(d.ransac_inlier_ratio, 4),
            "detect_time_ms": round(d.detect_time_ms, 3),
            "describe_time_ms": round(d.describe_time_ms, 3),
            "match_time_ms": round(d.match_time_ms, 3),
            "pose_time_ms": round(d.pose_time_ms, 3),
            "total_time_ms": round(d.total_time_ms, 3),
        })
    return pd.DataFrame(rows)


def save_per_frame_csv(
    diagnostics: List[FrameDiagnostics],
    path: str | Path,
) -> None:
    """Save per-frame diagnostics to CSV."""
    df = diagnostics_to_dataframe(diagnostics)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_summary_csv(
    rows: List[Dict[str, Any]],
    path: str | Path,
) -> None:
    """Save aggregate summary rows to CSV."""
    df = pd.DataFrame(rows)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
