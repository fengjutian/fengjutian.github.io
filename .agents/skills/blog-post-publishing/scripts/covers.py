# -*- coding: utf-8 -*-
"""Per-post cover cards for fengjutian.github.io.

One shared typographic frame (meta / title / thesis / domain), but each card
gets its own accent colour, its own motif, and one of three compositions, so
the blog sidebar stops looking like the same card with a different string.

To add a post: add an entry to CARDS (accent + glow position) and a branch in
build() that picks a motif helper (motif_grid / motif_area / motif_browser /
motif_rings / motif_tree / motif_layers / motif_game / motif_code) with its
coordinates. Render, then *look* at the JPEG before shipping it.

    python covers.py <out_dir>
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
M = 72

# MNN cover motif: 8 columns x 6 rows graded S / A / B / hole (C)
GRADES = [
    [1.0, 0.6, 1.0, 0.0, 0.6, 1.0, 1.0, 0.6],
    [0.6, 1.0, 0.6, 1.0, 0.0, 0.6, 1.0, 0.3],
    [1.0, 1.0, 1.0, 1.0, 0.6, 0.0, 0.3, 1.0],
    [1.0, 0.6, 0.0, 0.6, 1.0, 0.3, 0.0, 0.6],
    [0.6, 0.0, 0.3, 0.3, 0.0, 1.0, 0.6, 0.3],
    [0.3, 0.6, 0.3, 0.0, 0.6, 0.6, 0.3, 1.0],
]

WHITE = (238, 243, 250)
BODY = (186, 201, 220)
DIM = (118, 138, 164)
FAINT = (86, 104, 128)
BG_TOP = (17, 25, 40)
BG_BOT = (8, 11, 19)
MID = (34, 44, 60)

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def tint(accent, t=0.13):
    return mix(MID, accent, t)


def arrow(d, p1, p2, color, width=3, head=13):
    x1, y1 = p1
    x2, y2 = p2
    ang = math.atan2(y2 - y1, x2 - x1)
    d.line((x1, y1, x2, y2), fill=color, width=width)
    d.polygon([(x2, y2),
               (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42)),
               (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))], fill=color)


def canvas(glow_at, accent, glow_r=430, strength=0.34):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        d.line((0, y, W, y), fill=mix(BG_TOP, BG_BOT, t))

    gx, gy = glow_at
    n = 256
    yy, xx = np.mgrid[0:n, 0:n]
    rad = np.hypot(xx - n / 2, yy - n / 2) / (n / 2)
    field = np.clip(1 - rad, 0, 1) ** 2.1
    layer = Image.new("RGB", (glow_r * 2, glow_r * 2), accent)
    mask = Image.fromarray((field * 255 * strength).astype("uint8"), "L")
    mask = mask.resize((glow_r * 2, glow_r * 2), Image.BICUBIC)
    img.paste(layer, (int(gx - glow_r), int(gy - glow_r)), mask)
    return img, ImageDraw.Draw(img)


def tracked(d, xy, text, size, color, tracking=2.6):
    f = font(size)
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + tracking


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if d.textlength(trial, font=f) > maxw and cur:
            lines.append(cur)
            cur = "" if ch == " " else ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def para(d, xy, text, size, color, maxw, leading=1.45):
    f = font(size)
    x, y = xy
    for line in wrap(d, text, f, maxw):
        d.text((x, y), line, font=f, fill=color)
        y += int(size * leading)


def head(d, accent, meta, title, thesis, title_xy, title_size,
         thesis_xy, thesis_w, align="left", thesis_size=29):
    if align == "left":
        d.rounded_rectangle((M, 88, M + 34, 94), radius=3, fill=accent)
        tracked(d, (M, 112), meta.upper(), 21, mix(DIM, accent, 0.45), 2.4)
        tx, ty = title_xy
        f = font(title_size, True)
        parts = title.split("\n")
        for i, p in enumerate(parts):
            d.text((tx, ty + i * int(title_size * 1.06)), p, font=f, fill=WHITE)
        bottom = ty + len(parts) * int(title_size * 1.06)
        d.rounded_rectangle((tx, bottom + 18, tx + 96, bottom + 24), radius=3, fill=accent)
        para(d, thesis_xy, thesis, thesis_size, BODY, thesis_w)
    else:
        rx = W - M
        d.rounded_rectangle((rx - 34, 88, rx, 94), radius=3, fill=accent)
        f = font(21)
        x = rx
        for ch in reversed(meta.upper()):
            w = d.textlength(ch, font=f)
            d.text((x - w, 112), ch, font=f, fill=mix(DIM, accent, 0.45))
            x -= w + 2.4
        tx, ty = title_xy
        f = font(title_size, True)
        parts = title.split("\n")
        for i, p in enumerate(parts):
            d.text((tx, ty + i * int(title_size * 1.06)), p, font=f, fill=WHITE, anchor="ra")
        bottom = ty + len(parts) * int(title_size * 1.06)
        d.rounded_rectangle((tx - 96, bottom + 18, tx, bottom + 24), radius=3, fill=accent)
        f2 = font(thesis_size)
        y = thesis_xy[1]
        for line in wrap(d, thesis, f2, thesis_w):
            d.text((tx, y), line, font=f2, fill=BODY, anchor="ra")
            y += int(thesis_size * 1.45)


def domain(d, text="fengjutian.github.io"):
    d.text((M, 574), text, font=font(19), fill=(74, 92, 116))


# ------------------------------------------------------------------ motifs
def motif_grid(d, box, accent, cols=13, rows=9, lit=(), ring=None, tag=None):
    x, y, w, h = box
    gap = 9
    cell = min((w - gap * (cols - 1)) / cols, (h - gap * (rows - 1)) / rows)
    gw = cell * cols + gap * (cols - 1)
    gh = cell * rows + gap * (rows - 1)
    x0 = x + (w - gw) / 2
    y0 = y + (h - gh) / 2
    for r in range(rows):
        for c in range(cols):
            cx = x0 + c * (cell + gap)
            cy = y0 + r * (cell + gap)
            on = (r * cols + c) in lit
            d.rounded_rectangle((cx, cy, cx + cell, cy + cell), radius=3,
                                fill=tint(accent, 0.85) if on else tint(accent, 0.12),
                                outline=None if on else mix(BG_TOP, accent, 0.2))
    if ring is not None:
        r, c = ring
        cx = x0 + c * (cell + gap) + cell / 2
        cy = y0 + r * (cell + gap) + cell / 2
        rad = cell * 0.95
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=accent, width=3)
        if tag:
            d.text((cx + rad + 14, cy), tag, font=font(17), fill=mix(DIM, accent, 0.55), anchor="lm")


def motif_area(d, box, accent, values, bracket, ylabel, xlabel):
    x, y, w, h = box
    base = y + h
    step = w / (len(values) - 1)
    pts = [(x + i * step, base - v * h) for i, v in enumerate(values)]
    d.polygon(pts + [(x + w, base), (x, base)], fill=tint(accent, 0.18))
    for a, b in zip(pts[:-1], pts[1:]):
        d.line((a[0], a[1], b[0], b[1]), fill=accent, width=5)
    for p in pts:
        d.ellipse((p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4), fill=accent)
    d.line((x, base, x + w, base), fill=mix(BG_TOP, accent, 0.3), width=2)
    d.text((x, y - 36), ylabel, font=font(19), fill=DIM)
    d.text((x + w, base + 12), xlabel, font=font(19), fill=DIM, anchor="ra")
    by = base + 40
    d.line((x, by, x + w, by), fill=mix(DIM, accent, 0.4), width=3)
    for bx in (x, x + w):
        d.line((bx, by - 9, bx, by + 9), fill=mix(DIM, accent, 0.4), width=3)
    d.text(((2 * x + w) / 2, by + 12), bracket, font=font(20), fill=mix(DIM, accent, 0.6), anchor="ma")


def motif_browser(d, box, accent, chips, arcs, tag):
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.09),
                        outline=mix(BG_TOP, accent, 0.38), width=2)
    d.line((x, y + 46, x + w, y + 46), fill=mix(BG_TOP, accent, 0.3), width=2)
    for i, c in enumerate([(226, 96, 92), (226, 178, 88), (110, 190, 120)]):
        d.ellipse((x + 20 + i * 22, y + 17, x + 32 + i * 22, y + 29), fill=mix(c, (18, 22, 30), 0.3))
    d.rounded_rectangle((x + 96, y + 12, x + w - 20, y + 34), radius=11, fill=tint(accent, 0.22))
    d.text((x + 110, y + 15), "explainer.local / gpt2 / onnx", font=font(15), fill=DIM)

    tx = x + 24
    ty = y + 78
    f = font(20)
    boxes = []
    for chip in chips:
        cw = d.textlength(chip, font=f) + 22
        d.rounded_rectangle((tx, ty, tx + cw, ty + 38), radius=8,
                            fill=tint(accent, 0.26), outline=mix(BG_TOP, accent, 0.55))
        d.text((tx + 11, ty + 6), chip, font=f, fill=WHITE)
        boxes.append((tx + cw / 2, ty + 38))
        tx += cw + 8

    # attention: the last token looks back at the ones before it
    ty2 = ty + 38
    for idx, alpha, deep in arcs:
        bx = boxes[idx][0]
        src_x = boxes[5][0]
        pts = []
        for t in range(0, 41):
            t = t / 40
            ax = (1 - t) ** 2 * bx + 2 * (1 - t) * t * ((bx + src_x) / 2) + t * t * src_x
            ay = (1 - t) ** 2 * ty2 + 2 * (1 - t) * t * (ty2 + deep) + t * t * ty2
            pts.append((ax, ay))
        d.line(pts, fill=mix(BG_TOP, accent, alpha), width=4, joint="curve")

    by = y + h - 40
    for i, v in enumerate([0.9, 0.52, 0.32, 0.2, 0.12]):
        bx = x + 26 + i * ((w - 52) / 5.8)
        bh = 14 + v * 62
        d.rounded_rectangle((bx, by - bh, bx + 44, by), radius=6,
                            fill=accent if i == 0 else tint(accent, 0.32))
    d.text((x + 26, by + 8), tag, font=font(16), fill=DIM)


def motif_rings(d, cx, cy, accent, label, sub):
    d.ellipse((cx - 236, cy - 236, cx + 236, cy + 236), outline=mix(BG_TOP, accent, 0.12), width=2)
    d.ellipse((cx - 170, cy - 170, cx + 170, cy + 170), outline=mix(BG_TOP, accent, 0.2), width=2)
    d.ellipse((cx - 104, cy - 104, cx + 104, cy + 104), fill=tint(accent, 0.16),
              outline=mix(BG_TOP, accent, 0.5), width=3)
    heights = [10, 18, 30, 46, 26, 54, 34, 20, 40, 24, 14, 8]
    bw = 7
    total = len(heights) * (bw + 5) - 5
    sx = cx - total / 2
    for i, hgt in enumerate(heights):
        px = sx + i * (bw + 5)
        d.rounded_rectangle((px, cy - hgt / 2, px + bw, cy + hgt / 2), radius=3,
                            fill=accent if hgt > 30 else mix(BG_TOP, accent, 0.55))
    for ang in (-140, -40, 40, 140):
        a = math.radians(ang)
        px, py = cx + 202 * math.cos(a), cy + 202 * math.sin(a)
        d.line((cx + 104 * math.cos(a), cy + 104 * math.sin(a), px, py),
               fill=mix(BG_TOP, accent, 0.4), width=2)
        d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=tint(accent, 0.55), outline=accent, width=2)
    d.text((cx, cy + 254), label, font=font(21), fill=mix(DIM, accent, 0.6), anchor="ma")
    d.text((cx, cy + 286), sub, font=font(17), fill=FAINT, anchor="ma")


def motif_tree(d, box, accent, tag, caption=None):
    x, y, w, h = box
    cy = y + h / 2
    trunk_end = x + w * 0.24
    node_x = x + w * 0.62
    d.rounded_rectangle((x, cy - 14, x + 10, cy + 14), radius=6, fill=tint(accent, 0.6))
    d.line((x, cy, trunk_end, cy), fill=mix(BG_TOP, accent, 0.6), width=5)
    ys = [cy - h * 0.34, cy, cy + h * 0.34]
    for ty in ys:
        pts = []
        for t in range(0, 41):
            t = t / 40
            px = (1 - t) ** 2 * trunk_end + 2 * (1 - t) * t * (trunk_end + 64) + t * t * node_x
            py = (1 - t) ** 2 * cy + 2 * (1 - t) * t * ty + t * t * ty
            pts.append((px, py))
        d.line(pts, fill=mix(BG_TOP, accent, 0.5), width=3, joint="curve")
        d.ellipse((node_x - 8, ty - 8, node_x + 8, ty + 8), fill=accent)
    d.line((node_x + 6, cy - h * 0.34, node_x + 6, cy + h * 0.34),
           fill=mix(BG_TOP, accent, 0.5), width=3)
    d.line((node_x + 6, cy, node_x + 44, cy), fill=accent, width=5)
    d.rounded_rectangle((node_x + 44, cy - 30, x + w, cy + 30), radius=10,
                        fill=tint(accent, 0.26), outline=accent, width=2)
    size = 18
    while d.textlength(tag, font=font(size)) > (x + w - node_x - 44) - 26 and size > 12:
        size -= 1
    d.text(((node_x + 44 + x + w) / 2, cy), tag, font=font(size), fill=WHITE, anchor="mm")
    if caption:
        d.text((x + 10, y + h + 18), caption, font=font(18), fill=FAINT)


def motif_layers(d, box, accent, n, out_box, hook=7):
    x, y, w, h = box
    gap = 9
    sh = (h - gap * (n - 1)) / n
    for i in range(n):
        yy = y + i * (sh + gap)
        hot = i == hook
        d.rounded_rectangle((x, yy, x + w, yy + sh), radius=5,
                            fill=accent if hot else tint(accent, 0.13),
                            outline=None if hot else mix(BG_TOP, accent, 0.2))
    hy = y + hook * (sh + gap) + sh / 2
    ox, oy, ow, oh = out_box
    # hook taps the residual stream, then the head produces logits
    d.line((x + w, hy, ox - 18, hy), fill=mix(BG_TOP, accent, 0.7), width=3)
    d.polygon([(ox - 8, hy), (ox - 24, hy - 9), (ox - 24, hy + 9)], fill=mix(BG_TOP, accent, 0.7))
    d.text((x + w + 12, hy + 12), "hook", font=font(16), fill=mix(DIM, accent, 0.6))
    for i, v in enumerate([0.95, 0.6, 0.42, 0.28, 0.18]):
        bh = v * oh
        bx = ox + i * (ow / 5.4)
        d.rounded_rectangle((bx, oy + oh - bh, bx + 34, oy + oh), radius=5,
                            fill=accent if i == 0 else tint(accent, 0.32))
    d.text((ox, oy - 30), "logits / 50257", font=font(17), fill=DIM)
    d.text((ox, oy + oh + 14), "12 层后仍是同一条残差流", font=font(17), fill=FAINT)


def motif_game(d, box, accent, tag):
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=tint(accent, 0.09),
                        outline=mix(BG_TOP, accent, 0.4), width=2)
    d.line((x, y + 40, x + w, y + 40), fill=mix(BG_TOP, accent, 0.3), width=2)
    for i in range(3):
        d.ellipse((x + 16 + i * 18, y + 15, x + 26 + i * 18, y + 25), fill=mix((190, 200, 210), MID, 0.45))

    runs = [("run 01", "白屏", False), ("run 02", "控制台报错", False), ("run 03", "可玩 · 过关", True)]
    ry = y + 62
    for name, note, ok in runs:
        col = accent if ok else (196, 96, 92)
        d.rounded_rectangle((x + 24, ry, x + w - 24, ry + 68), radius=9,
                            fill=tint(col, 0.16), outline=mix(BG_TOP, col, 0.5))
        d.text((x + 44, ry + 11), name, font=font(19), fill=DIM)
        d.text((x + 44, ry + 36), note, font=font(21), fill=WHITE if ok else mix(BODY, col, 0.35))
        # verdict mark
        cx, cy = x + w - 58, ry + 34
        if ok:
            d.line((cx - 11, cy, cx - 3, cy + 9), fill=accent, width=5)
            d.line((cx - 3, cy + 9, cx + 12, cy - 11), fill=accent, width=5)
        else:
            d.line((cx - 9, cy - 9, cx + 9, cy + 9), fill=col, width=4)
            d.line((cx - 9, cy + 9, cx + 9, cy - 9), fill=col, width=4)
        ry += 86
    d.text((x + 24, y + h - 26), tag, font=font(16), fill=mix(DIM, accent, 0.5))


def motif_sheet(d, box, accent, tag):
    """A review sheet: six views, colour on top, clay below, one check."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=tint(accent, 0.08),
                        outline=mix(BG_TOP, accent, 0.38), width=2)
    d.text((x + 20, y + 14), "review sheet · 6 views", font=font(15), fill=FAINT)

    tw, th, gap = 118, 108, 14
    x0 = x + (w - (tw * 3 + gap * 2)) / 2
    # the object, seen front / side / top: fills for colour, outlines for clay
    for row in range(2):
        for col in range(3):
            tx = x0 + col * (tw + gap)
            ty = y + 52 + row * (th + gap)
            d.rounded_rectangle((tx, ty, tx + tw, ty + th), radius=8,
                                fill=(13, 18, 29) if row == 1 else tint(accent, 0.14),
                                outline=mix(BG_TOP, accent, 0.30))
            cx, cy = tx + tw / 2, ty + th / 2 + 2
            if row == 0:
                fill, line = accent, mix(BG_TOP, accent, 0.9)
            else:
                fill, line = mix((18, 24, 38), (170, 180, 195), 0.55), (196, 204, 216)
            if col == 0:      # front: a box with a lid
                d.rectangle((cx - 30, cy - 24, cx + 30, cy + 26), fill=fill)
                d.rectangle((cx - 36, cy - 34, cx + 36, cy - 18), fill=line)
            elif col == 1:    # side: narrower
                d.rectangle((cx - 16, cy - 24, cx + 16, cy + 26), fill=fill)
                d.rectangle((cx - 22, cy - 34, cx + 22, cy - 18), fill=line)
            else:             # top: flatter, from above
                d.rectangle((cx - 34, cy - 12, cx + 34, cy + 20), fill=fill)
                d.rectangle((cx - 34, cy - 26, cx + 34, cy - 14), fill=line)

    # close-up marker on one tile
    d.ellipse((x0 + 2 * (tw + gap) + tw - 34, y + 52 + th - 34,
               x0 + 2 * (tw + gap) + tw - 12, y + 52 + th - 12),
              outline=accent, width=3)

    # verdict badge
    cx, cy, r = x + w - 44, y + h - 46, 26
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(14, 19, 30), outline=accent, width=3)
    d.line((cx - 9, cy, cx - 2, cy + 8), fill=accent, width=5)
    d.line((cx - 2, cy + 8, cx + 11, cy - 9), fill=accent, width=5)
    d.text((x + 20, y + h - 34), tag, font=font(16), fill=mix(DIM, accent, 0.5))


