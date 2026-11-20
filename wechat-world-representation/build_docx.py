# -*- coding: utf-8 -*-
"""把 content.py 渲染为适合微信公众号粘贴的 Word 文档。

- 正文全部保留为可编辑文本
- 独立公式渲染为高清图片（公众号不支持 LaTeX）
- 表格使用 Word 原生表格，粘贴到公众号后仍可编辑
"""

import hashlib
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import Image, ImageChops
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from content import BLOCKS

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "images")
FORMULA_DIR = os.path.join(BASE, "formulas")
OUT = os.path.join(BASE, "世界表征是什么-公众号版.docx")

INK = RGBColor(0x11, 0x18, 0x27)
BODY = RGBColor(0x37, 0x41, 0x51)
MUTED = RGBColor(0x8A, 0x93, 0xA3)
ACCENT = RGBColor(0x1D, 0x4E, 0xD8)
ACCENT_DARK = RGBColor(0x1E, 0x3A, 0x8A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

BODY_FONT = "微软雅黑"
MATH_FONT = "Cambria Math"

rcParams["mathtext.fontset"] = "stix"
rcParams["font.family"] = "STIXGeneral"
rcParams["mathtext.default"] = "regular"

MATH_MAP = {
    r"\mid": " | ",
    r"\rightarrow": "→",
    r"\to": "→",
    r"\Rightarrow": " ⇒ ",
    r"\Delta": "Δ",
    r"\epsilon": "ε",
    r"\ldots": "…",
    r"\dots": "…",
    r"\cdot": "·",
    r"\,": "\u2009",
    r"\colon": ":",
    r"\;": " ",
    r"\ ": " ",
}


# --------------------------------------------------------------------------
# 基础排版工具
# --------------------------------------------------------------------------
def set_run(run, size=11, color=BODY, bold=False, italic=False, font=BODY_FONT):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:eastAsia"), BODY_FONT)


def shade(cell, hex_fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tc_pr.append(shd)


def cell_margins(table, top=70, bottom=70, left=110, right=110):
    tbl_pr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for tag, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{tag}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tbl_pr.append(mar)


def table_borders(table, color="D8E0EE", sz="4"):
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tbl_pr.append(borders)


def para_bottom_border(paragraph, color="E5E7EB", sz="6"):
    p_pr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), sz)
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    p_pr.append(pbdr)


def keep_next(paragraph):
    paragraph.paragraph_format.keep_with_next = True


def no_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    tr_pr.append(el)


# --------------------------------------------------------------------------
# 行内数学：用 Word 的斜体 + 上下标还原，粘贴后仍是文字
# --------------------------------------------------------------------------
def _emit_math(paragraph, text, size, color, bold, script=None):
    if not text:
        return
    run = paragraph.add_run(text)
    set_run(run, size, color, bold, italic=True, font=MATH_FONT)
    if script == "sub":
        run.font.subscript = True
    elif script == "sup":
        run.font.superscript = True


def add_math(paragraph, expr, size=11, color=BODY, bold=False):
    expr = expr.replace("\\colon ", ":").replace("\\colon", ":")
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch in "_^":
            script = "sub" if ch == "_" else "sup"
            i += 1
            if i < n and expr[i] == "{":
                depth = 1
                j = i + 1
                while j < n and depth:
                    if expr[j] == "{":
                        depth += 1
                    elif expr[j] == "}":
                        depth -= 1
                    j += 1
                content = expr[i + 1 : j - 1]
                i = j
            else:
                content = expr[i] if i < n else ""
                i += 1
            # 上下标内部继续按字符区分正斜体
            add_math_fragment(paragraph, content, size, color, bold, script)
            continue
        if ch == "\\":
            for cmd in sorted(MATH_MAP, key=len, reverse=True):
                if expr.startswith(cmd, i):
                    add_math_fragment(paragraph, MATH_MAP[cmd], size, color, bold)
                    i += len(cmd)
                    break
            else:
                i += 1
            continue
        if ch.isascii() and ch.isalpha():
            j = i
            while j < n and expr[j].isascii() and expr[j].isalpha():
                j += 1
            add_math_fragment(paragraph, expr[i:j], size, color, bold)
            i = j
            continue
        j = i
        while j < n and not (expr[j].isascii() and expr[j].isalpha()) and expr[j] not in "_^\\":
            j += 1
        add_math_fragment(paragraph, expr[i:j], size, color, bold)
        i = j


