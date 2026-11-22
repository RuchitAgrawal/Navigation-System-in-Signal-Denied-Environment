"""
make_poster.py - builds Project_Poster.pptx from "Poster Template.pptx".

Keeps the template's page size (A1 portrait), PDEU logo, header block, lavender
section banners and section order, and fills them with content from the report
(final_minor.pdf) and the repository (Navigation-System-in-Signal-Denied-Environment).

Run:  python make_poster.py
"""
import copy
import re
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "Navigation-System-in-Signal-Denied-Environment"
FIG = REPO / "results" / "figures"
OUT = ROOT / "Project_Poster.pptx"

# ---- template palette -------------------------------------------------------
LAV = RGBColor(0xDB, 0xB8, 0xFF)       # CC99FF @ 70% over white (template banners)
LAV_SOFT = RGBColor(0xF3, 0xEA, 0xFF)  # card tint
PURPLE_DK = RGBColor(0x3B, 0x1F, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x55, 0x55, 0x55)
ORANGE = RGBColor(0xED, 0x7D, 0x31)
LGREEN = RGBColor(0xE2, 0xEF, 0xDA)
YELLOW = RGBColor(0xFF, 0xC0, 0x00)
BLUE = RGBColor(0x44, 0x72, 0xC4)
GREEN = RGBColor(0x70, 0xAD, 0x47)
TEAL = RGBColor(0x45, 0xBE, 0x8F)
VIOLET = RGBColor(0x7E, 0x57, 0xC2)
GREY = RGBColor(0xB4, 0xB4, 0xB4)
ARROW_PALE = RGBColor(0xC9, 0xD3, 0xEA)

HEAD = "Times New Roman"   # template font for banners/labels
BODY = "Arial"

prs = Presentation(str(ROOT / "Poster Template.pptx"))
slide = prs.slides[0]
SW = prs.slide_width / 914400  # 23.39 in

# ---- strip template placeholder group, keep logo + school box ---------------
for shp in list(slide.shapes):
    if shp.name in ("Group 4", "Straight Connector 20"):
        shp._element.getparent().remove(shp._element)

school = next(s for s in slide.shapes if s.name == "Rectangle 5")
paras = school.text_frame.paragraphs
paras[0].runs[0].text = "School of"
for r in paras[0].runs[1:]:
    r.text = ""
paras[1].runs[0].text = "Technology"
for r in paras[1].runs[1:]:
    r.text = ""
for p in paras:
    for r in p.runs:
        r.font.size = Pt(26)

_id = [1000]


def name(shp, n):
    shp.name = n
    return shp


# ---- helpers ----------------------------------------------------------------
def box(x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None, lw=1.0, nm="Box"):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    return name(s, nm)


def _runs(p, text, size, color, font, bold=False, italic=False):
    """'**bold** plain' markup -> runs."""
    parts = re.split(r"(\*\*.+?\*\*)", text)
    for part in parts:
        if not part:
            continue
        b = bold
        if part.startswith("**") and part.endswith("**"):
            part, b = part[2:-2], True
        r = p.add_run()
        r.text = part
        f = r.font
        f.size = Pt(size)
        f.bold = b
        f.italic = italic
        f.name = font
        f.color.rgb = color


def _bullet(p, size):
    pPr = p._p.get_or_add_pPr()
    ind = int(Pt(size) * 1.1)
    pPr.set("marL", str(ind))
    pPr.set("indent", str(-ind))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    bf = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
    bc = pPr.makeelement(qn("a:buChar"), {"char": "•"})
    pPr.append(bf)
    pPr.append(bc)


def text(x, y, w, h, items, size=22, color=BLACK, font=BODY, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, bullets=False, bold=False, italic=False, space=6,
         margin=0.05, nm="Text", line_spacing=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = anchor
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    if isinstance(items, str):
        items = [items]
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space)
        if line_spacing:
            p.line_spacing = line_spacing
        sz, col, it_b, it_i = size, color, bold, italic
        if isinstance(it, tuple):  # (text, overrides)
            it, ov = it
            sz = ov.get("size", sz)
            col = ov.get("color", col)
            it_b = ov.get("bold", it_b)
            it_i = ov.get("italic", it_i)
        if bullets:
            _bullet(p, sz)
        _runs(p, it, sz, col, font, it_b, it_i)
    return name(tb, nm)


