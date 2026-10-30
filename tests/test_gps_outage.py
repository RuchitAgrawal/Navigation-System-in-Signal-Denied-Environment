"""
tests/test_gps_outage.py — Unit tests for GPS outage simulation and drift analysis.
"""

from pathlib import Path
import pytest
import numpy as np

from scripts.evaluate_gps_outage import (
    simulate_gps_outage,
    plot_gps_outage_analysis,
)


@pytest.fixture
def synthetic_poses():
    """Generate 20 straight-line poses along Z axis."""
    est_poses = []
    gt_poses = []
    for i in range(20):
        # GT moves 0.1m per step along Z
        T_gt = np.eye(4)
        T_gt[2, 3] = i * 0.1
        gt_poses.append(T_gt)

        # Est has small 1% scale error and slight drift
        T_est = np.eye(4)
        T_est[2, 3] = i * 0.098
        T_est[0, 3] = i * 0.002
        est_poses.append(T_est)

    return est_poses, gt_poses


def test_insufficient_poses_raises_error():
    with pytest.raises(ValueError, match="Insufficient poses"):
        simulate_gps_outage([np.eye(4)], [np.eye(4)])


def test_simulate_gps_outage_calculation(synthetic_poses):
    est_poses, gt_poses = synthetic_poses
    res = simulate_gps_outage(est_poses, gt_poses, outage_start_idx=5)

    assert "max_drift_m" in res
    assert "mean_drift_m" in res
    assert "drift_pct" in res
    assert res["outage_start_idx"] == 5
    assert res["total_distance_m"] > 0.5
    assert res["final_drift_m"] >= 0.0


def test_plot_gps_outage_analysis(synthetic_poses, tmp_path):
    est_poses, gt_poses = synthetic_poses
    res = simulate_gps_outage(est_poses, gt_poses, outage_start_idx=5)
    out_png = tmp_path / "gps_outage_test.png"

    path = plot_gps_outage_analysis(res, out_png)
    assert path.exists()
    assert path.stat().st_size > 1000
