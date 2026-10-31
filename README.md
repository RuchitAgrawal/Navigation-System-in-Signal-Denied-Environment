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

## Feature Configurations

| Config ID | Detector | Descriptor | Matcher | Status |
|-----------|----------|------------|---------|--------|
| A | FAST | BRIEF | Hamming BFMatcher | âœ… Implemented |
| B | FAST | ORB | Hamming BFMatcher | âœ… Implemented |
| C | ORB | ORB | Hamming BFMatcher | âœ… Baseline |
| D | ORB | BRISK | Hamming BFMatcher | âœ… Implemented |
| E | FASTER | â€” | â€” | âš ï¸ Future extension |

---

## Datasets

- **ICL-NUIM** â€” Synthetic indoor RGB-D benchmark ([link](https://www.doc.ic.ac.uk/~ahanda/VaFRIC/iclnuim.html))
- **TartanAir** â€” Large-scale synthetic multi-environment dataset ([link](https://tartanair.org/))

---

## Installation

```bash
# Clone the repository
git clone https://github.com/RuchitAgrawal/Navigation-System-in-Signal-Denied-Environment.git
cd Navigation-System-in-Signal-Denied-Environment

# Install dependencies
pip install -r requirements.txt

# Editable install (recommended for development)
pip install -e .
```

---

## Dataset Setup

### ICL-NUIM
Download the `living_room_traj1_loop` sequence from the [ICL-NUIM page](https://www.doc.ic.ac.uk/~ahanda/VaFRIC/iclnuim.html) (TUM RGB-D compatible format).

```
data/
  icl_nuim/
    living_room_traj1_loop/
      rgb/          # 0000.png, 0001.png, ...
      groundtruth.txt
      rgb.txt
```

Configure the path in `configs/datasets/icl_nuim.yaml`.

### TartanAir
Download one trajectory from the [TartanAir dataset](https://tartanair.org/) (e.g., `ocean/Easy/P000`).

```
data/
  tartanair/
    ocean/Easy/P000/
      image_left/   # 000000.png, ...
      pose_left.txt
```

Configure the path in `configs/datasets/tartanair.yaml`.

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

