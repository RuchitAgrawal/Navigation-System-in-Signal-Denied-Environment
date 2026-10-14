"""
test_extractor.py — Unit tests for the unified FeatureExtractor wrapper.
"""
import numpy as np
import pytest
import cv2

from src.features.config import build_feature_config
from src.features.extractor import FeatureExtractor, ExtractionResult


def _random_gray(h: int = 480, w: int = 640, seed: int = 0) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, 255, (h, w), dtype=np.uint8)


class TestExtractionResult:
    def test_n_keypoints_property(self):
        kps = [cv2.KeyPoint(100.0, 100.0, 5.0)] * 10
        result = ExtractionResult(keypoints=kps, descriptors=np.zeros((10, 32), dtype=np.uint8),
                                  detect_ms=1.0, describe_ms=0.5)
        assert result.n_keypoints == 10

    def test_has_descriptors_true(self):
        kps = [cv2.KeyPoint(100.0, 100.0, 5.0)]
        result = ExtractionResult(keypoints=kps,
                                  descriptors=np.zeros((1, 32), dtype=np.uint8),
                                  detect_ms=1.0, describe_ms=0.5)
        assert result.has_descriptors

    def test_has_descriptors_false_when_none(self):
        result = ExtractionResult(keypoints=[], descriptors=None,
                                  detect_ms=0.0, describe_ms=0.0)
        assert not result.has_descriptors


class TestFeatureExtractorORBORB:
    def setup_method(self):
        self.cfg = build_feature_config({"name": "ORB", "nfeatures": 500},
                                         {"name": "ORB"})
        self.extractor = FeatureExtractor(self.cfg)
        self.img = _random_gray(seed=1)

    def test_returns_extraction_result(self):
        result = self.extractor.extract(self.img)
        assert isinstance(result, ExtractionResult)

    def test_detects_keypoints(self):
        result = self.extractor.extract(self.img)
        assert result.n_keypoints > 0

    def test_descriptors_shape(self):
        result = self.extractor.extract(self.img)
        if result.has_descriptors:
            assert result.descriptors.shape[1] == 32  # ORB = 32 bytes
            assert result.descriptors.dtype == np.uint8

    def test_timing_recorded(self):
        result = self.extractor.extract(self.img)
        assert result.detect_ms >= 0
        assert result.describe_ms >= 0


class TestFeatureExtractorFASTORB:
    def setup_method(self):
        self.cfg = build_feature_config(
            {"name": "FAST", "threshold": 20, "max_keypoints": 200},
            {"name": "ORB"},
        )
        self.extractor = FeatureExtractor(self.cfg)
        self.img = _random_gray(seed=2)

    def test_detects_keypoints(self):
        result = self.extractor.extract(self.img)
        assert result.n_keypoints > 0

    def test_max_keypoints_respected(self):
        result = self.extractor.extract(self.img)
        assert result.n_keypoints <= 200

    def test_descriptors_shape(self):
        result = self.extractor.extract(self.img)
        if result.has_descriptors:
            # ORB descriptor = 32 bytes
            assert result.descriptors.shape[1] == 32


class TestFeatureExtractorFASTBRIEF:
    def setup_method(self):
        import warnings
        cfg = build_feature_config(
            {"name": "FAST", "threshold": 20, "max_keypoints": 200},
            {"name": "BRIEF", "bytes": 32},
        )
        self.extractor = FeatureExtractor(cfg)
        self.img = _random_gray(seed=3)

    def test_returns_result(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.extractor.extract(self.img)
        assert isinstance(result, ExtractionResult)
