# Benchmark Results

## 1. Executive Summary

| Configuration | Descriptor | Dataset | Sequence | ATE RMSE (m) | RPE Trans (m) | RPE Rot (deg) | Tracking % | FPS |
|---|---|---|---|---|---|---|---|---|
| orb_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.0331 | 0.9102 | 0.3867 | 100.00 | 20.04 |
| orb_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | 0.0331 | 0.9102 | 0.3867 | 100.00 | 13.88 |
| orb_orb_v1 | ORB | tartanair | ocean_Easy_P000 | 2.1199 | 0.2100 | 23.1712 | 2.04 | 1.26 |
| orb_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | 0.0509 | 0.9010 | 0.2472 | 100.00 | 15.56 |
| fast_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.0233 | 0.9088 | 0.3115 | 100.00 | 40.76 |
| fast_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | 0.0233 | 0.9088 | 0.3115 | 100.00 | 39.55 |
| fast_orb_v1 | ORB | tartanair | ocean_Easy_P000 | 2.1841 | 0.1526 | 0.0000 | 0.00 | 645.07 |
| fast_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | 0.0413 | 0.9009 | 0.3060 | 100.00 | 47.60 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | living_room_traj1_loop | 0.0218 | 0.9090 | 0.4388 | 100.00 | 20.51 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | office_room_traj0_loop | 0.0218 | 0.9090 | 0.4388 | 100.00 | 20.40 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | ocean_Easy_P000 | 1.4162 | 0.2032 | 24.2624 | 2.04 | 706.32 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | abandonedfactory_Easy_P000 | 0.0498 | 0.9019 | 0.3589 | 100.00 | 29.53 |
| orb_brisk_v1 | BRISK | icl_nuim | living_room_traj1_loop | 0.0312 | 0.9094 | 0.3224 | 100.00 | 17.21 |
| orb_brisk_v1 | BRISK | icl_nuim | office_room_traj0_loop | 0.0312 | 0.9094 | 0.3224 | 100.00 | 17.44 |
| orb_brisk_v1 | BRISK | tartanair | ocean_Easy_P000 | 2.1199 | 0.2045 | 24.3732 | 2.04 | 89.66 |
| orb_brisk_v1 | BRISK | tartanair | abandonedfactory_Easy_P000 | 0.0426 | 0.9007 | 0.2598 | 100.00 | 15.30 |
| faster_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.0231 | 0.9086 | 0.4300 | 100.00 | 24.86 |
| faster_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | 0.0231 | 0.9086 | 0.4300 | 100.00 | 25.88 |
| faster_orb_v1 | ORB | tartanair | ocean_Easy_P000 | 2.1841 | 0.1526 | 0.0000 | 0.00 | 574.48 |
| faster_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | 0.0236 | 0.9004 | 0.2690 | 100.00 | 29.62 |

## 2. Computational Latency and Throughput

| Configuration | Sequence | Mean Latency (ms) | Median Latency (ms) | P95 Latency (ms) | Mean FPS | Total Frames | Dropped Frames |
|---|---|---|---|---|---|---|---|
| orb_orb_v1 | living_room_traj1_loop | 68.2260 | 62.3390 | 151.9820 | 20.04 | 50 | 0 |
| orb_orb_v1 | office_room_traj0_loop | 79.8110 | 68.2410 | 145.9360 | 13.88 | 50 | 0 |
| orb_orb_v1 | ocean_Easy_P000 | 799.1340 | 790.9300 | 901.9940 | 1.26 | 50 | 48 |
| orb_orb_v1 | abandonedfactory_Easy_P000 | 65.3550 | 64.3630 | 81.5820 | 15.56 | 50 | 0 |
| fast_orb_v1 | living_room_traj1_loop | 27.1490 | 25.6190 | 50.2160 | 40.76 | 50 | 0 |
| fast_orb_v1 | office_room_traj0_loop | 28.0410 | 25.6300 | 49.7400 | 39.55 | 50 | 0 |
| fast_orb_v1 | ocean_Easy_P000 | 1.5850 | 1.6210 | 1.7920 | 645.07 | 50 | 49 |
| fast_orb_v1 | abandonedfactory_Easy_P000 | 23.6780 | 19.5820 | 42.3400 | 47.60 | 50 | 0 |
| fast_brief_v1 | living_room_traj1_loop | 54.6550 | 52.2910 | 81.9130 | 20.51 | 50 | 0 |
| fast_brief_v1 | office_room_traj0_loop | 54.8940 | 53.9030 | 80.2750 | 20.40 | 50 | 0 |
| fast_brief_v1 | ocean_Easy_P000 | 1.4540 | 1.4350 | 1.7160 | 706.32 | 50 | 48 |
| fast_brief_v1 | abandonedfactory_Easy_P000 | 35.5890 | 32.0590 | 55.9800 | 29.53 | 50 | 0 |
| orb_brisk_v1 | living_room_traj1_loop | 60.2570 | 61.3240 | 77.7550 | 17.21 | 50 | 0 |
| orb_brisk_v1 | office_room_traj0_loop | 59.4850 | 61.2960 | 77.4850 | 17.44 | 50 | 0 |
| orb_brisk_v1 | ocean_Easy_P000 | 27.7410 | 17.1640 | 77.3730 | 89.66 | 50 | 48 |
| orb_brisk_v1 | abandonedfactory_Easy_P000 | 66.8180 | 65.2400 | 83.2660 | 15.30 | 50 | 0 |
| faster_orb_v1 | living_room_traj1_loop | 44.0100 | 43.7180 | 65.5370 | 24.86 | 50 | 0 |
| faster_orb_v1 | office_room_traj0_loop | 42.1400 | 40.1710 | 65.1220 | 25.88 | 50 | 0 |
| faster_orb_v1 | ocean_Easy_P000 | 1.8060 | 1.8270 | 2.2340 | 574.48 | 50 | 49 |
| faster_orb_v1 | abandonedfactory_Easy_P000 | 36.1400 | 34.4520 | 57.2240 | 29.62 | 50 | 0 |

