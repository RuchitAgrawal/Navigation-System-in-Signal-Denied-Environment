# Running Experiments

## Quick Start

### 1. Check environment
`bash
python check_env.py
`

### 2. Verify data is set up
See docs/dataset_setup.md for download instructions.

### 3. Run one experiment (ORB+ORB on ICL-NUIM)
`bash
python scripts/run_vo.py \
  -e configs/experiments/orb_orb.yaml \
  -d configs/datasets/icl_nuim.yaml \
  --alignment sim3
`

### 4. Run all benchmarks
`bash
python scripts/run_benchmark.py
`

### 5. Evaluate a saved trajectory
`bash
python scripts/evaluate_trajectory.py \
  --est results/csv/orb_orb__icl_nuim__living_room_traj1_loop_trajectory.txt \
  --gt data/icl_nuim/living_room_traj1_loop/groundtruth.txt
`

## Output Files

| File | Description |
|------|-------------|
| results/csv/*_frames.csv | Per-frame diagnostics |
| results/csv/*_trajectory.txt | TUM-format estimated trajectory |
| results/csv/benchmark_summary.csv | Aggregate benchmark results |
| results/figures/*.png | Trajectory and comparison plots |
| results/logs/*.json | JSON summary per run |

