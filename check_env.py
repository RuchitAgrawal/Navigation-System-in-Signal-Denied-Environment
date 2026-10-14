#!/usr/bin/env python
"""
check_env.py — Environment inspection and dependency verification.

Run this first to confirm all required packages are available and
OpenCV features (FAST, ORB, BRISK, Essential matrix) work correctly.

Usage
-----
    python check_env.py
"""

import sys
import platform

print("=" * 60)
print("  Visual Odometry — Environment Check")
print("=" * 60)

# Python
print(f"\n[Python]")
print(f"  Version    : {sys.version}")
print(f"  Executable : {sys.executable}")
print(f"  Platform   : {platform.platform()}")

# Core packages
print(f"\n[Core Dependencies]")
deps = {
    "numpy": "np",
    "scipy": None,
    "matplotlib": None,
    "pandas": None,
    "yaml": "yaml",
    "psutil": None,
    "pytest": None,
}

all_ok = True
for pkg, alias in deps.items():
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "?")
        print(f"  {pkg:<20s} {ver}  ✓")
    except ImportError:
        print(f"  {pkg:<20s} NOT FOUND  ✗")
        all_ok = False

# OpenCV
print(f"\n[OpenCV]")
try:
    import cv2
    print(f"  opencv version : {cv2.__version__}  ✓")

    # Detectors
    print(f"\n  [Detectors]")
    fast = cv2.FastFeatureDetector_create(threshold=20)
    print(f"  FAST             ✓")
    orb  = cv2.ORB_create(nfeatures=100)
    print(f"  ORB              ✓")
    try:
        brisk = cv2.BRISK_create()
        print(f"  BRISK            ✓")
    except Exception as e:
        print(f"  BRISK            ✗  ({e})")

    # BRIEF
    print(f"\n  [BRIEF availability]")
    try:
        brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
        print(f"  BRIEF (contrib)  ✓  (opencv-contrib-python available)")
        brief_available = True
    except Exception:
        print(f"  BRIEF (contrib)  ✗  -> ManualBRIEF fallback will be used")
        brief_available = False

    # Essential matrix
    print(f"\n  [Geometric estimation]")
    import numpy as np
    pts1 = np.random.default_rng(0).uniform(100, 400, (20, 2)).astype(np.float32)
    pts2 = pts1 + np.float32([[2, 1]] * 20)
    K = np.float64([[481.2, 0, 319.5], [0, 480, 239.5], [0, 0, 1]])
    E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, threshold=1.0)
    if E is not None and E.shape == (3, 3):
        print(f"  findEssentialMat ✓")
    _, R, t, _ = cv2.recoverPose(E, pts1, pts2, K)
    print(f"  recoverPose      ✓  R.shape={R.shape}, t.shape={t.shape}")

except ImportError:
    print(f"  opencv-python    NOT FOUND  ✗")
    print(f"  Install with: pip install opencv-python")
    all_ok = False

# Import pipeline modules
print(f"\n[Pipeline Imports]")
pipeline_modules = [
    "src.geometry.transforms",
    "src.geometry.pose",
    "src.geometry.essential",
    "src.features.detector",
    "src.features.descriptor",
    "src.features.config",
    "src.matching.matcher",
    "src.odometry.pipeline",
    "src.odometry.tracker",
    "src.evaluation.ate",
    "src.evaluation.rpe",
    "src.evaluation.metrics",
    "src.visualization.trajectory_plot",
    "src.datasets.base_dataset",
    "src.datasets.icl_nuim",
    "src.datasets.tartanair",
    "experiments.runner",
]

sys.path.insert(0, ".")
for mod_name in pipeline_modules:
    try:
        __import__(mod_name)
        print(f"  {mod_name:<45s} ✓")
    except Exception as e:
        print(f"  {mod_name:<45s} ✗  {e}")
        all_ok = False

print(f"\n{'=' * 60}")
if all_ok:
    print("  ✓  All checks passed. Ready to run experiments.")
else:
    print("  ✗  Some checks failed. See messages above.")
print("=" * 60)
