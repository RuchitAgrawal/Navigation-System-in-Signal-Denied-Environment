# Benchmark Results

## 1. Executive Summary

| Configuration | Descriptor | Dataset | Sequence | ATE RMSE (m) | RPE Trans (m) | RPE Rot (deg) | Tracking % | FPS |
|---|---|---|---|---|---|---|---|---|
| orb_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.0331 | 0.9102 | 0.3867 | 100.0000 | 25.7800 |
| orb_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | 0.0331 | 0.9102 | 0.3867 | 100.0000 | 12.5600 |
| orb_orb_v1 | ORB | tartanair | ocean_Easy_P000 | 2.1199 | 0.2100 | 23.1712 | 2.0400 | 1.1800 |
| orb_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | 0.8262 | 0.3364 | 0.0000 | 8.1600 | 1.5800 |
| fast_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.0233 | 0.9088 | 0.3115 | 100.0000 | 31.5300 |
| fast_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | 0.0233 | 0.9088 | 0.3115 | 100.0000 | 32.4000 |
| fast_orb_v1 | ORB | tartanair | ocean_Easy_P000 | 2.1841 | 0.1526 | 0.0000 | 0.0000 | 573.6700 |
| fast_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | 1.0344 | 0.2387 | 33.5892 | 4.0800 | 212.1800 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | living_room_traj1_loop | 0.0218 | 0.9090 | 0.4388 | 100.0000 | 17.8100 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | office_room_traj0_loop | 0.0218 | 0.9090 | 0.4388 | 100.0000 | 19.2600 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | ocean_Easy_P000 | 1.4162 | 0.2032 | 24.2624 | 2.0400 | 781.4600 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | abandonedfactory_Easy_P000 | 1.0634 | 0.2489 | 13.5045 | 4.0800 | 213.6500 |
| orb_brisk_v1 | BRISK | icl_nuim | living_room_traj1_loop | 0.0340 | 0.9093 | 0.3176 | 100.0000 | 15.3300 |
| orb_brisk_v1 | BRISK | icl_nuim | office_room_traj0_loop | 0.0340 | 0.9093 | 0.3176 | 100.0000 | 15.3300 |
| orb_brisk_v1 | BRISK | tartanair | ocean_Easy_P000 | 1.4303 | 0.3054 | 20.5306 | 6.1200 | 84.5900 |
| orb_brisk_v1 | BRISK | tartanair | abandonedfactory_Easy_P000 | 1.5516 | 0.2734 | 42.4936 | 6.1200 | 1.2300 |
| faster_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | 0.0231 | 0.9086 | 0.4299 | 100.0000 | 18.6300 |
| faster_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | 0.0231 | 0.9086 | 0.4299 | 100.0000 | 19.7700 |
| faster_orb_v1 | ORB | tartanair | ocean_Easy_P000 | 2.1841 | 0.1526 | 0.0000 | 0.0000 | 500.0100 |
| faster_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | 1.0756 | 0.2845 | 25.0292 | 6.1200 | 161.4300 |

## 2. Computational Latency and Throughput

| Configuration | Sequence | Mean Latency (ms) | Median Latency (ms) | P95 Latency (ms) | Mean FPS | Total Frames | Dropped Frames |
|---|---|---|---|---|---|---|---|
| orb_orb_v1 | living_room_traj1_loop | 52.0970 | 33.8170 | 155.3480 | 25.7800 | 50 | 0 |
| orb_orb_v1 | office_room_traj0_loop | 87.4270 | 73.0300 | 157.0180 | 12.5600 | 50 | 0 |
| orb_orb_v1 | ocean_Easy_P000 | 851.9180 | 852.6400 | 943.4540 | 1.1800 | 50 | 48 |
| orb_orb_v1 | abandonedfactory_Easy_P000 | 733.2270 | 840.0400 | 950.5880 | 1.5800 | 50 | 45 |
| fast_orb_v1 | living_room_traj1_loop | 34.8730 | 31.6150 | 58.7400 | 31.5300 | 50 | 0 |
| fast_orb_v1 | office_room_traj0_loop | 33.5080 | 31.3920 | 53.6650 | 32.4000 | 50 | 0 |
| fast_orb_v1 | ocean_Easy_P000 | 1.7590 | 1.7260 | 1.9960 | 573.6700 | 50 | 49 |
| fast_orb_v1 | abandonedfactory_Easy_P000 | 18.2740 | 12.3480 | 47.7030 | 212.1800 | 50 | 47 |
| fast_brief_v1 | living_room_traj1_loop | 60.8470 | 61.1520 | 80.4920 | 17.8100 | 50 | 0 |
| fast_brief_v1 | office_room_traj0_loop | 56.4650 | 56.7260 | 79.4760 | 19.2600 | 50 | 0 |
| fast_brief_v1 | ocean_Easy_P000 | 1.3640 | 1.3350 | 1.6880 | 781.4600 | 50 | 48 |
| fast_brief_v1 | abandonedfactory_Easy_P000 | 23.0460 | 6.9650 | 104.7120 | 213.6500 | 50 | 47 |
| orb_brisk_v1 | living_room_traj1_loop | 68.0660 | 68.3090 | 94.2920 | 15.3300 | 50 | 0 |
| orb_brisk_v1 | office_room_traj0_loop | 68.8550 | 70.4930 | 88.6450 | 15.3300 | 50 | 0 |
| orb_brisk_v1 | ocean_Easy_P000 | 28.3300 | 16.6870 | 74.0330 | 84.5900 | 50 | 46 |
| orb_brisk_v1 | abandonedfactory_Easy_P000 | 837.9580 | 858.6960 | 939.6160 | 1.2300 | 50 | 46 |
| faster_orb_v1 | living_room_traj1_loop | 58.2510 | 55.3040 | 81.5070 | 18.6300 | 50 | 0 |
| faster_orb_v1 | office_room_traj0_loop | 54.2870 | 53.4390 | 79.2340 | 19.7700 | 50 | 0 |
| faster_orb_v1 | ocean_Easy_P000 | 2.0150 | 1.9970 | 2.3730 | 500.0100 | 50 | 49 |
| faster_orb_v1 | abandonedfactory_Easy_P000 | 23.7560 | 19.9090 | 76.6950 | 161.4300 | 50 | 46 |