def motif_audio(d, box, accent, tag):
    """Two tracks in, one narrow permission gate out."""
    x, y, w, h = box
    gate = x + w * 0.60
    rows = [("麦克风", y + h * 0.26, [0.30, 0.62, 0.44, 0.86, 0.52, 0.74, 0.34, 0.58, 0.40, 0.28]),
            ("系统音频", y + h * 0.62, [0.22, 0.48, 0.72, 0.38, 0.66, 0.30, 0.54, 0.80, 0.36, 0.24])]
    bw, gap = 13, 10
    for name, cy, hs in rows:
        d.text((x, cy - 54), name, font=font(17), fill=DIM)
        for i, v in enumerate(hs):
            bx = x + i * (bw + gap)
            bh = v * 46
            d.rounded_rectangle((bx, cy - bh, bx + bw, cy + bh), radius=4,
                                fill=accent if v > 0.5 else tint(accent, 0.5))
        # converge into the gate
        pts = []
        for t in range(0, 31):
            t = t / 30
            px = (1 - t) ** 2 * (x + len(hs) * (bw + gap)) + 2 * (1 - t) * t * (gate - 60) + t * t * (gate - 10)
            py = (1 - t) ** 2 * cy + 2 * (1 - t) * t * cy + t * t * (y + h * 0.44)
            pts.append((px, py))
        d.line(pts, fill=mix(DIM, accent, 0.55), width=3, joint="curve")

    top, bot = y + h * 0.10, y + h * 0.78
    d.rounded_rectangle((gate - 9, top, gate + 9, bot), radius=9, fill=accent)
    d.text((gate, top - 26), "0o600", font=font(19), fill=mix(DIM, accent, 0.75), anchor="ma")

    # one line out, small and read-only
    oy = y + h * 0.44
    d.line((gate + 12, oy, x + w - 96, oy), fill=mix(BG_TOP, accent, 0.65), width=4)
    for i in range(2):
        bx = gate + 40 + i * 56
        d.rounded_rectangle((bx, oy - 12, bx + 34, oy + 12), radius=5, fill=tint(accent, 0.35),
                            outline=mix(BG_TOP, accent, 0.5))
    d.rounded_rectangle((x + w - 92, oy - 24, x + w, oy + 24), radius=12, fill=tint(accent, 0.3),
                        outline=accent, width=2)
    d.text((x + w - 46, oy), "只读", font=font(19), fill=WHITE, anchor="mm")
    d.text((x, y + h + 8), tag, font=font(16), fill=FAINT)


def motif_matrix(d, box, accent, tag):
    """A tensor grid with one row lit, read into three verdicts."""
    x, y, w, h = box
    cols, rows, gap = 9, 9, 5
    cell = min((w * 0.52 - gap * (cols - 1)) / cols, (h - gap * (rows - 1)) / rows)
    gx, gy = x, y + (h - (cell * rows + gap * (rows - 1))) / 2
    lit_row, lit_cell = 4, (2, 7)
    for r in range(rows):
        for c in range(cols):
            cx = gx + c * (cell + gap)
            cy = gy + r * (cell + gap)
            on = r == lit_row or (r, c) == lit_cell
            d.rounded_rectangle((cx, cy, cx + cell, cy + cell), radius=3,
                                fill=accent if on else tint(accent, 0.14),
                                outline=None if on else mix(BG_TOP, accent, 0.22))

    ax0 = gx + cols * (cell + gap) + 6
    ay = gy + (cell * rows + gap * (rows - 1)) / 2
    d.line((ax0, ay, ax0 + 30, ay), fill=mix(BG_TOP, accent, 0.7), width=3)
    d.polygon([(ax0 + 38, ay), (ax0 + 22, ay - 8), (ax0 + 22, ay + 8)], fill=mix(BG_TOP, accent, 0.7))

    cx0 = ax0 + 56
    chw = x + w - cx0
    ch = 72
    cy = ay - (3 * ch + 2 * 16) / 2 + ch / 2
    for name, hot in [("up", True), ("down", False), ("same", False)]:
        top = cy - ch / 2
        d.rounded_rectangle((cx0, top, cx0 + chw, top + ch), radius=12,
                            fill=tint(accent, 0.22) if hot else (16, 22, 34),
                            outline=accent if hot else mix(BG_TOP, accent, 0.3), width=2)
        d.text((cx0 + 20, cy), name, font=font(23, hot), fill=WHITE if hot else DIM, anchor="lm")
        cy += ch + 16

    d.text((x, y + h + 10), tag, font=font(16), fill=FAINT)


def motif_boundary(d, box, accent, tag):
    """A pipe from the user side to root, with three gates on it."""
    x, y, w, h = box
    cy = y + h * 0.52
    # left: the unprivileged side, with a wifi ripple above it
    lx, lw, lh = x + 20, 140, 108
    d.rounded_rectangle((lx, cy - lh / 2, lx + lw, cy + lh / 2), radius=12,
                        fill=tint(accent, 0.16), outline=mix(BG_TOP, accent, 0.55), width=2)
    d.text((lx + lw / 2, cy - 8), "GUI", font=font(26, True), fill=WHITE, anchor="mm")
    d.text((lx + lw / 2, cy + 24), "uid 1000", font=font(16), fill=DIM, anchor="mm")
    for i in range(3):
        r = 16 + i * 13
        d.arc((lx + lw / 2 - r - 30, cy - lh / 2 - r - 18, lx + lw / 2 + r - 30, cy - lh / 2 + r - 18),
              200, 340, fill=mix(BG_TOP, accent, 0.55), width=3)

    # right: root
    rx, rw, rh = lx + lw + 250, 140, 108
    d.rounded_rectangle((rx, cy - rh / 2, rx + rw, cy + rh / 2), radius=12,
                        fill=accent, outline=accent, width=2)
    d.text((rx + rw / 2, cy - 8), "agent", font=font(25, True), fill=(18, 22, 30), anchor="mm")
    d.text((rx + rw / 2, cy + 24), "root", font=font(16), fill=mix((18, 22, 30), accent, 0.55), anchor="mm")

    # the pipe and its gates
    x0, x1 = lx + lw + 8, rx - 8
    d.line((x0, cy, x1, cy), fill=mix(BG_TOP, accent, 0.55), width=5)
    for i in range(3):
        gx = x0 + (x1 - x0) * (0.24 + i * 0.26)
        d.line((gx, cy - 15, gx, cy + 15), fill=WHITE, width=4)
        r = 13
        d.ellipse((gx - r, cy - 34 - r, gx + r, cy - 34 + r), fill=accent)
        d.text((gx, cy - 34), str(i + 1), font=font(16, True), fill=(16, 20, 28), anchor="mm")

    d.text((x + 20, cy + 90), "① 0600   ② peer uid   ③ 只 accept 一次",
           font=font(15), fill=mix(BODY, accent, 0.35))
    d.text((x + 20, y + h - 6), tag, font=font(16), fill=FAINT)


def motif_code(d, box, accent, code, gpu_box, gpu_title, gpu_sub):
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=(11, 16, 26),
                        outline=mix(BG_TOP, accent, 0.4), width=2)
    d.line((x, y + 36, x + w, y + 36), fill=mix(BG_TOP, accent, 0.28), width=2)
    d.text((x + 18, y + 9), "intervention.py", font=font(15), fill=FAINT)
    mono = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 17)
    cy = y + 52
    for text, kind in code:
        col = accent if kind == "hot" else (WHITE if kind == "code" else FAINT)
        d.text((x + 22, cy), text, font=mono, fill=col)
        cy += 30

    gx, gy, gw, gh = gpu_box
    mx = x + w / 2
    d.line((mx, y + h + 4, mx, gy - 6), fill=accent, width=3)
    d.polygon([(mx, gy - 2), (mx - 8, gy - 16), (mx + 8, gy - 16)], fill=accent)
    d.text((mx + 16, y + h + 14), "排队到远程执行", font=font(16), fill=FAINT)

    d.rounded_rectangle((gx, gy, gx + gw, gy + gh), radius=12, fill=tint(accent, 0.14),
                        outline=accent, width=2)
    d.text((gx + gw / 2, gy + gh * 0.36), gpu_title, font=font(30, True), fill=WHITE, anchor="mm")
    d.text((gx + gw / 2, gy + gh * 0.72), gpu_sub, font=font(17), fill=mix(DIM, accent, 0.55), anchor="mm")


def motif_duplex(d, box, accent, tag):
    """One mixed track forks into two tracks that take turns."""
    x, y, w, h = box
    cy = y + h * 0.50
    y1, y2 = y + h * 0.34, y + h * 0.70

    # the single mixed track
    bw, gap = 9, 7
    for i, v in enumerate([0.34, 0.62, 0.44, 0.82, 0.52, 0.70, 0.30]):
        bx = x + i * (bw + gap)
        bh = v * h * 0.17
        col = accent if i % 2 else mix(BG_TOP, accent, 0.55)
        d.rounded_rectangle((bx, cy - bh, bx + bw, cy + bh), radius=3, fill=col)
    d.text((x, cy + h * 0.21), "1 路混合", font=font(16), fill=DIM)

    # the fork
    fork = mix(BG_TOP, accent, 0.62)
    d.line((x + w * 0.28, cy, x + w * 0.35, cy), fill=fork, width=4)
    d.line((x + w * 0.35, cy, x + w * 0.44, y1), fill=fork, width=4)
    d.line((x + w * 0.35, cy, x + w * 0.44, y2), fill=fork, width=4)
    d.text((x + w * 0.285, cy + 24), "分离", font=font(15), fill=mix(DIM, accent, 0.6))

    # two aligned tracks: whoever is not talking leaves a gap
    user_on = [1, 1, 1, 0, 1, 1, 1, 0]
    model_on = [0, 1, 1, 1, 0, 0, 1, 1]
    cx0, step, bwidth = x + w * 0.46, 36, 20
    heights = [26, 44, 30, 40, 34, 46, 24, 32]
    for i in range(len(user_on)):
        bx = cx0 + i * step
        if user_on[i]:
            d.rounded_rectangle((bx, y1 - heights[i], bx + bwidth, y1 + heights[i]),
                                radius=3, fill=accent)
        if model_on[i]:
            d.rounded_rectangle((bx, y2 - heights[i], bx + bwidth, y2 + heights[i]),
                                radius=3, fill=mix(BG_TOP, accent, 0.55))

    d.text((cx0, y1 - 62), "用户流", font=font(15), fill=mix(DIM, accent, 0.55))
    d.text((cx0, y2 + 52), "模型流", font=font(15), fill=mix(DIM, accent, 0.40))
    d.text((cx0, y2 + 82), "同一帧号对齐 · 每格 133 ms", font=font(14), fill=FAINT)
    d.text((x, y + h + 10), tag, font=font(16), fill=FAINT)


