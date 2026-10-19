#!/usr/bin/env python
"""
run_vo.py â€” CLI: Run one VO experiment on one dataset.

Usage
-----
    python scripts/run_vo.py \\
        --experiment configs/experiments/orb_orb.yaml \\
        --dataset    configs/datasets/icl_nuim.yaml \\
        --output     results/ \\
        --alignment  sim3

Examples
--------
    # Baseline ORB+ORB on ICL-NUIM
    python scripts/run_vo.py -e configs/experiments/orb_orb.yaml -d configs/datasets/icl_nuim.yaml

    # FAST+ORB on TartanAir with SE(3) alignment
    python scripts/run_vo.py -e configs/experiments/fast_orb.yaml \\
        -d configs/datasets/tartanair.yaml --alignment se3
"""

import argparse
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.runner import run_experiment


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a single visual odometry experiment.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-e", "--experiment", required=True,
                        help="Path to experiment YAML config.")
    parser.add_argument("-d", "--dataset", required=True,
                        help="Path to dataset YAML config.")
    parser.add_argument("-o", "--output", default="results",
                        help="Output root directory.")
    parser.add_argument("--alignment", choices=["sim3", "se3"], default="sim3",
                        help="Trajectory alignment method for ATE.")
    parser.add_argument("--rpe-delta", type=int, default=1,
                        help="Frame interval for RPE computation.")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress output.")
    return parser.parse_args()


def main():
    args = parse_args()
    summary = run_experiment(
        experiment_cfg_path=args.experiment,
        dataset_cfg_path=args.dataset,
        output_root=args.output,
        ate_alignment=args.alignment,
        rpe_delta=args.rpe_delta,
        verbose=not args.quiet,
    )
    print("\n--- Summary ---")
    for k, v in summary.items():
        print(f"  {k:<30s} {v}")


if __name__ == "__main__":
    main()

