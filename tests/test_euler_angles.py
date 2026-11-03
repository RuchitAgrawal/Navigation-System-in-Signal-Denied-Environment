"""
tests/test_euler_angles.py — Unit tests for Euler angles and Rodrigues conversions.
"""

import numpy as np
import pytest

from src.geometry.transforms import (
    rotation_to_euler_angles,
    euler_angles_to_rotation,
    rotation_to_rodrigues,
    rodrigues_to_rotation,
    is_valid_rotation,
)


def test_euler_round_trip():
    angles = np.array([15.0, -25.0, 45.0])  # roll, pitch, yaw in degrees
    R = euler_angles_to_rotation(angles, seq="xyz", degrees=True)
    assert is_valid_rotation(R)

    recovered = rotation_to_euler_angles(R, seq="xyz", degrees=True)
    np.testing.assert_allclose(recovered, angles, atol=1e-6)


def test_euler_radians():
    angles_rad = np.array([0.2, -0.4, 0.6])
    R = euler_angles_to_rotation(angles_rad, seq="xyz", degrees=False)
    assert is_valid_rotation(R)

    recovered_rad = rotation_to_euler_angles(R, seq="xyz", degrees=False)
    np.testing.assert_allclose(recovered_rad, angles_rad, atol=1e-6)


def test_rodrigues_round_trip():
    rvec = np.array([0.1, -0.2, 0.3])
    R = rodrigues_to_rotation(rvec)
    assert is_valid_rotation(R)

    recovered_rvec = rotation_to_rodrigues(R)
    np.testing.assert_allclose(recovered_rvec, rvec, atol=1e-6)


def test_rodrigues_zero():
    rvec_zero = np.zeros(3)
    R_ident = rodrigues_to_rotation(rvec_zero)
    np.testing.assert_allclose(R_ident, np.eye(3), atol=1e-8)

