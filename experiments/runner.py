"""
runner.py — Single-experiment orchestrator.

Ties together dataset loading, feature config, VO pipeline,
evaluation, and result persistence for one (config, dataset) pair.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import yaml

from src.datasets.icl_nuim import load_icl_nuim_from_config
from src.datasets.tartanair import load_tartanair_from_config
from src.evaluation.ate import compute_ate
from src.evaluation.metrics import (
    build_summary_row,
    save_per_frame_csv,
    save_summary_csv,
)
from src.evaluation.rpe import compute_rpe
from src.features.config import config_from_yaml
from src.features.descriptor import get_implementation_label
from src.odometry.pipeline import VOPipeline
from src.odometry.tracker import compute_tracking_report
from src.geometry.pose import PoseAccumulator


def load_yaml(path: str | Path) -> dict:
    with open(path, encoding="utf-8-sig") as f:
        return yaml.safe_load(f)


def run_experiment(
    experiment_cfg_path: str | Path,
    dataset_cfg_path: str | Path,
    output_root: str | Path = "results",
    ate_alignment: str = "sim3",
    rpe_delta: int = 1,
    verbose: bool = True,
) -> dict:
    """Run one VO experiment and save all results.

    Parameters
    ----------
    experiment_cfg_path : path to experiment YAML (e.g., configs/experiments/orb_orb.yaml)
    dataset_cfg_path    : path to dataset YAML    (e.g., configs/datasets/icl_nuim.yaml)
    output_root         : root directory for results/
    ate_alignment       : 'sim3' or 'se3'
    rpe_delta           : frame interval for RPE
    verbose             : print progress

    Returns
    -------
    summary_row : dict  (can be collected across experiments for a summary CSV)
    """
    exp_cfg     = load_yaml(experiment_cfg_path)
    dataset_cfg = load_yaml(dataset_cfg_path)
    output_root = Path(output_root)

    exp_id      = exp_cfg["experiment_id"]
    dataset_name = dataset_cfg["dataset"]

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Experiment : {exp_id}")
        print(f"  Dataset    : {dataset_name}")
        print(f"{'='*60}")

    # --- Load dataset ---
    if dataset_name == "icl_nuim":
        dataset = load_icl_nuim_from_config(dataset_cfg)
    elif dataset_name == "tartanair":
        dataset = load_tartanair_from_config(dataset_cfg)
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    seq_name = dataset.sequence
    if verbose:
        print(f"  Sequence   : {seq_name}  ({len(dataset)} frames)")

    # --- Build feature config ---
    fc = config_from_yaml(exp_cfg)
    desc_label = get_implementation_label(fc.descriptor)
    if verbose:
        print(f"  Config     : {fc.detector_name} + {fc.descriptor_name} "
              f"(desc impl: {desc_label})")

    # --- Run VO ---
    tracking_cfg  = exp_cfg.get("tracking", {})
    ransac_cfg    = exp_cfg.get("ransac", {})
    match_cfg     = exp_cfg.get("matching", {})
    bucketing_cfg = exp_cfg.get("bucketing", {})
    refine_cfg    = exp_cfg.get("refinement", {})

    pipeline = VOPipeline(
        feature_config=fc,
        ransac_threshold=float(ransac_cfg.get("threshold", 1.0)),
        ransac_confidence=float(ransac_cfg.get("confidence", 0.999)),
        ransac_max_iter=int(ransac_cfg.get("max_iterations", 2000)),
        ratio_threshold=float(match_cfg.get("ratio_threshold", 0.75)),
        cross_check=bool(match_cfg.get("cross_check", False)),
        min_keypoints=int(tracking_cfg.get("min_keypoints", 8)),
        min_matches=int(tracking_cfg.get("min_matches", 8)),
        min_inlier_ratio=float(tracking_cfg.get("min_inlier_ratio", 0.10)),
        use_motion_model=bool(tracking_cfg.get("use_motion_model", True)),
        bucketing=str(bucketing_cfg.get("strategy", "none")),
        subpixel=bool(refine_cfg.get("subpixel", False)),
        max_features=int(bucketing_cfg.get("max_features", 2000)),
    )

    t_start = time.perf_counter()
    accumulator = pipeline.run(dataset)
    t_total = time.perf_counter() - t_start

    if verbose:
        print(f"  VO done in {t_total:.1f}s")

    # --- Evaluate ---
    gt_poses  = dataset.get_ground_truth_poses()
    est_poses = accumulator.poses

    ate_result = compute_ate(est_poses, gt_poses, alignment=ate_alignment)
    rpe_result = compute_rpe(est_poses, gt_poses, delta=rpe_delta)
    tracking   = compute_tracking_report(accumulator.diagnostics)

    if verbose:
        print(f"  ATE RMSE   : {ate_result.rmse:.4f} m  (scale={ate_result.scale:.4f})")
        print(f"  RPE trans  : {rpe_result.trans_rmse:.4f} m")
        print(f"  Tracking   : {tracking.success_rate*100:.1f}% success")

    # --- Save outputs ---
    run_tag = f"{exp_id}__{dataset_name}__{seq_name}"
    csv_dir = output_root / "csv"
    fig_dir = output_root / "figures"
    log_dir = output_root / "logs"

    # Per-frame CSV
    save_per_frame_csv(accumulator.diagnostics, csv_dir / f"{run_tag}_frames.csv")

    # Trajectory TUM file
    traj_path = csv_dir / f"{run_tag}_trajectory.txt"
    accumulator.save_tum_format(traj_path)

    # Summary row
    summary = build_summary_row(
        config_id=exp_id,
        dataset_name=dataset_name,
        sequence_name=seq_name,
        descriptor_label=desc_label,
        ate=ate_result,
        rpe=rpe_result,
        tracking=tracking,
        diagnostics=accumulator.diagnostics,
    )

    # JSON log
    log_dir.mkdir(parents=True, exist_ok=True)
    with open(log_dir / f"{run_tag}.json", "w") as f:
        json.dump({k: (v if not hasattr(v, "tolist") else v.tolist())
                   for k, v in summary.items()}, f, indent=2)

    if verbose:
        print(f"  Results saved to: {output_root}")

    return summary
