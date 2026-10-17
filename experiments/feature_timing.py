# experiments/feature_timing.py -- Feature extraction timing benchmark
'''''Measure per-config detection and description time on synthetic images.'''''
from __future__ import annotations
import time
import numpy as np
from src.features.config import build_feature_config
from src.features.extractor import FeatureExtractor

CONFIGS = [
    ({'name': 'ORB', 'nfeatures': 2000}, {'name': 'ORB'}),
    ({'name': 'FAST', 'threshold': 20, 'max_keypoints': 2000}, {'name': 'ORB'}),
    ({'name': 'ORB', 'nfeatures': 2000}, {'name': 'BRISK'}),
]

N_REPEAT = 50
\n\ndef benchmark_extraction(h=480, w=640, seed=0):
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 255, (h, w), dtype=np.uint8)
    print(f'\\nFeature Extraction Timing Benchmark ({N_REPEAT} reps, {h}x{w})')
    print('-' * 60)
    for det_cfg, desc_cfg in CONFIGS:
        fc = build_feature_config(det_cfg, desc_cfg)
        ex = FeatureExtractor(fc)
        times = []
        for _ in range(N_REPEAT):
            t0 = time.perf_counter()
            result = ex.extract(img)
            times.append((time.perf_counter() - t0) * 1000)
        mean_ms = np.mean(times)
        print(f'  {fc.config_id:<15s} {result.n_keypoints:>5d} kps  {mean_ms:.2f} ms/frame  {1000/mean_ms:.1f} fps')
    print('-' * 60)
\n\nif __name__ == '__main__':
    benchmark_extraction()

