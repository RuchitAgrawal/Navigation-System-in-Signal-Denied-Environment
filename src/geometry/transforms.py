"""
transforms.py — SE(3) and coordinate-frame utilities.

Coordinate-frame convention used throughout this pipeline
---------------------------------------------------------
All poses are stored as **T_wc** — a 4×4 float64 homogeneous matrix that
transforms a point expressed in the **camera frame** to the **world frame**:

    p_world = T_wc @ p_camera

* World frame: right-handed, Y-up (matching ICL-NUIM convention).
* Pose accumulation:
      T_wc[t] = T_wc[t-1] @ inv(T_c(t-1)_to_c(t))
  where T_c(t-1)_to_c(t) is the relative transform from frame t-1 to t
  recovered by Essential-matrix decomposition.

Reference: Hartley & Zisserman, "Multiple View Geometry in Computer Vision",
           Chapter 9 (Essential Matrix) and Appendix A (SE(3) algebra).
"""

from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation


# ---------------------------------------------------------------------------
# Basic SE(3) helpers
# ---------------------------------------------------------------------------

def make_pose(R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Assemble a 4×4 T_wc matrix from a rotation matrix and translation vector.

    Parameters
    ----------
    R : (3, 3) ndarray   Rotation part.
    t : (3,) ndarray     Translation part.

    Returns
    -------
    T : (4, 4) float64 ndarray
    """
    T = np.eye(4, dtype=np.float64)
    T[:3, :3] = R.astype(np.float64)
    T[:3,  3] = t.flatten().astype(np.float64)
    return T


def pose_identity() -> np.ndarray:
    """Return the 4×4 identity pose (camera at world origin, no rotation)."""
    return np.eye(4, dtype=np.float64)


def invert_pose(T: np.ndarray) -> np.ndarray:
    """Efficiently invert an SE(3) matrix without using np.linalg.inv.

    For T = [R | t; 0 | 1]:
        T^{-1} = [R^T | -R^T t; 0 | 1]
    """
    T = T.astype(np.float64)
    R = T[:3, :3]
    t = T[:3,  3]
    T_inv = np.eye(4, dtype=np.float64)
    T_inv[:3, :3] = R.T
    T_inv[:3,  3] = -R.T @ t
    return T_inv


def compose_poses(T_ab: np.ndarray, T_bc: np.ndarray) -> np.ndarray:
    """Compose two SE(3) transforms: T_ac = T_ab @ T_bc."""
    return T_ab.astype(np.float64) @ T_bc.astype(np.float64)


# ---------------------------------------------------------------------------
# Rotation utilities
# ---------------------------------------------------------------------------

def quat_to_rotation(qx: float, qy: float, qz: float, qw: float) -> np.ndarray:
    """Convert a unit quaternion (x, y, z, w) to a 3×3 rotation matrix."""
    r = Rotation.from_quat([qx, qy, qz, qw])
    return r.as_matrix().astype(np.float64)


def rotation_to_quat(R: np.ndarray):
    """Convert a 3×3 rotation matrix to a quaternion (x, y, z, w)."""
    r = Rotation.from_matrix(R.astype(np.float64))
    return r.as_quat()  # (x, y, z, w)


def rotation_angle_rad(R: np.ndarray) -> float:
    """Return the rotation angle (radians) of a rotation matrix via the trace formula.

    angle = arccos((trace(R) - 1) / 2)
    """
    cos_angle = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.arccos(cos_angle))


# ---------------------------------------------------------------------------
# TartanAir coordinate conversion
# ---------------------------------------------------------------------------

# TartanAir pose_left.txt uses NED (North-East-Down) body-frame convention.
# We convert NED body poses to camera-frame T_wc for internal use.
#
# The NED-to-camera rotation depends on how the camera is mounted.
# For TartanAir's left camera (standard configuration):
#   x_cam =  x_ned   (forward → forward)
#   y_cam = -z_ned   (down → up, camera Y points upward)
#   z_cam =  y_ned   (right → into scene, camera Z points forward... actually:
#
# TartanAir uses OpenCV camera convention:
#   x_cam right, y_cam down, z_cam forward (into scene)
# TartanAir body/NED:
#   x forward, y right, z down
#
# Rotation from NED to camera:  R_cam_ned
#   x_cam = y_ned   (right)
#   y_cam = z_ned   (down)
#   z_cam = x_ned   (forward)

_R_CAM_NED = np.array([
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [1.0, 0.0, 0.0],
], dtype=np.float64)


def ned_body_to_camera_pose(t_ned: np.ndarray,
                             q_ned: np.ndarray) -> np.ndarray:
    """Convert a TartanAir NED-body pose to a camera-frame T_wc matrix.

    Parameters
    ----------
    t_ned : (3,) array  Translation [x, y, z] in NED world coordinates.
    q_ned : (4,) array  Quaternion [qx, qy, qz, qw] in NED body frame.

    Returns
    -------
    T_wc : (4, 4) float64 ndarray
    """
    R_ned = quat_to_rotation(*q_ned)
    # Body-to-world in NED:  R_w_ned = R_ned
    # Camera-to-world:       R_w_cam = R_w_ned @ R_ned_cam
    R_ned_cam = _R_CAM_NED.T          # inverse of _R_CAM_NED (orthogonal)
    R_wc = R_ned @ R_ned_cam
    # Translation in world frame (NED world = world frame for our purposes)
    t_wc = t_ned.astype(np.float64)
    return make_pose(R_wc, t_wc)


# ---------------------------------------------------------------------------
# Validation helpers (used in unit tests)
# ---------------------------------------------------------------------------

def is_valid_rotation(R: np.ndarray, tol: float = 1e-6) -> bool:
    """Return True if R is a valid rotation matrix (det ≈ 1, R^T R ≈ I)."""
    if R.shape != (3, 3):
        return False
    det = np.linalg.det(R)
    if abs(det - 1.0) > tol:
        return False
    residual = np.max(np.abs(R.T @ R - np.eye(3)))
    return residual < tol


def is_valid_pose(T: np.ndarray, tol: float = 1e-6) -> bool:
    """Return True if T is a valid 4×4 SE(3) homogeneous matrix."""
    if T.shape != (4, 4):
        return False
    if not np.allclose(T[3], [0, 0, 0, 1], atol=tol):
        return False
    return is_valid_rotation(T[:3, :3], tol=tol)
