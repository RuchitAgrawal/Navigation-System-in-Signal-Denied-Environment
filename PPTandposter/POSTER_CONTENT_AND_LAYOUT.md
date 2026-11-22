# 🎓 Academic Seminar Poster Guide & Content Blueprint
## "A Computer Vision-Assisted GPS Navigation System for Robust Positioning in Signal-Denied Environments"

> **Institution:** Department of Computer Engineering, School of Technology, Pandit Deendayal Energy University (PDEU)  
> **Academic Year:** 2026–27  
> **Students:** Ruchit Agrawal (23BCP183) & Joy Patel (23BCP049)  
> **Guide:** Prof. Azriel Henry, Assistant Professor  
> **Interactive Printable Poster File:** [`poster.html`](file:///c:/Users/joypa/OneDrive/Desktop/MINOR_PROJECT/poster.html)

---

## 🎨 Poster Visual Design & Styling Reference

This poster follows the exact structural layout, visual hierarchy, color palette, and card styling of the official PDEU departmental poster template:

- **Header Banner:** Pale lavender/purple linear gradient (`#d3c4ed` to `#bda4e2`), dark purple text (`#2c1a4d`), official university emblem on the left, project title and student details in the center, and "School of Technology, PDEU" on the right.
- **Section Headers:** Full-width and split-column purple banner strips (`#c3aee2`) with bold uppercase lettering.
- **Grid Layout:** 
  - **Top Row (2 Columns):** Brief Motivation (Left) | Objective (Right)
  - **Middle Row (Full Width Banner):** Methodology & Full-Width Pipeline Flowchart (Fig. 1)
  - **Third Row (3 Columns):** Expected & Empirical Results (Left) | Live Demo Flow (Center) | Benchmark Plots (Right: Fig. 2 & Fig. 3)
  - **Bottom Row (2 Columns):** Outcomes with 4 Metric Badges + 4 Thumbnails (Left) | Budget Utilization, Tech Stack & Academic References (Right)
- **Typography:** High-readability clean sans-serif typography (`Segoe UI` / Helvetica) with monospace code snippets and KaTeX mathematical notation.

---

## 📑 Section-by-Section Poster Content

---

### [HEADER BANNER]

```text
[LEFT LOGO]
PANDIT DEENDAYAL ENERGY UNIVERSITY
A RESERVOIR OF KNOWLEDGE

[CENTER TITLE BLOCK]
A COMPUTER VISION-ASSISTED GPS NAVIGATION SYSTEM FOR ROBUST POSITIONING IN SIGNAL-DENIED ENVIRONMENTS
Ruchit Agrawal (23BCP183) • Joy Patel (23BCP049)
Guide: Prof. Azriel Henry, Assistant Professor, Department of Computer Engineering, PDEU

[RIGHT BLOCK]
School of Technology
PDEU, Gandhinagar
```

---

### [SECTION 1: MOTIVATION & OBJECTIVE] (Split 2-Column Banner)

#### Left Column: Brief Motivation
- **The GPS Failure Problem:** Satellite positioning degrades or fails catastrophically indoors, underground, in urban canyons, forested valleys, and during active RF electronic jamming.
- **Vulnerability of Autonomous Systems:** Drones, warehouse robots, and defense rovers relying strictly on GPS experience complete loss of situational awareness upon signal loss.
- **Inadequacy of Alternative Sensors:** Inertial Measurement Units (IMUs) accumulate unbounded drift ($d \propto t^2$) within seconds; active beacon infrastructure (UWB/LiDAR) is expensive and unavailable in uncharted territory.
- **Vision as the Resilient Solution:** Monocular Visual Odometry (VO) provides an entirely passive, self-contained, jam-proof positioning sensor using only a single commodity camera.

#### Right Column: Objective
- **Autonomous 6-DoF Pose Tracking:** Estimate camera displacement and heading continuously between consecutive image frames without external positioning aids.
- **Robust Feature Extraction & Distribution:** Implement Adaptive FASTER detection with QuadTree spatial bucketing to eliminate edge clustering and adapt to abrupt lighting changes.
- **Hybrid Rotation/Translation Solver:** Overcome epipolar zero-baseline degeneracy during in-place camera turning by seamlessly combining Homography and Essential Matrix estimation.
- **Empirical Multi-Config Benchmarking:** Evaluate 5 detector-descriptor combinations on the ICL-NUIM photographic benchmark across ATE RMSE, RPE, and FPS.
- **GPS Outage Simulation & Live HUD:** Build an interactive, real-time live webcam dashboard proving sub-2.5% dead-reckoning drift during simulated satellite outages.

---

### [SECTION 2: METHODOLOGY] (Full-Width Banner)

#### Left Column: How the Pipeline Works
1. **Frame Preprocessing:** Monocular camera frames ($I_{t-1}, I_t$) are converted to grayscale and normalized. Lens distortion is corrected via calibrated intrinsic matrix $K$.
2. **Feature Detection & QuadTree Bucketing:** Adaptive FASTER dynamically adjusts corner detection thresholds (target $\approx 500$ keypoints). QuadTree spatial partitioning guarantees uniform feature spread across all image quadrants.
3. **Sub-Pixel Refinement & Descriptors:** Coordinates are refined to sub-pixel accuracy via `cv2.cornerSubPix`. 256-bit steered ORB or 512-bit scale-invariant BRISK descriptors are generated.
4. **Matching & Epipolar Consensus:** Brute-Force Hamming matching is filtered using Lowe's Ratio Test ($\le 0.75$). Outliers are eliminated via RANSAC geometric consensus.
5. **Hybrid Pose Recovery (H vs E):**
   - **If pure rotation:** Planar Homography ($H = K R K^{-1}$) decomposes rotation via SVD ($R = U V^T, t = 0$).
   - **If 3D translation:** 5-point Essential Matrix ($E = [t]_\times R$) recovers $R$ and unit translation direction $t$ with chirality validation.
6. **Kinematic Prior & Trajectory Accumulation:** Constant-velocity motion model rejects unnatural direction reversals; global pose is integrated as $T_w^{(t)} = T_w^{(t-1)} \cdot (T_{rel}^{(t)})^{-1}$.

> **Why Hybrid?** Monocular Essential Matrix breaks down ($E \approx 0$) during in-place camera turning due to zero baseline ($t \approx 0$). Our dual Homography / Essential solver detects flow parallax to dynamically switch solvers, eliminating tracking loss.

#### Right Column: Architecture Diagram
- **Figure 1:** End-to-end Monocular Visual Odometry Architecture — from camera ingestion and QuadTree extraction to hybrid Homography/Essential pose recovery and GPS outage dead-reckoning.

---

### [SECTION 3: EXPECTED RESULTS & LIVE DEMO] (3-Column Grid)

#### Column 1: Findings & Theory
- **Benchmark Comparison (1,017 Frames on ICL-NUIM):**

| Configuration | ATE RMSE (m) | RPE Rot (deg) | Throughput (FPS) | Key Characteristic |
|---|:---:|:---:|:---:|---|
| **FAST + ORB** | 0.2219 | 0.55° | **48.22 FPS** | **Highest Throughput** (P95: 28.71 ms) |
| **FAST + BRIEF** | 0.2302 | 0.55° | 32.95 FPS | Fast binary matching, translation only |
| **ORB + ORB** | 0.2775 | 0.56° | 32.75 FPS | Standard OpenCV baseline |
| **ORB + BRISK** | **0.1732** | 0.96° | 30.11 FPS | **Highest Accuracy** (37.6% error reduction) |
| **FASTER + Quad** | **0.0380** | 0.28° | 36.50 FPS | Custom Adaptive Implementation (Synthetic) |

- **Key Mathematical Theory:**
  - **Epipolar Geometry:** $x'^T E x = 0$, where $E = [t]_\times R$. Decomposed via SVD into 4 possible solutions; chirality cheirality check enforces positive 3D camera depth.
  - **Umeyama Sim(3) Alignment:** Solves optimal scale $s^*$, rotation $R^*$, translation $t^*$ in closed form minimizing $\sum ||y_i - (s^* R^* x_i + t^*)||^2$.
  - **Drift Metric:** Measured as $e_{\text{drift}} = \frac{\Delta p}{d_{\text{total}}} \times 100\% = \mathbf{2.28\%}$.
- **Industrial & Defense Relevance:**
  - **Electronic Jamming Defense:** Anti-drone RF jammers sever GPS instantly; monocular VO operates immune to electromagnetic interference.
  - **Logistics & Autonomous Flight:** Eliminates need for factory floor QR markers or expensive LiDAR arrays.

#### Column 2: Try It: Live Demo Flow
1. **Launch Real-Time Dashboard:**
   Run script in terminal with live laptop / USB webcam:
   ```bash
   python scripts/live_dashboard.py --camera 0
   ```
2. **Real-Time Tracking & Motion Detection:**
   Webcam feeds live video; system extracts ~500 FAST corners, tracks optical flow vectors, and updates top-down X-Z bird's-eye map.
   - Badges: `[TRACKING]` `[YAW: +24°]` `[48.2 FPS]`
3. **Simulate Instant GPS Dropout (Press 'G'):**
   Press **[G]** to toggle GPS loss. HUD flashes RED alert. Visual odometry dead-reckoning seamlessly maintains continuous 3D positioning!
   - Badges: `[GPS: DENIED (VO MODE)]` `[DRIFT: 2.28%]`
- **Offline Fallback Demo:** Run `python scripts/run_demo.py` for an instant 5-second synthetic sequence test without needing a camera!

#### Column 3: Visual Output Figures
- **Figure 2:** 3D/2D Bird's-Eye Trajectory Overlay — Ground Truth (Green) vs Monocular Visual Odometry (Blue dashed) after Sim(3) alignment.
- **Figure 3:** GPS Outage Takeover — GPS signal cuts at Frame 15; VO dead-reckoning tracks true trajectory with low 2.28% metric drift.

---

### [SECTION 4: OUTCOMES & BUDGET UTILIZATION] (Split Banner)

#### Left Column: Outcomes
- **Metric Highlights (4 Pill Cards):**
  1. **48.22 FPS:** Real-Time Speed (comfortably exceeding 30 Hz requirement).
  2. **Hybrid H / E:** Dual Motion Solver eliminating pure rotation failure.
  3. **2.28% Drift:** GPS Outage Accuracy across simulated dropout corridors.
  4. **170 Tests:** Passing Automated Verification across geometry and pipelines.
- **Visual Thumbnails (4 Cards):**
  - **Fig. 4:** Inlier Matches (Consecutive video frames with Lowe filtering).
  - **Fig. 5:** Trajectory Fit (Estimated VO vs Ground Truth overlay).
  - **Fig. 6:** Scale Drift (Local scale factor vs frame index).
  - **Fig. 7:** Live HUD UI (3-Panel live camera and top-down map).

#### Right Column: Budget Utilization & Tech Stack
- **Budget:** No hardware cost incurred; system is a software-only prototype functioning on standard commodity laptop webcams without dedicated GPUs.
- **Tech Stack:** Python 3.10/3.11, OpenCV 4.x (Vision Core), NumPy (Matrix Kinematics), SciPy (Optimization & SVD), Matplotlib (Trajectory Plotting), Pytest (Test Harness).
- **Academic References:**
  - [1] F. J. Perez-Grau, R. Caballero, et al., "An architecture for robust UAV navigation in GPS-denied areas," *Journal of Field Robotics*, vol. 34, no. 5, pp. 909–936, 2017.
  - [2] A. Handa, T. Whelan, et al., "A benchmark for RGB-D visual odometry, 3D reconstruction and SLAM," in *IEEE ICRA*, 2014.
  - [3] E. Rublee, V. Rabaud, et al., "ORB: An efficient alternative to SIFT or SURF," in *IEEE ICCV*, 2011.
  - [4] S. Umeyama, "Least-squares estimation of transformation parameters between two point patterns," *IEEE TPAMI*, vol. 13, no. 4, 1991.

---

## 🖨️ How to View, Print, or Export to PDF

1. **In Any Web Browser:**
   - Double-click or open [`poster.html`](file:///c:/Users/joypa/OneDrive/Desktop/MINOR_PROJECT/poster.html) in Google Chrome, Microsoft Edge, or Firefox.
2. **To Export as High-Resolution PDF or Print for Seminar:**
   - Press **`Ctrl + P`** (Print).
   - Destination: **Save as PDF** (or select plotter printer).
   - Layout: **Portrait** (or Landscape depending on page fit).
   - Paper Size: **A1** or **A2** (or "Fit to Page").
   - Options: Check **"Background graphics"** (ensures all purple banners and card styling appear crisp).
   - Click **Save**.
