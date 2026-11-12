"""
scripts/run_full_benchmark.py
─────────────────────────────
Convenience entry point: runs all four feature configurations against every
dataset sequence found in data/, prints a formatted summary table, and writes
results to results/benchmark/.

Usage
-----
  python scripts/run_full_benchmark.py
  python scripts/run_full_benchmark.py --dataset icl_nuim --sequence living_room_traj1_loop
  python scripts/run_full_benchmark.py --configs orb_orb fast_orb --verbose
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.benchmark import run_benchmark, CONFIGS
from src.evaluation.summary import rank_configs


# ──────────────────────────────────────────────────────────────────────────────
# Config registry (must match experiments/benchmark.py)
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_SEQUENCES = {
    "icl_nuim": ["living_room_traj1_loop", "office_room_traj0_loop"],
    "tartanair": ["ocean/Easy/P000", "abandonedfactory/Easy/P000"],
}


def _print_table(rows: list[dict], metric_cols: list[str]) -> None:
    """Print a fixed-width ASCII results table."""
    col_w = 22
    header_cols = ["config", "dataset", "sequence"] + metric_cols
    sep = "+" + "+".join("-" * col_w for _ in header_cols) + "+"
    header = "|" + "|".join(c.center(col_w) for c in header_cols) + "|"
    print(sep)
    print(header)
    print(sep)
    for r in rows:
        def fmt(v):
            if v is None:
                return "—".center(col_w)
            if isinstance(v, float):
                return f"{v:.4f}".center(col_w)
            return str(v).center(col_w)

        row_str = "|" + "|".join(
            fmt(r.get(c)) for c in header_cols
        ) + "|"
        print(row_str)
    print(sep)


def _save_csv(rows: list[dict], out_path: Path) -> None:
    if not rows:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"[saved] {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full VO benchmark suite")
    parser.add_argument(
        "--dataset",
        choices=list(DEFAULT_SEQUENCES),
        default=None,
        help="Restrict to one dataset type (default: all)",
    )
    parser.add_argument(
        "--sequence",
        default=None,
        help="Restrict to one sequence name",
    )
    parser.add_argument(
        "--configs",
        nargs="+",
        default=None,
        choices=list(CONFIGS.keys()),
        help="Feature configs to run (default: all four)",
    )
    parser.add_argument(
        "--data-root",
        default=str(ROOT / "data"),
        help="Root directory containing dataset folders",
    )
    parser.add_argument(
        "--results-dir",
        default=str(ROOT / "results" / "benchmark"),
        help="Output directory for CSVs and plots",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    data_root = Path(args.data_root)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Build work list: (dataset_type, sequence_path)
    work: list[tuple[str, Path]] = []
    datasets_to_check = (
        {args.dataset: DEFAULT_SEQUENCES[args.dataset]}
        if args.dataset
        else DEFAULT_SEQUENCES
    )
    for ds_type, sequences in datasets_to_check.items():
        for seq in sequences:
            if args.sequence and seq != args.sequence:
                continue
            seq_path = data_root / ds_type / seq
            if not seq_path.exists():
                print(f"[skip] {ds_type}/{seq} — not found at {seq_path}")
                continue
            work.append((ds_type, seq_path))

    if not work:
        print("\n[ERROR] No dataset sequences found. Have you downloaded the data?")
        print("        Run:  python scripts/download_datasets.py --sequence living_room_traj1_loop")
        print("        Or:   python scripts/download_datasets.py --manual-steps")
        sys.exit(1)

    configs_to_run = args.configs or list(CONFIGS.keys())
    print(f"\n{'='*60}")
    print(f"  Visual Odometry Benchmark")
    print(f"  Configs : {', '.join(configs_to_run)}")
    print(f"  Sequences: {len(work)}")
    print(f"{'='*60}\n")

    all_rows: list[dict] = []
    t0_total = time.perf_counter()

    for ds_type, seq_path in work:
        seq_name = seq_path.name
        print(f"\n── {ds_type} / {seq_name} ──")
        rows = run_benchmark(
            dataset_type=ds_type,
            sequence_path=seq_path,
            configs=configs_to_run,
            results_dir=results_dir / ds_type / seq_name,
            verbose=args.verbose,
        )
        for r in rows:
            r["dataset"] = ds_type
            r["sequence"] = seq_name
        all_rows.extend(rows)

    elapsed = time.perf_counter() - t0_total
    print(f"\n{'='*60}")
    print(f"  Benchmark complete in {elapsed:.1f}s")
    print(f"{'='*60}\n")

    metric_cols = ["ate_rmse_m", "rpe_trans_rmse", "mean_fps", "tracking_rate_pct"]
    _print_table(all_rows, metric_cols)

    # Rankings
    if all_rows:
        print("\nRankings by ATE RMSE (lower = better):")
        for r in rank_configs(all_rows, metric="ate_rmse_m"):
            print(f"  #{r['rank']}  {r['config_id']:<18}  "
                  f"mean ATE = {r.get('mean_ate_rmse_m', r.get('mean_ate_rmse_m', '—')):.4f} m")

    _save_csv(all_rows, results_dir / "summary.csv")
    print(f"\nAll outputs in: {results_dir}")


if __name__ == "__main__":
    main()
