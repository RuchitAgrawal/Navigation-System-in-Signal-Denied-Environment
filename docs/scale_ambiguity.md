# Monocular Visual Odometry: Scale Ambiguity

## What is scale ambiguity?

In monocular VO, the essential matrix decomposition (cv2.recoverPose) recovers
the translation direction **t** as a unit vector:

    ||t|| = 1

This means the recovered pose describes the *direction* of camera motion but not
its *magnitude*. Two trajectories that differ only by a global scale factor s are
geometrically equivalent from the essential matrix perspective.

## Why does this matter for evaluation?

If the estimated trajectory is evaluated against metric ground truth using SE(3)
alignment (scale=1), the ATE will be dominated by scale error rather than
rotational or translational drift. This gives a misleading picture of accuracy.

## Correct handling in this pipeline

1. **Sim(3) alignment** (Umeyama 1991) is used for all ATE computations.
   This recovers the best-fit scale, rotation, and translation simultaneously.

2. The recovered **scale factor s** is reported in all result tables.

3. ATE values are reported **after** scale correction and are clearly labeled
   as 'Sim(3) aligned' in every output file.

4. The GPS-outage simulation uses a **one-time scale anchor** at the outage
   start, providing metric scale for that specific interval only.

## Implications for the research question

The metric ATE after Sim(3) alignment measures *shape accuracy* (how well the
trajectory shape matches GT) independent of global scale. This is the correct
metric for comparing monocular VO configurations.

RPE (Relative Pose Error) is **scale-independent** and measures local drift
directly without requiring any alignment.

