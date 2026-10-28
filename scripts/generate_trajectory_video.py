"""
generate_trajectory_video.py — Renders an animated side-by-side MP4 video
demonstrating the Visual Odometry pipeline with live tracking and trajectory map.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np

from src.datasets.icl_nuim import load_icl_nuim_from_config
from experiments.runner import load_yaml
from src.features.config import config_from_yaml
from src.features.extractor import FeatureExtractor
from src.matching.matcher import match_and_filter, matches_to_point_arrays
from src.geometry.essential import estimate_pose
from src.geometry.pose import PoseAccumulator
from src.evaluation.ate import compute_ate

def generate_video(
    dataset_cfg_path="configs/datasets/demo.yaml",
    traj_tum_path="results/csv/orb_orb_v1__icl_nuim__demo_sequence_trajectory.txt",
    output_video_path="results/figures/vo_trajectory_demo.mp4",
    fps=10,
    outage_start=15,
    outage_end=35,
):
    ds_cfg = load_yaml(dataset_cfg_path)
    dataset = load_icl_nuim_from_config(ds_cfg)
    exp_cfg = load_yaml("configs/experiments/orb_orb.yaml")
    fc = config_from_yaml(exp_cfg)
    extractor = FeatureExtractor(fc)

    # Load estimated trajectory and align with GT
    acc = PoseAccumulator.load_tum_format(traj_tum_path)
    gt_poses = dataset.get_ground_truth_poses()
    ate_res = compute_ate(acc.poses, gt_poses, alignment="sim3")
    aligned_est_pos = ate_res.aligned_est_positions  # (N, 3)
    gt_pos = ate_res.gt_positions  # (N, 3)

    n_frames = len(dataset)
    frame_h, frame_w = 480, 640
    map_size = 480
    total_w = frame_w + map_size
    total_h = frame_h

    # Map bounds for trajectory plotting (X-Z plane)
    all_x = np.concatenate([gt_pos[:, 0], aligned_est_pos[:, 0]])
    all_z = np.concatenate([gt_pos[:, 2], aligned_est_pos[:, 2]])
    pad = 0.5
    min_x, max_x = all_x.min() - pad, all_x.max() + pad
    min_z, max_z = all_z.min() - pad, all_z.max() + pad

    def world_to_map(x, z):
        u = int(40 + (x - min_x) / (max_x - min_x) * (map_size - 80))
        # Invert Z so forward (+Z) points up on the screen
        v = int((map_size - 40) - (z - min_z) / (max_z - min_z) * (map_size - 80))
        return u, v

    output_path = Path(output_video_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (total_w, total_h))

    prev_gray = None
    prev_kps = None
    prev_descs = None

    for i in range(n_frames):
        img_gray = dataset.load_image_gray(i)
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
                            # Inlier match: green line
                            cv2.line(camera_panel, pt0, pt1, (0, 220, 0), 1)
                            cv2.circle(camera_panel, pt1, 3, (0, 255, 0), -1)
                        else:
                            # Outlier match: red line
                            cv2.line(camera_panel, pt0, pt1, (0, 0, 220), 1)
                            cv2.circle(camera_panel, pt1, 2, (0, 0, 255), -1)

        # GPS status logic
        is_outage = outage_start <= i <= outage_end
        gps_status = "SIGNAL DENIED (VO DEAD-RECKONING)" if is_outage else "GPS ACTIVE [FIX OK]"
        status_color = (0, 0, 255) if is_outage else (0, 255, 0)

        # HUD Overlay on Camera Panel
        cv2.rectangle(camera_panel, (10, 10), (frame_w - 10, 85), (20, 20, 20), -1)
        cv2.rectangle(camera_panel, (10, 10), (frame_w - 10, 85), status_color, 2)
        cv2.putText(camera_panel, f"NAVIGATION: {gps_status}", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)
        cv2.putText(camera_panel, f"Frame: {i:03d}/{n_frames}  |  Features: {len(curr_kps)}  |  Inliers: {n_inliers}",
                    (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)
        cv2.putText(camera_panel, f"Sensor: Monocular VO (FAST+ORB) | K: fx={dataset.camera.fx:.0f}",
                    (20, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 160, 160), 1)

        # 2. Right Panel: Bird's-Eye View Trajectory Map (X-Z)
        map_panel = np.full((map_size, map_size, 3), 30, dtype=np.uint8)

        # Grid lines
        for gx in range(0, map_size, 60):
            cv2.line(map_panel, (gx, 0), (gx, map_size), (45, 45, 45), 1)
        for gz in range(0, map_size, 60):
            cv2.line(map_panel, (0, gz), (map_size, gz), (45, 45, 45), 1)

        # Draw Full Ground Truth Trajectory (Dashed / Grey)
        for k in range(len(gt_pos) - 1):
            p_a = world_to_map(gt_pos[k, 0], gt_pos[k, 2])
            p_b = world_to_map(gt_pos[k + 1, 0], gt_pos[k + 1, 2])
            cv2.line(map_panel, p_a, p_b, (120, 120, 120), 2)

        # Draw Estimated VO Trajectory up to current frame (Blue / Cyan)
        for k in range(min(i, len(aligned_est_pos) - 1)):
            p_a = world_to_map(aligned_est_pos[k, 0], aligned_est_pos[k, 2])
            p_b = world_to_map(aligned_est_pos[k + 1, 0], aligned_est_pos[k + 1, 2])
            # If during outage, draw in orange/red
            seg_color = (0, 140, 255) if (outage_start <= k <= outage_end) else (255, 180, 0)
            cv2.line(map_panel, p_a, p_b, seg_color, 3)

        # Current Vehicle Position
        curr_u, curr_v = world_to_map(aligned_est_pos[i, 0], aligned_est_pos[i, 2])
        gt_u, gt_v = world_to_map(gt_pos[i, 0], gt_pos[i, 2])

        # GT marker (grey ring)
        cv2.circle(map_panel, (gt_u, gt_v), 6, (180, 180, 180), 2)
        # VO Current marker (filled color)
        curr_marker_color = (0, 80, 255) if is_outage else (255, 200, 0)
        cv2.circle(map_panel, (curr_u, curr_v), 7, curr_marker_color, -1)
        cv2.circle(map_panel, (curr_u, curr_v), 9, (255, 255, 255), 1)

        # Error line between GT and VO
        cv2.line(map_panel, (gt_u, gt_v), (curr_u, curr_v), (0, 0, 255), 1)
        curr_err = np.linalg.norm(aligned_est_pos[i] - gt_pos[i])

        # Map Header & Legend
        cv2.putText(map_panel, "TOP-DOWN MAP (X-Z PLANE)", (20, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(map_panel, "Grey: Ground Truth Path", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 150, 150), 1)
        cv2.putText(map_panel, "Cyan: Normal VO  |  Orange: GPS Outage", (20, 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 180, 0), 1)
        cv2.putText(map_panel, f"Instant Error: {curr_err*100:.1f} cm", (20, map_size - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2)

        # Combine Panels Side-by-Side
        combined_frame = np.hstack([camera_panel, map_panel])
        writer.write(combined_frame)

        prev_gray = img_gray
        prev_kps = curr_kps
        prev_descs = curr_descs

    writer.release()
    print(f"Generated video demo successfully: {output_video_path}")

if __name__ == "__main__":
    generate_video()

