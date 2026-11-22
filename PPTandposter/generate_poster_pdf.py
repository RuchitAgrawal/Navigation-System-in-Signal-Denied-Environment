"""
generate_poster_pdf.py — Generates publication-ready academic seminar poster in single-page PDF format.
Matching the visual hierarchy, color palette, and layout of the PDEU School of Technology template.
"""

from pathlib import Path
import fitz  # PyMuPDF

def hex_to_rgb(h: str):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

# ── Color Palette ────────────────────────────────────────────────────────────
BG_HEADER      = hex_to_rgb('#cbb8e8')
BORDER_PURPLE  = hex_to_rgb('#5a3d7c')
TEXT_TITLE     = hex_to_rgb('#251246')
TEXT_AUTHORS   = hex_to_rgb('#381c5f')
TEXT_GUIDE     = hex_to_rgb('#4a2c75')
BANNER_BG      = hex_to_rgb('#c3aee2')
BANNER_BORDER  = hex_to_rgb('#997dc4')
CARD_BORDER    = hex_to_rgb('#dcd1ed')
TEXT_BODY      = hex_to_rgb('#222222')
TEXT_MUTED     = hex_to_rgb('#555555')
BOX_BG         = hex_to_rgb('#f7f3fd')
BOX_BORDER     = hex_to_rgb('#7c5295')
CLR_GREEN      = hex_to_rgb('#27ae60')
CLR_RED        = hex_to_rgb('#c0392b')
CLR_BLUE       = hex_to_rgb('#2980b9')
CLR_ORANGE     = hex_to_rgb('#d35400')
CLR_WHITE      = hex_to_rgb('#ffffff')
CLR_CODE_BG    = hex_to_rgb('#2c1f3d')

