# tests/test_pose_error.py -- Unit tests for pose error decomposition
import numpy as np
from src.evaluation.pose_error import decompose_pose_error
from src.geometry.transforms import make_pose
\n\nclass TestDecomposePoseError:
    def test_zero_error_for_identical_poses(self):
        T = make_pose(np.eye(3), np.array([1.0, 2.0, 3.0]))
        err = decompose_pose_error(T, T)
        assert abs(err['trans_error_m']) < 1e-10
        assert abs(err['rot_error_deg']) < 1e-8

    def test_translation_error_detected(self):
        T_est = make_pose(np.eye(3), np.array([0.0, 0.0, 0.0]))
        T_gt  = make_pose(np.eye(3), np.array([1.0, 0.0, 0.0]))
        err = decompose_pose_error(T_est, T_gt)
        np.testing.assert_allclose(err['trans_error_m'], 1.0, atol=1e-10)

    def test_rotation_error_detected(self):
        from scipy.spatial.transform import Rotation
        R = Rotation.from_euler('y', 45, degrees=True).as_matrix()
        T_est = make_pose(np.eye(3), np.zeros(3))
        T_gt  = make_pose(R, np.zeros(3))
        err = decompose_pose_error(T_est, T_gt)
        np.testing.assert_allclose(err['rot_error_deg'], 45.0, atol=0.01)

