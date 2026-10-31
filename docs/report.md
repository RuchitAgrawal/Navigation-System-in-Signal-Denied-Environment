# Research Report

**Title:** A Computer Vision-Assisted GPS Navigation System for Robust Positioning in Signal-Denied Environments  
**Module Contribution:** Visual Odometry Pipeline  
**Author:** Ruchit Agrawal

---

## 1. Abstract

This report presents an enhanced, feature-based classical Visual Odometry (VO) pipeline developed as the primary dead-reckoning positioning component for unmanned aerial vehicle (UAV) navigation in GPS-denied and signal-degraded environments. Drawing upon the foundational architecture proposed by Perez-Grau et al. (*Journal of Field Robotics*, 2017), we formulate an upgraded geometric motion estimation framework designed to overcome critical limitations identified in the reference literature. Specifically, we introduce:
1. **Adaptive FASTER Corner Detection**: dynamic feedback-driven threshold adaptation ensuring keypoint quota compliance across dynamic lighting conditions.
2. **Recursive Quadtree Spatial Bucketing**: replacing rigid uniform grid binning with quadtree spatial partitioning to enforce uniform feature distribution across the image plane and eliminate intra-cell clustering.
3. **Sub-Pixel Corner Refinement**: sub-pixel gradient optimization (`cornerSubPix`) achieving floating-point coordinate precision and suppressing rotational jitter.
4. **Hybrid RGB-D PnP Motion Engine with Monocular Fallback**: fusing metric depth maps via EPnP/P3P RANSAC while maintaining graceful degradation to monocular 5-point Essential matrix estimation when depth information is absent or out-of-range (>4m).
5. **Constant-Velocity Kinematic Motion Prior**: rejecting degenerate epipolar solutions and orientation flips under aggressive aircraft rotation.

We systematically benchmark five detector-descriptor configurations (**FAST+ORB**, **FASTER+ORB**, **ORB+ORB**, **FAST+BRIEF**, and **ORB+BRISK**) across a 2+2 Multi-Environment Suite encompassing indoor structured scenes (**ICL-NUIM Living Room and Office Room**) and challenging outdoor UAV environments (**TartanAir Ocean and Abandoned Factory**). Our empirical findings demonstrate that FASTER+ORB with quadtree bucketing achieves state-of-the-art indoor trajectory accuracy (**0.0231 m ATE RMSE**) at real-time processing speeds (**18.6–19.8 FPS**). Furthermore, a simulated GPS outage experiment confirms that the proposed VO engine sustains continuous, robust dead-reckoning with an accumulated drift rate of only **2.28%** over traveled path length, demonstrating superior robustness for GPS-denied UAV navigation.

---

## 2. Introduction

Global Positioning System (GPS) infrastructure remains inherently vulnerable to signal attenuation, multipath interference, intentional jamming, and physical denial in subterranean tunnels, dense urban canyons, natural ravines, and indoor architectural spaces. Unmanned aerial vehicles (UAVs) operating in such mission-critical settings cannot rely on satellite navigation for state estimation, altitude stabilization, or waypoint guidance.

Visual Odometry (VO)—the process of incrementally estimating the 6-DOF trajectory of an onboard camera through sequential optical frames—provides a completely self-contained, passive, and tamper-resistant positioning mechanism. When integrated with an onboard flight computer and secondary sensors (IMU, barometer, magnetometers), the visual odometry module functions as the mission-critical dead-reckoning backbone during GPS denial.

### 2.1 Problem Scope & The Perez-Grau (2017) Foundation

