"""
test_features.py — Unit tests for the feature detector/descriptor factory.

Verifies that:
- Valid combos instantiate without error.
- Invalid combos raise ValueError.
- FASTER raises NotImplementedError (not silently aliased to FAST).
- ManualBRIEF produces correct descriptor shape.
- FeatureConfig flags ORB+ORB as joint correctly.
"""
import numpy as np
import pytest
import cv2

from src.features.detector import create_detector
from src.features.descriptor import create_descriptor, ManualBRIEF
from src.features.config import build_feature_config, FeatureConfig


class TestDetectorFactory:
    def test_fast_creates_successfully(self):
        cfg = {"name": "FAST", "threshold": 20, "nonmax_suppression": True, "max_keypoints": 500}
        det = create_detector(cfg)
        assert det is not None

    def test_orb_creates_successfully(self):
        cfg = {"name": "ORB", "nfeatures": 500}
        det = create_detector(cfg)
        assert isinstance(det, cv2.ORB)

    def test_faster_raises_not_implemented(self):
        cfg = {"name": "FASTER"}
        with pytest.raises(NotImplementedError, match="FASTER"):
            create_detector(cfg)

    def test_unknown_detector_raises_value_error(self):
        cfg = {"name": "SIFT"}
        with pytest.raises(ValueError, match="Unknown detector"):
            create_detector(cfg)

    def test_fast_limits_keypoints(self):
        """FAST with max_keypoints=50 should return at most 50 keypoints."""
        cfg = {"name": "FAST", "threshold": 5, "max_keypoints": 50}
        det = create_detector(cfg)
        # Generate a random-noise image with many corners
        rng = np.random.default_rng(0)
        img = rng.integers(0, 255, (480, 640), dtype=np.uint8)
        kps = det.detect(img)
        assert len(kps) <= 50


class TestDescriptorFactory:
    def test_orb_descriptor_creates_successfully(self):
        cfg = {"name": "ORB", "nfeatures": 500}
        desc = create_descriptor(cfg)
        assert desc is not None

    def test_brisk_creates_successfully(self):
        cfg = {"name": "BRISK", "thresh": 30, "octaves": 3}
        desc = create_descriptor(cfg)
        assert isinstance(desc, cv2.BRISK)

    def test_unknown_descriptor_raises(self):
        with pytest.raises(ValueError, match="Unknown descriptor"):
            create_descriptor({"name": "SURF"})

    def test_brief_fallback_to_manual(self):
        """If contrib unavailable, should get ManualBRIEF (no error raised)."""
        import warnings
        cfg = {"name": "BRIEF", "bytes": 32}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            desc = create_descriptor(cfg)
        # Either contrib BRIEF or ManualBRIEF — both are valid
        assert desc is not None


class TestManualBRIEF:
    def test_descriptor_shape(self):
        brief = ManualBRIEF(bytes_=32)
        rng = np.random.default_rng(1)
        img = rng.integers(0, 255, (480, 640), dtype=np.uint8)
        # Create keypoints well inside the image
        kps = [cv2.KeyPoint(200.0, 200.0, 10.0),
               cv2.KeyPoint(300.0, 300.0, 10.0),
               cv2.KeyPoint(100.0, 150.0, 10.0)]
        valid_kps, descs = brief.compute(img, kps)
        assert descs.shape[1] == 32
        assert descs.dtype == np.uint8

    def test_border_keypoints_dropped(self):
        """Keypoints too close to image border should be dropped."""
        brief = ManualBRIEF(bytes_=32, patch_size=48)
        rng = np.random.default_rng(2)
        img = rng.integers(0, 255, (480, 640), dtype=np.uint8)
        border_kp = cv2.KeyPoint(1.0, 1.0, 5.0)  # very close to border
        interior_kp = cv2.KeyPoint(320.0, 240.0, 5.0)
        valid_kps, descs = brief.compute(img, [border_kp, interior_kp])
        assert len(valid_kps) == 1  # border kp dropped


class TestFeatureConfig:
    def test_orb_orb_is_joint(self):
        cfg = build_feature_config(
            {"name": "ORB", "nfeatures": 500},
            {"name": "ORB"},
        )
        assert cfg.is_joint_orb
        assert cfg.detector is cfg.descriptor

    def test_fast_orb_is_not_joint(self):
        cfg = build_feature_config(
            {"name": "FAST", "threshold": 20},
            {"name": "ORB"},
        )
        assert not cfg.is_joint_orb

    def test_invalid_combo_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            build_feature_config({"name": "FAST"}, {"name": "BRISK"})

    def test_config_id_format(self):
        cfg = build_feature_config({"name": "ORB"}, {"name": "ORB"})
        assert cfg.config_id == "orb_orb"
