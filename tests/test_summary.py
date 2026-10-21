"""
tests/test_summary.py — Unit tests for aggregate benchmark summary utilities.
"""
import numpy as np
import pytest

from src.evaluation.summary import (
    find_best_config,
    compute_aggregate_stats,
    rank_configs,
)


SAMPLE_ROWS = [
    {"config_id": "orb_orb",    "dataset": "icl_nuim",  "ate_rmse_m": 0.05, "mean_fps": 25.0},
    {"config_id": "fast_orb",   "dataset": "icl_nuim",  "ate_rmse_m": 0.08, "mean_fps": 40.0},
    {"config_id": "orb_brisk",  "dataset": "icl_nuim",  "ate_rmse_m": 0.06, "mean_fps": 20.0},
    {"config_id": "fast_brief", "dataset": "icl_nuim",  "ate_rmse_m": 0.12, "mean_fps": 50.0},
    {"config_id": "orb_orb",    "dataset": "tartanair", "ate_rmse_m": 0.10, "mean_fps": 24.0},
    {"config_id": "fast_orb",   "dataset": "tartanair", "ate_rmse_m": 0.09, "mean_fps": 38.0},
]


class TestFindBestConfig:
    def test_finds_lowest_ate(self):
        best = find_best_config(SAMPLE_ROWS, metric="ate_rmse_m", lower_is_better=True)
        assert best["config_id"] == "orb_orb"
        assert best["dataset"] == "icl_nuim"

    def test_finds_highest_fps(self):
        best = find_best_config(SAMPLE_ROWS, metric="mean_fps", lower_is_better=False)
        assert best["config_id"] == "fast_brief"

    def test_returns_none_for_empty(self):
        assert find_best_config([], metric="ate_rmse_m") is None

    def test_handles_missing_metric(self):
        rows = [{"config_id": "x", "ate_rmse_m": None}]
        assert find_best_config(rows, metric="ate_rmse_m") is None


class TestComputeAggregateStats:
    def test_mean_correct(self):
        stats = compute_aggregate_stats(SAMPLE_ROWS, metric="ate_rmse_m")
        expected_mean = np.mean([0.05, 0.08, 0.06, 0.12, 0.10, 0.09])
        np.testing.assert_allclose(stats["mean"], expected_mean, rtol=1e-6)

    def test_n_valid_count(self):
        stats = compute_aggregate_stats(SAMPLE_ROWS, metric="ate_rmse_m")
        assert stats["n_valid"] == 6

    def test_empty_returns_none_fields(self):
        stats = compute_aggregate_stats([], metric="ate_rmse_m")
        assert stats["mean"] is None
        assert stats["n_valid"] == 0


class TestRankConfigs:
    def test_best_ate_ranked_first(self):
        # orb_brisk: only icl_nuim row → mean = 0.06
        # orb_orb: 2 rows → mean = (0.05+0.10)/2 = 0.075
        # fast_orb: 2 rows → mean = (0.08+0.09)/2 = 0.085
        # fast_brief: 1 row → mean = 0.12
        # → orb_brisk is ranked first (lowest mean ATE)
        ranked = rank_configs(SAMPLE_ROWS, metric="ate_rmse_m", lower_is_better=True)
        assert ranked[0]["config_id"] == "orb_brisk"
        assert ranked[0]["rank"] == 1

    def test_all_configs_present(self):
        ranked = rank_configs(SAMPLE_ROWS, metric="ate_rmse_m")
        config_ids = {r["config_id"] for r in ranked}
        assert {"orb_orb", "fast_orb", "orb_brisk", "fast_brief"} == config_ids

    def test_rank_field_sequential(self):
        ranked = rank_configs(SAMPLE_ROWS, metric="ate_rmse_m")
        ranks = [r["rank"] for r in ranked]
        assert ranks == list(range(1, len(ranked) + 1))
