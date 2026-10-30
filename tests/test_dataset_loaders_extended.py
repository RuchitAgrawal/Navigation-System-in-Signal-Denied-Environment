"""
tests/test_dataset_loaders_extended.py — Integration tests for 2+2 multi-environment dataset loaders.
"""

from pathlib import Path
import pytest
from experiments.runner import load_yaml
from src.datasets.icl_nuim import load_icl_nuim_from_config
from src.datasets.tartanair import load_tartanair_from_config


class TestMultiEnvironmentLoaders:
    def test_icl_nuim_office_loads(self):
        cfg_path = Path("configs/datasets/icl_nuim_office.yaml")
        cfg = load_yaml(cfg_path)
        ds = load_icl_nuim_from_config(cfg)
        assert len(ds) > 0
        assert ds.name == "icl_nuim"
        assert ds.sequence == "office_room_traj0_loop"
        assert ds.camera.width == 640
        assert ds.camera.height == 480

    def test_tartanair_abandonedfactory_loads(self):
        cfg_path = Path("configs/datasets/tartanair_abandonedfactory.yaml")
        cfg = load_yaml(cfg_path)
        ds = load_tartanair_from_config(cfg)
        assert len(ds) > 0
        assert ds.name == "tartanair"
        assert "abandonedfactory" in ds.sequence
        assert ds.camera.width == 640
        assert ds.camera.height == 480
