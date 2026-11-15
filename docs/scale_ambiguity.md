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

## 2. Mathematical Formulation: Umeyama Sim(3) Alignment

To fairly evaluate estimated monocular trajectories against metric ground-truth, we apply the closed-form least-squares Sim(3) similarity transformation method formulated by Umeyama (1991).

Given $n$ estimated 3D position points $X = \{x_1, \dots, x_n\}$ and corresponding ground-truth points $Y = \{y_1, \dots, y_n\}$:

1. **Centroid Computation**:
   $$\mu_x = \frac{1}{n} \sum_{i=1}^n x_i, \quad \mu_y = \frac{1}{n} \sum_{i=1}^n y_i$$
2. **Variance & Cross-Covariance**:
   $$\sigma_x^2 = \frac{1}{n} \sum_{i=1}^n \|x_i - \mu_x\|^2$$
   $$\Sigma_{xy} = \frac{1}{n} \sum_{i=1}^n (y_i - \mu_y)(x_i - \mu_x)^T$$
3. **Singular Value Decomposition (SVD)**:
   $$\Sigma_{xy} = U D V^T, \quad \text{where } D = \text{diag}(d_1, d_2, d_3)$$
4. **Optimal Rotation, Scale, and Translation**:
   $$S = \text{diag}\left(1, 1, \det(U)\det(V)\right)$$
   $$R^* = U S V^T \in SO(3)$$
   $$s^* = \frac{1}{\sigma_x^2} \mathrm{tr}(D S)$$
   $$t^* = \mu_y - s^* R^* \mu_x$$

The aligned estimated positions are given by:
$$\hat{y}_i = s^* R^* x_i + t^*$$

This formulation guarantees that the resulting Absolute Trajectory Error (ATE RMSE) measures the intrinsic structural shape fidelity of the camera motion path, completely decoupling trajectory evaluation from the unobservable monocular scale gauge freedom.

## 3. Correct Handling in This Pipeline

1. **Sim(3) alignment** (Umeyama 1991) is used for all ATE computations.
   This recovers the best-fit scale, rotation, and translation simultaneously.

2. The recovered **scale factor s** is reported in all result tables (e.g., $s \approx 0.005–0.010$ on ICL-NUIM).

3. ATE values are reported **after** scale correction and are clearly labeled
   as 'Sim(3) aligned' in every output file.

4. The GPS-outage simulation uses a **one-time scale anchor** at the outage
   start, providing metric scale for that specific interval only.

## 4. Implications for the Research Question

The metric ATE after Sim(3) alignment measures *shape accuracy* (how well the
trajectory shape matches GT) independent of global scale. This is the correct
metric for comparing monocular VO configurations.

RPE (Relative Pose Error) is **scale-independent** and measures local drift
directly without requiring any alignment.

