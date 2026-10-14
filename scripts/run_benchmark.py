#!/usr/bin/env python
"""
run_benchmark.py — CLI: Run the full multi-config benchmark.

Runs all experiment configs × datasets as defined in
configs/experiments/benchmark.yaml.

Usage
-----
    python scripts/run_benchmark.py
    python scripts/run_benchmark.py --config configs/experiments/benchmark.yaml --output results/
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.benchmark import run_benchmark


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run full benchmark across all feature configurations and datasets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-c", "--config", default="configs/experiments/benchmark.yaml",
                        help="Path to benchmark YAML config.")
    parser.add_argument("-o", "--output", default="results",
                        help="Output root directory.")
    parser.add_argument("--alignment", choices=["sim3", "se3"], default="sim3")
    parser.add_argument("--rpe-delta", type=int, default=1)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    run_benchmark(
        benchmark_cfg_path=args.config,
        output_root=args.output,
        ate_alignment=args.alignment,
        rpe_delta=args.rpe_delta,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
