---
layout: page
title: 动态
permalink: /news/
description: 项目进展、版本发布与站点更新记录。
nav: true
nav_order: 6
_styles: |
  .news-feed {
    margin: 1.6rem 0 0;
    border-top: 1px solid var(--global-divider-color);
  }
  .news-item {
    display: grid;
    grid-template-columns: 7.5rem minmax(0, 1fr);
    gap: 1rem;
    padding: 1rem 0;
    border-bottom: 1px solid var(--global-divider-color);
  }
  .news-date {
    font-size: 0.8rem;
    font-variant-numeric: tabular-nums;
    color: var(--global-text-color-light);
  }
  .news-body {
    font-size: 0.95rem;
    line-height: 1.7;
  }
  .news-body p {
    margin: 0;
  }
  @media (max-width: 575.98px) {
    .news-item {
      grid-template-columns: 1fr;
      gap: 0.2rem;
    }
  }
---

<div class="news-feed">
  {% for item in site.news reversed %}
    <div class="news-item">
      <time class="news-date" datetime="{{ item.date | date_to_xmlschema }}">{{ item.date | date: '%Y-%m-%d' }}</time>
      <div class="news-body">
        {% if item.inline %}
          {{ item.content | remove: '<p>' | remove: '</p>' }}
        {% else %}
          <a href="{{ item.url | relative_url }}">{{ item.title }}</a>
        {% endif %}
      </div>
    </div>
  {% endfor %}
</div>
