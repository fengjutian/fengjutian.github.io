# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, r".agents\skills\blog-post-publishing\scripts")
from figkit import (BG, BLUE, BLUE_BG, GRAY_BG, GREEN, GREEN_BG, INK, LINE,
                    MUTED, ORANGE, ORANGE_BG, PURPLE, PURPLE_BG, arrow, box,
                    caption, font, label, new_canvas, polyline)

OUT = r"assets\img\blog\mainline-git-native-intent-memory"
os.makedirs(OUT, exist_ok=True)

ACC = (40, 84, 148)
ACC_BG = (232, 239, 249)
RED = (176, 52, 52)
RED_BG = (251, 235, 235)


def dashed(d, p1, p2, color=LINE, width=2, dash=10, gap=7):
    import math
    x1, y1 = p1
    x2, y2 = p2
    ln = math.hypot(x2 - x1, y2 - y1)
    if ln == 0:
        return
    ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
    t = 0.0
    while t < ln:
        a = (x1 + ux * t, y1 + uy * t)
        b = (x1 + ux * min(t + dash, ln), y1 + uy * min(t + dash, ln))
        d.line((a[0], a[1], b[0], b[1]), fill=color, width=width)
        t += dash + gap


def chip(d, x, y, text, fg, bg, size=16, pad=12, h=30):
    w = d.textlength(text, font=font(size)) + pad * 2
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=bg, outline=fg, width=2)
    d.text((x + pad, y + h // 2), text, font=font(size), fill=fg, anchor="lm")
    return w


# ---------------------------------------------------------------- fig 01
def fig01():
    W, H = 1400, 860
    img, d = new_canvas(W, H)
    label(d, 60, 44, "一个仓库，两条互不相干的历史", 26, INK, True)

    # left: commit spine
    d.rounded_rectangle((50, 76, 630, 780), radius=16, fill=(252, 253, 255), outline=LINE, width=2)
    label(d, 74, 104, "提交线：代码的历史", 20, MUTED, True)
    spine_x = 130
    rows = [
        ("c0f1a2", "重构导出模块", None),
        ("9d3e41", "改用 Parquet", "int_a1b2"),
        ("5b77c9", "补兼容分支", None),
        ("e2aa07", "移除旧队列", "int_c7d4"),
        ("74b1d8", "调整重试", None),
    ]
    y0, step = 160, 118
    d.line((spine_x, y0, spine_x, y0 + step * (len(rows) - 1)), fill=LINE, width=3)
    for i, (h, msg, note) in enumerate(rows):
        y = y0 + i * step
        d.ellipse((spine_x - 9, y - 9, spine_x + 9, y + 9), fill=INK)
        d.text((spine_x + 24, y - 26), h, font=font(18), fill=MUTED)
        d.text((spine_x + 24, y + 4), msg, font=font(20), fill=INK)
        if note:
            nx = 330
            dashed(d, (spine_x + 18, y), (nx - 6, y), color=ACC, width=2)
            d.rounded_rectangle((nx, y - 27, nx + 236, y + 27), radius=12,
                                fill=ACC_BG, outline=ACC, width=2)
            d.text((nx + 16, y - 8), note, font=font(19), fill=ACC, anchor="lm")
            d.text((nx + 16, y + 14), "note · 决策与约束", font=font(15), fill=MUTED, anchor="lm")
    label(d, 74, 738, "note 跟着 commit 走：代码被 checkout 到哪，判断就在哪", 17, MUTED)

    # right: refs table
    label(d, 690, 104, "ref 命名空间：意图的历史", 20, MUTED, True)
    refs = [
        ("refs/heads/main", "commit + tree，只有代码", "Git 原生", LINE, GRAY_BG),
        ("refs/mainline/actors/<id>/log", "append-only JSONL，每个 actor 一条", "新增", ACC, ACC_BG),
        ("refs/notes/mainline/intents", "commit 上挂 intent，代码合并到哪就跟到哪", "新增", ACC, ACC_BG),
        ("refs/mainline/imports/<id>/branches/*", "fork 的对象保活，供 squash 后按 tree 匹配", "新增", ACC, ACC_BG),
    ]
    y = 140
    for name, sub, tag, fg, bg in refs:
        h = 116
        d.rounded_rectangle((672, y, 1340, y + h), radius=14, fill=bg, outline=fg, width=2)
        d.text((700, y + 28), name, font=font(21, True), fill=fg if fg != LINE else INK)
        d.text((700, y + 64), sub, font=font(18), fill=MUTED)
        tw = d.textlength(tag, font=font(15)) + 22
        d.rounded_rectangle((1310 - tw, y + 16, 1310, y + 44), radius=14, outline=fg, width=2, fill=BG)
        d.text(((1310 - tw + 1310) / 2, y + 30), tag, font=font(15), fill=fg, anchor="mm")
        y += h + 14

    d.rounded_rectangle((672, 664, 1340, 776), radius=14, fill=(250, 250, 252), outline=LINE, width=2)
    d.text((700, 690), "两条历史唯一的交点，是那行 note", font=font(20, True), fill=INK)
    d.text((700, 726), "clone / fetch / push 一次，两条历史一起走", font=font(18), fill=MUTED)

    img.save(os.path.join(OUT, "fig-01-two-namespaces.png"))


# ---------------------------------------------------------------- fig 02
def fig02():
    W, H = 1400, 760
    img, d = new_canvas(W, H)
    label(d, 60, 44, "事件流留在 Git，视图留在本地", 26, INK, True)

    # A: actor log
    d.rounded_rectangle((60, 100, 470, 470), radius=16, fill=ACC_BG, outline=ACC, width=2)
    label(d, 84, 126, "refs/mainline/actors/<id>/log", 17, ACC, True)
    events = ["intent.started", "decision.recorded", "risk.added", "intent.sealed"]
    for i, e in enumerate(events):
        y = 168 + i * 62
        d.rounded_rectangle((86, y, 442, y + 46), radius=10, fill=BG, outline=LINE, width=2)
        d.text((104, y + 23), e, font=font(19), fill=INK, anchor="lm")
        d.text((420, y + 23), f"e{i+1}", font=font(16), fill=MUTED, anchor="rm")
    d.text((86, 432), "只追加，不改写：谁写谁的分片", font=font(17), fill=MUTED)

    arrow(d, (480, 285), (556, 285), color=INK, width=3)

    # B: replay
    d.rounded_rectangle((566, 150, 900, 420), radius=16, fill=GRAY_BG, outline=INK, width=2)
    d.multiline_text((733, 250), "全量重放", font=font(30, True), fill=INK, anchor="mm")
    d.multiline_text((733, 320), "事件 → 视图\n纯函数，无外部状态", font=font(18), fill=MUTED,
                     anchor="mm", align="center", spacing=10)

    arrow(d, (910, 285), (986, 285), color=INK, width=3)

    # C: views
    d.rounded_rectangle((972, 108, 1340, 578), radius=18, fill=(252, 252, 254), outline=LINE,
                        width=2)
    dashed(d, (986, 122), (1326, 122), color=LINE)
    dashed(d, (986, 564), (1326, 564), color=LINE)
    dashed(d, (986, 122), (986, 564), color=LINE)
    dashed(d, (1326, 122), (1326, 564), color=LINE)
    label(d, 1000, 142, ".ml-cache/views/  ·  gitignored", 17, MUTED, True)
    views = ["mainline.json", "proposed-index.json", "phase1-warnings.json", "last-sync.json"]
    for i, v in enumerate(views):
        y = 186 + i * 96
        d.rounded_rectangle((1000, y, 1312, y + 58), radius=10, fill=GRAY_BG, outline=LINE, width=2)
        d.text((1020, y + 29), v, font=font(19), fill=INK, anchor="lm")

    # bottom: consumers
    for i, (name, sub) in enumerate([("preflight", "编辑前先读"), ("status", "现在能不能动手"),
                                    ("hub", "给人看的同一份视图")]):
        x = 60 + i * 306
        d.rounded_rectangle((x, 604, x + 286, 700), radius=12, fill=BG, outline=ACC, width=2)
        d.text((x + 143, 636), name, font=font(21, True), fill=ACC, anchor="mm")
        d.text((x + 143, 674), sub, font=font(16), fill=MUTED, anchor="mm")
    d.text((1000, 640), "视图可以删：", font=font(18), fill=MUTED)
    d.text((1000, 672), "删掉不丢数据，只是要重放", font=font(18), fill=MUTED)

    img.save(os.path.join(OUT, "fig-02-event-log-and-view.png"))


# ---------------------------------------------------------------- fig 03
def fig03():
    W, H = 1400, 806
    img, d = new_canvas(W, H)
    label(d, 60, 44, "squash 之后，意图靠什么找回代码", 26, INK, True)

    # branch commits
    label(d, 60, 96, "分支上（seal 时记下的）", 18, MUTED, True)
    for i, h in enumerate(["b1", "b2", "b3"]):
        x = 60 + i * 128
        d.rounded_rectangle((x, 126, x + 104, 186), radius=12, fill=GRAY_BG, outline=LINE, width=2)
        d.text((x + 52, 156), h, font=font(20, True), fill=INK, anchor="mm")

    arrow(d, (452, 156), (556, 156), color=MUTED)
    d.rounded_rectangle((566, 118, 806, 196), radius=12, fill=ORANGE_BG, outline=ORANGE, width=2)
    d.multiline_text((686, 157), "squash merge\n父提交压成一个", font=font(17), fill=ORANGE,
                     anchor="mm", align="center", spacing=6)
    arrow(d, (816, 156), (900, 156), color=MUTED)

    d.rounded_rectangle((910, 108, 1340, 214), radius=12, fill=ACC_BG, outline=ACC, width=2)
    d.text((940, 138), "main 上的 M", font=font(21, True), fill=ACC)
    d.text((940, 176), "新的 commit hash，同一个 tree", font=font(17), fill=MUTED)

    # intent fields
    d.rounded_rectangle((60, 248, 640, 392), radius=14, fill=BG, outline=INK, width=2)
    label(d, 84, 272, "封存的 intent 里记了什么", 19, INK, True)
    d.text((84, 316), "code_commit = b3", font=font(19), fill=MUTED)
    d.text((84, 352), "code_tree   = T", font=font(19), fill=ACC)
    label(d, 700, 272, "pin：把 intent 挂到 M 上的三级级联", 19, INK, True)

    rows = [
        ("1  tree_hash", "M 的 tree == intent.code_tree", "命中", "squash 保留树", GREEN, GREEN_BG),
        ("2  commit_hash", "M 的 hash == intent.code_commit", "落空", "squash 换了 hash", MUTED, GRAY_BG),
        ("3  goal_text", "M 的 message 含 intent.goal 原文", "兜底", "前两级都失手才用", ORANGE, ORANGE_BG),
    ]
    y = 300
    for name, cond, verdict, why, fg, bg in rows:
        d.rounded_rectangle((700, y, 1340, y + 96), radius=12, fill=bg, outline=fg, width=2)
        d.text((724, y + 28), name, font=font(19, True), fill=fg)
        d.text((724, y + 62), cond, font=font(17), fill=MUTED)
        d.text((1220, y + 28), verdict, font=font(20, True), fill=fg, anchor="ra")
        d.text((1330, y + 62), why, font=font(15), fill=MUTED, anchor="ra")
        y += 112

    # result
    d.rounded_rectangle((700, 660, 1340, 742), radius=12, fill=ACC_BG, outline=ACC, width=3)
    d.text((724, 686), "结果：note 写到 refs/notes/mainline/intents", font=font(19, True), fill=ACC)
    d.text((724, 718), "一个 commit 上可以挂多个 intent，note 是合并而不是覆盖", font=font(16), fill=MUTED)

    label(d, 60, 436, "为什么第 1 级能命中：", 18, INK, True)
    d.multiline_text((60, 468), "squash 压掉的是提交关系，\n不是文件内容。树没变，\n所以 tree 仍是那把钥匙。",
                     font=font(18), fill=MUTED, spacing=10)
    label(d, 60, 590, "这是从级联顺序推断的，", 16, MUTED)
    label(d, 60, 616, "官方只说它让 squash 的 pin 接近全中。", 16, MUTED)

    img.save(os.path.join(OUT, "fig-03-pin-cascade.png"))


# ---------------------------------------------------------------- fig 04
def fig04():
    W, H = 1400, 720
    img, d = new_canvas(W, H)
    label(d, 60, 44, "每个提交只有三种状态，缺口是其中一种", 26, INK, True)

    states = ["s"] * 4 + ["c"] * 5 + ["u"] + ["c", "c"] + ["u", "u"] + ["c"] * 4 + ["s"] + ["c"] * 5
    x0, y0, sq, gap = 60, 140, 30, 8
    base_idx = 4
    for i, s in enumerate(states):
        x = x0 + i * (sq + gap)
        if s == "c":
            d.rounded_rectangle((x, y0, x + sq, y0 + sq), radius=6, fill=ACC, outline=ACC)
        elif s == "s":
            d.rounded_rectangle((x, y0, x + sq, y0 + sq), radius=6, fill=(232, 235, 240), outline=LINE, width=2)
            d.line((x + 7, y0 + sq - 7, x + sq - 7, y0 + 7), fill=MUTED, width=2)
        else:
            d.rounded_rectangle((x, y0, x + sq, y0 + sq), radius=6, fill=BG, outline=ORANGE, width=3)
            d.line((x + 9, y0 + 9, x + sq - 9, y0 + sq - 9), fill=ORANGE, width=3)
            d.line((x + sq - 9, y0 + 9, x + 9, y0 + sq - 9), fill=ORANGE, width=3)

    bx = x0 + base_idx * (sq + gap) - gap / 2
    dashed(d, (bx, 96), (bx, 206), color=INK, width=2)
    label(d, bx + 12, 96, "init 时的 main HEAD：此前一律记 skipped", 17, INK)
    label(d, x0, 236, "→ 越往右越新，一个方块就是一个 main 上的提交", 16, MUTED)

    # legend
    d.rounded_rectangle((60, 300, 650, 512), radius=14, fill=(252, 253, 255), outline=LINE, width=2)
    rows = [("covered", "commit 上挂了 sealed intent", ACC),
            ("skipped", "显式声明这一笔不需要意图", MUTED),
            ("uncovered", "既没挂也没声明，就是 gaps", ORANGE)]
    for i, (name, desc, fg) in enumerate(rows):
        y = 336 + i * 58
        sx, sy, ss = 88, y - 18, 20
        if name == "covered":
            d.rounded_rectangle((sx, sy, sx + ss, sy + ss), radius=4, fill=ACC, outline=ACC)
        elif name == "skipped":
            d.rounded_rectangle((sx, sy, sx + ss, sy + ss), radius=4, fill=(232, 235, 240), outline=LINE, width=2)
            d.line((sx + 5, sy + ss - 5, sx + ss - 5, sy + 5), fill=MUTED, width=2)
        else:
            d.rounded_rectangle((sx, sy, sx + ss, sy + ss), radius=4, fill=BG, outline=ORANGE, width=3)
            d.line((sx + 6, sy + 6, sx + ss - 6, sy + ss - 6), fill=ORANGE, width=2)
            d.line((sx + ss - 6, sy + 6, sx + 6, sy + ss - 6), fill=ORANGE, width=2)
        label(d, 124, y, name, 18, fg, True)
        label(d, 124, y + 26, desc, 16, MUTED)

    # skip mechanisms
    d.rounded_rectangle((672, 300, 1340, 512), radius=14, fill=ORANGE_BG, outline=ORANGE, width=2)
    label(d, 696, 328, "两种合法的跳过", 19, ORANGE, True)
    d.text((696, 366), "commit message 里加 trailer：", font=font(17), fill=MUTED)
    d.text((696, 396), "Mainline-Skip: formatting only", font=font(19), fill=INK)
    d.text((696, 438), "或在配置里写 pattern（版本号、格式化、生成物）", font=font(16), fill=MUTED)
    d.text((696, 470), "跳过是声明，不是沉默", font=font(16), fill=MUTED)

    # gaps output
    d.rounded_rectangle((672, 536, 1340, 656), radius=14, fill=GRAY_BG, outline=LINE, width=2)
    label(d, 696, 556, "mainline gaps", 16, MUTED, True)
    d.text((696, 584), "2 commits on main have no intent", font=font(18), fill=INK)
    d.text((696, 618), "→ start --commits <sha>   或   seal 补写", font=font(16), fill=MUTED)

    label(d, 60, 546, "覆盖率不是仪表盘，是提问：", 20, INK, True)
    d.text((60, 582), "这个仓库里，哪些改动没人解释过？", font=font(20), fill=MUTED)
    d.text((60, 632), "知识库回答不了这个问题，", font=font(18), fill=MUTED)
    d.text((60, 662), "因为它不知道自己的空白在哪里。", font=font(18), fill=MUTED)

    img.save(os.path.join(OUT, "fig-04-coverage-states.png"))


# ---------------------------------------------------------------- fig 05
def fig05():
    W, H = 1400, 780
    img, d = new_canvas(W, H)
    label(d, 60, 44, "preflight 的两种协作尺度", 26, INK, True)

    col_x = [470, 900]
    col_w = 410
    headers = [("coordination_scope = team", "默认，跨机器"), ("= local_worktrees", "本机 + linked worktree")]
    for i, (h, s) in enumerate(headers):
        x = col_x[i]
        d.rounded_rectangle((x, 106, x + col_w, 190), radius=12, fill=GRAY_BG, outline=LINE, width=2)
        d.text((x + 20, 128), h, font=font(18, True), fill=INK)
        d.text((x + 20, 158), s, font=font(15), fill=MUTED)

    rows = [
        ("同机 linked worktree\n的 drafting 草稿", [("阻塞", RED, RED_BG), ("阻塞", RED, RED_BG)]),
        ("共享 ref 上的\nproposed intent", [("阻塞", RED, RED_BG), ("仅警告", ORANGE, ORANGE_BG)]),
        ("只是 goal 文本相似", [("提示", MUTED, GRAY_BG), ("提示", MUTED, GRAY_BG)]),
    ]
    y = 196
    for name, cells in rows:
        d.multiline_text((70, y + 44), name, font=font(19), fill=INK, spacing=8)
        for i, (txt, fg, bg) in enumerate(cells):
            x = col_x[i]
            d.rounded_rectangle((x, y, x + col_w, y + 116), radius=12, fill=bg, outline=fg, width=2)
            d.text((x + col_w / 2, y + 58), txt, font=font(26, True), fill=fg, anchor="mm")
        y += 132

    d.text((70, 606), "尺度不同，语义不变：能看到对方，才有机会先改方案再改代码。", font=font(18), fill=MUTED)

    # hook budget
    d.rounded_rectangle((60, 646, 1340, 748), radius=14, fill=ACC_BG, outline=ACC, width=2)
    d.text((84, 668), "hook 只做机械动作：session 开始时跑 sync + status，把快照塞进上下文", font=font(17), fill=INK)
    d.text((84, 702), "注入有预算：会话开始 32 KiB，每轮 16 KiB；超了换成一行警告，指向完整命令", font=font(17), fill=MUTED)
    d.text((1150, 668), "不替 Agent 决定", font=font(16, True), fill=ACC, anchor="ra")
    d.text((1150, 702), "start / append / seal", font=font(16), fill=MUTED, anchor="ra")

    img.save(os.path.join(OUT, "fig-05-preflight-scope.png"))


if __name__ == "__main__":
    fig01()
    fig02()
    fig03()
    fig04()
    fig05()
    print("ok", OUT)
