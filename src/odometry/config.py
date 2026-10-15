# odometry/config.py -- VO pipeline config helpers

from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineConfig:
    '''''Pipeline hyperparameter bundle loaded from experiment YAML.'''''
    ransac_threshold: float = 1.0
    ransac_confidence: float = 0.999
    ransac_max_iter: int = 2000
    ratio_threshold: float = 0.75
    cross_check: bool = False
    min_keypoints: int = 8
    min_matches: int = 8
    min_inlier_ratio: float = 0.10

    @classmethod
    def from_dict(cls, d: dict) -> 'PipelineConfig':
        tracking = d.get('tracking', {})
        ransac   = d.get('ransac', {})
        matching = d.get('matching', {})
        return cls(
            ransac_threshold=float(ransac.get('threshold', 1.0)),
            ransac_confidence=float(ransac.get('confidence', 0.999)),
            ransac_max_iter=int(ransac.get('max_iterations', 2000)),
            ratio_threshold=float(matching.get('ratio_threshold', 0.75)),
            cross_check=bool(matching.get('cross_check', False)),
            min_keypoints=int(tracking.get('min_keypoints', 8)),
            min_matches=int(tracking.get('min_matches', 8)),
            min_inlier_ratio=float(tracking.get('min_inlier_ratio', 0.10)),
        )

