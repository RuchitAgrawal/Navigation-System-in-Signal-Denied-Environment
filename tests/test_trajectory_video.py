"""
tests/test_trajectory_video.py — Unit tests for video dashboard generation.
"""

from pathlib import Path
import pytest
import numpy as np
import cv2

from scripts.generate_trajectory_video import generate_video


def test_video_generator_execution(tmp_path):
    dataset_cfg = "configs/datasets/icl_nuim.yaml"
    exp_cfg = "configs/experiments/faster_orb.yaml"
    traj_path = "results/csv/faster_orb_v1__icl_nuim__living_room_traj1_loop_trajectory.txt"
    out_video = tmp_path / "test_output.mp4"

    if Path(dataset_cfg).exists() and Path(traj_path).exists():
        video_path = generate_video(
            dataset_cfg_path=dataset_cfg,
            experiment_cfg_path=exp_cfg,
            traj_tum_path=traj_path,
            output_video_path=out_video,
            fps=10,
            max_frames=5,  # fast test: 5 frames
        )
        assert video_path.exists()
        assert video_path.stat().st_size > 1000

        # Verify video can be opened by cv2.VideoCapture
        cap = cv2.VideoCapture(str(video_path))
        assert cap.isOpened()
        ret, frame = cap.read()
        assert ret is True
        assert frame.shape[0] == 480
        assert frame.shape[1] == 1120  # 640 + 480
        cap.release()