## 3. Complete Benchmark Raw Data

| config_id | descriptor_label | dataset | sequence | ate_alignment | ate_scale | ate_rmse_m | ate_mean_m | ate_median_m | ate_std_m | ate_n_frames | rpe_delta_frames | rpe_trans_rmse_m | rpe_trans_mean_m | rpe_trans_median_m | rpe_rot_rmse_deg | rpe_rot_mean_deg | rpe_n_pairs | total_frames | success_frames | failed_frames | tracking_success_pct | is_degenerate | mean_frame_time_ms | median_frame_time_ms | p95_frame_time_ms | mean_fps | median_fps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| orb_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0949 | 0.0331 | 0.0306 | 0.0278 | 0.0127 | 50 | 1 | 0.9102 | 0.9102 | 0.9094 | 0.3867 | 0.3097 | 49 | 50 | 49 | 0 | 100.0 | False | 68.226 | 62.339 | 151.982 | 20.04 | 16.04 |
| orb_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | sim3 | 0.0949 | 0.0331 | 0.0306 | 0.0278 | 0.0127 | 50 | 1 | 0.9102 | 0.9102 | 0.9094 | 0.3867 | 0.3097 | 49 | 50 | 49 | 0 | 100.0 | False | 79.811 | 68.241 | 145.936 | 13.88 | 14.65 |
| orb_orb_v1 | ORB | tartanair | ocean_Easy_P000 | sim3 | 3.7524 | 2.1199 | 1.8308 | 1.8263 | 1.0687 | 50 | 1 | 0.21 | 0.1703 | 0.1525 | 23.1712 | 3.3102 | 49 | 50 | 1 | 48 | 2.04 | True | 799.134 | 790.93 | 901.994 | 1.26 | 1.26 |
| orb_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | sim3 | 0.104 | 0.0509 | 0.0475 | 0.0427 | 0.0185 | 50 | 1 | 0.901 | 0.901 | 0.9002 | 0.2472 | 0.2169 | 49 | 50 | 49 | 0 | 100.0 | False | 65.355 | 64.363 | 81.582 | 15.56 | 15.54 |
| fast_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0931 | 0.0233 | 0.0211 | 0.0196 | 0.0099 | 50 | 1 | 0.9088 | 0.9088 | 0.9088 | 0.3115 | 0.2473 | 49 | 50 | 49 | 0 | 100.0 | False | 27.149 | 25.619 | 50.216 | 40.76 | 39.03 |
| fast_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | sim3 | 0.0931 | 0.0233 | 0.0211 | 0.0196 | 0.0099 | 50 | 1 | 0.9088 | 0.9088 | 0.9088 | 0.3115 | 0.2473 | 49 | 50 | 49 | 0 | 100.0 | False | 28.041 | 25.63 | 49.74 | 39.55 | 39.02 |
| fast_orb_v1 | ORB | tartanair | ocean_Easy_P000 | sim3 | 1.0 | 2.1841 | 1.9063 | 1.8994 | 1.066 | 50 | 1 | 0.1526 | 0.1526 | 0.1525 | 0.0 | 0.0 | 49 | 50 | 0 | 49 | 0.0 | True | 1.585 | 1.621 | 1.792 | 645.07 | 617.02 |
| fast_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | sim3 | 0.1046 | 0.0413 | 0.0371 | 0.0361 | 0.0183 | 50 | 1 | 0.9009 | 0.9009 | 0.9 | 0.306 | 0.2748 | 49 | 50 | 49 | 0 | 100.0 | False | 23.678 | 19.582 | 42.34 | 47.6 | 51.07 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | living_room_traj1_loop | sim3 | 0.0936 | 0.0218 | 0.0191 | 0.0181 | 0.0105 | 50 | 1 | 0.909 | 0.909 | 0.9087 | 0.4388 | 0.2946 | 49 | 50 | 49 | 0 | 100.0 | False | 54.655 | 52.291 | 81.913 | 20.51 | 19.12 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | office_room_traj0_loop | sim3 | 0.0936 | 0.0218 | 0.0191 | 0.0181 | 0.0105 | 50 | 1 | 0.909 | 0.909 | 0.9087 | 0.4388 | 0.2946 | 49 | 50 | 49 | 0 | 100.0 | False | 54.894 | 53.903 | 80.275 | 20.4 | 18.55 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | ocean_Easy_P000 | sim3 | 3.7906 | 1.4162 | 1.1699 | 0.9133 | 0.7982 | 50 | 1 | 0.2032 | 0.1689 | 0.1525 | 24.2624 | 3.4661 | 49 | 50 | 1 | 48 | 2.04 | True | 1.454 | 1.435 | 1.716 | 706.32 | 696.86 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | abandonedfactory_Easy_P000 | sim3 | 0.1051 | 0.0498 | 0.0446 | 0.0388 | 0.0222 | 50 | 1 | 0.9019 | 0.9018 | 0.9005 | 0.3589 | 0.3185 | 49 | 50 | 49 | 0 | 100.0 | False | 35.589 | 32.059 | 55.98 | 29.53 | 31.19 |
| orb_brisk_v1 | BRISK | icl_nuim | living_room_traj1_loop | sim3 | 0.0938 | 0.0312 | 0.0284 | 0.0253 | 0.0129 | 50 | 1 | 0.9094 | 0.9094 | 0.9086 | 0.3224 | 0.2795 | 49 | 50 | 49 | 0 | 100.0 | False | 60.257 | 61.324 | 77.755 | 17.21 | 16.31 |
| orb_brisk_v1 | BRISK | icl_nuim | office_room_traj0_loop | sim3 | 0.0938 | 0.0312 | 0.0284 | 0.0253 | 0.0129 | 50 | 1 | 0.9094 | 0.9094 | 0.9086 | 0.3224 | 0.2795 | 49 | 50 | 49 | 0 | 100.0 | False | 59.485 | 61.296 | 77.485 | 17.44 | 16.31 |
| orb_brisk_v1 | BRISK | tartanair | ocean_Easy_P000 | sim3 | 3.7524 | 2.1199 | 1.8308 | 1.8263 | 1.0687 | 50 | 1 | 0.2045 | 0.1691 | 0.1525 | 24.3732 | 3.4819 | 49 | 50 | 1 | 48 | 2.04 | True | 27.741 | 17.164 | 77.373 | 89.66 | 58.26 |
| orb_brisk_v1 | BRISK | tartanair | abandonedfactory_Easy_P000 | sim3 | 0.104 | 0.0426 | 0.0388 | 0.0343 | 0.0176 | 50 | 1 | 0.9007 | 0.9007 | 0.8996 | 0.2598 | 0.2221 | 49 | 50 | 49 | 0 | 100.0 | False | 66.818 | 65.24 | 83.266 | 15.3 | 15.33 |
| faster_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0927 | 0.0231 | 0.0215 | 0.0212 | 0.0084 | 50 | 1 | 0.9086 | 0.9086 | 0.9088 | 0.43 | 0.2864 | 49 | 50 | 49 | 0 | 100.0 | False | 44.01 | 43.718 | 65.537 | 24.86 | 22.87 |
| faster_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | sim3 | 0.0927 | 0.0231 | 0.0215 | 0.0212 | 0.0084 | 50 | 1 | 0.9086 | 0.9086 | 0.9088 | 0.43 | 0.2864 | 49 | 50 | 49 | 0 | 100.0 | False | 42.14 | 40.171 | 65.122 | 25.88 | 24.89 |
| faster_orb_v1 | ORB | tartanair | ocean_Easy_P000 | sim3 | 1.0 | 2.1841 | 1.9063 | 1.8994 | 1.066 | 50 | 1 | 0.1526 | 0.1526 | 0.1525 | 0.0 | 0.0 | 49 | 50 | 0 | 49 | 0.0 | True | 1.806 | 1.827 | 2.234 | 574.48 | 547.47 |
| faster_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | sim3 | 0.1033 | 0.0236 | 0.0213 | 0.0193 | 0.0101 | 50 | 1 | 0.9004 | 0.9004 | 0.8999 | 0.269 | 0.2406 | 49 | 50 | 49 | 0 | 100.0 | False | 36.14 | 34.452 | 57.224 | 29.62 | 29.03 |
