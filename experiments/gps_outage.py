"""
gps_outage.py — Simulated GPS-denied interval experiment.

IMPORTANT: This is a SIMULATED experiment only.
- No real RF interference or GPS hardware is involved.
- The GPS anchor uses one ground-truth position to establish global scale.
- VO-only propagation then runs during the simulated outage interval.
- Error growth is measured against reference ground-truth positions.

Methodology
-----------
1. Set a GPS anchor pose at frame ``outage_start - 1`` using the GT position.
   This provides a one-time scale anchor (documented clearly).
2. During frames [outage_start, outage_end], propagate only via VO relative motion.
3. After the outage, compare propagated position to GT and report drift.

Scale note
----------
Without the one-time GPS anchor, monocular VO translation has no metric scale.
The scale anchor is applied once at the start of the outage and is labeled
explicitly in all output tables. This does NOT constitute a full GPS/VO fusion.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from src.geometry.transforms import invert_pose, compose_poses, make_pose
from src.geometry.pose import PoseAccumulator


def simulate_gps_outage(
    accumulator: PoseAccumulator,
    gt_poses: List[Optional[np.ndarray]],
    outage_start: int,
    outage_end: int,
    output_root: str | Path = "results",
    config_id: str = "unknown",
    dataset_name: str = "unknown",
    sequence_name: str = "unknown",
    verbose: bool = True,
) -> dict:
    """Simulate a GPS-denied interval and measure VO-only drift.

    Parameters
    ----------
    accumulator   : PoseAccumulator from a completed VO run.
    gt_poses      : Ground-truth poses (list of T_wc or None).
    outage_start  : First frame index of the simulated outage.
    outage_end    : Last frame index of the simulated outage (inclusive).
    output_root   : Root directory for saving figures and results.
    config_id     : Feature config label (for filenames / titles).

    Returns
    -------
    dict with drift statistics.
    """
    est_poses = accumulator.poses
    n = len(est_poses)
    outage_start = max(1, min(outage_start, n - 2))
    outage_end   = max(outage_start + 1, min(outage_end, n - 1))

    # --- GPS anchor at frame before outage ---
    anchor_idx = outage_start - 1
    T_gt_anchor  = gt_poses[anchor_idx]
    T_est_anchor = est_poses[anchor_idx]

    if T_gt_anchor is None:
        raise ValueError(f"Ground-truth missing at anchor frame {anchor_idx}")

    # Scale factor: ratio of GT distance to VO distance over a small window
    # (simulates what a GPS fix provides at the start of outage)
    window = min(10, outage_start)
    gt_dists  = []
    est_dists = []
    for k in range(max(0, anchor_idx - window), anchor_idx):
        if gt_poses[k] is not None:
            gt_dists.append(np.linalg.norm(T_gt_anchor[:3, 3] - gt_poses[k][:3, 3]))
            est_dists.append(np.linalg.norm(T_est_anchor[:3, 3] - est_poses[k][:3, 3]))

    if sum(est_dists) > 1e-6:
        scale_anchor = sum(gt_dists) / sum(est_dists)
    else:
        scale_anchor = 1.0

    if verbose:
        print(f"\n[GPS Outage Simulation]")
        print(f"  Outage interval : frames {outage_start} – {outage_end}")
        print(f"  Scale anchor    : {scale_anchor:.4f} (applied at frame {anchor_idx})")

    # --- Propagate VO during outage ---
    propagated_positions = []
    drift_errors = []

    T_global_anchor = T_gt_anchor  # world-frame anchor from GPS

    for idx in range(outage_start, outage_end + 1):
        # Relative motion from anchor to current frame (in VO scale)
        T_rel_vo = invert_pose(T_est_anchor) @ est_poses[idx]

        # Apply scale to translation component
        T_rel_scaled = T_rel_vo.copy()
        T_rel_scaled[:3, 3] *= scale_anchor

        # Global position in world frame
        T_propagated = T_global_anchor @ T_rel_scaled
        pos_propagated = T_propagated[:3, 3]
        propagated_positions.append(pos_propagated)

        # Compare to GT
        if gt_poses[idx] is not None:
            pos_gt = gt_poses[idx][:3, 3]
            drift = float(np.linalg.norm(pos_propagated - pos_gt))
            drift_errors.append((idx, drift))

    positions_arr = np.array(propagated_positions)
    drift_arr = np.array([d for _, d in drift_errors])
    frames_arr = np.array([f for f, _ in drift_errors])

    if verbose and len(drift_errors) > 0:
        print(f"  Max drift   : {drift_arr.max():.4f} m at frame {frames_arr[drift_arr.argmax()]}")
        print(f"  Final drift : {drift_arr[-1]:.4f} m")

    # --- Plot ---
    output_root = Path(output_root)
    _save_outage_plot(
        gt_poses, propagated_positions, frames_arr, drift_arr,
        outage_start, outage_end,
        output_root / "figures" / f"gps_outage_{config_id}_{dataset_name}.png",
        config_id, dataset_name, sequence_name,
    )

    return {
        "config_id": config_id,
        "dataset": dataset_name,
        "sequence": sequence_name,
        "outage_start_frame": outage_start,
        "outage_end_frame": outage_end,
        "outage_duration_frames": outage_end - outage_start + 1,
        "scale_anchor": round(scale_anchor, 6),
        "max_drift_m": round(float(drift_arr.max()), 6) if len(drift_arr) else None,
        "final_drift_m": round(float(drift_arr[-1]), 6) if len(drift_arr) else None,
        "mean_drift_m": round(float(drift_arr.mean()), 6) if len(drift_arr) else None,
        "note": "SIMULATED GPS outage. Scale anchored once at outage start using GT position.",
    }


def _save_outage_plot(
    gt_poses, propagated_positions, frames_arr, drift_arr,
    outage_start, outage_end, save_path,
    config_id, dataset_name, sequence_name,
):
    """Save a two-panel GPS outage figure."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"Simulated GPS Outage — {config_id.upper()} | {dataset_name} / {sequence_name}\n"
        f"[Outage: frames {outage_start}–{outage_end}]",
        fontsize=12, fontweight="bold",
    )

    # Panel 1: trajectory
    gt_pos = np.array([p[:3, 3] for p in gt_poses if p is not None])
    prop   = np.array(propagated_positions) if propagated_positions else np.zeros((0, 3))

    ax1.plot(gt_pos[:, 0], gt_pos[:, 2], color="#6c757d", linewidth=1.5, label="GT trajectory")
    if prop.shape[0] > 0:
        ax1.plot(prop[:, 0], prop[:, 2], color="#dc3545", linewidth=1.5,
                 linestyle="--", label="VO-only (outage)")
    ax1.axvline(x=gt_pos[min(outage_start, len(gt_pos)-1), 0],
                color="orange", linestyle=":", linewidth=1.2, label="Outage start")
    ax1.set_xlabel("X (m)"); ax1.set_ylabel("Z (m)")
    ax1.set_title("Trajectory (X-Z)"); ax1.legend(fontsize=9); ax1.grid(True, alpha=0.3)

    # Panel 2: drift over outage
    if len(drift_arr) > 0:
        ax2.fill_between(frames_arr, drift_arr, alpha=0.35, color="#dc3545")
        ax2.plot(frames_arr, drift_arr, color="#dc3545", linewidth=1.2)
    ax2.set_xlabel("Frame Index"); ax2.set_ylabel("Positional Error (m)")
    ax2.set_title("Drift During Outage"); ax2.grid(True, alpha=0.3)

    # Label scale anchor
    ax2.text(0.02, 0.96,
             "Scale anchored once at outage start\n(GT fix simulated)",
             transform=ax2.transAxes, fontsize=8, va="top",
             bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
