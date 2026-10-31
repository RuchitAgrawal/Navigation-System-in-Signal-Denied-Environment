# Feature Algorithm Reference

Details on FAST, ORB, BRIEF, BRISK algorithms used in this project.

## FAST
Features from Accelerated Segment Test (Rosten & Drummond, 2006).
Tests a circle of 16 pixels around a candidate corner.

## ORB
Oriented FAST and Rotated BRIEF (Rublee et al., 2011).
Assigns orientation via intensity centroid. Rotation-invariant descriptor.

## BRIEF
Binary Robust Independent Elementary Features (Calonder et al., 2010).
Not rotation-invariant. Uses Gaussian-sampled binary tests.

## BRISK
Binary Robust Invariant Scalable Keypoints (Leutenegger et al., 2011).
Scale and rotation invariant. Uses AGAST detector internally.

## FASTER
Adaptive FAST Corner Detector with Dynamic Threshold Convergence (Rosten, Porter & Drummond, 2010).
Dynamically adjusts the FAST intensity difference threshold $\tau \in [\tau_{\min}, \tau_{\max}]$ based on local image contrast to maintain target keypoint density across varying lighting conditions and texture levels.

## Spatial Bucketing & Keypoint Distribution
1. **Grid Bucketing (Perez-Grau 2017):** Divides the image into a static $3 \times 2$ (6-bucket) grid and allocates an equal keypoint quota per bucket to mitigate edge clumping.
2. **Recursive Quadtree Bucketing (Proposed Enhanced Method):** Dynamically partitions dense image nodes into 4 quadrants recursively until leaf cells reach a target count or minimum cell dimension, selecting the highest-response keypoint per cell to guarantee ultra-uniform spatial coverage.

## Algorithm Comparison Matrix

| Property | FAST-9 | Adaptive FASTER | ORB | BRIEF | BRISK |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Role** | Detector | Detector | Detector + Descriptor | Descriptor | Detector + Descriptor |
| **Output Type** | Keypoints | Keypoints | Keypoints + 256-bit binary | 256-bit binary | Keypoints + 512-bit binary |
| **Rotation Invariance** | None | None | Intensity Centroid ($SO(2)$) | None | Sampling Pattern ($SO(2)$) |
| **Scale Invariance** | None | None | Scale Pyramid (8 levels) | None | Scale-Space Octaves |
| **Distance Metric** | N/A | N/A | Hamming Distance | Hamming Distance | Hamming Distance |
| **Typical Speed** | Ultra-Fast (~1-2 ms) | Fast (~3-5 ms) | Moderate (~8-15 ms) | Ultra-Fast (~0.5 ms) | Moderate (~10-20 ms) |
| **Memory per Feature** | 28 bytes | 28 bytes | 32 bytes (descriptor) | 32 bytes (descriptor) | 64 bytes (descriptor) |
| **Best Suited For** | Fast forward flight | Dynamic lighting shifts | Aggressive yaw turns | Forward flight, planar | Multi-scale UAV altitude shifts |


