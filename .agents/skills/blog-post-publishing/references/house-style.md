# House style — fengjutian.github.io

Details behind the SKILL.md stages. Read before writing; copy the templates verbatim.

## Front matter

```yaml
---
layout: post
title: <主体>：<带判断的副标题>
date: YYYY-MM-DD HH:MM:SS +0800
thumbnail: assets/img/blog/<slug>.jpg
description: <60–90 字>
tags: [AI, 开源, 开发者工具]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/<slug>.jpg
---
```

Rules that matter:

- `date` must be **earlier than now**. `future` is unset in `_config.yml`, so Jekyll's default (`false`) silently drops same-day future posts. Two posts in this repo were bitten by it.
- `thumbnail` and `og_image` point at the same file; only `og_image` keeps the leading slash.
- `description` states what was *dissected* ("从 X、Y 到 Z，拆解……"), never "本文介绍了……".
- Tags: keep the existing vocabulary (`AI`, `开源`, `开发者工具`, `机器学习`); don't invent one-off tags.

## Section skeleton

```
钩子：一个数字 / 一句反常识 / 一个对比
项目地址 + 一句"本文只讲 X"

## 一、问题：为什么这件事不简单
## 二、它是什么（三条命令 / 三个组件 / 一张总览图）
## 三～六、机制拆解（每节：一个机制 + 一张图 + 一段代价）
## 七、评测 / 数据（真表，带来源）
## 八、工程细节（部署 / 安全 / 协议，挑最容易被踩的）
## 九、局限（编号，按重要性排）
## 十、我的判断（可验证的下一步）
## 项目与资料
```

Section headings use Chinese numerals and a colon-free short phrase; the colon version is allowed when the second half carries the claim (`## 五、打断：体验的分水岭，也是进程模型的照妖镜`).

## Sentence-level habits

- Short paragraphs (1–3 sentences). Bold the claim, not the noun: `**Pipeline 一上来就是 5.6GB 起**`.
- Every table has a reason to exist: attributes ≥ 2, or a comparison across ≥ 3 items.
- Numbers get a source in the same paragraph or the closing section.
- Inference is marked: "从官方描述推断", "这更像是……而不是……".
- Closing section always returns to the user's current research thread (here: NNsight / pyvene / representation analysis).

## Image conventions

- Files: `assets/img/blog/<slug>/fig-0N-<semantic-name>.png`, 1400 px wide.
- Thumbnail: `assets/img/blog/<slug>.jpg`, 1200×630, quality 92 (JPEG, even though figures are PNG).
- Body reference: `![说明]({{ '/assets/img/blog/<slug>/fig-01-....png' | relative_url }})`.
- Caption line immediately after, italic, one sentence starting with a noun phrase — not "图片来源".
- Figure text is Chinese; keep English only for API/flag names.

## Mechanical checks

Quote conversion (ASCII `"` → `“”` outside fenced blocks):

```python
import io
p = r"_posts/2026-11-13-example.md"
lines = io.open(p, encoding="utf-8").read().split("\n")
out, in_code = [], False
for ln in lines:
    if ln.strip().startswith("```"):
        in_code = not in_code; out.append(ln); continue
    if in_code or ln.count('"') % 2 or not ln.count('"'):
        out.append(ln); continue
    buf, open_q = [], True
    for ch in ln:
        if ch == '"':
            buf.append("\u201c" if open_q else "\u201d"); open_q = not open_q
        else:
            buf.append(ch)
    out.append("".join(buf))
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out))
```

Asset existence check:

```powershell
$p = "_posts/<file>.md"
Select-String -Path $p -Pattern "/assets/img/blog/[^'| )]*" -AllMatches |
  ForEach-Object { $_.Matches.Value } | Sort-Object -Unique |
  ForEach-Object { "{0}  {1}" -f (Test-Path ($_ -replace '^/', '' -replace '/', '\')), $_ }
```

Formatting / contract:

```powershell
& ".\node_modules\.bin\prettier.cmd" --write $p
& ".\node_modules\.bin\prettier.cmd" --check $p
& "<node.exe>" test\style_contract.js
```

## Console gotcha

PowerShell `Get-Content` without `-Encoding UTF8` renders Chinese as mojibake and can merge lines. Never judge a file's content from console output — use the `read` tool, and write with:

```powershell
[System.IO.File]::WriteAllText((Resolve-Path $p), $s, (New-Object System.Text.UTF8Encoding($false)))
```

## Corrections table format (for the reply, and sometimes for the post)

| 草稿 | 实际（来源） |
| --- | --- |
| 支持 33 种语言 | FLORES-200 口径 33 种；README 语种表 38 条 |
| 模型 90.20 / 75.94 / 84.69 | 论文表 1：91.94 / 75.80 / 85.70 |

## Verification honesty

There is no Ruby and usually no running Docker daemon, so `bundle exec jekyll build` cannot run. Say so in the final message: what *was* checked (prettier, style contract, asset paths, Liquid tag count, front-matter shape) and what was not (rendered site). Never write "构建通过" without a build.