def banner(x, y, w, label, nm):
    """Template section banner: lavender strip, white bold Times text."""
    b = box(x, y, w, 0.62, fill=LAV, nm=nm)
    tf = b.text_frame
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _runs(p, label, 30.7, WHITE, HEAD, bold=True)
    return b


def label(x, y, w, txt, nm, h=0.5, size=24):
    """Template 'Insert Text' style sub-heading: lavender box, bold black Times."""
    b = box(x, y, w, h, fill=LAV, nm=nm)
    tf = b.text_frame
    tf.margin_left = Inches(0.1)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    _runs(p, txt, size, BLACK, HEAD, bold=True)
    return b


def step_box(x, y, w, h, fill, title, lines, nm, dark_text=False, tsize=24, bsize=17):
    b = box(x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12, nm=nm)
    tf = b.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for side in ("left", "right"):
        setattr(tf, f"margin_{side}", Inches(0.12))
    col = BLACK if dark_text else WHITE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(4)
    _runs(p, title, tsize, col, HEAD, bold=True)
    for ln in lines:
        q = tf.add_paragraph()
        q.alignment = PP_ALIGN.CENTER
        q.space_after = Pt(1)
        _runs(q, ln, bsize, col, BODY)
    return b


def arrow(x, y, w, h, direction, color, nm):
    shp = {"r": MSO_SHAPE.RIGHT_ARROW, "l": MSO_SHAPE.LEFT_ARROW,
           "d": MSO_SHAPE.DOWN_ARROW}[direction]
    return box(x, y, w, h, fill=color, shape=shp, nm=nm)


def picture(path, x, y, w=None, h=None, nm="Figure", alt=""):
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y),
                                   Inches(w) if w else None, Inches(h) if h else None)
    pic.name = nm
    pic._element.nvPicPr.cNvPr.set("descr", alt)
    pic.line.color.rgb = GREY
    pic.line.width = Pt(0.75)
    return pic


def table(x, y, w, rows, col_w, nm, size=17, row_h=0.42, bold_cells=()):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    gt.name = nm
    t = gt.table
    tblPr = t._tbl.tblPr
    for attr in ("bandRow", "firstRow"):
        tblPr.set(attr, "0")
    for j, cw in enumerate(col_w):
        t.columns[j].width = Inches(cw)
    for i in range(nr):
        t.rows[i].height = Inches(row_h)
        for j in range(nc):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.02)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            if i == 0:
                c.fill.fore_color.rgb = VIOLET
            else:
                c.fill.fore_color.rgb = WHITE if i % 2 else LAV_SOFT
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            _runs(p, str(rows[i][j]), size, WHITE if i == 0 else BLACK, BODY,
                  bold=(i == 0 or (i, j) in bold_cells))
    return gt


def bar_chart(x, y, w, h, title, cats, vals, colors, nm, fmt='0.000', vmax=None):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series(title, vals)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y),
                                Inches(w), Inches(h), cd)
    gf.name = nm
    ch = gf.chart
    ch.has_legend = False
    ch.has_title = True
    ch.chart_title.text_frame.text = title
    tp = ch.chart_title.text_frame.paragraphs[0]
    for r in tp.runs:
        r.font.size = Pt(20)
        r.font.bold = True
        r.font.name = HEAD
        r.font.color.rgb = PURPLE_DK
    ch.font.size = Pt(15)
    ch.font.name = BODY
    ch.font.color.rgb = MUTED
    plot = ch.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = fmt
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(16)
    dl.font.bold = True
    dl.font.color.rgb = BLACK
    ser = plot.series[0]
    for i, c in enumerate(colors):
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = c
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xE4, 0xE4, 0xE4)
    va.format.line.fill.background()
    va.tick_labels.font.size = Pt(14)
    va.tick_labels.number_format = '0' if fmt == '0.00' else '0.00'
    va.tick_labels.number_format_is_linked = False
    if vmax:
        va.maximum_scale = vmax
    va.minimum_scale = 0
    ca = ch.category_axis
    ca.tick_labels.font.size = Pt(15)
    ca.format.line.color.rgb = GREY
    return gf


