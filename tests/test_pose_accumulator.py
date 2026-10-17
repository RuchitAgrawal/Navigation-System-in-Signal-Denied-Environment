# tests/test_pose_accumulator.py -- PoseAccumulator unit tests
import numpy as np
import pytest
import tempfile
from pathlib import Path
from src.geometry.pose import PoseAccumulator, FrameDiagnostics, FrameStatus
from src.geometry.transforms import make_pose
from scipy.spatial.transform import Rotation

\nclass TestPoseAccumulator:
    def test_initialize_creates_identity_first_pose(self):
        acc = PoseAccumulator(); acc.initialize(0.0)
        np.testing.assert_allclose(acc.poses[0], np.eye(4))

    def test_get_positions_shape(self):
        acc = PoseAccumulator(); acc.initialize(0.0)
        diag = FrameDiagnostics(frame_idx=1, status=FrameStatus.SUCCESS)
        acc.add_relative_pose(np.eye(3), np.array([0.1, 0, 0]), 1.0, diag)
        pos = acc.get_positions()
        assert pos.shape == (2, 3)

    def test_tum_roundtrip(self, tmp_path):
        acc = PoseAccumulator(); acc.initialize(0.0)
        diag = FrameDiagnostics(frame_idx=1, status=FrameStatus.SUCCESS)
        R = Rotation.from_euler('y', 30, degrees=True).as_matrix()
        acc.add_relative_pose(R, np.array([0.1, 0, 0]), 1.0, diag)
        path = tmp_path / 'traj.txt'
        acc.save_tum_format(path)
        acc2 = PoseAccumulator.load_tum_format(path)
        assert len(acc2.poses) == len(acc.poses)
        np.testing.assert_allclose(acc2.poses[0], acc.poses[0], atol=1e-5)

    def test_failed_pose_carries_previous(self):
        acc = PoseAccumulator(); acc.initialize(0.0)
        T_prev = acc.current_pose.copy()
        diag = FrameDiagnostics(frame_idx=1, status=FrameStatus.FAILED_MATCHES)
        acc.add_failed_pose(1.0, diag)
        np.testing.assert_allclose(acc.poses[1], T_prev)

