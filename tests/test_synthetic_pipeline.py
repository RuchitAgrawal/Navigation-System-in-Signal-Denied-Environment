"""
tests/test_synthetic_pipeline.py — Smoke tests for full VO pipeline on synthetic data.
"""
import numpy as np
import pytest
from src.datasets.synthetic import SyntheticDataset
from src.features.config import build_feature_config
from src.odometry.pipeline import VOPipeline
from src.geometry.pose import FrameStatus


class TestSyntheticPipeline:
    def test_pipeline_runs_without_crash(self):
        dataset = SyntheticDataset(n_frames=5, seed=42)
        fc = build_feature_config(
            {"name": "ORB", "nfeatures": 200},
            {"name": "ORB"},
        )
        pipeline = VOPipeline(fc)
        acc = pipeline.run(dataset)
        assert len(acc.poses) == len(dataset)
        assert len(acc.diagnostics) == len(dataset)

    def test_first_pose_is_identity(self):
        dataset = SyntheticDataset(n_frames=5, seed=1)
        fc = build_feature_config({"name": "ORB", "nfeatures": 200}, {"name": "ORB"})
        pipeline = VOPipeline(fc)
        acc = pipeline.run(dataset)
        np.testing.assert_allclose(acc.poses[0], np.eye(4), atol=1e-12)

    def test_first_frame_is_skipped_status(self):
        dataset = SyntheticDataset(n_frames=5, seed=2)
        fc = build_feature_config({"name": "ORB", "nfeatures": 200}, {"name": "ORB"})
        pipeline = VOPipeline(fc)
        acc = pipeline.run(dataset)
        assert acc.diagnostics[0].status == FrameStatus.SKIPPED

    def test_all_poses_are_valid_shape(self):
        dataset = SyntheticDataset(n_frames=5, seed=3)
        fc = build_feature_config({"name": "ORB", "nfeatures": 200}, {"name": "ORB"})
        pipeline = VOPipeline(fc)
        acc = pipeline.run(dataset)
        for T in acc.poses:
            assert T.shape == (4, 4)
