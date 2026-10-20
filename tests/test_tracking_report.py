# tests/test_tracking_report.py -- TrackingReport unit tests
import pytest
from src.geometry.pose import FrameDiagnostics, FrameStatus
from src.odometry.tracker import compute_tracking_report, compute_fps_stats, TrackingReport

\ndef make_diag(status, total_ms=10.0):
    return FrameDiagnostics(frame_idx=0, status=status, total_time_ms=total_ms)
\n\nclass TestTrackingReport:
    def test_all_success(self):
        diags = [make_diag(FrameStatus.SKIPPED)] + [make_diag(FrameStatus.SUCCESS)] * 9
        r = compute_tracking_report(diags)
        assert r.success_rate == 1.0
        assert not r.is_degenerate

    def test_all_failed(self):
        diags = [make_diag(FrameStatus.SKIPPED)] + [make_diag(FrameStatus.FAILED_MATCHES)] * 9
        r = compute_tracking_report(diags)
        assert r.success_rate == 0.0
        assert r.is_degenerate

    def test_counts_correct(self):
        diags = [
            make_diag(FrameStatus.SKIPPED),
            make_diag(FrameStatus.SUCCESS),
            make_diag(FrameStatus.FAILED_FEATURES),
            make_diag(FrameStatus.FAILED_RANSAC),
        ]
        r = compute_tracking_report(diags)
        assert r.success_frames == 1
        assert r.failed_features_frames == 1
        assert r.failed_ransac_frames == 1
\n\nclass TestFpsStats:
    def test_zero_ms_handled(self):
        diags = [make_diag(FrameStatus.SUCCESS, total_ms=0.0)]
        stats = compute_fps_stats(diags)
        assert stats['mean_fps'] > 0

