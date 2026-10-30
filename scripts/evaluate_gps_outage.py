#!/usr/bin/env python
"""
evaluate_gps_outage.py — Quantitative GPS outage & dead-reckoning drift evaluation.

Simulates GPS signal loss events in GPS-denied environments (as formulated in
Perez-Grau et al., JFR 2017 Section 4-5). Evaluates dead-reckoning drift rate,
cumulative positional error, and trajectory divergence during signal dropouts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.geometry.pose import PoseAccumulator
from src.evaluation.ate import umeyama_alignment


def simulate_gps_outage(
    est_poses: List[np.ndarray],
    gt_poses: List[Optional[np.ndarray]],
    outage_start_idx: int = 10,
    outage_end_idx: Optional[int] = None,
) -> Dict[str, np.ndarray | float | int]:
    """Simulate GPS signal loss starting at outage_start_idx.

    Before outage_start_idx, the trajectory is anchored by GPS (ground truth).
    During [outage_start_idx, outage_end_idx], the vehicle navigates purely
    via dead-reckoning visual odometry relative poses.
    """
    n_frames = min(len(est_poses), len(gt_poses))
    if n_frames < 3:
        raise ValueError("Insufficient poses for GPS outage evaluation (minimum 3 required)")

    outage_start_idx = max(1, min(outage_start_idx, n_frames - 2))
    if outage_end_idx is None or outage_end_idx >= n_frames:
        outage_end_idx = n_frames

    # Extract positions
    est_pts = np.array([p[:3, 3] for p in est_poses[:n_frames]])
    gt_valid = [p is not None for p in gt_poses[:n_frames]]
    gt_pts = np.array([p[:3, 3] if p is not None else np.zeros(3) for p in gt_poses[:n_frames]])

    # Rigid SE(3) alignment on pre-outage window to calibrate scale and initial orientation
    pre_est = [est_poses[i] for i in range(outage_start_idx) if gt_valid[i]]
    pre_gt = [gt_poses[i] for i in range(outage_start_idx) if gt_valid[i]]

    if len(pre_est) >= 3:
        s_align, R_align, t_align = umeyama_alignment(
            np.array([p[:3, 3] for p in pre_est]),
            np.array([p[:3, 3] for p in pre_gt]),
            with_scale=True,
        )
    else:
        R_align = np.eye(3)
        t_align = np.zeros(3)
        s_align = 1.0

    # Transform all estimated points using pre-outage anchor
    aligned_est_pts = (s_align * (R_align @ est_pts.T)).T + t_align

    # Calculate distance travelled and positional drift during outage
    outage_indices = np.arange(outage_start_idx, outage_end_idx)
    drifts = []
    distances = []
    cum_dist = 0.0

    for idx in range(outage_start_idx, outage_end_idx):
        if idx > outage_start_idx:
            step_dist = np.linalg.norm(gt_pts[idx] - gt_pts[idx - 1])
            cum_dist += step_dist
        distances.append(cum_dist)

        pos_err = np.linalg.norm(aligned_est_pts[idx] - gt_pts[idx])
        drifts.append(pos_err)

    drifts = np.array(drifts)
    distances = np.array(distances)

    max_drift = float(np.max(drifts)) if len(drifts) > 0 else 0.0
    mean_drift = float(np.mean(drifts)) if len(drifts) > 0 else 0.0
    final_drift = float(drifts[-1]) if len(drifts) > 0 else 0.0
    total_outage_dist = float(distances[-1]) if len(distances) > 0 else 0.0
    drift_pct = (final_drift / total_outage_dist * 100.0) if total_outage_dist > 1e-4 else 0.0

    return {
        "outage_start_idx": outage_start_idx,
        "outage_end_idx": outage_end_idx,
        "aligned_est_pts": aligned_est_pts,
        "gt_pts": gt_pts,
        "outage_indices": outage_indices,
        "drifts": drifts,
        "distances": distances,
        "max_drift_m": max_drift,
        "mean_drift_m": mean_drift,
        "final_drift_m": final_drift,
        "total_distance_m": total_outage_dist,
        "drift_pct": drift_pct,
    }


def plot_gps_outage_analysis(
    outage_res: Dict[str, np.ndarray | float | int],
    save_path: str | Path,
    title: str = "GPS Outage Dead-Reckoning Drift Analysis",
) -> Path:
    """Plot dead-reckoning trajectory and drift accumulation curves."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    aligned_est = outage_res["aligned_est_pts"]
    gt_pts = outage_res["gt_pts"]
    start_idx = outage_res["outage_start_idx"]
    end_idx = outage_res["outage_end_idx"]
    drifts = outage_res["drifts"]
    distances = outage_res["distances"]
    outage_idx = outage_res["outage_indices"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # 1. 2D Top-down trajectory (X vs Z or X vs Y)
    ax1.plot(gt_pts[:, 0], gt_pts[:, 2], "k-", linewidth=2.0, label="Ground Truth (Pre-outage GPS)")
    ax1.plot(
        aligned_est[:start_idx, 0],
        aligned_est[:start_idx, 2],
        "g-",
        linewidth=2.0,
        label="GPS Anchored Phase",
    )
    ax1.plot(
        aligned_est[start_idx:end_idx, 0],
        aligned_est[start_idx:end_idx, 2],
        "r--",
        linewidth=2.5,
        label="Dead-Reckoning (VO Only)",
    )
    ax1.scatter(
        gt_pts[start_idx, 0],
        gt_pts[start_idx, 2],
        color="red",
        s=80,
        zorder=5,
        label="GPS Loss Event",
    )
    ax1.set_title("Navigation Path Under GPS Loss", fontsize=11, fontweight="bold")
    ax1.set_xlabel("X Position [m]", fontsize=10)
    ax1.set_ylabel("Z Position [m]", fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(fontsize=8, loc="best")
    ax1.axis("equal")

    # 2. Cumulative Drift vs Distance Travelled
    ax2.plot(distances, drifts, "r-o", markersize=4, linewidth=1.5, label="Dead-Reckoning Drift")
    ax2.set_title("Drift Accumulation in Outage Zone", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Distance Traveled in Outage [m]", fontsize=10)
    ax2.set_ylabel("Position Error (Drift) [m]", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.5)

    stats_text = (
        f"Final Drift: {outage_res['final_drift_m']:.3f} m\n"
        f"Max Drift:   {outage_res['max_drift_m']:.3f} m\n"
        f"Drift Rate:  {outage_res['drift_pct']:.2f}% of dist"
    )
    ax2.text(
        0.05,
        0.80,
        stats_text,
        transform=ax2.transAxes,
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="wheat", alpha=0.5),
    )
    ax2.legend(fontsize=8, loc="lower right")

    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate GPS outage dead-reckoning drift")
    parser.add_argument(
        "--traj",
        default="results/csv/faster_orb_v1__icl_nuim__living_room_traj1_loop_trajectory.txt",
        help="Path to estimated TUM trajectory file",
    )
    parser.add_argument(
        "--gt",
        default="data/icl_nuim/living_room_traj1_loop/groundtruth.txt",
        help="Path to groundtruth TUM trajectory file",
    )
    parser.add_argument("--outage-start", type=int, default=15, help="Frame where GPS is lost")
    parser.add_argument("--output", default="results/figures/gps_outage_drift_analysis.png")
    args = parser.parse_args()

    traj_path = Path(args.traj)
    gt_path = Path(args.gt)

    if not traj_path.exists():
        print(f"Error: Trajectory file {traj_path} not found.")
        sys.exit(1)
    if not gt_path.exists():
        print(f"Error: Groundtruth file {gt_path} not found.")
        sys.exit(1)

    est_acc = PoseAccumulator.load_tum_format(traj_path)
    gt_acc = PoseAccumulator.load_tum_format(gt_path)

    print(f"Evaluating GPS Outage:")
    print(f"  Estimated poses: {len(est_acc.poses)}")
    print(f"  GT poses:        {len(gt_acc.poses)}")
    print(f"  Outage start:    Frame {args.outage_start}")

    outage_res = simulate_gps_outage(
        est_acc.poses,
        gt_acc.poses,
        outage_start_idx=args.outage_start,
    )

    print(f"\nResults:")
    print(f"  Total outage distance: {outage_res['total_distance_m']:.3f} m")
    print(f"  Mean drift:            {outage_res['mean_drift_m']:.3f} m")
    print(f"  Max drift:             {outage_res['max_drift_m']:.3f} m")
    print(f"  Final drift:           {outage_res['final_drift_m']:.3f} m")
    print(f"  Drift percentage:      {outage_res['drift_pct']:.2f}%")

    out_plot = plot_gps_outage_analysis(outage_res, args.output)
    print(f"\nSaved GPS outage drift figure: {out_plot}")


if __name__ == "__main__":
    main()
