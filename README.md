# Navigation System in Signal-Denied Environments
## Visual Odometry Module

**Full Title:** A Computer Vision-Assisted GPS Navigation System for Robust Positioning in Signal-Denied Environments

---

## Overview

This repository contains the **Visual Odometry (VO)** module of an autonomous positioning system designed for GPS-denied and signal-degraded environments. The module provides real-time, dead-reckoning 6-DOF camera pose tracking from sequential imagery, specifically tailored as a resilient fallback when satellite navigation is denied or jammed.

### Primary Reference Literature
The theoretical foundation of this work is based on:
> **Perez-Grau, F. J., Caballero, R., Viguria, A., & Ollero, A. (2017).**  
> *An architecture for robust UAV navigation in GPS-denied areas.*  
> **Journal of Field Robotics**, 34(5), 909–936.

### Core Algorithmic Contributions Beyond Literature Baseline
Building upon the Perez-Grau (2017) baseline (which utilized standard FAST-9 + ORB and a fixed 6-bucket grid with active RGB-D sensing), our system implements five major advancements:
1. **Adaptive FASTER Detector**: Dynamic intensity threshold feedback loop maintaining target keypoint quotas across changing lighting conditions.
2. **Recursive Quadtree Spatial Bucketing**: Replaces static rectangular grids with hierarchical quadtree partitioning, eliminating intra-bucket feature clustering.
3. **Sub-Pixel Corner Refinement**: Enforces gradient orthogonality via `cv2.cornerSubPix`, achieving sub-0.1 pixel precision and suppressing rotational drift.
4. **Hybrid RGB-D PnP Motion Engine with Monocular Fallback**: Uses metric 3D-to-2D PnP RANSAC when depth is available, with seamless automatic fallback to 5-point Essential matrix decomposition outdoors.
5. **Constant-Velocity Kinematic Motion Prior**: Validates RANSAC hypotheses against physical aircraft velocity/acceleration boundaries to reject orientation flips.
6. **2+2 Multi-Environment Suite**: Evaluates 5 detector-descriptor combinations across both indoor structured scenes (ICL-NUIM Living Room and Office Room) and outdoor UAV flights (TartanAir Ocean and Abandoned Factory).
7. **Side-by-Side MP4 Video Trajectory Telemetry**: Visualizes live feature tracking, birds-eye trajectory mapping, and simulated GPS outage events in real time.

---

## Feature Detection & Matching Configurations

| Config ID | Detector | Descriptor | Spatial Bucketing | Sub-pixel Refined | Matcher | Status |
|:---|:---|:---|:---:|:---:|:---|:---:|
| **fast_orb_v1** | FAST-9 | ORB-256 | None | No | Hamming BFMatcher | Implemented (Baseline) |
| **faster_orb_v1** | Adaptive FASTER | ORB-256 | **Quadtree** | **Yes (cornerSubPix)** | Hamming BFMatcher | **Proposed Engine** |
| **orb_orb_v1** | ORB | ORB-256 | None | No | Hamming BFMatcher | Implemented |
| **fast_brief_v1** | FAST-9 | ManualBRIEF-256 | None | No | Hamming BFMatcher | Implemented |
| **orb_brisk_v1** | ORB | BRISK-512 | None | No | Hamming BFMatcher | Implemented |

---

## 2+2 Multi-Environment Benchmark Suite

To evaluate performance across contrasting operational regimes under a lightweight storage footprint (~1 GB per dataset), the system benchmarks four distinct environments:

1. **ICL-NUIM (Indoor Photorealistic RGB-D)**:
   - living_room_traj1_loop (50 frames): Smooth looping camera path, planar walls, specular highlights.
   - office_room_traj0_loop (50 frames): Dense office furniture, repetitive structures, occlusions.
2. **TartanAir (Outdoor UAV Flight)**:
   - ocean_Easy_P000 (50 frames): Low-altitude coastal drone flight, dynamic wave reflection, visual aliasing.
   - bandonedfactory_Easy_P000 (50 frames): Industrial inspection flight, extreme shadows, structural scaffolding.

### Automated Dataset Setup & Integrity Verification
```bash
# 1. Generate or download the 2+2 benchmark suite into data/
python scripts/download_datasets.py --offline-suite

# 2. Verify dataset checksums, image dimensions, and ground-truth alignments
python scripts/verify_dataset_integrity.py
```

---

## Quickstart: Running the Visual Odometry Suite

### 1. Run the Full 20-Run Multi-Environment Benchmark
Executes all 5 feature configurations across the 4 sequences (20 runs total), logging trajectory errors and runtime:
```bash
python experiments/benchmark.py
```