def motif_inverse(d, box, accent, tag):
    """A state, its changed self, and the arrow that brings it back."""
    x, y, w, h = box
    cy = y + h * 0.52
    bw, bh = 152, 118
    lx, rx = x + w * 0.03, x + w * 0.97 - bw

    d.rounded_rectangle((lx, cy - bh / 2, lx + bw, cy + bh / 2), radius=14,
                        fill=(14, 19, 30), outline=mix(BG_TOP, accent, 0.5), width=2)
    d.text((lx + bw / 2, cy - 8), "doc", font=font(26, True), fill=DIM, anchor="mm")
    d.text((lx + bw / 2, cy + 24), "旧", font=font(17), fill=FAINT, anchor="mm")

    d.rounded_rectangle((rx, cy - bh / 2, rx + bw, cy + bh / 2), radius=14,
                        fill=tint(accent, 0.28), outline=accent, width=3)
    d.text((rx + bw / 2, cy - 8), "doc'", font=font(26, True), fill=WHITE, anchor="mm")
    d.text((rx + bw / 2, cy + 24), "新", font=font(17), fill=mix(DIM, accent, 0.7), anchor="mm")

    x0, x1 = lx + bw + 16, rx - 16
    mid = (x0 + x1) / 2
    # forward
    d.line((x0, cy - 34, mid - 14, cy - 34), fill=accent, width=4)
    d.line((mid + 14, cy - 34, x1, cy - 34), fill=accent, width=4)
    arrow(d, (mid - 14, cy - 34), (mid + 14, cy - 34), color=accent, width=4, head=15)
    d.text((mid, cy - 56), "apply", font=font(16), fill=mix(DIM, accent, 0.6), anchor="mm")
    # and back
    d.line((x1, cy + 34, mid + 14, cy + 34), fill=mix(BG_TOP, accent, 0.45), width=4)
    d.line((mid - 14, cy + 34, x0, cy + 34), fill=mix(BG_TOP, accent, 0.45), width=4)
    arrow(d, (mid + 14, cy + 34), (mid - 14, cy + 34), color=mix(BG_TOP, accent, 0.45), width=4, head=15)
    d.text((mid, cy + 58), "返回的逆", font=font(15), fill=FAINT, anchor="mm")

    # the stack underneath
    sy = cy + bh / 2 + 34
    for i in range(3):
        wid = 210 - i * 26
        d.rounded_rectangle((x + w * 0.5 - wid / 2, sy + i * 13, x + w * 0.5 + wid / 2, sy + i * 13 + 8),
                            radius=4, fill=tint(accent, 0.55 - i * 0.14))
    d.text((x + w * 0.5, sy + 56), "undo 栈", font=font(15), fill=FAINT, anchor="ma")
    d.text((x, y + h + 10), tag, font=font(16), fill=FAINT)


def motif_wall(d, box, accent, tag):
    """Fifty app tiles on one wall, a handful of them heavy, and a single
    account bar running underneath all of them."""
    x, y, w, h = box
    cols, rows, gap, cell = 10, 5, 8, 44
    gw = cell * cols + gap * (cols - 1)
    gh = cell * rows + gap * (rows - 1)
    x0 = x + (w - gw) / 2
    y0 = y + (h - gh - 60) / 2 + 10
    heavy = {3, 12, 15, 24, 27, 31, 38, 42}
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            cx = x0 + c * (cell + gap)
            cy = y0 + r * (cell + gap)
            if i in heavy:
                fill = mix(MID, accent, 0.55)
                outline = accent
                wd = 2
            else:
                v = 0.09 + 0.05 * ((i * 7) % 3)
                fill = mix(BG_TOP, accent, v)
                outline = mix(BG_TOP, accent, 0.14)
                wd = 1
            d.rounded_rectangle((cx, cy, cx + cell, cy + cell), radius=4,
                                fill=fill, outline=outline, width=wd)

    bar_y = y0 + gh + 24
    d.rounded_rectangle((x0, bar_y, x0 + gw, bar_y + 30), radius=8,
                        fill=tint(accent, 0.30),
                        outline=mix(BG_TOP, accent, 0.58), width=2)
    d.text((x0 + 14, bar_y + 6), "1 个账号：文件 · KV · AI", font=font(16),
           fill=(216, 228, 242))
    d.text((x, bar_y + 40), tag, font=font(16), fill=FAINT)


def motif_nibbles(d, box, accent, tag):
    """Two 6x4 bit grids: the default (one amber bit in every row) against the
    unlocked one (the override bit set). The lock was a value, not a missing unit."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.06),
                        outline=mix(BG_TOP, accent, 0.30), width=2)

    rows, cw, ch, gx, gy = 6, 34, 34, 6, 12
    gw = 4 * cw + 3 * gx
    gh = rows * ch + (rows - 1) * gy
    gap = 44
    total = gw * 2 + gap
    lx = x + (w - total) // 2
    rx = lx + gw + gap
    top = y + 78
    amber = (188, 138, 62)

    d.text((lx, y + 26), "默认 0x00000001", font=font(17), fill=mix(DIM, amber, 0.75))
    d.text((rx, y + 26), "解锁 0x88888888", font=font(17), fill=mix(DIM, accent, 0.85))

    for r in range(rows):
        ry = top + r * (ch + gy)
        for c in range(4):
            cx = lx + c * (cw + gx)
            on = c == 3
            d.rounded_rectangle((cx, ry, cx + cw, ry + ch), radius=5,
                                fill=(70, 54, 32) if on else (22, 29, 42),
                                outline=mix(BG_TOP, amber if on else accent, 0.55 if on else 0.16),
                                width=2 if on else 1)
            cx2 = rx + c * (cw + gx)
            on2 = c == 0
            d.rounded_rectangle((cx2, ry, cx2 + cw, ry + ch), radius=5,
                                fill=mix(BG_TOP, accent, 0.62) if on2 else (22, 29, 42),
                                outline=mix(BG_TOP, accent, 0.9) if on2 else mix(BG_TOP, accent, 0.16),
                                width=2 if on2 else 1)

    mid_y = top + gh // 2
    arrow(d, (lx + gw + 8, mid_y), (rx - 8, mid_y), mix(DIM, accent, 0.7), 3, 12)

    d.multiline_text((x + 26, y + h - 70), tag, font=font(16), fill=FAINT, spacing=6)




def motif_words(d, box, accent, tag):
    """A script line of word chips, one span selected, a ruler whose ticks are
    computed rather than authored, and three variants off the same ruler."""
    x, y, w, h = box

    # --- word band: the editable unit is a word, not a second
    words = ["Bro", "more", "hair", "gel", "than", "trophies"]
    wy, wh, gap = y + 16, 40, 7
    wx = x + 2
    spans = []
    for name in words:
        cw = int(d.textlength(name, font=font(16))) + 24
        spans.append((wx, wx + cw))
        d.rounded_rectangle((wx, wy, wx + cw, wy + wh), radius=6,
                            fill=mix(BG_TOP, DIM, 0.16),
                            outline=mix(BG_TOP, DIM, 0.40), width=2)
        d.text((wx + cw / 2, wy + wh / 2), name, font=font(16),
               fill=mix(DIM, WHITE, 0.55), anchor="mm")
        wx += cw + gap

    # one span lifted into the accent: this is what later references point at
    a, b = spans[1][0], spans[5][1]
    br = wy + wh + 18
    d.rounded_rectangle((a - 7, wy - 7, b + 7, wy + wh + 5), radius=9,
                        outline=accent, width=3)
    d.line((a, br, b, br), fill=accent, width=2)
    for sx in (a, b):
        d.line((sx, wy + wh + 7, sx, br + 6), fill=accent, width=2)
    d.text((a, br + 10), "@{span} \u2192 story.selection", font=font(15),
           fill=mix(DIM, accent, 0.75))

    # --- the ruler: ticks come from measurement, so they are not evenly spaced
    ry = y + 168
    d.line((x + 2, ry, x + w - 4, ry), fill=accent, width=4)
    for t, big in ((0.01, True), (0.16, False), (0.33, True), (0.47, False),
                   (0.63, False), (0.79, True), (0.97, True)):
        tx = x + w * t
        d.line((tx, ry - (17 if big else 10), tx, ry + (17 if big else 10)),
               fill=accent if big else mix(BG_TOP, accent, 0.55), width=3 if big else 2)
    d.text((x + 2, ry + 28), "no authored seconds \u2014 measured extents", font=font(15),
           fill=mix(DIM, accent, 0.5))

    # --- variants: same ruler, three different fills
    vy, vh = y + 226, 156
    vw = (w - 2 * 14) / 3
    for i in range(3):
        vx = x + i * (vw + 14)
        hot = i == 1
        d.rounded_rectangle((vx, vy, vx + vw, vy + vh), radius=9,
                            fill=tint(accent, 0.5 if hot else 0.10),
                            outline=accent if hot else mix(BG_TOP, accent, 0.32), width=3 if hot else 2)
        for j, frac in enumerate((0.74, 0.52, 0.64, 0.40)):
            d.rounded_rectangle((vx + 14, vy + 20 + j * 30,
                                 vx + 14 + (vw - 28) * frac, vy + 20 + j * 30 + 11),
                                radius=4,
                                fill=mix(accent, WHITE, 0.55) if hot else mix(BG_TOP, DIM, 0.34))

    d.text((x, y + h + 14), tag, font=font(16), fill=FAINT)


def motif_nested(d, box, accent, tag):
    """A realization space narrowing: four nested frames, three acceptable
    points kept, one excluded, and the freedom each constraint spends."""
    x, y, w, h = box

    frames = [(0.0, 0.0, 1.0, 1.0, 0.48), (0.10, 0.09, 0.80, 0.74, 0.68),
              (0.20, 0.18, 0.60, 0.48, 0.86), (0.30, 0.27, 0.40, 0.22, 1.0)]
    for i, (fx, fy, fw, fh, k) in enumerate(frames):
        x0, y0 = x + w * fx, y + h * fy
        x1, y1 = x0 + w * fw, y0 + h * fh
        d.rounded_rectangle((x0, y0, x1, y1), radius=14 - i * 2,
                            fill=None if i < 4 else tint(accent, 0.30),
                            outline=mix(BG_TOP, accent, k), width=3 if i == 0 else 4)

    # three realizations inside the acceptable region, one outside it
    a0x, a0y = x + w * 0.30, y + h * 0.27
    for (px, py) in ((0.40, 0.40), (0.50, 0.44), (0.44, 0.46)):
        cx, cy = x + w * px, y + h * py
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=mix(accent, WHITE, 0.25))
    dx, dy = x + w * 0.86, y + h * 0.16
    d.ellipse((dx - 8, dy - 8, dx + 8, dy + 8), fill=(198, 84, 84))

    # the spent-freedom bar: one notch per constraint
    by = y + h - 34
    d.line((x + 8, by, x + w - 8, by), fill=mix(BG_TOP, accent, 0.35), width=2)
    for i in range(9):
        bx = x + 8 + (w - 16) * i / 8
        d.line((bx, by - 5, bx, by + 5), fill=mix(BG_TOP, accent, 0.45), width=2)
    d.text((x + 8, by - 24), "one constraint = one degree of freedom spent",
           font=font(15), fill=mix(DIM, accent, 0.45))

    d.text((x, y + h + 16), tag, font=font(16), fill=FAINT)


def motif_handoff(d, box, accent, tag):
    """Three automated stages, then a dashed slot with a button in it -- the
    click that stays human -- and one arrow looping over the auto-updating part."""
    x, y, w, h = box

    n, gap = 4, 14
    bw = (w - gap * (n - 1)) / n
    by, bh = y + 96, 96
    fills = [0.18, 0.42, 0.42, 0.0]
    for i in range(n):
        bx = x + i * (bw + gap)
        if fills[i]:
            d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=10,
                                fill=tint(accent, fills[i]),
                                outline=mix(BG_TOP, accent, 0.55), width=2)
        else:
            # dashed slot: the click the tool refuses to make
            d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=10, fill=(13, 18, 29))
            for k in range(0, int(bh), 12):
                d.line((bx, by + k, bx, by + min(k + 7, bh)), fill=accent, width=3)
                d.line((bx + bw, by + k, bx + bw, by + min(k + 7, bh)), fill=accent, width=3)
            for k in range(0, int(bw), 12):
                d.line((bx + k, by, bx + min(k + 7, bw), by), fill=accent, width=3)
                d.line((bx + k, by + bh, bx + min(k + 7, bw), by + bh), fill=accent, width=3)
            cx, cy = bx + bw / 2, by + bh / 2
            d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), outline=accent, width=3)

    # the update loop sits over the second stage only
    ax0 = x + (bw + gap) + bw / 2
    pts = []
    for t in range(0, 31):
        t = t / 30
        px = ax0 - 44 + 88 * t
        py = by - 16 - 34 * math.sin(math.pi * t)
        pts.append((px, py))
    d.line(pts, fill=accent, width=3, joint="curve")
    tip = pts[-1]
    d.polygon([(tip[0], tip[1] + 14), (tip[0] - 7, tip[1] + 1), (tip[0] + 7, tip[1] + 1)], fill=accent)
    d.text((ax0 - 44, by - 72), "chrome 自动更新", font=font(14), fill=mix(DIM, accent, 0.55))

    for i, name in enumerate(("skill", "plugin", "hub")):
        bx = x + i * (bw + gap)
        d.text((bx + bw / 2, by + bh - 24), name, font=font(17, True),
               fill=mix(WHITE, BG_TOP, 0.35), anchor="mm")

    d.text((x, y + h - 46), "8 个出口 · 4 自动 · 4 等你点", font=font(16), fill=mix(DIM, accent, 0.45))
    d.text((x, y + h + 14), tag, font=font(16), fill=FAINT)


# ------------------------------------------------------------------ cards

def motif_slot(d, box, accent, tag):
    """A wall with exactly one gap: everything the child agent cannot see stops
    at the wall, and a single contract passes through it."""
    x, y, w, h = box
    wall_x = x + 250
    gap_h = 88
    cy = y + h * 0.44

    d.rounded_rectangle((wall_x - 6, y, wall_x + 6, cy - gap_h / 2), radius=5, fill=accent)
    d.rounded_rectangle((wall_x - 6, cy + gap_h / 2, wall_x + 6, y + h), radius=5, fill=accent)

    blocked = ["intents/**", "packet.yaml", "queue-state", "runs.jsonl"]
    by = y + 18
    for name in blocked:
        d.rounded_rectangle((x, by, x + 190, by + 52), radius=9,
                            fill=tint(accent, 0.10), outline=mix(BG_TOP, accent, 0.30), width=2)
        d.text((x + 16, by + 26), name, font=font(17), fill=(150, 162, 180), anchor="lm")
        d.line((x + 198, by + 26, wall_x - 32, by + 26), fill=mix(BG_TOP, accent, 0.42), width=3)
        d.line((wall_x - 26, by + 17, wall_x - 12, by + 35), fill=(190, 84, 74), width=4)
        d.line((wall_x - 26, by + 35, wall_x - 12, by + 17), fill=(190, 84, 74), width=4)
        by += 74

    d.rounded_rectangle((wall_x + 24, cy - 34, wall_x + 24 + 200, cy + 34), radius=12,
                        fill=tint(accent, 0.32), outline=accent, width=3)
    d.text((wall_x + 124, cy), "issue body", font=font(20, True), fill=WHITE, anchor="mm")
    arrow(d, (wall_x + 8, cy), (wall_x + 22, cy), accent, 4, 12)
    d.text((wall_x + 24, cy + 56), "唯一通道", font=font(16), fill=mix(DIM, accent, 0.65))
    d.text((x, y + h + 12), tag, font=font(16), fill=FAINT)


def motif_grades(d, box, accent, tag):
    """A support matrix where a third of the cells are holes, not fills."""
    x, y, w, h = box
    cols, rows = 8, 6
    gap = 10
    cell = min((w - gap * (cols - 1)) / cols, (h - gap * (rows - 1)) / rows)
    gw = cell * cols + gap * (cols - 1)
    gh = cell * rows + gap * (rows - 1)
    x0 = x + (w - gw) / 2
    y0 = y + (h - gh) / 2
    for r in range(rows):
        for c in range(cols):
            v = GRADES[r][c]
            cx = x0 + c * (cell + gap)
            cy = y0 + r * (cell + gap)
            if v == 0:
                # a hole, not a filled cell: the column decides not to support it
                d.rounded_rectangle((cx, cy, cx + cell, cy + cell), radius=4,
                                    fill=(14, 19, 30),
                                    outline=mix(BG_TOP, accent, 0.30), width=2)
            else:
                d.rounded_rectangle((cx, cy, cx + cell, cy + cell), radius=4,
                                    fill=mix(MID, accent, v),
                                    outline=mix(BG_TOP, accent, 0.18 + 0.5 * v), width=1)
    d.text((x, y + h + 14), tag, font=font(17), fill=FAINT)


def motif_helix(d, box, accent, tag):
    """Two strands wound around each other — the name, drawn."""
    x, y, w, h = box
    cy = y + h * 0.44
    amp = h * 0.27
    n = 240
    a_pts, b_pts = [], []
    for i in range(n + 1):
        t = i / n
        px = x + w * t
        phase = math.sin(2 * math.pi * (t * 1.55) - 0.4)
        a_pts.append((px, cy - amp * phase))
        b_pts.append((px, cy + amp * phase))

    # rungs sit under the strands
    for k in range(1, 11):
        i = int((k / 11) * n)
        (ax, ay), (bx, by) = a_pts[i], b_pts[i]
        wide = abs(ay - by) > amp * 1.2
        d.line((ax, ay, bx, by), fill=accent if wide else tint(accent, 0.45),
               width=4 if wide else 3)

    d.line(a_pts, fill=accent, width=7, joint="curve")
    d.line(b_pts, fill=mix(BG_TOP, accent, 0.45), width=7, joint="curve")

    d.text((x, y + h + 10), tag, font=font(16), fill=FAINT)


def motif_tiers(d, box, accent, tag):
    """Three residency tiers, each labelled with the decode speed it buys."""
    x, y, w, h = box
    bands = [("VRAM", "最热专家 + dense 链", "9.0–9.2", 1.0, 7),
             ("RAM", "dense 常驻 + LRU 命中", "1.83", 0.42, 6),
             ("NVMe", "冷专家，按需 pread", "0.05–0.1", 0.12, 13)]
    bh, gap, bw = 104, 26, w * 0.70
    for i, (name, what, speed, lit, cells) in enumerate(bands):
        by = y + i * (bh + gap)
        d.rounded_rectangle((x, by, x + bw, by + bh), radius=12,
                            fill=tint(accent, 0.06 + 0.30 * lit) if lit > 0.2 else (12, 17, 27),
                            outline=mix(BG_TOP, accent, 0.18 + 0.60 * lit), width=2)
        d.text((x + 18, by + 11), name, font=font(22, True),
               fill=WHITE if lit > 0.5 else mix(BODY, BG_TOP, 0.45))
        d.text((x + 18, by + 43), what, font=font(15), fill=DIM)
        cw, cgap = 17, 7
        for c in range(cells):
            cx = x + 18 + c * (cw + cgap)
            if cx + cw > x + bw - 14:
                break
            on = (c % 2 == 0) if lit > 0.2 else (c % 4 == 0)
            d.rounded_rectangle((cx, by + bh - 31, cx + cw, by + bh - 14), radius=3,
                                fill=mix(accent, MID, 0.25) if on else tint(accent, 0.12))
        d.text((x + w * 0.74, by + bh / 2), speed, font=font(24, True),
               fill=mix(accent, WHITE, 0.2) if lit > 0.2 else FAINT, anchor="lm")

    d.text((x + w * 0.74, y - 32), "tok/s", font=font(15), fill=FAINT)
    d.text((x, y + 3 * (bh + gap) + 4), tag, font=font(16), fill=FAINT)


def motif_evidence(d, box, accent, tag):
    """A source document with three pieces of evidence inserted into the prose."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.07),
                        outline=mix(BG_TOP, accent, 0.34), width=2)
    d.text((x + 24, y + 16), "被改写的那一份来源", font=font(18), fill=mix(DIM, accent, 0.5))
    d.line((x + 24, y + 48, x + w - 24, y + 48), fill=mix(BG_TOP, accent, 0.22), width=2)

    widths = [0.40, 0.24, 0.40, 0.18, 0.58]
    chips = {0: "“据 2024 年行业报告”", 1: "62%", 2: "[来源 3]"}
    for i, wf in enumerate(widths):
        ly = y + 86 + i * 44
        bar_end = x + 26 + (w - 52) * wf
        d.rounded_rectangle((x + 26, ly, bar_end, ly + 11), radius=5,
                            fill=(44, 56, 76))
        if i in chips:
            txt = chips[i]
            f = font(17)
            tw = d.textlength(txt, font=f)
            d.rounded_rectangle((bar_end + 10, ly - 9, bar_end + 26 + tw, ly + 22), radius=6,
                                fill=tint(accent, 0.45), outline=accent, width=2)
            d.text((bar_end + 18, ly - 4), txt, font=f, fill=WHITE)
    d.text((x, y + h + 12), tag, font=font(17), fill=FAINT)


