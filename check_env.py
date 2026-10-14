#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_env.py -- Environment inspection and dependency verification.

Run this first to confirm all required packages are available and
OpenCV features (FAST, ORB, BRISK, Essential matrix) work correctly.

Usage
-----
    python check_env.py
"""

import sys
import platform

print("=" * 60)
print("  Visual Odometry - Environment Check")
print("=" * 60)

print("\n[Python]")
print("  Version    : " + sys.version)
print("  Executable : " + sys.executable)
print("  Platform   : " + platform.platform())

deps = {
    "numpy": None,
    "scipy": None,
    "matplotlib": None,
    "pandas": None,
    "yaml": None,
    "psutil": None,
    "pytest": None,
}

print("\n[Core Dependencies]")
all_ok = True
for pkg in deps:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "?")
        print("  {:<20s} {}  [OK]".format(pkg, ver))
    except ImportError:
        print("  {:<20s} NOT FOUND  [FAIL]".format(pkg))
        all_ok = False

print("\n[OpenCV]")
try:
    import cv2
    print("  opencv version : {}  [OK]".format(cv2.__version__))

    print("\n  [Detectors]")
    cv2.FastFeatureDetector_create(threshold=20)
    print("  FAST             [OK]")
    cv2.ORB_create(nfeatures=100)
    print("  ORB              [OK]")
    try:
        cv2.BRISK_create()
        print("  BRISK            [OK]")
    except Exception as e:
        print("  BRISK            [FAIL] ({})".format(e))

    print("\n  [BRIEF availability]")
    try:
        cv2.xfeatures2d.BriefDescriptorExtractor_create()
        print("  BRIEF (contrib)  [OK]")
    except Exception:
        print("  BRIEF (contrib)  [FAIL] -> ManualBRIEF fallback will be used")

    print("\n  [Geometric estimation]")
    import numpy as np
    pts1 = np.random.default_rng(0).uniform(100, 400, (20, 2)).astype(np.float32)
    pts2 = pts1 + np.float32([[2, 1]] * 20)
    K = np.float64([[481.2, 0, 319.5], [0, 480, 239.5], [0, 0, 1]])
    E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, threshold=1.0)
    if E is not None and E.shape == (3, 3):
        print("  findEssentialMat [OK]")
    else:
        print("  findEssentialMat [FAIL]")
        all_ok = False
    _, R, t, _ = cv2.recoverPose(E, pts1, pts2, K)
    print("  recoverPose      [OK]  R.shape={}, t.shape={}".format(R.shape, t.shape))

except ImportError:
    print("  opencv-python    NOT FOUND  [FAIL]")
    print("  Install with: pip install opencv-python")
    all_ok = False

print("\n[Pipeline Imports]")
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
        print("  {:<45s} [OK]".format(mod_name))
    except Exception as e:
        print("  {:<45s} [FAIL] {}".format(mod_name, e))
        all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("  All checks passed. Ready to run experiments.")
else:
    print("  Some checks failed. See messages above.")
print("=" * 60)
