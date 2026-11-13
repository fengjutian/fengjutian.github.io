import io
import os
import re

base = r"D:\github\fengjutian.github.io"
path = os.path.join(base, "_pages", "blog.md")
md = io.open(path, encoding="utf-8").read()

m = re.search(r"(?m)^_styles: \|\n(.*?)(?=^pagination:)", md, re.S)
block = m.group(1)
lines = block.splitlines()
out = []
for line in lines:
    stripped = line.strip()
    indent = line[: len(line) - len(line.lstrip())]
    if not stripped:
        out.append("")
        continue
    if stripped.endswith("{") and not stripped.startswith("@"):
        sel = stripped[:-1].strip()
        if sel == ".post":
            out.append(indent + ".post {")
            continue
        parts = [p.strip() for p in sel.split(",")]
        parts = [p if p.startswith(".post ") or p == ".post" else ".post " + p for p in parts]
        out.append(indent + ", ".join(parts) + " {")
    else:
        out.append(line)

new_block = "\n".join(out) + "\n"
md = md[: m.start(1)] + new_block + md[m.end(1) :]
io.open(path, "w", encoding="utf-8", newline="\n").write(md)
print("rewritten selectors")

# keep a copy for the preview
css = "\n".join(l[2:] for l in new_block.splitlines())
io.open(os.path.join(base, ".mockups", "blog.css"), "w", encoding="utf-8", newline="\n").write(css)