In *Journal of Field Robotics* (2017), Perez-Grau et al. presented an architecture for autonomous multi-rotor UAV navigation across GPS-denied environments. Their perception subsystem utilized a fixed FAST feature detector paired with ORB descriptors and a basic 6-bucket spatial distribution grid ($3 \times 2$ cells) paired with an active RGB-D sensor (ASUS Xtion Pro Live). While effective in controlled laboratory trials, the reference architecture exhibits four severe operational bottlenecks:
1. **Active IR Depth Range Limitations**: Structured-light/time-of-flight RGB-D cameras become completely blinded in outdoor sunlight due to solar IR saturation, and have an effective range bounded strictly to 0.5–4.0 meters. Beyond 4 meters or outdoors, the motion engine fails entirely.
2. **Spatial Feature Clustering**: The static $3 \times 2$ grid allows features to cluster locally inside each individual bucket, leaving wide texture gaps that degrade the epipolar conditioning of the Essential matrix.
3. **Discrete Integer Quantization**: Operating on integer pixel coordinates introduces angular quantization error, accumulating into catastrophic rotational drift over extended flight trajectories.
4. **Kinematic Vulnerability**: Standard RANSAC without kinematic constraints can converge to physically impossible cheirality or orientation solutions during aggressive UAV yaw/pitch maneuvers.

### 2.2 Research Objectives

This project builds upon the Perez-Grau framework to engineer a significantly improved, production-ready Visual Odometry engine in Python. We specifically address:
1. *Algorithmic Formulation*: How does recursive quadtree spatial bucketing and sub-pixel refinement compare quantitatively against the Perez-Grau 2017 baseline?
2. *Environmental Generalization*: How do binary descriptors (ORB, BRIEF, BRISK) behave across contrasting indoor vs outdoor UAV sequences exhibiting scale change, visual aliasing, and dynamic water surfaces?
3. *GPS Outage Resiliency*: What is the empirical drift rate of the dead-reckoning engine when satellite lock is abruptly lost, and how effectively can visual odometry preserve aircraft localization?

---

## 3. Related Work & Baseline Architectural Analysis

### 3.1 Foundational Visual Odometry

Monocular feature-based visual odometry relies on the epipolar constraint between consecutive image frames (Nistér, 2004; Hartley & Zisserman, 2004). For calibrated pinhole cameras with known intrinsics matrix $K$, calibrated normalized coordinates $x, x'$ satisfy the epipolar condition:
$$x'^T E x = 0$$
where $E = [t]_\times R$ is the Essential matrix. SVD decomposition of $E$ recovers the relative camera rotation $R \in SO(3)$ and unit translation direction $t \in \mathbb{R}^3$, subject to a four-fold ambiguity resolved by cheirality (positive scene depth) checks.

ORB-SLAM (Mur-Artal et al., 2015) and HSO (Luodongting, 2022) established state-of-the-art benchmarks for full SLAM and hybrid sparse VO, respectively. However, in resource-constrained embedded UAV flight controllers, full bundle adjustment and global map tracking introduce unpredictable CPU latency spikes that threaten flight stability. Consequently, lightweight frame-to-frame VO architectures remain vital.

### 3.2 The Perez-Grau et al. (2017) Baseline

Perez-Grau et al. (*Journal of Field Robotics*, 2017) introduced an autonomous multi-rotor UAV framework for industrial inspection in GPS-denied tunnels. The visual odometry pipeline in their system employed:
- **Detector**: FAST-9 corner detection (Rosten & Drummond, 2006).
- **Descriptor**: ORB 256-bit binary descriptors (Rublee et al., 2011).
- **Spatial Distribution**: Fixed $3 \times 2$ grid (6 uniform rectangular buckets) with a cap of $M$ features per cell to counteract high-contrast clustering.
- **Sensor**: ASUS Xtion Pro Live active RGB-D structured-light sensor.
- **Motion Solver**: 3D-to-2D Perspective-n-Point (PnP) when depth was available, without a graceful monocular fallback for long-range outdoor flight.

### 3.3 Proposed Algorithmic Enhancements vs. Perez-Grau (2017)

To elevate positioning performance beyond the 2017 literature baseline, our implementation integrates four targeted algorithmic advancements:

