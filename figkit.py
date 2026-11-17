# -*- coding: utf-8 -*-
"""figkit — tiny Pillow toolkit for the diagrams used on fengjutian.github.io.

No matplotlib in the bundled runtime; this file is the whole dependency.

Usage:
    import sys; sys.path.insert(0, r"<skill-dir>/scripts")
    from figkit import *

    img, d = new_canvas(1400, 760)
    box(d, 60, 60, 300, 120, "ASR", "语音 → 文字", fill=BLUE_BG, border=BLUE, tcolor=BLUE)
    arrow(d, (360, 120), (470, 120))
    img.save(os.path.join(OUT, "fig-01.png"))

Run `python figkit.py --demo <dir>` to render a smoke-test diagram.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
INK = (26, 32, 44)
MUTED = (110, 122, 140)
LINE = (203, 213, 225)
BG = (255, 255, 255)
GRAY_BG = (245, 247, 250)

BLUE = (37, 99, 178)
BLUE_BG = (233, 242, 252)
GREEN = (39, 122, 84)
GREEN_BG = (231, 245, 238)
ORANGE = (182, 80, 30)
ORANGE_BG = (253, 240, 232)
PURPLE = (99, 66, 180)
PURPLE_BG = (242, 238, 252)

_FONT_CANDIDATES = [
    (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc"),
    (r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simhei.ttf"),
    ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/PingFang.ttc"),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
     "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
]


def _font_paths():
    for regular, bold in _FONT_CANDIDATES:
        if os.path.exists(regular):
            return regular, bold if os.path.exists(bold) else regular
    raise RuntimeError("no CJK font found; add a path to _FONT_CANDIDATES")


def font(size, bold=False):
    regular, heavy = _font_paths()
    return ImageFont.truetype(heavy if bold else regular, size)


def new_canvas(w, h):
    img = Image.new("RGB", (w, h), BG)
    return img, ImageDraw.Draw(img)


def box(d, x, y, w, h, title, sub=None, fill=GRAY_BG, border=LINE,
        tcolor=INK, scolor=MUTED, tsize=28, ssize=20, radius=14, width=2):
    """Rounded card, optional second line. Text is centred and wrapped by newlines."""
    d.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=border, width=width)
    cx, cy = x + w / 2, y + h / 2
    if sub:
        d.multiline_text((cx, cy - h * 0.15), title, font=font(tsize, True), fill=tcolor,
                         anchor="mm", align="center", spacing=8)
        d.multiline_text((cx, cy + h * 0.19), sub, font=font(ssize), fill=scolor,
                         anchor="mm", align="center", spacing=6)
    else:
        d.multiline_text((cx, cy), title, font=font(tsize, True), fill=tcolor,
                         anchor="mm", align="center", spacing=6)


def arrow(d, p1, p2, color=MUTED, width=3, head=13):
    x1, y1 = p1
    x2, y2 = p2
    ang = math.atan2(y2 - y1, x2 - x1)
    d.line((x1, y1, x2, y2), fill=color, width=width)
    left = (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42))
    right = (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))
    d.polygon([(x2, y2), left, right], fill=color)


def polyline(d, pts, color=MUTED, width=3, head=13):
    """Elbow connector; draws straight segments then an arrow on the last one."""
    for a, b in zip(pts[:-1], pts[1:-1]):
        d.line((a[0], a[1], b[0], b[1]), fill=color, width=width)
    arrow(d, pts[-2], pts[-1], color=color, width=width, head=head)


def label(d, x, y, text, size=20, color=MUTED, bold=False, anchor="lm"):
    d.text((x, y), text, font=font(size, bold), fill=color, anchor=anchor)


def caption(d, text, y, w, size=20):
    label(d, w / 2, y, text, size, MUTED, False, "mm")


def thumbnail(dst, title, subtitle, meta, chips=(), width=1200, height=630,
              accent=(72, 187, 150), site="fengjutian.github.io", big=118):
    """Dark x:1.91 card. `title` is the project name, rendered at `big` px."""
    img = Image.new("RGB", (width, height), (12, 18, 30))
    d = ImageDraw.Draw(img)
    top, bottom = (20, 32, 54), (11, 15, 26)
    for y in range(height):
        t = y / (height - 1)
        d.line((0, y, width, y), fill=tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)))

    d.rounded_rectangle((70, 96, 78, height - 96), radius=4, fill=accent)
    d.text((120, 108), meta, font=font(25), fill=(126, 156, 190))
    d.text((116, 140), title, font=font(big, True), fill=(255, 255, 255))
    d.text((122, 328), subtitle, font=font(32), fill=(200, 216, 238))

    x = 122
    for chip in chips:
        tw = d.textlength(chip, font=font(21))
        d.rounded_rectangle((x, 442, x + tw + 34, 492), radius=25,
                            outline=(66, 96, 130), width=2, fill=(18, 28, 44))
        d.text((x + 17, 454), chip, font=font(21), fill=(168, 198, 230))
        x += tw + 50

    d.text((122, 540), site, font=font(22), fill=(92, 114, 142))
    img.save(dst, quality=92)
    return img


def _demo(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    img, d = new_canvas(1400, 780)
    label(d, 60, 50, "figkit demo", 26, INK, True)
    box(d, 60, 100, 320, 130, "ASR", "语音 → 文字", fill=BLUE_BG, border=BLUE, tcolor=BLUE)
    arrow(d, (390, 165), (500, 165))
    box(d, 510, 100, 320, 130, "LLM", "文字 → 文字")
    arrow(d, (840, 165), (950, 165))
    box(d, 960, 100, 320, 130, "TTS", "文字 → 语音", fill=GREEN_BG, border=GREEN, tcolor=GREEN)

    d.rounded_rectangle((60, 300, 1340, 420), radius=16, fill=PURPLE_BG, outline=PURPLE, width=2)
    label(d, 700, 360, "运行时层：设备 · 缓冲 · 检测 · 会话", 26, PURPLE, True, "mm")
    polyline(d, [(700, 230), (700, 300)], color=PURPLE)
    caption(d, "一个箭头、一个卡片、一行说明，够表达一件事", 470, 1400)

    d.line((150, 560, 1250, 560), fill=LINE, width=2)
    label(d, 60, 560, "用户", 22, INK, True, "lm")
    label(d, 60, 660, "系统", 22, INK, True, "lm")
    d.rounded_rectangle((170, 525, 520, 595), radius=12, fill=GREEN_BG, outline=GREEN, width=2)
    label(d, 345, 560, "说话", 21, GREEN, True, "mm")
    d.rounded_rectangle((170, 625, 520, 695), radius=12, fill=(232, 236, 242), outline=LINE, width=2)
    label(d, 345, 660, "采集 + VAD", 21, INK, False, "mm")
    img.save(os.path.join(out_dir, "figkit-demo.png"))

    thumbnail(os.path.join(out_dir, "figkit-demo.jpg"), "Demo", "一张封面图的默认排版",
              "Local Voice AI Runtime", ["run", "serve", "barge-in"])
    print("wrote", out_dir)


if __name__ == "__main__":
    import sys
    target = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "_figkit_demo")
    _demo(target)
