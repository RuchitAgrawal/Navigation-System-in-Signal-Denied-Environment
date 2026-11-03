"""
tests/test_evaluate_trajectory_cli.py — Unit tests for evaluate_trajectory CLI.
"""

import json
import subprocess
import sys
from pathlib import Path
import pytest


def test_evaluate_trajectory_cli_with_json_out(tmp_path):
    est_file = "results/csv/faster_orb_v1__icl_nuim__living_room_traj1_loop_trajectory.txt"
    gt_file = "data/icl_nuim/living_room_traj1_loop/groundtruth.txt"
    out_json = tmp_path / "metrics_test.json"

    if Path(est_file).exists() and Path(gt_file).exists():
        cmd = [
            sys.executable,
            "scripts/evaluate_trajectory.py",
            "--est", est_file,
            "--gt", gt_file,
            "--alignment", "sim3",
            "--json-out", str(out_json),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0
        assert out_json.exists()

        with open(out_json) as f:
            data = json.load(f)

        assert "ate_rmse_m" in data
        assert "rpe_trans_rmse_m" in data
        assert data["alignment"] == "sim3"
