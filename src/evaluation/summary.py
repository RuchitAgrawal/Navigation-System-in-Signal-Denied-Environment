"""
src/evaluation/summary.py — Aggregate summary statistics across multiple runs.

Provides utilities for comparing benchmark results across configurations
and datasets, identifying the best-performing configuration per metric.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np


def find_best_config(
    rows: List[Dict[str, Any]],
    metric: str = "ate_rmse_m",
    lower_is_better: bool = True,
) -> Optional[Dict[str, Any]]:
    """Find the best-performing row for a given metric.

    Parameters
    ----------
    rows            : list of summary dicts from run_experiment.
    metric          : key to compare (e.g. 'ate_rmse_m', 'mean_fps').
    lower_is_better : if True, smaller metric value is better.

    Returns
    -------
    The row dict with the best metric value, or None if rows is empty.
    """
    valid = [r for r in rows if r.get(metric) is not None]
    if not valid:
        return None
    return min(valid, key=lambda r: r[metric]) if lower_is_better \
        else max(valid, key=lambda r: r[metric])


def compute_aggregate_stats(
    rows: List[Dict[str, Any]],
    metric: str,
) -> Dict[str, float]:
    """Compute mean, std, min, max for a metric across all rows.

    Parameters
    ----------
    rows   : list of summary dicts.
    metric : numeric key to aggregate.

    Returns
    -------
    dict with keys: mean, std, min, max, n_valid.
    """
    values = [float(r[metric]) for r in rows
              if r.get(metric) is not None and np.isfinite(float(r[metric]))]
    if not values:
        return {"mean": None, "std": None, "min": None, "max": None, "n_valid": 0}
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "n_valid": len(values),
    }


def rank_configs(
    rows: List[Dict[str, Any]],
    metric: str = "ate_rmse_m",
    lower_is_better: bool = True,
    group_by: str = "config_id",
) -> List[Dict[str, Any]]:
    """Rank configurations by a metric, averaged across datasets.

    Parameters
    ----------
    rows            : list of summary dicts.
    metric          : key to rank by.
    lower_is_better : ranking direction.
    group_by        : field to group by before averaging (default: config_id).

    Returns
    -------
    List of dicts with fields: config_id, mean_metric, rank.
    """
    groups: Dict[str, List[float]] = {}
    for row in rows:
        key = row.get(group_by, "unknown")
        val = row.get(metric)
        if val is not None and np.isfinite(float(val)):
            groups.setdefault(key, []).append(float(val))

    ranked = [
        {group_by: k, f"mean_{metric}": float(np.mean(v)), "n_datasets": len(v)}
        for k, v in groups.items()
    ]
    ranked.sort(key=lambda r: r[f"mean_{metric}"], reverse=not lower_is_better)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
    return ranked
