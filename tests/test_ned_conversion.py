"""
tests/test_ned_conversion.py — NED to camera coordinate conversion tests.
"""
import numpy as np
import pytest
from src.geometry.transforms import ned_body_to_camera_pose, is_valid_pose, is_valid_rotation


class TestNEDConversion:
    def test_output_is_valid_pose(self):
        t = np.array([1.0, 2.0, 3.0])
        q = np.array([0.0, 0.0, 0.0, 1.0])  # identity quaternion (xyzw)
        T = ned_body_to_camera_pose(t, q)
        assert is_valid_pose(T)

    def test_output_shape(self):
        t = np.zeros(3)
        q = np.array([0.0, 0.0, 0.0, 1.0])
        T = ned_body_to_camera_pose(t, q)
        assert T.shape == (4, 4)

    def test_rotation_is_valid(self):
        from scipy.spatial.transform import Rotation
        R_ned = Rotation.from_euler("z", 45, degrees=True)
        q = R_ned.as_quat()  # xyzw
        T = ned_body_to_camera_pose(np.zeros(3), q)
        assert is_valid_rotation(T[:3, :3])

    def test_identity_gives_valid_pose(self):
        T = ned_body_to_camera_pose(np.zeros(3), np.array([0.0, 0.0, 0.0, 1.0]))
        assert is_valid_pose(T)
        # Translation should be zero
        np.testing.assert_allclose(T[:3, 3], np.zeros(3), atol=1e-10)
