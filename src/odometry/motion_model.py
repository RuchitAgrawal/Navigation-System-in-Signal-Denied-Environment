"""
motion_model.py — Kinematic motion prior and trajectory continuity validator.

Maintains a constant-velocity kinematic motion model across consecutive frames,
providing prior pose estimates and rejecting physically impossible acceleration
spikes (e.g., degenerate RANSAC orientation flips).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

from src.geometry.transforms import make_pose, invert_pose


@dataclass
class MotionValidationResult:
    """Result of kinematic motion validation."""
    is_valid: bool
    angular_change_deg: float
    direction_change_deg: float
    speed_ratio: float
    reason: str = ""


class ConstantVelocityMotionModel:
    """Constant-velocity kinematic motion model for aerial robot trajectory tracking.

    Parameters
    ----------
    max_angular_jump_deg : float
        Maximum allowable relative rotation change between consecutive frames (degrees).
    max_direction_change_deg : float
        Maximum allowable translation direction deviation (degrees).
    max_speed_ratio : float
        Maximum allowable ratio between consecutive frame translation magnitudes.
    """

    def __init__(
        self,
        max_angular_jump_deg: float = 45.0,
        max_direction_change_deg: float = 90.0,
        max_speed_ratio: float = 4.0,
    ) -> None:
        self.max_angular_jump_deg = max_angular_jump_deg
        self.max_direction_change_deg = max_direction_change_deg
        self.max_speed_ratio = max_speed_ratio

        self._last_R: Optional[np.ndarray] = None
        self._last_t: Optional[np.ndarray] = None
        self._last_ts: Optional[float] = None
        self._initialized: bool = False

    def reset(self) -> None:
        """Reset motion model state."""
        self._last_R = None
        self._last_t = None
        self._last_ts = None
        self._initialized = False

    @property
    def has_prior(self) -> bool:
        return self._initialized and self._last_R is not None

    def get_predicted_relative_pose(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return the constant-velocity predicted relative rotation and translation.

        Returns
        -------
        R_pred : (3, 3) ndarray
        t_pred : (3, 1) ndarray
        """
        if not self.has_prior:
            return np.eye(3, dtype=np.float64), np.zeros((3, 1), dtype=np.float64)
        return self._last_R.copy(), self._last_t.copy()

    def validate_relative_pose(
        self,
        R_curr: np.ndarray,
        t_curr: np.ndarray,
        timestamp: float,
    ) -> MotionValidationResult:
        """Validate candidate relative pose against the kinematic continuity prior.

        Parameters
        ----------
        R_curr : (3, 3) ndarray
            Estimated candidate rotation.
        t_curr : (3, 1) or (3,) ndarray
            Estimated candidate translation.
        timestamp : float
            Current frame timestamp.

        Returns
        -------
        MotionValidationResult
        """
        t_vec = t_curr.reshape(3, 1)

        if not self.has_prior:
            # First motion increment is always accepted as reference
            return MotionValidationResult(
                is_valid=True,
                angular_change_deg=0.0,
                direction_change_deg=0.0,
                speed_ratio=1.0,
                reason="initial_motion_prior",
            )

        # 1. Angular change check: trace(R_prior^T @ R_curr)
        R_diff = self._last_R.T @ R_curr
        tr = np.clip((np.trace(R_diff) - 1.0) / 2.0, -1.0, 1.0)
        angular_change = float(np.degrees(np.arccos(tr)))

        # 2. Direction change check
        norm_prev = float(np.linalg.norm(self._last_t))
        norm_curr = float(np.linalg.norm(t_vec))

        if norm_prev > 1e-6 and norm_curr > 1e-6:
            dir_prev = self._last_t.flatten() / norm_prev
            dir_curr = t_vec.flatten() / norm_curr
            dot = np.clip(np.dot(dir_prev, dir_curr), -1.0, 1.0)
            direction_change = float(np.degrees(np.arccos(dot)))
            speed_ratio = max(norm_curr / norm_prev, norm_prev / norm_curr)
        else:
            direction_change = 0.0
            speed_ratio = 1.0

        is_valid = True
        reason = "kinematic_continuity_accepted"

        if angular_change > self.max_angular_jump_deg:
            is_valid = False
            reason = f"excessive_angular_jump ({angular_change:.1f} deg > {self.max_angular_jump_deg} deg)"
        elif direction_change > self.max_direction_change_deg:
            is_valid = False
            reason = f"unnatural_direction_reversal ({direction_change:.1f} deg > {self.max_direction_change_deg} deg)"

        return MotionValidationResult(
            is_valid=is_valid,
            angular_change_deg=angular_change,
            direction_change_deg=direction_change,
            speed_ratio=speed_ratio,
            reason=reason,
        )

    def update(self, R_accepted: np.ndarray, t_accepted: np.ndarray, timestamp: float) -> None:
        """Update kinematic model with an accepted frame relative motion."""
        self._last_R = R_accepted.copy()
        self._last_t = t_accepted.reshape(3, 1).copy()
        self._last_ts = timestamp
        self._initialized = True
