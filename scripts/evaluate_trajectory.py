#!/usr/bin/env python
"""
evaluate_trajectory.py — CLI: Evaluate a saved trajectory against ground truth.

Loads a TUM-format estimated trajectory and a TUM-format ground-truth file,
computes ATE and RPE, and prints the results.

Usage
-----
    python scripts/evaluate_trajectory.py \\
        --est results/csv/orb_orb__icl_nuim__living_room_traj1_loop_trajectory.txt \\
        --gt  data/icl_nuim/living_room_traj1_loop/groundtruth.txt \\
        --alignment sim3
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.geometry.pose import PoseAccumulator
from src.evaluation.ate import compute_ate
from src.evaluation.rpe import compute_rpe


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate a saved TUM-format trajectory against ground truth.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--est", required=True,
                        help="Path to estimated trajectory (TUM format).")
    parser.add_argument("--gt", required=True,
                        help="Path to ground-truth trajectory (TUM format).")
    parser.add_argument("--alignment", choices=["sim3", "se3"], default="sim3")
    parser.add_argument("--rpe-delta", type=int, default=1)
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Loading estimated trajectory: {args.est}")
    est_acc = PoseAccumulator.load_tum_format(args.est)

    print(f"Loading ground-truth:         {args.gt}")
    gt_acc  = PoseAccumulator.load_tum_format(args.gt)

    n_est = len(est_acc.poses)
    n_gt  = len(gt_acc.poses)
    print(f"  Estimated frames : {n_est}")
    print(f"  GT frames        : {n_gt}")

    # Align by count (take the shorter)
    n = min(n_est, n_gt)
    est_poses = est_acc.poses[:n]
    gt_poses  = gt_acc.poses[:n]

    ate = compute_ate(est_poses, gt_poses, alignment=args.alignment)
    rpe = compute_rpe(est_poses, gt_poses, delta=args.rpe_delta)

    print(f"\n--- ATE ({args.alignment.upper()} alignment) ---")
    print(f"  RMSE   : {ate.rmse:.6f} m")
    print(f"  Mean   : {ate.mean:.6f} m")
    print(f"  Median : {ate.median:.6f} m")
    print(f"  Std    : {ate.std:.6f} m")
    print(f"  Scale  : {ate.scale:.6f}")
    print(f"  Frames : {ate.n_frames}")

    print(f"\n--- RPE (delta={args.rpe_delta} frames) ---")
    print(f"  Trans RMSE : {rpe.trans_rmse:.6f} m")
    print(f"  Trans mean : {rpe.trans_mean:.6f} m")
    print(f"  Rot RMSE   : {rpe.rot_rmse_deg:.4f} deg")
    print(f"  Pairs      : {rpe.n_pairs}")


if __name__ == "__main__":
    main()
