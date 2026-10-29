"""
config.py — Feature configuration factory and compatibility validation.

Valid detector/descriptor combinations
---------------------------------------
Not all detector–descriptor pairs are meaningful or technically valid.
This module enforces the allowed combinations and provides a unified
``FeatureConfig`` object used throughout the pipeline.

Compatibility rules
-------------------
* Binary descriptors (BRIEF, ORB, BRISK) must use Hamming distance matching.
* FAST produces unoriented keypoints. Using ORB descriptor on FAST keypoints
  assigns orientation from the image patch, which is valid but the detector
  does not perform scale estimation — document this limitation.
* ORB detector + ORB descriptor uses the same cv2.ORB_create object for
  both detection and description (the standard and most efficient usage).
* BRISK descriptor can be applied to keypoints detected by other detectors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2

from src.features.detector import create_detector, _LimitedDetector
from src.features.descriptor import create_descriptor, ManualBRIEF, get_implementation_label


# Valid (detector_name, descriptor_name) pairs
VALID_COMBINATIONS = {
    ("FAST", "BRIEF"),
    ("FAST", "ORB"),
    ("ORB",  "ORB"),
    ("ORB",  "BRISK"),
    ("FASTER", "ORB"),
    ("FASTER", "BRIEF"),
}


@dataclass
class FeatureConfig:
    """Validated feature configuration with instantiated detector and descriptor."""
    detector_name: str
    descriptor_name: str
    detector: object
    descriptor: object
    descriptor_label: str   # may differ from descriptor_name (e.g., ManualBRIEF)
    norm_type: int          # cv2.NORM_HAMMING for binary descriptors
    config_id: str          # human-readable identifier for results tables

    @property
    def is_joint_orb(self) -> bool:
        """True when ORB detector and descriptor share the same cv2.ORB object."""
        return (self.detector_name == "ORB" and
                self.descriptor_name == "ORB" and
                self.detector is self.descriptor)


def build_feature_config(detector_cfg: dict, descriptor_cfg: dict) -> FeatureConfig:
    """Create a validated FeatureConfig from detector and descriptor config dicts.

    Parameters
    ----------
    detector_cfg   : dict with 'name' and detector-specific keys.
    descriptor_cfg : dict with 'name' and descriptor-specific keys.

    Returns
    -------
    FeatureConfig

    Raises
    ------
    ValueError
        If the (detector, descriptor) combination is not supported.
    NotImplementedError
        If FASTER is requested.
    """
    det_name  = detector_cfg.get("name", "").upper()
    desc_name = descriptor_cfg.get("name", "").upper()

    if (det_name, desc_name) not in VALID_COMBINATIONS:
        raise ValueError(
            f"Unsupported detector/descriptor combination: ({det_name}, {desc_name}). "
            f"Valid combinations: {sorted(VALID_COMBINATIONS)}"
        )

    # Special case: ORB+ORB shares one object
    if det_name == "ORB" and desc_name == "ORB":
        orb = create_detector(detector_cfg)
        detector = orb
        descriptor = orb
    else:
        detector = create_detector(detector_cfg)
        descriptor = create_descriptor(descriptor_cfg)

    desc_label = get_implementation_label(descriptor)

    # All supported descriptors are binary → Hamming norm
    norm_type = cv2.NORM_HAMMING

    config_id = f"{det_name.lower()}_{desc_name.lower()}"

    return FeatureConfig(
        detector_name=det_name,
        descriptor_name=desc_name,
        detector=detector,
        descriptor=descriptor,
        descriptor_label=desc_label,
        norm_type=norm_type,
        config_id=config_id,
    )


def config_from_yaml(cfg: dict) -> FeatureConfig:
    """Build a FeatureConfig directly from an experiment YAML dict.

    Expects top-level keys: ``detector`` and ``descriptor``.
    """
    return build_feature_config(
        detector_cfg=cfg["detector"],
        descriptor_cfg=cfg["descriptor"],
    )