def motif_launcher(d, box, accent, tag):
    """Two launchers, one covering the other: the stock window behind, Aerial in
    front of it, with nothing but depth to say who won the foreground."""
    x, y, w, h = box

    # the stock launcher: a hero band and a recommendation grid, all grey
    sx, sy, sw, sh = x, y, 340, 232
    d.rounded_rectangle((sx, sy, sx + sw, sy + sh), radius=12,
                        fill=(14, 19, 29), outline=mix(BG_TOP, accent, 0.18), width=2)
    d.rounded_rectangle((sx + 16, sy + 18, sx + sw - 16, sy + 92), radius=8,
                        fill=(26, 32, 45))
    for r in range(2):
        for c in range(3):
            cx = sx + 16 + c * ((sw - 32) / 3)
            cy = sy + 106 + r * 56
            d.rounded_rectangle((cx, cy, cx + (sw - 44) / 3, cy + 44), radius=6,
                                fill=(26, 32, 45))
    d.text((sx + 2, sy - 28), "原厂桌面", font=font(16), fill=FAINT)

    # the aerial window: clock on top, a glass shelf of five tiles below
    fx, fy, fw, fh = x + 174, y + 136, 330, 208
    d.rounded_rectangle((fx, fy, fx + fw, fy + fh), radius=14,
                        fill=tint(accent, 0.16), outline=mix(BG_TOP, accent, 0.62), width=2)
    d.text((fx + 18, fy + 12), "12:29", font=font(30, True), fill=WHITE)
    d.text((fx + 18, fy + 52), "桌面守护已开启", font=font(15),
           fill=mix(DIM, accent, 0.8))

    sy2, sh2 = fy + fh - 66, 52
    d.rounded_rectangle((fx + 12, sy2, fx + fw - 12, sy2 + sh2), radius=10,
                        fill=mix(BG_TOP, accent, 0.18),
                        outline=mix(BG_TOP, accent, 0.34), width=2)
    for c in range(5):
        tx = fx + 22 + c * (44 + 12)
        hot = c == 0
        d.rounded_rectangle((tx, sy2 + 8, tx + 44, sy2 + sh2 - 8), radius=6,
                            fill=mix(accent, MID, 0.65) if hot else (32, 41, 56),
                            outline=WHITE if hot else mix(BG_TOP, accent, 0.24),
                            width=3 if hot else 1)
    d.text((fx, fy + fh + 12), tag, font=font(16), fill=FAINT)


def motif_seam(d, box, accent, tag):
    """A host slab above, a guest slab below, and the thin bright seam between
    them -- the only part of the stack this project actually wrote."""
    x, y, w, h = box
    pad = 18
    top_h = 118
    seam_y = y + top_h + 16
    bot_y = seam_y + 16

    # host slab: a launcher strip over a row of game cards
    d.rounded_rectangle((x, y, x + w, y + top_h), radius=12, fill=(15, 21, 33),
                        outline=mix(BG_TOP, accent, 0.26), width=2)
    d.rounded_rectangle((x + pad, y + 16, x + pad + 120, y + 30), radius=6,
                        fill=mix(BG_TOP, accent, 0.30))
    for c in range(4):
        cx = x + pad + c * ((w - 2 * pad) / 4)
        cw = (w - 2 * pad) / 4 - 14
        d.rounded_rectangle((cx, y + 44, cx + cw, y + top_h - 14), radius=7,
                            fill=(26, 34, 48), outline=mix(BG_TOP, accent, 0.16), width=1)
    d.text((x + 2, y - 26), "Android 主机", font=font(16), fill=FAINT)

    # the seam: accent bar with three notches, and two arrows crossing it
    d.rounded_rectangle((x, seam_y, x + w, seam_y + 16), radius=8, fill=accent)
    for nx in (0.22, 0.5, 0.78):
        cx = x + w * nx
        d.rounded_rectangle((cx - 3, seam_y - 5, cx + 3, seam_y + 21), radius=3,
                            fill=mix(accent, WHITE, 0.55))
    arrow(d, (x + 58, seam_y - 30), (x + 58, seam_y + 44), WHITE, 3, 11)
    arrow(d, (x + w - 58, seam_y + 46), (x + w - 58, seam_y - 28), WHITE, 3, 11)

    # guest slab: a terminal, dim lines and one bright prompt
    gh = y + h - bot_y
    d.rounded_rectangle((x, bot_y, x + w, bot_y + gh), radius=12, fill=(11, 15, 24),
                        outline=mix(BG_TOP, accent, 0.22), width=2)
    for i, lw in enumerate((0.52, 0.34, 0.61, 0.28)):
        ly = bot_y + 22 + i * 26
        d.rounded_rectangle((x + pad, ly, x + pad + (w - 2 * pad) * lw, ly + 9), radius=4,
                            fill=(40, 50, 68))
    d.rounded_rectangle((x + pad, bot_y + 22 + 4 * 26, x + pad + 14, bot_y + 22 + 4 * 26 + 9),
                        radius=4, fill=accent)
    d.text((x + 2, bot_y + gh + 12), "Ubuntu 客人", font=font(16), fill=FAINT)
    d.text((x, bot_y + gh + 40), tag, font=font(17), fill=mix(DIM, accent, 0.45))


