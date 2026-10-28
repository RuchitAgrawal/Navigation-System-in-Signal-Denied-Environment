"""
run_demo.py — End-to-end demonstration of the Visual Odometry module.

Executes:
1. Synthetic dataset check / generation.
2. Feature extraction & matching with inlier/outlier plot.
3. VO trajectory estimation & evaluation (ATE Sim(3), RPE).
4. Trajectory plotting (estimated vs ground truth).
5. Scale drift analysis and plotting.
6. Simulated GPS outage test and plotting.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np

from scripts.generate_demo_data import generate_demo_dataset
from experiments.runner import run_experiment, load_yaml
from src.datasets.icl_nuim import load_icl_nuim_from_config
from src.features.config import config_from_yaml
from src.features.extractor import FeatureExtractor
from src.geometry.essential import estimate_pose
from src.geometry.pose import PoseAccumulator
from src.matching.matcher import match_and_filter, matches_to_point_arrays
from src.evaluation.ate import compute_ate
from src.evaluation.drift import compute_scale_over_time
from src.visualization.trajectory_plot import plot_trajectory_2d
from src.visualization.match_plot import draw_matches_inliers_outliers
from src.visualization.scale_plot import plot_scale_drift
from experiments.gps_outage import simulate_gps_outage

def main():
    print("=" * 65)
    print("  VISUAL ODOMETRY MODULE — END-TO-END DEMONSTRATION")
    print("=" * 65)

    data_dir = Path("data/demo_sequence")
    if not (data_dir / "rgb.txt").exists():
        print("\n[Step 1/5] Generating demo 3D textured visual sequence...")
        generate_demo_dataset("data/demo_sequence", n_frames=40)
    else:
        print("\n[Step 1/5] Demo dataset verified at data/demo_sequence.")

    # 2. Visual feature match sample
    print("\n[Step 2/5] Extracting visual features & matching frame 0 -> frame 1...")
    exp_cfg = load_yaml("configs/experiments/orb_orb.yaml")
    ds_cfg = load_yaml("configs/datasets/demo.yaml")
    dataset = load_icl_nuim_from_config(ds_cfg)

    fc = config_from_yaml(exp_cfg)
    extractor = FeatureExtractor(fc)

    img0 = dataset.load_image_gray(0)
    img1 = dataset.load_image_gray(1)
    res0 = extractor.extract(img0)
    res1 = extractor.extract(img1)

    raw_matches, good_matches = match_and_filter(
        res0.descriptors, res1.descriptors,
        norm_type=fc.norm_type,
        ratio_threshold=0.75
    )
    pts0, pts1 = matches_to_point_arrays(good_matches, res0.keypoints, res1.keypoints)
    pose_res = estimate_pose(pts0, pts1, dataset.camera.K)
    inlier_mask = pose_res.inlier_mask

    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    match_fig_path = fig_dir / "feature_matches_sample.png"
    draw_matches_inliers_outliers(
        img0, img1, res0.keypoints, res1.keypoints, good_matches, inlier_mask,
        save_path=match_fig_path, frame_idx=1
    )
    n_inliers = int(inlier_mask.sum()) if inlier_mask is not None else len(good_matches)
    print(f"  Keypoints frame 0: {len(res0.keypoints)}")
    print(f"  Keypoints frame 1: {len(res1.keypoints)}")
    print(f"  Matches: {len(good_matches)} (Inliers: {n_inliers}, {n_inliers/len(good_matches)*100:.1f}%)")
    print(f"  Saved match figure: {match_fig_path}")

    # 3. Run full VO experiment
    print("\n[Step 3/5] Running visual odometry trajectory estimation...")
    summary = run_experiment(
        "configs/experiments/orb_orb.yaml",
        "configs/datasets/demo.yaml",
        output_root="results",
        ate_alignment="sim3",
        verbose=False
    )
    print(f"  Frames processed: {summary['total_frames']}")
    print(f"  Tracking success: {summary['tracking_success_pct']}%")
    print(f"  ATE RMSE (Sim3): {summary['ate_rmse_m']:.4f} m (Scale factor: {summary['ate_scale']:.4f})")
    print(f"  Mean processing FPS: {summary['mean_fps']:.1f} fps")

    # 4. Generate Trajectory Plot & Scale Drift Plot
    print("\n[Step 4/5] Generating trajectory comparison & scale drift plots...")
    traj_path = Path("results/csv/orb_orb_v1__icl_nuim__demo_sequence_trajectory.txt")
    acc = PoseAccumulator.load_tum_format(traj_path)
    gt_poses = dataset.get_ground_truth_poses()

    ate_res = compute_ate(acc.poses, gt_poses, alignment="sim3")
    traj_fig_path = fig_dir / "trajectory_comparison.png"
    plot_trajectory_2d(
        ate_res,
        acc.get_positions(),
        config_id="ORB_ORB",
        dataset_name="demo",
        sequence_name="demo_sequence",
        save_path=traj_fig_path
    )
    print(f"  Saved trajectory plot: {traj_fig_path}")

    scales = compute_scale_over_time(acc.poses, gt_poses, window=5)
    scale_fig_path = fig_dir / "scale_drift.png"
    plot_scale_drift(scales, config_id="ORB_ORB", dataset_name="demo", save_path=scale_fig_path, window=5)
    print(f"  Saved scale drift plot: {scale_fig_path}")

    # 5. GPS Outage Simulation
    print("\n[Step 5/5] Running simulated GPS-denied outage experiment...")
    outage_res = simulate_gps_outage(
        accumulator=acc,
        gt_poses=gt_poses,
        outage_start=15,
        outage_end=35,
        output_root="results",
        config_id="orb_orb",
        dataset_name="demo",
        sequence_name="demo_sequence",
        verbose=False
    )
    print(f"  Simulated outage interval: frames {outage_res['outage_start_frame']} to {outage_res['outage_end_frame']}")
    print(f"  Max drift during outage:   {outage_res['max_drift_m']:.4f} m")
    print(f"  Final drift at reconnection: {outage_res['final_drift_m']:.4f} m")
    print(f"  Saved GPS outage plot: results/figures/gps_outage_orb_orb_demo.png")

    print("\n" + "=" * 65)
    print("  DEMONSTRATION COMPLETE — ALL OUTPUTS GENERATED SUCCESSFULLY")
    print("=" * 65)

if __name__ == "__main__":
    main()
