"""
benchmark.py — Multi-config benchmark orchestrator.

Iterates over all experiment configs × datasets defined in
configs/experiments/benchmark.yaml and collects results.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from experiments.runner import run_experiment
from src.evaluation.metrics import save_summary_csv
from src.visualization.trajectory_plot import plot_benchmark_comparison


def run_benchmark(
    benchmark_cfg_path: str | Path = "configs/experiments/benchmark.yaml",
    output_root: str | Path = "results",
    ate_alignment: str = "sim3",
    rpe_delta: int = 1,
    verbose: bool = True,
) -> None:
    """Run all experiment × dataset combinations and aggregate results.

    Parameters
    ----------
    benchmark_cfg_path : path to benchmark YAML
    output_root        : root directory for all results
    ate_alignment      : 'sim3' or 'se3'
    rpe_delta          : frame interval for RPE
    verbose            : print progress
    """
    with open(benchmark_cfg_path, encoding="utf-8-sig") as f:
        bench_cfg = yaml.safe_load(f)

    exp_configs     = bench_cfg.get("configs", [])
    dataset_configs = bench_cfg.get("datasets", [])
    output_root     = Path(output_root)

    all_summaries = []
    failed_runs   = []

    for exp_path in exp_configs:
        for ds_path in dataset_configs:
            try:
                row = run_experiment(
                    experiment_cfg_path=exp_path,
                    dataset_cfg_path=ds_path,
                    output_root=output_root,
                    ate_alignment=ate_alignment,
                    rpe_delta=rpe_delta,
                    verbose=verbose,
                )
                all_summaries.append(row)
            except FileNotFoundError as e:
                if verbose:
                    print(f"  [SKIP] {exp_path} × {ds_path}: {e}")
                failed_runs.append({"exp": str(exp_path), "ds": str(ds_path), "error": str(e)})
            except Exception as e:
                if verbose:
                    print(f"  [ERROR] {exp_path} × {ds_path}: {e}")
                failed_runs.append({"exp": str(exp_path), "ds": str(ds_path), "error": str(e)})

    # Save aggregate summary CSV
    if all_summaries:
        save_summary_csv(all_summaries, output_root / "csv" / "benchmark_summary.csv")
        if verbose:
            print(f"\nSummary CSV saved: {output_root}/csv/benchmark_summary.csv")

        # Benchmark comparison plots
        datasets_seen = set(r["dataset"] for r in all_summaries)
        for ds_name in datasets_seen:
            plot_benchmark_comparison(
                all_summaries,
                dataset_name=ds_name,
                save_path=output_root / "figures" / f"benchmark_{ds_name}.png",
            )

    if failed_runs and verbose:
        print(f"\n[WARNING] {len(failed_runs)} run(s) failed:")
        for fr in failed_runs:
            print(f"  {fr['exp']} × {fr['ds']}: {fr['error']}")


if __name__ == "__main__":
    run_benchmark()