def motif_gates(d, box, accent, tag):
    """A diagram on a 4px grid, one accent node, one node crossed out, and the
    row of gates that would have caught the rest."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)
    for gx in range(int(x) + 20, int(x + w) - 12, 16):
        d.line((gx, y + 10, gx, y + h - 10), fill=mix(BG_TOP, accent, 0.12), width=1)
    for gy in range(int(y) + 20, int(y + h) - 12, 16):
        d.line((x + 10, gy, x + w - 10, gy), fill=mix(BG_TOP, accent, 0.12), width=1)

    nodes = {
        "a": (x + 36, y + 36, 100, 44, "网关", False),
        "b": (x + 196, y + 36, 100, 44, "订单", True),
        "c": (x + 356, y + 36, 100, 44, "库存", False),
        "e": (x + 96, y + 136, 100, 44, "队列", False),
        "f": (x + 256, y + 136, 100, 44, "支付", False),
        "g": (x + 196, y + 236, 100, 44, "库", False),
    }
    for k, (nx, ny, nw, nh, name, hot) in nodes.items():
        d.rounded_rectangle((nx, ny, nx + nw, ny + nh), radius=8,
                            fill=accent if hot else (16, 22, 34),
                            outline=accent if hot else mix(BG_TOP, accent, 0.5), width=2)
        d.text((nx + nw / 2, ny + nh / 2), name, font=font(20, hot),
               fill=(18, 22, 30) if hot else (222, 230, 242), anchor="mm")

    # orthogonal, one bend each — the only legal connector
    for a, b in (("a", "e"), ("b", "f"), ("c", "f"), ("e", "g"), ("f", "g")):
        ax, ay, aw, ah, _, _ = nodes[a]
        bx, by, bw, bh, _, _ = nodes[b]
        mx = ax + aw / 2
        my = ay + ah + 22
        d.line((mx, ay + ah, mx, my), fill=mix(BG_TOP, accent, 0.62), width=3)
        d.line((mx, my, bx + bw / 2, my), fill=mix(BG_TOP, accent, 0.62), width=3)
        d.line((bx + bw / 2, my, bx + bw / 2, by), fill=mix(BG_TOP, accent, 0.62), width=3)
        d.polygon([(bx + bw / 2, by), (bx + bw / 2 - 6, by - 10),
                   (bx + bw / 2 + 6, by - 10)], fill=mix(BG_TOP, accent, 0.62))

    # the node that got deleted
    gx, gy, gw2, gh2 = x + 398, y + 196, 96, 42
    for i in range(0, gw2, 8):
        d.line((gx + i, gy, gx + min(i + 5, gw2), gy), fill=FAINT, width=2)
        d.line((gx + i, gy + gh2, gx + min(i + 5, gw2), gy + gh2), fill=FAINT, width=2)
    for i in range(0, gh2, 8):
        d.line((gx, gy + i, gx, gy + min(i + 5, gh2)), fill=FAINT, width=2)
        d.line((gx + gw2, gy + i, gx + gw2, gy + min(i + 5, gh2)), fill=FAINT, width=2)
    d.line((gx + 18, gy + 12, gx + gw2 - 18, gy + gh2 - 12), fill=mix(FAINT, accent, 0.4), width=3)
    d.line((gx + 18, gy + gh2 - 12, gx + gw2 - 18, gy + 12), fill=mix(FAINT, accent, 0.4), width=3)

    # the gates underneath
    gates = ["网格", "对比度", "几何", "单文件", "CJK", "导出"]
    cy = y + h + 22
    cw = (w - 5 * 10) / 6
    for i, name in enumerate(gates):
        cx = x + i * (cw + 10)
        d.rounded_rectangle((cx, cy, cx + cw, cy + 34), radius=8,
                            fill=tint(accent, 0.22), outline=mix(BG_TOP, accent, 0.5), width=2)
        d.line((cx + 12, cy + 17, cx + 17, cy + 23), fill=accent, width=3)
        d.line((cx + 17, cy + 23, cx + 27, cy + 10), fill=accent, width=3)
        d.text((cx + 32, cy + 9), name, font=font(15), fill=(214, 224, 240))
    d.text((x, cy + 44), tag, font=font(16), fill=FAINT)


def motif_pages(d, box, accent, tag=None):
    """Three sequences paged into one block pool: the block table is the ledger."""
    x, y, w, h = box
    cols, rows, gap = 7, 5, 11
    cell = min((w - gap * (cols - 1)) / cols, (h - 64 - gap * (rows - 1)) / rows)
    gw = cell * cols + gap * (cols - 1)
    gh = cell * rows + gap * (rows - 1)
    x0 = x + (w - gw) / 2
    y0 = y + 26

    def center(i):
        r, c = divmod(i, cols)
        return (x0 + c * (cell + gap) + cell / 2, y0 + r * (cell + gap) + cell / 2)

    chains = [
        ([1, 9, 16], accent, 1.0),
        ([3, 10, 11], (226, 150, 70), 0.92),
        ([5, 19, 26, 32], (86, 196, 186), 0.92),
    ]
    # grid: every block exists, only some are owned
    owned = {}
    for cells, color, _k in chains:
        for c in cells:
            owned[c] = color
    for i in range(cols * rows):
        cx, cy = center(i)
        d.rounded_rectangle((cx - cell / 2, cy - cell / 2, cx + cell / 2, cy + cell / 2),
                            radius=4, fill=tint(accent, 0.08),
                            outline=mix(BG_TOP, accent, 0.16), width=1)
    # mapping lines, then the blocks on top
    for cells, color, k in chains:
        for a, b in zip(cells[:-1], cells[1:]):
            pa, pb = center(a), center(b)
            mid = (pa[0] + pb[0]) / 2
            line = mix(BG_TOP, color, 0.85)
            d.line((pa[0], pa[1], mid, pa[1]), fill=line, width=3)
            d.line((mid, pa[1], mid, pb[1]), fill=line, width=3)
            d.line((mid, pb[1], pb[0], pb[1]), fill=line, width=3)
    for i, color in owned.items():
        cx, cy = center(i)
        d.rounded_rectangle((cx - cell / 2, cy - cell / 2, cx + cell / 2, cy + cell / 2),
                            radius=4, fill=mix(BG_TOP, color, 0.78), outline=color, width=2)
    for cells, color, _k in chains:
        cx, cy = center(cells[0])
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=WHITE)
    if tag:
        d.text((x0, y0 + gh + 22), tag, font=font(19), fill=mix(DIM, accent, 0.45))


def band_shares(d, x0, x1, y, accent):
    """Five sources splitting one answer; the third one grew."""
    shares = [19.3, 19.3, 27.2, 17.1, 17.1]
    gap = 10
    avail = (x1 - x0) - gap * (len(shares) - 1)
    cx = x0
    for i, v in enumerate(shares):
        bw = avail * v / sum(shares)
        hot = i == 2
        d.rounded_rectangle((cx, y, cx + bw, y + 34), radius=6,
                            fill=tint(accent, 0.45 if hot else 0.10),
                            outline=accent if hot else mix(BG_TOP, accent, 0.26), width=2)
        d.text((cx + 12, y + 6), f"{v:.1f}", font=font(18), fill=WHITE if hot else FAINT)
        cx += bw + gap


def motif_registry(d, box, accent, tag=None):
    """73 records, every one of them still unchecked."""
    x, y, w, h = box
    cols, rows, total = 11, 7, 73
    gap = 8
    cell = min((w - gap * (cols - 1)) / cols, (h - 76 - gap * (rows - 1)) / rows)
    gw = cell * cols + gap * (cols - 1)
    gh = cell * rows + gap * (rows - 1)
    x0 = x + (w - gw) / 2
    y0 = y + 34
    d.text((x, y), "backend/config/model_licenses.json", font=font(18), fill=mix(DIM, accent, 0.45))
    n = 0
    for r in range(rows):
        for c in range(cols):
            if n >= total:
                break
            cx = x0 + c * (cell + gap)
            cy = y0 + r * (cell + gap)
            d.rounded_rectangle((cx, cy, cx + cell, cy + cell), radius=3,
                                outline=mix(BG_TOP, accent, 0.30), width=2)
            n += 1
    ty = y0 + gh + 26
    d.text((x0, ty - 4), "0", font=font(38, True), fill=accent)
    d.text((x0 + 30, ty + 6), "条标了 commercial_use: true", font=font(19), fill=BODY)
    d.text((x0 + 30, ty + 34), "默认引擎那一条写的是 CC-BY-NC", font=font(18), fill=mix(DIM, accent, 0.55))


def motif_funnel(d, box, accent, tag=None):
    """Four surfaces, one process boundary, one database — and no queue."""
    x, y, w, h = box
    edge = mix(accent, MID, 0.25)
    d.rounded_rectangle((x, y, x + w, y + h), radius=24, fill=tint(accent, 0.12),
                        outline=edge, width=3)
    if tag:
        d.text((x + 28, y + 24), tag, font=font(18), fill=mix(DIM, accent, 0.55))

    chips = ["Web", "IM", "Cron", "CLI"]
    cw = (w - 56 - 36) / 4
    ch_h = 46
    cy = y + 66
    centers = []
    for i, c in enumerate(chips):
        cx = x + 28 + i * (cw + 12)
        d.rounded_rectangle((cx, cy, cx + cw, cy + ch_h), radius=9,
                            fill=mix(MID, BG_TOP, 0.25), outline=accent, width=2)
        d.text((cx + cw / 2, cy + ch_h / 2), c, font=font(19), fill=WHITE, anchor="mm")
        centers.append(cx + cw / 2)

    spine = cy + ch_h + 40
    for cxx in centers:
        d.line((cxx, cy + ch_h, cxx, spine), fill=mix(accent, MID, 0.35), width=3)
    d.line((centers[0], spine, centers[-1], spine), fill=accent, width=3)
    mid = (centers[0] + centers[-1]) / 2

    node_y = spine + 22
    d.line((mid, spine, mid, node_y), fill=accent, width=3)
    nw, nh = 300, 56
    d.rounded_rectangle((mid - nw / 2, node_y, mid + nw / 2, node_y + nh), radius=10,
                        fill=mix(MID, accent, 0.30), outline=accent, width=2)
    d.text((mid, node_y + nh / 2), "HarnessProcessor", font=font(19), fill=WHITE, anchor="mm")

    db_y = node_y + nh + 34
    arrow(d, (mid, node_y + nh), (mid, db_y), mix(accent, MID, 0.35), width=3, head=10)
    dw = 320
    d.rounded_rectangle((mid - dw / 2, db_y, mid + dw / 2, db_y + 56), radius=10,
                        fill=mix(MID, BG_TOP, 0.25), outline=mix(accent, MID, 0.5), width=2)
    d.text((mid, db_y + 28), "SQLite / PostgreSQL", font=font(18), fill=BODY, anchor="mm")

    ax, ay = x + 28, y + h + 26
    aw = 258
    d.rounded_rectangle((ax, ay, ax + aw, ay + 44), radius=9,
                        fill=(20, 27, 40), outline=mix(DIM, BG_TOP, 0.35), width=2)
    d.text((ax + 18, ay + 22), "×", font=font(24, True), fill=(192, 84, 78), anchor="lm")
    d.text((ax + 48, ay + 22), "没有队列 · 没有 worker", font=font(17),
           fill=FAINT, anchor="lm")


def motif_refs(d, box, accent, tag):
    """Two histories in one repo: a commit spine, a ledger of intent events,
    and the single note that crosses between them."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.06),
                        outline=mix(BG_TOP, accent, 0.34), width=2)

    sx = x + 58
    top, bot = y + 40, y + h - 84
    d.line((sx, top, sx, bot), fill=mix(DIM, accent, 0.28), width=4)
    dots = [top + (bot - top) * i / 4 for i in range(5)]
    for i, cy in enumerate(dots):
        on = i == 2
        d.ellipse((sx - 7, cy - 7, sx + 7, cy + 7),
                  fill=mix(accent, WHITE, 0.55) if on else mix(accent, BG_TOP, 0.25))

    cy = dots[2]
    d.line((sx + 9, cy, sx + 74, cy), fill=accent, width=3)
    d.rounded_rectangle((sx + 74, cy - 19, sx + 74 + 112, cy + 19), radius=9,
                        fill=accent, outline=accent, width=2)
    d.text((sx + 74 + 52, cy), "note", font=font(18, True), fill=(16, 20, 28), anchor="mm")

    lx = x + w - 132
    for i in range(9):
        ry = y + 42 + i * 22
        bw = 92 + (i * 37) % 30
        d.rounded_rectangle((lx, ry, lx + bw, ry + 11), radius=5,
                            fill=tint(accent, 0.72 if i % 3 == 1 else 0.4))
    d.text((lx + 4, y + h - 74), "intent events", font=font(15),
           fill=mix(DIM, accent, 0.45), anchor="lm")

    d.text((x + 24, y + h - 34), tag, font=font(18), fill=mix(DIM, accent, 0.55), anchor="lm")


def motif_verdict(d, box, accent, tag):
    """Source languages on the left, a bridge in the middle, Rust on the right
    with a tick — and a verdict chip that can still say no."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.06),
                        outline=mix(BG_TOP, accent, 0.34), width=2)

    for i, name in enumerate(["TS", "Py", "Go"]):
        cy = y + 66 + i * 62
        d.rounded_rectangle((x + 34, cy - 19, x + 34 + 58, cy + 19), radius=8,
                            fill=tint(accent, 0.30), outline=mix(BG_TOP, accent, 0.5), width=2)
        d.text((x + 34 + 29, cy), name, font=font(17, True), fill=BODY, anchor="mm")
        d.line((x + 96, cy, x + 168, cy), fill=mix(BG_TOP, accent, 0.55), width=2)

    bx = x + 176
    d.line((bx, y + 52, bx, y + 242), fill=accent, width=3)
    d.rounded_rectangle((bx - 6, y + 116, bx + 62, y + 178), radius=8,
                        fill=tint(accent, 0.45), outline=accent, width=2)
    d.text((bx + 28, y + 147), "桥", font=font(20, True), fill=WHITE, anchor="mm")

    rx = x + 262
    d.rounded_rectangle((rx, y + 58, x + w - 34, y + 236), radius=12,
                        fill=tint(accent, 0.16), outline=accent, width=2)
    d.text((rx + 24, y + 88), "Rust", font=font(26, True), fill=WHITE)
    cx, cy = rx + 34, y + 158
    d.line((cx - 10, cy, cx - 2, cy + 10), fill=WHITE, width=5)
    d.line((cx - 2, cy + 10, cx + 14, cy - 12), fill=WHITE, width=5)
    d.text((rx + 24, y + 200), "0 不一致", font=font(17), fill=BODY)

    d.rounded_rectangle((x + 34, y + h - 84, x + w - 34, y + h - 34), radius=10,
                        fill=(26, 18, 14), outline=(206, 108, 84), width=2)
    d.text((x + 54, y + h - 59), tag, font=font(17, True), fill=(226, 128, 104), anchor="lm")


def motif_narrow(d, box, accent, tag):
    """A broad grey distribution and the narrow spike the same preference
    optimization leaves behind."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)
    base = y + h - 88
    left, right = x + 30, x + w - 30
    d.line((left, base, right, base), fill=mix(BG_TOP, accent, 0.28), width=2)

    def curve(cx, sg, height, col, width, power=2, fill=None):
        pts = []
        px = left
        while px <= right:
            v = math.exp(-((abs(px - cx) / sg) ** power))
            pts.append((px, base - height * v))
            px += 2
        if fill:
            d.polygon(pts + [(right, base), (left, base)], fill=fill)
        for a, b in zip(pts[:-1], pts[1:]):
            d.line((a[0], a[1], b[0], b[1]), fill=col, width=width)

    peak = x + w * 0.62
    curve(peak, 26, 196, accent, 4, fill=tint(accent, 0.20))
    curve(x + w * 0.46, 118, 84, (152, 160, 174), 3, power=4)

    d.line((peak, base, peak, base - 58), fill=mix(accent, MID, 0.5), width=2)
    d.text((x + 24, y + 26), "分布越训越窄", font=font(19), fill=mix(DIM, accent, 0.55))
    d.text((x + 24, y + h - 30), tag, font=font(17), fill=mix(DIM, accent, 0.55), anchor="lm")


