"""
src/features/__init__.py — Public API for the features module.
"""
from src.features.detector import create_detector
from src.features.descriptor import create_descriptor, ManualBRIEF, get_implementation_label
from src.features.config import (
    FeatureConfig,
    build_feature_config,
    config_from_yaml,
    VALID_COMBINATIONS,
)

__all__ = [
    "create_detector",
    "create_descriptor",
    "ManualBRIEF",
    "get_implementation_label",
    "FeatureConfig",
    "build_feature_config",
    "config_from_yaml",
    "VALID_COMBINATIONS",
]
