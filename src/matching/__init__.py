"""
src/matching/__init__.py — Public API for the matching module.
"""
from src.matching.matcher import (
    create_matcher,
    match_and_filter,
    matches_to_point_arrays,
)

__all__ = [
    "create_matcher",
    "match_and_filter",
    "matches_to_point_arrays",
]
