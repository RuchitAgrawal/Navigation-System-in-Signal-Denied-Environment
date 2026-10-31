# Evaluation Metrics Reference

This document defines all evaluation metrics used in the benchmark and explains
how to interpret the results correctly.

---

## 1. Absolute Trajectory Error (ATE)

### Definition

ATE measures the global consistency of the estimated trajectory against ground truth.

For each frame $i$ with valid ground-truth $T_{\mathrm{gt}}[i]$ and estimated $T_{\mathrm{est}}[i]$:
1. Align the estimated trajectory to the ground truth using the **Umeyama (1991) method**.
2. Compute the per-frame translation error: $\|p_{\mathrm{aligned}}[i] - p_{\mathrm{gt}}[i]\|_2$.

### Alignment Modes

| Mode | Scale | When to Use |
|------|-------|-------------|
| `sim3` | Recovered ($s \ne 1$) | **Monocular VO** — removes scale ambiguity |
| `se3`  | Fixed ($s = 1$)       | Stereo, RGB-D (PnP), or after explicit GPS scale anchoring |

> **Important:** Monocular VO ATE must use Sim(3) alignment. Reporting SE(3) ATE
> for monocular VO without explicit scale anchoring is methodologically incorrect.
> This pipeline always reports the alignment mode and scale factor.

### Reported Metrics

| Metric | Symbol | Meaning |
|--------|--------|---------|
| `ate_rmse_m` | RMSE | Primary accuracy metric (metres after alignment) |
| `ate_mean_m` | $\mu$ | Mean per-frame error |
| `ate_median_m` | median | Robust to outlier frames |
| `ate_std_m` | $\sigma$ | Spread of per-frame errors |
| `ate_scale` | $s$ | Recovered scale factor ($s=1$ means no scale difference) |
| `ate_n_frames` | $N$ | Number of frames used (frames with valid GT) |

### Reference

Sturm, J., et al. (2012). A benchmark for the evaluation of RGB-D SLAM systems.
IROS 2012. https://vision.in.tum.de/data/datasets/rgbd-dataset/tools

---

## 2. Relative Pose Error (RPE)

### Definition

RPE measures **local drift** over a fixed frame interval `delta`. Unlike ATE,
RPE does not require global alignment and is not affected by the scale factor.

For each valid pair (i, i+delta):
```
Q_est = inv(T_est[i]) @ T_est[i+delta]   # relative estimated motion
Q_gt  = inv(T_gt[i])  @ T_gt[i+delta]    # relative GT motion
E_i   = inv(Q_est) @ Q_gt                # error transform
```

Translation error: $\|E_i[:3, 3]\|_2$  
Rotation error: $\arccos((\mathrm{trace}(E_i[:3,:3]) - 1) / 2)$ (degrees)

### Reported Metrics

| Metric | Symbol | Meaning |
|--------|--------|---------|
| `rpe_trans_rmse_m` | $\mathrm{RMSE}_t$ | Translation drift RMSE |
| `rpe_trans_mean_m` | $\mu_t$ | Mean translation drift |
| `rpe_rot_rmse_deg` | $\mathrm{RMSE}_r$ | Rotation drift RMSE (degrees) |
| `rpe_delta_frames` | $\delta$ | Frame interval used (default: 1) |
| `rpe_n_pairs` | $N$ | Number of valid $(i, i+\delta)$ pairs |

---

## 3. Tracking Success Rate

Percentage of processable frames (excluding frame 0) where the pipeline successfully estimated a relative pose.

```
success_rate = success_frames / (total_frames - skipped_frames)
```

A run is flagged as **degenerate** if `success_rate < 50%`.

### Failure Categories

| Category | Code | Cause |
|----------|------|-------|
| FAILED_FEATURES | `FFEAT` | < min_keypoints detected |
| FAILED_MATCHES | `FMATCH` | < min_matches after ratio filter |
| FAILED_RANSAC | `FRANSAC` | RANSAC inlier ratio < threshold |
| FAILED_POSE | `FPOSE` | recoverPose returned invalid rotation |

---

## 4. Runtime Metrics

| Metric | Meaning |
|--------|---------|
| `mean_fps` | Mean frames per second across all processable frames |
| `median_fps` | Median FPS (more robust to outlier frames) |
| `mean_frame_time_ms` | Mean total processing time per frame |
| `p95_frame_time_ms` | 95th percentile frame time (worst-case performance) |

---

## 5. Scale Factor Interpretation

For monocular VO after Sim(3) alignment:

- `ate_scale ≈ 1.0` → estimated and GT trajectories have the same scale.
- `ate_scale < 1.0` → estimated trajectory is compressed relative to GT.
- `ate_scale > 1.0` → estimated trajectory is expanded relative to GT.

Large scale drift ($|s - 1| > 0.5$) usually indicates significant scale drift accumulation or poor initialization.

---

## 6. GPS Outage Dead-Reckoning Metrics

Simulates satellite navigation loss starting at frame $T_{\mathrm{outage}}$:

| Metric | Definition | Unit |
|:---|:---|:---:|
| `total_distance_m` | Cumulative ground-truth distance traveled in outage window | m |
| `mean_drift_m` | Mean Euclidean offset from ground-truth during outage | m |
| `max_drift_m` | Maximum Euclidean drift observed during outage window | m |
| `final_drift_m` | Terminal Euclidean drift at the end of the outage | m |
| `drift_pct` | Terminal drift normalized by traveled distance: $(d_{\mathrm{final}} / D_{\mathrm{total}}) \times 100$ | % |

