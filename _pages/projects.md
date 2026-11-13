---
layout: page
title: 项目
permalink: /projects/
description: 持续维护的项目，每个都有详情页与源码入口。
nav: true
nav_order: 4
_styles: |
  .all-projects-summary {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    margin: 1.5rem 0 2rem;
  }
  .all-projects-stat {
    padding: 1rem;
    text-align: center;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 0.5rem;
  }
  .all-projects-stat strong,
  .all-projects-stat span {
    display: block;
  }
  .all-projects-stat strong {
    font-size: 1.5rem;
    font-weight: 500;
  }
  .all-projects-stat span {
    margin-top: 0.2rem;
    color: var(--global-text-color-light);
    font-size: 0.78rem;
  }
  .all-projects-meta {
    margin-bottom: 1rem;
    color: var(--global-text-color-light);
    font-size: 0.82rem;
  }
  .all-projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
  }
  .all-project-card {
    display: flex;
    flex-direction: column;
    min-height: 190px;
    padding: 1rem 1.1rem;
    color: var(--global-text-color);
    text-decoration: none;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 0.5rem;
    transition:
      transform 0.18s ease,
      border-color 0.18s ease,
      box-shadow 0.18s ease;
  }
  .all-project-card:hover {
    color: var(--global-text-color);
    text-decoration: none;
    transform: translateY(-2px);
    border-color: var(--global-theme-color);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  }
  .all-project-head {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .all-project-name {
    min-width: 0;
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.35;
    overflow-wrap: anywhere;
  }
  .all-project-arrow {
    margin-left: auto;
    padding-top: 0.25rem;
    font-size: 0.7rem;
    opacity: 0.4;
  }
  .all-project-desc {
    flex: 1;
    margin: 0.65rem 0;
    color: var(--global-text-color-light);
    font-size: 0.84rem;
    line-height: 1.55;
  }
  .all-project-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    align-items: center;
    font-size: 0.7rem;
  }
  .all-project-tag {
    padding: 0.24rem 0.5rem;
    background: color-mix(in srgb, var(--global-theme-color) 14%, transparent);
    border-radius: 999px;
  }
  @media (max-width: 575.98px) {
    .all-projects-summary {
      grid-template-columns: 1fr;
    }
    .all-projects-grid {
      grid-template-columns: 1fr;
    }
  }
---

{% assign github_data = site.data.github_repositories %}
{% assign projects = site.projects | sort: "importance" %}

<div class="all-projects-summary">
  <div class="all-projects-stat">
    <strong>{{ projects | size }}</strong>
    <span>精选项目</span>
  </div>
  <div class="all-projects-stat">
    <strong>{{ github_data.total }}</strong>
    <span>公开仓库</span>
  </div>
  <div class="all-projects-stat">
    <strong>{{ github_data.original_count }}</strong>
    <span>原创仓库</span>
  </div>
</div>

<p class="all-projects-meta">
  这里只放持续维护、能跑起来的项目，按重要度排序；完整仓库清单（含实验与 Fork）见
  <a href="{{ '/repositories/' | relative_url }}">全部仓库</a>。
</p>

<div class="all-projects-grid">
  {% for project in projects %}
    <a class="all-project-card" href="{{ project.url | relative_url }}">
      <span class="all-project-head">
        <span class="all-project-name">{{ project.title }}</span>
        <i class="fa-solid fa-arrow-up-right-from-square all-project-arrow"></i>
      </span>
      <span class="all-project-desc">{{ project.description }}</span>
      <span class="all-project-tags">
        <span class="all-project-tag">{{ project.category }}</span>
      </span>
    </a>
  {% endfor %}
</div>
