---
layout: page
permalink: /repositories/
title: 开源仓库
description: 从 AI 智能体到工程工具，持续构建有趣且实用的软件。
nav: true
nav_order: 4
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
  .rp h2 {
    margin: 2.1rem 0 0.9rem;
    font-size: 1.35rem;
  }
  .rp h2:first-child {
    margin-top: 0;
  }
  .rp-hint {
    margin: 0 0 0.9rem;
    font-size: 0.86rem;
    color: var(--rp-muted);
  }
  .rp-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }
  .rp-card {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    height: 100%;
    padding: 1rem 1.1rem 1.05rem;
    color: var(--global-text-color);
    text-decoration: none;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 0.5rem;
    transition:
      transform 0.18s ease,
      box-shadow 0.18s ease,
      border-color 0.18s ease;
  }
  .rp-card:hover {
    transform: translateY(-2px);
    border-color: var(--global-theme-color);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
    text-decoration: none;
  }
  .rp-card-head {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .rp-card-name {
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.3;
    overflow-wrap: anywhere;
  }
  .rp-card-arrow {
    margin-left: auto;
    font-size: 0.72rem;
    opacity: 0.35;
    transition: opacity 0.18s ease;
  }
  .rp-card:hover .rp-card-arrow {
    opacity: 1;
  }
  .rp-card-desc {
    flex: 1;
    margin: 0;
    font-size: 0.86rem;
    line-height: 1.55;
    color: var(--rp-muted);
  }
  .rp-dot {
    display: inline-block;
    flex: 0 0 auto;
    width: 0.6rem;
    height: 0.6rem;
    border-radius: 50%;
  }
  .rp-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.1rem;
  }
  .rp-tag {
    padding: 0.28rem 0.55rem;
    font-size: 0.7rem;
    line-height: 1.1;
    border-radius: 999px;
    background: color-mix(in srgb, var(--global-theme-color) 14%, transparent);
    color: var(--global-text-color);
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
  .rp-cta {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.6rem 1.15rem;
    font-size: 0.9rem;
    color: var(--global-hover-text-color);
    text-decoration: none;
    background: var(--global-theme-color);
    border-radius: 0.35rem;
  }
  .rp-cta:hover {
    color: var(--global-hover-text-color);
    background: var(--global-hover-color);
    text-decoration: none;
  }
  @media (max-width: 575.98px) {
    .rp-stats {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .rp-grid {
      grid-template-columns: 1fr;
    }
  }
---

{% assign repos = site.data.repositories.repos %}
{% assign owner = site.data.repositories.github_users | first %}
{% assign featured = repos | where: "featured", true %}
{% assign langs = repos | map: "lang" | uniq %}
{% assign cats = site.data.repositories.categories %}

<div class="rp">

  <div class="rp-stats">
    <div class="rp-stat">
      <span class="rp-stat-num">{{ repos | size }}</span>
      <span class="rp-stat-label">公开项目</span>
    </div>
    <div class="rp-stat">
      <span class="rp-stat-num">{{ featured | size }}</span>
      <span class="rp-stat-label">重点项目</span>
    </div>
    <div class="rp-stat">
      <span class="rp-stat-num">{{ langs | size }}</span>
      <span class="rp-stat-label">主要语言</span>
    </div>
    <div class="rp-stat">
      <span class="rp-stat-num">{{ cats | size }}</span>
      <span class="rp-stat-label">探索方向</span>
    </div>
  </div>

  <h2>重点项目</h2>

  <div class="rp-grid">
    {% for cat in cats %}
      {% assign cat_featured = repos | where: "category", cat.id | where: "featured", true %}
      {% for r in cat_featured %}
        {% assign color = site.data.repositories.languages[r.lang] | default: "#8b949e" %}
        <a class="rp-card" href="https://github.com/{{ owner }}/{{ r.name }}">
          <span class="rp-card-head">
            <span class="rp-dot" style="background: {{ color }}"></span>
            <span class="rp-card-name">{{ r.title | default: r.name }}</span>
            <i class="fa-solid fa-arrow-up-right-from-square rp-card-arrow"></i>
          </span>
          <p class="rp-card-desc">{{ r.desc }}</p>
          <span class="rp-tags">
            <span class="rp-tag">{{ r.lang }}</span>
          </span>
        </a>
      {% endfor %}
    {% endfor %}
  </div>

  <h2>更多探索</h2>

  <p class="rp-hint">按方向浏览全部公开项目，点击分类展开。</p>

{% for cat in cats %}
    {% assign cat_repos = repos | where: "category", cat.id | where_exp: "r", "r.featured != true" %}
    <details class="rp-group" {% if forloop.first %}open{% endif %}>
      <summary class="rp-summary">
        <span>{{ cat.name }}</span>
        <span class="rp-count">{{ cat_repos | size }} 个项目</span>
        <i class="fa-solid fa-chevron-down rp-chevron"></i>
      </summary>
      <div class="rp-items">
        {% for r in cat_repos %}
          {% assign color = site.data.repositories.languages[r.lang] | default: "#8b949e" %}
          <a class="rp-item" href="https://github.com/{{ owner }}/{{ r.name }}">
            <span class="rp-dot" style="background: {{ color }}"></span>
            <span class="rp-item-body">
              <span class="rp-item-title">
                <span class="rp-item-name">{{ r.title | default: r.name }}</span>
                <span class="rp-item-lang">{{ r.lang }}</span>
              </span>
              <span class="rp-item-desc">{{ r.desc }}</span>
            </span>
          </a>
        {% endfor %}
      </div>
    </details>
{% endfor %}

  <div class="text-center">
    <a class="rp-cta" href="https://github.com/{{ owner }}?tab=repositories">
      浏览全部公开仓库 <i class="fa-solid fa-arrow-up-right-from-square fa-sm"></i>
    </a>
  </div>

</div>
