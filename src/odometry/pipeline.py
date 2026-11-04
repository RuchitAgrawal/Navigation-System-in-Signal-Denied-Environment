"""
pipeline.py â€” Main visual odometry pipeline loop.

Implements a classical frame-to-frame monocular VO:
    1. Load greyscale frame pair (prev, curr)
    2. Detect keypoints and compute descriptors (via FeatureExtractor)
    3. Match with Hamming BFMatcher + Lowe ratio filter
    4. Estimate Essential matrix via RANSAC
    5. Recover R, t (direction only â€” scale ambiguous)
    6. Accumulate pose into trajectory
    7. Record per-frame diagnostics

Design decisions
----------------
- Delegates detect/describe to FeatureExtractor for clean separation.
- All failure modes are handled gracefully (no crashes).
- On failure, the previous pose is carried forward.
- Every frame gets a FrameDiagnostics record (success or failure).
- Ground truth is used ONLY for evaluation, never for motion estimation.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

from src.datasets.base_dataset import BaseDataset
from src.features.config import FeatureConfig
from src.features.extractor import FeatureExtractor
from src.geometry.essential import estimate_pose
from src.geometry.pnp import hybrid_estimate_pose
from src.geometry.pose import FrameDiagnostics, FrameStatus, PoseAccumulator
from src.matching.matcher import match_and_filter, matches_to_point_arrays
from src.odometry.motion_model import ConstantVelocityMotionModel


class VOPipeline:
    """Classical monocular visual odometry pipeline.

    Parameters
    ----------
    feature_config : FeatureConfig
        Validated detector/descriptor/norm configuration.
    ransac_threshold : float
        RANSAC pixel reprojection threshold.
    ransac_confidence : float
        RANSAC confidence level.
    ransac_max_iter : int
        Maximum RANSAC iterations.
    ratio_threshold : float
        Lowe ratio test threshold.
    cross_check : bool
        Use cross-check instead of ratio test.
    min_keypoints : int
        Minimum keypoints to attempt matching.
    min_matches : int
        Minimum filtered matches to attempt pose estimation.
    min_inlier_ratio : float
        Minimum RANSAC inlier ratio to accept the pose.
    """

    def __init__(
        self,
        feature_config: FeatureConfig,
        ransac_threshold: float = 1.0,
        ransac_confidence: float = 0.999,
        ransac_max_iter: int = 2000,
        ratio_threshold: float = 0.75,
        cross_check: bool = False,
        min_keypoints: int = 8,
        min_matches: int = 8,
        min_inlier_ratio: float = 0.10,
        use_motion_model: bool = True,
        use_pnp: bool = False,
        bucketing: str = "none",
        subpixel: bool = False,
        max_features: int = 2000,
        clahe: bool = False,
        clahe_clip_limit: float = 2.0,
        clahe_grid_size: Tuple[int, int] = (8, 8),
    ) -> None:
        self.fc = feature_config
        self.extractor = FeatureExtractor(
            feature_config,
            bucketing=bucketing,
            subpixel=subpixel,
            max_features=max_features,
            clahe=clahe,
            clahe_clip_limit=clahe_clip_limit,
            clahe_grid_size=clahe_grid_size,
        )
        self.ransac_threshold = ransac_threshold
        self.ransac_confidence = ransac_confidence
        self.ransac_max_iter = ransac_max_iter
        self.ratio_threshold = ratio_threshold
        self.cross_check = cross_check
        self.min_keypoints = min_keypoints
        self.min_matches = min_matches
        self.min_inlier_ratio = min_inlier_ratio
        self.use_motion_model = use_motion_model
        self.use_pnp = use_pnp
        self.motion_model = ConstantVelocityMotionModel() if use_motion_model else None

        self.accumulator = PoseAccumulator()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self, dataset: BaseDataset) -> PoseAccumulator:
        """Process all frames in the dataset and return the pose accumulator.

        Parameters
        ----------
        dataset : BaseDataset

        Returns
        -------
        PoseAccumulator  with poses, timestamps, and diagnostics for every frame.
        """
        K = dataset.camera.K
        n_frames = len(dataset)

        # Initialize with the first frame's timestamp
        first_frame = dataset[0]
        self.accumulator.initialize(timestamp=first_frame.timestamp)
        if self.motion_model is not None:
            self.motion_model.reset()

        prev_gray = dataset.load_image_gray(0)
        prev_result = self.extractor.extract(prev_gray)
        prev_kps, prev_descs = prev_result.keypoints, prev_result.descriptors

        # Diagnostic for frame 0 (no relative pose, just SKIPPED)
        diag0 = FrameDiagnostics(
            frame_idx=0,
            status=FrameStatus.SKIPPED,
            n_keypoints_curr=len(prev_kps),
        )
        self.accumulator.diagnostics.append(diag0)

        for idx in range(1, n_frames):
            frame = dataset[idx]
            t_start_total = time.perf_counter()

            curr_gray = dataset.load_image_gray(idx)

            # ---------- Detect + Describe ----------
            curr_result = self.extractor.extract(curr_gray)
            curr_kps   = curr_result.keypoints
            curr_descs = curr_result.descriptors
            detect_describe_ms = curr_result.detect_ms + curr_result.describe_ms

            # ---------- Check keypoint count ----------
            if len(prev_kps) < self.min_keypoints or len(curr_kps) < self.min_keypoints:
                diag = FrameDiagnostics(
                    frame_idx=idx,
                    status=FrameStatus.FAILED_FEATURES,
                    n_keypoints_prev=len(prev_kps),
                    n_keypoints_curr=len(curr_kps),
                    detect_time_ms=detect_describe_ms,
                    total_time_ms=(time.perf_counter() - t_start_total) * 1000.0,
                )
                self.accumulator.add_failed_pose(frame.timestamp, diag)
                prev_gray, prev_kps, prev_descs = curr_gray, curr_kps, curr_descs
                continue

            # ---------- Match ----------
            t0 = time.perf_counter()
            raw_matches, good_matches = match_and_filter(
                prev_descs, curr_descs,
                norm_type=self.fc.norm_type,
                ratio_threshold=self.ratio_threshold,
                cross_check=self.cross_check,
            )
            match_ms = (time.perf_counter() - t0) * 1000.0

            if len(good_matches) < self.min_matches:
                diag = FrameDiagnostics(
                    frame_idx=idx,
                    status=FrameStatus.FAILED_MATCHES,
                    n_keypoints_prev=len(prev_kps),
                    n_keypoints_curr=len(curr_kps),
                    n_raw_matches=len(raw_matches),
                    n_filtered_matches=len(good_matches),
                    detect_time_ms=detect_describe_ms,
                    match_time_ms=match_ms,
                    total_time_ms=(time.perf_counter() - t_start_total) * 1000.0,
                )
                self.accumulator.add_failed_pose(frame.timestamp, diag)
                prev_gray, prev_kps, prev_descs = curr_gray, curr_kps, curr_descs
                continue

            # ---------- Estimate pose ----------
            pts_prev, pts_curr = matches_to_point_arrays(good_matches, prev_kps, curr_kps)

            t0 = time.perf_counter()
            result = estimate_pose(
                pts_prev, pts_curr, K,
                ransac_threshold=self.ransac_threshold,
                ransac_confidence=self.ransac_confidence,
                ransac_max_iter=self.ransac_max_iter,
                min_inlier_ratio=self.min_inlier_ratio,
            )
            pose_ms = (time.perf_counter() - t0) * 1000.0

            total_ms = (time.perf_counter() - t_start_total) * 1000.0

            if not result.success:
                status = FrameStatus.FAILED_RANSAC if "Inlier" in result.failure_reason \
                    else FrameStatus.FAILED_POSE
                diag = FrameDiagnostics(
                    frame_idx=idx,
                    status=status,
                    n_keypoints_prev=len(prev_kps),
                    n_keypoints_curr=len(curr_kps),
                    n_raw_matches=len(raw_matches),
                    n_filtered_matches=len(good_matches),
                    n_ransac_inliers=result.n_inliers,
                    ransac_inlier_ratio=result.inlier_ratio,
                    detect_time_ms=detect_describe_ms,
                    match_time_ms=match_ms,
                    pose_time_ms=pose_ms,
                    total_time_ms=total_ms,
                )
                self.accumulator.add_failed_pose(frame.timestamp, diag)
            else:
                # Check kinematic continuity if motion prior is active
                if self.motion_model is not None:
                    val = self.motion_model.validate_relative_pose(result.R, result.t, frame.timestamp)
                    if not val.is_valid:
                        diag = FrameDiagnostics(
                            frame_idx=idx,
                            status=FrameStatus.FAILED_POSE,
                            n_keypoints_prev=len(prev_kps),
                            n_keypoints_curr=len(curr_kps),
                            n_raw_matches=len(raw_matches),
                            n_filtered_matches=len(good_matches),
                            n_ransac_inliers=result.n_inliers,
                            ransac_inlier_ratio=result.inlier_ratio,
                            detect_time_ms=detect_describe_ms,
                            match_time_ms=match_ms,
                            pose_time_ms=pose_ms,
                            total_time_ms=total_ms,
                        )
                        self.accumulator.add_failed_pose(frame.timestamp, diag)
                        prev_gray, prev_kps, prev_descs = curr_gray, curr_kps, curr_descs
                        continue
                    else:
                        self.motion_model.update(result.R, result.t, frame.timestamp)

                diag = FrameDiagnostics(
                    frame_idx=idx,
                    status=FrameStatus.SUCCESS,
                    n_keypoints_prev=len(prev_kps),
                    n_keypoints_curr=len(curr_kps),
                    n_raw_matches=len(raw_matches),
                    n_filtered_matches=len(good_matches),
                    n_ransac_inliers=result.n_inliers,
                    ransac_inlier_ratio=result.inlier_ratio,
                    detect_time_ms=detect_describe_ms,
                    match_time_ms=match_ms,
                    pose_time_ms=pose_ms,
                    total_time_ms=total_ms,
                )
                self.accumulator.add_relative_pose(
                    result.R, result.t, frame.timestamp, diag
                )

            # Update previous frame
            prev_gray, prev_kps, prev_descs = curr_gray, curr_kps, curr_descs

        return self.accumulator