def add_math_fragment(paragraph, text, size, color, bold, script=None):
    if not text:
        return
    # 把片段拆成「字母（斜体）」与「其余（正体）」
    tokens = re.findall(r"[A-Za-z]+|[^A-Za-z]+", text)
    for tok in tokens:
        italic = tok.isascii() and tok.isalpha()
        run = paragraph.add_run(tok)
        set_run(run, size, color, bold, italic=italic, font=MATH_FONT)
        if script == "sub":
            run.font.subscript = True
        elif script == "sup":
            run.font.superscript = True


def add_rich(paragraph, text, size=11, color=BODY, bold=False):
    for part in re.split(r"(\*\*.+?\*\*|\$.+?\$)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            add_rich(paragraph, part[2:-2], size, color, True)
        elif part.startswith("$") and part.endswith("$") and len(part) > 2:
            add_math(paragraph, part[1:-1], size, color, bold)
        else:
            run = paragraph.add_run(part)
            set_run(run, size, color, bold)


# --------------------------------------------------------------------------
# 公式图片
# --------------------------------------------------------------------------
def render_formula(tex, fontsize=16):
    os.makedirs(FORMULA_DIR, exist_ok=True)
    key = hashlib.md5(f"{tex}|{fontsize}".encode("utf-8")).hexdigest()[:16]
    path = os.path.join(FORMULA_DIR, f"{key}.png")
    if os.path.exists(path):
        return path

    fig = plt.figure(figsize=(12, 3), dpi=300)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.5, tex, ha="center", va="center", fontsize=fontsize, color="#111111")
    tmp = path + ".tmp.png"
    fig.savefig(tmp, dpi=300, facecolor="white")
    plt.close(fig)

    img = Image.open(tmp).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bbox = ImageChops.difference(img, bg).getbbox()
    if bbox:
        pad = 26
        box = (
            max(bbox[0] - pad, 0),
            max(bbox[1] - pad, 0),
            min(bbox[2] + pad, img.width),
            min(bbox[3] + pad, img.height),
        )
        img = img.crop(box)
    img.save(path, "PNG")
    os.remove(tmp)
    return path


# --------------------------------------------------------------------------
# 文档构件
# --------------------------------------------------------------------------
def add_paragraph(doc, text, size=11, color=BODY, align=WD_ALIGN_PARAGRAPH.LEFT, after=10, before=0, line=1.7):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    add_rich(p, text, size, color)
    return p


def add_heading(doc, text, level):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(26 if level == 1 else 18)
    pf.space_after = Pt(12 if level == 1 else 8)
    pf.line_spacing = 1.35
    if level == 1:
        run = p.add_run(text)
        set_run(run, 17, INK, bold=True)
        para_bottom_border(p)
        pf.space_before = Pt(30)
    else:
        run = p.add_run(text)
        set_run(run, 13.5, ACCENT, bold=True)
    keep_next(p)
    return p


def add_image(doc, filename, credit, max_width=None):
    path = os.path.join(IMG_DIR, filename)
    with Image.open(path) as im:
        w, h = im.size
    width = max_width or 16.0
    if h > w:
        width = min(width, 11.0)
    if max_width is None and w < 900:
        width = min(width, 11.0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4 if credit else 18)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width))
    if credit:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_before = Pt(0)
        cap.paragraph_format.space_after = Pt(18)
        run = cap.add_run(f"参考：{credit}")
        set_run(run, 8.5, MUTED)


