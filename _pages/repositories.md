---
layout: page
permalink: /repositories/
title: 全部仓库
description: GitHub 上的全部公开仓库，按语言分组、按最近推送排序。
nav: true
nav_order: 5
_styles: |
  /* 该页专属样式：仓库卡片、方向分组、概览条。
     主题 v1 未提供 Bootstrap 兼容层（compat.bootstrap.enabled=false），
     因此这里只依赖主题自身的 CSS 变量，暗色模式自动跟随。 */
  .rp {
    /* 次要文字用自定义灰度：主题的 --global-text-color-light（#828282）
       在浅色/深色背景上的对比度都低于 WCAG AA 的 4.5:1。 */
    --rp-muted: #6b6b6b;
  }
  html[data-theme="dark"] .rp {
    --rp-muted: #a8a8a8;
  }
  .rp-stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 0 0 2.4rem;
  }
  .rp-stat {
    padding: 1.05rem 0.6rem;
    text-align: center;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 0.5rem;
  }
  .rp-stat-num {
    display: block;
    font-size: 1.55rem;
    font-weight: 500;
    line-height: 1.2;
  }
  .rp-stat-label {
    display: block;
    margin-top: 0.2rem;
    font-size: 0.78rem;
    color: var(--rp-muted);
  }
  .rp-hint {
    margin: 0 0 0.9rem;
    font-size: 0.86rem;
    color: var(--rp-muted);
  }
  .rp-dot {
    display: inline-block;
    flex: 0 0 auto;
    width: 0.6rem;
    height: 0.6rem;
    border-radius: 50%;
  }
  .rp-group {
    margin: 0 0 0.9rem;
    overflow: hidden;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 0.5rem;
  }
  .rp-summary {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.8rem 1rem;
    font-weight: 500;
    cursor: pointer;
    list-style: none;
  }
  .rp-summary::-webkit-details-marker {
    display: none;
  }
  .rp-summary:hover {
    background: color-mix(in srgb, var(--global-theme-color) 7%, transparent);
  }
  .rp-count {
    margin-left: auto;
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--rp-muted);
  }
  .rp-chevron {
    font-size: 0.7rem;
    color: var(--rp-muted);
    transition: transform 0.18s ease;
  }
  .rp-group[open] .rp-chevron {
    transform: rotate(180deg);
  }
  .rp-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.1rem 1rem;
    padding: 0.2rem 0.7rem 0.85rem;
  }
  .rp-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.45rem 0.4rem;
    color: var(--global-text-color);
    text-decoration: none;
    border-radius: 0.35rem;
  }
  .rp-item:hover {
    background: color-mix(in srgb, var(--global-theme-color) 8%, transparent);
    text-decoration: none;
  }
  .rp-item-body {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .rp-item-title {
    display: flex;
    align-items: baseline;
    gap: 0.45rem;
    min-width: 0;
  }
  .rp-item-name {
    font-size: 0.92rem;
    font-weight: 500;
    line-height: 1.35;
    overflow-wrap: anywhere;
  }
  .rp-item-desc {
    font-size: 0.78rem;
    line-height: 1.4;
    color: var(--rp-muted);
  }
  .rp-item-lang {
    font-size: 0.7rem;
    white-space: nowrap;
    color: var(--rp-muted);
  }
  .rp-item-date {
    margin-left: auto;
    padding-left: 0.6rem;
    font-size: 0.7rem;
    white-space: nowrap;
    color: var(--rp-muted);
  }
  @media (max-width: 575.98px) {
    .rp-stats {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
---

{% assign github_data = site.data.github_repositories %}
{% assign languages = site.data.repositories.languages %}
{% assign groups = github_data.repositories | group_by: "language" | sort: "size" | reverse %}

<div class="rp">

  <div class="rp-stats">
    <div class="rp-stat">
      <span class="rp-stat-num">{{ github_data.total }}</span>
      <span class="rp-stat-label">公开仓库</span>
    </div>
    <div class="rp-stat">
      <span class="rp-stat-num">{{ github_data.original_count }}</span>
      <span class="rp-stat-label">原创仓库</span>
    </div>
    <div class="rp-stat">
      <span class="rp-stat-num">{{ github_data.fork_count }}</span>
      <span class="rp-stat-label">Fork 仓库</span>
    </div>
    <div class="rp-stat">
      <span class="rp-stat-num">{{ groups | size }}</span>
      <span class="rp-stat-label">语言</span>
    </div>
  </div>

  <p class="rp-hint">
    按语言分组、数量多的在前，组内按最近推送排序。快照同步于 {{ github_data.generated_at | date: "%Y-%m-%d" }}，精选项目与详情见
    <a href="{{ '/projects/' | relative_url }}">项目</a>。
  </p>

{% for group in groups %}
    {% assign color = languages[group.name] | default: "#8b949e" %}
    <details class="rp-group"{% if forloop.index <= 3 %} open{% endif %}>
      <summary class="rp-summary">
        <span class="rp-dot" style="background: {{ color }}"></span>
        <span>{{ group.name }}</span>
        <span class="rp-count">{{ group.items | size }} 个</span>
        <i class="fa-solid fa-chevron-down rp-chevron" aria-hidden="true"></i>
      </summary>
      <div class="rp-items">
        {% for repo in group.items %}
          <a class="rp-item" href="{{ repo.url }}">
            <span class="rp-item-body">
              <span class="rp-item-title">
                <span class="rp-item-name">{{ repo.name }}</span>
                {% if repo.fork %}<span class="rp-item-lang">Fork</span>{% endif %}
                {% if repo.archived %}<span class="rp-item-lang">已归档</span>{% endif %}
              </span>
              {% if repo.description != blank %}<span class="rp-item-desc">{{ repo.description }}</span>{% endif %}
            </span>
            <span class="rp-item-date">{{ repo.pushed_at | date: "%Y-%m" }}</span>
          </a>
        {% endfor %}
      </div>
    </details>
{% endfor %}

</div>
