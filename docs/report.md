# Research Report

**Title:** A Computer Vision-Assisted GPS Navigation System for Robust Positioning in Signal-Denied Environments  
**Module Contribution:** Visual Odometry Pipeline  
**Author:** Ruchit Agrawal

---

## 1. Abstract

This report presents a classical, feature-based visual odometry (VO) pipeline implemented in Python as a contribution to a GPS-denied navigation system. The pipeline estimates camera motion from consecutive monocular images using standard computer vision techniques and evaluates resulting trajectories against ground truth on two synthetic datasets: ICL-NUIM (indoor) and TartanAir (outdoor). We investigate how four lightweight feature detection and description configurations â€” FAST+BRIEF, FAST+ORB, ORB+ORB, and ORB+BRISK â€” affect trajectory accuracy (ATE), robustness (tracking success rate), and computational efficiency (FPS). A simulated GPS-outage experiment demonstrates the pipeline's role as a fallback positioning mechanism. The implementation is modular, configurable, and designed for eventual integration with a GPS/sensor-fusion component.

---

## 2. Introduction

GPS-based positioning fails or degrades in signal-denied environments such as tunnels, dense urban canyons, indoor spaces, and GPS-jammed zones. Visual odometry offers a self-contained motion estimation capability using only camera images. When integrated with GPS measurements via a sensor-fusion layer (e.g., Extended Kalman Filter), VO can maintain positioning during GPS outages.

This project implements and evaluates the VO module. The broader system â€” including GPS processing, EKF fusion, IMU integration, and road-network localization â€” is handled by other modules outside the scope of this report.

**Research question:**
> How do lightweight feature detection, description, and matching strategies affect the trajectory accuracy, tracking robustness, and computational efficiency of classical visual odometry across synthetic indoor and outdoor environments?

---

## 3. Related Work

### 3.1 Classical Visual Odometry

Feature-based monocular VO (Nister et al., 2004) estimates relative camera pose from 2-D point correspondences using the essential matrix. ORB-SLAM (Mur-Artal et al., 2015) extended this into a full SLAM system with loop closure and bundle adjustment. Our pipeline focuses on the core frame-to-frame estimation without map management.

### 3.2 Reference: HSO

HSO (Luodongting, 2022) is a hybrid sparse VO system in C++ that combines FAST-based detection with direct patch tracking and a sliding-window bundle adjuster. We use HSO as an architectural reference for modular component separation and trajectory output conventions. No HSO source code is included; see `docs/hso_comparison.md` for a detailed comparison.

### 3.3 Feature Algorithms

| Method | Reference | Type |
|--------|-----------|------|
| FAST | Rosten & Drummond, 2006 | Detector |
| ORB | Rublee et al., 2011 | Detector + Descriptor |
| BRIEF | Calonder et al., 2010 | Descriptor (binary, not rotation-invariant) |
| BRISK | Leutenegger et al., 2011 | Descriptor (binary, scale/rotation-invariant) |

---

## 4. Methodology

### 4.1 Pipeline Architecture

```
Frame(t) â”€â”€â–º Detect â”€â”€â–º Describe â”€â”€â–º Match â”€â”€â–º Filter â”€â”€â–º Essential Matrix
                                                           â”€â”€â–º recoverPose
                                                           â”€â”€â–º Accumulate T_wc[t]
```

Every frame produces a `FrameDiagnostics` record regardless of success or failure. Failed frames carry the previous pose forward without extrapolation.

### 4.2 Coordinate Frame Convention

All poses are stored as **T_wc** (4Ã—4 float64) â€” camera-to-world transforms. Pose accumulation:

```
T_wc[t] = T_wc[t-1] @ inv(T_{c(t-1)â†’c(t)})
```

where `T_{c(t-1)â†’c(t)}` is recovered by `cv2.recoverPose`.

### 4.3 Scale Ambiguity

Monocular Essential matrix decomposition recovers translation as a unit direction vector. All ATE results use **Sim(3) alignment** (Umeyama, 1991) to remove the global scale factor. The recovered scale is reported separately.

### 4.4 Feature Configurations

| Config | Detector | Descriptor | Rotation Invariant |
|--------|----------|------------|-------------------|
| A | FAST | BRIEF | No |
| B | FAST | ORB | Partial (descriptor only) |
| C | ORB | ORB | Yes |
| D | ORB | BRISK | Yes |

BRIEF availability: if `opencv-contrib-python` is not installed, a genuine `ManualBRIEF` implementation (Gaussian-sampled 256-bit tests, no orientation) is used and labeled accordingly in all results.

