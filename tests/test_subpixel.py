"""
tests/test_subpixel.py — Unit tests for sub-pixel corner refinement.
"""

import cv2
import numpy as np
import pytest
from src.features.subpixel import refine_keypoints_subpixel


class TestRefineKeypointsSubpixel:
    def test_empty_keypoints_returns_empty(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        assert refine_keypoints_subpixel(img, []) == []

    def test_preserves_attributes(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(img, (20, 20), (60, 60), 255, -1)

        kp = cv2.KeyPoint(x=20.0, y=20.0, size=5.0, angle=45.0, response=100.0, octave=1, class_id=7)
        refined = refine_keypoints_subpixel(img, [kp])
        assert len(refined) == 1
        assert refined[0].size == 5.0
        assert refined[0].angle == 45.0
        assert refined[0].response == 100.0
        assert refined[0].octave == 1
        assert refined[0].class_id == 7

    def test_refines_coordinates(self):
        # Create an image with a high-contrast sharp corner
        img = np.zeros((100, 100), dtype=np.uint8)
        img[30:70, 30:70] = 200

        # Slightly offset keypoint
        kp = cv2.KeyPoint(x=30.0, y=30.0, size=3.0)
        refined = refine_keypoints_subpixel(img, [kp])
        assert len(refined) == 1
        # Coordinates must be valid within the image bounds
        assert 0 <= refined[0].pt[0] < 100
        assert 0 <= refined[0].pt[1] < 100
