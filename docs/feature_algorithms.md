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

