# -*- coding: utf-8 -*-
"""Lead illustration for the WeChat version: one guess, two futures.

Portrait 1000x1250 so that at the 677px column it still reads on a phone.
"""
import math
import os
import sys

sys.path.insert(0, r"D:\github\fengjutian.github.io\.agents\skills\blog-post-publishing\scripts")

from figkit import BG, BLUE, BLUE_BG, GRAY_BG, GREEN, INK, LINE, MUTED, ORANGE, ORANGE_BG
from figkit import arrow, font, label, new_canvas
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
RED = (176, 58, 58)
RED_BG = (252, 236, 236)
W, H = 1000, 1250


def alpha(img, pts, color, a):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon(pts, fill=color + (a,))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def dot(d, x, y, r, color, fill=None, letter=None):
    d.ellipse((x - r, y - r, x + r, y + r), fill=fill or color, outline=color, width=2)
    if letter:
        d.text((x, y + 1), letter, font=font(18, True), fill=color, anchor="mm")


def chip(d, x, y, text, color, bg):
    w = d.textlength(text, font=font(21, True)) + 34
    d.rounded_rectangle((x, y, x + w, y + 46), radius=23, fill=bg, outline=color, width=2)
    d.text((x + w / 2, y + 23), text, font=font(21, True), fill=color, anchor="mm")


def dashed(d, p0, p1, color, width=3, dash=16, gap=11):
    x0, y0 = p0
    x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    t = 0.0
    while t < length:
        a = (x0 + ux * t, y0 + uy * t)
        b = (x0 + ux * min(t + dash, length), y0 + uy * min(t + dash, length))
        d.line((a[0], a[1], b[0], b[1]), fill=color, width=width)
        t += dash + gap


def cross(d, x, y, s, color, width=4):
    d.line((x - s, y - s, x + s, y + s), fill=color, width=width)
    d.line((x - s, y + s, x + s, y - s), fill=color, width=width)


def check(d, x, y, s, color, width=5):
    d.line((x - s, y + s * 0.1, x - s * 0.2, y + s * 0.8), fill=color, width=width)
    d.line((x - s * 0.2, y + s * 0.8, x + s, y - s * 0.7), fill=color, width=width)


def main():
    img, d = new_canvas(W, H)

    label(d, 46, 54, "同一句判断，用与不用", 30, INK, True, "lm")
    label(d, 46, 96, "得到的是两个未来", 24, MUTED, False, "lm")

    # -------------------------------------------------- panel 1: guess only
    chip(d, 46, 140, "① 只是猜，不动手", MUTED, GRAY_BG)

    ax, ay = 150, 450
    bx, by = 430, 350
    dot(d, ax, ay, 17, BLUE, BLUE_BG, "A")
    dot(d, bx, by, 17, ORANGE, ORANGE_BG, "B")

    d.line((ax + 22, ay - 8, ax + 86, ay - 8), fill=LINE, width=3)
    label(d, ax + 98, ay - 8, "枪口没动", 20, MUTED, False, "lm")

    d.line((bx + 20, by, 846, by), fill=LINE, width=5)
    dashed(d, (bx + 20, by), (846, by), MUTED, 3)
    arrow(d, (820, by), (852, by), MUTED, 3, 13)
    check(d, 890, by, 16, GREEN, 5)
    label(d, 890, by + 46, "猜中了", 22, GREEN, True, "mm")

    label(d, 470, by - 52, "他照原路走，和猜的一样", 21, MUTED, False, "lm")
    label(d, 470, by + 34, "预测和实际重合", 20, MUTED, False, "lm")

    d.line((46, 600, 954, 600), fill=(233, 236, 241), width=2)

    # -------------------------------------------------- panel 2: acted upon
    chip(d, 46, 650, "② 猜了，还用它瞄准", RED, RED_BG)

    ax2, ay2 = 150, 1090
    bx2, by2 = 430, 990
    dot(d, ax2, ay2, 17, BLUE, BLUE_BG, "A")
    dot(d, bx2, by2, 17, ORANGE, ORANGE_BG, "B")

    cone = [(ax2, ay2), (846, 920), (872, 1040)]
    img = alpha(img, cone, BLUE, 16)
    d = ImageDraw.Draw(img)
    d.line((ax2, ay2, 856, 980), fill=BLUE, width=2)
    label(d, ax2 + 26, ay2 + 40, "枪口移向右", 20, BLUE, True, "lm")

    dashed(d, (bx2 + 20, by2), (846, by2), MUTED, 3)
    arrow(d, (820, by2), (852, by2), MUTED, 3, 13)
    cross(d, 890, by2, 15, MUTED, 4)
    label(d, 890, by2 + 44, "没去这儿", 22, MUTED, True, "mm")

    bend_start, bend_end, ctrl = (660, by2), (872, 800), (760, 880)
    d.line((bx2 + 20, by2, bend_start[0], bend_start[1]), fill=ORANGE, width=4)
    px, py = bend_start
    for i in range(1, 41):
        t = i / 40
        x = (1 - t) ** 2 * bend_start[0] + 2 * (1 - t) * t * ctrl[0] + t * t * bend_end[0]
        y = (1 - t) ** 2 * bend_start[1] + 2 * (1 - t) * t * ctrl[1] + t * t * bend_end[1]
        d.line((px, py, x, y), fill=ORANGE, width=4)
        px, py = x, y
    arrow(d, (px, py), (884, 782), ORANGE, 4, 15)

    label(d, 470, by2 - 54, "看到枪口右移，他改了方向", 21, MUTED, False, "lm")
    label(d, 884, 748, "他改道了", 22, ORANGE, True, "mm")

    label(d, 46, 1196, "判断本身没变，变的是它有没有被拿去用。", 24, INK, False, "lm")

    out = os.path.join(OUT, "illus-guess-becomes-action.png")
    img.save(out)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