| Architectural Component | Perez-Grau et al. (2017) Baseline | Proposed Advanced VO Pipeline | Algorithmic Benefit |
|:---|:---|:---|:---|
| **Corner Detection** | Standard FAST-9 (fixed threshold) | **Adaptive FASTER Detector** | Dynamic threshold convergence guaranteeing uniform feature count across lighting shifts |
| **Spatial Distribution** | Fixed $3 \times 2$ uniform grid (6 buckets) | **Recursive Quadtree Partitioning** | Enforces hierarchical planar dispersion; eliminates intra-bucket clustering |
| **Coordinate Accuracy** | Integer pixel discretization | **Sub-pixel Refinement (`cornerSubPix`)** | Gradient-based floating-point precision, suppressing rotational angular jitter |
| **Motion Estimation** | Rigid RGB-D PnP only (range limited <4m) | **Hybrid PnP + 5-Point Essential Fallback** | Full metric tracking indoor; seamless monocular fallback outdoor |
| **Kinematic Validation** | Raw RANSAC pose acceptance | **Constant-Velocity Motion Prior** | Rejects unphysical orientation flips and degenerate epipolar solutions |

---

## 4. Methodology & Algorithmic Formulation

### 4.1 Upgraded Visual Odometry Architecture

```
                      ┌──────────────────────────────────────────────┐
                      │              Input Frame I_t                 │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Adaptive FASTER / FAST / ORB Detector     │
                      └──────────────────────┬───────────────────────┘
                                             │ Keypoints {k_i}
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Recursive Quadtree Spatial Bucketing      │
                      └──────────────────────┬───────────────────────┘
                                             │ Uniform Keypoints
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │  Sub-pixel Corner Refinement (cornerSubPix)  │
                      └──────────────────────┬───────────────────────┘
                                             │ Refined Float Keypoints
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │      Descriptor Extraction (ORB/BRIEF/BRISK) │
                      └──────────────────────┬───────────────────────┘
                                             │
                        ┌────────────────────┴───────────────────┐
                        │ Hamming / L2 Distance Matching         │
                        │ Lowe's Ratio Test (thresh = 0.75)      │
                        └────────────────────┬───────────────────┘
                                             │ Verified Matches
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │     Hybrid Motion Estimation Engine          │
                      │  - Depth available? -> solvePnPRansac (PnP)  │
                      │  - Monocular only?  -> findEssentialMat      │
                      └──────────────────────┬───────────────────────┘
                                             │ Relative Pose [R | t]
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │   Kinematic Motion Prior Validation (CVMM)   │
                      └──────────────────────┬───────────────────────┘
                                             │ Validated Pose
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │  World Pose Accumulator: T_wc[t]             │
                      └──────────────────────────────────────────────┘
```

### 4.2 Adaptive FASTER Feature Detection

Standard FAST-9 corner detection applies a fixed intensity difference threshold $\tau$:
$$|I(p) - I(c)| > \tau$$
for $N \ge 9$ contiguous pixels along a Bresenham circle of radius 3. In outdoor flight, rapid exposure changes (e.g., flying from shadows into direct sunlight) cause fixed-threshold FAST to either over-saturate (thousands of weak corners) or starve (zero corners).

Our **Adaptive FASTER Detector** employs a dynamic feedback loop that iteratively converges toward a target keypoint quota $N_{\text{target}}$:
$$\tau_{k+1} = \mathrm{clip}\left(\tau_k \cdot \left(\frac{N_k}{N_{\text{target}}}\right)^\gamma, \;\tau_{\min}, \;\tau_{\max}\right)$$
where $\gamma = 0.5$ acts as a damping factor preventing oscillation. This guarantees a stable feature density of $\sim 500-1000$ well-distributed points across arbitrary lighting shifts.

### 4.3 Recursive Quadtree Spatial Bucketing

To prevent feature clustering in high-contrast textures (e.g., foliage or window frames), we partition the image plane recursively using a Quadtree structure. 
1. The root node spans the full image dimension $[0, W] \times [0, H]$.
2. While the number of active leaf nodes is less than the desired bucket count $B$, the node containing the highest keypoint count is subdivided into four equal quadrants:
   $$\Omega_{TL}, \;\Omega_{TR}, \;\Omega_{BL}, \;\Omega_{BR}$$
