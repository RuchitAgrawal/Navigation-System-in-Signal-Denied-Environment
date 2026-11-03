"""
tests/test_trajectory_plot_3d.py — Unit tests for 3D trajectory visualization.
"""

from pathlib import Path
import numpy as np
import pytest

from src.evaluation.ate import ATEResult
from src.visualization.trajectory_plot import plot_trajectory_3d


@pytest.fixture
def mock_ate_result():
    n_frames = 25
    gt = np.zeros((n_frames, 3))
    gt[:, 0] = np.linspace(0, 5, n_frames)
    gt[:, 2] = np.sin(np.linspace(0, np.pi, n_frames))

    est = gt + np.random.default_rng(42).normal(0, 0.05, gt.shape)
    errors = np.linalg.norm(est - gt, axis=1)

    return ATEResult(
        alignment="sim3",
        scale=1.02,
        rmse=float(np.sqrt(np.mean(errors ** 2))),
        mean=float(np.mean(errors)),
        median=float(np.median(errors)),
        std=float(np.std(errors)),
        per_frame_errors=errors,
        aligned_est_positions=est,
        gt_positions=gt,
        n_frames=n_frames,
    )


def test_plot_trajectory_3d_saves_file(mock_ate_result, tmp_path):
    out_file = tmp_path / "traj3d.png"
    plot_trajectory_3d(
        ate_result=mock_ate_result,
        config_id="faster_orb_v1",
        dataset_name="icl_nuim",
        sequence_name="living_room",
        save_path=out_file,
    )
    assert out_file.exists()
    assert out_file.stat().st_size > 1000

