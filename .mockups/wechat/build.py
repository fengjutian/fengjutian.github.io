# -*- coding: utf-8 -*-
"""Turn article.txt into a WeChat-ready HTML fragment (inline styles only).

WeChat's editor strips <style> blocks and class selectors, ignores MathJax, and
will not render external links as links. So: every style inline, every formula a
text line, every image base64 so a browser copy/paste carries the pixels.
"""
import base64
import io
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article.txt")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cognitive-game-wechat.html")

ACCENT = "#A8405F"
DEEP = "#7A3247"
INK = "#2B2B2B"
BODY = "#3E3E3E"
MUTED = "#8A8A8A"
BORDER = "#EDDFE3"
TINT = "#FBF1F4"
FONT = ("-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB',"
        "'Microsoft YaHei',sans-serif")


def inline(text):
    text = re.sub(r"\*\*(.+?)\*\*",
                  r'<strong style="color:%s;font-weight:700;">\1</strong>' % DEEP, text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)",
                  r'<em style="font-style:italic;color:%s;">\1</em>' % BODY, text)
    text = re.sub(r"\[\[(.+?)\]\]",
                  r'<span style="color:%s;font-weight:600;">\1</span>' % ACCENT, text)
    return text


def p(text, first=False):
    return ('<section style="margin:0 0 22px;font-size:16px;line-height:%s;color:%s;'
            'letter-spacing:.4px;text-align:justify;">%s</section>'
            % ("2.0" if first else "1.85", BODY, inline(text)))


def h2(text):
    return ('<section style="margin:44px 0 20px;padding:0 0 0 12px;border-left:4px solid %s;">'
            '<section style="font-size:19px;font-weight:700;color:%s;line-height:1.5;'
            'letter-spacing:.5px;">%s</section></section>' % (ACCENT, INK, inline(text)))


def quote(text):
    return ('<section style="margin:0 0 14px;padding:14px 18px;background:#FAFAFA;'
            'border-left:3px solid #D9A7B4;border-radius:0 4px 4px 0;">'
            '<section style="font-size:16px;color:#5A5A5A;line-height:1.75;">%s</section></section>'
            % inline(text))


def highlight(text):
    return ('<section style="margin:0 0 24px;padding:16px 18px;background:%s;border-radius:6px;">'
            '<section style="font-size:16px;font-weight:700;color:%s;line-height:1.8;'
            'letter-spacing:.3px;">%s</section></section>' % (TINT, DEEP, inline(text)))


def formula(text):
    return ('<section style="margin:2px 0 26px;padding:18px 14px;background:#FAFAFB;'
            'border:1px solid #EFEFEF;border-radius:6px;text-align:center;">'
            "<section style=\"font-family:Georgia,'Times New Roman',serif;font-size:17px;"
            'color:%s;line-height:1.6;letter-spacing:.6px;">%s</section></section>'
            % (INK, inline(text)))


