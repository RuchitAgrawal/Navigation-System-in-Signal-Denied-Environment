"""
live_dashboard.py — Real-time Visual Odometry Dashboard

Runs the full VO pipeline on a LIVE webcam feed and renders a 3-panel
OpenCV dashboard:

  ┌────────────────────────┬────────────────────────┐
  │                        │                        │
  │  LIVE CAMERA + FEATURES│    TRAJECTORY MAP      │
  │  (keypoints + matches) │    (bird's-eye path)   │
  │                        │                        │
  ├────────────────────────┴────────────────────────┤
  │  STATUS BAR: FPS | Features | Matches | GPS Mode│
  └─────────────────────────────────────────────────┘

Controls
--------
  Q  — quit
  R  — reset trajectory (new run)
  G  — toggle GPS DENIED mode (simulates outage)
  S  — save screenshot to results/figures/
  +  — increase FAST threshold (fewer features)
  -  — decrease FAST threshold (more features)

Usage
-----
  cd Navigation-System-in-Signal-Denied-Environment
  python scripts/live_dashboard.py

  # With a specific camera index (default 0):
  python scripts/live_dashboard.py --camera 1

  # With known focal length (better trajectory):
  python scripts/live_dashboard.py --focal-length 800
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

# ── Add project root to path so src.* imports work ──────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.features.config import build_feature_config
from src.features.extractor import FeatureExtractor
from src.geometry.essential import estimate_pose
from src.geometry.transforms import make_pose, invert_pose, compose_poses
from src.matching.matcher import match_and_filter, matches_to_point_arrays
from src.odometry.motion_model import ConstantVelocityMotionModel


# ════════════════════════════════════════════════════════════════════════════
# Configuration
# ════════════════════════════════════════════════════════════════════════════

DETECTOR_CFG = {
    "name": "FASTER",
    "initial_threshold": 20,
    "min_threshold": 7,
    "max_threshold": 60,
    "target_features": 500,       # keep lower for real-time speed
    "nonmax_suppression": True,
}
DESCRIPTOR_CFG = {"name": "ORB"}

RATIO_THRESHOLD    = 0.75
RANSAC_THRESHOLD   = 1.0
RANSAC_CONFIDENCE  = 0.999
MIN_INLIER_RATIO   = 0.10
MIN_MATCHES        = 8

# Dashboard layout
FEED_W, FEED_H      = 640, 360    # live camera panel size
MAP_W,  MAP_H       = 640, 360    # trajectory map panel size
STATUS_H            = 60          # bottom status bar height
WINDOW_W            = FEED_W + MAP_W
WINDOW_H            = max(FEED_H, MAP_H) + STATUS_H

# Colors  (BGR)
CLR_GREEN   = (50,  220, 80)
CLR_RED     = (60,  60,  220)
CLR_YELLOW  = (0,   220, 220)
CLR_CYAN    = (220, 200, 50)
CLR_WHITE   = (255, 255, 255)
CLR_GREY    = (120, 120, 120)
CLR_DARK    = (30,  30,  30)
CLR_ORANGE  = (0,   140, 255)
CLR_TRAJ    = (80,  200, 255)
CLR_DENIED  = (60,  60,  220)


def decompose_homography_rotation(H: np.ndarray, K: np.ndarray, K_inv: np.ndarray) -> np.ndarray:
    """Extract relative rotation SO(3) matrix from planar homography H = K R K_inv."""
    M = K_inv @ H @ K
    det = float(np.linalg.det(M))
    if abs(det) > 1e-8:
        sign = 1.0 if det > 0 else -1.0
        M = M / (sign * (abs(det) ** (1.0 / 3.0)))
    U, _, Vt = np.linalg.svd(M)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        R = -R
    return R


# ════════════════════════════════════════════════════════════════════════════
# Trajectory Map
# ════════════════════════════════════════════════════════════════════════════

class TrajectoryMap:
    """Draws the camera path on a fixed-size canvas (top-down X-Z bird's-eye view).

    Coordinate convention:
      - X axis: Camera lateral motion (Right = Right on map)
      - Z axis: Camera depth/forward motion (Forward = UP on map)
    """

    def __init__(self, width: int = MAP_W, height: int = MAP_H) -> None:
        self.w = width
        self.h = height
        self.positions: list[np.ndarray] = []       # list of (x, y, z) in meters
        self.headings: list[np.ndarray] = []        # forward direction vector
        self.scale = 100.0                          # pixels per meter
        self.target_scale = 100.0                   # target scale for smooth zooming
        self.origin = np.array([width // 2, int(height * 0.75)], dtype=float)
        self.total_distance = 0.0

    def reset(self) -> None:
        self.positions.clear()
        self.headings.clear()
        self.scale = 100.0
        self.target_scale = 100.0
        self.origin = np.array([self.w // 2, int(self.h * 0.75)], dtype=float)
        self.total_distance = 0.0

    def add_position(self, pos: np.ndarray, R_world: Optional[np.ndarray] = None) -> None:
        """Add a 3-element world position (x, y, z) and optional camera orientation."""
        p = pos.copy()
        if self.positions:
            dist = float(np.linalg.norm(p - self.positions[-1]))
            self.total_distance += dist
        self.positions.append(p)

        # Forward vector in camera coordinates is [0, 0, 1]
        if R_world is not None:
            forward = R_world @ np.array([0.0, 0.0, 1.0])
            self.headings.append(forward)
        else:
            self.headings.append(np.array([0.0, 0.0, 1.0]))

    def world_to_screen(self, pos: np.ndarray, origin: np.ndarray, scale: float) -> Tuple[int, int]:
        """Convert world coordinates (X, Y, Z) to screen (pixel_x, pixel_y).

        In camera coords:
          +X is Right   -> moves Right on screen (+X)
          +Z is Forward -> moves UP on screen    (-Z)
        """
        px = int(round(origin[0] + pos[0] * scale))
        py = int(round(origin[1] - pos[2] * scale))
        return px, py

    def render(self, gps_denied: bool = False) -> np.ndarray:
        canvas = np.full((self.h, self.w, 3), 16, dtype=np.uint8)  # dark background

        # Smooth scale adjustment if path expands
        if len(self.positions) >= 2:
            xs = [p[0] for p in self.positions]
            zs = [p[2] for p in self.positions]
            max_x = max(abs(min(xs)), abs(max(xs)), 0.5)
            max_z = max(abs(min(zs)), abs(max(zs)), 0.5)

            # Fit nicely within 70% of canvas half-dimensions
            allowed_w = (self.w * 0.40)
            allowed_h = (self.h * 0.40)
            ideal_scale = min(allowed_w / max_x, allowed_h / max_z, 160.0)
            self.target_scale = max(ideal_scale, 15.0)

            # Smooth exponential moving average for scale to completely kill zoom jitter
            self.scale = 0.94 * self.scale + 0.06 * self.target_scale

        # Grid lines (concentric distance rings and axes)
        ox, oy = int(self.origin[0]), int(self.origin[1])

        # Subtle Cartesian grid
        grid_step = max(20, int(self.scale * 0.5))  # every 0.5 meter
        for gx in range(ox % grid_step, self.w, grid_step):
            cv2.line(canvas, (gx, 0), (gx, self.h), (26, 26, 26), 1)
        for gy in range(oy % grid_step, self.h, grid_step):
            cv2.line(canvas, (0, gy), (self.w, gy), (26, 26, 26), 1)

        # Coordinate axes cross at origin
        cv2.line(canvas, (ox, 0), (ox, self.h), (40, 40, 40), 1)
        cv2.line(canvas, (0, oy), (self.w, oy), (40, 40, 40), 1)

        # Distance reference circles: 0.5m, 1m, 2m
        for r_m in [0.5, 1.0, 2.0]:
            r_px = int(r_m * self.scale)
            if 10 < r_px < min(self.w, self.h):
                cv2.circle(canvas, (ox, oy), r_px, (32, 32, 32), 1)
                cv2.putText(canvas, f"{r_m}m", (ox + r_px + 2, oy - 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.30, (70, 70, 70), 1)

        # Title & GPS Status Header
        mode_txt = "GPS: DENIED (VO MODE)" if gps_denied else "GPS: ACTIVE (AUGMENTED)"
        mode_clr = CLR_DENIED if gps_denied else CLR_GREEN
        cv2.putText(canvas, "BIRD'S-EYE TRAJECTORY (TOP-DOWN X-Z)", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, CLR_GREY, 1)
        cv2.putText(canvas, mode_txt, (self.w - 220, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, mode_clr, 1)

        # Compass Indicator (Top Right)
        comp_x, comp_y = self.w - 35, 55
        cv2.arrowedLine(canvas, (comp_x, comp_y + 15), (comp_x, comp_y - 12), CLR_CYAN, 1, tipLength=0.35)
        cv2.putText(canvas, "FWD (+Z)", (comp_x - 30, comp_y - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, CLR_CYAN, 1)

        if len(self.positions) < 2:
            cv2.putText(canvas, "Waiting for camera movement...", (self.w // 2 - 130, self.h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, CLR_GREY, 1)
            # Draw start origin
            cv2.circle(canvas, (ox, oy), 5, CLR_GREEN, -1)
            cv2.putText(canvas, "START (0,0)", (ox + 8, oy + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, CLR_GREEN, 1)
            return canvas

        # Convert positions to screen points
        px_pts = [self.world_to_screen(p, self.origin, self.scale) for p in self.positions]

        # Draw trajectory path with subtle color trail
        traj_clr = CLR_DENIED if gps_denied else CLR_TRAJ
        n_pts = len(px_pts)
        for i in range(1, n_pts):
            alpha = max(0.25, i / float(n_pts))
            c = tuple(int(v * alpha) for v in traj_clr)
            cv2.line(canvas, px_pts[i - 1], px_pts[i], c, 2, cv2.LINE_AA)

        # Draw Start Marker
        start_pt = px_pts[0]
        cv2.circle(canvas, start_pt, 6, CLR_GREEN, -1)
        cv2.putText(canvas, "START", (start_pt[0] + 8, start_pt[1] + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, CLR_GREEN, 1)

        # Draw Current Position + Orientation Arrow
        curr_pt = px_pts[-1]
        cv2.circle(canvas, curr_pt, 7, CLR_YELLOW, -1)
        cv2.circle(canvas, curr_pt, 10, CLR_YELLOW, 1, cv2.LINE_AA)

        yaw_deg = 0.0
        if self.headings:
            fwd = self.headings[-1]
            norm_xz = float(np.hypot(fwd[0], fwd[2]))
            if norm_xz > 1e-4:
                ux = fwd[0] / norm_xz
                uz = fwd[2] / norm_xz
            else:
                ux, uz = 0.0, 1.0

            arrow_len = 24.0
            arr_x = int(curr_pt[0] + ux * arrow_len)
            arr_y = int(curr_pt[1] - uz * arrow_len)
            cv2.arrowedLine(canvas, curr_pt, (arr_x, arr_y), CLR_CYAN, 2, tipLength=0.35)

            yaw_deg = float(np.degrees(np.arctan2(ux, uz)))
            cv2.putText(canvas, f"Yaw: {yaw_deg:+.0f}\u00b0", (curr_pt[0] + 12, curr_pt[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36, CLR_CYAN, 1)

        # Telemetry overlay (Bottom Left)
        curr_pos = self.positions[-1]
        telemetry = f"Odom: {self.total_distance:.2f}m | X={curr_pos[0]:+.2f}m, Z={curr_pos[2]:+.2f}m | Yaw={yaw_deg:+.1f}\u00b0"
        cv2.putText(canvas, telemetry, (10, self.h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, CLR_WHITE, 1)

        # Metric scale bar (Bottom Right)
        scale_m = 0.5 if self.scale > 70 else 1.0
        bar_px = int(scale_m * self.scale)
        bx, by = self.w - 110, self.h - 16
        cv2.line(canvas, (bx, by), (bx + bar_px, by), CLR_WHITE, 2)
        cv2.putText(canvas, f"{scale_m} m", (bx + bar_px + 6, by + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, CLR_WHITE, 1)

        return canvas


# ════════════════════════════════════════════════════════════════════════════
# Status Bar
# ════════════════════════════════════════════════════════════════════════════

def render_status_bar(
    width: int,
    fps: float,
    n_kp: int,
    n_matches: int,
    n_inliers: int,
    status: str,
    gps_denied: bool,
    frame_count: int,
    threshold: int,
) -> np.ndarray:
    bar = np.full((STATUS_H, width, 3), 20, dtype=np.uint8)
    cv2.line(bar, (0, 0), (width, 0), (60, 60, 60), 1)

    # GPS mode badge
    gps_txt = " GPS DENIED " if gps_denied else " GPS ACTIVE "
    gps_clr = CLR_DENIED if gps_denied else CLR_GREEN
    cv2.rectangle(bar, (10, 10), (10 + len(gps_txt)*10, 46), gps_clr, -1)
    cv2.putText(bar, gps_txt, (12, 34),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    # Stats columns
    col2 = 220
    col3 = 400
    col4 = 580
    col5 = 760
    col6 = 920

    def stat(label, val, x, color=CLR_WHITE):
        cv2.putText(bar, label, (x, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, CLR_GREY, 1)
        cv2.putText(bar, str(val), (x, 46),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.60, color, 2)

    fps_clr = CLR_GREEN if fps >= 20 else (CLR_YELLOW if fps >= 10 else CLR_RED)
    stat("FPS",      f"{fps:5.1f}", col2, fps_clr)
    stat("FEATURES", f"{n_kp}",     col3, CLR_CYAN)
    stat("MATCHES",  f"{n_matches}", col4, CLR_CYAN)
    stat("INLIERS",  f"{n_inliers}", col5,
         CLR_GREEN if n_inliers >= 20 else (CLR_YELLOW if n_inliers >= 8 else CLR_RED))
    stat("THRESH",   f"{threshold}", col6, CLR_GREY)

    # Status text (tracking/rotating/stationary/failed)
    status_clr = (
        CLR_GREEN if status in ("TRACKING", "ROTATING")
        else (CLR_CYAN if status == "STATIONARY" else CLR_RED)
    )
    cv2.putText(bar, status, (width - 200, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_clr, 2)

    # Frame counter
    cv2.putText(bar, f"Frame {frame_count:05d}", (width - 200, 54),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, CLR_GREY, 1)

    return bar


# ════════════════════════════════════════════════════════════════════════════
# Camera Feed Panel
# ════════════════════════════════════════════════════════════════════════════

def render_camera_panel(
    frame: np.ndarray,
    kps_prev: list,
    kps_curr: list,
    good_matches: list,
    n_inliers: int,
    gps_denied: bool,
    width: int = FEED_W,
    height: int = FEED_H,
) -> np.ndarray:
    panel = cv2.resize(frame, (width, height))

    # Draw matched keypoints as green circles
    for m in good_matches[:80]:   # limit for speed
        pt = kps_curr[m.trainIdx].pt
        x, y = int(pt[0] * width / frame.shape[1]), int(pt[1] * height / frame.shape[0])
        cv2.circle(panel, (x, y), 3, CLR_GREEN, -1)

    # Draw inlier count
    overlay_txt = f"{n_inliers} inliers"
    cv2.putText(panel, overlay_txt, (10, height - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, CLR_YELLOW, 2)

    # GPS DENIED red border
    if gps_denied:
        cv2.rectangle(panel, (0, 0), (width-1, height-1), CLR_DENIED, 4)
        cv2.putText(panel, "VO DEAD-RECKONING MODE", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, CLR_DENIED, 2)
    else:
        cv2.putText(panel, "LIVE CAMERA", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, CLR_GREEN, 2)

    return panel


# ════════════════════════════════════════════════════════════════════════════
# Main Loop
# ════════════════════════════════════════════════════════════════════════════

def build_intrinsics(focal_length: float, width: int, height: int) -> np.ndarray:
    """Build a camera intrinsics matrix K from focal length and image size."""
    cx, cy = width / 2.0, height / 2.0
    return np.array([
        [focal_length, 0.0,          cx],
        [0.0,          focal_length, cy],
        [0.0,          0.0,          1.0],
    ], dtype=np.float64)


def main(camera_idx: int = 0, focal_length: float | None = None) -> None:
    # ── Open camera ─────────────────────────────────────────────────────────
    cap = cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera index {camera_idx}.")
        print("  Try: python scripts/live_dashboard.py --camera 0")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Camera opened: {cam_w}×{cam_h} @ index {camera_idx}")

    # ── Camera intrinsics (approximation if not calibrated) ─────────────────
    fl = focal_length if focal_length else float(cam_w)   # common approximation
    K  = build_intrinsics(fl, cam_w, cam_h)
    K_inv = np.linalg.inv(K)
    print(f"[INFO] Using focal_length={fl:.0f} px  (cx={K[0,2]:.0f}, cy={K[1,2]:.0f})")
    print("[INFO] For better results, calibrate your camera and pass --focal-length")

    # ── Feature extractor & motion model ────────────────────────────────────
    fc        = build_feature_config(DETECTOR_CFG, DESCRIPTOR_CFG)
    extractor = FeatureExtractor(fc, bucketing="quadtree", subpixel=True, max_features=500)
    # Permissive motion model tuned for live handheld/robotic camera (allows holonomic lateral & turnaround moves):
    motion_model = ConstantVelocityMotionModel(
        max_angular_jump_deg=65.0,
        max_direction_change_deg=180.0,
        max_speed_ratio=6.0,
    )

    # ── State ───────────────────────────────────────────────────────────────
    traj_map    = TrajectoryMap()
    world_pose  = np.eye(4, dtype=np.float64)   # accumulates T_world
    prev_gray   = None
    prev_kps    = []
    prev_descs  = None
    fps_buffer  = deque(maxlen=20)
    frame_count = 0
    gps_denied  = False
    threshold   = DETECTOR_CFG["initial_threshold"]

    # Last-frame stats for status bar
    n_kp = n_matches = n_inliers = 0
    tracking_status = "STARTING"
    good_matches_cache: list = []

    # ── Output dir for screenshots ───────────────────────────────────────────
    out_dir = ROOT / "results" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Window ──────────────────────────────────────────────────────────────
    cv2.namedWindow("VO Live Dashboard", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("VO Live Dashboard", WINDOW_W, WINDOW_H)

    print("\n[CONTROLS]  Q=quit | R=reset | G=toggle GPS | S=screenshot | +/-=threshold\n")

    t_last = time.perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame capture failed — retrying...")
            time.sleep(0.05)
            continue

        frame_count += 1
        t_now  = time.perf_counter()
        dt     = t_now - t_last
        t_last = t_now
        fps_buffer.append(1.0 / dt if dt > 0 else 0.0)
        fps = float(np.mean(fps_buffer))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ── Feature extraction ───────────────────────────────────────────────
        result   = extractor.extract(gray)
        curr_kps  = result.keypoints
        curr_descs = result.descriptors
        n_kp     = len(curr_kps)

        # ── Matching + pose estimation ───────────────────────────────────────
        if prev_gray is not None and prev_descs is not None and curr_descs is not None:
            _, good_matches = match_and_filter(
                prev_descs, curr_descs,
                norm_type=fc.norm_type,
                ratio_threshold=RATIO_THRESHOLD,
            )
            n_matches = len(good_matches)
            good_matches_cache = good_matches

            if n_matches >= MIN_MATCHES:
                pts_prev, pts_curr = matches_to_point_arrays(good_matches, prev_kps, curr_kps)

                # Feature displacement analysis
                disp = np.linalg.norm(pts_curr - pts_prev, axis=1)
                median_flow = float(np.median(disp)) if len(disp) > 0 else 0.0

                if median_flow < 1.8:
                    # 1. STATIONARY DEADBAND:
                    # Optical flow is sub-threshold; camera is held still.
                    # Carry pose over to prevent random floating drift.
                    tracking_status = "STATIONARY"
                    n_inliers = n_matches
                    pos = world_pose[:3, 3]
                    R_curr = world_pose[:3, :3]
                    traj_map.add_position(pos, R_world=R_curr)
                else:
                    # 2. DUAL ESTIMATOR: PURE ROTATION vs TRANSLATION WITH PARALLAX
                    # Under pure rotation (or camera pan/yaw), epipolar baseline t ≈ 0,
                    # which makes Essential matrix E degenerate. In that regime, points
                    # obey a planar Homography (H = K R K_inv) with near-zero residual.
                    is_pure_rotation = False
                    H, h_mask = cv2.findHomography(
                        pts_prev.astype(np.float32), pts_curr.astype(np.float32),
                        cv2.RANSAC, 2.5
                    )
                    if H is not None and h_mask is not None:
                        inliers = np.where(h_mask.ravel() == 1)[0]
                        h_inlier_ratio = len(inliers) / len(pts_prev)
                        if len(inliers) >= 8:
                            p1_h = np.hstack([pts_prev[inliers], np.ones((len(inliers), 1), dtype=np.float32)])
                            p2_proj = (H @ p1_h.T).T
                            w = p2_proj[:, 2:3]
                            w[w == 0] = 1e-6
                            p2_proj = p2_proj[:, :2] / w
                            rep_errs = np.linalg.norm(pts_curr[inliers] - p2_proj, axis=1)
                            median_h_err = float(np.median(rep_errs))
                        else:
                            median_h_err = 999.0

                        # If homography fits a large majority of points with low reprojection error:
                        if h_inlier_ratio >= 0.65 and median_h_err <= 1.8:
                            R_H = decompose_homography_rotation(H, K, K_inv)
                            tr = np.clip((np.trace(R_H) - 1.0) / 2.0, -1.0, 1.0)
                            rot_deg = float(np.degrees(np.arccos(tr)))

                            if rot_deg > 0.35:
                                # Pure rotation confirmed (rotation in place, zero translation)
                                is_pure_rotation = True
                                t_zero = np.zeros(3, dtype=np.float64)
                                val = motion_model.validate_relative_pose(R_H, t_zero, t_now)
                                if val.is_valid:
                                    motion_model.update(R_H, t_zero, t_now)
                                    T_rel = make_pose(R_H, t_zero)
                                    world_pose = compose_poses(world_pose, invert_pose(T_rel))
                                    pos = world_pose[:3, 3]
                                    R_curr = world_pose[:3, :3]
                                    traj_map.add_position(pos, R_world=R_curr)
                                    tracking_status = "ROTATING"
                                    n_inliers = len(inliers)
                                else:
                                    tracking_status = "INVALID POSE"

                    if not is_pure_rotation:
                        # 3. TRANSLATION (3D Parallax present -> Essential Matrix)
                        pose_result = estimate_pose(
                            pts_prev, pts_curr, K,
                            ransac_threshold=RANSAC_THRESHOLD,
                            ransac_confidence=RANSAC_CONFIDENCE,
                            min_inlier_ratio=MIN_INLIER_RATIO,
                        )

                        if pose_result.success:
                            # Scale relative translation proportionally to flow displacement:
                            # Forward/backward & lateral left/right speeds are dynamically scaled
                            step_m = np.clip(median_flow * 0.0035, 0.012, 0.060)
                            t_scaled = pose_result.t.flatten() * step_m

                            val = motion_model.validate_relative_pose(
                                pose_result.R, t_scaled, t_now
                            )
                            n_inliers = pose_result.n_inliers

                            if val.is_valid:
                                motion_model.update(pose_result.R, t_scaled, t_now)
                                T_rel = make_pose(pose_result.R, t_scaled)
                                world_pose = compose_poses(world_pose, invert_pose(T_rel))

                                pos = world_pose[:3, 3]
                                R_curr = world_pose[:3, :3]
                                traj_map.add_position(pos, R_world=R_curr)
                                tracking_status = "TRACKING"
                            else:
                                tracking_status = "INVALID POSE"
                        else:
                            tracking_status = "RANSAC FAILED"
                            n_inliers = 0
            else:
                tracking_status = "FEW MATCHES"
                n_inliers = 0
                good_matches_cache = []
        else:
            tracking_status = "INITIALIZING"

        # ── Build dashboard panels ───────────────────────────────────────────
        cam_panel   = render_camera_panel(
            frame, prev_kps, curr_kps, good_matches_cache, n_inliers, gps_denied
        )
        map_panel   = traj_map.render(gps_denied=gps_denied)
        map_panel   = cv2.resize(map_panel, (MAP_W, FEED_H))

        top_row     = np.hstack([cam_panel, map_panel])

        status_bar  = render_status_bar(
            WINDOW_W, fps, n_kp, n_matches, n_inliers,
            tracking_status, gps_denied, frame_count, threshold
        )

        dashboard   = np.vstack([top_row, status_bar])

        cv2.imshow("VO Live Dashboard", dashboard)

        # ── Update previous frame ────────────────────────────────────────────
        prev_gray  = gray
        prev_kps   = curr_kps
        prev_descs = curr_descs

        # ── Keyboard controls ────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:   # Q or ESC → quit
            break

        elif key == ord('r'):              # R → reset
            traj_map.reset()
            world_pose = np.eye(4, dtype=np.float64)
            motion_model.reset()
            frame_count = 0
            print("[INFO] Trajectory reset.")

        elif key == ord('g'):              # G → toggle GPS mode
            gps_denied = not gps_denied
            mode = "DENIED (VO dead-reckoning)" if gps_denied else "ACTIVE"
            print(f"[INFO] GPS mode → {mode}")

        elif key == ord('s'):              # S → screenshot
            ts = int(time.time())
            path = out_dir / f"live_dashboard_{ts}.png"
            cv2.imwrite(str(path), dashboard)
            print(f"[INFO] Screenshot saved → {path}")

        elif key == ord('+') or key == ord('='):
            threshold = min(60, threshold + 5)
            DETECTOR_CFG["initial_threshold"] = threshold
            fc        = build_feature_config(DETECTOR_CFG, DESCRIPTOR_CFG)
            extractor = FeatureExtractor(fc, bucketing="quadtree", subpixel=True, max_features=500)
            print(f"[INFO] FAST threshold → {threshold}")

        elif key == ord('-'):
            threshold = max(5, threshold - 5)
            DETECTOR_CFG["initial_threshold"] = threshold
            fc        = build_feature_config(DETECTOR_CFG, DESCRIPTOR_CFG)
            extractor = FeatureExtractor(fc, bucketing="quadtree", subpixel=True, max_features=500)
            print(f"[INFO] FAST threshold → {threshold}")

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[DONE] Processed {frame_count} frames. Final FPS avg: {fps:.1f}")


# ════════════════════════════════════════════════════════════════════════════
# Entry point
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Live Visual Odometry Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--camera", type=int, default=0,
        help="Camera device index (default: 0 = built-in webcam)",
    )
    parser.add_argument(
        "--focal-length", type=float, default=None,
        help="Camera focal length in pixels (default: image_width — approximate)",
    )
    args = parser.parse_args()
    main(camera_idx=args.camera, focal_length=args.focal_length)
