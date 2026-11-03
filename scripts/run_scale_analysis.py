"""
scripts/run_scale_analysis.py -- CLI for scale drift analysis over a sequence.

Runs a VO experiment and then computes the sliding-window local scale drift,
comparing estimated trajectory scale to ground truth.

Usage
-----
    python scripts/run_scale_analysis.py \\
        -e configs/experiments/orb_orb.yaml \\
        -d configs/datasets/icl_nuim.yaml \\
        --window 10
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.runner import run_experiment, load_yaml
from src.evaluation.drift import compute_scale_over_time
from src.datasets import load_dataset
import numpy as np


def parse_args():
    p = argparse.ArgumentParser(
        description="Run VO and analyse scale drift over the trajectory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-e", "--experiment", required=True)
    p.add_argument("-d", "--dataset", required=True)
    p.add_argument("-o", "--output", default="results")
    p.add_argument("--window", type=int, default=10,
                   help="Sliding window size for local scale estimation.")
    p.add_argument("--plot", default=None, help="Optional output PNG path for scale drift plot")
    return p.parse_args()


def main():
    args = parse_args()
    summary = run_experiment(args.experiment, args.dataset, args.output)

    ds_cfg  = load_yaml(args.dataset)
    dataset = load_dataset(ds_cfg)
    gt_poses = dataset.get_ground_truth_poses()

    # Load saved accumulator poses from TUM file
    from src.geometry.pose import PoseAccumulator
    from src.visualization.scale_plot import plot_scale_drift
    exp_cfg = load_yaml(args.experiment)
    exp_id  = exp_cfg["experiment_id"]
    seq     = ds_cfg.get("sequence", "seq")
    traj_path = Path(args.output) / "csv" / f"{exp_id}__{ds_cfg['dataset']}__{seq}_trajectory.txt"

    if not traj_path.exists():
        print(f"Trajectory file not found: {traj_path}")
        sys.exit(1)

    acc = PoseAccumulator.load_tum_format(traj_path)
    scales = compute_scale_over_time(acc.poses, gt_poses, window=args.window)
    finite = scales[np.isfinite(scales)]

    print(f"\n--- Scale Drift Analysis (window={args.window}) ---")
    if len(finite) > 0:
        print(f"  Mean local scale   : {np.mean(finite):.4f}")
        print(f"  Std local scale    : {np.std(finite):.4f}")
        print(f"  Min / Max          : {np.min(finite):.4f} / {np.max(finite):.4f}")
        print(f"  Frames analysed    : {len(finite)}")
    else:
        print("  No valid scale frames (check GT poses and trajectory length).")

    if args.plot:
        plot_path = Path(args.plot)
        plot_scale_drift(scales, exp_id, ds_cfg['dataset'], plot_path, window=args.window)
        print(f"Saved scale drift plot: {plot_path}")


if __name__ == "__main__":
    main()
