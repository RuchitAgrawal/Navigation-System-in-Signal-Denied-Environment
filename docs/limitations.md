# Known Limitations and Future Work

## Current Limitations

### 1. No Bundle Adjustment
Frame-to-frame pose estimation accumulates drift without correction.
Future extension: sliding-window bundle adjuster (similar to HSO).

### 2. No Loop Closure
Long sequences will drift without loop-closure detection.
Future extension: DBoW2-style bag-of-words place recognition.

### 3. FASTER Not Implemented
Genuine FASTER requires ML-based threshold selection on training data.
Future extension: train on COCO or similar and implement the decision tree.

### 4. Synthetic Datasets Only
All experiments use synthetic data. Real-world testing is planned as Phase 9.

### 5. No IMU Integration
IMU data could stabilize scale and reduce rotation drift.
Future extension: tightly-coupled VIO (Visual-Inertial Odometry).

### 6. No GPU Acceleration
All operations run on CPU. Potential extension: CUDA-accelerated ORB.

## Validated Claims
Only the following claims are based on actual implemented and tested code:
- [x] 66 unit tests passing on Python 3.10 / OpenCV 4.13
- [x] All four feature configurations initialize correctly
- [x] ManualBRIEF fallback activates and produces correct descriptor shape
- [x] ATE Umeyama alignment recovers known scale on synthetic trajectories
- [x] RPE detects constant per-frame drift on synthetic trajectories
- [x] ICL-NUIM loader parses TUM-format files with timestamp association

