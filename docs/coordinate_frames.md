# Coordinate Frame Conventions

## Camera Convention (OpenCV)
All images and camera operations follow the OpenCV camera convention:
- x-axis: rightward
- y-axis: downward
- z-axis: forward (into the scene)

## World Frame (ICL-NUIM convention)
- Right-handed
- Y-up
- Matches the ICL-NUIM ground-truth frame

## Pose Storage: T_wc
All poses are stored as 4x4 float64 T_wc matrices (camera-to-world).

    p_world = T_wc @ p_camera

Reading the camera position in world coordinates:

    pos_world = T_wc[:3, 3]

## TartanAir Convention
Pose files use NED body frame (North-East-Down).
Conversion to camera frame is applied during loading in src/datasets/tartanair.py.

