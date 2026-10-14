"""
src/visualization/__init__.py — Public API for the visualization module.
"""
from src.visualization.trajectory_plot import (
    plot_trajectory_2d,
    plot_ate_over_time,
    plot_benchmark_comparison,
)
from src.visualization.match_plot import draw_matches_inliers_outliers
from src.visualization.report import print_summary_table, save_markdown_summary

__all__ = [
    "plot_trajectory_2d",
    "plot_ate_over_time",
    "plot_benchmark_comparison",
    "draw_matches_inliers_outliers",
    "print_summary_table",
    "save_markdown_summary",
]
