# Architecture Overview

This document describes the internal architecture of the visual odometry
pipeline and explains key design decisions.

---

## Module Map

```
minor-project/
│
├── src/
│   ├── datasets/           ← Dataset loaders (ICL-NUIM, TartanAir)
│   │   ├── base_dataset.py ← Abstract interface + CameraIntrinsics
│   │   ├── icl_nuim.py     ← TUM-format parser, timestamp association
│   │   └── tartanair.py    ← NED→camera conversion, frame discovery
│   │
│   ├── features/           ← Feature detection and description
│   │   ├── detector.py     ← FAST, ORB factories; FASTER NotImplemented
│   │   ├── descriptor.py   ← BRIEF (contrib + ManualBRIEF), ORB, BRISK
│   │   └── config.py       ← Combo validation, FeatureConfig dataclass
│   │
│   ├── matching/           ← Descriptor matching
│   │   └── matcher.py      ← Hamming BFMatcher, Lowe ratio test
│   │
│   ├── geometry/           ← SE(3) math and geometric estimation
│   │   ├── transforms.py   ← SE(3) helpers, NED conversion, validators
│   │   ├── pose.py         ← PoseAccumulator, TUM I/O, FrameDiagnostics
│   │   └── essential.py    ← RANSAC Essential matrix + recoverPose
│   │
│   ├── odometry/           ← Main VO loop
│   │   ├── pipeline.py     ← VOPipeline: detect → match → estimate → accumulate
│   │   └── tracker.py      ← TrackingReport, FPS stats
│   │
│   ├── evaluation/         ← Metrics
│   │   ├── ate.py          ← Umeyama Sim(3)/SE(3) alignment + ATE
│   │   ├── rpe.py          ← Relative Pose Error
│   │   └── metrics.py      ← CSV export, summary row builder
│   │
│   └── visualization/      ← Figures and reports
│       ├── trajectory_plot.py  ← 2D/benchmark comparison plots
│       ├── match_plot.py       ← Inlier/outlier match visualization
│       └── report.py           ← Console table, Markdown export
│
├── experiments/
│   ├── runner.py           ← Single experiment orchestrator
│   ├── benchmark.py        ← Multi-config benchmark loop
│   └── gps_outage.py       ← GPS-denied interval simulation
│
├── scripts/                ← CLI entry points
│   ├── run_vo.py
│   ├── run_benchmark.py
│   └── evaluate_trajectory.py
│
├── tests/                  ← Unit tests (pytest)
├── configs/                ← YAML configuration files
└── docs/                   ← Documentation
```

---

## Key Design Decisions

### 1. Coordinate Frame Convention

All poses stored as **T_wc** (camera-to-world 4×4 float64).

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
FAILED_FEATURES → too few keypoints (< min_keypoints)
FAILED_MATCHES  → too few filtered matches (< min_matches)
FAILED_RANSAC   → RANSAC inlier ratio below threshold
FAILED_POSE     → recoverPose returned invalid rotation
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
