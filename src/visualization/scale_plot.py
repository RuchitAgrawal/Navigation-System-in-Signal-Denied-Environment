# visualization/scale_plot.py -- Scale drift visualization
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

\ndef plot_scale_drift(
    scales: np.ndarray,
    config_id: str,
    dataset_name: str,
    save_path,
    window: int = 10,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    frames = np.arange(len(scales))
    finite = np.isfinite(scales)
    ax.plot(frames[finite], scales[finite], color='#0d6efd', linewidth=1.2)
    ax.axhline(1.0, color='black', linestyle='--', linewidth=1.0, label='Scale=1 (no drift)')
    ax.fill_between(frames[finite], scales[finite], 1.0, alpha=0.2, color='#0d6efd')
    ax.set_xlabel('Frame Index'); ax.set_ylabel('Local Scale (est/gt)')
    ax.set_title(f'Scale Drift Over Trajectory -- {config_id.upper()} | {dataset_name}')
    ax.legend(); ax.grid(True, alpha=0.35)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


