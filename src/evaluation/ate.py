"""
ate.py — Absolute Trajectory Error (ATE) computation.

Implements Sim(3) and SE(3) trajectory alignment using the Umeyama method,
followed by per-frame translation error computation.

Alignment conventions
---------------------
For monocular VO, translation scale is inherently ambiguous. Two alignment
modes are supported:

* ``sim3`` (default): Similarity transform alignment — recovers scale, rotation,
  and translation that minimises ||s*R*p_est + t - p_gt||². This removes the
  global scale difference and is appropriate for comparing trajectory *shape*.
  Report ATE after Sim(3) alignment when evaluating monocular VO.

* ``se3``: Rigid body alignment — scale fixed at 1. Use when scale is known
  (e.g., stereo VO, RGB-D, or after scale anchoring).

The ATE is defined as in:
    Sturm et al. (2012). A benchmark for the evaluation of RGB-D SLAM systems.
    IROS 2012.

Important
---------
- Ground truth poses and estimated poses must be associated before calling
  these functions (same frame indices assumed).
- Scale drift is NOT hidden — it is reported as part of the Sim(3) alignment
  scale factor.
- Never claim monocular ATE in absolute metres without documenting alignment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class ATEResult:
    """Result of ATE computation."""
    alignment: str               # 'sim3' or 'se3'
    scale: float                 # recovered scale (1.0 for se3)
    rmse: float                  # ATE RMSE (metres after alignment)
    mean: float
    median: float
    std: float
    per_frame_errors: np.ndarray  # (N,) per-frame translation errors
    aligned_est_positions: np.ndarray  # (N, 3) aligned estimated positions
    gt_positions: np.ndarray           # (N, 3) ground-truth positions
    n_frames: int


def umeyama_alignment(
    src: np.ndarray,
    dst: np.ndarray,
    with_scale: bool = True,
) -> Tuple[float, np.ndarray, np.ndarray]:
    """Umeyama (1991) similarity / rigid alignment.

    Finds s, R, t minimising:
        sum_i ||s * R * src[i] + t - dst[i]||²

    Parameters
    ----------
    src : (N, 3) float64   Source points (estimated positions).
    dst : (N, 3) float64   Destination points (ground-truth positions).
    with_scale : bool       If True, recover scale (Sim3). If False, s=1 (SE3).

    Returns
    -------
    scale : float
    R     : (3, 3) float64
    t     : (3,) float64

    Reference
    ---------
    Umeyama, S. (1991). Least-squares estimation of transformation parameters
    between two point patterns. IEEE TPAMI 13(4), 376-380.
    """
    assert src.shape == dst.shape, "src and dst must have the same shape"
    assert src.ndim == 2 and src.shape[1] == 3, "expected (N, 3) arrays"

    n = src.shape[0]
    mu_src = src.mean(axis=0)
    mu_dst = dst.mean(axis=0)

    src_c = src - mu_src
    dst_c = dst - mu_dst

    var_src = np.mean(np.sum(src_c ** 2, axis=1))

    H = (src_c.T @ dst_c) / n   # (3, 3)

    U, D, Vt = np.linalg.svd(H)

    # Ensure proper rotation (det = +1)
    d = np.linalg.det(Vt.T @ U.T)
    S = np.diag([1.0, 1.0, np.sign(d)])

    R = Vt.T @ S @ U.T

    if with_scale:
        scale = float(np.sum(D * np.diag(S)) / var_src) if var_src > 0 else 1.0
    else:
        scale = 1.0

    t = mu_dst - scale * R @ mu_src

    return scale, R, t


def compute_ate(
    est_poses: List[np.ndarray],
    gt_poses: List[Optional[np.ndarray]],
    alignment: str = "sim3",
) -> ATEResult:
    """Compute Absolute Trajectory Error (ATE).

    Parameters
    ----------
    est_poses : list of (4, 4) float64   Estimated T_wc poses.
    gt_poses  : list of (4, 4) | None    Ground-truth T_wc poses (None = skip).
    alignment : str   'sim3' or 'se3'.

    Returns
    -------
    ATEResult
    """
    assert len(est_poses) == len(gt_poses), "pose lists must be the same length"

    # Filter out frames without GT
    valid = [(i, est_poses[i], gt_poses[i])
             for i in range(len(est_poses))
             if gt_poses[i] is not None]

    if len(valid) < 3:
        raise ValueError(f"Need at least 3 paired poses for ATE; got {len(valid)}")

    est_pos = np.array([v[1][:3, 3] for v in valid], dtype=np.float64)   # (N, 3)
    gt_pos  = np.array([v[2][:3, 3] for v in valid], dtype=np.float64)   # (N, 3)

    with_scale = (alignment.lower() == "sim3")
    scale, R, t = umeyama_alignment(est_pos, gt_pos, with_scale=with_scale)

    aligned = (scale * (R @ est_pos.T)).T + t   # (N, 3)

    per_frame_err = np.linalg.norm(aligned - gt_pos, axis=1)   # (N,)

    return ATEResult(
        alignment=alignment,
        scale=scale,
        rmse=float(np.sqrt(np.mean(per_frame_err ** 2))),
        mean=float(np.mean(per_frame_err)),
        median=float(np.median(per_frame_err)),
        std=float(np.std(per_frame_err)),
        per_frame_errors=per_frame_err,
        aligned_est_positions=aligned,
        gt_positions=gt_pos,
        n_frames=len(valid),
    )
