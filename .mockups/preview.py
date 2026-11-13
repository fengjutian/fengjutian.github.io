import io
import os

base = r"D:\github\fengjutian.github.io"
css = io.open(os.path.join(base, ".mockups", "blog.css"), encoding="utf-8").read()

posts = [
    (
        "技术随笔",
        "TransformerLens：打开大模型的黑盒，用 Hook 和因果干预研究 Transformer 内部",
        "从 Hook 系统、Activation Patching、DLA 到 4.0 的 Driver 架构，系统梳理 TransformerLens 这套机制可解释性工具链能证明什么、不能证明什么。",
        "2026-11-13",
        "12 分钟阅读",
        "transformerlens-mech-interp.jpg",
    ),
    (
        "工程实践",
        "Sub2API：把 Claude、OpenAI、Gemini 统一接入，一个开源 AI API 网关的设计与边界",
        "从多账号管理、API Key 分发、账号调度、Token 级计费到协议适配，拆解 Sub2API 这套 Go + Vue 3 的 AI API 网关架构，以及它在合规与稳定性上的真实边界。",
        "2026-11-13",
        "7 分钟阅读",
        "sub2api-ai-api-gateway.jpg",
    ),
    (
        "技术随笔",
        "Train LLM From Scratch：从零开始训练自己的大语言模型",
        "使用原生 PyTorch，从 Tokenizer、Transformer 和预训练出发，逐步理解 SFT、DPO、PPO、GRPO 与大语言模型的完整训练流程。",
        "2026-11-12",
        "6 分钟阅读",
        "train-llm-from-scratch.jpg",
    ),
    (
        "技术随笔",
        "DeepSeek-V4.1-Flash-1017-Uncensored：不重新训练模型，直接修改权重，让 AI 改变回答行为",
        "从闭式权重编辑、MoE 架构、能力评测和部署方式出发，分析如何在不重新训练模型的情况下改变大模型的拒绝行为。",
        "2026-11-12",
        "4 分钟阅读",
        "deepseek-v4-weight-editing.jpg",
    ),
    (
        "技术随笔",
        "Idol：一张图片生成百万级 3D 高斯模型，AI 正在重新定义三维建模",
        "Idol 通过单张图片推断三维结构，最多生成 1,048,576 个 3D Gaussian，为三维资产生成与实时交互提供了新的工作流。",
        "2026-11-12",
        "5 分钟阅读",
        "idol-image-to-3d-gaussian.jpg",
    ),
]

items = []
for cat, title, desc, date, read, cover in posts:
    items.append(
        """      <li class="post-item">
        <a class="post-item-link" href="#">
          <div class="post-item-body">
            <div class="post-item-cat">%s</div>
            <h2 class="post-item-title">%s</h2>
            <p class="post-item-desc">%s</p>
            <p class="post-item-meta">
              <time datetime="%s">%s</time>
              <span class="post-item-dot">·</span>
              %s
            </p>
          </div>
          <span class="post-item-thumb"><img src="../assets/img/blog/%s" alt="" width="800" height="500" /></span>
        </a>
      </li>"""
        % (cat, title, desc, date, date, read, cover)
    )

html = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<style>
:root {
  --global-theme-color: #b509ac;
  --global-text-color: #16181d;
  --global-text-color-light: #6b7280;
  --global-divider-color: #ececec;
  --global-card-bg-color: #f5f5f7;
}
html, body { margin:0; padding:0; background:#fff; color:#16181d;
  font-family: 'Segoe UI','Microsoft YaHei','PingFang SC',sans-serif; -webkit-font-smoothing: antialiased; }
a { color: inherit; }
.container { max-width: 1140px; margin: 0 auto; padding: 0 24px; }
.nav { border-bottom: 1px solid #ececec; }
.nav-inner { max-width: 1120px; margin: 0 auto; padding: 0 32px; height: 72px; display: flex; align-items: center; gap: 28px; }
.brand { font-size: 16px; font-weight: 500; white-space: nowrap; }
.brand span { color:#6f7683; font-weight: 400; }
.nav-links { margin-left: auto; display: flex; align-items: center; gap: 26px; font-size: 14.5px; color:#4b5563; }
.nav-links .active { color:#b509ac; font-weight: 500; }
.nav-icons { display:flex; align-items:center; gap:16px; color:#4b5563; }
.kbd { font-size:12px; color:#6f7683; border:1px solid #ececec; border-radius:4px; padding:1px 5px; margin-left:-8px; }
.footer { border-top:1px solid #ececec; padding:18px 24px 22px; text-align:center; font-size:12px; color:#6f7683; }
__CSS__
</style>
</head>
<body>
<header class="nav">
  <div class="nav-inner">
    <div class="brand">Fengjutian <span>· 独立开发者</span></div>
    <nav class="nav-links">
      <a href="#">关于我</a><a href="#" class="active">博客</a><a href="#">项目</a><a href="#">开源仓库</a><a href="#">动态</a>
    </nav>
    <div class="nav-icons"><span class="kbd">ctrl k</span></div>
  </div>
</header>
<div class="container">
  <div class="post">
    <div class="header-bar">
      <h1>Fengjutian 的博客</h1>
      <h2>关于 AI、开发者工具、知识管理与产品实践的记录</h2>
    </div>

    <div class="blog-filters">
      <a href="#"><span class="blog-filter-hash">#</span>AI</a><span class="blog-filter-sep">·</span>
      <a href="#"><span class="blog-filter-hash">#</span>开发者工具</a><span class="blog-filter-sep">·</span>
      <a href="#"><span class="blog-filter-hash">#</span>开源</a><span class="blog-filter-sep">·</span>
      <a href="#">技术随笔</a><span class="blog-filter-sep">·</span>
      <a href="#">工程实践</a>
    </div>

    <hr class="blog-rule" />

    <div class="pinned-posts">
      <a class="pinned-post" href="#">
        <div class="pinned-label">置顶</div>
        <h2 class="pinned-title">从这里开始</h2>
        <p class="pinned-desc">记录 AI、开发者工具、知识管理与产品实践。</p>
        <p class="post-item-meta"><time datetime="2026-10-15">2026-10-15</time><span class="post-item-dot">·</span>1 分钟阅读</p>
      </a>
    </div>

    <ul class="post-list">
__ITEMS__
    </ul>
  </div>
</div>
<footer class="footer">© Copyright 2026 Ju Tian Feng. Powered by Jekyll with al-folio theme. Hosted by GitHub Pages.</footer>
</body>
</html>"""

html = html.replace("__CSS__", css).replace("__ITEMS__", "\n".join(items))
io.open(os.path.join(base, ".mockups", "final-preview.html"), "w", encoding="utf-8", newline="\n").write(html)
print("written", len(html))
