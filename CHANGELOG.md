# Changelog

All notable changes to this project are documented here.

## [Unreleased]
- [ ] Download and run on actual ICL-NUIM dataset
- [ ] Populate report.md results tables with measured values
- [ ] Implement GPS/VO fusion EKF interface
- [ ] FASTER detector genuine implementation

## [0.5.0] - 2024-10-19 to 2024-10-21
- Add epipolar geometry visualization module
- Add scale drift visualization with fill-between
- Add `run_scale_analysis.py` CLI
- Export ExtractionResult and scale_plot from packages
- Add limitations and validated claims document
- Add coordinate frame conventions reference
- Add feature algorithm reference with availability notes

## [0.4.0] - 2024-10-17 to 2024-10-18
- Add SyntheticDataset for in-memory testing
- Add scale drift analysis and visualization
- Add PipelineConfig dataclass
- Add TrackingReport unit tests
- Add NED->camera conversion tests
- Add AbandonedFactory TartanAir config
- Add extended benchmark config with v2 tuned configs

## [0.3.0] - 2024-10-16 to 2024-10-17
- Add triangulation and Fundamental matrix modules
- Add FeatureExtractor unified wrapper
- Refactor pipeline to delegate detect/describe
- Add PoseAccumulator TUM roundtrip tests
- Add scale drift experiment module
- Add tuned v2 configs (FAST+BRIEF v2, ORB+BRISK v2, ORB+ORB v2)
- Add feature extraction timing benchmark experiment

## [0.2.0] - 2024-10-15 to 2024-10-16
- Add experiment runner, benchmark, GPS outage simulation
- Add CLI scripts: run_vo, evaluate_trajectory, run_benchmark
- Add docs: architecture, dataset_setup, evaluation_metrics
- Fix check_env.py Unicode encoding on Windows
- Export clean public APIs from all package __init__ modules

## [0.1.0] - 2024-10-15
- Initial project scaffold with README, requirements, pyproject
- All four feature configurations (FAST+BRIEF, FAST+ORB, ORB+ORB, ORB+BRISK)
- ManualBRIEF fallback for environments without opencv-contrib
- 66 unit tests passing (geometry, features, matching, datasets, evaluation)
- ATE Umeyama Sim(3) alignment verified on synthetic trajectories
- ICL-NUIM and TartanAir dataset loaders with ground-truth parsing
