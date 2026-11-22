# How It Works: A Complete Walkthrough of the Visual Odometry System

This document explains **every step** of the project in detail: what happens, which file does it,
how it is calculated (with real numbers from this repo), and why it was designed that way.

It is written to be read top to bottom, like a textbook chapter. Each step builds on the previous one.
Every claim here was checked against the actual source code in `src/`, `experiments/` and `scripts/`.

---

## Table of Contents

1. [The problem, in plain words](#1-the-problem-in-plain-words)
2. [The core idea of visual odometry](#2-the-core-idea-of-visual-odometry)
3. [Repository map: which folder does what](#3-repository-map-which-folder-does-what)
4. [The full journey of one run (call graph)](#4-the-full-journey-of-one-run-call-graph)
5. [Step 0: Configuration (YAML to Python objects)](#5-step-0-configuration-yaml-to-python-objects)
6. [Step 1: Loading the dataset and ground truth](#6-step-1-loading-the-dataset-and-ground-truth)
7. [Step 2: The camera model (intrinsic matrix K)](#7-step-2-the-camera-model-intrinsic-matrix-k)
8. [Step 3: Image preprocessing](#8-step-3-image-preprocessing)
9. [Step 4: Feature detection (FAST, ORB, Adaptive FASTER)](#9-step-4-feature-detection-fast-orb-adaptive-faster)
10. [Step 5: Spatial bucketing and sub-pixel refinement (optional)](#10-step-5-spatial-bucketing-and-sub-pixel-refinement-optional)
11. [Step 6: Feature description (BRIEF, ORB, BRISK)](#11-step-6-feature-description-brief-orb-brisk)
12. [Step 7: Feature matching (Hamming + Lowe ratio)](#12-step-7-feature-matching-hamming--lowe-ratio)
13. [Step 8: Pose estimation (Essential matrix + RANSAC)](#13-step-8-pose-estimation-essential-matrix--ransac)
14. [Step 9: Motion model sanity check](#14-step-9-motion-model-sanity-check)
15. [Step 10: Building the trajectory (pose chaining)](#15-step-10-building-the-trajectory-pose-chaining)
16. [Failure handling: every way a frame can fail](#16-failure-handling-every-way-a-frame-can-fail)
17. [Evaluation: how every number in the results table is calculated](#17-evaluation-how-every-number-in-the-results-table-is-calculated)
18. [The four configurations: what changes and why results differ](#18-the-four-configurations-what-changes-and-why-results-differ)
19. [Reading the benchmark results](#19-reading-the-benchmark-results)
20. [GPS outage simulation](#20-gps-outage-simulation)
21. [The live webcam dashboard](#21-the-live-webcam-dashboard)
22. [The synthetic demo sequence](#22-the-synthetic-demo-sequence)
23. [Output files: what each one contains](#23-output-files-what-each-one-contains)
24. [Commands cheat sheet](#24-commands-cheat-sheet)
25. [Tests](#25-tests)
26. [Known gaps between code, report and README](#26-known-gaps-between-code-report-and-readme)
27. [Glossary](#27-glossary)

---

## 1. The problem, in plain words

GPS tells a device where it is by listening to satellites. Indoors, underground, in tunnels, or when
someone jams the signal, those satellite signals do not arrive, so GPS stops working.

A robot or drone still needs to know **where it is** and **which way it is facing** at every moment.
This project answers: *can we estimate the path of a moving camera using only the images it sees?*

That technique is called **monocular visual odometry (VO)**:

- **Visual**: it uses images.
- **Odometry**: it measures motion step by step (like a car's odometer counting wheel turns).
- **Monocular**: it uses just one camera (no stereo pair, no depth sensor).

---

## 2. The core idea of visual odometry

Imagine walking through a room while taking photos. Between two consecutive photos, everything in the
scene appears to shift slightly. *How* it shifts tells you how you moved:

- If everything slides left, you probably turned right.
- If things near the centre spread outward, you moved forward.
- Near objects shift more than far objects (this is called **parallax**).

The pipeline turns that intuition into maths, for every pair of consecutive frames:

```
 Frame t-1 ─┐
            ├─► find distinctive points ─► describe them ─► match them between frames
 Frame t ───┘                                                        │
                                                                     ▼
            estimate how the camera rotated (R) and in which direction it moved (t)
                                                                     │
                                                                     ▼
            add this small motion onto the running total ─► full trajectory
```

**One important limitation** runs through the whole project: with one camera you can find the
*direction* of movement but **not the distance**. A small room filmed from close up and a large room
filmed from far away can produce identical images. This is called **scale ambiguity**, and it is why
the evaluation uses Sim(3) alignment (Section 17.4).

---

## 3. Repository map: which folder does what

```
Navigation-System-in-Signal-Denied-Environment/
├── configs/
│   ├── default.yaml                 Global defaults (RANSAC, matching, tracking thresholds)
│   ├── datasets/*.yaml              Where a dataset lives + its camera intrinsics
│   └── experiments/*.yaml           One file per detector+descriptor combination
│
├── src/                             The actual library (importable package)
│   ├── datasets/                    Read images + ground truth from disk
│   │   ├── base_dataset.py          Common interface: len(), [i], load_image_gray(), camera.K
│   │   ├── icl_nuim.py              ICL-NUIM / TUM-format loader + timestamp association
│   │   ├── tartanair.py             TartanAir loader (NED coordinate conversion)
│   │   └── synthetic.py             Synthetic data helper
│   ├── features/                    Finding and describing keypoints
│   │   ├── detector.py              FAST, ORB, Adaptive FASTER
│   │   ├── descriptor.py            BRIEF (+ ManualBRIEF fallback), ORB, BRISK
│   │   ├── config.py                Validates combinations, builds FeatureConfig
│   │   ├── extractor.py             One call: image → keypoints + descriptors
│   │   ├── bucketing.py             Grid (3×2) and Quadtree keypoint spreading
│   │   └── subpixel.py              cv2.cornerSubPix refinement
│   ├── matching/matcher.py          Brute-force Hamming matching + Lowe ratio test
│   ├── geometry/
│   │   ├── essential.py             Essential matrix + RANSAC + recoverPose
│   │   ├── pose.py                  PoseAccumulator, FrameStatus, FrameDiagnostics
│   │   ├── transforms.py            4×4 pose maths, quaternions, validity checks
│   │   ├── pnp.py                   PnP with depth (exists, NOT used by the pipeline)
│   │   ├── fundamental.py           Fundamental matrix utilities
│   │   └── triangulation.py         3D point triangulation utilities
│   ├── odometry/
│   │   ├── pipeline.py              ★ The main loop: VOPipeline.run()
│   │   ├── motion_model.py          Rejects physically impossible jumps
│   │   ├── tracker.py               Success-rate and FPS statistics
│   │   └── filter.py                Optional trajectory smoothing (post-processing)
│   ├── evaluation/
│   │   ├── ate.py                   Umeyama alignment + Absolute Trajectory Error
│   │   ├── rpe.py                   Relative Pose Error
│   │   ├── drift.py                 Local scale over time
│   │   └── metrics.py               Builds the summary CSV row
│   └── visualization/               Plots (trajectory, matches, scale, report)
│
├── experiments/
│   ├── runner.py                    ★ Runs ONE (config, dataset) pair end to end
│   └── benchmark.py                 Loops runner over many configs × datasets
│
├── scripts/                         Command-line tools (demo, live dashboard, GPS outage, ...)
├── data/demo_sequence/              40-frame synthetic sequence (ships with the repo)
├── results/                         csv/, figures/, logs/ written by runs
└── tests/                           pytest suite (170 test functions)
```

---

## 4. The full journey of one run (call graph)

This is exactly what happens, in order, when the benchmark runs one configuration:

```
experiments/benchmark.py :: run_benchmark(benchmark_yaml)
 └─ for each experiment yaml × dataset yaml:
     experiments/runner.py :: run_experiment()
      ├─ load_yaml(experiment) , load_yaml(dataset)
      ├─ load_icl_nuim_from_config()                  → ICLNUIMDataset (1,017 frames)
      ├─ config_from_yaml()  → build_feature_config() → FeatureConfig (detector + descriptor objects)
      ├─ VOPipeline(feature_config, thresholds...)    → creates FeatureExtractor + MotionModel
      ├─ pipeline.run(dataset)                        ★ the per-frame loop (Sections 8–16)
      │    for idx = 1 … 1016:
      │      load_image_gray → extractor.extract → match_and_filter
      │      → estimate_pose (E + RANSAC + recoverPose) → motion_model.validate
      │      → accumulator.add_relative_pose  OR  accumulator.add_failed_pose
      ├─ compute_ate(est_poses, gt_poses, "sim3")     (Section 17.4)
      ├─ compute_rpe(est_poses, gt_poses, delta=1)    (Section 17.6)
      ├─ compute_tracking_report(diagnostics)         (Section 17.1)
      ├─ save_per_frame_csv, save_tum_format, build_summary_row, JSON log
      └─ return summary row
 └─ save_summary_csv(all rows) → results/csv/benchmark_summary.csv
```

**Key design rule** (stated in `pipeline.py`): ground truth is **never** used to estimate motion. It is
only loaded afterwards, for evaluation. The VO works blind, exactly like it would on a real robot.

---

## 5. Step 0: Configuration (YAML to Python objects)

Nothing is hard-coded in the experiments. Each run is described by two YAML files.

### 5.1 Experiment YAML (what algorithm to use)

Example: `configs/experiments/orb_brisk.yaml`

```yaml
experiment_id: orb_brisk_v1
detector:   { name: ORB, nfeatures: 2000, scale_factor: 1.2, nlevels: 8,
              edge_threshold: 31, patch_size: 31, fast_threshold: 20 }
descriptor: { name: BRISK, thresh: 30, octaves: 3, pattern_scale: 1.0 }
matching:   { method: hamming, cross_check: false, ratio_threshold: 0.75 }
ransac:     { method: RANSAC, threshold: 1.0, confidence: 0.999, max_iterations: 2000 }
tracking:   { min_keypoints: 8, min_matches: 8, min_inlier_ratio: 0.10 }
```

### 5.2 Dataset YAML (what data to read)

`configs/datasets/icl_nuim.yaml` gives the folder (`data/icl_nuim/living_room_traj1_loop`), the camera
intrinsics (fx, fy, cx, cy), the timestamp tolerance (0.02 s), and an optional frame range.

### 5.3 How YAML becomes objects (`src/features/config.py`)

`build_feature_config()` does four things:

1. **Upper-cases the names** (`"orb"` → `"ORB"`).
2. **Checks the pair is allowed.** Only these combinations exist in `VALID_COMBINATIONS`:

   | Detector | Descriptor | Used in the 4-config benchmark? |
   |---|---|---|
   | FAST | BRIEF | ✅ `fast_brief_v1` |
   | FAST | ORB | ✅ `fast_orb_v1` |
   | ORB | ORB | ✅ `orb_orb_v1` |
   | ORB | BRISK | ✅ `orb_brisk_v1` |
   | FASTER | ORB | experimental (`faster_orb_v1`) |
   | FASTER | BRIEF | experimental (`faster_brief_v1`) |

   Anything else (for example FAST + BRISK) raises a `ValueError` immediately, before any image is read.
3. **Creates the OpenCV objects.** Special case: for ORB + ORB, **one** `cv2.ORB_create()` object is used
   as both detector and descriptor (this enables a faster single-call path, Section 11.5).
4. **Picks the distance type.** All descriptors here are binary, so the norm is always `cv2.NORM_HAMMING`.

### 5.4 Where every threshold comes from

`experiments/runner.py` reads each value from the YAML and falls back to a default if missing:

| Parameter | Default | Meaning | Used in |
|---|---|---|---|
| `ratio_threshold` | 0.75 | Lowe ratio test cut-off | Section 12.3 |
| `cross_check` | false | Bidirectional matching instead of ratio test | Section 12.4 |
| `ransac.threshold` | 1.0 px | Max error for a match to count as an inlier | Section 13.4 |
| `ransac.confidence` | 0.999 | Probability RANSAC finds a clean sample | Section 13.4 |
| `ransac.max_iterations` | 2000 | Hard cap on RANSAC loops | Section 13.4 |
| `min_keypoints` | 8 | Fewer → `FAILED_FEATURES` | Section 16 |
| `min_matches` | 8 | Fewer → `FAILED_MATCHES` | Section 16 |
| `min_inlier_ratio` | 0.10 | Lower → `FAILED_RANSAC` | Section 16 |
| `use_motion_model` | **true** | Kinematic sanity check on | Section 14 |
| `bucketing.strategy` | none | `none` / `grid` / `quadtree` | Section 10 |
| `refinement.subpixel` | false | Sub-pixel corner refinement | Section 10.3 |
| `preprocessing.clahe` | false | Contrast equalisation | Section 8 |

The four benchmark YAMLs do not set bucketing, sub-pixel or CLAHE, so those are **off** for the
reported results. The motion model is **on** (default `true`).

---

## 6. Step 1: Loading the dataset and ground truth

File: `src/datasets/icl_nuim.py`

### 6.1 The ICL-NUIM sequence

- Sequence: `living_room_traj1_loop` (a camera moving around a rendered living room)
- **1,017** RGB images, each 640 × 480 pixels
- A ground-truth file giving the true camera pose at each timestamp

### 6.2 The file formats (TUM format)

`rgb.txt`: one line per image, `timestamp filename`
```
0.000000 rgb/0000.png
0.100000 rgb/0001.png
```

`groundtruth.txt`: one line per pose, `timestamp tx ty tz qx qy qz qw`
```
0.100000 0.029928 0.006393 0.090000 0.009928 0.001796 0.000018 0.999949
```
- `tx ty tz` = camera position in metres
- `qx qy qz qw` = camera orientation as a **quaternion** (a 4-number way to store a rotation)

Each ground-truth line is converted into a **4×4 pose matrix** (Section 15.1):
`quat_to_rotation(qx,qy,qz,qw)` gives the 3×3 rotation, then `make_pose(R, t)` assembles the 4×4 matrix.

### 6.3 Timestamp association (why 1,017 frames but 965 GT poses)

Images and ground-truth poses are not guaranteed to have identical timestamps. `_associate()` does this
for each image:

```
diffs     = | every GT timestamp − this image's timestamp |
best      = the smallest diff
if best ≤ 0.02 s:  frame.gt_pose = that GT pose
else:              frame.gt_pose = None        (no ground truth for this frame)
```

In the benchmark, **965** of the 1,017 frames received a ground-truth pose. The other frames get `None`
and are simply skipped during evaluation. The VO still processes all 1,017 images.

### 6.4 Loading pixels

`BaseDataset.load_image_gray(i)` calls `cv2.imread(path, cv2.IMREAD_GRAYSCALE)`.
The result is a 480 × 640 array of numbers 0 (black) to 255 (white). Colour is discarded because all
detectors and descriptors here work on brightness only.

---

## 7. Step 2: The camera model (intrinsic matrix K)

To turn pixel positions into geometry, the code needs to know how the camera projects the 3D world
onto the image. That is stored in the **intrinsic matrix K**:

```
      ┌ fx   0   cx ┐     ┌ 481.20     0    319.50 ┐
K  =  │  0  fy   cy │  =  │    0    480.00  239.50 │      (ICL-NUIM living room)
      └  0   0    1 ┘     └    0       0       1   ┘
```

- **fx, fy (focal length in pixels):** how strongly the lens magnifies. Larger = more zoomed in.
- **cx, cy (principal point):** the pixel where the camera's optical axis hits the image,
  roughly the image centre (640/2 ≈ 319.5, 480/2 ≈ 239.5).
- ICL-NUIM is rendered, so there is **no lens distortion** (k1 = k2 = p1 = p2 = 0).

### 7.1 What K is used for

A 3D point at camera coordinates (X, Y, Z) appears at pixel:
```
u = fx · X/Z + cx
v = fy · Y/Z + cy
```
Going backwards, a pixel (u, v) becomes a **normalised ray direction**:
```
x = (u − cx) / fx
y = (v − cy) / fy          →  ray = (x, y, 1)
```
**Worked example:** pixel (400, 300) → x = (400 − 319.5)/481.2 = 0.167, y = (300 − 239.5)/480 = 0.126.
So that pixel looks along direction (0.167, 0.126, 1), about 9.5° right of and 7.2° below centre.

The Essential matrix (Section 13) works with these normalised rays, which is why K is passed to
`cv2.findEssentialMat` and `cv2.recoverPose`.

---

## 8. Step 3: Image preprocessing

File: `src/features/extractor.py`

1. **Greyscale** (already done when loading).
2. **CLAHE** (optional, off in the benchmark): *Contrast Limited Adaptive Histogram Equalisation*.
   The image is split into 8 × 8 tiles and contrast is stretched inside each tile, with a clip limit
   (2.0) so noise is not amplified too much. This helps in dark or washed-out scenes by making
   corners easier to detect.

---

## 9. Step 4: Feature detection (FAST, ORB, Adaptive FASTER)

A **feature** (or **keypoint**) is a small, distinctive spot in the image, usually a **corner**, that
can be found again in the next frame. Flat walls are useless (every patch looks the same); edges are
ambiguous along their length; corners are unique in both directions.

Each keypoint is stored as a `cv2.KeyPoint` with: position `pt=(x, y)`, `response` (corner strength),
`size`, `angle` (orientation, or −1 if none), and `octave` (pyramid level).

### 9.1 FAST-9 (Features from Accelerated Segment Test)

File: `src/features/detector.py` → `cv2.FastFeatureDetector_create(threshold=20, nonmaxSuppression=True)`

**How FAST decides if pixel p is a corner:**

```
               16  1  2
            15          3
          14              4
          13      p       5        16 pixels on a circle of radius 3 around p
          12              6
            11          7
               10  9  8
```

1. Take the brightness of the centre pixel, I(p).
2. Look at the 16 pixels on the circle.
3. A circle pixel is **"brighter"** if I > I(p) + t, **"darker"** if I < I(p) − t, where t = **20**.
4. If **9 or more contiguous** circle pixels are all brighter, or all darker, p is a corner.

**Worked example:** I(p) = 100, t = 20. A circle pixel must be > 120 (brighter) or < 80 (darker).
If pixels 3, 4, 5, 6, 7, 8, 9, 10, 11 are all around 150, that is 9 contiguous brighter pixels, so p is a corner.

**Why it is fast:** a quick pre-test checks pixels 1, 5, 9, 13 first. If fewer than 3 of those 4 pass,
p cannot be a corner and is rejected after only 4 comparisons. Most pixels are rejected this way.

**Non-maximum suppression (NMS):** a real corner triggers FAST at several neighbouring pixels. NMS
gives each candidate a score (`response`, how strongly it exceeds the threshold) and keeps only the
local maximum, so one corner = one keypoint.

**Capping at 2,000 (`_LimitedDetector`):** FAST has no built-in limit and can return 5,000+ corners
in a textured image. The wrapper sorts by `response` (strongest first) and keeps the top 2,000.

**FAST limitations:** no orientation (angle = −1) and no scale (it only looks at the full-resolution image).

### 9.2 ORB detector (Oriented FAST + pyramid)

File: `src/features/detector.py` → `cv2.ORB_create(nfeatures=2000, scaleFactor=1.2, nlevels=8, ...)`

ORB improves FAST in three ways.

**(a) Image pyramid for scale.** The image is shrunk repeatedly by a factor of 1.2 to make 8 levels:

| Level | Scale | Image size (approx.) |
|---|---|---|
| 0 | 1.000 | 640 × 480 |
| 1 | 1/1.2 = 0.833 | 533 × 400 |
| 2 | 0.694 | 444 × 333 |
| 3 | 0.579 | 370 × 278 |
| 4 | 0.482 | 309 × 231 |
| 5 | 0.402 | 257 × 193 |
| 6 | 0.335 | 214 × 161 |
| 7 | 0.279 | 179 × 134 |

FAST runs on **every** level. A corner that looks big when the camera is close will still be found
at a smaller level when the camera moves away. This gives *partial* scale invariance, but also costs
time: 8 detections instead of 1. **This is the main reason FAST-based configs are faster.**

**(b) Harris ranking.** ORB scores FAST corners with the Harris corner measure and keeps the best
2,000 across all levels (distributed over levels in proportion to their area).

**(c) Orientation by intensity centroid.** For each keypoint, ORB computes the "centre of mass" of
brightness in a circular patch (radius ≈ 15 px):
```
m10 = Σ x · I(x,y)      m01 = Σ y · I(x,y)
angle θ = atan2(m01, m10)
```
The arrow from the keypoint to that brightness centroid defines which way the corner "points".
If the camera rolls by 30°, θ also changes by 30°, so the descriptor can be rotated to match
(Section 11.2).

`edgeThreshold = 31` and `patchSize = 31`: keypoints closer than ~31 px to the border are not used,
because their description patch would fall off the image.

### 9.3 Adaptive FASTER (experimental, used by the live dashboard)

File: `src/features/detector.py` → `AdaptiveFASTERDetector`

Plain FAST uses a fixed threshold of 20. In a dark room that may find only 100 corners; in a busy
scene it may find 10,000. Adaptive FASTER **adjusts the threshold each frame** to hit a target count.

```
target = 2000   min_ok = 0.6 × target = 1200   max_ok = 1.6 × target = 3200
thresh = last frame's threshold (starts at 20)

repeat up to 3 times:
    kps = FAST(thresh)
    if 1200 ≤ len(kps) ≤ 3200:  stop (good)
    if too few and thresh > 7:   thresh = max(7,  thresh − max(3, 30% of thresh))
    if too many and thresh < 60: thresh = min(60, thresh + max(3, 30% of thresh))
remember thresh for next frame; keep strongest 2000
```

**Worked example:** threshold 20 finds 800 corners (below 1,200). Lower it by max(3, int(6.0)) = 6 → 14.
At 14 it finds 1,900: within range, stop. Next frame starts at 14.

> Note: the code comment in `detector.py` itself says real FASTER (Rosten et al., 2010) uses a
> machine-learned decision tree. This is an adaptive-threshold FAST, inspired by that idea.

---

## 10. Step 5: Spatial bucketing and sub-pixel refinement (optional)

Off in the 4-config benchmark; on in `faster_orb.yaml` and the live dashboard.

### 10.1 Why spread features out?

If all 2,000 corners sit on one bookshelf, the pose estimate depends on one small region and becomes
unstable. Spreading keypoints across the whole image gives better geometry.

### 10.2 Grid bucketing (Perez-Grau 2017 style)

`distribute_grid()` splits the image into **3 × 2 = 6 buckets** (each 213 × 240 px for 640 × 480).
Quota per bucket = 2000 // 6 = **333**. Each bucket keeps its 333 strongest corners. If some buckets
are nearly empty (a blank wall), the leftover capacity is filled with the strongest remaining corners anywhere.

### 10.3 Quadtree bucketing (ORB-SLAM2 style)

`distribute_quadtree()`:
1. Start with one node = the whole image, holding all keypoints.
2. Repeatedly split the **densest** nodes into 4 quadrants (NW, NE, SW, SE). Empty children are dropped.
3. Stop when there are ≥ 2,000 nodes, or nodes are too small (each side must stay > 2 × 12 = 24 px), or nothing can split.
4. From each final node keep **only the single strongest** keypoint.
5. If still under 2,000, top up with the strongest remaining keypoints.

Result: dense areas get many small cells (one point each), sparse areas get large cells, so the
points end up evenly spread. If there are already ≤ 2,000 keypoints, nothing is changed.

### 10.4 Sub-pixel refinement

`refine_keypoints_subpixel()` calls `cv2.cornerSubPix` with a 5 × 5 half-window (11 × 11 search area),
up to 30 iterations, stopping when the shift is < 0.01 px. It uses image gradients to find the exact
corner position, e.g. (215, 140) → (215.37, 139.82). Since 1 pixel of error at 481 px focal length is
about 0.12°, sub-pixel accuracy reduces angular error in the pose.

---

## 11. Step 6: Feature description (BRIEF, ORB, BRISK)

A keypoint's position alone cannot be matched (the camera moved, so positions changed). Each keypoint
needs a **fingerprint** of the patch around it: the **descriptor**.

All three descriptors here are **binary**: a string of 0s and 1s, each bit answering one yes/no
question about the patch, *"is pixel A darker than pixel B?"*.

### 11.1 BRIEF (used in FAST + BRIEF)

File: `src/features/descriptor.py`

The code first tries OpenCV's BRIEF (`cv2.xfeatures2d`, which needs `opencv-contrib-python`). In this
project's environment that module is not available, so the code falls back to its own
**`ManualBRIEF`**. That is why the results CSV labels the descriptor `ManualBRIEF-Gaussian-256`.

**How ManualBRIEF works (exact code behaviour):**

1. **Once, at start-up:** draw 256 random test pairs with seed 42, from a Gaussian distribution
   centred on the keypoint with σ = patch_size / 5 = 48 / 5 = **9.6 px**, clipped to ±24 px:
   ```
   pair k:  A_k = (x1_k, y1_k)   B_k = (x2_k, y2_k)      for k = 1 … 256
   ```
   Gaussian sampling means most tests are near the centre (most informative), a few further out.
2. **For each keypoint:** if it is within 24 px of any border, **drop it** (its 49 × 49 patch would leave the image).
3. Cut the 49 × 49 patch around the keypoint.
4. For each of the 256 pairs: `bit_k = 1 if I(A_k) < I(B_k) else 0`.
5. Pack 256 bits into **32 bytes** with `np.packbits`.

**Worked example (first 8 tests):**
```
I(A) :  52  130   90   44  200   61  77  140
I(B) :  80  100   95   40  210   20  90  139
A<B ?   1    0    1    0    1    0   1    0     → byte 0b10101010 = 170
```

**Limitation:** the test positions are fixed relative to the image axes. If the camera rolls 30°,
the same physical corner gives completely different bits. BRIEF therefore works well only when
rotation between frames is small, which is the case for consecutive video frames.

### 11.2 ORB descriptor (rotated BRIEF, used in FAST + ORB and ORB + ORB)

`cv2.ORB_create()`. Also 256 tests, 32 bytes, but:
- The 256 test pairs were **learned** (chosen to be uncorrelated and highly variable), not random.
- Before testing, the pattern is **rotated by the keypoint's angle θ** (Section 9.2c). So if the
  image rotates, the pattern rotates with it and the bits stay the same: **rotation invariant**.
- ORB's `compute()` also removes keypoints too close to the border, so the keypoint list returned
  can be shorter than the list given in (the code always uses the returned list).

### 11.3 BRISK descriptor (used in ORB + BRISK)

`cv2.BRISK_create(thresh=30, octaves=3, patternScale=1.0)`.
- Samples **60 points on 4 concentric circles** around the keypoint, each point slightly blurred
  (outer circles are blurred more, to cope with noise).
- **Long-distance pairs** are used to estimate the patch's dominant gradient direction (orientation).
- **Short-distance pairs** (512 of them), rotated by that orientation, give the bits.
- Result: **512 bits = 64 bytes**, twice as long as ORB/BRIEF.

Longer descriptor = more distinctive (fewer accidental look-alikes), but more time to compute and
compare. This is exactly the accuracy-vs-speed trade-off seen in the results.

### 11.4 Descriptor summary

| | BRIEF (Manual) | ORB | BRISK |
|---|---|---|---|
| Bits / bytes | 256 / 32 | 256 / 32 | 512 / 64 |
| Test pattern | random Gaussian (σ = 9.6) | learned | concentric circles |
| Rotation invariant | ❌ | ✅ (intensity centroid) | ✅ (long-pair gradients) |
| Border removed | ≤ 24 px | ≈ 31 px | pattern-dependent |
| Relative cost | cheapest | cheap | most expensive |

### 11.5 The extractor's two code paths

`FeatureExtractor.extract()`:

```
if ORB+ORB and no bucketing and no subpixel:            ("joint ORB fast path")
    kps, descs = orb.detectAndCompute(gray)              one OpenCV call
    detect_ms = describe_ms = total / 2                  (time is split evenly; cannot be measured separately)
else:                                                    (all other combinations)
    kps   = detector.detect(gray)
    kps   = bucketing + subpixel (if enabled)
    kps, descs = descriptor.compute(gray, kps)           may DROP border keypoints
```

**Efficiency detail:** each frame is described **once**. In `pipeline.py`, after processing frame t,
its keypoints and descriptors are stored as "previous" for frame t+1, so they are never recomputed.

---

## 12. Step 7: Feature matching (Hamming + Lowe ratio)

File: `src/matching/matcher.py`

Now we have ~2,000 descriptors in frame t−1 and ~2,000 in frame t. We need to pair them up.

### 12.1 Hamming distance

For binary strings, distance = **number of bits that differ**. Computed as XOR then count the 1s:
```
A      = 1011 0110
B      = 1001 0011
A XOR B= 0010 0101   → three 1s → Hamming distance = 3
```
For a 256-bit descriptor, distance is 0 (identical) to 256 (opposite). Similar patches give small
distances. XOR + popcount is extremely fast on CPUs, which is why binary descriptors suit real time.

### 12.2 Brute-force k-nearest-neighbour search

`cv2.BFMatcher(NORM_HAMMING).knnMatch(desc_prev, desc_curr, k=2)`:
for **each** descriptor in frame t−1, compare it with **every** descriptor in frame t
(2,000 × 2,000 = 4 million comparisons) and return the **best** and **second-best** match.

That is why `n_raw_matches` in the CSV is about **4,000** = 2,000 keypoints × 2 candidates each.

### 12.3 Lowe's ratio test (the default filter)

A match is accepted only if the best is **clearly better** than the runner-up:
```
accept  if  d_best < 0.75 × d_second
```
**Worked examples:**
- d_best = 20, d_second = 60 → 20 < 45 ✅ unambiguous, keep.
- d_best = 40, d_second = 45 → 40 < 33.75 ❌ two candidates look almost the same (repeated texture,
  like tiles or bookshelf), so the match is unreliable. Reject.

This one test removes most wrong matches. In the demo sequence's first frame pair, **4,000 raw**
candidates → **649** pass the ratio test.

### 12.4 Cross-check (alternative, off in the 4-config benchmark)

With `cross_check: true` the code uses `BFMatcher(crossCheck=True).match()`: keep A↔B only if B's best
match in frame t−1 is also A. In this code the two filters are **mutually exclusive**: if cross-check
is on, the ratio test is skipped (see `match_and_filter`). Only `faster_orb.yaml` turns it on.

### 12.5 Converting matches to coordinates

`matches_to_point_arrays()` turns each match into two pixel coordinates:
`pts_prev[i] = keypoint in frame t−1`, `pts_curr[i] = keypoint in frame t`. These two N × 2 arrays are
all the geometry step needs.

**Gate:** if fewer than **8** matches survive, the frame is marked `FAILED_MATCHES` and pose estimation
is skipped.

---

## 13. Step 8: Pose estimation (Essential matrix + RANSAC)

File: `src/geometry/essential.py`

This is the mathematical heart of the project: given N matched point pairs, find how the camera moved.

### 13.1 What we want: R and t

- **R** (3 × 3 rotation matrix): how the camera turned between frames.
- **t** (3-vector): the direction the camera moved.

Convention from `cv2.recoverPose`: a 3D point in the previous camera's coordinates, p_prev, appears in the
current camera's coordinates as
```
p_curr = R · p_prev + t
```

### 13.2 Epipolar geometry: the key constraint

A 3D point P, the previous camera centre, and the current camera centre form a triangle. All three
lie on one plane (the **epipolar plane**). The rays from both cameras to P must lie on that plane.
That geometric fact gives one equation per matched pair:

```
x_currᵀ · E · x_prev = 0          (the epipolar constraint)
```
where x_prev and x_curr are the **normalised** ray directions (Section 7.1) and E is the
**Essential matrix**:
```
E = [t]ₓ · R          with   [t]ₓ = ┌  0   −tz   ty ┐
                                    │  tz   0   −tx │   (cross-product matrix of t)
                                    └ −ty   tx   0  ┘
```
E is 3 × 3 but has only **5 degrees of freedom** (3 for rotation + 2 for the translation direction;
the length of t is unknowable, Section 2). So a minimum of **5 matched points** determines E. OpenCV
uses **Nistér's five-point algorithm**. That is why `estimate_pose` refuses to run with fewer than 5 points.

### 13.3 Why RANSAC is needed

Even after the ratio test, some matches are wrong (outliers). A single wrong match can ruin a
least-squares solution. **RANSAC** (Random Sample Consensus) ignores outliers by voting:

```
best = none
repeat:
    1. pick 5 random matches
    2. solve the 5-point problem → candidate E (can give up to 10 solutions; each is tested)
    3. for every match, compute its error against E (Sampson distance, in pixels)
    4. inliers = matches with error < 1.0 px          (ransac.threshold)
    5. if more inliers than best → best = this E
    6. update how many iterations are still needed (see below)
until enough iterations, or 2000 iterations           (ransac.max_iterations)
return best E and its inlier mask
```

### 13.4 How many iterations? (with real numbers)

If a fraction **w** of matches are inliers, the chance that 5 random picks are **all** inliers is w⁵.
To be **p = 99.9 %** sure at least one sample was clean:
```
N = log(1 − p) / log(1 − w⁵)
```
| Inlier ratio w | w⁵ | Iterations N |
|---|---|---|
| 0.8 | 0.328 | ≈ 18 |
| 0.5 | 0.03125 | ≈ 218 |
| 0.3 | 0.00243 | ≈ 2,840 → capped at **2,000** |

OpenCV updates w as it finds better models, so with good matches (demo: 538/649 = **82.9 %** inliers)
RANSAC finishes in a few dozen iterations. That is why pose estimation takes only ~7–11 ms per frame.

### 13.5 Inlier ratio gate

```
inlier_ratio = n_inliers / n_matches          demo frame 1: 538 / 649 = 0.829
if inlier_ratio < 0.10 → FAILED_RANSAC
```
If fewer than 10 % of matches agree on one motion, the scene is probably degenerate (motion blur,
a moving object, a textureless wall), so the frame is rejected rather than trusted.

### 13.6 Recovering R and t from E (`cv2.recoverPose`)

Decomposing E with SVD (singular value decomposition) gives **four** possible (R, t) answers:
```
(R1, +t)   (R1, −t)   (R2, +t)   (R2, −t)
```
Only one is physically real. **Cheirality check:** for each candidate, triangulate the inlier points in 3D;
the correct candidate is the one where the points are **in front of both cameras** (positive depth).
The others put points behind the camera, which is impossible. `recoverPose` returns the winner.

The returned **t always has length 1**. It is a direction only.

### 13.7 Final validity check

`is_valid_rotation(R)` checks that R is a true rotation:
- det(R) = 1 (within 1e−6), meaning no reflection
- Rᵀ · R = I (within 1e−6), meaning axes stay perpendicular and unit length

If any step fails, the frame gets `FAILED_POSE` (or `FAILED_RANSAC`), and no motion is added.

---

## 14. Step 9: Motion model sanity check

File: `src/odometry/motion_model.py` (on by default)

RANSAC occasionally returns a mathematically valid but **physically absurd** answer, e.g. the camera
suddenly flipping 120° or reversing direction. A real camera on a robot cannot do that in 1/30 s.
`ConstantVelocityMotionModel` compares each new motion with the **last accepted** one.

### 14.1 Rotation-change check
```
R_diff = R_lastᵀ · R_new
angle  = arccos( (trace(R_diff) − 1) / 2 )        (in degrees)
reject if angle > 45°
```
The formula `arccos((trace − 1)/2)` gives the angle of any rotation matrix.
**Example:** a 10° rotation has trace = 1 + 2·cos 10° = 2.970 → (2.970 − 1)/2 = 0.985 → arccos = 10°. ✓

### 14.2 Direction-change check
```
cos φ = (t_last · t_new) / (|t_last| · |t_new|)
reject if φ > 90°      ("unnatural direction reversal")
```

### 14.3 What happens next
- The **first** motion is always accepted (nothing to compare with).
- If valid: the model stores this motion (`update`) and the pose is accumulated.
- If invalid: the frame is marked `FAILED_POSE` and the previous pose is carried forward.

> The model also computes a `speed_ratio` (max of new/old and old/new length) with a 4.0 limit, but
> the current code does **not** reject on it. Since monocular t always has length 1, the ratio would be 1 anyway.

---

## 15. Step 10: Building the trajectory (pose chaining)

File: `src/geometry/pose.py` (`PoseAccumulator`) and `src/geometry/transforms.py`

### 15.1 The 4×4 pose matrix

A camera pose (where it is + which way it faces) is stored as one 4 × 4 matrix:
```
         ┌ r11 r12 r13 tx ┐
T_wc  =  │ r21 r22 r23 ty │      R = rotation (3×3),  (tx,ty,tz) = camera position in the world
         │ r31 r32 r33 tz │
         └  0   0   0   1 ┘
```
**T_wc** means "camera → world": a point in camera coordinates times T_wc gives world coordinates.
The **last column is the camera's position**. That is what gets plotted and compared with ground truth.

Why 4 × 4? It lets rotation **and** translation be combined by one matrix multiplication.

### 15.2 Inverting a pose cheaply
```
T⁻¹ = ┌ Rᵀ   −Rᵀ·t ┐        (invert_pose: no general matrix inverse needed,
      └ 0       1   ┘         because a rotation's inverse is its transpose)
```

### 15.3 The chaining formula
```
start:          T_wc[0] = I            (identity: frame 0 is the world origin, facing forward)
each success:   T_rel   = make_pose(R, t)                  (prev-camera → curr-camera)
                T_wc[t] = T_wc[t−1] · inverse(T_rel)
each failure:   T_wc[t] = T_wc[t−1]                         (carry forward, no movement)
```
**Why the inverse?** `recoverPose` describes how points move from the previous camera frame into the
current one. We want the opposite: where the *current camera* sits inside the *previous* camera's
frame. That is the inverse transform. Multiplying onto the running total takes it into world coordinates.

### 15.4 Worked example (two steps, straight line)

Step 1: the camera moves straight forward, no rotation. recoverPose gives R = I, t = (0, 0, −1)
(points appear to move toward the camera, so their z decreases).
```
inverse(T_rel) = [ I | −Iᵀ·(0,0,−1) ] = [ I | (0,0,1) ]
T_wc[1] = I · that  →  position (0, 0, 1)
```
Step 2: same motion again → position (0, 0, 2).

So the camera is 2 **units** forward. Not 2 metres: units of unknown size (Section 17.4 explains
how the evaluation finds the real scale).

### 15.5 Saving the trajectory

`save_tum_format()` writes one line per frame in the same format as the ground truth:
`timestamp tx ty tz qx qy qz qw` (rotation converted back to a quaternion with SciPy).
Output: `results/csv/<config>__<dataset>__<sequence>_trajectory.txt`.

---

## 16. Failure handling: every way a frame can fail

Every frame gets exactly one status (`FrameStatus` in `pose.py`) and one diagnostics row. A failure
**never crashes** the run; the pose is carried forward.

```
frame t
  │
  ├─ keypoints(prev) < 8  or  keypoints(curr) < 8 ───────► FAILED_FEATURES
  ├─ good matches < 8 ────────────────────────────────────► FAILED_MATCHES
  ├─ < 5 points / E is None / recoverPose error ──────────► FAILED_POSE
  ├─ inlier ratio < 0.10 ─────────────────────────────────► FAILED_RANSAC
  ├─ R not a valid rotation ──────────────────────────────► FAILED_POSE
  ├─ motion model: angle > 45° or direction > 90° ───────► FAILED_POSE
  └─ otherwise ───────────────────────────────────────────► SUCCESS  (pose accumulated)

frame 0 ─────────────────────────────────────────────────► SKIPPED  (no previous frame)
```

**Why tracking is only 44–54 % on ICL-NUIM** (from the report's analysis): the living room has
repeated textures (the ratio test rejects ambiguous matches), motion blur during fast turns (fewer
corners and matches), and partial occlusions. Rejected frames add **zero** motion, so the trajectory
"pauses" and then jumps when tracking resumes. That is a major source of ATE error.

---

## 17. Evaluation: how every number in the results table is calculated

Files: `src/odometry/tracker.py`, `src/evaluation/ate.py`, `rpe.py`, `drift.py`, `metrics.py`.
All examples below use the real numbers from `results/csv/benchmark_summary.csv`.

### 17.1 Tracking success %
```
success_rate = SUCCESS frames / (total frames − SKIPPED frames)
```
FAST + BRIEF: 466 / (1017 − 1) = 466 / 1016 = **45.87 %** ✓ (failed = 550; 466 + 550 = 1016)
ORB + BRISK: 549 / 1016 = **54.04 %** ✓

`is_degenerate = success_rate < 50 %`. That is why the CSV marks FAST + BRIEF and FAST + ORB as
`is_degenerate = True`. It is a warning flag, not a crash.

### 17.2 Timing: mean, median, P95 latency
For every frame except the skipped first one, `total_time_ms` is measured with `time.perf_counter()`
from the start of image loading to the end of pose estimation.
```
mean   = average of all frame times
median = middle value (P50)
P95    = 95 % of frames finished faster than this
```
FAST + ORB: mean **21.47 ms**, median **20.96 ms**, P95 **28.71 ms**.
P95 under 33.3 ms means even slow frames meet a 30 frames-per-second budget.

### 17.3 FPS (and why it is not exactly 1000 / mean)
```
per-frame FPS = 1000 / frame_time_ms
mean_fps      = average of the per-frame FPS values
```
1000 / 21.47 = 46.6, but the reported mean FPS is **48.22**. The difference is because the code
averages the per-frame FPS values: fast frames (often quick failures, e.g. 10 ms = 100 FPS) pull the
average up more than slow frames pull it down. Both numbers are correct; they answer slightly different questions.

### 17.4 ATE: Absolute Trajectory Error (with Sim(3) alignment)

**Problem:** the estimated trajectory is in unknown units, in an arbitrary starting orientation,
starting at (0,0,0). The ground truth is in metres, in the dataset's world frame. Comparing them
directly is meaningless.

**Solution:** find the best similarity transform (scale s, rotation R, translation t) that lays the
estimated path on top of the true path, **then** measure the leftover error. This is **Umeyama's
algorithm (1991)**, implemented in `umeyama_alignment()`:

```
Input:  est positions p_i   (N × 3)       GT positions q_i   (N × 3)      N = 965

1. centroids:         μ_p = mean(p_i)            μ_q = mean(q_i)
2. centre both:       p'_i = p_i − μ_p           q'_i = q_i − μ_q
3. spread of est:     σ²  = mean( |p'_i|² )
4. cross-covariance:  H   = (1/N) Σ p'_i · q'_iᵀ          (3 × 3)
5. SVD:               H   = U · D · Vᵀ
6. reflection guard:  S   = diag(1, 1, sign(det(V·Uᵀ)))
7. rotation:          R   = V · S · Uᵀ
8. scale:             s   = (Σ D_k · S_kk) / σ²
9. translation:       t   = μ_q − s · R · μ_p

aligned_i = s · R · p_i + t
error_i   = | aligned_i − q_i |                 (metres)
ATE RMSE  = sqrt( mean(error_i²) )
```
Also reported: mean, median and standard deviation of `error_i`.

**Intuition for each step:**
- Steps 1–2 move both point clouds so their centres sit at the origin (removes translation).
- Steps 4–7 find the rotation that best lines up the two centred clouds. SVD gives the optimum in
  closed form, no iteration. Step 6 stops the answer from being a mirror image.
- Step 8 finds how much to stretch or shrink the estimate.
- Step 9 moves the result back to where the ground truth is.

**Reading the scale numbers:** the recovered scales are tiny, for example **0.00563** for ORB + BRISK.
Every successful frame adds a unit-length step, but the real camera moves only millimetres between
frames. So s ≈ 0.0056 means "1 estimated unit ≈ 5.6 mm of real motion". The report's 0.005–0.010
range is exactly this.

**Why RMSE and not just mean?** Squaring punishes large errors more, so a trajectory with a few big
jumps scores worse than one with uniform small errors.

ORB + BRISK: RMSE **0.1732 m**, median **0.1675 m** (mean 0.1669 m, std 0.0463 m).

> SE(3) mode (`--alignment se3`) fixes s = 1 (rotation + translation only). That is only meaningful
> when the scale is known, e.g. stereo or RGB-D. The benchmark uses Sim(3).

### 17.5 Why ATE is the headline metric for monocular VO

ATE measures how well the **shape** of the whole path matches after removing the parts monocular VO
cannot know (global position, orientation, scale). It is the standard metric of Sturm et al. (2012)
used across the visual SLAM literature.

### 17.6 RPE: Relative Pose Error

RPE checks **local** accuracy: is each frame-to-frame step right?
```
for each i (delta = 1):
    Q_est = inverse(T_est[i]) · T_est[i+1]        estimated step
    Q_gt  = inverse(T_gt[i])  · T_gt[i+1]         true step
    E     = inverse(Q_est) · Q_gt                  error between them
    trans_err = | translation part of E |
    rot_err   = arccos( (trace(rotation part of E) − 1) / 2 )     in degrees
RPE = RMSE over all pairs
```
**RPE rotation is meaningful** (angles have no scale problem): ≈ 0.55° per frame for FAST and ORB
configs, 0.96° for ORB + BRISK.

> ⚠️ **RPE translation in this codebase is not scale-corrected.** `compute_rpe` compares the raw
> estimated steps (length 1 unit, or 0 on a failed frame) with true steps (a few millimetres). So
> "RPE Trans 0.67–0.74 m" in the table does not mean metres of error. You can see it in the medians
> in the CSV: **0.003** for the FAST configs (most frames failed → step 0 ≈ true step of ~3 mm) and
> **0.997** for the ORB configs (most frames succeeded → step 1 vs ~3 mm). Treat RPE-translation as
> not comparable. Use ATE for translation and RPE for rotation.

### 17.7 Scale drift over time (`drift.py`)
```
for each frame i (window w = 10, or 5 in the demo figure):
    local_scale_i = (estimated path length over last w steps) / (true path length over last w steps)
```
If VO were perfect apart from one fixed scale, this would be a flat line. Changes over time are
**scale drift**, a known weakness of monocular VO. That is what `scale_drift.png` plots.

---

## 18. The four configurations: what changes and why results differ

Everything after the descriptor (matching, RANSAC, motion model, chaining, evaluation) is
**identical** for all four. Only detection and description change.

| | `fast_brief_v1` | `fast_orb_v1` | `orb_orb_v1` | `orb_brisk_v1` |
|---|---|---|---|---|
| Detector | FAST-9, t = 20, top 2000 | FAST-9, t = 20, top 2000 | ORB pyramid (8 levels, ×1.2) | ORB pyramid (8 levels, ×1.2) |
| Detector scale | single level | single level | 8 levels | 8 levels |
| Keypoint orientation | none | FAST gives none; ORB's `compute` handles it (see `features/config.py` note) | intensity centroid | intensity centroid |
| Descriptor | ManualBRIEF 256-bit | ORB 256-bit | ORB 256-bit | BRISK 512-bit |
| Rotation invariant descriptor | ❌ | ✅ | ✅ | ✅ |
| Code path | detect → compute (pure NumPy loop) | detect → compute | **single detectAndCompute** | detect → compute |

### 18.1 Why FAST + ORB is fastest (48.22 FPS)
- FAST runs once on one 640 × 480 image; ORB detection runs FAST on 8 pyramid levels plus Harris scoring.
- ORB description is optimised C++.
- FAST + BRIEF uses the same detector but is slower (32.95 FPS) because **ManualBRIEF is a Python
  loop over every keypoint**. That is an implementation cost, not a property of BRIEF itself
  (OpenCV's compiled BRIEF would be much faster).

### 18.2 Why ORB + BRISK is most accurate (0.1732 m) but slowest (30.11 FPS)
- 512-bit descriptors are more distinctive, so fewer ambiguous matches are thrown away by the ratio
  test and more frames keep enough matches: highest tracking, **54.04 %**.
- More successful frames means fewer "pauses" in the trajectory, so its shape matches the truth better.
- BRISK's sampling pattern is more expensive to compute, and 64-byte comparisons take twice as long as 32-byte ones.

### 18.3 The descriptor matters more than the detector
ORB + ORB → ORB + BRISK changes only the descriptor, and ATE drops from 0.2775 to 0.1732 m:
```
(0.2775 − 0.1732) / 0.2775 = 0.1043 / 0.2775 = 37.6 % lower error
```

### 18.4 Experimental configurations in `configs/experiments/` (not in the 4-config results)

| File | What it adds | Status |
|---|---|---|
| `faster_orb.yaml` | Adaptive FASTER + Quadtree + sub-pixel + cross-check | Runs; not part of the reported 4-config benchmark |
| `faster_orb_grid.yaml` | Same, with 3×2 grid bucketing | Runs; experimental |
| `faster_brief.yaml` | Adaptive FASTER + BRIEF | Runs; experimental |
| `fast_orb_pnp.yaml` | Intended PnP with depth | ⚠️ `use_pnp` is accepted but **never used** by `pipeline.py` |
| `gps_outage.yaml` | Settings for the outage experiment | See Section 20 |

---

## 19. Reading the benchmark results

From `results/csv/benchmark_summary.csv` (ICL-NUIM living room, 1,017 frames, 965 GT poses, Sim(3)):

| Config | ATE RMSE (m) | ATE median (m) | RPE rot (°) | Tracking % | Mean FPS | Mean / P50 / P95 (ms) | Sim(3) scale |
|---|---|---|---|---|---|---|---|
| FAST + BRIEF | 0.2302 | 0.2112 | 0.5544 | 45.87 | 32.95 | 31.39 / 29.69 / 42.11 | 0.00660 |
| FAST + ORB | 0.2219 | 0.2212 | 0.5571 | 44.59 | **48.22** | **21.47 / 20.96 / 28.71** | 0.00995 |
| ORB + ORB | 0.2775 | 0.2466 | 0.5599 | 52.26 | 32.75 | 35.70 / 28.18 / 63.00 | 0.00501 |
| ORB + BRISK | **0.1732** | **0.1675** | 0.9610 | **54.04** | 30.11 | 38.83 / 30.57 / 66.52 | 0.00563 |

**How to talk about it:**
- **No single winner.** FAST + ORB wins speed; ORB + BRISK wins accuracy and tracking.
- **Speed:** FAST + ORB is 48.22 / 30.11 = 1.60×, i.e. about 60 % faster than ORB + BRISK.
- **Accuracy cost of speed:** FAST + ORB's ATE is 0.2219 / 0.1732 = 1.28×, i.e. 28 % higher.
- **Choice depends on the use:** a fast drone needs FAST + ORB's low latency; offline mapping or
  precision landing benefits from ORB + BRISK.
- **Curious result:** ORB + ORB has *better* tracking than FAST + ORB (52 % vs 45 %) but *worse* ATE.
  ATE depends on *which* frames fail (a long gap during a turn hurts much more than scattered failures),
  not only on how many.
- **Pipeline-stage timings** (from the ORB + ORB demo-sequence per-frame CSV): detect + describe
  ~6–11 ms, match ~6–7 ms, pose ~6–11 ms per frame. Matching is a big share because it is brute force (4 million comparisons).

---

## 20. GPS outage simulation

Files: `scripts/evaluate_gps_outage.py`, `experiments/gps_outage.py`. Figure: `results/figures/gps_outage_orb_orb_demo.png`.

This simulates the real use case: GPS works, then suddenly disappears, and VO must carry on alone.

```
1. GPS phase (frames 0 … start−1):
     use ground truth as "GPS". Fit Sim(3) (Umeyama) using ONLY these frames.
     This is like calibrating VO's scale and heading while GPS is still available.
2. Outage (frames start … end):
     apply that fixed transform to the VO positions. No more ground truth is used for correction.
3. For each outage frame:
     drift_i     = | aligned VO position − true position |
     distance_i  = true distance travelled since the outage began
4. Report:  max drift, mean drift, final drift,
            drift % = final drift / total outage distance × 100
```

The repo's figure uses the **40-frame synthetic demo sequence** with the outage over frames 15–35:
the VO-only path (red dashed) follows the true path (grey) and the error grows gradually (to ≈ 0.15 m
by frame 35). This is the expected behaviour of dead reckoning: error accumulates because every step
adds a small mistake and nothing corrects it.

---

## 21. The live webcam dashboard

File: `scripts/live_dashboard.py`. Run: `python scripts/live_dashboard.py --camera 0`

It runs a variant of the pipeline on live video and draws a 3-panel window: camera with features,
top-down trajectory map, and a status bar.

### 21.1 Setup differences from the benchmark
| | Benchmark | Live dashboard |
|---|---|---|
| Detector | FAST / ORB | **Adaptive FASTER**, target **500** keypoints (speed) |
| Descriptor | per config | ORB |
| Bucketing / sub-pixel | off | **Quadtree + sub-pixel on** |
| Camera K | calibrated | **guessed**: focal = image width (e.g. 1280 px), centre = image centre, unless `--focal-length` is given |
| Motion model | 45° / 90° | relaxed: **65° / 180°** (hand-held cameras turn fast) |

### 21.2 Per-frame decision logic
```
match features (ratio 0.75)                 < 8 matches → "FEW MATCHES"
median_flow = median pixel movement of matched points

if median_flow < 1.8 px:
    "STATIONARY": camera is still; keep pose, do NOT estimate (avoids drifting from noise)

else:
    fit a Homography H with RANSAC (2.5 px)
    if ≥ 65 % of points fit H  and  median reprojection error ≤ 1.8 px:
        R = decompose_homography_rotation(H)      (pure rotation case)
        if rotation > 0.35°:  "ROTATING", update pose with t = 0
    if not pure rotation:
        Essential matrix + recoverPose (as in Section 13)
        step length = clip(median_flow × 0.0035, 0.012, 0.060)   ← heuristic scale
        t = unit t × step length                 "TRACKING"
```

### 21.3 Why the homography branch exists
When the camera only **turns in place**, there is no translation, so **t ≈ 0** and E = [t]ₓR ≈ 0:
the Essential matrix is undefined (degenerate). In that case every point moves according to a
**homography** H = K · R · K⁻¹, which depends only on rotation. `decompose_homography_rotation`:
```
M = K⁻¹ · H · K               (should equal R up to a scale)
M = M / cbrt(det M)           (normalise so det = 1)
U, Σ, Vᵀ = SVD(M);  R = U · Vᵀ    (nearest true rotation)
if det R < 0: R = −R
```

### 21.4 Honest notes on the dashboard
- **Scale is a heuristic.** `median_flow × 0.0035` (clamped to 1.2–6 cm per frame) is a rule of thumb,
  not a measurement, so map distances are approximate.
- **The G key only changes the display.** It toggles the "GPS DENIED" banner and red border. There
  is no GPS input; the VO runs the same in both modes. It demonstrates that the system never relied on GPS.
- Other keys: **R** resets, **S** saves a screenshot, **+ / −** raise or lower the starting FAST
  threshold by 5 (range 5–60) and rebuild the detector, **Q/Esc** quits.

---

## 22. The synthetic demo sequence

File: `scripts/generate_demo_data.py` → `data/demo_sequence/` (40 frames). Run all demos: `python scripts/run_demo.py`.

How it is made:
1. Place **600 random 3D landmarks** in a box in front of the camera (x ∈ [−3.5, 3.5], y ∈ [−2.5, 2.5],
   z ∈ [1.5, 7] m), each drawn as a random marker shape, size and colour (seed 12345).
2. Move a virtual camera along a smooth forward path with a gentle turn (0.1 s per frame).
3. Project each landmark into the image using K (fx = fy = 480, cx = 320, cy = 240) and draw it.
4. Write `rgb/0000.png …`, `rgb.txt`, `groundtruth.txt` in TUM format.

Because the true path is known exactly and there is no blur, the demo is perfect for checking the
pipeline works end to end without downloading the real dataset. The figures `feature_matches_sample.png`,
`trajectory_comparison.png`, `scale_drift.png` and `gps_outage_orb_orb_demo.png` all come from this demo.

---

## 23. Output files: what each one contains

| File | Content |
|---|---|
| `results/csv/benchmark_summary.csv` | One row per (config, dataset): all metrics in Section 17 |
| `results/csv/<run>_frames.csv` | One row per frame (columns below) |
| `results/csv/<run>_trajectory.txt` | Estimated poses, TUM format |
| `results/logs/<run>.json` | Same as the summary row, as JSON |
| `results/figures/*.png` | Plots |

Per-frame CSV columns:

| Column | Meaning |
|---|---|
| `frame_idx` | Frame number |
| `status` | SUCCESS / FAILED_* / SKIPPED (Section 16) |
| `n_keypoints_prev`, `n_keypoints_curr` | Keypoints in frame t−1 and t |
| `n_raw_matches` | All knn candidates (≈ 2 × keypoints) |
| `n_filtered_matches` | After Lowe ratio test |
| `n_ransac_inliers`, `ransac_inlier_ratio` | Agreeing with the final E |
| `detect_time_ms` | Detection + description time |
| `describe_time_ms` | Always 0 in the CSV: description time is folded into `detect_time_ms` |
| `match_time_ms`, `pose_time_ms`, `total_time_ms` | Stage timings |

Demo frame 1 example: 2000 / 2000 keypoints → 4000 raw → 649 filtered → 538 inliers (82.9 %), 26.5 ms.

---

## 24. Commands cheat sheet

```bash
pip install -e .                                   # install the package
python scripts/download_datasets.py               # fetch datasets (see docs/dataset_setup.md)
python scripts/verify_dataset_integrity.py        # check files are complete

# one configuration on one dataset
python scripts/run_vo.py -e configs/experiments/orb_brisk.yaml -d configs/datasets/icl_nuim.yaml

# the 4-config ICL-NUIM benchmark used in the report
python -c "from experiments.benchmark import run_benchmark; run_benchmark('configs/experiments/benchmark_icl_nuim_real.yaml')"

# the bigger default benchmark (5 configs × 4 datasets; skips datasets not downloaded)
python experiments/benchmark.py

python scripts/run_demo.py                         # synthetic end-to-end demo + figures
python scripts/evaluate_gps_outage.py --traj <trajectory.txt> --gt <groundtruth.txt> --outage-start 15
python scripts/live_dashboard.py --camera 0       # webcam demo
pytest tests/ -v                                   # run the test suite
```

Note: `data/icl_nuim/` is not in the repo folder right now (only `data/demo_sequence/`), so the real
benchmark needs the dataset downloaded first.

---

## 25. Tests

`tests/` has **170 test functions** (count of `def test_`) across 33 files, covering:
geometry and pose composition, Essential-matrix recovery on synthetic points, feature extraction,
bucketing, sub-pixel refinement, matching, the motion model, ATE/RPE/Umeyama alignment, the
tracking report, dataset loaders (ICL-NUIM, TartanAir, NED conversion), GPS outage, filters, plots,
and a full synthetic pipeline run. Run with `pytest tests/ -v`.

---

## 26. Known gaps between code, report and README

Found while tracing the code for this document. Knowing these in advance helps in a viva.

| # | Where | What it says | What the code actually does |
|---|---|---|---|
| 1 | Report §3.4 | "Brute-force Hamming with cross-check enabled", then ratio test | The 4 benchmark configs use `cross_check: false`; only the ratio test runs. In this code the two are mutually exclusive |
| 2 | Report App. B / §4.4 | `scripts/run_benchmark.py` | No such file. Use `experiments/benchmark.py` with `benchmark_icl_nuim_real.yaml` (Section 24) |
| 3 | README | "144 tests" | 170 test functions exist (report's number is right) |
| 4 | Report | "BRIEF" | The run used **ManualBRIEF** (Python fallback); results CSV says so. It also explains FAST + BRIEF's lower FPS |
| 5 | `pipeline.py` | `use_pnp` parameter, `hybrid_estimate_pose` imported | Never called; PnP is not part of any reported result |
| 6 | `motion_model.py` | `max_speed_ratio` | Computed but not used for rejection |
| 7 | Results table | "RPE Trans (m)" | Not scale-aligned, so not a metric distance (Section 17.6) |
| 8 | Report Fig. 3.2 caption | Matches "from ICL-NUIM" | `feature_matches_sample.png` comes from the synthetic demo sequence |
| 9 | Per-frame CSV | `describe_time_ms` | Always 0; description time is included in `detect_time_ms` |

None of these change the reported ATE, FPS or tracking numbers. They are wording or
documentation mismatches worth fixing or being ready to explain.

---

## 27. Glossary

| Term | Meaning |
|---|---|
| **VO** | Visual Odometry: estimating motion from consecutive images |
| **Monocular** | One camera; distance scale cannot be recovered |
| **Keypoint / feature** | A distinctive image location (usually a corner) |
| **Descriptor** | A binary fingerprint of the patch around a keypoint |
| **Hamming distance** | Number of differing bits between two binary strings |
| **Lowe ratio test** | Keep a match only if best < 0.75 × second best |
| **K** | Camera intrinsic matrix (focal lengths + principal point) |
| **Essential matrix E** | 3×3 matrix linking matched rays of two calibrated views: x₂ᵀ E x₁ = 0 |
| **RANSAC** | Fit a model to random minimal samples; keep the one most points agree with |
| **Inlier / outlier** | A match that agrees / disagrees with the best model |
| **Cheirality** | Requirement that reconstructed points are in front of the camera |
| **R, t** | Rotation matrix and (unit) translation direction between frames |
| **T_wc** | 4×4 camera-to-world pose matrix; last column = camera position |
| **SE(3)** | Rigid motions (rotation + translation) |
| **Sim(3)** | Rigid motion + uniform scale |
| **Umeyama** | Closed-form SVD method to find the best Sim(3)/SE(3) between two point sets |
| **ATE** | Absolute Trajectory Error: global path error after alignment |
| **RPE** | Relative Pose Error: per-step error |
| **RMSE** | Root mean square error: sqrt(mean(error²)) |
| **P95** | 95th percentile: 95 % of values are below it |
| **Scale drift** | The (unknown) scale slowly changing along the path |
| **Dead reckoning** | Navigating by adding up measured steps, without external fixes |
| **Homography H** | 3×3 mapping between images valid for pure rotation or a planar scene |
| **TUM format** | Text format `timestamp tx ty tz qx qy qz qw` |
| **Quaternion** | 4-number representation of a 3D rotation |
| **CLAHE** | Tile-wise contrast equalisation with a clip limit |
| **Quadtree** | Recursive 4-way splitting of the image to spread keypoints evenly |