---

## 5. Datasets

### 5.1 ICL-NUIM

Synthetic indoor benchmark with accurate ground-truth poses. We use `living_room_traj1_loop`. Camera: `fx=481.20, fy=480.00, cx=319.50, cy=239.50`. No lens distortion (synthetic).

### 5.2 TartanAir

Large-scale multi-environment synthetic dataset. We use `ocean/Easy/P000`. Camera: `fx=fy=320.0, cx=320.0, cy=240.0`. Poses are converted from NED body frame to camera frame before evaluation.

---

## 6. Results

> **Note:** Results below are placeholders to be filled after running experiments with the actual datasets. All values must be measured â€” none are fabricated.

### 6.1 ICL-NUIM â€” living_room_traj1_loop

| Config | ATE RMSE (m) | RPE Trans RMSE (m) | RPE Rot RMSE (Â°) | Tracking % | Mean FPS |
|--------|--------------|--------------------|------------------|------------|----------|
| FAST+BRIEF | â€” | â€” | â€” | â€” | â€” |
| FAST+ORB   | â€” | â€” | â€” | â€” | â€” |
| ORB+ORB    | â€” | â€” | â€” | â€” | â€” |
| ORB+BRISK  | â€” | â€” | â€” | â€” | â€” |

*Table will be populated after dataset download and experiment execution.*

### 6.2 TartanAir â€” ocean/Easy/P000

| Config | ATE RMSE (m) | RPE Trans RMSE (m) | Tracking % | Mean FPS |
|--------|--------------|--------------------|------------|----------|
| FAST+BRIEF | â€” | â€” | â€” | â€” |
| FAST+ORB   | â€” | â€” | â€” | â€” |
| ORB+ORB    | â€” | â€” | â€” | â€” |
| ORB+BRISK  | â€” | â€” | â€” | â€” |

---

## 7. Discussion

*(To be written after experiments.)*

Key questions to address:
- Which configuration gives the best ATE on indoor vs. outdoor?
- Does rotation invariance (ORB, BRISK) improve results on sequences with large rotational motion?
- Is BRIEF's lack of rotation invariance a practical problem on the chosen sequences?
- How does computation time trade off against accuracy?

---

## 8. Simulated GPS-Outage Experiment

A GPS-denied interval is simulated by withholding GPS updates during a selected frame interval. A one-time scale anchor is set at the outage start using the ground-truth position (simulating the last GPS fix). VO-only propagation then accumulates during the outage.

Drift is measured against ground-truth reference positions. This experiment is clearly labeled as **simulated** â€” no real RF interference or GPS hardware is used.

Results and drift plots will be added after experiment execution.

---

## 9. Limitations

1. **Scale ambiguity** â€” monocular VO cannot recover metric scale without additional information.
2. **No bundle adjustment** â€” frame-to-frame estimation accumulates drift faster than map-based methods.
3. **No loop closure** â€” long sequences will drift without correction.
4. **FASTER not implemented** â€” genuine implementation requires training-data-driven threshold selection.
5. **Synthetic datasets only** â€” real-world results may differ due to lighting, motion blur, and occlusion.

---

## 10. Conclusions

*(To be written after experiments.)*

---

## 11. References

- Calonder et al. (2010). BRIEF: Binary Robust Independent Elementary Features. *ECCV 2010*.
- Hartley & Zisserman (2004). *Multiple View Geometry in Computer Vision*, 2nd ed.
- Leutenegger et al. (2011). BRISK: Binary Robust Invariant Scalable Keypoints. *ICCV 2011*.
- Luodongting (2022). HSO: Hybrid Sparse Visual Odometry. https://github.com/luodongting/HSO
- Mur-Artal et al. (2015). ORB-SLAM. *IEEE T-RO 31(5)*.
- Nister et al. (2004). An Efficient Solution to the Five-Point Relative Pose Problem. *IEEE TPAMI*.
- Rosten & Drummond (2006). Machine Learning for High-Speed Corner Detection. *ECCV 2006*.
- Rublee et al. (2011). ORB: An Efficient Alternative to SIFT or SURF. *ICCV 2011*.
- Sturm et al. (2012). A Benchmark for the Evaluation of RGB-D SLAM Systems. *IROS 2012*.
- Umeyama (1991). Least-Squares Estimation of Transformation Parameters. *IEEE TPAMI*.
- Wang et al. (2020). TartanAir: A Dataset to Push the Limits of Visual SLAM. *IROS 2020*.