# =============================================================================
# HEADER (template rows 0 - 2.15 in)
# =============================================================================
hdr = box(2.58, 0.0, 20.9 - 2.58, 2.14, fill=LAV, nm="Header Band")
# keep logo + school box on top of the band
sp_tree = slide.shapes._spTree
for nm_ in ("Picture 7", "Rectangle 5"):
    el = next(s for s in slide.shapes if s.name == nm_)._element
    sp_tree.remove(el)
    sp_tree.append(el)

text(2.75, 0.08, 18.0, 2.0, [
    ("A Computer Vision-Assisted GPS Navigation System",
     {"size": 33, "bold": True, "color": PURPLE_DK}),
    ("for Robust Positioning in Signal-Denied Environments",
     {"size": 33, "bold": True, "color": PURPLE_DK}),
    ("Ruchit Agrawal (23BCP183)  ·  Joy Patel (23BCP049)   |   Guide: Prof. Azriel Henry, Assistant Professor",
     {"size": 22, "italic": True, "bold": True, "color": PURPLE_DK}),
    ("Department of Computer Engineering, School of Technology, Pandit Deendayal Energy University  ·  2026–27",
     {"size": 18, "italic": True, "color": PURPLE_DK}),
], font=HEAD, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space=0, nm="Title Block")

# =============================================================================
# BRIEF MOTIVATION | OBJECTIVE   (y 2.3 - 7.15)
# =============================================================================
Y = 2.3
banner(0, Y, 11.75, "Brief Motivation", "Banner Motivation")
banner(11.75, Y, SW - 11.75, "Objective", "Banner Objective")
line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(11.75), Inches(Y + 0.75),
                                  Inches(11.75), Inches(7.05))
line.line.color.rgb = LAV
line.line.width = Pt(1.5)
line.name = "Divider"

text(0.4, Y + 0.8, 11.0, 4.0, [
    "**GPS fails** indoors, underground and in dense urban corridors where satellite signals cannot reach.",
    "Warehouse robots, search-and-rescue drones and inspection vehicles still need their **exact position at every moment**.",
    "**Inertial sensors drift** within minutes; UWB or range-sensor SLAM needs pre-installed infrastructure.",
    "A **single camera** is cheap, light and passive: it emits nothing that can be jammed and needs no external setup.",
    "The reference system (Perez-Grau et al., 2017) used **FAST + ORB**; other descriptor choices were left untested.",
], size=21, bullets=True, space=7, nm="Motivation Text")

text(12.15, Y + 0.8, 10.85, 4.0, [
    "**Build** a monocular visual odometry (VO) pipeline using classical computer-vision methods.",
    "**Compare** four feature detector + descriptor combinations on a standard benchmark.",
    "**Measure** Absolute (ATE) and Relative (RPE) Pose Error on ICL-NUIM living room (1,017 frames).",
    "**Identify** the best configuration for accuracy and, separately, for real-time throughput.",
    "**Deliver** a reproducible, tested codebase with 170 passing automated tests.",
], size=21, bullets=True, space=7, nm="Objective Text")

# =============================================================================
# METHODOLOGY   (banner 7.32; content 8.05 - 17.95)
# =============================================================================
Y = 7.32
banner(0, Y, SW, "Methodology", "Banner Methodology")

