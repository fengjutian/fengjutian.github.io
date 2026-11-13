---
name: blog-post-publishing
description: "Use when the user pastes a long Chinese tech article draft (often ending with 写文章 / 写一篇 / 发文章), or asks to publish, rewrite, or fact-check a post for the al-folio blog at fengjutian.github.io. Covers the whole pipeline: verifying every claim against primary sources, choosing a thesis instead of a feature tour, generating the technical figures and thumbnail, matching repo front-matter and style conventions, and committing the post."
compatibility: "Needs Python with Pillow (bundled DSH runtime is enough; matplotlib is NOT installed), Node + node_modules/.bin/prettier, git. Jekyll/Ruby is usually absent and Docker may be down, so a local site build is usually impossible — validate mechanically instead and say so."
metadata:
  version: "1.0.0"
  author: "fengjutian"
---

# Publishing a post on fengjutian.github.io

The user typically pastes a complete-looking draft produced by a chat model. **The draft is raw material, not the deliverable.** Three things always need work: the facts (drafts hallucinate numbers), the argument (drafts tour features instead of making a point), and the packaging (front matter, figures, quotes, date).

Do all of this without asking permission for each step; ask only when the thesis itself is ambiguous.

## Non-negotiables

1. **Verify before publishing.** Every number, model name, license, platform claim, and API name gets checked against a primary source. Where the draft and the source disagree, the source wins and the post says so.
2. **Never ship a feature tour.** The post must have one sentence-level thesis, and every section must serve it.
3. **Never claim a build you did not run.** If Jekyll cannot run locally, report that plainly instead of implying the site was verified.
4. **Never leave ASCII quotes in Chinese prose**, and never let `{{` / `{%` leak into the body outside image tags.
5. **Backdate the post.** `future: false` is the Jekyll default here; a post dated later today is silently excluded.

## Stage 1 — Read the draft, extract claims

Skim for: numbers, proper nouns (model names, versions, benchmark names), platform/support claims, license claims, and benchmark tables. List them; those are the things you will check. Also note what the draft is *missing* — the strongest sections usually come from the primary source, not the draft.

Watch for these recurring draft tells: inflated marketing ordering, "支持 X 种语言" with no source, feature lists with no cost, and meta sections (`配图建议`, `我的技术评价`, `文章依据`, trailing `写文章` button text) that must be deleted before publishing.

## Stage 2 — Verify against primary sources

Fetch in this order, and prefer the earliest:

1. The project's own `README.md` (raw.githubusercontent.com URL is cleaner than the GitHub HTML).
2. The paper: `arxiv.org/abs/<id>` for the abstract, `arxiv.org/html/<id>` for methods and tables. **The HTML fetch truncates around the bibliography** — if you need late tables, fetch the benchmark's own companion paper, which often reprints them.
3. The project's model/registry page and docs site (they usually carry download sizes, memory floors, and per-platform support the README omits).
4. Vendor blog / release notes for dates.

Build a small corrections table as you go — draft claim vs. source claim. That table becomes a section of your final reply to the user, and sometimes a paragraph in the post ("论文写 33 种语言，README 的表实际列了 38 条").

Hedge what you infer rather than read. Mark your own reasoning explicitly ("从官方描述推断", "这更像是……而不是……"), and keep inference out of tables that look like measurements.

## Stage 3 — Decide the thesis, rebuild the outline

Write the thesis as one sentence with a claim in it:

- weak: "Boubou 是一个本地语音 AI 工具"
- strong: "本地语音 AI 缺的不是模型，是一层能借给全屋的运行时"

Then rebuild the outline: 9–12 numbered sections (`## 一、…`), opening with a number or a hard contrast, not with "随着……的发展". The shape that works here:

1. 钩子（三个数字 / 一句反常识）+ 项目地址 + 一句"本文只讲 X"
2. 问题背景，带一张能力/成本对照表
3. 架构总览（图）
4. 核心技术拆解（2–4 节，每节一个机制 + 一张图）
5. 工程细节（部署、量化、协议、安全任意其一）
6. 评测/数据（用真表，不用形容词）
7. 局限（编号列表，按重要性排）
8. 我的判断（可验证的下一步，接回用户近期关注的方向）
9. 项目与资料（链接列表，含许可证与数据来源声明）

Delete the draft's meta sections. If `我的技术评价` has a good point, fold it into the closing section in first person.

## Stage 4 — Repo conventions

Read `AGENTS.md` and one recent post before writing. The template:

