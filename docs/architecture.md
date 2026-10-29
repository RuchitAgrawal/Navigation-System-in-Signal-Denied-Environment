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
│   │   └── tartanair.py    ← NED-to-camera conversion, frame discovery
│   │
│   ├── features/           ← Feature detection, description, and bucketing
│   │   ├── detector.py     ← FAST, ORB, and adaptive FASTER detector
│   │   ├── descriptor.py   ← BRIEF (contrib + ManualBRIEF), ORB, BRISK
│   │   ├── bucketing.py    ← Recursive Quadtree & Perez-Grau grid bucketer
│   │   ├── subpixel.py     ← Sub-pixel corner coordinate refinement
│   │   └── config.py       ← Combo validation, FeatureConfig dataclass
│   │
│   ├── matching/           ← Descriptor matching
│   │   └── matcher.py      ← Hamming BFMatcher, Lowe ratio test, cross-check
│   │
│   ├── geometry/           ← SE(3) math, epipolar, and PnP estimation
│   │   ├── transforms.py   ← SE(3) helpers, NED conversion, validators
│   │   ├── pose.py         ← PoseAccumulator, TUM I/O, FrameDiagnostics
│   │   ├── essential.py    ← RANSAC Essential matrix + recoverPose
│   │   ├── fundamental.py  ← Fundamental matrix + epipolar filtering
│   │   ├── triangulation.py← Multi-view 3D point triangulation
│   │   └── pnp.py          ← Metric PnP RANSAC & hybrid fallback solver
│   │
│   ├── odometry/           ← Main VO loop & kinematics
│   │   ├── pipeline.py     ← VOPipeline: detect -> bucket -> match -> estimate -> accumulate
│   │   ├── motion_model.py ← Constant-velocity kinematic motion prior & validation
│   │   └── tracker.py      ← TrackingReport, FPS stats
│   │
│   ├── evaluation/         ← Metrics
│   │   ├── ate.py          ← Umeyama Sim(3)/SE(3) alignment + ATE
│   │   ├── rpe.py          ← Relative Pose Error
│   │   ├── drift.py        ← Sliding-window scale drift analysis
│   │   └── metrics.py      ← CSV export, summary row builder
│   │
│   └── visualization/      ← Figures, videos, and reports
│       ├── trajectory_plot.py ← 2D/benchmark comparison plots
│       ├── match_plot.py   ← Inlier/outlier match visualization
│       ├── scale_plot.py   ← Scale drift ratio plot
│       └── report.py       ← Console table, Markdown export
│
├── experiments/
│   ├── runner.py           ← Single experiment orchestrator
│   ├── benchmark.py        ← Multi-config benchmark loop
│   └── gps_outage.py       ← GPS-denied interval simulation
│
├── scripts/                ← CLI entry points
│   ├── run_vo.py
│   ├── run_benchmark.py
│   ├── evaluate_trajectory.py
│   ├── run_demo.py
│   ├── generate_demo_data.py
│   └── generate_trajectory_video.py
│
├── tests/                  ← Unit tests (pytest)
├── configs/                ← YAML configuration files
└── docs/                   ← Documentation & research report
```

---

## Design Principles

1. **Separation of Concerns:** Feature extraction, matching, and geometry are decoupled.
2. **Graceful Degradation:** Tracking failures never throw unhandled exceptions; previous poses are carried forward with clear diagnostics.
3. **Reproducibility:** All experiments are driven by version-controlled YAML configuration files.
4. **Metric Integrity:** Ground truth is strictly segregated from state estimation and used exclusively during evaluation.