# --- snake flowchart (template Diagram 13 style) ---
bx, bw, bh, gx = 0.4, 3.35, 2.55, 0.85
x1, x2 = bx, bx + bw + gx
r1, r2, r3 = 8.3, 11.6, 14.9
step_box(x1, r1, bw, bh, ORANGE, "1  Input Frames", ["Frames t−1 and t", "640×480 RGB", "→ grayscale"], "Step 1")
arrow(x1 + bw + 0.15, r1 + bh / 2 - 0.3, gx - 0.3, 0.6, "r", ORANGE, "Arrow 1-2")
step_box(x2, r1, bw, bh, LGREEN, "2  Detection", ["FAST-9 corners", "or ORB (pyramid", "+ orientation)"], "Step 2", dark_text=True)
arrow(x2 + bw / 2 - 0.3, r1 + bh + 0.1, 0.6, r2 - r1 - bh - 0.2, "d", RGBColor(0xA9, 0xD1, 0x8E), "Arrow 2-3")
step_box(x2, r2, bw, bh, YELLOW, "3  Description", ["BRIEF / ORB 256-bit", "BRISK 512-bit", "binary vectors"], "Step 3", dark_text=True)
arrow(x1 + bw + 0.15, r2 + bh / 2 - 0.3, gx - 0.3, 0.6, "l", YELLOW, "Arrow 3-4")
step_box(x1, r2, bw, bh, BLUE, "4  Matching", ["Brute-force Hamming", "Lowe ratio < 0.75", "≥ 8 inliers"], "Step 4")
arrow(x1 + bw / 2 - 0.3, r2 + bh + 0.1, 0.6, r3 - r2 - bh - 0.2, "d", BLUE, "Arrow 4-5")
step_box(x1, r3, bw, bh, GREEN, "5  Pose", ["Essential matrix", "+ RANSAC, SVD", "→ R and unit t"], "Step 5")
arrow(x1 + bw + 0.15, r3 + bh / 2 - 0.3, gx - 0.3, 0.6, "r", GREEN, "Arrow 5-6")
step_box(x2, r3, bw, bh, VIOLET, "6  Trajectory", ["Chain Tᵢ = Tᵢ₋₁·[R|t]", "Sim(3) align", "→ ATE / RPE"], "Step 6")
text(0.4, r3 + bh + 0.12, 7.6, 0.45, "Detect → describe → match → estimate → chain, for every frame pair",
     size=16, italic=True, color=MUTED, align=PP_ALIGN.CENTER, nm="Flow Caption")

# --- middle column: how it works ---
mx, mw = 8.5, 7.0
label(mx, 8.2, mw, "How the Pipeline Works", "Label How")
text(mx, 8.8, mw, 6.0, [
    "**Detect:** FAST-9 marks a corner when ≥ 9 contiguous pixels on a 16-pixel circle are all brighter or darker than the centre (t = 20). ORB adds a scale pyramid and an orientation angle.",
    "**Describe:** BRIEF compares 256 pixel pairs; ORB rotates that pattern by the keypoint angle; BRISK uses a 512-bit concentric pattern that is scale- and rotation-invariant.",
    "**Match:** Hamming distance with cross-check; keep a match only if best < 0.75 × second-best.",
    "**Estimate:** epipolar constraint x′ᵀ E x = 0 solved with RANSAC; SVD of E gives R and t; the cheirality check keeps points in front of both cameras.",
    "**Integrate:** relative poses are chained; a frame that fails keeps the previous pose.",
], size=19, bullets=True, space=6, nm="How Text")

label(mx, 14.2, mw, "Why Sim(3) Alignment?", "Label Sim3")
text(mx, 14.77, mw, 1.6, [
    "One camera recovers translation only as a **direction**, so scale is unknown. "
    "Umeyama (1991) finds the best scale s*, rotation R* and translation t* before ATE is computed "
    "(s* = 0.005–0.010 on ICL-NUIM). This is the standard evaluation for monocular VO.",
], size=18, space=4, nm="Sim3 Text")
label(mx, 16.5, mw, "Scope & Limitations", "Label Scope")
text(mx, 17.05, mw, 1.1, [
    "Monocular RGB only; no stereo, depth, deep learning or loop closure. Frames with < 8 inliers (blur, repeated texture) are skipped.",
], size=18, space=2, nm="Scope Text")

# --- right column: setup + configs + figure ---
rx, rw = 15.95, SW - 15.95 - 0.4
label(rx, 8.2, rw, "Benchmark Setup", "Label Setup")
text(rx, 8.78, rw, 1.75, [
    "**Dataset:** ICL-NUIM living_room_traj1_loop, 1,017 frames, 640×480, 965 ground-truth poses",
    "**Camera:** fx 481.2, fy 480.0, cx 319.5, cy 239.5 px; no distortion",
    "**Hardware:** single-threaded laptop CPU, no GPU",
], size=17, bullets=True, space=3, nm="Setup Text")
table(rx, 10.6, rw, [
    ["Config", "Detector", "Descriptor", "Bits"],
    ["fast_brief_v1", "FAST-9", "BRIEF", "256"],
    ["fast_orb_v1", "FAST-9", "ORB", "256"],
    ["orb_orb_v1", "ORB", "ORB", "256"],
    ["orb_brisk_v1", "ORB", "BRISK", "512"],
], [2.2, 1.55, 1.75, 1.54], "Config Table", size=17, row_h=0.42)
fig_w = rw
fig_h = fig_w * 467 / 1142
picture(FIG / "feature_matches_sample.png", rx, 12.95, w=fig_w, nm="Fig Matches",
        alt="Feature matches between two consecutive frames; green lines are inliers")
