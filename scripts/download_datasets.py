"""
download_datasets.py — Automated downloader and benchmark sequence generator.

Supports:
1. Automated download of official ICL-NUIM sequences (with retry + progress bar).
2. TartanAir automated downloader instructions / tools interface.
3. Offline benchmark sequence generator for testing the 2+2 suite immediately.
4. --manual-steps flag: prints step-by-step browser download instructions.

Usage
-----
  python scripts/download_datasets.py --sequence living_room_traj1_loop
  python scripts/download_datasets.py --manual-steps
  python scripts/download_datasets.py --generate-offline
"""

from pathlib import Path
import argparse
import shutil
import time
import urllib.request
import tarfile
import sys
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).parent.parent))
from scipy.spatial.transform import Rotation
from scripts.generate_demo_data import generate_demo_dataset
from src.geometry.transforms import _R_CAM_NED


ICL_NUIM_URLS = {
    "living_room_traj1_loop": "https://www.doc.ic.ac.uk/~ahanda/living_room_traj1_loop.tar.gz",
    "office_room_traj0_loop": "https://www.doc.ic.ac.uk/~ahanda/office_room_traj0_loop.tar.gz",
}

ICL_NUIM_GT_URLS = {
    "living_room_traj1_loop": (
        "https://www.doc.ic.ac.uk/~ahanda/VaFRIC/livingRoom1.gt.freiburg",
        "livingRoom1.gt.freiburg",
    ),
    "office_room_traj0_loop": (
        "https://www.doc.ic.ac.uk/~ahanda/VaFRIC/office0.gt.freiburg",
        "office0.gt.freiburg",
    ),
}

MANUAL_STEPS = """
══════════════════════════════════════════════════════════
  ICL-NUIM Manual Download Instructions
══════════════════════════════════════════════════════════

The automated download requires access to Imperial College
London's server. If it fails, follow these steps:

Step 1 — Open this page in your browser:
  https://www.doc.ic.ac.uk/~ahanda/VaFRIC/iclnuim.html

Step 2 — Download these two files:
  • living_room_traj1_loop.tar.gz     (~700 MB)
  • livingRoom1.gt.freiburg           (ground truth, ~few KB)

  Both links are under "RGB-D Dataset" on that page.

Step 3 — Place the files here:
  d:\\projects\\minor-project\\data\\icl_nuim\\

  So the layout is:
    data/icl_nuim/living_room_traj1_loop.tar.gz
    data/icl_nuim/livingRoom1.gt.freiburg

Step 4 — Tell the agent to continue. It will extract the
  archive and run the benchmark automatically.

══════════════════════════════════════════════════════════
"""


def _progress_hook(block_count: int, block_size: int, total_size: int) -> None:
    """Display a simple download progress bar."""
    if total_size <= 0:
        print(f"\r  Downloaded {block_count * block_size // 1024 // 1024} MB...", end="", flush=True)
        return
    downloaded = block_count * block_size
    pct = min(100, int(downloaded * 100 / total_size))
    mb_done = downloaded / 1024 / 1024
    mb_total = total_size / 1024 / 1024
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    print(f"\r  [{bar}] {pct:3d}%  {mb_done:.1f}/{mb_total:.1f} MB", end="", flush=True)