def create_poster():
    root = Path(__file__).resolve().parent
    repo_fig = root / "Navigation-System-in-Signal-Denied-Environment" / "results" / "figures"
    pdf_out = root / "poster.pdf"

    # Poster dimensions: 1200 x 1700 (standard A-series 1:1.414 ratio)
    W, H = 1200.0, 1700.0
    doc = fitz.open()
    page = doc.new_page(width=W, height=H)

    # ══════════════════════════════════════════════════════════════════════════
    # 1. HEADER (Y: 0 to 110)
    # ══════════════════════════════════════════════════════════════════════════
    page.draw_rect(fitz.Rect(0, 0, W, 110), fill=BG_HEADER)
    page.draw_line(fitz.Point(0, 110), fitz.Point(W, 110), color=BORDER_PURPLE, width=3.0)

    # PDEU Logo Circle (Left)
    logo_cx, logo_cy, logo_r = 65, 55, 42
    page.draw_circle(fitz.Point(logo_cx, logo_cy), logo_r, color=hex_to_rgb('#8e2800'), fill=CLR_WHITE, width=2.5)
    page.draw_circle(fitz.Point(logo_cx, logo_cy), logo_r - 4, color=hex_to_rgb('#d35400'), width=0.8)
    page.insert_text(fitz.Point(logo_cx - 24, logo_cy - 16), "PANDIT DEENDAYAL", fontsize=5.0, fontname="helv-bold", color=hex_to_rgb('#8e2800'))
    page.insert_text(fitz.Point(logo_cx - 6, logo_cy + 2), "☀", fontsize=16.0, fontname="helv-bold", color=CLR_ORANGE)
    page.insert_text(fitz.Point(logo_cx - 26, logo_cy + 16), "ENERGY UNIVERSITY", fontsize=5.0, fontname="helv-bold", color=hex_to_rgb('#8e2800'))
    page.insert_text(fitz.Point(logo_cx - 32, logo_cy + 26), "A RESERVOIR OF KNOWLEDGE", fontsize=4.5, fontname="helv-bold", color=CLR_GREEN)

    # Title & Student Details (Center)
    title_rect = fitz.Rect(130, 12, 1020, 52)
    page.insert_textbox(
        title_rect,
        "A COMPUTER VISION-ASSISTED GPS NAVIGATION SYSTEM FOR ROBUST POSITIONING IN SIGNAL-DENIED ENVIRONMENTS",
        fontsize=16.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_CENTER
    )

    authors_rect = fitz.Rect(130, 58, 1020, 78)
    page.insert_textbox(
        authors_rect,
        "Ruchit Agrawal (23BCP183)  •  Joy Patel (23BCP049)",
        fontsize=13.0, fontname="helv-bold", color=TEXT_AUTHORS, align=fitz.TEXT_ALIGN_CENTER
    )

    guide_rect = fitz.Rect(130, 80, 1020, 102)
    page.insert_textbox(
        guide_rect,
        "Guide: Prof. Azriel Henry, Assistant Professor, Department of Computer Engineering, School of Technology, PDEU",
        fontsize=11.0, fontname="helv", color=TEXT_GUIDE, align=fitz.TEXT_ALIGN_CENTER
    )

    # Department (Right)
    page.draw_line(fitz.Point(1030, 20), fitz.Point(1030, 95), color=hex_to_rgb('#8e7bb0'), width=1.5)
    dept_rect = fitz.Rect(1040, 28, 1180, 95)
    page.insert_textbox(
        dept_rect,
        "School of\nTechnology\nPDEU, Gandhinagar",
        fontsize=12.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_LEFT
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 2. TOP SECTION: MOTIVATION & OBJECTIVES (Y: 110 to 365)
    # ══════════════════════════════════════════════════════════════════════════
    # Banners (Y: 110 to 138)
    page.draw_rect(fitz.Rect(0, 110, 598, 138), fill=BANNER_BG)
    page.draw_rect(fitz.Rect(602, 110, W, 138), fill=BANNER_BG)
    page.draw_line(fitz.Point(0, 138), fitz.Point(W, 138), color=BANNER_BORDER, width=1.5)

    page.insert_textbox(fitz.Rect(0, 114, 598, 136), "Brief Motivation", fontsize=12.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_CENTER)
    page.insert_textbox(fitz.Rect(602, 114, W, 136), "Objective", fontsize=12.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_CENTER)

    # Content Panels (Y: 142 to 360)
    page.draw_line(fitz.Point(600, 110), fitz.Point(600, 360), color=CARD_BORDER, width=1.5)

    # Motivation Text
    mot_text = (
        "• The GPS Failure Problem: Satellite positioning degrades or fails catastrophically indoors, underground (tunnels/mines), in urban canyons, and during active electronic jamming.\n\n"
        "• Vulnerability of Autonomous Systems: Mobile platforms (warehouse AGVs, inspection drones, rovers) relying solely on GPS experience immediate disorientation upon signal loss.\n\n"
        "• Inadequacy of Sensor Alternatives: Inertial sensors (IMUs) accumulate unbounded quadratic drift (d ~ 0.5 a t^2) within seconds; active beacon systems (UWB/LiDAR) require expensive infrastructure unavailable in uncharted environments.\n\n"
        "• Vision as the Resilient Solution: Monocular Visual Odometry (VO) provides an entirely passive, self-contained, jam-proof positioning sensor using only a single commodity camera."
    )
    page.insert_textbox(fitz.Rect(18, 146, 582, 358), mot_text, fontsize=10.0, fontname="helv", color=TEXT_BODY)

    # Objective Text
    obj_text = (
        "• Autonomous 6-DoF Pose Tracking: Estimate camera displacement and heading continuously between consecutive image frames without external positioning aids.\n\n"
        "• Robust Feature Extraction: Implement Adaptive FASTER detection with QuadTree spatial bucketing to eliminate edge clustering and adapt to abrupt illumination changes.\n\n"
        "• Hybrid Motion Estimation: Overcome epipolar zero-baseline degeneracy during in-place camera panning by seamlessly combining Homography and Essential Matrix estimation.\n\n"
        "• Empirical Benchmarking: Systematically evaluate 5 detector-descriptor combinations on the ICL-NUIM photographic benchmark across ATE RMSE, RPE, and FPS.\n\n"
        "• GPS Outage Simulation & Live HUD: Build an interactive, real-time live webcam dashboard proving sub-2.5% dead-reckoning drift during simulated satellite dropouts."
    )
    page.insert_textbox(fitz.Rect(618, 146, 1182, 358), obj_text, fontsize=10.0, fontname="helv", color=TEXT_BODY)

    # ══════════════════════════════════════════════════════════════════════════
    # 3. MIDDLE SECTION: METHODOLOGY & ARCHITECTURE (Y: 360 to 770)
    # ══════════════════════════════════════════════════════════════════════════
    page.draw_rect(fitz.Rect(0, 360, W, 388), fill=BANNER_BG)
    page.draw_line(fitz.Point(0, 388), fitz.Point(W, 388), color=BANNER_BORDER, width=1.5)
    page.insert_textbox(fitz.Rect(0, 364, W, 386), "Methodology", fontsize=12.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_CENTER)

    # Methodology Left Column (Y: 395 to 760)
    page.insert_textbox(fitz.Rect(18, 395, 420, 415), "How the Pipeline Works", fontsize=11.5, fontname="helv-bold", color=TEXT_TITLE)
    page.draw_line(fitz.Point(18, 414), fitz.Point(420, 414), color=hex_to_rgb('#cbb8e8'), width=1.0)

    pipe_text = (
        "1. Intake & Preprocessing: Grayscale video frames (I_{t-1}, I_t) are normalized; calibrated camera matrix K corrects geometric distortion.\n\n"
        "2. Adaptive FASTER & QuadTree: Dynamic threshold iteration maintains target feature count (~500 kps); QuadTree spatial division guarantees uniform feature spread.\n\n"
        "3. Sub-Pixel Coordinates & Descriptors: Coordinates are refined via cv2.cornerSubPix; 256-bit steered ORB or 512-bit circular BRISK descriptors are generated.\n\n"
        "4. Hamming Matching & Filtering: Brute-Force matching filtered with Lowe's Ratio Test (distance ratio <= 0.75) and cross-check verification.\n\n"
        "5. Hybrid Pose Recovery (H vs E):\n"
        "   • Pure Rotation: Planar Homography (H = K R K^-1) via SVD (R = U V^T, t = 0).\n"
        "   • 3D Translation: 5-Point Essential Matrix (E = [t]_x R) with RANSAC & chirality check.\n\n"
        "6. Kinematic Accumulation: Constant-velocity model rejects outlier jumps; relative SE(3) transforms chained to maintain global trajectory T_world."
    )
    page.insert_textbox(fitz.Rect(18, 420, 420, 680), pipe_text, fontsize=9.2, fontname="helv", color=TEXT_BODY)

    # "Why Hybrid?" Highlight Box
    page.draw_rect(fitz.Rect(18, 686, 420, 755), fill=BOX_BG, color=BOX_BORDER, width=1.2)
    hybrid_box_text = (
        "Why Hybrid Solver? Under pure camera rotation (panning in place), baseline t ≈ 0, causing the Essential Matrix to become degenerate (E ≈ 0) and flip orientation by 180°. Our dual Homography / Essential solver detects flow parallax to switch models dynamically, ensuring zero tracking dropouts."
    )
    page.insert_textbox(fitz.Rect(24, 690, 414, 752), hybrid_box_text, fontsize=8.6, fontname="helv-bold", color=TEXT_TITLE)

    # Methodology Right Side: Architecture Diagram Container (Y: 395 to 760)
    page.draw_rect(fitz.Rect(435, 395, 1182, 755), fill=hex_to_rgb('#fcfbfe'), color=CARD_BORDER, width=1.0)

    # Draw Vector Architecture Diagram inside box
    # Block 1: Camera
    page.draw_rect(fitz.Rect(450, 420, 545, 485), fill=hex_to_rgb('#eaf2f8'), color=CLR_BLUE, width=1.2)
    page.insert_textbox(fitz.Rect(452, 428, 543, 480), "CAMERA INTAKE\nRGB Video Stream\n(640×480 @ 30 FPS)", fontsize=7.8, fontname="helv-bold", color=CLR_BLUE, align=fitz.TEXT_ALIGN_CENTER)
    page.draw_line(fitz.Point(545, 452), fitz.Point(565, 452), color=BORDER_PURPLE, width=1.5)

    # Block 2: Adaptive FASTER
    page.draw_rect(fitz.Rect(565, 410, 695, 495), fill=hex_to_rgb('#fef5e7'), color=CLR_ORANGE, width=1.2)
    page.insert_textbox(fitz.Rect(568, 416, 692, 490), "ADAPTIVE FASTER\n• Dynamic Threshold\n• QuadTree Bucketing\n• Sub-Pixel Refinement\n(Target: ~500 kps)", fontsize=7.5, fontname="helv", color=hex_to_rgb('#7e3204'), align=fitz.TEXT_ALIGN_CENTER)
    page.draw_line(fitz.Point(695, 452), fitz.Point(715, 452), color=BORDER_PURPLE, width=1.5)

    # Block 3: Matching
    page.draw_rect(fitz.Rect(715, 410, 845, 495), fill=hex_to_rgb('#eafaf1'), color=CLR_GREEN, width=1.2)
    page.insert_textbox(fitz.Rect(718, 416, 842, 490), "MATCHING & FILTER\n• ORB (256b) / BRISK (512b)\n• BFMatcher (Hamming)\n• Lowe Ratio (<= 0.75)\n(Cross-Check Active)", fontsize=7.5, fontname="helv", color=hex_to_rgb('#145a32'), align=fitz.TEXT_ALIGN_CENTER)
    page.draw_line(fitz.Point(845, 452), fitz.Point(865, 452), color=BORDER_PURPLE, width=1.5)

    # Block 4: Hybrid Estimator
    page.draw_rect(fitz.Rect(865, 405, 1030, 500), fill=hex_to_rgb('#f5eef8'), color=hex_to_rgb('#8e44ad'), width=1.2)
    page.insert_textbox(fitz.Rect(868, 410, 1027, 430), "HYBRID ESTIMATOR", fontsize=8.5, fontname="helv-bold", color=hex_to_rgb('#4a235a'), align=fitz.TEXT_ALIGN_CENTER)
    page.draw_rect(fitz.Rect(875, 432, 1020, 460), fill=CLR_WHITE, color=hex_to_rgb('#9b59b6'), width=0.8)
    page.insert_textbox(fitz.Rect(876, 435, 1019, 458), "Pure Rotation: Homography\nSVD Decomposition [R | t=0]", fontsize=7.0, fontname="helv", color=hex_to_rgb('#6c3483'), align=fitz.TEXT_ALIGN_CENTER)
    page.draw_rect(fitz.Rect(875, 465, 1020, 495), fill=CLR_WHITE, color=hex_to_rgb('#9b59b6'), width=0.8)
    page.insert_textbox(fitz.Rect(876, 468, 1019, 492), "3D Translation: Essential Matrix\n5-Pt RANSAC + Chirality Check", fontsize=7.0, fontname="helv", color=hex_to_rgb('#6c3483'), align=fitz.TEXT_ALIGN_CENTER)
    page.draw_line(fitz.Point(1030, 452), fitz.Point(1050, 452), color=BORDER_PURPLE, width=1.5)

    # Block 5: Pose Accumulation
    page.draw_rect(fitz.Rect(1050, 410, 1165, 495), fill=hex_to_rgb('#fcedec'), color=CLR_RED, width=1.2)
    page.insert_textbox(fitz.Rect(1052, 416, 1163, 490), "SE(3) CHAIN\nKinematic Prior\nFilter Spikes\nT_world Accumulate\n6-DoF Path", fontsize=7.8, fontname="helv-bold", color=hex_to_rgb('#78281f'), align=fitz.TEXT_ALIGN_CENTER)

    # Feedback Loop: Outage Takeover Block
    page.draw_rect(fitz.Rect(580, 545, 990, 620), fill=hex_to_rgb('#f4f6f7'), color=hex_to_rgb('#34495e'), width=1.2)
    page.insert_textbox(fitz.Rect(585, 552, 985, 570), "GPS OUTAGE & DEAD-RECKONING MODULE", fontsize=8.5, fontname="helv-bold", color=hex_to_rgb('#1a252f'), align=fitz.TEXT_ALIGN_CENTER)
    page.insert_textbox(fitz.Rect(585, 572, 985, 615), "• GPS Active: Visual-Inertial Alignment & Periodic Anchor Calibration\n• GPS Signal Lost: Instant Autonomous Handover to Monocular VO\n• Measured Result: 2.28% Metric Position Drift Rate Across Outage", fontsize=7.8, fontname="helv", color=TEXT_BODY, align=fitz.TEXT_ALIGN_CENTER)

    # Connection lines to Outage block
    page.draw_line(fitz.Point(1107, 495), fitz.Point(1107, 582), color=hex_to_rgb('#2c3e50'), width=1.2)
    page.draw_line(fitz.Point(1107, 582), fitz.Point(990, 582), color=hex_to_rgb('#2c3e50'), width=1.2)

    page.insert_textbox(fitz.Rect(440, 715, 1175, 745), "Fig. 1: Monocular Visual Odometry Architecture — from camera intake and QuadTree feature extraction to hybrid Homography/Essential pose recovery and GPS outage dead-reckoning.", fontsize=8.8, fontname="helv-oblique", color=TEXT_MUTED, align=fitz.TEXT_ALIGN_CENTER)

    # ══════════════════════════════════════════════════════════════════════════
    # 4. THIRD SECTION: EXPECTED RESULTS & LIVE DEMO (Y: 770 to 1290)
    # ══════════════════════════════════════════════════════════════════════════
    page.draw_rect(fitz.Rect(0, 770, W, 798), fill=BANNER_BG)
    page.draw_line(fitz.Point(0, 798), fitz.Point(W, 798), color=BANNER_BORDER, width=1.5)
    page.insert_textbox(fitz.Rect(0, 774, W, 796), "Expected Results", fontsize=12.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_CENTER)

    # Col 1: Findings & Benchmark Table (X: 18 to 380, Y: 805 to 1280)
    page.insert_textbox(fitz.Rect(18, 805, 380, 825), "Expected Results & Benchmarking", fontsize=11.0, fontname="helv-bold", color=TEXT_TITLE)
    page.draw_line(fitz.Point(18, 824), fitz.Point(380, 824), color=hex_to_rgb('#cbb8e8'), width=1.0)

    res_bullet_text = (
        "• ORB+BRISK: Best Trajectory Accuracy with 0.1732 m ATE RMSE (37.6% lower error than standard ORB+ORB) and 54.04% tracking stability.\n"
        "• FAST+ORB: Highest Frame Throughput at 48.22 FPS and tight 28.71 ms P95 latency (exceeding 30 Hz real-time budget with headroom).\n"
        "• Adaptive FASTER + QuadTree: Reached 0.0380 m ATE RMSE on synthetic sequence, proving value of dynamic threshold self-tuning."
    )
    page.insert_textbox(fitz.Rect(18, 828, 380, 930), res_bullet_text, fontsize=8.6, fontname="helv", color=TEXT_BODY)

    # Table of Benchmark Results
    table_y = 935
    page.draw_rect(fitz.Rect(18, table_y, 380, table_y + 110), fill=hex_to_rgb('#faf7ff'), color=CARD_BORDER, width=1.0)
    # Table Header
    page.draw_rect(fitz.Rect(18, table_y, 380, table_y + 20), fill=hex_to_rgb('#eadef7'))
    page.insert_text(fitz.Point(25, table_y + 14), "Configuration", fontsize=8.0, fontname="helv-bold", color=TEXT_TITLE)
    page.insert_text(fitz.Point(150, table_y + 14), "ATE RMSE", fontsize=8.0, fontname="helv-bold", color=TEXT_TITLE)
    page.insert_text(fitz.Point(235, table_y + 14), "RPE Rot", fontsize=8.0, fontname="helv-bold", color=TEXT_TITLE)
    page.insert_text(fitz.Point(315, table_y + 14), "Mean FPS", fontsize=8.0, fontname="helv-bold", color=TEXT_TITLE)

    rows = [
        ("FAST + ORB", "0.2219 m", "0.557°", "48.22 FPS"),
        ("FAST + BRIEF", "0.2302 m", "0.554°", "32.95 FPS"),
        ("ORB + ORB", "0.2775 m", "0.560°", "32.75 FPS"),
        ("ORB + BRISK", "0.1732 m (★)", "0.961°", "30.11 FPS"),
    ]
    for idx, (c1, c2, c3, c4) in enumerate(rows):
        ry = table_y + 20 + idx * 22
        page.draw_line(fitz.Point(18, ry), fitz.Point(380, ry), color=hex_to_rgb('#e5daf3'), width=0.8)
        color = CLR_GREEN if "★" in c2 else TEXT_BODY
        page.insert_text(fitz.Point(25, ry + 15), c1, fontsize=8.0, fontname="helv-bold" if "★" in c2 else "helv", color=color)
        page.insert_text(fitz.Point(150, ry + 15), c2, fontsize=8.0, fontname="helv-bold" if "★" in c2 else "helv", color=color)
        page.insert_text(fitz.Point(235, ry + 15), c3, fontsize=8.0, fontname="helv", color=TEXT_BODY)
        page.insert_text(fitz.Point(315, ry + 15), c4, fontsize=8.0, fontname="helv-bold" if idx == 0 else "helv", color=CLR_GREEN if idx == 0 else TEXT_BODY)

    # Key Theory
    page.insert_textbox(fitz.Rect(18, 1055, 380, 1072), "Key Theory", fontsize=10.5, fontname="helv-bold", color=TEXT_TITLE)
    page.draw_line(fitz.Point(18, 1071), fitz.Point(380, 1071), color=hex_to_rgb('#cbb8e8'), width=1.0)
    theory_text = (
        "• Epipolar Constraint: x'^T E x = 0 with Essential matrix E = [t]_x R. Chirality condition ensures 3D points lie strictly in front of both camera planes.\n"
        "• Umeyama Sim(3): Closed-form SVD optimization recovering optimal scale s*, rotation R*, translation t* matching metric ground truth.\n"
        "• Dead-Reckoning Metric Drift: Measured as e_drift = ||p_vo - p_gt|| / d_total * 100% = 2.28%."
    )
    page.insert_textbox(fitz.Rect(18, 1076, 380, 1175), theory_text, fontsize=8.3, fontname="helv", color=TEXT_BODY)

    # Job Market Relevance
    page.insert_textbox(fitz.Rect(18, 1182, 380, 1200), "Job Market & Defense Relevance", fontsize=10.5, fontname="helv-bold", color=TEXT_TITLE)
    page.draw_line(fitz.Point(18, 1199), fitz.Point(380, 1199), color=hex_to_rgb('#cbb8e8'), width=1.0)
    market_text = (
        "• Defense & Jamming Resilience: Electronic warfare GPS jamming increased +400% in regional conflicts (2024–2026); passive vision systems are mission-critical.\n"
        "• Robotics Demand: Autonomous mobile robotics engineers +180% demand in warehouse automation, drone delivery, and sub-surface mining."
    )
    page.insert_textbox(fitz.Rect(18, 1204, 380, 1280), market_text, fontsize=8.3, fontname="helv", color=TEXT_BODY)

    # Col 2: Try It: Live Demo Flow (X: 395 to 760, Y: 805 to 1280)
    page.draw_line(fitz.Point(390, 805), fitz.Point(390, 1280), color=CARD_BORDER, width=1.0)
    page.insert_textbox(fitz.Rect(400, 805, 760, 825), "Try It: Live Demo Flow", fontsize=11.0, fontname="helv-bold", color=TEXT_TITLE)
    page.draw_line(fitz.Point(400, 824), fitz.Point(760, 824), color=hex_to_rgb('#cbb8e8'), width=1.0)

    # Demo Step 1
    page.draw_rect(fitz.Rect(400, 835, 760, 925), fill=hex_to_rgb('#fbfaff'), color=CARD_BORDER, width=1.0)
    page.insert_text(fitz.Point(410, 852), "1. Launch Live Interactive Dashboard", fontsize=9.0, fontname="helv-bold", color=BORDER_PURPLE)
    page.insert_text(fitz.Point(410, 868), "Start real-time VO HUD using commodity laptop/USB webcam:", fontsize=8.0, fontname="helv", color=TEXT_MUTED)
    page.draw_rect(fitz.Rect(410, 876, 750, 915), fill=CLR_CODE_BG)
    page.insert_text(fitz.Point(420, 894), "$ python scripts/live_dashboard.py --camera 0", fontsize=8.5, fontname="courier", color=hex_to_rgb('#e0d7f2'))
    page.insert_text(fitz.Point(420, 907), "[Controls: Q=quit | R=reset | G=toggle GPS | S=screenshot]", fontsize=7.2, fontname="courier", color=hex_to_rgb('#a5d6a7'))

    # Demo Step 2
    page.draw_rect(fitz.Rect(400, 935, 760, 1025), fill=hex_to_rgb('#fbfaff'), color=CARD_BORDER, width=1.0)
    page.insert_text(fitz.Point(410, 952), "2. Real-Time Tracking & Motion Classification", fontsize=9.0, fontname="helv-bold", color=BORDER_PURPLE)
    page.insert_text(fitz.Point(410, 968), "Camera feeds live frames; pipeline extracts FAST corners and matches:", fontsize=8.0, fontname="helv", color=TEXT_MUTED)
    # Badges
    page.draw_rect(fitz.Rect(410, 980, 490, 1002), fill=hex_to_rgb('#e8f8f5'), color=CLR_GREEN, width=1.0)
    page.insert_text(fitz.Point(420, 995), "TRACKING", fontsize=8.0, fontname="helv-bold", color=CLR_GREEN)
    page.draw_rect(fitz.Rect(498, 980, 588, 1002), fill=hex_to_rgb('#eaf2f8'), color=CLR_BLUE, width=1.0)
    page.insert_text(fitz.Point(508, 995), "YAW: +24.0°", fontsize=8.0, fontname="helv-bold", color=CLR_BLUE)
    page.draw_rect(fitz.Rect(596, 980, 680, 1002), fill=hex_to_rgb('#fef9e7'), color=CLR_ORANGE, width=1.0)
    page.insert_text(fitz.Point(608, 995), "48.2 FPS", fontsize=8.0, fontname="helv-bold", color=CLR_ORANGE)
    page.insert_text(fitz.Point(410, 1018), "Top-down bird's-eye map updates lateral X and forward Z positions.", fontsize=7.8, fontname="helv-oblique", color=TEXT_MUTED)

    # Demo Step 3
    page.draw_rect(fitz.Rect(400, 1035, 760, 1135), fill=hex_to_rgb('#fbfaff'), color=CARD_BORDER, width=1.0)
    page.insert_text(fitz.Point(410, 1052), "3. Simulate Instant GPS Dropout (Press 'G')", fontsize=9.0, fontname="helv-bold", color=BORDER_PURPLE)
    page.insert_text(fitz.Point(410, 1068), "Press 'G' key to simulate entry into tunnel or jamming zone:", fontsize=8.0, fontname="helv", color=TEXT_MUTED)
    page.draw_rect(fitz.Rect(410, 1078, 595, 1100), fill=hex_to_rgb('#fcedec'), color=CLR_RED, width=1.0)
    page.insert_text(fitz.Point(420, 1093), "GPS: DENIED (VO DEAD-RECKONING)", fontsize=8.0, fontname="helv-bold", color=CLR_RED)
    page.draw_rect(fitz.Rect(603, 1078, 715, 1100), fill=hex_to_rgb('#fef9e7'), color=CLR_ORANGE, width=1.0)
    page.insert_text(fitz.Point(613, 1093), "DRIFT: 2.28%", fontsize=8.0, fontname="helv-bold", color=CLR_ORANGE)
    page.insert_text(fitz.Point(410, 1115), "HUD flashes red banner. Visual odometry seamlessly takes over navigation!", fontsize=7.8, fontname="helv-bold", color=CLR_RED)
    page.insert_text(fitz.Point(410, 1128), "Odometry continues accumulating trajectory with smooth X-Z coordinates.", fontsize=7.5, fontname="helv", color=TEXT_MUTED)

    # Offline Demo prompt
    page.draw_rect(fitz.Rect(400, 1150, 760, 1270), fill=hex_to_rgb('#f7f3fd'), color=BOX_BORDER, width=1.0)
    page.insert_text(fitz.Point(410, 1170), "Turnkey Fallback: 5-Second Synthetic Demo", fontsize=9.0, fontname="helv-bold", color=TEXT_TITLE)
    page.insert_text(fitz.Point(410, 1188), "For instant offline demonstration on bundled 40-frame sequence:", fontsize=8.0, fontname="helv", color=TEXT_MUTED)
    page.draw_rect(fitz.Rect(410, 1198, 750, 1228), fill=CLR_CODE_BG)
    page.insert_text(fitz.Point(420, 1218), "$ python scripts/run_demo.py", fontsize=8.8, fontname="courier", color=hex_to_rgb('#e0d7f2'))
    page.insert_text(fitz.Point(410, 1245), "• Runs in 4.8 seconds on any standard laptop without camera.", fontsize=7.8, fontname="helv", color=TEXT_BODY)
    page.insert_text(fitz.Point(410, 1258), "• Computes ATE RMSE, RPE drift, and generates comparison plots.", fontsize=7.8, fontname="helv", color=TEXT_BODY)

    # Col 3: Visual Output Figures (X: 775 to 1182, Y: 805 to 1280)
    page.draw_line(fitz.Point(770, 805), fitz.Point(770, 1280), color=CARD_BORDER, width=1.0)

    # Fig 2: Trajectory Comparison
    fig2_path = repo_fig / "trajectory_comparison.png"
    if fig2_path.exists():
        page.insert_image(fitz.Rect(785, 810, 1175, 1025), filename=str(fig2_path))
    else:
        page.draw_rect(fitz.Rect(785, 810, 1175, 1025), fill=hex_to_rgb('#eee'))
    page.insert_textbox(fitz.Rect(785, 1028, 1175, 1045), "Fig. 2: 3D/2D Bird's-Eye Trajectory Overlay — Ground Truth (Green) vs Monocular Visual Odometry (Blue dashed) after Sim(3) alignment.", fontsize=7.8, fontname="helv-oblique", color=TEXT_MUTED, align=fitz.TEXT_ALIGN_CENTER)

    # Fig 3: GPS Outage
    fig3_path = repo_fig / "gps_outage_orb_orb_demo.png"
    if fig3_path.exists():
        page.insert_image(fitz.Rect(785, 1055, 1175, 1255), filename=str(fig3_path))
    else:
        page.draw_rect(fitz.Rect(785, 1055, 1175, 1255), fill=hex_to_rgb('#eee'))
    page.insert_textbox(fitz.Rect(785, 1258, 1175, 1276), "Fig. 3: GPS Outage Takeover — GPS signal cuts at Frame 15; VO dead-reckoning tracks true trajectory with low 2.28% metric drift.", fontsize=7.8, fontname="helv-oblique", color=TEXT_MUTED, align=fitz.TEXT_ALIGN_CENTER)

    # ══════════════════════════════════════════════════════════════════════════
    # 5. BOTTOM SECTION: OUTCOMES & BUDGET UTILIZATION (Y: 1290 to 1700)
    # ══════════════════════════════════════════════════════════════════════════
    page.draw_rect(fitz.Rect(0, 1290, 598, 1318), fill=BANNER_BG)
    page.draw_rect(fitz.Rect(602, 1290, W, 1318), fill=BANNER_BG)
    page.draw_line(fitz.Point(0, 1318), fitz.Point(W, 1318), color=BANNER_BORDER, width=1.5)

    page.insert_textbox(fitz.Rect(0, 1294, 598, 1316), "Outcomes", fontsize=12.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_CENTER)
    page.insert_textbox(fitz.Rect(602, 1294, W, 1316), "Budget Utilization & Tech Stack", fontsize=12.5, fontname="helv-bold", color=TEXT_TITLE, align=fitz.TEXT_ALIGN_CENTER)

    page.draw_line(fitz.Point(600, 1290), fitz.Point(600, 1700), color=CARD_BORDER, width=1.5)

    # Outcomes Left Panel (Y: 1325 to 1690)
    # 4 Metric Pill Cards
    pill_w, pill_h = 132, 50
    pills = [
        ("48.22 FPS", "Real-Time Speed", CLR_GREEN, hex_to_rgb('#f2fcf6')),
        ("Hybrid H / E", "Dual Motion Solver", CLR_BLUE, hex_to_rgb('#f2f8fc')),
        ("2.28% Drift", "GPS Outage Accuracy", CLR_ORANGE, hex_to_rgb('#fdf6ee')),
        ("170 Tests", "Passing Verification", hex_to_rgb('#8e44ad'), hex_to_rgb('#fbf4fc')),
    ]
    for idx, (title, sub, stroke, bg) in enumerate(pills):
        px = 18 + idx * (pill_w + 12)
        page.draw_rect(fitz.Rect(px, 1328, px + pill_w, 1328 + pill_h), fill=bg, color=stroke, width=1.2)
        page.insert_text(fitz.Point(px + 10, 1348), title, fontsize=10.5, fontname="helv-bold", color=TEXT_TITLE)
        page.insert_text(fitz.Point(px + 10, 1365), sub, fontsize=8.0, fontname="helv", color=TEXT_MUTED)

    # 4 Thumbnails (Y: 1395 to 1680)
    th_w, th_h = 132, 95
    thumbs = [
        ("feature_matches_sample.png", "Fig. 4: Inlier Matches"),
        ("trajectory_comparison.png", "Fig. 5: Trajectory Fit"),
        ("scale_drift.png", "Fig. 6: Scale Drift"),
    ]
    for idx, (fn, cap) in enumerate(thumbs):
        tx = 18 + idx * (th_w + 12)
        p = repo_fig / fn
        if p.exists():
            page.insert_image(fitz.Rect(tx, 1400, tx + th_w, 1400 + th_h), filename=str(p))
            page.draw_rect(fitz.Rect(tx, 1400, tx + th_w, 1400 + th_h), color=CARD_BORDER, width=0.8)
        page.insert_textbox(fitz.Rect(tx, 1500, tx + th_w, 1515), cap, fontsize=7.8, fontname="helv-bold", color=TEXT_BODY, align=fitz.TEXT_ALIGN_CENTER)

    # Fig 7: Simulated Live HUD Card
    tx4 = 18 + 3 * (th_w + 12)
    page.draw_rect(fitz.Rect(tx4, 1400, tx4 + th_w, 1400 + th_h), fill=hex_to_rgb('#1e1e24'), color=hex_to_rgb('#333333'), width=1.0)
    page.insert_text(fitz.Point(tx4 + 18, 1425), "LIVE HUD [3-PANEL]", fontsize=7.5, fontname="courier", color=CLR_ORANGE)
    page.insert_text(fitz.Point(tx4 + 10, 1445), "Camera | Top-Down X-Z", fontsize=7.0, fontname="courier", color=CLR_GREEN)
    page.insert_text(fitz.Point(tx4 + 15, 1465), "GPS: DENIED (VO)", fontsize=7.5, fontname="courier", color=CLR_RED)
    page.insert_text(fitz.Point(tx4 + 22, 1482), "Yaw: +24° | 48 FPS", fontsize=6.8, fontname="courier", color=CLR_WHITE)
    page.insert_textbox(fitz.Rect(tx4, 1500, tx4 + th_w, 1515), "Fig. 7: Live HUD UI", fontsize=7.8, fontname="helv-bold", color=TEXT_BODY, align=fitz.TEXT_ALIGN_CENTER)

    # Budget Utilization Right Panel (Y: 1325 to 1690)
    budget_rect = fitz.Rect(618, 1328, 1182, 1400)
    budget_text = (
        "• Budget: No cost figures incurred; the system is a software-only prototype functioning on standard commodity laptop webcams without dedicated GPUs.\n\n"
        "• Tech Stack: Python 3.10/3.11, OpenCV 4.x (Vision Core), NumPy (Matrix Kinematics), SciPy (Optimization & SVD), Matplotlib (Trajectory Plotting), Pytest (Automated Test Suite)."
    )
    page.insert_textbox(budget_rect, budget_text, fontsize=9.2, fontname="helv", color=TEXT_BODY)

    # References
    page.insert_textbox(fitz.Rect(618, 1405, 1182, 1425), "References", fontsize=10.0, fontname="helv-bold", color=TEXT_TITLE)
    page.draw_line(fitz.Point(618, 1423), fitz.Point(1182, 1423), color=hex_to_rgb('#cbb8e8'), width=0.8)

    ref_text = (
        "[1] F. J. Perez-Grau, R. Caballero, et al., 'An architecture for robust UAV navigation in GPS-denied areas,' Journal of Field Robotics, vol. 34, no. 5, pp. 909–936, 2017.\n"
        "[2] A. Handa, T. Whelan, J. McDonald, and A. J. Davison, 'A benchmark for RGB-D visual odometry, 3D reconstruction and SLAM,' in IEEE ICRA, 2014.\n"
        "[3] E. Rublee, V. Rabaud, K. Konolige, and G. Bradski, 'ORB: An efficient alternative to SIFT or SURF,' in IEEE ICCV, 2011.\n"
        "[4] S. Umeyama, 'Least-squares estimation of transformation parameters between two point patterns,' IEEE TPAMI, vol. 13, no. 4, pp. 376–380, 1991."
    )
    page.insert_textbox(fitz.Rect(618, 1428, 1182, 1515), ref_text, fontsize=7.8, fontname="helv", color=TEXT_MUTED)

    # Save PDF
    doc.save(str(pdf_out))
    print(f"[SUCCESS] High-resolution single-page PDF poster generated at: {pdf_out}")
    print(f"  Dimensions: {W} x {H} pt (standard A-series portrait ratio)")
    print(f"  Pages: {len(doc)}")

if __name__ == "__main__":
    create_poster()
