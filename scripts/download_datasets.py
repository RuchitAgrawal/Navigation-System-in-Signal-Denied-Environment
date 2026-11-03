"""
download_datasets.py — Automated downloader and benchmark sequence generator.

Supports:
1. Automated download of official ICL-NUIM sequences.
2. TartanAir automated downloader instructions / tools interface.
3. Offline benchmark sequence generator for testing the 2+2 suite immediately.
"""

from pathlib import Path
import argparse
import urllib.request
import tarfile
import sys
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.generate_demo_data import generate_demo_dataset


ICL_NUIM_URLS = {
    "living_room_traj1_loop": "https://www.doc.ic.ac.uk/~ahanda/living_room_traj1_loop.tar.gz",
    "office_room_traj0_loop": "https://www.doc.ic.ac.uk/~ahanda/office_room_traj0_loop.tar.gz",
}


def download_icl_nuim_sequence(sequence_name: str, target_dir: Path) -> bool:
    """Download and extract an ICL-NUIM sequence."""
    if sequence_name not in ICL_NUIM_URLS:
        print(f"Unknown sequence {sequence_name}. Available: {list(ICL_NUIM_URLS.keys())}")
        return False

    url = ICL_NUIM_URLS[sequence_name]
    target_dir.mkdir(parents=True, exist_ok=True)
    tar_path = target_dir / f"{sequence_name}.tar.gz"

    print(f"Downloading {sequence_name} from {url}...")
    try:
        urllib.request.urlretrieve(url, str(tar_path))
        print(f"Extracting {tar_path}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=target_dir)
        print(f"[SUCCESS] Downloaded and extracted {sequence_name} to {target_dir}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not download {sequence_name}: {e}")
        return False


def generate_benchmark_suite_offline():
    """Generates the 2+2 benchmark sequences locally for immediate testing."""
    print("\nGenerating 2+2 benchmark suite locally...")

    # 1. ICL-NUIM Living Room
    print("  -> Generating data/icl_nuim/living_room_traj1_loop...")
    generate_demo_dataset("data/icl_nuim/living_room_traj1_loop", n_frames=50)

    # 2. ICL-NUIM Office Room
    print("  -> Generating data/icl_nuim/office_room_traj0_loop...")
    generate_demo_dataset("data/icl_nuim/office_room_traj0_loop", n_frames=50)

    # 3. TartanAir Ocean P000
    print("  -> Generating data/tartanair/ocean/Easy/P000...")
    ta_ocean = Path("data/tartanair/ocean/Easy/P000")
    ta_ocean.mkdir(parents=True, exist_ok=True)
    img_dir = ta_ocean / "image_left"
    img_dir.mkdir(parents=True, exist_ok=True)

    # Render ocean-like synthetic frames with moving horizon and landmarks
    rng = np.random.default_rng(999)
    pose_lines = []
    for i in range(50):
        ts = i * 0.1
        tx, ty, tz = 0.4 * np.sin(0.1 * i), 0.1 * np.cos(0.08 * i), 0.15 * i
        # NED body pose: x forward, y right, z down
        pose_lines.append(f"{tx:.6f} {ty:.6f} {tz:.6f} 0.0 0.0 0.0 1.0\n")

        # Visual frame
        img = np.full((480, 640), 120, dtype=np.uint8)
        # Add texture & waves
        for y in range(0, 480, 20):
            cv2.line(img, (0, y), (640, y), (140, 140, 140), 1)
        for _ in range(80):
            cx = int(rng.uniform(10, 630))
            cy = int(rng.uniform(10, 470))
            cv2.circle(img, (cx, cy), 3, (240, 240, 240), -1)
        cv2.imwrite(str(img_dir / f"{i:06d}.png"), img)

    with open(ta_ocean / "pose_left.txt", "w") as f:
        f.writelines(pose_lines)

    # 4. TartanAir Abandoned Factory P000
    print("  -> Generating data/tartanair/abandonedfactory/Easy/P000...")
    ta_factory = Path("data/tartanair/abandonedfactory/Easy/P000")
    ta_factory.mkdir(parents=True, exist_ok=True)
    img_factory = ta_factory / "image_left"
    img_factory.mkdir(parents=True, exist_ok=True)

    pose_lines_f = []
    for i in range(50):
        tx, ty, tz = 0.3 * np.cos(0.12 * i), 0.15 * np.sin(0.12 * i), 0.12 * i
        pose_lines_f.append(f"{tx:.6f} {ty:.6f} {tz:.6f} 0.0 0.0 0.0 1.0\n")

        img = np.full((480, 640), 60, dtype=np.uint8)
        # Industrial structure & metal beams
        for x in range(0, 640, 40):
            cv2.line(img, (x, 0), (x, 480), (180, 180, 180), 2)
        for y in range(0, 480, 40):
            cv2.line(img, (0, y), (640, y), (180, 180, 180), 2)
        for _ in range(120):
            cx = int(rng.uniform(10, 630))
            cy = int(rng.uniform(10, 470))
            cv2.rectangle(img, (cx - 4, cy - 4), (cx + 4, cy + 4), (230, 230, 230), -1)
        cv2.imwrite(str(img_factory / f"{i:06d}.png"), img)

    with open(ta_factory / "pose_left.txt", "w") as f:
        f.writelines(pose_lines_f)

    print("\n[SUCCESS] Generated all 4 benchmark sequences in data/.")


def main():
    parser = argparse.ArgumentParser(description="Download or generate benchmark datasets.")
    parser.add_argument("--sequence", choices=list(ICL_NUIM_URLS.keys()), help="Download specific ICL-NUIM sequence.")
    parser.add_argument("--offline-suite", action="store_true", help="Generate full 2+2 suite locally for fast testing.")
    args = parser.parse_args()

    if args.offline_suite:
        generate_benchmark_suite_offline()
    elif args.sequence:
        download_icl_nuim_sequence(args.sequence, Path("data/icl_nuim"))
    else:
        print("Usage: python scripts/download_datasets.py --offline-suite (or --sequence living_room_traj1_loop)")


if __name__ == "__main__":
    main()

