"""
tests/test_motion_model.py — Unit tests for ConstantVelocityMotionModel.
"""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from src.odometry.motion_model import ConstantVelocityMotionModel


class TestConstantVelocityMotionModel:
    def test_initial_motion_accepted(self):
        mm = ConstantVelocityMotionModel()
        assert not mm.has_prior
        R = np.eye(3)
        t = np.array([0.1, 0.0, 0.0])
        res = mm.validate_relative_pose(R, t, timestamp=1.0)
        assert res.is_valid

    def test_smooth_motion_accepted(self):
        mm = ConstantVelocityMotionModel()
        R1 = np.eye(3)
        t1 = np.array([0.1, 0.0, 0.0])
        mm.update(R1, t1, timestamp=1.0)

        # Small 2 degree turn and same translation
        R2 = Rotation.from_euler("y", 2.0, degrees=True).as_matrix()
        t2 = np.array([0.1, 0.005, 0.0])
        res = mm.validate_relative_pose(R2, t2, timestamp=2.0)
        assert res.is_valid
        assert res.angular_change_deg < 5.0

    def test_excessive_angular_jump_rejected(self):
        mm = ConstantVelocityMotionModel(max_angular_jump_deg=30.0)
        R1 = np.eye(3)
        t1 = np.array([0.1, 0.0, 0.0])
        mm.update(R1, t1, timestamp=1.0)

        # Sudden 80 degree orientation jump (unnatural jerk)
        R2 = Rotation.from_euler("y", 80.0, degrees=True).as_matrix()
        t2 = np.array([0.1, 0.0, 0.0])
        res = mm.validate_relative_pose(R2, t2, timestamp=2.0)
        assert not res.is_valid
        assert "excessive_angular_jump" in res.reason

    def test_unnatural_direction_reversal_rejected(self):
        mm = ConstantVelocityMotionModel(max_direction_change_deg=60.0)
        R1 = np.eye(3)
        t1 = np.array([0.1, 0.0, 0.0])  # Moving +X
        mm.update(R1, t1, timestamp=1.0)

        # Sudden 180 degree reversal (moving -X)
        R2 = np.eye(3)
        t2 = np.array([-0.1, 0.0, 0.0])
        res = mm.validate_relative_pose(R2, t2, timestamp=2.0)
        assert not res.is_valid
        assert "unnatural_direction_reversal" in res.reason

    def test_reset_clears_prior(self):
        mm = ConstantVelocityMotionModel()
        mm.update(np.eye(3), np.array([0.1, 0.0, 0.0]), timestamp=1.0)
        assert mm.has_prior
        mm.reset()
        assert not mm.has_prior
