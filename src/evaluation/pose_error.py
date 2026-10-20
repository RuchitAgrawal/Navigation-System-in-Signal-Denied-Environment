# evaluation/pose_error.py -- Pose-level error decomposition
from __future__ import annotations
import numpy as np
from src.geometry.transforms import rotation_angle_rad


def decompose_pose_error(T_est: np.ndarray, T_gt: np.ndarray) -> dict:
    '''Decompose the error between two SE(3) poses into translation and rotation.

    Parameters
    ----------
    T_est : (4, 4) estimated T_wc
    T_gt  : (4, 4) ground-truth T_wc

    Returns
    -------
    dict with keys: trans_error_m, rot_error_deg, rot_error_rad
    '''
    import numpy as np
    from src.geometry.transforms import invert_pose
    E = invert_pose(T_est) @ T_gt
    trans_err = float(np.linalg.norm(E[:3, 3]))
    rot_err_rad = rotation_angle_rad(E[:3, :3])
    return {
        'trans_error_m': trans_err,
        'rot_error_rad': rot_err_rad,
        'rot_error_deg': float(np.degrees(rot_err_rad)),
    }


