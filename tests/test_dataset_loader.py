"""
test_dataset_loader.py — Unit tests for dataset loader interfaces.

These tests validate the loader logic using synthetic/minimal data
without requiring the actual ICL-NUIM or TartanAir downloads.
"""
import numpy as np
import pytest
import tempfile
import os
from pathlib import Path

from src.datasets.base_dataset import CameraIntrinsics, DatasetFrame
from src.geometry.transforms import make_pose


class TestCameraIntrinsics:
    def test_K_matrix_shape(self):
        cam = CameraIntrinsics(fx=481.2, fy=480.0, cx=319.5, cy=239.5)
        K = cam.K
        assert K.shape == (3, 3)
        assert K.dtype == np.float64

    def test_K_values(self):
        cam = CameraIntrinsics(fx=320.0, fy=320.0, cx=320.0, cy=240.0)
        assert cam.K[0, 0] == 320.0
        assert cam.K[1, 1] == 320.0
        assert cam.K[0, 2] == 320.0
        assert cam.K[1, 2] == 240.0
        assert cam.K[2, 2] == 1.0

    def test_dist_coeffs_shape(self):
        cam = CameraIntrinsics(fx=481.2, fy=480.0, cx=319.5, cy=239.5,
                               k1=0.01, k2=-0.02, p1=0.001, p2=0.0)
        dc = cam.dist_coeffs
        assert dc.shape == (4,)
        assert dc[0] == 0.01

    def test_zero_distortion_default(self):
        cam = CameraIntrinsics(fx=320.0, fy=320.0, cx=320.0, cy=240.0)
        np.testing.assert_array_equal(cam.dist_coeffs, np.zeros(4))


class TestDatasetFrame:
    def test_frame_creation(self):
        T = make_pose(np.eye(3), np.array([1.0, 2.0, 3.0]))
        frame = DatasetFrame(
            index=5,
            timestamp=1.234,
            image_path=Path("rgb/0005.png"),
            gt_pose=T,
        )
        assert frame.index == 5
        assert abs(frame.timestamp - 1.234) < 1e-9
        assert frame.gt_pose is not None

    def test_frame_without_gt(self):
        frame = DatasetFrame(index=0, timestamp=0.0, image_path=Path("img.png"))
        assert frame.gt_pose is None


class TestICLNUIMLoader:
    """Tests that use minimal synthetic files to validate the loader logic."""

    def _write_tum_list(self, path: Path, entries: list):
        with open(path, "w") as f:
            for ts, fname in entries:
                f.write(f"{ts:.6f} {fname}\n")

    def _write_groundtruth(self, path: Path, entries: list):
        with open(path, "w") as f:
            for ts, tx, ty, tz, qx, qy, qz, qw in entries:
                f.write(f"{ts:.6f} {tx} {ty} {tz} {qx} {qy} {qz} {qw}\n")

    def test_load_synthetic_sequence(self, tmp_path):
        """Create a minimal synthetic ICL-NUIM sequence and validate loading."""
        from src.datasets.icl_nuim import ICLNUIMDataset

        # Create directory structure
        rgb_dir = tmp_path / "rgb"
        rgb_dir.mkdir()

        n_frames = 5
        # Write dummy images (1×1 pixel PNG stubs via numpy)
        import cv2
        for i in range(n_frames):
            img = np.zeros((480, 640), dtype=np.uint8)
            cv2.imwrite(str(rgb_dir / f"{i:04d}.png"), img)

        # Write rgb.txt
        rgb_entries = [(float(i) * 0.033, f"rgb/{i:04d}.png") for i in range(n_frames)]
        self._write_tum_list(tmp_path / "rgb.txt", rgb_entries)

        # Write groundtruth.txt (identity poses)
        gt_entries = [
            (float(i) * 0.033, 0.0, 0.0, float(i)*0.1, 0.0, 0.0, 0.0, 1.0)
            for i in range(n_frames)
        ]
        self._write_groundtruth(tmp_path / "groundtruth.txt", gt_entries)

        # Load
        dataset = ICLNUIMDataset(root=tmp_path, sequence_name="test_seq")

        assert len(dataset) == n_frames
        assert dataset.name == "icl_nuim"
        assert dataset.sequence == "test_seq"

        frame0 = dataset[0]
        assert frame0.index == 0
        assert frame0.gt_pose is not None
        assert frame0.gt_pose.shape == (4, 4)

        gt_poses = dataset.get_ground_truth_poses()
        assert len(gt_poses) == n_frames
        # Third frame should have translation ~0.2 in Z
        np.testing.assert_allclose(gt_poses[2][:3, 3], [0.0, 0.0, 0.2], atol=1e-5)
