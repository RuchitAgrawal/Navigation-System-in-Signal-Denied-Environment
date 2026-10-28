# experiments/scale_analysis.py -- Scale drift analysis experiment
'''''Analyse how monocular VO scale drifts over the trajectory length.'''''
from __future__ import annotations
from pathlib import Path
import numpy as np

def run_scale_analysis(
    accumulator,
    gt_poses,
    window: int = 10,
    output_root: str = 'results',
    config_id: str = 'unknown',
    dataset_name: str = 'unknown',
) -> dict:
    from src.evaluation.drift import compute_scale_over_time
    scales = compute_scale_over_time(accumulator.poses, gt_poses, window=window)
    finite = scales[np.isfinite(scales)]
    output = {
        'config_id': config_id,
        'dataset': dataset_name,
        'window': window,
        'mean_local_scale': float(np.mean(finite)) if len(finite) > 0 else None,
        'std_local_scale': float(np.std(finite)) if len(finite) > 0 else None,
        'max_local_scale': float(np.max(finite)) if len(finite) > 0 else None,
        'min_local_scale': float(np.min(finite)) if len(finite) > 0 else None,
    }
    return output