## 3. Complete Benchmark Raw Data

| config_id | descriptor_label | dataset | sequence | ate_alignment | ate_scale | ate_rmse_m | ate_mean_m | ate_median_m | ate_std_m | ate_n_frames | rpe_delta_frames | rpe_trans_rmse_m | rpe_trans_mean_m | rpe_trans_median_m | rpe_rot_rmse_deg | rpe_rot_mean_deg | rpe_n_pairs | total_frames | success_frames | failed_frames | tracking_success_pct | is_degenerate | mean_frame_time_ms | median_frame_time_ms | p95_frame_time_ms | mean_fps | median_fps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| orb_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0949 | 0.0331 | 0.0306 | 0.0278 | 0.0127 | 50 | 1 | 0.9102 | 0.9102 | 0.9094 | 0.3867 | 0.3097 | 49 | 50 | 49 | 0 | 100.0000 | No | 52.0970 | 33.8170 | 155.3480 | 25.7800 | 29.5700 |
| orb_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | sim3 | 0.0949 | 0.0331 | 0.0306 | 0.0278 | 0.0127 | 50 | 1 | 0.9102 | 0.9102 | 0.9094 | 0.3867 | 0.3097 | 49 | 50 | 49 | 0 | 100.0000 | No | 87.4270 | 73.0300 | 157.0180 | 12.5600 | 13.6900 |
| orb_orb_v1 | ORB | tartanair | ocean_Easy_P000 | sim3 | 3.7524 | 2.1199 | 1.8308 | 1.8263 | 1.0687 | 50 | 1 | 0.2100 | 0.1703 | 0.1525 | 23.1712 | 3.3102 | 49 | 50 | 1 | 48 | 2.0400 | Yes | 851.9180 | 852.6400 | 943.4540 | 1.1800 | 1.1700 |
| orb_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | sim3 | 1.6298 | 0.8262 | 0.7617 | 0.6780 | 0.3200 | 50 | 1 | 0.3364 | 0.2033 | 0.1239 | 0.0000 | 0.0000 | 49 | 50 | 4 | 45 | 8.1600 | Yes | 733.2270 | 840.0400 | 950.5880 | 1.5800 | 1.1900 |
| fast_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0931 | 0.0233 | 0.0211 | 0.0196 | 0.0099 | 50 | 1 | 0.9088 | 0.9088 | 0.9088 | 0.3115 | 0.2473 | 49 | 50 | 49 | 0 | 100.0000 | No | 34.8730 | 31.6150 | 58.7400 | 31.5300 | 31.6300 |
| fast_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | sim3 | 0.0931 | 0.0233 | 0.0211 | 0.0196 | 0.0099 | 50 | 1 | 0.9088 | 0.9088 | 0.9088 | 0.3115 | 0.2473 | 49 | 50 | 49 | 0 | 100.0000 | No | 33.5080 | 31.3920 | 53.6650 | 32.4000 | 31.8500 |
| fast_orb_v1 | ORB | tartanair | ocean_Easy_P000 | sim3 | 1.0000 | 2.1841 | 1.9063 | 1.8994 | 1.0660 | 50 | 1 | 0.1526 | 0.1526 | 0.1525 | 0.0000 | 0.0000 | 49 | 50 | 0 | 49 | 0.0000 | Yes | 1.7590 | 1.7260 | 1.9960 | 573.6700 | 579.4100 |
| fast_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | sim3 | 2.8215 | 1.0344 | 0.8606 | 0.7917 | 0.5739 | 50 | 1 | 0.2387 | 0.1600 | 0.1238 | 33.5892 | 6.7676 | 49 | 50 | 2 | 47 | 4.0800 | Yes | 18.2740 | 12.3480 | 47.7030 | 212.1800 | 80.9900 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | living_room_traj1_loop | sim3 | 0.0936 | 0.0218 | 0.0191 | 0.0181 | 0.0105 | 50 | 1 | 0.9090 | 0.9090 | 0.9087 | 0.4388 | 0.2946 | 49 | 50 | 49 | 0 | 100.0000 | No | 60.8470 | 61.1520 | 80.4920 | 17.8100 | 16.3500 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | icl_nuim | office_room_traj0_loop | sim3 | 0.0936 | 0.0218 | 0.0191 | 0.0181 | 0.0105 | 50 | 1 | 0.9090 | 0.9090 | 0.9087 | 0.4388 | 0.2946 | 49 | 50 | 49 | 0 | 100.0000 | No | 56.4650 | 56.7260 | 79.4760 | 19.2600 | 17.6300 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | ocean_Easy_P000 | sim3 | 3.7906 | 1.4162 | 1.1699 | 0.9133 | 0.7982 | 50 | 1 | 0.2032 | 0.1689 | 0.1525 | 24.2624 | 3.4661 | 49 | 50 | 1 | 48 | 2.0400 | Yes | 1.3640 | 1.3350 | 1.6880 | 781.4600 | 748.9000 |
| fast_brief_v1 | ManualBRIEF-Gaussian-256 | tartanair | abandonedfactory_Easy_P000 | sim3 | 2.7694 | 1.0634 | 0.8794 | 0.6934 | 0.5979 | 50 | 1 | 0.2489 | 0.1624 | 0.1237 | 13.5045 | 2.6839 | 49 | 50 | 2 | 47 | 4.0800 | Yes | 23.0460 | 6.9650 | 104.7120 | 213.6500 | 143.5700 |
| orb_brisk_v1 | BRISK | icl_nuim | living_room_traj1_loop | sim3 | 0.0938 | 0.0340 | 0.0316 | 0.0298 | 0.0126 | 50 | 1 | 0.9093 | 0.9093 | 0.9086 | 0.3176 | 0.2741 | 49 | 50 | 49 | 0 | 100.0000 | No | 68.0660 | 68.3090 | 94.2920 | 15.3300 | 14.6400 |
| orb_brisk_v1 | BRISK | icl_nuim | office_room_traj0_loop | sim3 | 0.0938 | 0.0340 | 0.0316 | 0.0298 | 0.0126 | 50 | 1 | 0.9093 | 0.9093 | 0.9086 | 0.3176 | 0.2741 | 49 | 50 | 49 | 0 | 100.0000 | No | 68.8550 | 70.4930 | 88.6450 | 15.3300 | 14.1900 |
| orb_brisk_v1 | BRISK | tartanair | ocean_Easy_P000 | sim3 | 2.5258 | 1.4303 | 1.2426 | 1.2374 | 0.7083 | 50 | 1 | 0.3054 | 0.2094 | 0.1529 | 20.5306 | 5.0487 | 49 | 50 | 3 | 46 | 6.1200 | Yes | 28.3300 | 16.6870 | 74.0330 | 84.5900 | 59.9300 |
| orb_brisk_v1 | BRISK | tartanair | abandonedfactory_Easy_P000 | sim3 | 1.7676 | 1.5516 | 1.2150 | 0.8859 | 0.9650 | 50 | 1 | 0.2734 | 0.1767 | 0.1238 | 42.4936 | 10.5093 | 49 | 50 | 3 | 46 | 6.1200 | Yes | 837.9580 | 858.6960 | 939.6160 | 1.2300 | 1.1600 |
| faster_orb_v1 | ORB | icl_nuim | living_room_traj1_loop | sim3 | 0.0927 | 0.0231 | 0.0215 | 0.0212 | 0.0084 | 50 | 1 | 0.9086 | 0.9086 | 0.9088 | 0.4299 | 0.2862 | 49 | 50 | 49 | 0 | 100.0000 | No | 58.2510 | 55.3040 | 81.5070 | 18.6300 | 18.0800 |
| faster_orb_v1 | ORB | icl_nuim | office_room_traj0_loop | sim3 | 0.0927 | 0.0231 | 0.0215 | 0.0212 | 0.0084 | 50 | 1 | 0.9086 | 0.9086 | 0.9088 | 0.4299 | 0.2862 | 49 | 50 | 49 | 0 | 100.0000 | No | 54.2870 | 53.4390 | 79.2340 | 19.7700 | 18.7100 |
| faster_orb_v1 | ORB | tartanair | ocean_Easy_P000 | sim3 | 1.0000 | 2.1841 | 1.9063 | 1.8994 | 1.0660 | 50 | 1 | 0.1526 | 0.1526 | 0.1525 | 0.0000 | 0.0000 | 49 | 50 | 0 | 49 | 0.0000 | Yes | 2.0150 | 1.9970 | 2.3730 | 500.0100 | 500.7800 |
| faster_orb_v1 | ORB | tartanair | abandonedfactory_Easy_P000 | sim3 | 2.0838 | 1.0756 | 0.9466 | 0.8126 | 0.5106 | 50 | 1 | 0.2845 | 0.1797 | 0.1237 | 25.0292 | 6.1358 | 49 | 50 | 3 | 46 | 6.1200 | Yes | 23.7560 | 19.9090 | 76.6950 | 161.4300 | 50.2300 |

*Generated automatically. ATE uses Sim(3) alignment unless noted.*
