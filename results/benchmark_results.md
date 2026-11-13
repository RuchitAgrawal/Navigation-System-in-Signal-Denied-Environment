# Benchmark Results

## 1. Executive Summary

| Configuration | Descriptor | Dataset | Sequence | ATE RMSE (m) | RPE Trans (m) | RPE Rot (deg) | Tracking % | FPS |
|---|---|---|---|---|---|---|---|---|
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | living_room_traj1_loop | 0.2302 | 0.6755 | 0.5544 | 45.8700 | 32.9500 |
| fast_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.2219 | 0.6662 | 0.5571 | 44.5900 | 48.2200 |
| orb_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.2775 | 0.7242 | 0.5599 | 52.2600 | 32.7500 |
| orb_brisk_v1 | BRISK | icl_nuim | living_room_traj1_loop | 0.1732 | 0.7377 | 0.9610 | 54.0400 | 30.1100 |

## 2. Computational Latency and Throughput

| Configuration | Sequence | Mean Latency (ms) | Median Latency (ms) | P95 Latency (ms) | Mean FPS | Total Frames | Dropped Frames |
|---|---|---|---|---|---|---|---|
| fast_brief_v1 | living_room_traj1_loop | 31.3880 | 29.6900 | 42.1080 | 32.9500 | 1017 | 550 |
| fast_orb_v1 | living_room_traj1_loop | 21.4710 | 20.9580 | 28.7110 | 48.2200 | 1017 | 563 |
| orb_orb_v1 | living_room_traj1_loop | 35.7010 | 28.1800 | 63.0010 | 32.7500 | 1017 | 485 |
| orb_brisk_v1 | living_room_traj1_loop | 38.8310 | 30.5730 | 66.5230 | 30.1100 | 1017 | 467 |

## 3. Complete Benchmark Raw Data

| config_id | descriptor_label | dataset | sequence | ate_alignment | ate_scale | ate_rmse_m | ate_mean_m | ate_median_m | ate_std_m | ate_n_frames | rpe_delta_frames | rpe_trans_rmse_m | rpe_trans_mean_m | rpe_trans_median_m | rpe_rot_rmse_deg | rpe_rot_mean_deg | rpe_n_pairs | total_frames | success_frames | failed_frames | tracking_success_pct | is_degenerate | mean_frame_time_ms | median_frame_time_ms | p95_frame_time_ms | mean_fps | median_fps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | living_room_traj1_loop | sim3 | 0.0066 | 0.2302 | 0.2144 | 0.2112 | 0.0837 | 965 | 1 | 0.6755 | 0.4576 | 0.0035 | 0.5544 | 0.4850 | 964 | 1017 | 466 | 550 | 45.8700 | Yes | 31.3880 | 29.6900 | 42.1080 | 32.9500 | 33.6800 |
| fast_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0100 | 0.2219 | 0.2113 | 0.2212 | 0.0680 | 965 | 1 | 0.6662 | 0.4451 | 0.0032 | 0.5571 | 0.4963 | 964 | 1017 | 453 | 563 | 44.5900 | Yes | 21.4710 | 20.9580 | 28.7110 | 48.2200 | 47.7100 |
| orb_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0050 | 0.2775 | 0.2642 | 0.2466 | 0.0849 | 965 | 1 | 0.7242 | 0.5257 | 0.9971 | 0.5599 | 0.4940 | 964 | 1017 | 531 | 485 | 52.2600 | No | 35.7010 | 28.1800 | 63.0010 | 32.7500 | 35.4900 |
| orb_brisk_v1 | BRISK | icl_nuim | living_room_traj1_loop | sim3 | 0.0056 | 0.1732 | 0.1669 | 0.1675 | 0.0463 | 965 | 1 | 0.7377 | 0.5454 | 0.9972 | 0.9610 | 0.5410 | 964 | 1017 | 549 | 467 | 54.0400 | No | 38.8310 | 30.5730 | 66.5230 | 30.1100 | 32.7100 |

*Generated automatically. ATE uses Sim(3) alignment unless noted.*