def motif_budget(d, box, accent, tag):
    """Two hard constraints — a peak-memory ceiling and a decode floor —
    meeting at the corner where the model size gets chosen."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)

    cx, cy = x + w * 0.60, y + h - 104
    d.rectangle((x + 24, y + 30, cx, cy), fill=mix(BG_TOP, accent, 0.22),
                outline=mix(BG_TOP, accent, 0.45), width=2)

    d.line((x + 24, cy, x + w - 30, cy), fill=mix(accent, WHITE, 0.35), width=3)
    for gx in range(int(x + 24), int(x + w - 30), 14):
        d.line((gx, cy, gx, cy + 8), fill=mix(accent, WHITE, 0.25), width=2)
    d.line((cx, y + 30, cx, cy), fill=mix(accent, WHITE, 0.35), width=3)

    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=accent)
    d.text((cx + 22, cy - 30), "0.3B", font=font(24, True), fill=WHITE, anchor="lm")

    d.text((x + 24, cy + 26), "参数量 →", font=font(16), fill=mix(DIM, WHITE, 0.35))
    d.text((x + 40, y + 44), "可行区", font=font(17, True), fill=mix(WHITE, accent, 0.5))
    d.text((cx + 16, y + 44), "Decode", font=font(16), fill=mix(DIM, WHITE, 0.35))
    d.text((cx + 16, y + 68), "≥ 200 tok/s", font=font(16), fill=mix(DIM, WHITE, 0.35))
    d.text((x + 24, y + h - 34), tag, font=font(17), fill=mix(DIM, accent, 0.55), anchor="lm")


def motif_compress(d, box, accent, tag):
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)

    px, py, pw, ph = x + 34, y + 42, 118, 132
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=8, fill=(206, 214, 232),
                        outline=mix(BG_TOP, accent, 0.5), width=2)
    for i in range(5):
        ly = py + 20 + i * 22
        d.rounded_rectangle((px + 14, ly, px + 14 + (70 if i % 2 else 90), ly + 6), radius=3,
                            fill=(150, 162, 190))

    cx0, cx1 = px + pw + 24, px + pw + 84
    d.polygon([(cx0, py + 24), (cx0, py + ph - 24), (cx1, py + ph / 2 + 26), (cx1, py + ph / 2 - 26)],
              fill=tint(accent, 0.30), outline=accent)

    tx = cx1 + 28
    for i in range(4):
        for j in range(4):
            d.rounded_rectangle((tx + i * 24, py + 24 + j * 24, tx + i * 24 + 16, py + 24 + j * 24 + 16),
                                radius=4, fill=accent)

    ly = py + ph + 14
    d.text((px, ly), "1,024²", font=font(15), fill=mix(DIM, WHITE, 0.4))
    d.text((cx0 + 6, ly), "16x", font=font(15, True), fill=mix(DIM, accent, 0.7))
    d.text((tx, ly), "256", font=font(15, True), fill=mix(DIM, accent, 0.7))

    oy = ly + 48
    d.text((x + 34, oy - 24), "输出：一页 1,085 token", font=font(15), fill=mix(DIM, WHITE, 0.45))
    for i in range(3):
        d.rounded_rectangle((x + 34, oy + i * 24, x + w - 34, oy + i * 24 + 14), radius=4,
                            fill=tint(accent, 0.45 if i == 0 else 0.25))

    d.text((x + 34, y + h - 30), tag, font=font(17), fill=mix(DIM, accent, 0.6), anchor="lm")


def motif_cards(d, box, accent, tag):
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)

    d.text((x + 26, y + 24), "124 张卡 · 150 个镜头", font=font(17), fill=mix(DIM, accent, 0.5))

    cw, gap = 96, 18
    total = 4 * cw + 3 * gap
    x0 = x + (w - total) / 2
    cy = y + 74
    for i in range(4):
        cx = x0 + i * (cw + gap)
        hot = i == 1
        d.rounded_rectangle((cx, cy, cx + cw, cy + 150), radius=10,
                            fill=tint(accent, 0.55) if hot else tint(accent, 0.12),
                            outline=mix(BG_TOP, accent, 0.55), width=2)
        d.line((cx + 14, cy + 26, cx + cw - 14, cy + 26), fill=mix(DIM, WHITE, 0.35), width=3)
        d.line((cx + 14, cy + 46, cx + cw - 34, cy + 46), fill=mix(DIM, WHITE, 0.35), width=3)
        d.line((cx + 14, cy + 66, cx + cw - 24, cy + 66), fill=mix(DIM, WHITE, 0.25), width=3)
        if hot:
            d.rounded_rectangle((cx + 14, cy + 100, cx + cw - 14, cy + 128), radius=6,
                                fill=accent)
            d.text((cx + cw / 2, cy + 114), "shot", font=font(14, True), fill=(26, 20, 12),
                   anchor="mm")
        else:
            d.line((cx + 14, cy + 108, cx + cw - 40, cy + 108), fill=mix(DIM, WHITE, 0.22), width=3)

    d.text((x + 26, y + h - 62), "点名字就够：deck-deal-flyin", font=font(16), fill=mix(DIM, accent, 0.6))
    d.text((x + 26, y + h - 34), tag, font=font(17), fill=mix(DIM, accent, 0.55), anchor="lm")


def motif_quant_tiers(d, box, accent, tag):
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)

    rows = [("14.23 GB", 0.96, "BF16"), ("7.12 GB", 0.52, "FP8"), ("3.67 GB", 0.26, "NF4")]
    for i, (label_txt, frac, name) in enumerate(rows):
        ry = y + 54 + i * 78
        d.text((x + 30, ry), name, font=font(15), fill=mix(DIM, WHITE, 0.4))
        bw = (w - 200) * frac
        d.rounded_rectangle((x + 96, ry - 4, x + 96 + bw, ry + 22), radius=6,
                            fill=tint(accent, 0.55 if i == 2 else 0.25),
                            outline=mix(BG_TOP, accent, 0.55), width=2)
        d.text((x + 96 + bw + 14, ry + 9), label_txt, font=font(15, True),
               fill=accent if i == 2 else mix(DIM, WHITE, 0.5), anchor="lm")

    d.line((x + 30, y + h - 96, x + w - 30, y + h - 96), fill=mix(BG_TOP, accent, 0.35), width=2)
    d.text((x + 30, y + h - 74), "同一份权重，12 个构建", font=font(16), fill=mix(DIM, WHITE, 0.5))
    d.text((x + 30, y + h - 34), tag, font=font(17), fill=mix(DIM, accent, 0.55), anchor="lm")


def motif_lora(d, box, accent, tag):
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)

    # frozen W
    d.rounded_rectangle((x + 44, y + 40, x + 236, y + 250), radius=10,
                        fill=tint(accent, 0.10), outline=mix(BG_TOP, accent, 0.45), width=2)
    d.text((x + 140, y + 128), "W", font=font(40, True), fill=mix(DIM, WHITE, 0.35), anchor="mm")
    d.text((x + 140, y + 178), "冻结", font=font(15), fill=mix(DIM, WHITE, 0.3), anchor="mm")

    d.text((x + 256, y + 140), "+", font=font(30, True), fill=mix(DIM, WHITE, 0.4), anchor="mm")

    # B slab
    d.rounded_rectangle((x + 292, y + 40, x + 334, y + 250), radius=8,
                        fill=tint(accent, 0.45), outline=accent, width=2)
    d.text((x + 313, y + 262), "B", font=font(16, True), fill=mix(DIM, accent, 0.7), anchor="ma")
    # A slab
    d.rounded_rectangle((x + 348, y + 196, x + 500, y + 250), radius=8,
                        fill=tint(accent, 0.45), outline=accent, width=2)
    d.text((x + 424, y + 262), "A", font=font(16, True), fill=mix(DIM, accent, 0.7), anchor="ma")

    d.text((x + 44, y + 282), "671 MB 只训练 A 与 B，W 不动", font=font(15), fill=mix(DIM, WHITE, 0.42))
    d.text((x + 44, y + h - 34), tag, font=font(16), fill=mix(DIM, accent, 0.55), anchor="lm")


def motif_twocloud(d, box, accent, tag):
    """Two density clouds side by side, a reticle in the overlap, and two arcs
    that carry each agent's model of the other across the gap."""
    x, y, w, h = box
    c1 = (x + w * 0.30, y + h * 0.44)
    c2 = (x + w * 0.70, y + h * 0.56)
    rx, ry = 124, 90

    for cx, cy in (c1, c2):
        for i in range(4, 0, -1):
            k = i / 4
            d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k),
                      fill=tint(accent, 0.10 + 0.36 * (1 - k)))
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry),
                  outline=mix(BG_TOP, accent, 0.55), width=2)

    # the reticle sits where the two clouds overlap, on neither agent
    mx, my = (c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2
    r = 24
    d.ellipse((mx - r, my - r, mx + r, my + r), outline=WHITE, width=3)
    d.line((mx - r - 13, my, mx - r + 4, my), fill=WHITE, width=3)
    d.line((mx + r - 4, my, mx + r + 13, my), fill=WHITE, width=3)
    d.line((mx, my - r - 13, mx, my - r + 4), fill=WHITE, width=3)
    d.line((mx, my + r - 4, mx, my + r + 13), fill=WHITE, width=3)

    def arc(p0, p1, lift, color):
        ctrl = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + lift)
        pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * ctrl[0] + t * t * p1[0],
                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * ctrl[1] + t * t * p1[1])
               for t in (i / 40 for i in range(41))]
        d.line(pts, fill=color, width=3, joint="curve")
        arrow(d, pts[-5], pts[-1], color, 3, 12)

    arc((c1[0] + 40, c1[1] - 80), (c2[0] - 40, c2[1] - 86), -80, mix(accent, WHITE, 0.42))
    arc((c2[0] - 40, c2[1] + 84), (c1[0] + 40, c1[1] + 80), 80, mix(accent, WHITE, 0.42))

    d.text((x + 6, y + h + 14), tag, font=font(16), fill=FAINT)


def motif_phaselag(d, box, accent, tag):
    """Two action traces that answer each other with a delay: the lag is the
    only part of the loop you can actually measure from outside."""
    x, y, w, h = box
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=tint(accent, 0.05),
                        outline=mix(BG_TOP, accent, 0.32), width=2)
    d.text((x + 26, y + 24), "两条行动曲线，差一个反应延迟", font=font(17),
           fill=mix(DIM, accent, 0.5))

    x0, x1 = x + 44, x + w - 44
    mid = y + 208
    amp = 74.0
    cyc = 2.2 * math.pi

    def trace(shift, color, width=3):
        pts = []
        for i in range(161):
            u = i / 160
            px = x0 + (x1 - x0) * u
            py = mid - amp * math.sin(cyc * u + shift)
            pts.append((px, py))
        d.line(pts, fill=color, width=width, joint="curve")
        return pts

    a_pts = trace(0.0, accent)
    b_pts = trace(-0.62, mix(accent, WHITE, 0.42), width=2)

    d.line((x0, mid, x1, mid), fill=mix(BG_TOP, accent, 0.26), width=1)

    # the lag between the two peaks, marked by two guides
    def peak_x(shift):
        best, bx_ = -1e9, x0
        for i in range(161):
            u = i / 160
            v = math.sin(cyc * u + shift)
            if v > best:
                best, bx_ = v, x0 + (x1 - x0) * u
        return bx_

    pa, pb = peak_x(0.0), peak_x(-0.62)
    for px in (pa, pb):
        for yy in range(y + 96, mid + 6, 14):
            d.line((px, yy, px, yy + 7), fill=mix(BG_TOP, accent, 0.45), width=2)

    d.line((pb, mid - amp - 26, pa, mid - amp - 26), fill=mix(DIM, WHITE, 0.45), width=2)
    for px in (pa, pb):
        d.line((px, mid - amp - 34, px, mid - amp - 18), fill=mix(DIM, WHITE, 0.45), width=2)
    d.text(((pa + pb) / 2, mid - amp - 46), "相位滞后", font=font(16), fill=mix(DIM, WHITE, 0.62),
           anchor="mm")

    d.text((x + 44, y + h - 62), "延迟固定、响应不固定：这是闭环的指纹", font=font(16), fill=mix(DIM, WHITE, 0.5))
    d.text((x + 44, y + h - 30), tag, font=font(17), fill=mix(DIM, accent, 0.55), anchor="lm")


