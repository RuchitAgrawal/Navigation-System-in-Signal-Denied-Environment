"""src/evaluation/__init__.py — Public API for evaluation module."""
from src.evaluation.ate import compute_ate, umeyama_alignment, ATEResult
from src.evaluation.rpe import compute_rpe, RPEResult
from src.evaluation.metrics import (
    build_summary_row,
    diagnostics_to_dataframe,
    save_per_frame_csv,
    save_summary_csv,
)

__all__ = [
    "compute_ate", "umeyama_alignment", "ATEResult",
    "compute_rpe", "RPEResult",
    "build_summary_row", "diagnostics_to_dataframe",
    "save_per_frame_csv", "save_summary_csv",
]
