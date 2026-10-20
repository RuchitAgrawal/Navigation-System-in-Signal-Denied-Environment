"""
tests/test_scale_plot.py — Unit tests for scale drift visualization.

Verifies that plot_scale_drift runs without error and saves a valid PNG
on a synthetic scale array.
"""
import numpy as np
import pytest
from pathlib import Path


class TestPlotScaleDrift:
    def test_creates_png_file(self, tmp_path):
        """plot_scale_drift should save a PNG without raising."""
        from src.visualization.scale_plot import plot_scale_drift

        scales = np.linspace(0.8, 1.2, 50)
        save_path = tmp_path / "scale_drift.png"

        plot_scale_drift(
            scales=scales,
            config_id="orb_orb",
            dataset_name="icl_nuim",
            save_path=save_path,
            window=5,
        )
        assert save_path.exists()
        assert save_path.stat().st_size > 0

    def test_handles_nan_values(self, tmp_path):
        """NaN values in scales array should not crash the plot."""
        from src.visualization.scale_plot import plot_scale_drift

        scales = np.array([1.0, np.nan, 1.1, np.nan, 0.95, 1.05])
        save_path = tmp_path / "scale_nan.png"

        plot_scale_drift(
            scales=scales,
            config_id="fast_orb",
            dataset_name="tartanair",
            save_path=save_path,
        )
        assert save_path.exists()

    def test_empty_finite_values(self, tmp_path):
        """All-NaN scales array should produce an empty plot without crash."""
        from src.visualization.scale_plot import plot_scale_drift

        scales = np.full(10, np.nan)
        save_path = tmp_path / "scale_allnan.png"

        plot_scale_drift(
            scales=scales,
            config_id="orb_brisk",
            dataset_name="icl_nuim",
            save_path=save_path,
        )
        # Just verify it didn't crash — file may or may not be saved