def build(slug, out_dir):
    A = CARDS[slug]
    accent = A["color"]
    img, d = canvas(A["glow"], accent, A.get("glow_r", 430), A.get("strength", 0.32))

    if slug == "saelens":
        head(d, accent, "Decode Research / MIT / v6",
             "SAELens", "重建误差不告诉你特征对不对",
             (M, 138), 112, (M, 320), 560)
        motif_grid(d, (690, 112, 430, 320), accent, cols=13, rows=9,
                   lit=[12, 25, 38, 41, 57, 70, 83, 96, 104, 21, 64, 88],
                   ring=(3, 4), tag="1 / 16384")
        d.text((694, 460), "2304 维激活 到 16384 个稀疏方向", font=font(21), fill=DIM)
        d.text((694, 494), "重建误差降下去，不代表特征为真", font=font(21), fill=mix(DIM, accent, 0.6))

    elif slug == "tokeneconomizer":
        head(d, accent, "Microsoft Research / UC Berkeley / Apache 2.0",
             "TokenEconomizer", "成本按仓库累积，不按任务计价",
             (M, 124), 84, (M, 244), 700)
        motif_area(d, (M, 348, W - 2 * M, 146), accent,
                   [0.02, 0.03, 0.05, 0.07, 0.13, 0.21, 0.46, 0.72, 0.86, 0.94],
                   "同一个仓库 / 12 个任务 / 一份预算", "累计成本", "任务")
        d.text((W - M, 250), "失败的 32% 也在计费", font=font(22),
               fill=mix(DIM, accent, 0.6), anchor="ra")

    elif slug == "transformer-explainer":
        motif_browser(d, (M, 112, 496, 392), accent,
                      ["The", "cat", "sat", "on", "the", "mat"],
                      [(0, 0.32, 168), (1, 0.6, 120), (3, 0.95, 66)],
                      "softmax 到下一个 token")
        head(d, accent, "Georgia Tech / ONNX Runtime Web",
             "Transformer\nExplainer", "把 GPT-2 塞进浏览器，让模型边算边解释自己",
             (W - M, 146), 80, (W - M, 350), 420, align="right", thesis_size=27)
        d.text((W - M, 500), "Svelte / D3", font=font(21), fill=mix(DIM, accent, 0.6), anchor="ra")

    elif slug == "boubou":
        head(d, accent, "Local Voice AI Runtime / Rust / MIT",
             "Boubou", "本地语音模型变成全屋可调用的服务",
             (M, 146), 112, (M, 326), 520)
        motif_rings(d, 930, 262, accent, "一台机器，全屋可调用", "barge-in / QR + 密钥 / MIT")

    elif slug == "hy-mt2":
        head(d, accent, "Tencent Hunyuan / 1T tokens / 33 languages",
             "Hy-MT2", "把翻译拆成语言家族分头训练，再蒸馏回一个模型",
             (M, 138), 104, (M, 296), 420)
        motif_tree(d, (500, 104, 628, 388), accent, "1 个 1.25-bit 模型",
                   "EN / ZH / JA / 33 种语言，一支语料路由")
        d.text((M, 462), "Chimera Teacher / 在线蒸馏 / 家族 GRPO", font=font(20), fill=DIM)

    elif slug == "gpt2-forward":
        motif_layers(d, (M, 104, 136, 400), accent, 12, (322, 132, 226, 310))
        head(d, accent, "GPT-2 small / 12 layers / 124M",
             "GPT-2", "一条 768 维向量，被改写 12 次",
             (W - M, 186), 132, (W - M, 356), 430, align="right")
        d.text((W - M, 466), "残差流 / Hook / 干预", font=font(21), fill=mix(DIM, accent, 0.6), anchor="ra")

    elif slug == "ohmygame":
        head(d, accent, "Agent / Game Studio / Playwright",
             "OhMyGame", "AI 写游戏不难，难的是让它自己发现游戏跑不起来",
             (M, 138), 86, (M, 282), 470)
        motif_game(d, (620, 104, 508, 380), accent, "canary: 控制台 / 截图 / 重跑")

    elif slug == "nnsight":
        head(d, accent, "Harvard NLP / NDIF",
             "NNsight", "干预写进前向传播，同一段代码跑 405B",
             (M, 138), 112, (M, 320), 460)
        motif_code(d, (600, 96, 528, 206), accent,
                   [("with model.trace():", "hot"),
                    ("    x = model.layers[6].output", "code"),
                    ("    x.save()", "dim"),
                    ("    x[:] = x + v", "hot"),
                    ("    logits = model.lm_head(x)", "code")],
                   (664, 356, 464, 152), "405B", "一次 forward，介入在执行时注入")

    elif slug == "blender-kiln":
        head(d, accent, "Claude Code / Blender MCP / MIT",
             "Blender\nKiln", "干活的不是 3D 引擎，是一套能被量出来的流程",
             (M, 128), 88, (M, 364), 500)
        motif_sheet(d, (686, 104, 442, 408), accent, "每轮换一个人来读")

    elif slug == "yogurt":
        head(d, accent, "Frigade / MIT / Electron 44 / whisper.cpp",
             "Yogurt", "本地优先不是一句承诺，是一组能被算出来的预算",
             (M, 138), 112, (M, 316), 470)
        motif_audio(d, (620, 112, 512, 372), accent, "两路音频 · 一个权限口 · 一份纪要")
        d.text((M, 434), "0.5 RTF · 15 tok/s · 0o600", font=font(21), fill=mix(DIM, accent, 0.7))

    elif slug == "wsr":
        head(d, accent, "Poindexter Labs / alphaXiv / Apache-2.0",
             "WSR", "权重确实多给了 15 个点，也让它更敢说「变了」",
             (M, 138), 124, (M, 330), 450)
        motif_matrix(d, (600, 104, 540, 396), accent, "只读张量 · 0 次前向 · 猜 up / down / same")
        d.text((M, 470), "0.730 vs 0.578 · 53–88% 误报", font=font(21), fill=mix(DIM, accent, 0.7))

    elif slug == "airgorah":
        head(d, accent, "Rust / GTK4 / Polkit / Linux",
             "Airgorah", "把 root 赶出 GUI 之后，每个参数都得重新验一遍",
             (M, 138), 108, (M, 316), 470)
        motif_boundary(d, (600, 122, 540, 340), accent, "16 个请求 · 1 个客户端 · 0600")
        d.text((M, 452), "id 1000 → socket → root", font=font(21), fill=mix(DIM, accent, 0.7))

    elif slug == "haru":
        head(d, accent, "higurashi-ai / Apache 2.0 / 40M hours",
             "Haru-4B", "全双工的瓶颈不在架构，在没人录得下双声道对话",
             (M, 146), 106, (M, 322), 480)
        motif_duplex(d, (600, 112, 540, 356), accent, "13M 小时分离对话 · 7.5 Hz · 65 ms")

    elif slug == "desigma":
        head(d, accent, "Rust / MIT OR Apache-2.0 / 1,600+ tests",
             "Desigma", "撤销不是功能，是编辑原语自己算出来的",
             (M, 146), 106, (M, 322), 480)
        motif_inverse(d, (600, 112, 540, 356), accent, "Command::apply → 逆命令 · 同一个 undo 栈")

    elif slug == "mnn":
        head(d, accent, "Alibaba / Apache 2.0 / MNN 3.6.2",
             "MNN", "端侧推理引擎真正的产品，是一张敢给自己标 C 的支持矩阵",
             (M, 150), 124, (M, 322), 470)
        motif_grades(d, (610, 118, 500, 336), accent,
                     "18 行（CPU 8 · GPU 4 · NPU 6）× 4 种精度，C 格是空的")
        d.text((M, 452), "Prefill 3542.91 tok/s · Decode 111.89 → 233.98",
               font=font(20), fill=mix(DIM, accent, 0.65))
        d.text((M, 492), "iPhone 18 Pro 上 173 MB / 350 tok/s", font=font(20), fill=DIM)

    elif slug == "helixharness":
        head(d, accent, "didi / Apache 2.0 / 9 commands / 1.0.0",
             "Helix\nHarness", "两份契约：读什么由 index 决定，改得对不对由冻结版本决定",
             (M, 128), 88, (M, 358), 470)
        motif_helix(d, (600, 120, 540, 320), accent, "账本默认关闭 · 平台截图是合成数据")

    elif slug == "colibri":
        head(d, accent, "Apache 2.0 / 13 engines / GLM-5.2",
             "colibri", "权重住在哪一层，只准改速度，不准改模型",
             (M, 146), 112, (M, 322), 430)
        motif_tiers(d, (600, 138, 540, 386), accent, "同一份 int4 权重 · 184×")

    elif slug == "geo":
        head(d, accent, "arXiv 2311.09735 / KDD 2024",
             "GEO", "", (M, 138), 118, (M, 300), 470)
        d.text((M, 302), "论文里最有效的三种写法，", font=font(28), fill=BODY)
        d.text((M, 342), "官方提示词都允许编造", font=font(28), fill=BODY)
        motif_evidence(d, (640, 100, 488, 300), accent, "插入的不是信息，是可被指认的碎片")
        d.text((M, 456), "一条答案的份额总和是 1.0，均分 20", font=font(20), fill=DIM)
        d.text((W - M, 456), "引用语句 +40.9%", font=font(20),
               fill=mix(DIM, accent, 0.7), anchor="ra")
        band_shares(d, M, W - M, 486, accent)

    elif slug == "aerial":
        head(d, accent, "Kotlin + Compose / MIT / 12k stars",
             "Aerial", "换桌面不是画界面，是在别人的固件里抢前台",
             (M, 146), 116, (M, 322), 440)
        motif_launcher(d, (586, 150, 548, 344), accent, "主页键 · 前台窗口 · 守护")
        d.text((M, 452), "89 行机型记录：56 能用 / 23 有限制 / 10 接管不了",
               font=font(20), fill=mix(DIM, accent, 0.65))
        d.text((M, 492), "无障碍服务 · 通知监听 · 同步适配器", font=font(20), fill=DIM)

    elif slug == "droiddeck":
        head(d, accent, "GPL-3.0 / Kotlin + Compose / 20k stars",
             "DroidDeck", "翻译层会过时，宿主层不会",
             (M, 152), 84, (M, 330), 430)
        motif_seam(d, (620, 176, 508, 294), accent, "1.7 µs 一次事件往返 · 9.5 W → 7.1 W")
        d.text((M, 424), "18 个 PRoot 补丁 · ntsync · 双屏 · 眼镜", font=font(21), fill=DIM)
        d.text((M, 462), "195,108 次下载 · 92 MB APK", font=font(21),
               fill=mix(DIM, accent, 0.65))

    elif slug == "voicestudio":
        head(d, accent, "AGPL-3.0 / Electron + FastAPI / 0.5.8",
             "VoiceStudio", "把语音搬回本地，账单换成了许可证",
             (M, 146), 80, (M, 316), 470)
        motif_registry(d, (636, 158, 516, 340), accent,
                       "73 条模型记录 · 0 条可商用")
        d.text((M, 424), "646 种语言 · 581,489 小时 · 20 个引擎", font=font(21), fill=DIM)
        d.text((M, 462), "0.5.8 / 2026-11-17", font=font(20), fill=mix(DIM, accent, 0.6))
    elif slug == "everything":
        head(d, accent, "HeyPuter / 50 apps / 0 frameworks",
             "Everything", "50 款软件压成 50 个目录，账号是唯一的公共设施",
             (M, 152), 88, (M, 306), 430)
        motif_wall(d, (600, 132, 520, 356), accent, "51 次部署 · 15 个 AGPL")
        d.text((M, 424), "1,327 MB · 37,424 个文件", font=font(21), fill=DIM)
        d.text((M, 462), "Excel 到 AutoCAD：每个应用自己写内核", font=font(21),
               fill=mix(DIM, accent, 0.65))

    elif slug == "gpu-unlock":
        head(d, accent, "Linux module / GPL-2.0 / RTX 20 · 30 · 40",
             "gpu-unlock", "算力不是被驱动锁住的，是八个 4 位字段写死的",
             (M, 168), 88, (M, 302), 500, thesis_size=28)
        motif_nibbles(d, (636, 104, 500, 426), accent,
                      "写它们需要 SEC2 的 heavy-secure 上下文，\n只存在于引导的那一瞬间")
        d.text((M, 410), "SS0 0x00000001 → 0x88888888", font=font(21), fill=mix(DIM, accent, 0.85))
        d.text((M, 446), "输出逐位相同，只有速度变了", font=font(21), fill=DIM)

    elif slug == "diagram-design":
        head(d, accent, "Agent Skill / MIT / 67,720 stars",
             "Diagram\nDesign", "审美不是提示词，是会失败的检查",
             (M, 122), 92, (M, 336), 470, thesis_size=27)
        motif_gates(d, (600, 128, 546, 336), accent, "9 个节点 · 2 个 accent · 4.71:1")
        d.text((M, 438), "481 KB 参考 · 一次只读 1 KB", font=font(21), fill=DIM)
        d.text((M, 472), "6 条连线规则 · 38 个 test-verify", font=font(21),
               fill=mix(DIM, accent, 0.65))

    elif slug == "octop":
        head(d, accent, "TencentCloud / MIT / 12.1k stars",
             "Octop", "单进程是它的地基，也是它的天花板",
             (M, 132), 112, (M, 320), 470, thesis_size=28)
        motif_funnel(d, (620, 116, 508, 356), accent, "octop run --port 8088")
        d.text((M, 424), "1.0.3b6 · Python 3.12 + React 18", font=font(21), fill=DIM)
        d.text((M, 462), "Web · IM · Cron · CLI 共用一个 HarnessProcessor", font=font(20),
               fill=mix(DIM, accent, 0.65))

    elif slug == "vllm":
        motif_pages(d, (M, 128, 470, 300), accent,
                    "三条序列 · 一个块池 · 块表负责顺序")
        head(d, accent, "Berkeley Sky Lab / Apache 2.0 / 97k stars",
             "vLLM", "每一次重写，改的都是同一本显存的账",
             (W - M, 158), 116, (W - M, 330), 470, align="right", thesis_size=26)
        d.text((W - M, 470), "60–80%  →  不足 4%", font=font(26),
               fill=mix(DIM, accent, 0.85), anchor="ra")
        d.text((W - M, 508), "1 + 1 + 4 = 6 个进程", font=font(20), fill=DIM, anchor="ra")

    elif slug == "intent-system":
        motif_slot(d, (640, 118, 500, 350), accent, "两侧之间只有一道缝")
        head(d, accent, "J-Tech Japan / Apache-2.0 / C# / 0.32.1",
             "Intent\nSystem", "它不信任 AI，所以把流程搬出 AI 的上下文",
             (M, 138), 88, (M, 366), 566, thesis_size=26)
        d.text((M, 440), "113 star · 1 fork · 6 open issue", font=font(21), fill=DIM)
        d.text((M, 478), "确定性 CLI + GitHub label 状态机 + 四类 facets", font=font(20),
               fill=mix(DIM, accent, 0.7))

    elif slug == "mainline":
        head(d, accent, "mainline-org / Go / 205 stars",
             "Mainline", "代码记 what，它把 why 也塞进 Git",
             (M, 152), 104, (M, 306), 476, thesis_size=28)
        motif_refs(d, (630, 112, 500, 356), accent, "两条历史，一个交点")
        d.text((M, 424), "v0.5.1 · Apache-2.0 / 商业分层", font=font(21), fill=DIM)
        d.text((M, 462), "refs 存事件流 · notes 把意图钉在 commit 上", font=font(19),
               fill=mix(DIM, accent, 0.65))

    elif slug == "rust-anything":
        head(d, accent, "erkamyaman / MIT / 1.3k stars",
             "rust-\nanything", "换语言不是翻译，是一场可以判负的比较",
             (M, 122), 78, (M, 350), 512, thesis_size=26)
        motif_verdict(d, (640, 112, 500, 356), accent, "0.23x · 建议不要发")
        d.text((M, 428), "29 个函数 · 7,925 个案例 · 0 不一致", font=font(21), fill=DIM)
        d.text((M, 466), "…然后把它们全部判成「更慢」", font=font(19),
               fill=mix(DIM, accent, 0.65))

    elif slug == "sft-rlhf":
        head(d, accent, "后训练 / 两个阶段 / 一个共同动作",
             "SFT 与\nRLHF", "教接口，选口味，然后把分布收窄",
             (M, 128), 76, (M, 330), 520, thesis_size=26)
        motif_narrow(d, (640, 112, 500, 356), accent, "1,000 条示范 · 一个标量奖励")
        d.text((M, 424), "SFT 学格式，RLHF 学偏好", font=font(21), fill=DIM)
        d.text((M, 462), "泛化变好，代价是多样性", font=font(19), fill=mix(DIM, accent, 0.65))

    elif slug == "mnn-pocket":
        head(d, accent, "MNN Team / Apache 2.0 / 300M",
             "MNN-\nPocket", "先定 300 MB 和 200 tok/s，再挑模型",
             (M, 126), 78, (M, 330), 512, thesis_size=26)
        motif_budget(d, (640, 112, 500, 356), accent, "173 MB · 32K · 466 tok/s")
        d.text((M, 424), "词表 151K → 64K，等于还回 77M 参数", font=font(21), fill=DIM)
        d.text((M, 462), "INT4 掉了 0.41 分，KV cache 涨回 448 MiB", font=font(19),
               fill=mix(DIM, accent, 0.65))

    elif slug == "jina-ocr":
        head(d, accent, "Jina AI / CC BY-NC 4.0 / 570M active",
             "Jina-\nOCR", "赢在少写，不在写快",
             (M, 126), 84, (M, 352), 486, thesis_size=26)
        motif_compress(d, (630, 112, 500, 356), accent, "2.57 页/秒 · 一页 1,085 token")
        d.text((M, 424), "4,096 像素压成 1 个视觉 token", font=font(20), fill=DIM)
        d.text((M, 462), "3,568 tok/page 的方案，吞吐只有 1.05 页/秒", font=font(17),
               fill=mix(DIM, accent, 0.7))

    elif slug == "video-shotcraft":
        head(d, accent, "Vincentwei1021 / Apache-2.0 / 21k stars",
             "video-\nshotcraft", "视频不是生成的，是点名字点出来的",
             (M, 118), 70, (M, 330), 496, thesis_size=25)
        motif_cards(d, (640, 112, 500, 356), accent, "逐帧渲染 · 帧级可编辑")
        d.text((M, 424), "124 张配方卡，150 个镜头，0 个生成模型", font=font(19), fill=DIM)
        d.text((M, 462), "预设与预览帧级一致，改一个镜头不用重做整片", font=font(17),
               fill=mix(DIM, accent, 0.7))

    elif slug == "omni-quantized":
        head(d, accent, "ChatR Labs / Qwen Research License",
             "Omni-\nQuantized", "省的是显存，不是时间",
             (M, 138), 76, (M, 330), 500, thesis_size=26)
        motif_quant_tiers(d, (640, 112, 500, 356), accent, "12 个构建 · 2 套布局 · 1 条许可")
        d.text((M, 424), "14.23 GB → 3.67 GB，耗时几乎没变", font=font(20), fill=DIM)
        d.text((M, 462), "最小的那个，只在 Diffusers 那条路上成立", font=font(17),
               fill=mix(DIM, accent, 0.7))

    elif slug == "omni-lora":
        head(d, accent, "ChatR Labs / rank 128 / BF16",
             "Omni\nLoRA", "一个 671 MB 的修正，要背两个任务",
             (M, 132), 76, (M, 330), 500, thesis_size=26)
        motif_lora(d, (640, 112, 500, 356), accent, "占底座 4.7% · 224 个模块 · 448 个张量")
        d.text((M, 424), "32k 检查点：遵循 +2.3，通用 −4.0", font=font(19), fill=DIM)
        d.text((M, 462), "容量是共享的，两个任务在同一个秩里抢位置", font=font(17),
               fill=mix(DIM, accent, 0.7))

    elif slug == "hypit":
        head(d, accent, "hypit-ai / TypeScript / 30.5k stars",
             "Hypit", "你编辑的是词，秒是编译出来的",
             (M, 132), 100, (M, 320), 486, thesis_size=27)
        motif_words(d, (636, 108, 508, 404), accent, "1 个模板 · N 份 .svrun · 0 个手写秒数")
        d.text((M, 424), "SVML → Compiler → Plan → Build → Result", font=font(20), fill=DIM)
        d.text((M, 462), "20 秒片子 $1.15 · 64 个 Chromium 并发渲染", font=font(20),
               fill=mix(DIM, accent, 0.65))
    elif slug == "se-handbook":
        head(d, accent, "James C. Davis / Purdue / 11 chapters",
             "SE\nHandbook", "钉死了哪些自由，凭什么证据敢交付",
             (M, 146), 84, (M, 372), 470, thesis_size=25)
        motif_nested(d, (648, 112, 496, 372), accent, "需求 → 规格 → 架构 → 设计：每步再收窄一次")
        d.text((M, 470), "Model → Property → Observation → Evidence → Judgment",
               font=font(18), fill=DIM)
        d.text((M, 504), "受控变化：可改 · 可复制 · 可迁移 · 可更新", font=font(19),
               fill=mix(DIM, accent, 0.65))

    elif slug == "maitian":
        head(d, accent, "CzzzzzzJ / MIT / macOS / 1.1k stars",
             "Maitian", "易碎的那一层，住在会自己更新的容器里",
             (M, 142), 92, (M, 352), 470, thesis_size=24)
        motif_handoff(d, (648, 122, 496, 376), accent, "平台改版：只更新插件，不更新麦田")
        d.text((M, 442), "skill 写文案 · 插件填表单 · hub 记账", font=font(19), fill=DIM)
        d.text((M, 478), "国内四家的最后一次点击，永远留给人", font=font(19),
               fill=mix(DIM, accent, 0.6))

    elif slug == "cognitive-game":
        head(d, accent, "认知博弈 / I-POMDP / 可辨识性",
             "认知\n博弈", "两个主体互相预测时，未来由谁决定",
             (M, 126), 96, (M, 372), 470, thesis_size=25)
        motif_phaselag(d, (620, 112, 508, 396), accent, "行动 → 观测 → 更新 → 行动")
        d.text((M, 468), "信念表示 · 递归层级 · 可辨识性", font=font(20), fill=DIM)
        d.text((M, 504), "从概率云到双主体闭环", font=font(20),
               fill=mix(DIM, accent, 0.7))

    elif slug == "two-agent":
        head(d, accent, "POMDP · I-POMDP · ToM · 主动推断",
             "双主体\n概率云", "射手瞄准的不是位置，是对手看见你之后的那团分布",
             (M, 138), 76, (M, 352), 470, thesis_size=25)
        motif_twocloud(d, (594, 146, 532, 336), accent, "两层信念 · 同一发子弹")
        d.text((M, 470), "4 成继续 · 3 成左躲 · 2 成右闪 · 1 成不动", font=font(20), fill=DIM)
        d.text((M, 506), "分布动了，不等于行为动了", font=font(20),
               fill=mix(DIM, accent, 0.65))

    domain(d)
    path = os.path.join(out_dir, A["file"])
    img.save(path, "JPEG", quality=92, optimize=True, subsampling=0)
    return path


