"""
conftest.py — Shared pytest fixtures.
"""
import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from src.geometry.transforms import make_pose, pose_identity


@pytest.fixture
def identity_pose():
    return pose_identity()


@pytest.fixture
def known_rotation_pose():
    """A pose with a 45-degree yaw around the Y axis and translation [1, 2, 3]."""
    R = Rotation.from_euler("y", 45, degrees=True).as_matrix()
    t = np.array([1.0, 2.0, 3.0])
    return make_pose(R, t)


@pytest.fixture
def straight_trajectory():
    """Synthetic straight-line trajectory: 50 poses, moving +X at 0.1 m/frame."""
    poses = []
    for i in range(50):
        T = make_pose(np.eye(3), np.array([i * 0.1, 0.0, 0.0]))
        poses.append(T)
    return poses


@pytest.fixture
def circular_trajectory():
    """Synthetic circular trajectory: 100 poses around the Y axis."""
    poses = []
    n = 100
    radius = 5.0
    for i in range(n):
        angle = 2 * np.pi * i / n
        t = np.array([radius * np.cos(angle), 0.0, radius * np.sin(angle)])
        yaw = angle + np.pi / 2
        R = Rotation.from_euler("y", yaw).as_matrix()
        poses.append(make_pose(R, t))
    return poses
