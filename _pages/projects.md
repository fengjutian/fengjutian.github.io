---
layout: page
title: 项目
permalink: /projects/
description: 我正在构建的 AI、开发者工具与知识管理项目。
nav: true
nav_order: 3
# 与 _data/repositories.yml 的分类口径保持一致；只列真正有项目条目的分类，
# 否则会渲染出空的分类标题。
display_categories: [AI 与开发者工具, 知识与内容工具, 应用与场景探索]
horizontal: false
_styles: |
  /* 项目卡片底部图标对齐：主题的 .card-body 是 block，标题长短不同时
     GitHub 图标会跟着文字上下漂。改成纵向 flex 后文字块撑满、图标统一贴底。
     首页（about 版式不支持 _styles）里有一份同样的规则。 */
  .projects .card > .card-body {
    display: flex;
    flex-direction: column;
  }
  .projects .card > .card-body > a {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
  }
  .projects .card > .card-body > a > .card-text {
    flex: 1 1 auto;
  }
---

<!-- pages/projects.md -->
<div class="projects">
{% if site.enable_project_categories and page.display_categories %}
  <!-- Display categorized projects -->
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>
  {% assign categorized_projects = site.projects | where: "category", category %}
  {% assign sorted_projects = categorized_projects | sort: "importance" %}
  <!-- Generate cards for each project -->
  {% if page.horizontal %}
  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
  {% endfor %}

{% else %}

<!-- Display projects without categories -->

{% assign sorted_projects = site.projects | sort: "importance" %}

  <!-- Generate cards for each project -->

{% if page.horizontal %}

  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>
