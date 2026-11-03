# Minor Project Viva & Presentation Defense Guide

**Project Topic:** A Computer Vision-Assisted GPS Navigation System for Robust Positioning in Signal-Denied Environments  
**Module:** Visual Odometry Pipeline  
**Student:** Ruchit Agrawal  
**Reference Paper:** Perez-Grau et al., *"An architecture for robust UAV navigation in GPS-denied areas"*, *Journal of Field Robotics* (2017)

---

## 1. Core Examiner Questions & Answers

### Q1: "Why is your Visual Odometry module not trained with deep learning? Where is the training dataset and loss function?"
> **Answer:**  
> "Classical Visual Odometry is an **algorithmic geometric inference engine**, not a data-driven neural network. It operates on deterministic principles of projective and epipolar geometry (Multiple View Geometry, Hartley & Zisserman, 2004). 
> 
> Motion is recovered on a frame-to-frame basis using feature detection (FAST/FASTER/ORB), binary descriptor matching (Hamming distance with Lowe's ratio test), 5-point Essential matrix estimation ($x'^T E x = 0$), and singular value decomposition ($E = [t]_\times R$). 
> 
> There are no trainable weights, backpropagation loops, or weight files. The ICL-NUIM and TartanAir datasets serve as benchmark test suites for empirical metric evaluation (ground-truth comparison via Umeyama Sim(3) alignment), not training sets. This ensures zero risk of data overfitting, deterministic execution latency, and mathematical explainability critical for safety-certified avionics."

---

### Q2: "What was the Perez-Grau (2017) paper doing, and what did your project improve beyond it?"
> **Answer:**  
> "Perez-Grau et al. (2017) presented an autonomous UAV system using a FAST-9 detector, ORB descriptors, and a static $3 \times 2$ grid (6 uniform buckets) coupled with an ASUS Xtion active RGB-D sensor. 
> 
> We identified four critical limitations in their perception engine and engineered targeted solutions:
> 1. **Active IR Depth Blindness**: Structured-light depth cameras are completely blinded by direct sunlight outdoors and limited to $<4$ meters. We designed a **Hybrid Motion Engine**: when depth is available, it solves metric 3D-to-2D PnP; when depth drops or sunlight saturates the sensor, it degrades gracefully to a 5-point monocular Essential matrix solver.
> 2. **Intra-Bucket Clustering**: Their static $3 \times 2$ grid allowed keypoints to cluster within each cell. We implemented **Recursive Quadtree Spatial Bucketing**, dividing the image hierarchically to enforce uniform planar dispersion.
> 3. **Integer Quantization Error**: FAST reports integer pixel coordinates, causing angular drift over long flights. We added **Sub-pixel Corner Refinement (`cornerSubPix`)**, achieving sub-0.1 pixel precision.
> 4. **Degenerate RANSAC Solutions**: We integrated a **Constant-Velocity Motion Model (CVMM)** prior to reject unphysical yaw flips or acceleration spikes."

---

### Q3: "How does monocular VO handle scale ambiguity, and how do you achieve metric positioning?"
> **Answer:**  
> "In pure monocular vision, the Essential matrix decomposition yields translation as a unit direction vector ($\|t\| = 1$); scale is inherently unobservable from 2D pixel motion alone.
> 
> In our project, metric scale is handled through three mechanisms:
> 1. **RGB-D PnP Mode**: When depth is available, 2D pixels are backprojected into 3D metric camera coordinates ($P_i = [X, Y, Z]^T$), enabling PnP to compute metric translations ($t$ in meters).
> 2. **Pre-Outage GPS Anchoring**: Before entering a GPS-denied zone, the last valid satellite fixes anchor the initial scale ($s$) and coordinate alignment.
> 3. **Sim(3) Umeyama Evaluation**: When benchmarking monocular sequences, we employ Umeyama Sim(3) similarity transformation to isolate trajectory *shape accuracy* from arbitrary scale scaling."

---

### Q4: "Why did your results achieve 100% tracking indoors but struggle on the TartanAir Ocean sequence?"
> **Answer:**  
> "This empirical contrast demonstrates the fundamental **static world assumption** of epipolar geometry.
> - **Indoor Structured Scenes (ICL-NUIM)**: Feature points correspond to rigid, stationary surfaces (walls, tables, cabinetry). The epipolar constraint holds strictly, yielding **100% tracking success** and **0.0231 m ATE RMSE** (2.3 cm error).
> - **Ocean UAV Flight (TartanAir Ocean)**: The sea surface consists of moving waves with specular sun glints. Feature points tracked across frames represent moving fluid rather than static land points. Consequently, epipolar consensus fails (0% tracking rate).
> 
> This proves precisely why visual odometry must be part of a multi-sensor system (GPS + IMU + VO), as single-sensor monocular VO cannot navigate over dynamic bodies of water."

---

### Q5: "What were your exact quantitative results during a simulated GPS outage?"
> **Answer:**  
> "We simulated a sudden GPS carrier loss at Frame 15 during an indoor flight:
> - Total dead-reckoning distance traveled: **3.144 meters**.
> - Mean positional drift during outage: **0.039 meters (3.9 cm)**.
> - Maximum terminal drift: **0.072 meters (7.2 cm)**.
> - Normalized drift rate: **2.28% of distance traveled**.
> 
> A drift rate under 2.5% confirms that the visual odometry module can safely sustain aircraft localization through GPS dropouts and tunnel passages without loss of control."

---

## 2. Key Architecture Metrics Cheatsheet

| Parameter | Value |
|:---|:---|
| Best Indoor ATE RMSE | **0.0231 m (2.3 cm)** via FASTER+ORB+Quadtree |
| Real-time Throughput | **31.5–32.4 FPS** (FAST+ORB) / **18.6–19.8 FPS** (FASTER+ORB) |
| Dead-Reckoning Drift Rate | **2.28%** of distance traveled |
| Unit Test Suite Coverage | **100% pass rate** across **144 test cases** |
| Benchmark Scope | 20 runs (5 feature configs $\times$ 4 multi-environment sequences) |

