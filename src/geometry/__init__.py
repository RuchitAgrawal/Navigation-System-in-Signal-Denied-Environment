"""src/geometry/__init__.py — Public API for geometry module."""
from src.geometry.transforms import (
    make_pose,
    pose_identity,
    invert_pose,
    compose_poses,
    quat_to_rotation,
    rotation_to_quat,
    rotation_angle_rad,
    is_valid_rotation,
    is_valid_pose,
    ned_body_to_camera_pose,
)
from src.geometry.pose import PoseAccumulator, FrameDiagnostics, FrameStatus
from src.geometry.essential import estimate_pose, build_intrinsic_matrix, EssentialResult

__all__ = [
    "make_pose", "pose_identity", "invert_pose", "compose_poses",
    "quat_to_rotation", "rotation_to_quat", "rotation_angle_rad",
    "is_valid_rotation", "is_valid_pose", "ned_body_to_camera_pose",
    "PoseAccumulator", "FrameDiagnostics", "FrameStatus",
    "estimate_pose", "build_intrinsic_matrix", "EssentialResult",
]
