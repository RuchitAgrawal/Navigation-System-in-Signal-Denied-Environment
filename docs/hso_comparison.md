# HSO vs. Our Implementation â€” Comparison

**Reference:** [HSO â€” Hybrid Sparse Visual Odometry](https://github.com/luodongting/HSO)  
**License:** HSO is distributed under GPL-3.0.  
**Attribution:** Luodongting. *HSO: Hybrid Sparse Visual Odometry*. GitHub, 2022.

> No HSO source code has been copied into this repository.
> This document records the architectural similarities and differences
> that informed design decisions in the Python pipeline.

---

## Side-by-Side Comparison

| Aspect | HSO (reference) | Our Python Pipeline |
|--------|----------------|---------------------|
| **Language** | C++17 | Python 3.10+ |
| **License** | GPL-3.0 | MIT (own code) |
| **Feature detection** | Custom FAST-based patch selector | Adaptive FASTER / FAST-9 / ORB |
| **Spatial Distribution** | Bucket grid | Recursive Quadtree Spatial Partitioning |
| **Sub-pixel Refinement** | Inverse compositional LK | Gradient Orthogonality (`cornerSubPix`) |
| **Feature tracking** | Patch-based Lucas-Kanade optical flow | Descriptor matching (Hamming BFMatcher) |
| **Descriptor** | None (direct patch comparison) | BRIEF / ORB / BRISK |
| **Map** | Sparse 3-D point map + semi-dense depth | Frame-to-frame tracking with motion prior |
| **Geometric estimation** | Full pose graph with sliding-window BA | Hybrid RGB-D PnP + 5-Point Essential Fallback |
| **Kinematic Model** | None (direct frame registration) | Constant-Velocity Motion Model (CVMM) Prior |
| **Scale** | Metric (stereo or depth initialization) | Metric (via PnP depth) + Monocular Sim(3) Fallback |
| **Loop closure** | Not in base version | Not implemented |
| **IMU** | Not in base version | Not implemented |
| **Dataset loaders** | TUM, EuRoC (C++ readers) | ICL-NUIM, TartanAir 2+2 Suite (Python) |
| **Evaluation** | Internal ATE print | ATE + RPE + Trajectory Video Dashboards + Outage Sim |
| **Benchmarking** | Single-config | Multi-config 20-run benchmark orchestrator |
| **GPS-outage sim** | Not present | Implemented with drift rate analysis (2.28%) |

---

## Architectural Inspirations from HSO

The following design patterns in our pipeline were informed by studying HSO:

1. **Modular component separation** â€” HSO separates feature tracking, map
   management, and pose estimation into distinct classes. We mirror this with
   `detector`, `descriptor`, `matcher`, `pipeline`, and `accumulator` modules.

2. **Failure handling per frame** â€” HSO tracks tracking quality per frame and
   resets when quality drops. We adopt a similar per-frame `FrameStatus` enum
   with graceful failure logging.

3. **Trajectory output format** â€” HSO outputs poses in TUM format. We follow
   the same convention for compatibility with standard evaluation tools.

4. **Evaluation against ground truth** â€” HSO evaluates ATE post-run without
   using GT during motion estimation. We enforce the same rule strictly.

---

## Key Differences

- **No bundle adjustment.** HSO refines poses using a sliding-window
  bundle adjuster. Our pipeline uses only RANSAC Essential matrix estimation
  without any map-based refinement. This is a deliberate scope choice for
  the undergraduate module.

- **Descriptor-based matching vs. direct tracking.** HSO uses direct patch
  correlation for tracking. Our pipeline uses descriptor matching, which is
  more interpretable and configurable for the multi-config experiment.

- **Python vs. C++.** The Python implementation is slower per frame but
  allows rapid experimentation and is accessible without a C++ build system.

- **Explicit experiment framework.** HSO does not include a multi-config
  benchmarking system. Our pipeline adds YAML-driven experiment configs,
  per-frame CSV logging, and automated comparison plots specifically to
  answer the research question.

---

## License Note

HSO is released under GPL-3.0. Because no HSO source code has been
incorporated into this repository, this project's own code is released
under the MIT License without GPL inheritance obligations.

If any HSO code is incorporated in future extensions, the GPL-3.0 license
terms must be respected and the repository license updated accordingly.

