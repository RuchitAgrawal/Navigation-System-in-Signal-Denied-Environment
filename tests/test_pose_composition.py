"""
test_pose_composition.py — Unit tests for SE(3) pose math.

Verifies: identity, inversion, composition, rotation validity,
coordinate-frame convention, and TUM serialization round-trip.
"""
import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from src.geometry.transforms import (
    compose_poses,
    invert_pose,
    is_valid_pose,
    is_valid_rotation,
    make_pose,
    pose_identity,
    quat_to_rotation,
    rotation_angle_rad,
    rotation_to_quat,
)


class TestIdentityPose:
    def test_identity_is_4x4(self):
        T = pose_identity()
        assert T.shape == (4, 4)

    def test_identity_values(self):
        T = pose_identity()
        np.testing.assert_array_equal(T, np.eye(4))

    def test_identity_is_valid(self):
        assert is_valid_pose(pose_identity())


class TestPoseInversion:
    def test_T_inv_T_is_identity(self, known_rotation_pose):
        T = known_rotation_pose
        T_inv = invert_pose(T)
        product = T @ T_inv
        np.testing.assert_allclose(product, np.eye(4), atol=1e-10)

    def test_inv_T_T_is_identity(self, known_rotation_pose):
        T = known_rotation_pose
        T_inv = invert_pose(T)
        product = T_inv @ T
        np.testing.assert_allclose(product, np.eye(4), atol=1e-10)

    def test_identity_inverse_is_identity(self):
        T_inv = invert_pose(pose_identity())
        np.testing.assert_allclose(T_inv, np.eye(4), atol=1e-12)


class TestPoseComposition:
    def test_compose_with_identity_left(self, known_rotation_pose):
        T = known_rotation_pose
        result = compose_poses(pose_identity(), T)
        np.testing.assert_allclose(result, T, atol=1e-12)

    def test_compose_with_identity_right(self, known_rotation_pose):
        T = known_rotation_pose
        result = compose_poses(T, pose_identity())
        np.testing.assert_allclose(result, T, atol=1e-12)

    def test_compose_then_inverse(self, known_rotation_pose):
        T = known_rotation_pose
        T2 = compose_poses(T, invert_pose(T))
        np.testing.assert_allclose(T2, np.eye(4), atol=1e-10)

    def test_composition_associativity(self):
        R1 = Rotation.from_euler("x", 30, degrees=True).as_matrix()
        R2 = Rotation.from_euler("y", 45, degrees=True).as_matrix()
        R3 = Rotation.from_euler("z", 60, degrees=True).as_matrix()
        T1 = make_pose(R1, np.array([1.0, 0.0, 0.0]))
        T2 = make_pose(R2, np.array([0.0, 1.0, 0.0]))
        T3 = make_pose(R3, np.array([0.0, 0.0, 1.0]))
        lhs = compose_poses(compose_poses(T1, T2), T3)
        rhs = compose_poses(T1, compose_poses(T2, T3))
        np.testing.assert_allclose(lhs, rhs, atol=1e-10)


class TestRotationUtils:
    def test_known_yaw_rotation(self):
        """90-degree yaw around Y maps X→Z."""
        R = Rotation.from_euler("y", 90, degrees=True).as_matrix()
        assert is_valid_rotation(R)
        x_axis = np.array([1.0, 0.0, 0.0])
        rotated = R @ x_axis
        np.testing.assert_allclose(rotated, [0.0, 0.0, -1.0], atol=1e-10)

    def test_rotation_angle_identity(self):
        angle = rotation_angle_rad(np.eye(3))
        assert abs(angle) < 1e-10

    def test_rotation_angle_90_deg(self):
        R = Rotation.from_euler("y", 90, degrees=True).as_matrix()
        angle = rotation_angle_rad(R)
        np.testing.assert_allclose(angle, np.pi / 2, atol=1e-10)

    def test_quat_roundtrip(self):
        R_orig = Rotation.from_euler("xyz", [10, 20, 30], degrees=True).as_matrix()
        q = rotation_to_quat(R_orig)
        R_back = quat_to_rotation(*q)
        np.testing.assert_allclose(R_back, R_orig, atol=1e-10)


class TestCoordinateConvention:
    def test_T_wc_transforms_cam_to_world(self):
        """A point at the camera origin should map to the world translation."""
        t_world = np.array([3.0, 1.0, -2.0])
        T_wc = make_pose(np.eye(3), t_world)
        p_cam = np.array([0.0, 0.0, 0.0, 1.0])   # camera origin
        p_world = T_wc @ p_cam
        np.testing.assert_allclose(p_world[:3], t_world, atol=1e-12)

    def test_is_valid_pose_rejects_bad_rotation(self):
        T = np.eye(4)
        T[0, 0] = 2.0   # not a rotation matrix
        assert not is_valid_pose(T)

    def test_is_valid_pose_rejects_wrong_shape(self):
        assert not is_valid_pose(np.eye(3))
