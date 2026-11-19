# -*- coding: utf-8 -*-
"""WeChat 首图: 2.35:1 (1410x600). Reuses the cover card's helpers."""
import os
import sys

sys.path.insert(0, r"D:\github\fengjutian.github.io\.agents\skills\blog-post-publishing\scripts")
import covers

covers.W, covers.H = 1410, 600
ACCENT = (208, 92, 132)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wechat-cover-235.jpg")

img, d = covers.canvas((1010, 300), ACCENT, 470, 0.32)
covers.head(d, ACCENT, "认知博弈 / I-POMDP / 可辨识性",
            "认知\n博弈", "两个主体互相预测时，未来由谁决定",
            (covers.M, 146), 92, (covers.M, 384), 610, thesis_size=24)
covers.motif_phaselag(d, (750, 78, 570, 424), ACCENT, "行动 → 观测 → 更新 → 行动")
d.text((covers.M, 486), "信念表示 · 递归层级 · 可辨识性", font=covers.font(19), fill=covers.DIM)
covers.domain(d)
img.save(OUT, "JPEG", quality=92, optimize=True, subsampling=0)
print("wrote", OUT, img.size)
