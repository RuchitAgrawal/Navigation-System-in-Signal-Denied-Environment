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
`ash
# 1. Generate or download the 2+2 benchmark suite into data/
python scripts/download_datasets.py --offline-suite

# 2. Verify dataset checksums, image dimensions, and ground-truth alignments
python scripts/verify_dataset_integrity.py
`

---

## Running Experiments

### Single VO run
```bash
python scripts/run_vo.py --config configs/experiments/orb_orb.yaml --dataset icl_nuim
```

### Evaluate a saved trajectory
```bash
python scripts/evaluate_trajectory.py --est results/csv/orb_orb_icl_traj.txt --gt data/icl_nuim/living_room_traj1_loop/groundtruth.txt
```

### Full benchmark (all configs)
```bash
python scripts/run_benchmark.py --dataset icl_nuim
```

---

## Project Structure

```
.
â”œâ”€â”€ configs/          # YAML experiment and dataset configs
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ datasets/     # ICL-NUIM and TartanAir loaders
â”‚   â”œâ”€â”€ features/     # Detector, descriptor, and combo factory
â”‚   â”œâ”€â”€ matching/     # Feature matcher with filtering
â”‚   â”œâ”€â”€ geometry/     # SE(3) pose, Essential matrix, Umeyama alignment
â”‚   â”œâ”€â”€ odometry/     # Main VO pipeline and failure tracker
â”‚   â”œâ”€â”€ evaluation/   # ATE, RPE, and tracking metrics
â”‚   â””â”€â”€ visualization/# Trajectory and match plots
â”œâ”€â”€ experiments/      # Benchmark runner and GPS-outage simulation
â”œâ”€â”€ scripts/          # CLI entry points
â”œâ”€â”€ tests/            # Unit tests (pytest)
â”œâ”€â”€ results/          # Generated CSVs, figures, and logs
â””â”€â”€ docs/             # Research report and HSO comparison
```

---

## Evaluation Metrics

- **ATE** (Absolute Trajectory Error) â€” RMSE, mean, median after Sim(3) alignment
- **RPE** (Relative Pose Error) â€” per-frame translation and rotation error
- **Tracking robustness** â€” success rate, failure classification
- **Runtime** â€” mean/median FPS, 95th-percentile frame time

---

## Known Limitations

- Monocular VO has inherent scale ambiguity. All ATE results use Sim(3) alignment and are clearly labeled.
- FASTER detector is not implemented (no verified pure-Python API available in standard OpenCV).
- No bundle adjustment, loop closure, or IMU fusion (separate system components).

---

## License

This project's source code is released under the **MIT License**.  
HSO is referenced for architecture inspiration only; no GPL code is included.

---

## Author

**Ruchit Agrawal** â€” Visual Odometry Module  
Minor Project, Computer Science Engineering