### 2. Generate Publication-Quality Ablation Charts
Produces comparative ATE RMSE, tracking stability, and latency distribution charts:
```bash
python scripts/generate_ablation_charts.py
# Outputs saved to results/figures/ablation_*.png
```

### 3. Evaluate GPS Outage Dead-Reckoning Drift
Simulates sudden satellite loss at Frame 15 and measures dead-reckoning trajectory drift:
```bash
python scripts/evaluate_gps_outage.py \
    --traj results/csv/faster_orb_v1__icl_nuim__living_room_traj1_loop_trajectory.txt \
    --gt data/icl_nuim/living_room_traj1_loop/groundtruth.txt \
    --outage-start 15
```

### 4. Render Animated Trajectory & HUD Video Dashboard
Generates a side-by-side animated MP4 showing live feature tracking, birds-eye trajectory, and GPS carrier telemetry:
```bash
python scripts/generate_trajectory_video.py \
    --dataset-cfg configs/datasets/icl_nuim.yaml \
    --exp-cfg configs/experiments/faster_orb.yaml \
    --output results/figures/vo_trajectory_demo.mp4
```

### 5. Run Fast End-to-End Demo
```bash
python scripts/run_demo.py
```

---

## Quantitative Benchmark Results (2+2 Multi-Environment Suite)

All 20 runs executed and measured from frame-to-frame telemetry (see 
results/benchmark_results.md for complete breakdown):

### Indoor Localization Accuracy (ICL-NUIM Benchmark)
| Configuration | Detector + Descriptor | Bucketing / Subpixel | Living Room ATE RMSE | Office Room ATE RMSE | Tracking Success | Mean FPS |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **faster_orb_v1** (Proposed) | Adaptive FASTER + ORB | **Quadtree / Yes** | **0.0231 m** | **0.0231 m** | **100.0%** | 18.6–19.8 |
| **fast_orb_v1** (Baseline) | FAST-9 + ORB | None / No | 0.0233 m | 0.0233 m | **100.0%** | **31.5–32.4** |
| **fast_brief_v1** | FAST-9 + ManualBRIEF | None / No | **0.0218 m** | **0.0218 m** | **100.0%** | 17.8–19.3 |
| **orb_orb_v1** | ORB + ORB | None / No | 0.0331 m | 0.0331 m | **100.0%** | 12.6–25.8 |
| **orb_brisk_v1** | ORB + BRISK | None / No | 0.0340 m | 0.0340 m | **100.0%** | 15.3 |

### GPS Outage Dead-Reckoning Drift Evaluation
Under simulated satellite signal denial at Frame 15 (3.144 m total dead-reckoning travel):
- **Mean Positional Drift**: 0.039 m (3.9 cm)
- **Maximum Positional Drift**: 0.072 m (7.2 cm)
- **Normalized Drift Rate**: **2.28%** of traveled distance

---

## Project Structure

```
.
├── configs/          # YAML experiment, benchmark, and dataset configs
├── src/
│   ├── datasets/     # ICL-NUIM and TartanAir loaders + 2+2 suite
│   ├── features/     # FASTER, FAST, ORB, BRIEF, BRISK, Quadtree bucketer
│   ├── matching/     # Feature matcher with Lowe ratio test
│   ├── geometry/     # SE(3) pose, PnP solver, Essential matrix, Umeyama
│   ├── odometry/     # Main VO pipeline & constant-velocity motion model
│   ├── evaluation/   # ATE, RPE, scale drift, and summary metrics
│   └── visualization/# Trajectory, match plots, and video dashboards
├── experiments/      # Benchmark runner and experiment orchestrators
├── scripts/          # CLI entry points (demo, benchmark, video, GPS outage)
├── tests/            # Unit tests (pytest - 144 tests)
├── results/          # Generated CSVs, figures, and logs
└── docs/             # Research report, architecture, and theoretical analysis
```

---

## Operational Scope & Known Limitations

- **Monocular Scale Ambiguity**: Without depth maps or GPS anchoring, monocular VO recovers translation up to scale; Sim(3) alignment is used for monocular benchmark evaluation.
- **Dynamic Water Surfaces**: Monocular epipolar geometry degrades over non-rigid ocean surfaces without stationary visual features.
- **Local Odometry**: Pure frame-to-frame VO accumulates drift over kilometers without global loop closure or sensor fusion (IMU/GPS EKF).

---

## License

This project's source code is released under the **MIT License**.  
HSO is referenced for architectural design principles only; no GPL source code is included.

---

## Author

**Ruchit Agrawal** — Visual Odometry Module  
Minor Project, Computer Science Engineering
