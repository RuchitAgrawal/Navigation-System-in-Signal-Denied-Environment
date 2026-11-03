"""
tests/test_inlier_plot.py — Unit tests for RANSAC inlier ratio visualization.
"""

from pathlib import Path
import pytest

from src.geometry.pose import FrameDiagnostics, FrameStatus
from src.visualization.inlier_plot import plot_inlier_history


@pytest.fixture
def sample_diagnostics():
    diags = []
    for i in range(15):
        d = FrameDiagnostics(
            frame_idx=i,
            status=FrameStatus.SUCCESS,
            n_keypoints_prev=500,
            n_keypoints_curr=520,
            n_raw_matches=250,
            n_filtered_matches=180,
            n_ransac_inliers=140,
            ransac_inlier_ratio=140 / 180,
            total_time_ms=35.0,
        )
        diags.append(d)
    return diags


def test_plot_inlier_history_saves_file(sample_diagnostics, tmp_path):
    out_file = tmp_path / "inlier_hist.png"
    result = plot_inlier_history(
        diagnostics=sample_diagnostics,
        config_id="faster_orb_v1",
        dataset_name="icl_nuim",
        save_path=out_file,
    )
    assert result.exists()
    assert result.stat().st_size > 1000