def download_icl_nuim_sequence(
    sequence_name: str,
    target_dir: Path,
    max_retries: int = 3,
    retry_delay_s: float = 5.0,
) -> bool:
    """Download and extract an ICL-NUIM sequence with retry and progress display.

    Parameters
    ----------
    sequence_name : one of the keys in ICL_NUIM_URLS
    target_dir    : destination directory (created if absent)
    max_retries   : number of download attempts before giving up
    retry_delay_s : seconds to wait between retries

    Returns
    -------
    True on success, False on failure (prints manual instructions on failure).
    """
    if sequence_name not in ICL_NUIM_URLS:
        print(f"[ERROR] Unknown sequence '{sequence_name}'.")
        print(f"        Available: {list(ICL_NUIM_URLS.keys())}")
        return False

    url = ICL_NUIM_URLS[sequence_name]
    gt_url, gt_filename = ICL_NUIM_GT_URLS[sequence_name]
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    tar_path = target_dir / f"{sequence_name}.tar.gz"
    gt_path = target_dir / gt_filename

    # ── Download main archive ────────────────────────────────────────────────
    for attempt in range(1, max_retries + 1):
        print(f"\n[{attempt}/{max_retries}] Downloading {sequence_name}")
        print(f"  URL : {url}")
        print(f"  Dest: {tar_path}")
        try:
            urllib.request.urlretrieve(url, str(tar_path), reporthook=_progress_hook)
            print()  # newline after progress bar
            break
        except Exception as exc:
            print(f"\n  [WARN] Attempt {attempt} failed: {exc}")
            if tar_path.exists():
                tar_path.unlink()
            if attempt < max_retries:
                print(f"  Retrying in {retry_delay_s}s...")
                time.sleep(retry_delay_s)
            else:
                print("\n[ERROR] All download attempts failed.")
                print(MANUAL_STEPS)
                return False

    # ── Download ground-truth file ───────────────────────────────────────────
    if not gt_path.exists():
        print(f"\nDownloading ground truth: {gt_filename}")
        try:
            urllib.request.urlretrieve(gt_url, str(gt_path), reporthook=_progress_hook)
            print()
        except Exception as exc:
            print(f"\n  [WARN] Ground truth download failed: {exc}")
            print(f"  You can download it manually from:\n  {gt_url}")

    # ── Extract archive ──────────────────────────────────────────────────────
    print(f"\nExtracting {tar_path.name}  ({tar_path.stat().st_size / 1024 / 1024:.1f} MB)...")
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=target_dir)
        # Remove archive to save space
        tar_path.unlink()
        print(f"[SUCCESS] {sequence_name} extracted to {target_dir}")
        return True
    except Exception as exc:
        print(f"[ERROR] Extraction failed: {exc}")
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

    # 4. TartanAir Abandoned Factory P000 (3D projective industrial landmarks)
    print("  -> Generating data/tartanair/abandonedfactory/Easy/P000...")
    ta_factory = Path("data/tartanair/abandonedfactory/Easy/P000")
    ta_factory.mkdir(parents=True, exist_ok=True)
    img_factory = ta_factory / "image_left"
    img_factory.mkdir(parents=True, exist_ok=True)

    width, height = 640, 480
    fx, fy, cx, cy = 320.0, 320.0, 320.0, 240.0
    rng_f = np.random.default_rng(777)
    n_landmarks = 600
    landmarks = []
    marker_types = []
    marker_sizes = []
    for _ in range(n_landmarks):
        x = rng_f.uniform(-4.0, 4.0)
        y = rng_f.uniform(-3.0, 3.0)
        z = rng_f.uniform(1.5, 12.0)
        landmarks.append([x, y, z])
        marker_types.append(int(rng_f.integers(0, 3)))
        marker_sizes.append(rng_f.uniform(0.04, 0.12))
    landmarks = np.array(landmarks, dtype=np.float64)

    pose_lines_f = []
    for i in range(50):
        tx = 0.25 * np.sin(0.1 * i)
        ty = 0.10 * np.cos(0.08 * i)
        tz = 0.10 * i
        t_wc = np.array([tx, ty, tz])

        yaw = 0.02 * np.sin(0.1 * i)
        pitch = 0.015 * np.cos(0.1 * i)
        rot = Rotation.from_euler("yxz", [yaw, pitch, 0.0])
        R_wc = rot.as_matrix()

        # TartanAir NED convention: R_ned = R_wc @ _R_CAM_NED
        R_ned = R_wc @ _R_CAM_NED
        q_ned = Rotation.from_matrix(R_ned).as_quat()
        t_ned = t_wc
        pose_lines_f.append(f"{t_ned[0]:.6f} {t_ned[1]:.6f} {t_ned[2]:.6f} {q_ned[0]:.6f} {q_ned[1]:.6f} {q_ned[2]:.6f} {q_ned[3]:.6f}\n")

        # Project 3D landmarks into camera frame: P_c = (landmarks - t_wc) @ R_wc
        P_c = (landmarks - t_wc) @ R_wc

        img = np.full((height, width, 3), 50, dtype=np.uint8)
        # Industrial structural framework (beams and walls)
        for y_line in range(0, height, 40):
            cv2.line(img, (0, y_line), (width, y_line), (35, 35, 35), 1)
        for x_line in range(0, width, 40):
            cv2.line(img, (x_line, 0), (x_line, height), (35, 35, 35), 1)

        for pt, m_type, m_size in zip(P_c, marker_types, marker_sizes):
            if pt[2] <= 0.4:
                continue
            u = int(fx * pt[0] / pt[2] + cx)
            v = int(fy * pt[1] / pt[2] + cy)
            radius = max(2, int(fx * m_size / pt[2]))
            if 5 <= u < width - 5 and 5 <= v < height - 5:
                if m_type == 0:
                    cv2.circle(img, (u, v), radius, (220, 220, 220), -1)
                elif m_type == 1:
                    cv2.rectangle(img, (u - radius, v - radius), (u + radius, v + radius), (200, 240, 200), -1)
                else:
                    pts = np.array([[u, v - radius], [u - radius, v + radius], [u + radius, v + radius]])
                    cv2.drawContours(img, [pts], 0, (240, 200, 200), -1)

        cv2.imwrite(str(img_factory / f"{i:06d}.png"), img)

    with open(ta_factory / "pose_left.txt", "w") as f:
        f.writelines(pose_lines_f)

    print("\n[SUCCESS] Generated all 4 benchmark sequences in data/.")


def main():
    parser = argparse.ArgumentParser(
        description="Download or generate benchmark datasets for the VO project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download ICL-NUIM living room sequence (real data, ~700 MB):
  python scripts/download_datasets.py --sequence living_room_traj1_loop

  # Print manual browser download steps (use if automated download fails):
  python scripts/download_datasets.py --manual-steps

  # Generate offline 2+2 synthetic benchmark suite (no internet needed):
  python scripts/download_datasets.py --offline-suite
        """,
    )
    parser.add_argument(
        "--sequence",
        choices=list(ICL_NUIM_URLS.keys()),
        help="ICL-NUIM sequence to download (automated, with retry and progress bar).",
    )
    parser.add_argument(
        "--manual-steps",
        action="store_true",
        help="Print step-by-step browser download instructions for ICL-NUIM.",
    )
    parser.add_argument(
        "--offline-suite",
        action="store_true",
        help="Generate the full 2+2 synthetic benchmark suite locally (no download needed).",
    )
    parser.add_argument(
        "--data-root",
        default="data",
        help="Root directory for downloaded datasets (default: data/).",
    )
    args = parser.parse_args()

    if args.manual_steps:
        print(MANUAL_STEPS)
    elif args.offline_suite:
        generate_benchmark_suite_offline()
    elif args.sequence:
        dest = Path(args.data_root) / "icl_nuim"
        success = download_icl_nuim_sequence(args.sequence, dest)
        if not success:
            print("\nTip: Run with --manual-steps to see browser download instructions.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