def add_bullets(doc, items, numbered=False):
    for idx, item in enumerate(items, 1):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Cm(0.7)
        pf.first_line_indent = Cm(-0.55)
        pf.space_before = Pt(0)
        pf.space_after = Pt(4)
        pf.line_spacing = 1.6
        marker = f"{idx}. " if numbered else "•  "
        run = p.add_run(marker)
        set_run(run, 11, ACCENT if numbered else MUTED, bold=numbered)
        add_rich(p, item, 11, BODY)


def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table_borders(table)
    cell_margins(table)

    total = sum(widths)
    tbl_pr = table._tbl.tblPr
    tbl_w = OxmlElement("w:tblW")
    tbl_w.set(qn("w:w"), str(int(total / 2.54 * 1440)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_pr.append(tbl_w)

    hdr = table.rows[0]
    no_split(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.width = Cm(widths[i])
        shade(cell, "EEF4FF")
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.35
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        set_run(run, 9.5, ACCENT_DARK, bold=True)

    for r_idx, row in enumerate(rows):
        tr = table.add_row()
        no_split(tr)
        for i, text in enumerate(row):
            cell = tr.cells[i]
            cell.width = Cm(widths[i])
            if r_idx % 2 == 1:
                shade(cell, "FAFBFE")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.4
            if i == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                set_run(run, 9.5, INK, bold=True)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                set_run(run, 9.5, BODY)

    rows = table.rows
    for idx, row in enumerate(rows):
        if idx < len(rows) - 1:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.paragraph_format.keep_with_next = True

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(6)
    spacer.paragraph_format.line_spacing = 1.0
    run = spacer.add_run("")
    set_run(run, 4)
    return table


def add_box(doc, text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table_borders(table, color="C7D2FE", sz="8")
    cell_margins(table, top=140, bottom=140, left=140, right=140)
    tbl_pr = table._tbl.tblPr
    tbl_w = OxmlElement("w:tblW")
    tbl_w.set(qn("w:w"), str(int(16.0 / 2.54 * 1440)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_pr.append(tbl_w)
    cell = table.rows[0].cells[0]
    cell.width = Cm(16.0)
    shade(cell, "F2F6FF")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.4
    run = p.add_run(text)
    set_run(run, 14, ACCENT_DARK, bold=True)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(4)
    spacer.paragraph_format.line_spacing = 1.0
    set_run(spacer.add_run(""), 4)


def add_formula(doc, tex):
    path = render_formula(tex)
    with Image.open(path) as im:
        w_px, h_px = im.size
    width_cm = w_px / 300 * 2.54
    if width_cm > 13.5:
        width_cm = 13.5
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(path, width=Cm(width_cm))


def add_diagram(doc, lines, size=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.6
    for idx, line in enumerate(lines):
        if idx:
            p.add_run().add_break()
        add_rich(p, line, size, ACCENT_DARK, True)


def add_cards(doc, cards):
    for num, title, desc in cards:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.keep_with_next = True
        num_run = p.add_run(num)
        set_run(num_run, 26, RGBColor(0xBF, 0xD3, 0xFF), bold=True)
        run = p.add_run("   ")
        set_run(run, 10)
        title_run = p.add_run(title)
        set_run(title_run, 13.5, INK, bold=True)
        d = doc.add_paragraph()
        d.paragraph_format.left_indent = Cm(0.05)
        d.paragraph_format.space_before = Pt(0)
        d.paragraph_format.space_after = Pt(14)
        d.paragraph_format.line_spacing = 1.65
        run = d.add_run(desc)
        set_run(run, 10.5, BODY)


def add_layer(doc, title, desc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(title)
    set_run(run, 11.5, ACCENT_DARK, bold=True)
    d = doc.add_paragraph()
    d.paragraph_format.space_before = Pt(0)
    d.paragraph_format.space_after = Pt(6)
    d.paragraph_format.line_spacing = 1.55
    run = d.add_run(desc)
    set_run(run, 10.5, BODY)



def para_shading(paragraph, fill):
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)


def para_left_border(paragraph, color="3B82F6", sz="18", space="8"):
    p_pr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), sz)
    left.set(qn("w:space"), space)
    left.set(qn("w:color"), color)
    pbdr.append(left)
    p_pr.append(pbdr)


def add_lead(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(16)
    pf.line_spacing = 1.55
    run = p.add_run(text)
    set_run(run, 15, INK, bold=True)


def add_stage(doc, label, title, desc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.25
    run = p.add_run(label)
    set_run(run, 9, MUTED, bold=True)
    run = p.add_run("   ")
    set_run(run, 9)
    run = p.add_run(title)
    set_run(run, 12, ACCENT_DARK, bold=True)
    d = doc.add_paragraph()
    d.paragraph_format.space_before = Pt(0)
    d.paragraph_format.space_after = Pt(6)
    d.paragraph_format.line_spacing = 1.55
    run = d.add_run(desc)
    set_run(run, 10.5, BODY)


def add_code(doc, code):
    lines = code.split("\n")
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(8)
    pf.space_after = Pt(16)
    pf.line_spacing = 1.2
    pf.left_indent = Cm(0.5)
    pf.keep_together = True
    para_shading(p, "F7F8FA")
    para_left_border(p, "3B82F6", "18", "8")
    for i, line in enumerate(lines):
        if i:
            p.add_run().add_break()
        run = p.add_run(line if line else " ")
        set_run(run, 9.5, RGBColor(0x1F, 0x29, 0x37), font="Consolas")


def add_ftext(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    add_rich(p, text, 13, INK, False)


def add_kicker(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run(text)
    set_run(run, 10, MUTED, bold=True)


# --------------------------------------------------------------------------
def build():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(11)
    normal.font.color.rgb = BODY
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), BODY_FONT)

    doc.core_properties.title = "世界表征（World Representation）是什么？"
    doc.core_properties.author = "冯举天"
    doc.core_properties.comments = "微信公众号排版稿"

    for block in BLOCKS:
        kind = block[0]
        if kind == "title":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.35
            run = p.add_run(block[1])
            set_run(run, 22, INK, bold=True)
        elif kind == "subtitle":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(14)
            p.paragraph_format.line_spacing = 1.4
            run = p.add_run(block[1])
            set_run(run, 11, MUTED)
        elif kind == "h1":
            add_heading(doc, block[1], 1)
        elif kind == "h2":
            add_heading(doc, block[1], 2)
        elif kind == "p":
            add_paragraph(doc, block[1])
        elif kind == "ul":
            add_bullets(doc, block[1], numbered=False)
            doc.paragraphs[-1].paragraph_format.space_after = Pt(10)
        elif kind == "ol":
            add_bullets(doc, block[1], numbered=True)
            doc.paragraphs[-1].paragraph_format.space_after = Pt(10)
        elif kind == "img":
            add_image(doc, block[1], block[2] if len(block) > 2 else "", block[3] if len(block) > 3 else None)
        elif kind == "formula":
            add_formula(doc, block[1])
        elif kind == "table":
            add_table(doc, block[1], block[2], block[3])
        elif kind == "box":
            add_box(doc, block[1])
        elif kind == "diagram":
            add_diagram(doc, block[1], block[2] if len(block) > 2 else 12)
        elif kind == "cards":
            add_cards(doc, block[1])
        elif kind == "layer":
            add_layer(doc, block[1], block[2])
        elif kind == "lead":
            add_lead(doc, block[1])
        elif kind == "stage":
            add_stage(doc, block[1], block[2], block[3])
        elif kind == "code":
            add_code(doc, block[1])
        elif kind == "ftext":
            add_ftext(doc, block[1])
        elif kind == "kicker":
            add_kicker(doc, block[1])
        else:
            raise ValueError(f"unknown block: {kind}")

    doc.save(OUT)
    print("saved:", OUT)


if __name__ == "__main__":
    build()
