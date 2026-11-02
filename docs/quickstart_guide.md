# Visual Odometry Quickstart & Reproduction Guide

This guide walks through reproducing all experimental benchmarks, video dashboards, and ablation figures in this repository.

---

## 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/RuchitAgrawal/Navigation-System-in-Signal-Denied-Environment.git
cd Navigation-System-in-Signal-Denied-Environment

# Install dependencies in editable mode
pip install -r requirements.txt
pip install -e .

# Run pytest to verify all 144 unit tests
pytest
```

---

## 2. Dataset Suite Ingestion

Generate and verify the 2+2 Multi-Environment Suite (`living_room`, `office_room`, `ocean`, `abandonedfactory`):
```bash
# Generate the benchmark suite
python scripts/download_datasets.py --offline-suite

# Verify image counts, dimensions, and ground-truth alignments
python scripts/verify_dataset_integrity.py
```

---

## 3. End-to-End Demo & Multi-Config Benchmark

### Run Interactive Demonstration
```bash
python scripts/run_demo.py
```

### Run Full 20-Run Benchmark
```bash
python experiments/benchmark.py
```
Outputs are written to:
- `results/csv/benchmark_summary.csv`
- `results/benchmark_results.md`
- `results/logs/*.json`

---

## 4. Visualization & Ablation Charts

### Generate Comparative Figures
```bash
python scripts/generate_ablation_charts.py
```
Generates:
- `results/figures/ablation_ate_comparison.png`
- `results/figures/ablation_tracking_stability.png`
- `results/figures/ablation_latency_throughput.png`

### Generate GPS Outage Drift Analysis
```bash
python scripts/evaluate_gps_outage.py \
    --traj results/csv/faster_orb_v1__icl_nuim__living_room_traj1_loop_trajectory.txt \
    --gt data/icl_nuim/living_room_traj1_loop/groundtruth.txt \
    --outage-start 15 \
    --output results/figures/gps_outage_drift_analysis.png
```

### Generate Animated MP4 Video Dashboards
```bash
# Indoor living room
python scripts/generate_trajectory_video.py \
    --dataset-cfg configs/datasets/icl_nuim.yaml \
    --exp-cfg configs/experiments/faster_orb.yaml \
    --output results/figures/vo_trajectory_demo.mp4

# Indoor office room
python scripts/generate_trajectory_video.py \
    --dataset-cfg configs/datasets/icl_nuim_office.yaml \
    --exp-cfg configs/experiments/faster_orb.yaml \
    --traj results/csv/faster_orb_v1__icl_nuim__office_room_traj0_loop_trajectory.txt \
    --output results/figures/vo_trajectory_office.mp4
```

---

## 5. Trajectory Post-Smoothing
```bash
python scripts/filter_trajectory.py \
    --in-traj results/csv/faster_orb_v1__icl_nuim__living_room_traj1_loop_trajectory.txt \
    --out-traj results/csv/faster_orb_smoothed_trajectory.txt \
    --gt data/icl_nuim/living_room_traj1_loop/groundtruth.txt \
    --window 5
```
