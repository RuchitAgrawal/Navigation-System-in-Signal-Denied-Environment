"""
tests/test_ablation_charts.py — Unit tests for ablation chart generation.
"""

from pathlib import Path
import pytest
import pandas as pd

from scripts.generate_ablation_charts import (
    load_benchmark_data,
    plot_ate_comparison,
    plot_tracking_stability,
    plot_latency_throughput,
    generate_all_ablation_charts,
)


@pytest.fixture
def mock_benchmark_df(tmp_path):
    csv_file = tmp_path / "mock_summary.csv"
    data = {
        "config_id": ["fast_orb_v1", "orb_orb_v1", "faster_orb_v1"],
        "dataset": ["icl_nuim", "icl_nuim", "tartanair"],
        "sequence": ["living_room", "living_room", "ocean"],
        "ate_rmse_m": [0.023, 0.033, 1.25],
        "tracking_success_pct": [100.0, 100.0, 50.0],
        "mean_frame_time_ms": [32.0, 55.0, 20.0],
        "mean_fps": [31.25, 18.18, 50.0],
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    return csv_file, df


def test_load_benchmark_data_valid(mock_benchmark_df):
    csv_file, _ = mock_benchmark_df
    df = load_benchmark_data(csv_file)
    assert len(df) == 3
    assert "ate_rmse_m" in df.columns
    assert df["ate_rmse_m"].iloc[0] == pytest.approx(0.023)


def test_load_benchmark_data_missing():
    with pytest.raises(FileNotFoundError):
        load_benchmark_data("non_existent_file.csv")


def test_plot_ate_comparison(mock_benchmark_df, tmp_path):
    _, df = mock_benchmark_df
    out_png = tmp_path / "ate_test.png"
    result = plot_ate_comparison(df, out_png)
    assert result.exists()
    assert result.stat().st_size > 1000


def test_plot_tracking_stability(mock_benchmark_df, tmp_path):
    _, df = mock_benchmark_df
    out_png = tmp_path / "tracking_test.png"
    result = plot_tracking_stability(df, out_png)
    assert result.exists()
    assert result.stat().st_size > 1000


def test_plot_latency_throughput(mock_benchmark_df, tmp_path):
    _, df = mock_benchmark_df
    out_png = tmp_path / "latency_test.png"
    result = plot_latency_throughput(df, out_png)
    assert result.exists()
    assert result.stat().st_size > 1000


def test_generate_all_ablation_charts_integration(tmp_path):
    # Test against real summary if exists
    real_csv = Path("results/csv/benchmark_summary.csv")
    if real_csv.exists():
        charts = generate_all_ablation_charts(real_csv, tmp_path)
        assert "ate_comparison" in charts
        assert "tracking_stability" in charts
        assert "latency_throughput" in charts
        for path in charts.values():
            assert path.exists()