text(rx, 12.95 + fig_h + 0.05, rw, 0.7,
     "Fig. 1: Matched keypoints between consecutive frames (538 of 649 kept as inliers, green) after Lowe's ratio test and RANSAC",
     size=15, italic=True, color=MUTED, align=PP_ALIGN.CENTER, nm="Fig1 Caption")

# =============================================================================
# EXPECTED RESULTS   (banner 18.25; content 19.0 - 27.2)
# =============================================================================
Y = 18.25
banner(0, Y, SW, "Expected Results", "Banner Results")

# --- stepped stat boxes (template Diagram 10 style) ---
sx, sw_, sh_ = 0.35, 7.4, 2.25
s_y = [19.15, 21.75, 24.35]
for i, (fill, big, small, nm_) in enumerate([
    (BLUE, "0.1732 m  ATE RMSE", "ORB + BRISK: best accuracy and highest tracking rate (54.04%)", "Stat Accuracy"),
    (TEAL, "48.22 FPS", "FAST + ORB: mean 21.47 ms, P95 28.71 ms (30 Hz-ready)", "Stat Speed"),
    (GREEN, "37.6% lower error", "Changing only the descriptor, ORB → BRISK (0.2775 → 0.1732 m)", "Stat Descriptor"),
]):
    xo = sx + i * 0.35
    step_box(xo, s_y[i], sw_, sh_, fill, big, [small], nm_, tsize=30, bsize=18)
    if i < 2:
        arrow(xo + sw_ - 1.15, s_y[i] + sh_ - 0.35, 0.75, 0.75, "d", ARROW_PALE, f"Stat Arrow {i}")

# --- native charts ---
cats = ["FAST+BRIEF", "FAST+ORB", "ORB+ORB", "ORB+BRISK"]
cx_, cw_ = 8.75, 6.95
bar_chart(cx_, 19.0, cw_, 4.05, "ATE RMSE (m), lower is better", cats,
          [0.2302, 0.2219, 0.2775, 0.1732], [GREY, GREY, GREY, BLUE], "Chart ATE", fmt='0.000', vmax=0.32)
bar_chart(cx_ + cw_ + 0.25, 19.0, cw_, 4.05, "Mean FPS, higher is better", cats,
          [32.95, 48.22, 32.75, 30.11], [GREY, TEAL, GREY, GREY], "Chart FPS", fmt='0.00', vmax=56)

table(cx_, 23.25, 2 * cw_ + 0.25, [
    ["Configuration", "ATE RMSE (m)", "ATE Median (m)", "RPE Rot (°)", "Tracking %", "Mean FPS", "P95 (ms)"],
    ["FAST + BRIEF", "0.2302", "0.2112", "0.5544", "45.87", "32.95", "42.11"],
    ["FAST + ORB", "0.2219", "0.2212", "0.5571", "44.59", "48.22", "28.71"],
    ["ORB + ORB", "0.2775", "0.2466", "0.5599", "52.26", "32.75", "63.00"],
    ["ORB + BRISK", "0.1732", "0.1675", "0.9610", "54.04", "30.11", "66.52"],
], [2.45, 2.0, 2.15, 1.85, 1.85, 1.9, 1.95], "Results Table", size=17, row_h=0.42,
    bold_cells={(4, 1), (4, 2), (1, 3), (4, 4), (2, 5), (2, 6)})
text(cx_, 25.4, 2 * cw_ + 0.25, 0.4,
     "Table: ICL-NUIM living room, 1,017 frames, Sim(3)-aligned against 965 ground-truth poses. Bold = best in column.",
     size=15, italic=True, color=MUTED, nm="Table Caption")
text(cx_, 25.85, 2 * cw_ + 0.25, 1.35, [
    "**No configuration wins both.** FAST skips the scale pyramid, so it is faster; BRISK's 512-bit pattern is more distinctive, so it is more accurate. "
    "Use **FAST + ORB** for real-time control and **ORB + BRISK** when accuracy matters (mapping, precision landing).",
], size=18, nm="Tradeoff Text")

