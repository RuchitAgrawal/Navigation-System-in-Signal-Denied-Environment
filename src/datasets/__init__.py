"""
src/datasets/__init__.py â€” Public API for the datasets module.
"""
from src.datasets.base_dataset import BaseDataset, CameraIntrinsics, DatasetFrame
from src.datasets.icl_nuim import ICLNUIMDataset, load_icl_nuim_from_config
from src.datasets.tartanair import TartanAirDataset, load_tartanair_from_config


def load_dataset(dataset_cfg: dict):
    """Load a dataset from a config dict. Dispatches on ``dataset_cfg['dataset']``."""
    name = dataset_cfg.get("dataset", "")
    if name == "icl_nuim":
        return load_icl_nuim_from_config(dataset_cfg)
    elif name == "tartanair":
        return load_tartanair_from_config(dataset_cfg)
    else:
        raise ValueError(f"Unknown dataset type: '{name}'. Supported: icl_nuim, tartanair")


__all__ = [
    "BaseDataset", "CameraIntrinsics", "DatasetFrame",
    "ICLNUIMDataset", "load_icl_nuim_from_config",
    "TartanAirDataset", "load_tartanair_from_config",
    "load_dataset",
]


