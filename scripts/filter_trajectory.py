#!/usr/bin/env python
"""
filter_trajectory.py — CLI utility for trajectory post-smoothing and outlier rejection.

Loads a TUM-format trajectory, applies moving-average smoothing and step outlier
filtering, saves the cleaned trajectory, and optionally evaluates ATE before and after.

Usage
-----
    python scripts/filter_trajectory.py \\
        --in-traj results/csv/faster_orb_v1__icl_nuim__living_room_traj1_loop_trajectory.txt \\
        --out-traj results/csv/faster_orb_smoothed_trajectory.txt \\
        --gt data/icl_nuim/living_room_traj1_loop/groundtruth.txt \\
        --window 5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.geometry.pose import PoseAccumulator
from src.odometry.filter import smooth_trajectory_poses, filter_outlier_steps
from src.evaluation.ate import compute_ate


def parse_args():
    parser = argparse.ArgumentParser(description="Smooth and clean raw visual odometry trajectory")
    parser.add_argument("--in-traj", required=True, help="Input raw TUM trajectory path")
    parser.add_argument("--out-traj", required=True, help="Output smoothed TUM trajectory path")
    parser.add_argument("--gt", default=None, help="Optional ground-truth TUM file to compare ATE")
    parser.add_argument("--window", type=int, default=5, help="Moving average window size")
    parser.add_argument("--max-step", type=float, default=2.0, help="Max step distance threshold for outliers")
    return parser.parse_args()


def main():
    args = parse_args()
    in_path = Path(args.in_traj)
    out_path = Path(args.out_traj)

    if not in_path.exists():
        print(f"Error: Input trajectory {in_path} does not exist.")
        sys.exit(1)

    acc = PoseAccumulator.load_tum_format(in_path)
    raw_poses = acc.poses
    timestamps = acc.timestamps

    print(f"Loaded {len(raw_poses)} poses from {in_path}")

    # 1. Reject outlier jumps
    filtered_poses = filter_outlier_steps(raw_poses, max_step_distance=args.max_step)

    # 2. Smooth trajectory
    smoothed_poses = smooth_trajectory_poses(filtered_poses, window_size=args.window)

    # 3. Save output
    out_acc = PoseAccumulator(poses=smoothed_poses, timestamps=timestamps)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_acc.save_tum_format(out_path)
    print(f"Saved smoothed trajectory to {out_path}")

    # 4. Optional ATE comparison
    if args.gt:
        gt_path = Path(args.gt)
        if gt_path.exists():
            gt_acc = PoseAccumulator.load_tum_format(gt_path)
            n = min(len(raw_poses), len(gt_acc.poses))
            ate_raw = compute_ate(raw_poses[:n], gt_acc.poses[:n], alignment="sim3")
            ate_smooth = compute_ate(smoothed_poses[:n], gt_acc.poses[:n], alignment="sim3")

            print("\nATE Comparison (Sim3 alignment):")
            print(f"  Raw Trajectory ATE RMSE:      {ate_raw.rmse:.6f} m")
            print(f"  Smoothed Trajectory ATE RMSE: {ate_smooth.rmse:.6f} m")
            diff = (ate_raw.rmse - ate_smooth.rmse) / ate_raw.rmse * 100
            print(f"  Improvement:                  {diff:+.2f}%")


if __name__ == "__main__":
    main()
