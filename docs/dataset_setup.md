# Dataset Setup Guide

This guide explains how to download and organize the datasets
required to run the visual odometry experiments.

> **Important:** Do not commit any dataset files to the repository.
> The `data/` directory is listed in `.gitignore`.

---

## Directory Structure Expected

```
data/
├── icl_nuim/
│   ├── living_room_traj0_loop/
│   │   ├── rgb/            ← 0000.png, 0001.png, ...
│   │   ├── depth/          ← (optional, not used by monocular VO)
│   │   ├── rgb.txt
│   │   └── groundtruth.txt
│   └── living_room_traj1_loop/
│       └── (same structure)
│
└── tartanair/
    └── ocean/
        └── Easy/
            └── P000/
                ├── image_left/    ← 000000.png, 000001.png, ...
                └── pose_left.txt
```

---

## ICL-NUIM

**Official page:** https://www.doc.ic.ac.uk/~ahanda/VaFRIC/iclnuim.html

**Recommended sequence:** `living_room_traj1_loop`

### Download Steps

1. Visit the official page and download the TUM-compatible archives:
   - `living_room_traj1_loop.tar.gz`

2. Extract to `data/icl_nuim/`:

   ```
   tar -xzf living_room_traj1_loop.tar.gz -C data/icl_nuim/
   ```

3. Verify structure:

   ```
   data/icl_nuim/living_room_traj1_loop/
       rgb/
       rgb.txt
       groundtruth.txt
   ```

4. Update `configs/datasets/icl_nuim.yaml` if you change the path or sequence.

---

## TartanAir

**Official page:** https://tartanair.org/  
**Tools:** https://github.com/castacks/tartanair_tools

**Recommended sequence:** `ocean / Easy / P000`

### Download Steps

Option A — TartanAir Python tools:

```bash
pip install tartanair
python -c "
import tartanair
tartanair.download(
    env='ocean',
    difficulty='Easy',
    trajectory_id=['P000'],
    modality=['image', 'pose'],
    camera_name=['lcam_front'],
    unzip=True,
    destination='data/tartanair',
)
"
```

Option B — Manual download from the portal (zip per trajectory):

1. Visit https://tartanair.org/ and navigate to **ocean → Easy → P000**.
2. Download `image_left.zip` and `pose_left.txt`.
3. Extract images to `data/tartanair/ocean/Easy/P000/image_left/`.
4. Place `pose_left.txt` at `data/tartanair/ocean/Easy/P000/pose_left.txt`.

---

## Verifying Data Integrity

After setup, run the environment check:

```bash
python check_env.py
```

To quickly test dataset loading (no actual VO run):

```python
from src.datasets.icl_nuim import ICLNUIMDataset
ds = ICLNUIMDataset("data/icl_nuim/living_room_traj1_loop")
print(f"Loaded {len(ds)} frames")
print(f"Camera K:\n{ds.camera.K}")
```
