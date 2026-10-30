#!/usr/bin/env python
"""
generate_trajectory_video.py — Renders an animated side-by-side MP4 video
demonstrating the Visual Odometry pipeline with live tracking and trajectory map.
Supports both ICL-NUIM (indoor) and TartanAir (outdoor) sequences.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.datasets import load_dataset
from experiments.runner import load_yaml
from src.features.config import config_from_yaml
from src.features.extractor import FeatureExtractor
from src.matching.matcher import match_and_filter, matches_to_point_arrays
from src.geometry.essential import estimate_pose
from src.geometry.pose import PoseAccumulator
from src.evaluation.ate import compute_ate


def generate_video(
    dataset_cfg_path: str | Path = "configs/datasets/icl_nuim.yaml",
    experiment_cfg_path: str | Path = "configs/experiments/faster_orb.yaml",
    traj_tum_path: Optional[str | Path] = None,
    output_video_path: str | Path = "results/figures/vo_trajectory_demo.mp4",
    fps: int = 15,
    outage_start: int = 15,
    outage_end: int = 35,
    max_frames: Optional[int] = None,
) -> Path:
    """Render an animated side-by-side MP4 trajectory and camera video dashboard."""
    ds_cfg = load_yaml(dataset_cfg_path)
    dataset = load_dataset(ds_cfg)

    exp_cfg = load_yaml(experiment_cfg_path)
    fc = config_from_yaml(exp_cfg)
    extractor = FeatureExtractor(fc)

    # Determine trajectory path if not explicitly provided
    if traj_tum_path is None:
        exp_id = exp_cfg.get("experiment_id", "vo_exp")
        ds_name = ds_cfg.get("dataset", "dataset")
        seq = ds_cfg.get("sequence", "seq")
        traj_tum_path = Path("results/csv") / f"{exp_id}__{ds_name}__{seq}_trajectory.txt"

    traj_path = Path(traj_tum_path)
    if not traj_path.exists():
        raise FileNotFoundError(f"Trajectory file not found: {traj_path}")

    # Load estimated trajectory and align with GT
    acc = PoseAccumulator.load_tum_format(traj_path)
    gt_poses = dataset.get_ground_truth_poses()

    n_frames = min(len(dataset), len(acc.poses))
    if max_frames is not None:
        n_frames = min(n_frames, max_frames)

    ate_res = compute_ate(acc.poses[:n_frames], gt_poses[:n_frames], alignment="sim3")
    aligned_est_pos = ate_res.aligned_est_positions  # (N, 3)
    gt_pos = ate_res.gt_positions  # (N, 3)

    frame_h, frame_w = 480, 640
    map_size = 480
    total_w = frame_w + map_size
    total_h = frame_h

    # Map bounds for trajectory plotting (X-Z plane)
    all_x = np.concatenate([gt_pos[:, 0], aligned_est_pos[:, 0]])
    all_z = np.concatenate([gt_pos[:, 2], aligned_est_pos[:, 2]])
    pad = max(0.5, float(np.std(all_x) * 0.2), float(np.std(all_z) * 0.2))
    min_x, max_x = all_x.min() - pad, all_x.max() + pad
    min_z, max_z = all_z.min() - pad, all_z.max() + pad

    span_x = max(max_x - min_x, 1e-4)
    span_z = max(max_z - min_z, 1e-4)

    def world_to_map(x: float, z: float) -> tuple[int, int]:
        u = int(40 + (x - min_x) / span_x * (map_size - 80))
        v = int((map_size - 40) - (z - min_z) / span_z * (map_size - 80))
        return max(0, min(u, map_size - 1)), max(0, min(v, map_size - 1))

    output_path = Path(output_video_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (total_w, total_h))

    prev_kps = None
    prev_descs = None

    for i in range(n_frames):
        img_gray = dataset.load_image_gray(i)
        if img_gray.shape[:2] != (frame_h, frame_w):
            img_gray = cv2.resize(img_gray, (frame_w, frame_h))

        curr_res = extractor.extract(img_gray)
        curr_kps, curr_descs = curr_res.keypoints, curr_res.descriptors

        # 1. Left Panel: Camera frame with feature tracking
        camera_panel = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

        # Draw matches from previous frame
        n_inliers = 0
        if prev_descs is not None and len(prev_kps) > 0 and len(curr_kps) > 0:
            raw_matches, good_matches = match_and_filter(
                prev_descs, curr_descs, norm_type=fc.norm_type, ratio_threshold=0.75
            )
            pts_prev, pts_curr = matches_to_point_arrays(good_matches, prev_kps, curr_kps)
            if len(pts_prev) >= 8:
                pose_res = estimate_pose(pts_prev, pts_curr, dataset.camera.K)
                mask = pose_res.inlier_mask
                if mask is not None:
                    n_inliers = int(mask.sum())
                    for m_idx, (p0, p1) in enumerate(zip(pts_prev, pts_curr)):
                        pt0 = (int(p0[0]), int(p0[1]))
                        pt1 = (int(p1[0]), int(p1[1]))
                        if mask[m_idx]:
                            cv2.line(camera_panel, pt0, pt1, (0, 220, 0), 1)
                            cv2.circle(camera_panel, pt1, 3, (0, 255, 0), -1)
                        else:
                            cv2.line(camera_panel, pt0, pt1, (0, 0, 220), 1)
                            cv2.circle(camera_panel, pt1, 2, (0, 0, 255), -1)

        # GPS status logic
        is_outage = outage_start <= i <= outage_end
        gps_status = "SIGNAL DENIED (DEAD-RECKONING)" if is_outage else "GPS CARRIER LOCK [FIX OK]"
        status_color = (0, 0, 255) if is_outage else (0, 255, 0)

        # HUD Overlay on Camera Panel
        cv2.rectangle(camera_panel, (10, 10), (frame_w - 10, 85), (20, 20, 20), -1)
        cv2.rectangle(camera_panel, (10, 10), (frame_w - 10, 85), status_color, 2)
        cv2.putText(
            camera_panel,
            f"NAVIGATION: {gps_status}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            status_color,
            2,
        )
        cv2.putText(
            camera_panel,
            f"Frame: {i:03d}/{n_frames}  |  Features: {len(curr_kps)}  |  Inliers: {n_inliers}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (220, 220, 220),
            1,
        )
        cv2.putText(
            camera_panel,
            f"Config: {fc.detector_name}+{fc.descriptor_name} | Dataset: {ds_cfg.get('dataset', 'ds')}",
            (20, 78),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (160, 160, 160),
            1,
        )

        # 2. Right Panel: Bird's-Eye View Trajectory Map (X-Z)
        map_panel = np.full((map_size, map_size, 3), 30, dtype=np.uint8)

        # Grid lines
        for gx in range(0, map_size, 60):
            cv2.line(map_panel, (gx, 0), (gx, map_size), (45, 45, 45), 1)
        for gz in range(0, map_size, 60):
            cv2.line(map_panel, (0, gz), (map_size, gz), (45, 45, 45), 1)

        # Ground Truth Path
        for k in range(len(gt_pos) - 1):
            p_a = world_to_map(gt_pos[k, 0], gt_pos[k, 2])
            p_b = world_to_map(gt_pos[k + 1, 0], gt_pos[k + 1, 2])
            cv2.line(map_panel, p_a, p_b, (120, 120, 120), 2)

        # Estimated VO Path up to current frame
        for k in range(min(i, len(aligned_est_pos) - 1)):
            p_a = world_to_map(aligned_est_pos[k, 0], aligned_est_pos[k, 2])
            p_b = world_to_map(aligned_est_pos[k + 1, 0], aligned_est_pos[k + 1, 2])
            seg_color = (0, 140, 255) if (outage_start <= k <= outage_end) else (255, 180, 0)
            cv2.line(map_panel, p_a, p_b, seg_color, 3)

        # Current Vehicle Position
        curr_u, curr_v = world_to_map(aligned_est_pos[i, 0], aligned_est_pos[i, 2])
        gt_u, gt_v = world_to_map(gt_pos[i, 0], gt_pos[i, 2])

        cv2.circle(map_panel, (gt_u, gt_v), 6, (180, 180, 180), 2)
        curr_marker_color = (0, 80, 255) if is_outage else (255, 200, 0)
        cv2.circle(map_panel, (curr_u, curr_v), 7, curr_marker_color, -1)
        cv2.circle(map_panel, (curr_u, curr_v), 9, (255, 255, 255), 1)

        cv2.line(map_panel, (gt_u, gt_v), (curr_u, curr_v), (0, 0, 255), 1)
        curr_err = np.linalg.norm(aligned_est_pos[i] - gt_pos[i])

        cv2.putText(
            map_panel,
            "TOP-DOWN MAP (X-Z PLANE)",
            (20, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            map_panel,
            "Grey: Ground Truth Path",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (150, 150, 150),
            1,
        )
        cv2.putText(
            map_panel,
            "Cyan: Normal VO  |  Orange: GPS Outage",
            (20, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (255, 180, 0),
            1,
        )
        cv2.putText(
            map_panel,
            f"Instant Error: {curr_err*100:.1f} cm",
            (20, map_size - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 220, 255),
            2,
        )

        combined_frame = np.hstack([camera_panel, map_panel])
        writer.write(combined_frame)

        prev_kps = curr_kps
        prev_descs = curr_descs

    writer.release()
    print(f"Generated video demo successfully: {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate side-by-side VO trajectory video dashboard")
    parser.add_argument("--dataset-cfg", default="configs/datasets/icl_nuim.yaml", help="Dataset YAML path")
    parser.add_argument("--exp-cfg", default="configs/experiments/faster_orb.yaml", help="Experiment YAML path")
    parser.add_argument("--traj", default=None, help="Trajectory TUM file path (auto-detected if None)")
    parser.add_argument("--output", default="results/figures/vo_trajectory_demo.mp4", help="Output MP4 path")
    parser.add_argument("--fps", type=int, default=15, help="Video framerate")
    parser.add_argument("--outage-start", type=int, default=15, help="Outage start frame")
    parser.add_argument("--outage-end", type=int, default=35, help="Outage end frame")
    parser.add_argument("--max-frames", type=int, default=None, help="Max frames to render")
    args = parser.parse_args()

    generate_video(
        dataset_cfg_path=args.dataset_cfg,
        experiment_cfg_path=args.exp_cfg,
        traj_tum_path=args.traj,
        output_video_path=args.output,
        fps=args.fps,
        outage_start=args.outage_start,
        outage_end=args.outage_end,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    main()