def image(path, caption):
    full = os.path.join(ROOT, path.replace("/", os.sep))
    if not os.path.exists(full):
        full = os.path.join(os.path.dirname(os.path.abspath(__file__)), path.replace("/", os.sep))
    if not os.path.exists(full):
        raise SystemExit("missing image: " + path)
    with open(full, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")
    mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    cap = ('<section style="margin:10px 0 30px;text-align:center;">'
           '<section style="font-size:13px;color:%s;line-height:1.7;letter-spacing:.2px;">%s'
           "</section></section>" % (MUTED, inline(caption))) if caption else ""
    return ('<section style="margin:30px 0 0;">'
            '<img src="data:%s;base64,%s" style="width:100%%;height:auto;display:block;'
            'border-radius:4px;" /></section>%s' % (mime, b64, cap))


def code(lines):
    body = "\n".join(lines)
    body = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return ('<section style="margin:0 0 26px;padding:16px 18px;background:#F7F7F8;'
            'border-radius:6px;">'
            "<pre style=\"margin:0;font-family:Menlo,Consolas,'Courier New',monospace;"
            'font-size:12.5px;line-height:1.75;color:#333;white-space:pre-wrap;'
            'word-break:break-word;\">%s</pre></section>' % body)


def table(rows):
    head, body = rows[0], rows[1:]
    out = ['<section style="margin:0 0 26px;overflow-x:auto;">',
           '<table style="border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.65;">']
    out.append("<tr>")
    for cell in head:
        out.append('<th style="padding:10px 8px;border:1px solid %s;background:%s;'
                   'color:%s;font-weight:600;text-align:left;">%s</th>'
                   % (BORDER, TINT, DEEP, inline(cell)))
    out.append("</tr>")
    for row in body:
        out.append("<tr>")
        for cell in row:
            out.append('<td style="padding:10px 8px;border:1px solid %s;color:%s;'
                       'vertical-align:top;">%s</td>' % (BORDER, BODY, inline(cell)))
        out.append("</tr>")
    out.append("</table></section>")
    return "".join(out)


def card(title, meta, lines):
    meta_html = ('<span style="font-size:13px;color:%s;font-weight:400;"> · %s</span>'
                 % (MUTED, inline(meta))) if meta else ""
    body = "<br/>".join(inline(x) for x in lines)
    return ('<section style="margin:0 0 14px;padding:16px 18px;background:#FCFAFB;'
            'border:1px solid #EFE6E9;border-radius:6px;">'
            '<section style="margin:0 0 8px;font-size:16px;font-weight:700;color:%s;">%s%s</section>'
            '<section style="font-size:14px;color:#5A5A5A;line-height:1.75;">%s</section></section>'
            % (DEEP, inline(title), meta_html, body))


def bullet(text, marker="·"):
    return ('<section style="margin:0 0 10px;padding-left:16px;text-indent:-16px;'
            'font-size:16px;color:%s;line-height:1.85;letter-spacing:.3px;">'
            '<span style="color:%s;font-weight:700;">%s</span> %s</section>'
            % (BODY, ACCENT, marker, inline(text)))


def divider():
    return ('<section style="margin:40px 0;text-align:center;color:#D9C3CA;'
            'font-size:14px;letter-spacing:8px;">· · ·</section>')


def foot(parts):
    body = "<br/>".join(inline(x) for x in parts)
    return ('<section style="margin:44px 0 0;padding:18px;background:#FAFAFA;'
            'border-radius:6px;text-align:center;">'
            '<section style="font-size:13px;color:%s;line-height:1.9;letter-spacing:.2px;">%s'
            "</section></section>" % (MUTED, body))


def build():
    raw = io.open(SRC, encoding="utf-8").read().split("\n")
    out, i = [], 0
    first_para = True
    while i < len(raw):
        line = raw[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            out.append(h2(line[2:].strip()))
        elif line.startswith("> "):
            buf = [line[2:].strip()]
            while i + 1 < len(raw) and raw[i + 1].startswith("> "):
                i += 1
                buf.append(raw[i][2:].strip())
            out.append(quote("<br/>".join(inline(x) for x in buf)))
        elif line.startswith("FOOT "):
            out.append(foot([x.strip() for x in line[5:].split("|")]))
        elif line.startswith("! "):
            out.append(highlight(line[2:].strip()))
        elif line.startswith("$ "):
            out.append(formula(line[2:].strip()))
        elif line.startswith("IMG "):
            path, _, cap = line[4:].partition("|")
            out.append(image(path.strip(), cap.strip()))
        elif line.startswith("CODE"):
            i += 1
            buf = []
            while i < len(raw) and raw[i].strip() != "END":
                buf.append(raw[i].rstrip())
                i += 1
            out.append(code(buf))
        elif line.startswith("TBL"):
            i += 1
            rows = []
            while i < len(raw) and raw[i].strip() != "END":
                if raw[i].strip():
                    rows.append([c.strip() for c in raw[i].split("||")])
                i += 1
            out.append(table(rows))
        elif line.startswith("CARD "):
            parts = [x.strip() for x in line[5:].split("||")]
            out.append(card(parts[0], parts[1] if len(parts) > 1 else "",
                            parts[2:] if len(parts) > 2 else []))
        elif line.startswith("- "):
            out.append(bullet(line[2:].strip()))
        elif re.match(r"^\d+\. ", line):
            n, _, rest = line.partition(". ")
            out.append(bullet(rest.strip(), marker=n))
        elif line.startswith("---"):
            out.append(divider())
        else:
            out.append(p(line.strip(), first=first_para))
            first_para = False
        i += 1

    body = "\n".join(out)
    html = ("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\" />\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
            "<title>认知博弈 · 微信公众号版</title>\n</head>\n"
            "<body style=\"margin:0;padding:0;background:#F2F2F2;\">\n"
            "<section style=\"max-width:677px;margin:0 auto;padding:28px 20px 60px;"
            "background:#FFFFFF;font-family:%s;color:%s;\">\n%s\n</section>\n</body>\n</html>\n"
            % (FONT, BODY, body))
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(html)
    print("wrote", OUT, "%.1f KB" % (os.path.getsize(OUT) / 1024.0))


if __name__ == "__main__":
    build()
