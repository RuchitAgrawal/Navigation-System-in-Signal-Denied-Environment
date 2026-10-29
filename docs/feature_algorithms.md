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

## Sub-Pixel Corner Refinement
Applies `cv2.cornerSubPix` using gradient orthogonality criteria $((\nabla I)^T \cdot (p - q) = 0)$ over a search window to resolve corner locations with sub-pixel precision ($< 0.1\text{ px}$), reducing angular triangulation noise and trajectory drift.


