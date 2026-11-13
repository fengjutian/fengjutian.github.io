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


# ------------------------------------------------------------------ cards
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
}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "_covers")
    os.makedirs(out, exist_ok=True)
    for s in CARDS:
        print("wrote", build(s, out))
