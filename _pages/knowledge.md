---
layout: page
title: 知识地图
permalink: /knowledge/
description: 沿着概念、文章与项目之间的关系，探索本站的知识脉络。
nav: true
nav_order: 3
---

<style>
  .knowledge-intro {
    max-width: 48rem;
    margin-bottom: 1.5rem;
    color: var(--global-text-color-light);
    font-size: 1.05rem;
  }

  .knowledge-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem 1rem;
    align-items: center;
    margin: -0.75rem 0 1.25rem;
    color: var(--global-text-color-light);
    font-size: 0.8rem;
  }

  .knowledge-meta strong {
    color: var(--global-text-color);
    font-variant-numeric: tabular-nums;
  }

  .knowledge-status {
    margin-left: auto;
  }

  .knowledge-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    align-items: center;
    margin-bottom: 1rem;
  }

  .knowledge-search {
    flex: 1 1 16rem;
    min-width: 0;
    padding: 0.65rem 0.85rem;
    border: 1px solid var(--global-divider-color);
    border-radius: 0.65rem;
    color: var(--global-text-color);
    background: var(--global-bg-color);
  }

  .knowledge-search:focus {
    border-color: var(--global-theme-color);
    outline: 2px solid color-mix(in srgb, var(--global-theme-color) 24%, transparent);
    outline-offset: 1px;
  }

  .knowledge-reset,
  .knowledge-chip {
    border: 1px solid var(--global-divider-color);
    border-radius: 999px;
    color: var(--global-text-color);
    background: var(--global-bg-color);
    cursor: pointer;
  }

  .knowledge-reset {
    padding: 0.6rem 0.9rem;
  }

  .knowledge-reset:hover,
  .knowledge-reset:focus-visible,
  .knowledge-chip:hover,
  .knowledge-chip:focus-visible {
    border-color: var(--global-theme-color);
    color: var(--global-theme-color);
  }

  .knowledge-filters {
    display: flex;
    gap: 0.45rem;
    overflow-x: auto;
    margin-bottom: 1rem;
    padding-bottom: 0.3rem;
    scrollbar-width: thin;
  }

  .knowledge-chip {
    flex: 0 0 auto;
    padding: 0.38rem 0.72rem;
    font-size: 0.86rem;
  }

  .knowledge-chip[aria-pressed="true"] {
    border-color: var(--chip-color);
    color: #fff;
    background: var(--chip-color);
  }

  .knowledge-workspace {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 17rem;
    min-height: 42rem;
    overflow: hidden;
    border: 1px solid var(--global-divider-color);
    border-radius: 0.9rem;
    background:
      radial-gradient(circle at 15% 15%, color-mix(in srgb, var(--global-theme-color) 8%, transparent), transparent 35%),
      var(--global-card-bg-color, var(--global-bg-color));
  }

  .knowledge-canvas {
    position: relative;
    min-height: 42rem;
  }

  .knowledge-canvas-controls {
    position: absolute;
    z-index: 2;
    right: 0.75rem;
    bottom: 0.75rem;
    display: flex;
    overflow: hidden;
    border: 1px solid var(--global-divider-color);
    border-radius: 999px;
    background: color-mix(in srgb, var(--global-bg-color) 92%, transparent);
    box-shadow: 0 0.25rem 0.9rem color-mix(in srgb, var(--global-text-color) 10%, transparent);
    backdrop-filter: blur(8px);
  }

  .knowledge-canvas-controls button {
    width: 2.3rem;
    height: 2.3rem;
    padding: 0;
    border: 0;
    border-right: 1px solid var(--global-divider-color);
    color: var(--global-text-color);
    background: transparent;
    cursor: pointer;
  }

  .knowledge-canvas-controls button:last-child {
    border-right: 0;
  }

  .knowledge-canvas-controls button:hover,
  .knowledge-canvas-controls button:focus-visible {
    color: var(--global-theme-color);
    background: color-mix(in srgb, var(--global-theme-color) 8%, transparent);
  }

  .knowledge-canvas svg {
    display: block;
    width: 100%;
    height: 42rem;
    touch-action: none;
  }

  .knowledge-edge {
    marker-end: url(#knowledge-arrow);
    stroke: var(--global-divider-color);
    stroke-width: 1.15;
    transition: opacity 160ms ease, stroke 160ms ease;
  }

  .knowledge-edge.is-compares_with,
  .knowledge-edge.is-related_to {
    marker-end: none;
    stroke-dasharray: 5 4;
  }

  .knowledge-edge.is-grounds {
    stroke-width: 2;
  }

  .knowledge-edge.is-implemented_by {
    stroke: #d18a36;
    stroke-dasharray: 2 3;
  }

  .knowledge-edge.is-hidden {
    pointer-events: none;
    opacity: 0;
  }

  .knowledge-node {
    cursor: pointer;
    transition: opacity 160ms ease;
  }

  .knowledge-node circle {
    stroke: var(--global-bg-color);
    stroke-width: 2.5;
    transition: r 160ms ease, stroke 160ms ease;
  }

  .knowledge-node text {
    fill: var(--global-text-color);
    font-size: 11px;
    font-weight: 500;
    paint-order: stroke;
    stroke: var(--global-bg-color);
    stroke-width: 3px;
    stroke-linejoin: round;
    pointer-events: none;
    opacity: 0;
    transition: opacity 120ms ease;
  }

  .knowledge-node.is-topic text,
  .knowledge-node.show-label text {
    opacity: 1;
  }

  .knowledge-node.is-topic text {
    font-size: 12px;
    font-weight: 700;
  }

  .knowledge-node.is-hidden {
    pointer-events: none;
    opacity: 0;
  }

  .knowledge-node:hover circle,
  .knowledge-node:focus circle,
  .knowledge-node.is-selected circle {
    stroke: var(--global-theme-color);
    stroke-width: 3.5;
  }

  .knowledge-node:focus {
    outline: none;
  }

  .knowledge-muted {
    opacity: 0.12;
  }

  .knowledge-highlight {
    stroke: var(--global-theme-color);
    stroke-width: 2;
  }

  .knowledge-panel {
    padding: 1.1rem;
    border-left: 1px solid var(--global-divider-color);
    background: color-mix(in srgb, var(--global-bg-color) 94%, transparent);
  }

  .knowledge-panel-kicker {
    margin-bottom: 0.35rem;
    color: var(--global-text-color-light);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .knowledge-panel h2 {
    margin: 0 0 0.65rem;
    font-size: 1.2rem;
  }

  .knowledge-panel p {
    margin-bottom: 0.9rem;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
  }

  .knowledge-panel a {
    font-weight: 600;
  }

  .knowledge-neighbors {
    margin: 1rem 0 0;
    padding: 0;
    list-style: none;
  }

  .knowledge-neighbors li {
    padding: 0.45rem 0;
    border-top: 1px solid var(--global-divider-color);
    font-size: 0.85rem;
  }

  .knowledge-relation {
    display: block;
    margin-top: 0.08rem;
    color: var(--global-text-color-light);
    font-size: 0.72rem;
  }

  .knowledge-neighbors button {
    padding: 0;
    border: 0;
    color: var(--global-text-color);
    background: transparent;
    text-align: left;
    cursor: pointer;
  }

  .knowledge-neighbors button:hover {
    color: var(--global-theme-color);
  }

  .knowledge-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem 1.2rem;
    margin-top: 0.8rem;
    color: var(--global-text-color-light);
    font-size: 0.78rem;
  }

  .knowledge-legend span::before {
    display: inline-block;
    width: 0.62rem;
    height: 0.62rem;
    margin-right: 0.35rem;
    border-radius: 50%;
    background: var(--legend-color);
    content: "";
  }

  .knowledge-relation-legend {
    gap: 0.55rem 1rem;
    margin-top: 0.35rem;
  }

  .knowledge-relation-legend span::before {
    width: 1.35rem;
    height: 0;
    border-top: 2px solid var(--relation-color, var(--global-divider-color));
    border-radius: 0;
    background: none;
  }

  .knowledge-relation-legend .is-dashed::before {
    border-top-style: dashed;
  }

  .knowledge-relation-legend .is-thick::before {
    border-top-width: 3px;
  }

  .knowledge-missing {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem 0.85rem;
    align-items: baseline;
    margin-top: 1rem;
    padding: 0.7rem 0.9rem;
    border: 1px dashed var(--global-divider-color);
    border-radius: 0.65rem;
    color: var(--global-text-color-light);
    font-size: 0.82rem;
  }

  .knowledge-missing[hidden] {
    display: none;
  }

  .knowledge-missing a {
    color: var(--global-theme-color);
  }

  .knowledge-topic-size {
    margin-left: 0.45rem;
    padding: 0 0.42rem;
    border-radius: 999px;
    color: var(--topic-color);
    background: color-mix(in srgb, var(--topic-color) 14%, transparent);
    font-size: 0.72rem;
    font-variant-numeric: tabular-nums;
    vertical-align: 0.1em;
  }

  .knowledge-directory {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
    gap: 0.8rem;
    margin-top: 2rem;
  }

  .knowledge-directory article {
    padding: 1rem;
    border: 1px solid var(--global-divider-color);
    border-top: 3px solid var(--topic-color);
    border-radius: 0.65rem;
    cursor: pointer;
    transition: border-color 160ms ease, transform 160ms ease;
  }

  .knowledge-directory article:hover {
    border-color: var(--topic-color);
    transform: translateY(-2px);
  }

  .knowledge-directory h3 {
    margin: 0 0 0.4rem;
    font-size: 1rem;
  }

  .knowledge-directory p {
    margin: 0;
    color: var(--global-text-color-light);
    font-size: 0.84rem;
  }

  .knowledge-noscript {
    padding: 1rem;
    border: 1px solid var(--global-divider-color);
    border-radius: 0.6rem;
  }

  @media (max-width: 760px) {
    .knowledge-status {
      flex-basis: 100%;
      margin-left: 0;
    }

    .knowledge-workspace {
      grid-template-columns: 1fr;
    }

    .knowledge-canvas,
    .knowledge-canvas svg {
      min-height: 29rem;
      height: 29rem;
    }

    .knowledge-panel {
      min-height: 11rem;
      border-top: 1px solid var(--global-divider-color);
      border-left: 0;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .knowledge-edge,
    .knowledge-node,
    .knowledge-node circle {
      transition: none;
    }
  }
</style>

<p class="knowledge-intro">
  这里不是标签云，而是一张手工维护的内容关系图。每条边都说明两端为什么相关：主题可以解释一篇文章，文章可以延伸或对比另一篇，项目可以是一个主题的实现。选择一个主题、点击任意节点，或者直接搜索标题。
</p>

<div class="knowledge-meta" aria-label="知识地图统计">
  <span><strong id="knowledge-topic-count">0</strong> 个主题</span>
  <span><strong id="knowledge-content-count">0</strong>/<strong id="knowledge-content-total">0</strong> 篇文章与项目</span>
  <span><strong id="knowledge-relation-count">0</strong> 条关系</span>
  <span id="knowledge-status" class="knowledge-status" role="status">选择一个主题展开内容</span>
</div>

<div class="knowledge-toolbar">
  <label class="sr-only" for="knowledge-search">搜索知识地图</label>
  <input id="knowledge-search" class="knowledge-search" type="search" placeholder="搜索主题、文章或项目…" autocomplete="off" />
  <button id="knowledge-reset" class="knowledge-reset" type="button">重置视图</button>
</div>

<div id="knowledge-filters" class="knowledge-filters" aria-label="按主题筛选"></div>

<div class="knowledge-workspace">
  <div id="knowledge-canvas" class="knowledge-canvas" role="region" aria-label="交互式知识关系图"></div>
  <aside id="knowledge-panel" class="knowledge-panel" aria-live="polite">
    <div class="knowledge-panel-kicker">使用提示</div>
    <h2>从一个节点开始</h2>
    <p>点击节点查看它的说明、连接和访问入口。拖动节点可以调整局部布局。</p>
  </aside>
</div>

<div class="knowledge-legend" aria-label="节点图例">
  <span style="--legend-color: var(--global-theme-color)">主题</span>
  <span style="--legend-color: #6f8ea8">文章</span>
  <span style="--legend-color: #d18a36">项目</span>
</div>
<div class="knowledge-legend knowledge-relation-legend" aria-label="关系图例">
  <span>解释 / 应用 / 延伸</span>
  <span class="is-thick">提供基础</span>
  <span class="is-dashed">对比 / 相关</span>
  <span class="is-dashed" style="--relation-color: #d18a36">项目实现</span>
</div>

<div id="knowledge-missing" class="knowledge-missing" hidden></div>

<section aria-labelledby="knowledge-directory-title">
  <h2 id="knowledge-directory-title" style="margin-top: 2.2rem">主题目录</h2>
  <div class="knowledge-directory">
    {% for topic in site.data.knowledge_topics %}
      {% assign topic_key = topic.id | prepend: "topic:" %}
      {% assign topic_size = 0 %}
      {% for relation in site.data.knowledge_relations %}
        {% if relation.source == topic_key or relation.target == topic_key %} {% assign topic_size = topic_size | plus: 1 %} {% endif %}
      {% endfor %}
      <article style="--topic-color: {{ topic.color }}" data-topic-id="topic:{{ topic.id }}" tabindex="0" role="button" aria-label="在图中查看{{ topic.name }}">
        <h3>{{ topic.name }}<span class="knowledge-topic-size" title="指向该主题的关系数">{{ topic_size }}</span></h3>
        <p>{{ topic.description }}</p>
      </article>
    {% endfor %}
  </div>
</section>

<noscript>
  <p class="knowledge-noscript">交互式关系图需要 JavaScript；你仍然可以通过上方主题目录了解本站的知识结构。</p>
</noscript>

<script>
  (() => {
    const topics = {{ site.data.knowledge_topics | jsonify }};
    const relations = {{ site.data.knowledge_relations | jsonify }};
    const content = [
      {% for post in site.posts %}
        {
          id: {{ post.slug | prepend: "post:" | jsonify }},
          kind: "post",
          name: {{ post.title | jsonify }},
          description: {{ post.description | default: post.excerpt | strip_html | strip_newlines | truncate: 150 | jsonify }},
          url: {{ post.url | relative_url | jsonify }}
        },
      {% endfor %}
      {% for project in site.projects %}
        {
          id: {{ project.slug | prepend: "project:" | jsonify }},
          kind: "project",
          name: {{ project.title | jsonify }},
          description: {{ project.description | default: project.excerpt | strip_html | strip_newlines | truncate: 150 | jsonify }},
          url: {{ project.url | relative_url | jsonify }}
        }{% unless forloop.last %},{% endunless %}
      {% endfor %}
    ];

    const topicNodes = topics.map((topic) => ({
      ...topic,
      id: `topic:${topic.id}`,
      kind: "topic",
      radius: 12
    }));
    const available = new Map([...topicNodes, ...content].map((node) => [node.id, node]));
    const links = relations.filter((link) => available.has(link.source) && available.has(link.target));
    const usedIds = new Set(links.flatMap((link) => [link.source, link.target]));
    const nodes = [...available.values()].filter((node) => usedIds.has(node.id)).map((node) => ({
      ...node,
      radius: node.radius || (node.kind === "project" ? 8 : 6)
    }));
    const nodeById = new Map(nodes.map((node) => [node.id, node]));
    const neighbors = new Map(nodes.map((node) => [node.id, new Set()]));
    links.forEach((link) => {
      neighbors.get(link.source).add(link.target);
      neighbors.get(link.target).add(link.source);
    });
    // Topics never link to each other, so the overview carries their weight in
    // the circle instead: a bigger dot means more content hangs off it.
    nodes.forEach((node) => {
      if (node.kind === "topic") {
        node.radius = 9 + Math.min(11, neighbors.get(node.id).size);
      }
    });

    const canvas = document.getElementById("knowledge-canvas");
    const panel = document.getElementById("knowledge-panel");
    const filters = document.getElementById("knowledge-filters");
    const search = document.getElementById("knowledge-search");
    const reset = document.getElementById("knowledge-reset");
    const status = document.getElementById("knowledge-status");
    const svgNS = "http://www.w3.org/2000/svg";
    let selectedId = null;
    let activeTopic = null;
    let width = 0;
    let height = 0;
    let raf = 0;
    let drag = null;
    let hoveredId = null;

    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("aria-label", `${topicNodes.length} 个主题组成的知识关系图`);
    const defs = document.createElementNS(svgNS, "defs");
    const arrow = document.createElementNS(svgNS, "marker");
    const arrowPath = document.createElementNS(svgNS, "path");
    arrow.id = "knowledge-arrow";
    arrow.setAttribute("viewBox", "0 0 10 10");
    arrow.setAttribute("refX", "9");
    arrow.setAttribute("refY", "5");
    arrow.setAttribute("markerWidth", "5");
    arrow.setAttribute("markerHeight", "5");
    arrow.setAttribute("orient", "auto-start-reverse");
    arrowPath.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
    arrowPath.setAttribute("fill", "context-stroke");
    arrow.append(arrowPath);
    defs.append(arrow);
    const viewport = document.createElementNS(svgNS, "g");
    const edgeLayer = document.createElementNS(svgNS, "g");
    const nodeLayer = document.createElementNS(svgNS, "g");
    viewport.append(edgeLayer, nodeLayer);
    svg.append(defs, viewport);
    canvas.append(svg);

    const controls = document.createElement("div");
    controls.className = "knowledge-canvas-controls";
    controls.setAttribute("aria-label", "图谱缩放控制");
    controls.innerHTML = `
      <button type="button" data-zoom="in" aria-label="放大图谱" title="放大">＋</button>
      <button type="button" data-zoom="out" aria-label="缩小图谱" title="缩小">−</button>
      <button type="button" data-zoom="reset" aria-label="返回知识地图总览" title="返回总览">⌂</button>`;
    canvas.append(controls);

    const view = { x: 0, y: 0, scale: 1 };
    let pan = null;

    function renderViewport() {
      viewport.setAttribute("transform", `translate(${view.x} ${view.y}) scale(${view.scale})`);
    }

    function resetViewport() {
      view.x = 0;
      view.y = 0;
      view.scale = 1;
      renderViewport();
    }

    function zoomAt(factor, clientX, clientY) {
      const rect = svg.getBoundingClientRect();
      const pointX = ((clientX ?? rect.left + rect.width / 2) - rect.left) * (width / rect.width);
      const pointY = ((clientY ?? rect.top + rect.height / 2) - rect.top) * (height / rect.height);
      const nextScale = Math.max(0.65, Math.min(2.5, view.scale * factor));
      const ratio = nextScale / view.scale;
      view.x = pointX - (pointX - view.x) * ratio;
      view.y = pointY - (pointY - view.y) * ratio;
      view.scale = nextScale;
      renderViewport();
    }

    const colorFor = (node) => node.kind === "topic" ? node.color : node.kind === "project" ? "#d18a36" : "#6f8ea8";
    const kindName = { topic: "主题", post: "文章", project: "项目" };
    const relationName = {
      explains: "解释",
      grounds: "提供基础",
      applies: "应用",
      compares_with: "对比",
      extends: "延伸",
      related_to: "相关",
      implemented_by: "由项目实现"
    };

    const edgeEls = links.map((link) => {
      const line = document.createElementNS(svgNS, "line");
      const title = document.createElementNS(svgNS, "title");
      line.classList.add("knowledge-edge", `is-${link.type}`);
      line.dataset.source = link.source;
      line.dataset.target = link.target;
      title.textContent = relationName[link.type] || "相关";
      line.append(title);
      edgeLayer.append(line);
      return { link, line };
    });

    const nodeEls = nodes.map((node) => {
      const group = document.createElementNS(svgNS, "g");
      const circle = document.createElementNS(svgNS, "circle");
      const label = document.createElementNS(svgNS, "text");
      group.classList.add("knowledge-node", `is-${node.kind}`);
      group.setAttribute("tabindex", "0");
      group.setAttribute("role", "button");
      group.setAttribute("aria-label", `${kindName[node.kind]}：${node.name}`);
      group.append(document.createElementNS(svgNS, "title"));
      group.querySelector("title").textContent = node.name;
      group.dataset.id = node.id;
      circle.setAttribute("r", node.radius);
      circle.setAttribute("fill", colorFor(node));
      label.setAttribute("x", node.radius + 4);
      label.setAttribute("y", "4");
      label.textContent = node.name.length > 18 ? `${node.name.slice(0, 18)}…` : node.name;
      group.append(circle, label);
      // The layout needs the rendered label width, not only the circle radius.
      // A conservative fallback keeps the first layout stable while fonts load.
      node.labelWidth = Math.max(24, label.textContent.length * (node.kind === "topic" ? 12 : 11));
      group.addEventListener("click", () => selectNode(node.id));
      group.addEventListener("pointerenter", () => {
        hoveredId = node.id;
        applyVisibility();
      });
      group.addEventListener("pointerleave", () => {
        hoveredId = null;
        applyVisibility();
      });
      group.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectNode(node.id);
        }
      });
      group.addEventListener("pointerdown", (event) => {
        drag = { node, pointerId: event.pointerId };
        group.setPointerCapture(event.pointerId);
      });
      group.addEventListener("pointermove", (event) => {
        if (!drag || drag.pointerId !== event.pointerId) return;
        const point = svg.createSVGPoint();
        point.x = event.clientX;
        point.y = event.clientY;
        const local = point.matrixTransform(viewport.getScreenCTM().inverse());
        node.x = local.x;
        node.y = local.y;
        node.fixed = true;
        draw();
      });
      group.addEventListener("pointerup", () => { drag = null; });
      nodeLayer.append(group);
      return { node, group };
    });

    requestAnimationFrame(() => {
      nodeEls.forEach(({ node, group }) => {
        const label = group.querySelector("text");
        node.labelWidth = Math.ceil(label.getComputedTextLength()) || node.labelWidth;
      });
      layout();
    });

    topics.forEach((topic) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "knowledge-chip";
      button.textContent = topic.name;
      button.dataset.id = `topic:${topic.id}`;
      button.style.setProperty("--chip-color", topic.color);
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => {
        activeTopic = activeTopic === button.dataset.id ? null : button.dataset.id;
        filters.querySelectorAll("button").forEach((item) => item.setAttribute("aria-pressed", String(item.dataset.id === activeTopic)));
        if (activeTopic) selectNode(activeTopic);
        else clearSelection();
        applyVisibility();
      });
      filters.append(button);
    });

    function connectedSet(id) {
      if (!id) return null;
      return new Set([id, ...(neighbors.get(id) || [])]);
    }

    function selectNode(id) {
      selectedId = id;
      const node = nodeById.get(id);
      const adjacent = [...(neighbors.get(id) || [])]
        .map((neighborId) => {
          const item = nodeById.get(neighborId);
          const relation = links.find((link) => (link.source === id && link.target === neighborId) || (link.target === id && link.source === neighborId));
          return item ? { ...item, relation: relationName[relation?.type] || "相关" } : null;
        })
        .filter(Boolean)
        .sort((a, b) => a.kind.localeCompare(b.kind) || a.name.localeCompare(b.name, "zh-CN"));
      panel.innerHTML = `
        <div class="knowledge-panel-kicker">${kindName[node.kind]}</div>
        <h2>${escapeHtml(node.name)}</h2>
        <p>${escapeHtml(node.description || "这是知识地图中的一个连接点。")}</p>
        ${node.url ? `<a href="${node.url}">打开${kindName[node.kind]} →</a>` : ""}
        <ul class="knowledge-neighbors" aria-label="相邻节点">
          ${adjacent.map((item) => `<li><button type="button" data-node-id="${item.id}">${escapeHtml(item.name)}<span class="knowledge-relation">${escapeHtml(item.relation)}</span></button></li>`).join("")}
        </ul>`;
      panel.querySelectorAll("[data-node-id]").forEach((button) => button.addEventListener("click", () => selectNode(button.dataset.nodeId)));
      applyVisibility();
      requestAnimationFrame(() => layout());
    }

    function clearSelection({ relayout = true } = {}) {
      selectedId = null;
      panel.innerHTML = '<div class="knowledge-panel-kicker">使用提示</div><h2>从一个节点开始</h2><p>点击节点查看它的说明、连接和访问入口。拖动节点可以调整局部布局。</p>';
      applyVisibility();
      if (relayout) requestAnimationFrame(() => layout());
    }

    function applyVisibility() {
      const term = search.value.trim().toLocaleLowerCase();
      const focus = connectedSet(activeTopic || selectedId);
      const matches = new Set(nodes.filter((node) => !term || `${node.name} ${node.description || ""}`.toLocaleLowerCase().includes(term)).map((node) => node.id));
      const searchContext = new Set(matches);
      if (term) matches.forEach((id) => (neighbors.get(id) || []).forEach((neighborId) => searchContext.add(neighborId)));
      let visibleCount = 0;
      nodeEls.forEach(({ node, group }) => {
        const inOverview = !focus && !term;
        const visible = (inOverview ? node.kind === "topic" : (!focus || focus.has(node.id)) && (!term || searchContext.has(node.id)));
        if (visible) visibleCount += 1;
        group.classList.toggle("is-hidden", !visible);
        group.classList.toggle("show-label", node.kind === "topic" || node.id === selectedId || node.id === hoveredId || (visible && Boolean(focus)) || (term && matches.has(node.id)));
        group.classList.toggle("is-selected", node.id === selectedId);
      });
      edgeEls.forEach(({ link, line }) => {
        const highlighted = selectedId && (link.source === selectedId || link.target === selectedId);
        const hovered = hoveredId && (link.source === hoveredId || link.target === hoveredId);
        const inOverview = !focus && !term;
        const visible = !inOverview && (!focus || (focus.has(link.source) && focus.has(link.target))) && (!term || (searchContext.has(link.source) && searchContext.has(link.target)));
        line.classList.toggle("is-hidden", !visible);
        line.classList.toggle("knowledge-highlight", highlighted || hovered);
      });
      if (term) status.textContent = `找到 ${matches.size} 个结果，显示 ${visibleCount} 个相关节点`;
      else if (activeTopic) status.textContent = `正在查看 ${nodeById.get(activeTopic).name}`;
      else if (selectedId) status.textContent = `正在查看 ${nodeById.get(selectedId).name} 的相邻关系`;
      else status.textContent = "选择一个主题展开内容";
    }

    function visibleNodes() {
      return nodeEls.filter(({ group }) => !group.classList.contains("is-hidden")).map(({ node }) => node);
    }

    function escapeHtml(value) {
      const span = document.createElement("span");
      span.textContent = value;
      return span.innerHTML;
    }

    function initializePositions(layoutNodes) {
      const cx = width / 2;
      const cy = height / 2;
      const focusId = activeTopic || selectedId;
      const focusNode = focusId && layoutNodes.find((node) => node.id === focusId);
      const ordered = [...layoutNodes].sort((a, b) => a.id.localeCompare(b.id));

      if (focusNode) {
        focusNode.x = cx;
        focusNode.y = cy;
        focusNode.anchorX = cx;
        focusNode.anchorY = cy;
        focusNode.fixed = true;
        const satellites = ordered.filter((node) => node.id !== focusId);
        const ringRadius = Math.min(width * 0.3, height * 0.34, 210);
        satellites.forEach((node, index) => {
          const angle = (Math.PI * 2 * index) / Math.max(satellites.length, 1) - Math.PI / 2;
          node.x = cx + Math.cos(angle) * ringRadius;
          node.y = cy + Math.sin(angle) * ringRadius;
          node.anchorX = node.x;
          node.anchorY = node.y;
        });
        return;
      }

      const radiusX = Math.min(width * 0.34, 300);
      const radiusY = Math.min(height * 0.31, 205);
      ordered.forEach((node, index) => {
        const angle = (Math.PI * 2 * index) / Math.max(ordered.length, 1) - Math.PI / 2;
        node.x = cx + Math.cos(angle) * radiusX;
        node.y = cy + Math.sin(angle) * radiusY;
        node.anchorX = node.x;
        node.anchorY = node.y;
      });
    }

    function labelBounds(node) {
      return {
        left: node.x - node.radius - 3,
        right: node.x + node.radius + 5 + node.labelWidth,
        top: node.y - Math.max(node.radius, 9) - 3,
        bottom: node.y + Math.max(node.radius, 9) + 3
      };
    }

    function boundaryForce(node) {
      const leftExtent = node.radius + 8;
      const rightExtent = node.radius + 9 + node.labelWidth;
      const topExtent = node.radius + 12;
      const bottomExtent = node.radius + 12;
      let fx = 0;
      let fy = 0;
      if (node.x < leftExtent) fx += (leftExtent - node.x) * 0.12;
      if (node.x > width - rightExtent) fx -= (node.x - (width - rightExtent)) * 0.12;
      if (node.y < topExtent) fy += (topExtent - node.y) * 0.12;
      if (node.y > height - bottomExtent) fy -= (node.y - (height - bottomExtent)) * 0.12;
      return { fx, fy };
    }

    function settle(layoutNodes) {
      const layoutIds = new Set(layoutNodes.map((node) => node.id));
      const layoutLinks = links.filter((link) => layoutIds.has(link.source) && layoutIds.has(link.target));
      for (let iteration = 0; iteration < 140; iteration += 1) {
        layoutNodes.forEach((a, i) => {
          if (a.fixed) return;
          let fx = 0;
          let fy = 0;
          for (let j = i + 1; j < layoutNodes.length; j += 1) {
            const b = layoutNodes[j];
            const dx = a.x - b.x || 0.1;
            const dy = a.y - b.y || 0.1;
            const distance2 = Math.max(dx * dx + dy * dy, 100);
            const force = 260 / distance2;
            fx += dx * force;
            fy += dy * force;
            if (!b.fixed) {
              b.x -= dx * force;
              b.y -= dy * force;
            }

            // Resolve overlapping label rectangles. Moving along the smaller
            // overlap preserves clusters while preventing rows of stacked text.
            const boxA = labelBounds(a);
            const boxB = labelBounds(b);
            const overlapX = Math.min(boxA.right, boxB.right) - Math.max(boxA.left, boxB.left);
            const overlapY = Math.min(boxA.bottom, boxB.bottom) - Math.max(boxA.top, boxB.top);
            if (overlapX > 0 && overlapY > 0) {
              if (overlapY <= overlapX) {
                const push = (overlapY + 4) * 0.22 * (a.y <= b.y ? -1 : 1);
                fy += push;
                if (!b.fixed) b.y -= push;
              } else {
                const push = (overlapX + 6) * 0.12 * (a.x <= b.x ? -1 : 1);
                fx += push;
                if (!b.fixed) b.x -= push;
              }
            }
          }
          layoutLinks.forEach((link) => {
            let other;
            if (link.source === a.id) other = nodeById.get(link.target);
            if (link.target === a.id) other = nodeById.get(link.source);
            if (!other) return;
            const dx = other.x - a.x;
            const dy = other.y - a.y;
            const distance = Math.max(Math.hypot(dx, dy), 1);
            const desired = a.kind === "topic" || other.kind === "topic" ? 72 : 92;
            const pull = (distance - desired) * 0.006;
            fx += (dx / distance) * pull;
            fy += (dy / distance) * pull;
          });
          fx += (a.anchorX - a.x) * 0.035;
          fy += (a.anchorY - a.y) * 0.035;
          const boundary = boundaryForce(a);
          fx += boundary.fx;
          fy += boundary.fy;
          const maxStep = 7;
          a.x += Math.max(-maxStep, Math.min(maxStep, fx));
          a.y += Math.max(-maxStep, Math.min(maxStep, fy));
        });
      }
      draw();
    }

    function fitViewport(layoutNodes) {
      if (!layoutNodes.length) return resetViewport();
      const bounds = layoutNodes.map(labelBounds);
      const left = Math.min(...bounds.map((box) => box.left));
      const right = Math.max(...bounds.map((box) => box.right));
      const top = Math.min(...bounds.map((box) => box.top));
      const bottom = Math.max(...bounds.map((box) => box.bottom));
      const padding = 38;
      const contentWidth = Math.max(1, right - left);
      const contentHeight = Math.max(1, bottom - top);
      view.scale = Math.max(0.65, Math.min(1.35, (width - padding * 2) / contentWidth, (height - padding * 2) / contentHeight));
      view.x = width / 2 - ((left + right) / 2) * view.scale;
      view.y = height / 2 - ((top + bottom) / 2) * view.scale;
      renderViewport();
    }

    function draw() {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        edgeEls.forEach(({ link, line }) => {
          const source = nodeById.get(link.source);
          const target = nodeById.get(link.target);
          line.setAttribute("x1", source.x);
          line.setAttribute("y1", source.y);
          line.setAttribute("x2", target.x);
          line.setAttribute("y2", target.y);
        });
        nodeEls.forEach(({ node, group }) => group.setAttribute("transform", `translate(${node.x},${node.y})`));
      });
    }

    function layout({ fit = true } = {}) {
      const bounds = canvas.getBoundingClientRect();
      width = Math.max(320, Math.round(bounds.width));
      height = Math.round(svg.getBoundingClientRect().height) || 544;
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
      nodes.forEach((node) => { node.fixed = false; });
      const layoutNodes = visibleNodes();
      initializePositions(layoutNodes);
      // A focused view represents one-hop adjacency, not relationship weight.
      // Keep every neighbor on the same ring so line length cannot imply
      // stronger or weaker relationships.
      if (activeTopic || selectedId) draw();
      else settle(layoutNodes);
      if (fit) fitViewport(layoutNodes);
    }

    let searchTimer = 0;
    search.addEventListener("input", () => {
      applyVisibility();
      clearTimeout(searchTimer);
      searchTimer = setTimeout(layout, 80);
    });

    function resetKnowledgeView() {
      search.value = "";
      activeTopic = null;
      selectedId = null;
      filters.querySelectorAll("button").forEach((button) => button.setAttribute("aria-pressed", "false"));
      clearSelection({ relayout: false });
      resetViewport();
      layout();
    }

    svg.addEventListener("wheel", (event) => {
      event.preventDefault();
      zoomAt(event.deltaY < 0 ? 1.12 : 1 / 1.12, event.clientX, event.clientY);
    }, { passive: false });
    svg.addEventListener("pointerdown", (event) => {
      if (event.target !== svg) return;
      pan = { pointerId: event.pointerId, clientX: event.clientX, clientY: event.clientY, x: view.x, y: view.y };
      svg.setPointerCapture(event.pointerId);
    });
    svg.addEventListener("pointermove", (event) => {
      if (!pan || pan.pointerId !== event.pointerId) return;
      const rect = svg.getBoundingClientRect();
      view.x = pan.x + (event.clientX - pan.clientX) * (width / rect.width);
      view.y = pan.y + (event.clientY - pan.clientY) * (height / rect.height);
      renderViewport();
    });
    svg.addEventListener("pointerup", () => { pan = null; });
    svg.addEventListener("pointercancel", () => { pan = null; });
    svg.addEventListener("dblclick", resetViewport);
    controls.addEventListener("click", (event) => {
      const action = event.target.closest("button")?.dataset.zoom;
      if (action === "in") zoomAt(1.2);
      if (action === "out") zoomAt(1 / 1.2);
    });
    controls.querySelector('[data-zoom="reset"]').addEventListener("click", resetKnowledgeView);
    reset.addEventListener("click", resetKnowledgeView);

    const resizeObserver = new ResizeObserver(() => {
      clearTimeout(resizeObserver.timer);
      resizeObserver.timer = setTimeout(layout, 120);
    });
    resizeObserver.observe(canvas);
    document.getElementById("knowledge-topic-count").textContent = topicNodes.length;
    document.getElementById("knowledge-content-count").textContent = nodes.filter((node) => node.kind !== "topic").length;
    document.getElementById("knowledge-content-total").textContent = content.length;
    document.getElementById("knowledge-relation-count").textContent = links.length;

    // A post with no relation never reaches the graph, so surface it instead of
    // letting it disappear: a new post is visible here until it is mapped.
    const missing = content.filter((item) => !usedIds.has(item.id));
    const missingBox = document.getElementById("knowledge-missing");
    if (missing.length) {
      missingBox.hidden = false;
      missingBox.append(document.createTextNode(`尚未纳入关系图（${missing.length}）：`));
      missing.forEach((item) => {
        const link = document.createElement("a");
        link.href = item.url;
        link.textContent = item.name;
        missingBox.append(link);
      });
    }
    document.querySelectorAll("[data-topic-id]").forEach((card) => {
      const activate = () => {
        const button = filters.querySelector(`[data-id="${card.dataset.topicId}"]`);
        button?.click();
        canvas.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
      };
      card.addEventListener("click", activate);
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          activate();
        }
      });
    });
    applyVisibility();
    layout();
  })();
</script>
