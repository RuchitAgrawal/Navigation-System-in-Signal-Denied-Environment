"""
generate_demo_data.py — Generates a synthetic 3D visual dataset in TUM RGB-D format.
"""

from pathlib import Path
import numpy as np
import cv2
from scipy.spatial.transform import Rotation

def generate_demo_dataset(output_dir="data/demo_sequence", n_frames=40):
    output_path = Path(output_dir)
    rgb_dir = output_path / "rgb"
    rgb_dir.mkdir(parents=True, exist_ok=True)

    width, height = 640, 480
    fx, fy, cx, cy = 480.0, 480.0, 320.0, 240.0
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)

    # Generate 3D landmarks in the world
    rng = np.random.default_rng(12345)
    n_landmarks = 600
    points_3d = []
    marker_types = []
    marker_sizes = []
    marker_colors = []

    for _ in range(n_landmarks):
        # Distribute points in a corridor ahead of the camera
        x = rng.uniform(-3.5, 3.5)
        y = rng.uniform(-2.5, 2.5)
        z = rng.uniform(1.5, 7.0)
        points_3d.append([x, y, z])
        marker_types.append(rng.integers(0, 4))
        marker_sizes.append(rng.uniform(0.04, 0.12))
        marker_colors.append((int(rng.integers(30, 250)), int(rng.integers(30, 250)), int(rng.integers(30, 250))))

    points_3d = np.array(points_3d, dtype=np.float64)

    # Trajectory: smooth forward movement with gentle curve and heading change
    gt_poses = []
    timestamps = []
    rgb_lines = []
    gt_lines = []

    for i in range(n_frames):
        ts = i * 0.1
        timestamps.append(ts)

        # Camera trajectory in world coordinates (T_wc)
        # Translation
        tx = 0.25 * np.sin(0.12 * i)
        ty = 0.08 * np.sin(0.08 * i)
        tz = 0.09 * i
        t_wc = np.array([tx, ty, tz])

        # Slight rotation (yaw and pitch)
        yaw = 0.03 * np.sin(0.12 * i)
        pitch = 0.02 * np.cos(0.12 * i)
        rot = Rotation.from_euler("yxz", [yaw, pitch, 0.0])
        R_wc = rot.as_matrix()

        # T_wc (camera to world)
        T_wc = np.eye(4)
        T_wc[:3, :3] = R_wc
        T_wc[:3, 3] = t_wc
        gt_poses.append(T_wc)

        # Quaternion for TUM format (x, y, z, w)
        q = rot.as_quat()
        gt_lines.append(f"{ts:.6f} {tx:.6f} {ty:.6f} {tz:.6f} {q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}\n")

        filename = f"{i:04d}.png"
        rgb_lines.append(f"{ts:.6f} rgb/{filename}\n")

        # Render frame
        # Transform 3D points from world to camera: P_c = R_cw @ (P_w - t_wc) = R_wc.T @ (P_w - t_wc)
        R_cw = R_wc.T
        t_cw = -R_cw @ t_wc

        # Background with subtle gradient
        img = np.zeros((height, width, 3), dtype=np.uint8)
        # Add background grid lines / gradient
        for y_coord in range(0, height, 40):
            cv2.line(img, (0, y_coord), (width, y_coord), (40, 40, 40), 1)
        for x_coord in range(0, width, 40):
            cv2.line(img, (x_coord, 0), (x_coord, height), (40, 40, 40), 1)

        # Transform and sort points by depth (painter's algorithm)
        pts_c = (R_cw @ points_3d.T + t_cw[:, None]).T
        order = np.argsort(-pts_c[:, 2])

        for idx in order:
            pt_c = pts_c[idx]
            z_c = pt_c[2]
            if z_c <= 0.4:
                continue

            u = int(fx * pt_c[0] / z_c + cx)
            v = int(fy * pt_c[1] / z_c + cy)

            rad = int(fx * marker_sizes[idx] / z_c)
            rad = max(3, min(rad, 50))

            if -rad < u < width + rad and -rad < v < height + rad:
                color = marker_colors[idx]
                mtype = marker_types[idx]
                if mtype == 0:
                    cv2.circle(img, (u, v), rad, color, -1)
                    cv2.circle(img, (u, v), max(1, rad // 2), (255 - color[0], 255 - color[1], 255 - color[2]), -1)
                elif mtype == 1:
                    cv2.rectangle(img, (u - rad, v - rad), (u + rad, v + rad), color, -1)
                    cv2.rectangle(img, (u - rad // 2, v - rad // 2), (u + rad // 2, v + rad // 2), (255, 255, 255), 1)
                elif mtype == 2:
                    cv2.circle(img, (u, v), rad, color, 2)
                    cv2.drawMarker(img, (u, v), color, cv2.MARKER_CROSS, rad * 2, 2)
                else:
                    cv2.drawMarker(img, (u, v), color, cv2.MARKER_STAR, rad * 2, 2)

        # Save RGB image
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(str(rgb_dir / filename), img_gray)

    # Save rgb.txt and groundtruth.txt
    with open(output_path / "rgb.txt", "w") as f:
        f.write("# RGB frame index\n")
        f.writelines(rgb_lines)

    with open(output_path / "groundtruth.txt", "w") as f:
        f.write("# Groundtruth trajectory TUM format (timestamp tx ty tz qx qy qz qw)\n")
        f.writelines(gt_lines)

    print(f"Generated {n_frames} demo frames in {output_path}")

if __name__ == "__main__":
    generate_demo_dataset()

