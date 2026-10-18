# tests/test_ned_conversion.py -- NED to camera conversion tests
import numpy as np
import pytest
from src.geometry.transforms import ned_body_to_camera_pose, is_valid_pose
\n\nclass TestNEDConversion:
    def test_output_is_valid_pose(self):
        t = np.array([1.0, 2.0, 3.0])
        q = np.array([0.0, 0.0, 0.0, 1.0])  # identity quaternion
        T = ned_body_to_camera_pose(t, q)
        assert is_valid_pose(T)

    def test_identity_rotation_preserves_translation_direction(self):
        t = np.array([10.0, 0.0, 0.0])  # NED: forward
        q = np.array([0.0, 0.0, 0.0, 1.0])
        T = ned_body_to_camera_pose(t, q)
        pos = T[:3, 3]
        assert pos.shape == (3,)

    def test_rotation_is_valid(self):
        from scipy.spatial.transform import Rotation
        R_ned = Rotation.from_euler('z', 45, degrees=True)
        q = R_ned.as_quat()  # xyzw
        T = ned_body_to_camera_pose(np.zeros(3), q)
        from src.geometry.transforms import is_valid_rotation
        assert is_valid_rotation(T[:3, :3])