CARDS = {
    "saelens": dict(file="saelens-sparse-autoencoder-instrument.jpg", color=(198, 112, 228),
                    glow=(880, 240), glow_r=380, strength=0.30),
    "tokeneconomizer": dict(file="tokeneconomizer-experience-driven-cost-control.jpg",
                            color=(232, 164, 62), glow=(740, 420), glow_r=470, strength=0.24),
    "transformer-explainer": dict(file="transformer-explainer.jpg", color=(84, 158, 238),
                                  glow=(300, 300), glow_r=420, strength=0.28),
    "boubou": dict(file="boubou-local-voice-runtime.jpg", color=(72, 198, 158),
                   glow=(930, 262), glow_r=420, strength=0.30),
    "hy-mt2": dict(file="hy-mt2-family-centric-post-training.jpg", color=(140, 128, 240),
                   glow=(800, 300), glow_r=430, strength=0.30),
    "gpt2-forward": dict(file="gpt2-forward-pass-intervention.jpg", color=(72, 198, 216),
                         glow=(380, 300), glow_r=400, strength=0.26),
    "ohmygame": dict(file="ohmygame-agent-game-studio.jpg", color=(178, 208, 78),
                     glow=(870, 300), glow_r=420, strength=0.24),
    "nnsight": dict(file="nnsight-deferred-intervention.jpg", color=(232, 112, 104),
                    glow=(860, 300), glow_r=420, strength=0.26),
    "blender-kiln": dict(file="blender-kiln-3d-asset-pipeline.jpg", color=(204, 74, 72),
                         glow=(900, 300), glow_r=430, strength=0.26),
    "yogurt": dict(file="yogurt-local-meeting-notes.jpg", color=(212, 170, 92),
                   glow=(886, 300), glow_r=440, strength=0.26),
    "wsr": dict(file="wsr-weight-space-reading.jpg", color=(216, 138, 168),
                glow=(880, 300), glow_r=440, strength=0.26),
    "airgorah": dict(file="airgorah-privilege-boundary.jpg", color=(64, 152, 172),
                     glow=(880, 300), glow_r=440, strength=0.26),
    "haru": dict(file="haru-4b-full-duplex.jpg", color=(94, 122, 236),
                 glow=(900, 300), glow_r=440, strength=0.28),
    "desigma": dict(file="desigma-command-inverse.jpg", color=(200, 106, 62),
                    glow=(900, 300), glow_r=440, strength=0.28),
    "mnn": dict(file="mnn-backend-precision-matrix.jpg", color=(176, 138, 72),
                glow=(900, 300), glow_r=440, strength=0.30),
    "helixharness": dict(file="helixharness-harness-contracts.jpg", color=(36, 158, 108),
                         glow=(880, 300), glow_r=440, strength=0.28),
    "colibri": dict(file="colibri-tiered-expert-placement.jpg", color=(146, 96, 196),
                    glow=(880, 300), glow_r=440, strength=0.30),
    "geo": dict(file="geo-generative-engine-optimization.jpg", color=(232, 190, 62),
                glow=(900, 280), glow_r=450, strength=0.28),
    "aerial": dict(file="aerial-tv-launcher-foreground-takeover.jpg", color=(96, 186, 226),
                   glow=(880, 300), glow_r=440, strength=0.28),
    "droiddeck": dict(file="droiddeck-android-handheld-host.jpg", color=(238, 132, 58),
                      glow=(770, 300), glow_r=450, strength=0.28),
    "voicestudio": dict(file="voicestudio-local-voice-workstation.jpg", color=(168, 78, 116),
                        glow=(860, 300), glow_r=430, strength=0.28),    "everything": dict(file="everything-monorepo-fifty-apps.jpg", color=(206, 86, 178),
                       glow=(860, 260), glow_r=440, strength=0.30),
    "gpu-unlock": dict(file="gpu-unlock-geforce-tensor-half-rate.jpg", color=(108, 178, 84),
                       glow=(880, 280), glow_r=450, strength=0.28),
    "diagram-design": dict(file="diagram-design-agent-skill-lint.jpg", color=(191, 69, 32),
                           glow=(880, 250), glow_r=450, strength=0.30),
    "octop": dict(file="octop-single-process-agent-platform.jpg", color=(40, 176, 168),
                  glow=(880, 260), glow_r=460, strength=0.28),
    "vllm": dict(file="vllm-kv-cache-ledger.jpg", color=(104, 116, 236),
                 glow=(940, 240), glow_r=450, strength=0.30),
    "intent-system": dict(file="intent-system-intent-driven-development.jpg",
                          color=(108, 164, 132), glow=(880, 292), glow_r=470, strength=0.30),
    "mainline": dict(file="mainline-git-native-intent-memory.jpg",
                     color=(78, 116, 178), glow=(890, 286), glow_r=460, strength=0.30),
    "sft-rlhf": dict(file="sft-rlhf-narrowing.jpg",
                      color=(152, 52, 74), glow=(880, 286), glow_r=470, strength=0.30),
    "rust-anything": dict(file="rust-anything-behavioral-port.jpg",
                          color=(198, 96, 38), glow=(880, 280), glow_r=470, strength=0.30),
    "mnn-pocket": dict(file="mnn-pocket-on-device-budget.jpg",
                       color=(22, 118, 108), glow=(880, 288), glow_r=470, strength=0.30),
    "video-shotcraft": dict(file="video-shotcraft-shot-names.jpg",
                            color=(198, 140, 56), glow=(884, 288), glow_r=470, strength=0.30),
    "omni-lora": dict(file="omni-lora-shared-capacity.jpg",
                        color=(18, 96, 120), glow=(884, 288), glow_r=470, strength=0.30),
    "omni-quantized": dict(file="omni-quantized-runtime-contracts.jpg",
                             color=(122, 62, 132), glow=(884, 288), glow_r=470, strength=0.30),
    "jina-ocr": dict(file="jina-ocr-output-length.jpg",
                     color=(72, 88, 160), glow=(886, 290), glow_r=470, strength=0.30),
    "hypit": dict(file="hypit-video-compiler-timeline.jpg",
                  color=(206, 70, 120), glow=(884, 288), glow_r=470, strength=0.30),
    "se-handbook": dict(file="software-engineering-handbook-judgment.jpg",
                        color=(128, 142, 60), glow=(890, 292), glow_r=470, strength=0.30),
    "maitian": dict(file="maitian-multi-platform-publishing.jpg",
                    color=(132, 170, 198), glow=(890, 292), glow_r=470, strength=0.30),
    "two-agent": dict(file="two-agent-probabilistic-cloud.jpg",
                      color=(96, 122, 196), glow=(320, 268), glow_r=470, strength=0.30),
    "cognitive-game": dict(file="cognitive-game-mutual-prediction.jpg",
                           color=(208, 92, 132), glow=(884, 288), glow_r=470, strength=0.30),
}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "_covers")
    os.makedirs(out, exist_ok=True)
    for s in CARDS:
        print("wrote", build(s, out))