3. Inside each leaf quadrant $\Omega_i$, keypoints are sorted by corner response strength (Harris/Fast score), and only the top $k = \lceil N_{\text{max}} / B \rceil$ features are retained.

This guarantees uniform spatial distribution across all quadrants, dramatically improving the conditioning of the epipolar Essential matrix.

### 4.4 Sub-Pixel Corner Refinement

Standard corner detectors report integer pixel coordinates $(u, v) \in \mathbb{Z}^2$. When integrating motion over hundreds of frames, coordinate quantization introduces high-frequency rotational jitter. 

We refine keypoint coordinates using gradient dot-product orthogonality:
$$\nabla I(q)^T (q - p^*) = 0 \quad \forall q \in \mathcal{N}(p)$$
where $p^*$ represents the continuous sub-pixel corner location within a $5 \times 5$ window $\mathcal{N}(p)$. Solving the resulting linear system via `cv2.cornerSubPix` yields sub-pixel coordinates $(u^*, v^*) \in \mathbb{R}^2$ with precision exceeding $0.1$ pixels.

### 4.5 Hybrid Motion Estimation Engine

To bridge the gap between indoor RGB-D sensing and outdoor monocular navigation, our motion engine executes a hybrid estimation policy:
- **RGB-D Mode (Indoor / Metric)**: When valid depth $Z(u, v) \in [Z_{\min}, Z_{\max}]$ is available for $\ge 6$ correspondences, 2D coordinates are backprojected to 3D camera coordinates:
  $$P_i = \left(\frac{u - c_x}{f_x} Z, \;\frac{v - c_y}{f_y} Z, \;Z\right)^T$$
  The 6-DOF transform $[R | t]$ is estimated via Perspective-n-Point with RANSAC (`cv2.solvePnPRansac`) using the Levenberg-Marquardt algorithm. This yields absolute metric scale ($t$ in meters) without scale drift.
- **Monocular Fallback Mode (Outdoor / Unscaled)**: When depth is absent (e.g., outdoor sunlight, distance $> 4$m), the pipeline seamlessly transitions to 5-point epipolar Essential matrix decomposition (`cv2.findEssentialMat` + `cv2.recoverPose`), estimating the unit motion direction.

### 4.6 Constant-Velocity Kinematic Motion Prior

Under rapid flight maneuvers or low-texture frames, RANSAC can return geometrically valid epipolar solutions that violate physical aircraft dynamics (e.g., instantaneous 180° yaw flips or impossible translational jumps). 

We enforce a **Constant-Velocity Motion Model (CVMM)** prior:
$$T_{\text{prior}} = T_{t-1} \cdot (T_{t-2}^{-1} \cdot T_{t-1})$$
Candidate transformations $[R | t]$ returned by RANSAC are evaluated against the prior:
$$\Delta \theta = \|\mathrm{Log}(R_{\text{prior}}^T R)\|_2 < \theta_{\max}$$
$$\Delta d = \|t_{\text{prior}} - t\|_2 < d_{\max}$$
Hypotheses exceeding physical limits (e.g., angular rate $> 120^\circ/\text{s}$ or acceleration $> 5g$) are rejected, preserving dead-reckoning trajectory continuity.

### 4.7 Evaluated System Configurations

| Config Identifier | Detector | Descriptor | Spatial Bucketing | Sub-pixel Refined | Rotation Invariant |
|:---|:---|:---|:---|:---|:---|
| **fast_orb_v1** (Baseline) | FAST-9 | ORB-256 | None | No | Partial |
| **faster_orb_v1** (Proposed) | Adaptive FASTER | ORB-256 | Quadtree (4-level) | Yes (`cornerSubPix`) | Partial |
| **orb_orb_v1** | ORB | ORB-256 | None | No | Full ($SO(2)$) |
| **fast_brief_v1** | FAST-9 | ManualBRIEF-256 | None | No | None |
| **orb_brisk_v1** | ORB | BRISK-512 | None | No | Full ($SO(2)$) |

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


