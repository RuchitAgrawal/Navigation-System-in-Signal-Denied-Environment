# Navigation System in Signal-Denied Environments
## Visual Odometry Module

**Full Title:** A Computer Vision-Assisted GPS Navigation System for Robust Positioning in Signal-Denied Environments

---

## Overview

This repository contains the **Visual Odometry (VO)** module of a larger GPS-denied navigation system. The module estimates camera motion from consecutive monocular images using classical feature-based methods and evaluates the resulting trajectory against ground truth.

The system is designed so its output can eventually be integrated with a GPS navigation or sensor-fusion (EKF) component.

**Research Question:**
> How do lightweight feature detection, description, and matching strategies affect the trajectory accuracy, tracking robustness, and computational efficiency of classical visual odometry across synthetic indoor and outdoor environments?

---

## Architecture Reference

This implementation is architecturally inspired by [HSO (Hybrid Sparse Visual Odometry)](https://github.com/luodongting/HSO) by Luodongting — a C++ implementation of hybrid sparse VO. We adopt its modular component separation philosophy but implement an independent Python pipeline using OpenCV and NumPy. No HSO source code has been copied. HSO is licensed under GPL-3.0.

---

## Feature Configurations

| Config ID | Detector | Descriptor | Matcher | Status |
|-----------|----------|------------|---------|--------|
| A | FAST | BRIEF | Hamming BFMatcher | ✅ Implemented |
| B | FAST | ORB | Hamming BFMatcher | ✅ Implemented |
| C | ORB | ORB | Hamming BFMatcher | ✅ Baseline |
| D | ORB | BRISK | Hamming BFMatcher | ✅ Implemented |
| E | FASTER | — | — | ⚠️ Future extension |

---

## Datasets

- **ICL-NUIM** — Synthetic indoor RGB-D benchmark ([link](https://www.doc.ic.ac.uk/~ahanda/VaFRIC/iclnuim.html))
- **TartanAir** — Large-scale synthetic multi-environment dataset ([link](https://tartanair.org/))

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
├── configs/          # YAML experiment and dataset configs
├── src/
│   ├── datasets/     # ICL-NUIM and TartanAir loaders
│   ├── features/     # Detector, descriptor, and combo factory
│   ├── matching/     # Feature matcher with filtering
│   ├── geometry/     # SE(3) pose, Essential matrix, Umeyama alignment
│   ├── odometry/     # Main VO pipeline and failure tracker
│   ├── evaluation/   # ATE, RPE, and tracking metrics
│   └── visualization/# Trajectory and match plots
├── experiments/      # Benchmark runner and GPS-outage simulation
├── scripts/          # CLI entry points
├── tests/            # Unit tests (pytest)
├── results/          # Generated CSVs, figures, and logs
└── docs/             # Research report and HSO comparison
```

---

## Evaluation Metrics

- **ATE** (Absolute Trajectory Error) — RMSE, mean, median after Sim(3) alignment
- **RPE** (Relative Pose Error) — per-frame translation and rotation error
- **Tracking robustness** — success rate, failure classification
- **Runtime** — mean/median FPS, 95th-percentile frame time

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

**Ruchit Agrawal** — Visual Odometry Module  
Minor Project, Computer Science Engineering