# =============================================================================
# OUTCOMES | BUDGET UTILIZATION   (banner 27.4; content 28.1 - 33.0)
# =============================================================================
Y = 27.4
banner(0, Y, 13.02, "Outcomes", "Banner Outcomes")
banner(13.02, Y, SW - 13.02, "Budget Utilization & References", "Banner Budget")

# --- 2x2 quad (template Diagram 14 style) with cross arrows ---
qx, qy, qs, qg = 0.45, 28.3, 2.25, 0.25
cxm = qx + qs + qg / 2
cym = qy + qs + qg / 2
box(qx - 0.3, cym - 0.06, 2 * qs + qg + 0.6, 0.12, fill=RGBColor(0xF8, 0xCB, 0xAD), nm="Quad Cross H")
box(cxm - 0.06, qy - 0.3, 0.12, 2 * qs + qg + 0.6, fill=RGBColor(0xF8, 0xCB, 0xAD), nm="Quad Cross V")
for (i, j, fill, t, dark) in [
    (0, 0, ORANGE, "Working monocular VO pipeline", False),
    (1, 0, LGREEN, "4 configs benchmarked on 1,017 frames", True),
    (0, 1, YELLOW, "Real time on CPU: 48.22 FPS", True),
    (1, 1, BLUE, "170 automated tests passing", False),
]:
    step_box(qx + i * (qs + qg), qy + j * (qs + qg), qs, qs, fill, t, [], f"Outcome {i}{j}",
             dark_text=dark, tsize=20)

# --- prototype picture ---
px = qx + 2 * qs + qg + 0.6
pw = 13.02 - px - 0.3
CROP = 0.12  # hide the PNG's baked-in title (contains a mis-encoded dash)
ph = pw * 740 * (1 - CROP) / 2084
g = picture(FIG / "gps_outage_orb_orb_demo.png", px, 28.25, w=pw, nm="Fig GPS Outage",
            alt="Simulated GPS outage: VO-only trajectory vs ground truth and drift during outage")
g.crop_top = CROP
g.height = Inches(ph)
text(px, 28.25 + ph + 0.05, pw, 0.75,
     "Fig. 2: Simulated GPS outage (frames 15–35, demo sequence): VO alone keeps tracking; error grows slowly",
     size=15, italic=True, color=MUTED, align=PP_ALIGN.CENTER, nm="Fig2 Caption")
text(px, 31.35, pw, 1.6, [
    "**Live demo:** live_dashboard.py runs the pipeline on a webcam with a trajectory map; press **G** to switch to GPS-denied mode.",
], size=17, nm="Demo Text")

# --- budget, stack, future work, references ---
bx_ = 13.35
bw_ = SW - bx_ - 0.35
text(bx_, 28.12, bw_, 2.0, [
    "**Budget:** no funding used. Software-only prototype on a standard laptop CPU with a public dataset.",
    "**Tech stack:** Python 3.10, OpenCV 4.x, NumPy, pytest; custom ICL-NUIM loader and Sim(3) evaluator.",
    "**Next:** stereo / RGB-D for metric scale, loop closure, learned features (SuperPoint), IMU fusion (EKF), Jetson deployment.",
], size=17, space=4, nm="Budget Text")
text(bx_, 29.95, bw_, 0.4, "**References**", size=18, font=HEAD, nm="Ref Heading")
text(bx_, 30.35, bw_, 2.7, [
    "[1] F. J. Perez-Grau et al., “An architecture for robust UAV navigation in GPS-denied areas,” J. Field Robotics, 34(5), 2017.",
    "[2] A. Handa et al., “A benchmark for RGB-D visual odometry, 3D reconstruction and SLAM,” IEEE ICRA, 2014.",
    "[3] E. Rublee et al., “ORB: An efficient alternative to SIFT or SURF,” IEEE ICCV, 2011.",
    "[4] S. Leutenegger et al., “BRISK: Binary robust invariant scalable keypoints,” IEEE ICCV, 2011.",
    "[5] J. Sturm et al., “A benchmark for the evaluation of RGB-D SLAM systems,” IEEE/RSJ IROS, 2012.",
    "[6] S. Umeyama, “Least-squares estimation of transformation parameters,” IEEE TPAMI, 13(4), 1991.",
], size=14.5, space=1, nm="References")

prs.save(str(OUT))
print("saved", OUT)
