# 📋 Complete Project Audit & File Cleanup Guide

> **Project Title:** A Computer Vision-Assisted GPS Navigation System for Robust Positioning in Signal-Denied Environments  
> **Repository:** `Navigation-System-in-Signal-Denied-Environment`  
> **Audit Date:** November 2026  
> **Status:** Read-Only Audit (No files have been modified or deleted yet)

---

## 📑 Table of Contents
1. [Executive Summary](#-executive-summary)
2. [Actionable File Deletion & Retention Checklist](#-actionable-file-deletion--retention-checklist)
   - [Category 1: Safe to Delete (Redundant & Backup Files)](#category-1-safe-to-delete-redundant--backup-files)
   - [Category 2: Optional Removal (Only if you want an Ultra-Minimal Repo)](#category-2-optional-removal-only-if-you-want-an-ultra-minimal-repo)
   - [Category 3: Protected Files (DO NOT DELETE)](#category-3-protected-files-do-not-delete)
3. [Complete File-by-File & Folder-by-Folder Audit](#-complete-file-by-file--folder-by-folder-audit)
   - [Root Directory Files](#root-directory-files)
   - [Configuration Files (`configs/`)](#configuration-files-configs)
   - [Data Directory (`data/`)](#data-directory-data)
   - [Documentation (`docs/`)](#documentation-docs)
   - [Experiments (`experiments/`)](#experiments-experiments)
   - [Results & Figures (`results/`)](#results--figures-results)
   - [Executable Scripts (`scripts/`)](#executable-scripts-scripts)
   - [Core Source Code Library (`src/`)](#core-source-code-library-src)
   - [Automated Tests (`tests/`)](#automated-tests-tests)
4. [Missing Professional Assets](#-missing-professional-assets)
5. [Final Target Project Structure](#-final-target-project-structure)

---

## 🔍 Executive Summary

This audit examined every single file across the repository, tracing code imports, YAML references, dataset loaders, benchmark pipelines, and documentation dependencies.

### Key Findings:
- **Total Project Items:** 211 active repository items (excluding `venv/`, `.git/`, and caches).
- **Redundant Exact Duplicates:** 1 exact duplicate (`overall.md` is an exact duplicate of `docs/project_guide.md`, SHA-256: `f57eed8e...`).
- **Safety Backup Files:** 1 backup document (`Seminar_Report_VO_Navigation_backup.docx` in the parent folder).
- **Core Engine Health:** 168 passing automated tests validating all features, geometry, motion models, and evaluations.
- **Presentation Capabilities:** Dual demonstration modes ready — **Turnkey offline demo** (`scripts/run_demo.py`) and **Interactive real-time webcam dashboard** (`scripts/live_dashboard.py`).

---

## ⚡ Actionable File Deletion & Retention Checklist

Use this checklist to decide which files to delete.

### Category 1: Safe to Delete (Redundant & Backup Files)

These files can be removed immediately without breaking any script, test, or functionality.

| # | File Path | Size | Reason for Removal | Consequence of Deletion | Action |
|---|---|---|---|---|:---:|
| 1 | `Navigation-System-in-Signal-Denied-Environment/overall.md` | 33.1 KB | **100% Exact Duplicate** of `docs/project_guide.md`. Created as a temporary working copy. | **Zero impact.** The canonical guide is stored safely in `docs/project_guide.md`. | ❌ **DELETE** |
| 2 | `Seminar_Report_VO_Navigation_backup.docx` | 1.33 MB | Temporary safety backup copy of the Word report created before updates. | **Zero impact on code.** You already have the updated `Seminar_Report_VO_Navigation.docx`. | ❌ **DELETE (or move to external backup)** |

---

### Category 2: Optional Removal (Only if you want an Ultra-Minimal Repo)

These files are working components, but they are **secondary/advanced** (used only for downloading external multi-GB datasets or extra ablation experiments). If your goal is a stripped-down, presentation-only repo, these can optionally be deleted or archived.

| # | File / Folder | Purpose | Why it is Optional | Recommendation |
|---|---|---|---|:---:|
| 1 | `scripts/download_datasets.py` | Automated downloader for external ICL-NUIM / TartanAir datasets. | You already have `data/demo_sequence` bundled for presentations. | ⚠️ **Optional** |
| 2 | `scripts/verify_dataset_integrity.py` | Integrity checker for downloaded multi-GB dataset sequences. | Only needed if you download raw external zip files. | ⚠️ **Optional** |
| 3 | `configs/datasets/icl_nuim*.yaml`<br>`configs/datasets/tartanair*.yaml` | Configs for external sequences. | Not needed if presenting with the bundled synthetic demo data or live webcam. | ⚠️ **Optional** |
| 4 | `src/datasets/tartanair.py` | Sequence loader for AirSim TartanAir drone data. | TartanAir dataset is not downloaded; base dataset is synthetic/ICL-NUIM. | ⚠️ **Optional** |
| 5 | `docs/references/perez_grau_2017_uav_gps_denied.pdf` | 4.2 MB academic reference paper. | Academic reference for thesis literature review; code does not read it. | ⚠️ **Optional** (Keep for viva reference) |
| 6 | `experiments/feature_timing.py` | Standalone microsecond timing test. | Latency numbers are already compiled in your report tables. | ⚠️ **Optional** |

---

### Category 3: Protected Files (DO NOT DELETE)

These files are **essential** for running the demo, live dashboard, test suite, and viva presentation.

| Component | Files / Folders | Why They Must Be Kept |
|---|---|---|
| **Core Source (`src/`)** | `src/features/`, `src/geometry/`, `src/odometry/`, `src/evaluation/`, `src/matching/`, `src/visualization/`, `src/datasets/base_dataset.py`, `synthetic.py`, `icl_nuim.py` | Contains your entire algorithm implementation (Adaptive FASTER, QuadTree, Essential Matrix, Umeyama ATE). Deleting any file here breaks the project. |
| **Live Interactive HUD** | `scripts/live_dashboard.py` | Your hero live demonstration tool with webcam tracking and top-down map. |
| **Offline Demo** | `scripts/run_demo.py` & `data/demo_sequence/` | Your fallback demonstration that works offline in 5 seconds. |
| **GPS Outage CLI** | `scripts/evaluate_gps_outage.py` & `experiments/gps_outage.py` | Evaluates navigation performance when GPS drops out ($2.28\%$ drift rate). |
| **Benchmark Visuals** | `scripts/generate_ablation_charts.py` & `scripts/generate_trajectory_video.py` | Generates publication-ready figures and MP4 video for your presentation slides. |
| **Configs** | `configs/default.yaml`, `configs/datasets/demo.yaml`, `configs/experiments/faster_orb.yaml` (and benchmark configs) | Defines the 5 comparative configurations and RANSAC thresholds. |
| **Official Report & Guides** | `Seminar_Report_VO_Navigation.docx`, `README.md`, `docs/project_defense_master_guide.md`, `docs/project_guide.md` | Your primary written report, front page, and viva examination preparation guides. |
| **Results Assets** | `results/figures/*.png`, `results/benchmark_results.md`, `results/csv/benchmark_summary.csv` | Evidence of your experimental results and accuracy benchmarks. |
| **Automated Tests** | `tests/` (all 33 test files) | Demonstrates software engineering rigor and passing test coverage. |
| **Build & Environment** | `check_env.py`, `requirements.txt`, `pyproject.toml`, `.gitignore` | Required for installing, checking, and packaging dependencies. |

---

## 🔍 Complete File-by-File & Folder-by-Folder Audit

Below is the exhaustive, item-by-item breakdown of every file in the repository.

### Root Directory Files

#### `Seminar_Report_VO_Navigation.docx`
- **Purpose:** Primary official Microsoft Word seminar / project report containing complete theoretical background, mathematical derivations, five-configuration benchmarks, and visual figures.
- **Usage:** Academic submission, examiner review, and grading.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `Seminar_Report_VO_Navigation_backup.docx`
- **Purpose:** Safety backup snapshot created before editing the report document.
- **Usage:** Recovery file in case the main document is corrupted.
- **Presentation Necessity:** None.
- **Recommendation:** **Unnecessary** (Delete or move to an external flash drive/cloud).

#### `.gitattributes`
- **Purpose:** Configures Git Line Endings (CRLF/LF) and Git LFS tracking rules.
- **Usage:** Git version control client.
- **Presentation Necessity:** None.
- **Recommendation:** **Useful.**

#### `.gitignore`
- **Purpose:** Prevents temporary caches (`__pycache__`, `.pytest_cache`), virtual environments (`venv/`), and raw data from cluttering Git history.
- **Usage:** Git version control client.
- **Presentation Necessity:** None.
- **Recommendation:** **Essential.**

#### `CHANGELOG.md`
- **Purpose:** Documents chronological release history, bug fixes, and feature milestones (Adaptive FASTER, QuadTree bucketing, GPS outage simulation).
- **Usage:** Project documentation and version tracking.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `check_env.py`
- **Purpose:** Standalone verification script that inspects Python environment, NumPy, SciPy, Matplotlib, OpenCV algorithms (FAST, ORB, BRISK, BRIEF availability), and verifies pipeline imports.
- **Usage:** Executed before running any demo or benchmark (`python check_env.py`) to confirm hardware and library compatibility.
- **Presentation Necessity:** **High.** Excellent opening step in a viva demo to verify that the environment is healthy.
- **Recommendation:** **Essential.**

#### `LICENSE`
- **Purpose:** Formal open-source license text (BSD 3-Clause).
- **Usage:** Open-source compliance.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `overall.md`
- **Purpose:** Exact byte-for-byte duplicate (SHA-256: `f57eed8e...`) of `docs/project_guide.md`.
- **Usage:** None (orphaned duplicate in root directory).
- **Presentation Necessity:** None.
- **Recommendation:** **Unnecessary (DELETE).**

#### `pyproject.toml`
- **Purpose:** Standard Python build system configuration (PEP 517/518), package metadata, and Pytest configuration rules.
- **Usage:** Invoked by `pip install -e .` and `pytest`.
- **Presentation Necessity:** None.
- **Recommendation:** **Essential.**

#### `README.md`
- **Purpose:** Front-page GitHub markdown guide detailing project motivation, architecture, key results, five benchmark configurations, quickstart steps, and interactive live dashboard instructions.
- **Usage:** Primary project overview.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `requirements.txt`
- **Purpose:** Pinned list of required runtime Python packages (`numpy>=1.24,<2.0`, `opencv-python>=4.8.0`, `scipy>=1.10.0`, `matplotlib>=3.7.0`, `pandas>=2.0.0`, `pyyaml>=6.0`, `psutil>=5.9.0`).
- **Usage:** Used by `pip install -r requirements.txt`.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

---

### Configuration Files (`configs/`)

#### `configs/default.yaml`
- **Purpose:** Central baseline parameters (RANSAC thresholds, Lowe ratio `0.75`, minimum inlier thresholds, default output flags).
- **Usage:** Read by `src/odometry/config.py` and `experiments/runner.py` as default values when not overridden by specific experiment YAML files.
- **Presentation Necessity:** Low.
- **Recommendation:** **Essential.**

#### `configs/datasets/demo.yaml`
- **Purpose:** Configures dataset path, image dimensions, camera focal length (`481.2 px`), and principal point for the bundled 40-frame synthetic demo sequence.
- **Usage:** Consumed by `scripts/run_demo.py` and `scripts/verify_dataset_integrity.py`.
- **Presentation Necessity:** **Essential.** Powers the zero-setup offline demonstration.
- **Recommendation:** **Essential.**

#### `configs/datasets/icl_nuim.yaml` & `configs/datasets/icl_nuim_office.yaml`
- **Purpose:** Dataset definitions, intrinsic calibration, and ground-truth file formats for external ICL-NUIM benchmark sequences.
- **Usage:** Consumed by `experiments/benchmark.py` and `src/datasets/icl_nuim.py`.
- **Presentation Necessity:** Optional.
- **Recommendation:** **Useful.**

#### `configs/datasets/tartanair.yaml` & `configs/datasets/tartanair_abandonedfactory.yaml`
- **Purpose:** Configuration files for the AirSim-based TartanAir drone dataset.
- **Usage:** Consumed by `src/datasets/tartanair.py` and `experiments/benchmark.py`.
- **Presentation Necessity:** Optional.
- **Recommendation:** **Useful.**

#### `configs/experiments/benchmark.yaml`
- **Purpose:** Master configuration mapping all five configurations across test sequences for automated benchmarking.
- **Usage:** Executed by `python -m experiments.benchmark`.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `configs/experiments/benchmark_icl_nuim_real.yaml`
- **Purpose:** Experiment runner configuration targeting physical downloaded sequences rather than synthetic data.
- **Usage:** Referenced for testing external sequences.
- **Presentation Necessity:** Optional.
- **Recommendation:** **Useful.**

#### `configs/experiments/fast_orb.yaml` (Config 1)
- **Purpose:** Fixed-threshold FAST detector + ORB descriptor configuration.
- **Usage:** Standard comparison baseline in project report.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `configs/experiments/fast_brief.yaml` (Config 2)
- **Purpose:** FAST detector + ManualBRIEF descriptor configuration.
- **Usage:** Evaluates fast binary matching without rotation invariance.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `configs/experiments/orb_brisk.yaml` (Config 3)
- **Purpose:** Multi-scale ORB detector + 512-bit BRISK descriptor configuration.
- **Usage:** Evaluates high-dimensional binary matching robustness.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `configs/experiments/faster_orb.yaml` (Config 4 - Primary Contribution)
- **Purpose:** Our core innovation: Adaptive FASTER detector (dynamic threshold iteration) + QuadTree spatial bucketing + sub-pixel corner refinement + ORB descriptors.
- **Usage:** Primary configuration achieving the lowest ATE RMSE ($0.038\text{ m}$).
- **Presentation Necessity:** **Essential.** The central focus of the project defense.
- **Recommendation:** **Essential.**

#### `configs/experiments/fast_orb_pnp.yaml` (Config 5)
- **Purpose:** Hybrid 2D-to-3D pose estimation configuration using EPnP with RANSAC.
- **Usage:** Compares monocular Essential Matrix against depth-assisted PnP estimation.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `configs/experiments/faster_brief.yaml` & `configs/experiments/faster_orb_grid.yaml`
- **Purpose:** Ablation study configurations testing Adaptive FASTER with BRIEF and FASTER with Uniform Grid bucketing instead of QuadTree.
- **Usage:** Proves why QuadTree is superior to Grid bucketing.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Useful.**

#### `configs/experiments/gps_outage.yaml`
- **Purpose:** Configures GPS dropout start/end frame indices, satellite measurement noise ($\sigma = 0.5\text{ m}$), and VO dead-reckoning drift accumulation metrics.
- **Usage:** Consumed by `experiments/gps_outage.py` and `scripts/evaluate_gps_outage.py`.
- **Presentation Necessity:** **Essential.** Key demonstration of GPS-denied navigation.
- **Recommendation:** **Essential.**

#### `configs/experiments/orb_orb.yaml`
- **Purpose:** OpenCV default ORB detector + ORB descriptor baseline configuration.
- **Usage:** Industry baseline used in `scripts/run_demo.py`.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

---

### Data Directory (`data/`)

#### `data/demo_sequence/groundtruth.txt`
- **Purpose:** 40 lines of 6-DoF ground truth poses in standard TUM format (`timestamp tx ty tz qx qy qz qw`).
- **Usage:** Trajectory alignment, scale calculation, and ATE RMSE metric computation.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `data/demo_sequence/rgb.txt`
- **Purpose:** TUM-format index mapping timestamps to relative image file paths.
- **Usage:** Read by dataset parsers to load frames sequentially.
- **Presentation Necessity:** **Essential.**
- **Recommendation:** **Essential.**

#### `data/demo_sequence/rgb/0000.png` through `0039.png`
- **Purpose:** 40 pre-rendered synthetic image frames ($640 \times 480$) with known 3D camera trajectory through a textured indoor environment.
- **Usage:** Loaded by `scripts/run_demo.py` and unit test pipelines.
- **Presentation Necessity:** **Essential.** Enables instant offline demonstration without external hardware.
- **Recommendation:** **Essential.**

---

### Documentation (`docs/`)

#### `docs/architecture.md`
- **Purpose:** System architecture specification, ASCII pipeline diagrams, and modular interface definitions.
- **Usage:** Referenced in report methodology and presentation slides.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `docs/coordinate_frames.md`
- **Purpose:** Definition of Camera coordinate frame ($+X$ Right, $+Y$ Down, $+Z$ Forward), World frame, and aerospace NED (North-East-Down) frame transformations.
- **Usage:** Explains why camera vectors transform as they do during 3D plotting.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Essential.**

#### `docs/dataset_setup.md`
- **Purpose:** Guide detailing how to download and extract full ICL-NUIM and TartanAir datasets.
- **Usage:** Reference for downloading external multi-gigabyte datasets.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `docs/evaluation_metrics.md`
- **Purpose:** Mathematical derivations of Absolute Trajectory Error (ATE RMSE), Relative Pose Error (RPE), drift percentage, and Umeyama Sim(3) closed-form alignment.
- **Usage:** Core theory behind performance validation.
- **Presentation Necessity:** **High.** Explains the mathematical rigor behind benchmark numbers.
- **Recommendation:** **Essential.**

#### `docs/feature_algorithms.md`
- **Purpose:** Mathematical descriptions of FAST (Bresenham circle test), Adaptive FASTER threshold adaptation logic, ORB scale pyramids, and BRIEF/BRISK bitstrings.
- **Usage:** Theory reference for Chapter 4 of the project report.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `docs/hso_comparison.md`
- **Purpose:** Literature comparison contrasting our feature-based VO system with direct methods (DSO / Hybrid Sparse Odometry).
- **Usage:** Viva defense prep when asked why feature-based VO was chosen over direct methods.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `docs/limitations.md`
- **Purpose:** Honest engineering appraisal of monocular VO limitations (scale ambiguity, low-texture failure, motion blur, pure rotation degeneracy).
- **Usage:** Critical section in report and defense presentation.
- **Presentation Necessity:** **High.** Demonstrates engineering maturity to evaluators.
- **Recommendation:** **Essential.**

#### `docs/project_defense_master_guide.md`
- **Purpose:** Comprehensive Master Defense / Viva Guide containing anticipated examiner questions, technical answers, algorithm justifications, and key statistics.
- **Usage:** Student preparation for oral examination.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `docs/project_guide.md`
- **Purpose:** Complete narrative explanation of the entire project written in a clear, educational, step-by-step format.
- **Usage:** Project study guide and teaching resource.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `docs/quickstart_guide.md`
- **Purpose:** Quick reference card of shell commands to run demos, live webcam, benchmarks, and tests.
- **Usage:** Quick CLI reference during live demonstrations.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `docs/references.md`
- **Purpose:** Academic bibliography listing peer-reviewed papers (Nistér 2004, Hartley & Zisserman, Rublee et al. 2011, Rosten & Drummond, Umeyama 1991).
- **Usage:** Academic citation in reports and slides.
- **Presentation Necessity:** Low.
- **Recommendation:** **Essential.**

#### `docs/references/perez_grau_2017_uav_gps_denied.pdf`
- **Purpose:** Downloaded 4.2 MB research paper (*"Multi-Sensor Navigation System for UAVs in GPS-Denied Environments"* by Perez-Grau et al., 2017) serving as the academic baseline for the GPS outage problem statement.
- **Usage:** Literature reference.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `docs/report.md`
- **Purpose:** Comprehensive 40 KB Markdown report containing the full technical paper text.
- **Usage:** Source text for compiling reports and documentation.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Useful.**

#### `docs/running_experiments.md`
- **Purpose:** Instructions for running benchmark experiments across various configurations and datasets.
- **Usage:** Operational guide.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `docs/scale_ambiguity.md`
- **Purpose:** In-depth treatise on the monocular scale problem, epipolar baseline normalization ($||\mathbf{t}|| = 1$), and physical scale recovery methods (RGB-D, stereo baseline, ground plane height prior).
- **Usage:** Crucial for answering viva questions on why monocular VO has arbitrary scale.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `docs/troubleshooting.md`
- **Purpose:** Diagnostic guide for OpenCV installation issues, missing C++ DLLs, camera index errors, and RANSAC degeneracies.
- **Usage:** Reference during setup.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

---

### Experiments (`experiments/`)

#### `experiments/__init__.py`
- **Purpose:** Exposes package structure for `python -m experiments.benchmark`.
- **Usage:** Python module import resolution.
- **Presentation Necessity:** None.
- **Recommendation:** **Essential.**

#### `experiments/benchmark.py`
- **Purpose:** Executes automated comparative benchmarks across all configured feature detector/descriptor pairs, gathers ATE RMSE, RPE, runtime FPS, and writes `benchmark_summary.csv` and `benchmark_results.md`.
- **Usage:** Run via `python -m experiments.benchmark --config configs/experiments/benchmark.yaml`.
- **Presentation Necessity:** **High.** Produces the core comparative experimental evidence.
- **Recommendation:** **Essential.**

#### `experiments/feature_timing.py`
- **Purpose:** Benchmarks microsecond extraction latencies of FAST, ORB, and BRISK on standard test images over 50 repetitions.
- **Usage:** Standalone script (`python -m experiments.feature_timing`) to verify real-time frame rates.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Useful.**

#### `experiments/gps_outage.py`
- **Purpose:** Implements the GPS outage simulation: feeds GPS fixes, cuts GPS at frame 15, activates VO dead-reckoning, and measures position drift ($2.28\%$ drift rate).
- **Usage:** Consumed by `scripts/evaluate_gps_outage.py`.
- **Presentation Necessity:** **Essential.** Proves the core mission of navigating in GPS-denied areas.
- **Recommendation:** **Essential.**

#### `experiments/runner.py`
- **Purpose:** Low-level orchestrator that takes any (experiment YAML, dataset YAML) pair, executes the VO pipeline, calculates ATE via Umeyama Sim(3), and saves per-frame logs.
- **Usage:** Underlying engine called by `benchmark.py` and `scripts/run_vo.py`.
- **Presentation Necessity:** None.
- **Recommendation:** **Essential.**

#### `experiments/scale_analysis.py`
- **Purpose:** Computes local scale factors over sliding temporal windows to quantify monocular scale drift.
- **Usage:** Analyzes scale stability over long trajectories.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Useful.**

---

### Results & Figures (`results/`)

#### `results/benchmark_results.md`
- **Purpose:** Rendered Markdown table displaying benchmark results (ATE RMSE, RPE drift, inliers, execution time) across all 5 configurations.
- **Usage:** Can be opened directly in VS Code / GitHub during presentation to display results instantly.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `results/csv/benchmark_summary.csv`
- **Purpose:** Tabular raw metrics data corresponding to `benchmark_results.md`.
- **Usage:** Source data for table generation.
- **Presentation Necessity:** Low.
- **Recommendation:** **Essential.**

#### `results/csv/orb_orb_v1__icl_nuim__demo_sequence_frames.csv` & `...trajectory.txt`
- **Purpose:** Log of per-frame tracking states (inliers, matching time, pose coordinates).
- **Usage:** Output files from running the demo sequence.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `results/figures/feature_matches_sample.png`
- **Purpose:** Clean side-by-side visualization of consecutive video frames connected by green inlier feature correspondence lines.
- **Usage:** Essential visual slide in project presentation showing feature matching in action.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `results/figures/gps_outage_orb_orb_demo.png`
- **Purpose:** Trajectory plot showing Ground Truth (Green), GPS Fixes (Blue Dots), and VO Dead-Reckoning (Red Dashed Line) taking over during outage.
- **Usage:** The hero graphic illustrating the primary problem and solution of the project.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `results/figures/scale_drift.png`
- **Purpose:** Graph illustrating monocular scale drift over frame index.
- **Usage:** Visual aid explaining scale ambiguity.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Useful.**

#### `results/figures/trajectory_comparison.png`
- **Purpose:** Bird's-eye and 3D comparison plot of Estimated VO Trajectory vs Ground Truth Trajectory.
- **Usage:** Primary visual result proving trajectory tracking accuracy.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `results/logs/orb_orb_v1__icl_nuim__demo_sequence.json`
- **Purpose:** Machine-readable run configuration log with timestamps, parameters, and summary error metrics.
- **Usage:** Reproducibility verification.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

---

### Executable Scripts (`scripts/`)

#### `scripts/download_datasets.py`
- **Purpose:** Utility script with automated curl/requests logic to download official ICL-NUIM and TartanAir sequences.
- **Usage:** Used if you want to download external multi-gigabyte datasets.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `scripts/evaluate_gps_outage.py`
- **Purpose:** Command-line tool to run the GPS dropout simulation and compute drift metrics ($2.28\%$ drift rate) with visual plotting.
- **Usage:** Run via `python scripts/evaluate_gps_outage.py`.
- **Presentation Necessity:** **High.** Primary CLI tool to demonstrate the GPS-denied takeover.
- **Recommendation:** **Essential.**

#### `scripts/evaluate_trajectory.py`
- **Purpose:** Evaluates an estimated trajectory text file against ground truth using Umeyama Sim(3) alignment, printing ATE RMSE, Mean, and RPE.
- **Usage:** Headless metric verification CLI.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Essential.**

#### `scripts/filter_trajectory.py`
- **Purpose:** Applies moving average or Kalman filtering to noisy estimated trajectories.
- **Usage:** Optional trajectory post-processing CLI.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `scripts/generate_ablation_charts.py`
- **Purpose:** Reads `results/csv/benchmark_summary.csv` and renders publication-ready Matplotlib bar charts and line graphs comparing detector thresholds, bucketing techniques, and error rates.
- **Usage:** Generates visual charts for inclusion in presentation slides and report.
- **Presentation Necessity:** **High.**
- **Recommendation:** **Essential.**

#### `scripts/generate_demo_data.py`
- **Purpose:** Procedurally generates the 40-frame textured synthetic images in `data/demo_sequence/`.
- **Usage:** Used if demo data needs to be regenerated from scratch.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

#### `scripts/generate_trajectory_video.py`
- **Purpose:** Generates a dual-panel animated MP4 video showing the camera view on the left and the 3D trajectory growing dynamically on the right.
- **Usage:** Excellent presentation asset to play during slides.
- **Presentation Necessity:** **High.** Highly impressive visual demonstration for examiners.
- **Recommendation:** **Essential.**

#### `scripts/live_dashboard.py`
- **Purpose:** Real-time OpenCV live dashboard running on a physical USB/laptop webcam. Features a 3-panel UI: Live Camera with tracked keypoints, Top-Down Bird's-Eye X-Z Trajectory Map with heading arrow and yaw telemetry, and a Status Bar (FPS, features, inliers, GPS status). Incorporates our dual Homography (for pure rotation) and Essential Matrix (for 3D translation) pose estimation.
- **Usage:** Run via `python scripts/live_dashboard.py`.
- **Presentation Necessity:** **Critical.** The primary interactive live demonstration piece of the project.
- **Recommendation:** **Essential.**

#### `scripts/run_demo.py`
- **Purpose:** One-command turnkey demonstration running the full pipeline on the bundled 40-frame sequence in under 5 seconds, displaying real-time tracking and generating comparison plots.
- **Usage:** Run via `python scripts/run_demo.py`.
- **Presentation Necessity:** **Critical.** Guaranteed, zero-failure fallback demo for presentations even without internet or an external camera.
- **Recommendation:** **Essential.**

#### `scripts/run_vo.py`
- **Purpose:** General-purpose headless runner to execute any experiment config on any dataset config from the CLI.
- **Usage:** General command-line invocation.
- **Presentation Necessity:** Medium.
- **Recommendation:** **Essential.**

#### `scripts/verify_dataset_integrity.py`
- **Purpose:** Sanity checker that inspects dataset folders for missing images, broken timestamp mappings, or corrupted PNGs.
- **Usage:** Diagnostic utility.
- **Presentation Necessity:** Low.
- **Recommendation:** **Useful.**

---

### Core Source Code Library (`src/`)

All modules in `src/` form the core engine of the project.

#### `src/datasets/`
- `base_dataset.py`: Abstract BaseDataset interface and CameraIntrinsics dataclass. (**Essential**)
- `icl_nuim.py`: Parser for ICL-NUIM synthetic RGB-D sequences. (**Essential**)
- `synthetic.py`: In-memory programmatic geometric camera-point projection generator used for test verification. (**Essential**)
- `tartanair.py`: Parser for TartanAir drone dataset sequences. (**Useful**)

#### `src/features/`
- `bucketing.py`: Implements Spatial Bucketing: QuadTree recursive spatial division and Uniform Grid bucketing to enforce uniform feature distribution across the image. (**Essential**)
- `config.py`: Configuration dataclasses and factory functions for detector/descriptor combinations. (**Essential**)
- `descriptor.py`: Wraps ORB, BRISK, and includes our custom pure-Python `ManualBRIEF` fallback when `opencv-contrib` is not installed. (**Essential**)
- `detector.py`: Implements standard FAST, ORB, and our novel **Adaptive FASTER detector** with iterative threshold self-tuning. (**Essential**)
- `extractor.py`: High-level `FeatureExtractor` combining detection, spatial bucketing, subpixel refinement, and descriptor extraction into a unified call. (**Essential**)
- `subpixel.py`: Sub-pixel corner coordinate refinement via `cv2.cornerSubPix`. (**Essential**)

#### `src/geometry/`
- `essential.py`: Calibrated 5-point Essential Matrix estimation with RANSAC (`cv2.findEssentialMat` and `cv2.recoverPose`), chirality cheirality check, and inlier masking. (**Essential**)
- `fundamental.py`: Uncalibrated 8-point Fundamental Matrix estimation for epipolar geometry verification. (**Useful**)
- `pnp.py`: Perspective-n-Point pose solver (`cv2.solvePnPRansac`) used in Config 5 (Hybrid PnP). (**Essential**)
- `pose.py`: `PoseAccumulator` maintaining global SE(3) trajectory state by chaining relative frame-to-frame pose estimates. (**Essential**)
- `transforms.py`: SE(3) transformation matrices, inversion, composition, Euler angles, SO(3) validation, and NED frame conversions. (**Essential**)
- `triangulation.py`: 3D landmark triangulation from calibrated two-view correspondences. (**Essential**)

#### `src/matching/`
- `matcher.py`: Robust feature matching using Brute-Force Hamming distance and Lowe's Ratio Test ($0.75$) to reject ambiguous matches. (**Essential**)

#### `src/odometry/`
- `config.py`: VO pipeline parameters dataclass. (**Essential**)
- `filter.py`: Trajectory smoothing filters (Kalman filter, exponential moving average). (**Useful**)
- `motion_model.py`: Constant-velocity kinematic motion prior validating relative pose transitions and rejecting degenerate RANSAC flips. (**Essential**)
- `pipeline.py`: Main `VOPipeline` orchestrating feature extraction, temporal matching, pose recovery, scale scaling, and pose accumulation across video sequences. (**Essential**)
- `tracker.py`: Tracks frame-to-frame tracking health, counting inliers, match drops, and tracking state flags. (**Essential**)

#### `src/visualization/`
- `epipolar_plot.py`: Visualizes epipolar geometry lines across matched image pairs. (**Useful**)
- `inlier_plot.py`: Plots RANSAC inlier count and ratio over time. (**Useful**)
- `match_plot.py`: Renders side-by-side feature match correspondences. (**Essential**)
- `report.py`: Builds visual HTML/Markdown experiment reports. (**Useful**)
- `scale_plot.py`: Plots local scale factor evolution over trajectory length. (**Useful**)
- `trajectory_plot.py`: Renders 2D top-down bird's-eye and 3D Matplotlib trajectory plots comparing estimated path with ground truth. (**Essential**)

#### `src/evaluation/`
- `ate.py`: Implements Absolute Trajectory Error (ATE RMSE, Mean, Median, Std) with Umeyama Sim(3) closed-form alignment. (**Essential**)
- `drift.py`: Calculates metric translation drift percentage ($e_{\text{drift}} = \frac{\Delta p}{d_{\text{total}}} \times 100\%$) and scale drift over distance. (**Essential**)
- `metrics.py`: Computes summary metrics and exports formatted CSV files. (**Essential**)
- `pose_error.py`: Calculates relative rotational and translational errors between pose matrices. (**Essential**)
- `rpe.py`: Relative Pose Error (RPE) assessing frame-to-frame drift over sliding intervals. (**Essential**)
- `summary.py`: Formats comparison tables and Markdown/LaTeX summary reports for research documentation. (**Essential**)

---

### Automated Tests (`tests/`)

The repository contains 33 test modules (`test_ablation_charts.py` through `test_triangulation.py`) with 170 unit and integration tests.
- **Purpose:** Verifies mathematical precision, SE(3) matrix invertibility, Umeyama alignment, feature bucketing distribution, and pipeline continuity.
- **Usage:** Run via `pytest tests/`.
- **Presentation Necessity:** **High.** Running `pytest tests/` during an evaluation or defense demonstrates rigorous software engineering practices.
- **Recommendation:** **Essential.**

---

## 💡 Missing Professional Assets

The following two additions are recommended to make the project presentation-ready:

1. **One-Click Windows Launcher (`run_demo.bat`):**  
   A double-clickable desktop batch script that runs the offline demo in one step:
   ```cmd
   @echo off
   echo Launching Visual Odometry Demo...
   python scripts\run_demo.py
   pause
   ```

2. **Presentation Slide Blueprint (`docs/presentation_slides_outline.md`):**  
   A 12-slide structured outline mapping:
   - Slide 1: Title & Team
   - Slide 2: Problem Statement (GPS-Denied Environments)
   - Slide 3: What is Visual Odometry?
   - Slide 4: System Architecture
   - Slide 5: Core Innovation (Adaptive FASTER + QuadTree Bucketing)
   - Slide 6: Pose Recovery & Geometry (Essential Matrix vs Homography)
   - Slide 7: Five Benchmark Configurations & Accuracy Comparison
   - Slide 8: GPS Outage & Dead-Reckoning Experiment (2.28% drift rate)
   - Slide 9: Live Webcam VO Dashboard Demo
   - Slide 10: Limitations & Engineering Trade-offs
   - Slide 11: Real-World Applications (Robotics, UAVs, Defense)
   - Slide 12: Conclusion & Q&A

---

## 🎯 Final Target Project Structure

```
MINOR_PROJECT/
├── Seminar_Report_VO_Navigation.docx                 # Academic Seminar Report
└── Navigation-System-in-Signal-Denied-Environment/
    ├── .gitignore
    ├── .gitattributes
    ├── pyproject.toml
    ├── requirements.txt
    ├── README.md                                     # Project Overview & Quickstart
    ├── check_env.py                                  # Environment & Dependency Verifier
    ├── run_demo.bat                                  # [New] One-Click Windows Demo Launcher
    │
    ├── configs/
    │   ├── default.yaml                              # Global RANSAC & VO Parameters
    │   ├── datasets/                                 # Dataset Calibration Configs
    │   └── experiments/                              # 5 Benchmark & Outage Experiment Configs
    │
    ├── data/
    │   └── demo_sequence/                            # Bundled 40-Frame Synthetic Sequence
    │
    ├── docs/
    │   ├── project_defense_master_guide.md           # Master Viva / Examiner Q&A Guide
    │   ├── project_guide.md                          # Comprehensive Technical Guide
    │   ├── architecture.md                           # System Architecture & Dataflow
    │   ├── evaluation_metrics.md                     # Mathematical Formulations (ATE, RPE)
    │   ├── feature_algorithms.md                     # Feature Detector/Descriptor Mathematics
    │   ├── scale_ambiguity.md                        # Scale Ambiguity & Metric Recovery
    │   ├── hso_comparison.md                         # Direct vs Feature-Based VO Comparison
    │   ├── limitations.md                            # Assumptions & Failure Modes
    │   ├── quickstart_guide.md                       # CLI Cheat Sheet
    │   ├── presentation_outline.md                   # [New] 12-Slide Presentation Blueprint
    │   └── references/                               # Academic Literature Reference PDF
    │
    ├── experiments/                                  # Benchmark & Outage Simulation Engines
    │   ├── benchmark.py
    │   ├── gps_outage.py
    │   └── runner.py
    │
    ├── results/                                      # Experimental Visuals & Summary Tables
    │   ├── benchmark_results.md                      # Comparative Results Table
    │   ├── csv/                                      # Benchmark & Trajectory CSVs
    │   └── figures/                                  # Hero Plots (GPS Outage, Trajectory, Matches)
    │
    ├── scripts/                                      # Executable CLI Tools & Live Applications
    │   ├── live_dashboard.py                         # Real-Time Webcam VO HUD & Trajectory Map
    │   ├── run_demo.py                               # 5-Second Synthetic Demo Runner
    │   ├── evaluate_gps_outage.py                    # GPS Outage Evaluation CLI
    │   ├── generate_ablation_charts.py               # Generates Comparison Charts
    │   ├── generate_trajectory_video.py              # Generates Animated MP4 Video
    │   └── run_vo.py                                 # Headless VO CLI
    │
    ├── src/                                          # Core Algorithm Library (Python Package)
    │   ├── datasets/                                 # Sequence Loaders
    │   ├── features/                                 # Adaptive FASTER, QuadTree, Subpixel, Descriptors
    │   ├── geometry/                                 # Essential Matrix, PnP, PoseAccumulator, Transforms
    │   ├── matching/                                 # BFMatcher + Lowe's Ratio Filter
    │   ├── odometry/                                 # Pipeline, Motion Model, Tracker
    │   ├── evaluation/                               # ATE RMSE, RPE, Drift Computations
    │   └── visualization/                            # 2D/3D Trajectory & Match Plotters
    │
    └── tests/                                        # Automated Pytest Suite (168+ Passing Tests)
```