```yaml
---
layout: post
title: <主体>：<带判断的副标题>          # 全角冒号，不用问号收尾
date: YYYY-MM-DD HH:MM:SS +0800        # 必须早于当前时间
thumbnail: assets/img/blog/<slug>.jpg  # 无前导斜杠
description: <60–90 字，写清"拆了什么">
tags: [AI, 开源, <第三个>]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/<slug>.jpg  # 有前导斜杠
---
```

- File name: `_posts/YYYY-MM-DD-<slug>.md`, slug in kebab-case English.
- Images: `assets/img/blog/<slug>/fig-0N-<name>.png` + thumbnail `assets/img/blog/<slug>.jpg`.
- In body: `![说明]({{ '/assets/img/blog/<slug>/fig-01-....png' | relative_url }})`; italic caption line right below (`_…_`).
- Math: `$…$` inline, `$$` blocks on their own lines. MathJax is CHTML 3.2.2 — **no CJK inside `\text{}`**, it renders as tofu.
- Avoid a hero image that duplicates a figure used 20 lines later.

Check with `git log --oneline -5` whether posts are committed directly (they are), and mirror the commit message style: `Add <Project> post with <what the figures show>`.

## Stage 5 — Figures

`matplotlib` is not installed in the bundled runtime; use Pillow. Copy or import `scripts/figkit.py` from this skill (palette, `box`, `arrow`, `polyline`, `label`, `thumbnail` are all there).

Rules that keep the diagrams from looking generated:

- 1400 px wide, generous margins, one idea per figure.
- Accent colour = the thing being explained; everything else grey.
- Label the *mechanism*, not the vendor ("reverse KL · 按语料路由教师").
- Put the cost where the cost lives (download size, latency, memory), in the corner of the panel it belongs to.
- Render, then **look at the PNG** with `read_image`; fix overlaps, clipped text, and arrows that cross boxes. Two iterations is normal.
- Thumbnail: use `scripts/covers.py`, not `figkit.thumbnail`. The old one-template card (same gradient, same 90 px title, same chip row) made ten consecutive posts look identical in the sidebar. Each cover now carries **its own motif** — a mini-diagram of the post's mechanism (cost curve, sparse grid, attention arcs, hub rings, family tree, layer stack + logits, run log, code + remote model) — **its own accent colour**, and one of three compositions (split, mirrored, band). Keep the shared frame (margins, meta line, thesis, domain) so it still reads as one blog. Add the new post to `CARDS` + `build()`, render, look at the JPEG, then drop it at `assets/img/blog/<slug>.jpg`.
  - Check the crop: the sidebar shows it near 1.77:1, so keep everything inside 60 px side margins or the title gets clipped (`TokenEconomizer` and `Transformer Explainer` were cut mid-word).
  - Check it at 240 px wide too — if the motif is invisible at that size it is decoration, not a signature.
  - Do **not** reach for the article's own figure as the cover. Tested both ways: a 1400 px-wide figure carries 20–26 px labels, which land at ~4 px in a 250 px sidebar tile — eight of them read as the same pale block, and 1.43–2.9:1 sources lose 10–40% of the drawing to the 1.77:1 crop. The one exception is a single-idea chart (one line, one bar row, big numerals), which survives a straight crop.

## Stage 6 — Write

Voice: first person, short paragraphs, bold the claim not the noun. Use tables for anything with more than two attributes. Use ```text blocks for pipelines, ```python/```bash for runnable snippets (copy them from the README and adapt, don't invent flags).

Include the failure modes the source documents (restart-based interrupt, unencrypted fallback, single-client limit, non-commercial model licences). Those details are what make the post worth reading.

## Stage 7 — Mechanical cleanup

```powershell
# ASCII double quotes -> Chinese quotes, skipping fenced code blocks
# (script in references/house-style.md)
```

Then scan for leftovers:

```powershell
Select-String -Path $p -Pattern '"' | Where-Object { $_.Line -notmatch '^\s*```' }
(Select-String -Path $p -Pattern "\{\{|\{%" -AllMatches).Matches.Count   # should equal image count
```

## Stage 8 — Validate, then commit

```powershell
& ".\node_modules\.bin\prettier.cmd" --write $p
& ".\node_modules\.bin\prettier.cmd" --check $p
& "<node>" test\style_contract.js
```

Also assert every referenced asset exists (loop over matches, `Test-Path`). Then:

```powershell
git add $post "assets/img/blog/<slug>.jpg" "assets/img/blog/<slug>"
git commit -m "Add <Project> post with <…> diagrams"
```

Do not push. Do not create a `_scripts/`, `_includes/`, `_sass/` or `_layouts/` directory — `lint:style-contract` fails on them.

## Reporting back

The final message should carry: the thesis you chose, a corrections table (draft vs. source), what the figures encode, the verification actually performed, and what could **not** be verified (usually the site build). Link the post and the thumbnail with `present`.
