# Architecture Overview

This document describes the internal architecture of the visual odometry
pipeline and explains key design decisions.

---

## Module Map

```
minor-project/
â”‚
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ datasets/           â† Dataset loaders (ICL-NUIM, TartanAir)
â”‚   â”‚   â”œâ”€â”€ base_dataset.py â† Abstract interface + CameraIntrinsics
â”‚   â”‚   â”œâ”€â”€ icl_nuim.py     â† TUM-format parser, timestamp association
â”‚   â”‚   â””â”€â”€ tartanair.py    â† NEDâ†’camera conversion, frame discovery
â”‚   â”‚
â”‚   â”œâ”€â”€ features/           â† Feature detection and description
â”‚   â”‚   â”œâ”€â”€ detector.py     â† FAST, ORB factories; FASTER NotImplemented
â”‚   â”‚   â”œâ”€â”€ descriptor.py   â† BRIEF (contrib + ManualBRIEF), ORB, BRISK
â”‚   â”‚   â””â”€â”€ config.py       â† Combo validation, FeatureConfig dataclass
â”‚   â”‚
â”‚   â”œâ”€â”€ matching/           â† Descriptor matching
â”‚   â”‚   â””â”€â”€ matcher.py      â† Hamming BFMatcher, Lowe ratio test
â”‚   â”‚
â”‚   â”œâ”€â”€ geometry/           â† SE(3) math and geometric estimation
â”‚   â”‚   â”œâ”€â”€ transforms.py   â† SE(3) helpers, NED conversion, validators
â”‚   â”‚   â”œâ”€â”€ pose.py         â† PoseAccumulator, TUM I/O, FrameDiagnostics
â”‚   â”‚   â””â”€â”€ essential.py    â† RANSAC Essential matrix + recoverPose
â”‚   â”‚
â”‚   â”œâ”€â”€ odometry/           â† Main VO loop
â”‚   â”‚   â”œâ”€â”€ pipeline.py     â† VOPipeline: detect â†’ match â†’ estimate â†’ accumulate
â”‚   â”‚   â””â”€â”€ tracker.py      â† TrackingReport, FPS stats
â”‚   â”‚
â”‚   â”œâ”€â”€ evaluation/         â† Metrics
â”‚   â”‚   â”œâ”€â”€ ate.py          â† Umeyama Sim(3)/SE(3) alignment + ATE
â”‚   â”‚   â”œâ”€â”€ rpe.py          â† Relative Pose Error
â”‚   â”‚   â””â”€â”€ metrics.py      â† CSV export, summary row builder
â”‚   â”‚
â”‚   â””â”€â”€ visualization/      â† Figures and reports
â”‚       â”œâ”€â”€ trajectory_plot.py  â† 2D/benchmark comparison plots
â”‚       â”œâ”€â”€ match_plot.py       â† Inlier/outlier match visualization
â”‚       â””â”€â”€ report.py           â† Console table, Markdown export
â”‚
â”œâ”€â”€ experiments/
â”‚   â”œâ”€â”€ runner.py           â† Single experiment orchestrator
â”‚   â”œâ”€â”€ benchmark.py        â† Multi-config benchmark loop
â”‚   â””â”€â”€ gps_outage.py       â† GPS-denied interval simulation
â”‚
â”œâ”€â”€ scripts/                â† CLI entry points
â”‚   â”œâ”€â”€ run_vo.py
â”‚   â”œâ”€â”€ run_benchmark.py
â”‚   â””â”€â”€ evaluate_trajectory.py
â”‚
â”œâ”€â”€ tests/                  â† Unit tests (pytest)
â”œâ”€â”€ configs/                â† YAML configuration files
â””â”€â”€ docs/                   â† Documentation
```

---

## Key Design Decisions

### 1. Coordinate Frame Convention

All poses stored as **T_wc** (camera-to-world 4Ã—4 float64).

**Why T_wc instead of T_cw?**
Ground-truth files (TUM, TartanAir) provide camera-in-world positions.
T_wc lets us directly read `T[:3, 3]` as the camera's world-frame position,
which is the natural interpretation for trajectory plots.

### 2. Scale Ambiguity Handling

Monocular VO has no metric scale. We:
- Store unit-norm translation directions from `recoverPose`.
- Use **Sim(3) alignment (Umeyama 1991)** for ATE, not SE(3).
- Report the recovered scale factor in all result tables.
- Clearly document this in every output file.

### 3. Failure Handling

Every frame is processed unconditionally. Failures are classified:
```
FAILED_FEATURES â†’ too few keypoints (< min_keypoints)
FAILED_MATCHES  â†’ too few filtered matches (< min_matches)
FAILED_RANSAC   â†’ RANSAC inlier ratio below threshold
FAILED_POSE     â†’ recoverPose returned invalid rotation
```
On any failure, the **previous pose is carried forward** (no extrapolation).
This is logged as a diagnostic, not silently ignored.

### 4. ManualBRIEF Fallback

`opencv-contrib-python` is not universally available. Rather than crashing
or silently substituting ORB, we implement a genuine BRIEF (Calonder et al., 2010)
using Gaussian-sampled binary test pairs. This is:
- Clearly not rotation-invariant by design.
- Labeled as `ManualBRIEF-Gaussian-256` in all result tables.
- Never presented as equivalent to the contrib implementation.

### 5. Configuration via YAML

All hyperparameters live in YAML files (not hardcoded). This allows:
- Reproducing any experiment by sharing one YAML file.
- Running benchmarks without code changes.
- Peer review of experimental setup without reading Python.

### 6. No Ground Truth During Estimation

Ground truth is **only** used post-run for evaluation. The VO pipeline
reads only images and camera intrinsics. This ensures the results reflect
genuine VO estimation, not GT-guided pose refinement.

