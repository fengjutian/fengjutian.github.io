---
layout: default
permalink: /blog/
title: 博客
description: 记录 AI、开发者工具、知识管理与产品实践。
nav: true
nav_order: 2
_styles: |
  /* 博客页：窄版心 + 编辑式列表。正文列宽控制在中文舒适阅读区间，封面只在有 thumbnail 时占位。 */
  .post {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
  }
  .post .header-bar {
    padding-top: 0.5rem;
    padding-bottom: 1rem;
    text-align: left;
    border-bottom: none;
  }
  .post .header-bar h1 {
    color: var(--global-text-color);
    font-size: 1.9rem;
    font-weight: 400;
    letter-spacing: 0.01em;
  }
  .post .header-bar h2 {
    color: var(--global-text-color-light);
    font-size: 0.95rem;
    font-weight: 400;
    margin-top: 0.6rem;
  }
  .post .blog-filters {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem 0.55rem;
    margin-top: 1.6rem;
    font-size: 0.85rem;
  }
  .post .blog-filters a {
    color: var(--global-text-color-light);
    text-decoration: none;
    transition: color 0.15s ease;
  }
  .post .blog-filters a:hover {
    color: var(--global-theme-color);
    text-decoration: none;
  }
  .post .blog-filter-hash {
    color: var(--global-theme-color);
    opacity: 0.75;
    margin-right: 1px;
  }
  .post .blog-filter-sep {
    color: var(--global-divider-color);
  }
  .post .blog-rule {
    border: 0;
    border-top: 1px solid var(--global-divider-color);
    margin: 1.2rem 0 0;
    opacity: 1;
  }
  .post .pinned-posts {
    margin-top: 1.7rem;
  }
  .post .pinned-post {
    display: block;
    padding: 1.05rem 1.4rem 1.15rem;
    color: inherit;
    text-decoration: none;
    background: color-mix(in srgb, var(--global-theme-color) 6%, transparent);
    border-left: 3px solid var(--global-theme-color);
    border-bottom: 0;
    border-radius: 0 4px 4px 0;
    transition: background-color 0.15s ease;
  }
  .post .pinned-post + .pinned-post {
    margin-top: 0.8rem;
  }
  .post .pinned-post:hover {
    color: inherit;
    text-decoration: none;
    background: color-mix(in srgb, var(--global-theme-color) 9%, transparent);
  }
  .post .pinned-label {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    color: var(--global-theme-color);
    font-size: 0.7rem;
    letter-spacing: 0.12em;
  }
  .post .pinned-title {
    margin: 0.5rem 0 0.35rem;
    color: var(--global-text-color);
    font-size: 1.15rem;
    font-weight: 500;
    line-height: 1.5;
  }
  .post .pinned-desc {
    margin: 0;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
    line-height: 1.7;
  }
  .post .pinned-post .post-item-meta {
    margin-top: 0.7rem;
  }
  .post .post-list {
    margin: 0.3rem 0 0;
    padding: 0;
    list-style: none;
  }
  .post .post-list .post-item {
    margin: 0;
    padding: 0;
    border: 0;
  }
  .post .post-item + .post-item {
    border-top: 1px solid var(--global-divider-color);
  }
  .post .post-item-link {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    column-gap: 1.75rem;
    align-items: start;
    padding: 1.55rem 0;
    color: inherit;
    text-decoration: none;
  }
  .post .post-item-link:hover {
    color: inherit;
    text-decoration: none;
  }
  .post .post-item-cat {
    color: var(--global-theme-color);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
  }
  .post .post-item-title {
    margin: 0.5rem 0;
    color: var(--global-text-color);
    font-size: 1.28rem;
    font-weight: 500;
    line-height: 1.55;
    transition: color 0.15s ease;
  }
  .post .post-item-link:hover .post-item-title {
    color: var(--global-theme-color);
  }
  .post .post-item-desc {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin: 0 0 0.7rem;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
    line-height: 1.8;
  }
  .post .post-item-meta {
    margin: 0;
    color: var(--global-text-color-light);
    font-size: 0.78rem;
    font-variant-numeric: tabular-nums;
  }
  .post .post-item-dot {
    margin: 0 0.45rem;
    color: var(--global-divider-color);
  }
  .post .post-item-thumb {
    display: block;
    width: 208px;
    aspect-ratio: 8 / 5;
    overflow: hidden;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 4px;
  }
  .post .post-item-thumb img {
    display: block;
    width: 100%;
    height: 100%;
    margin: 0;
    object-fit: cover;
    transition: transform 0.35s ease;
  }
  .post .post-item-link:hover .post-item-thumb img {
    transform: scale(1.04);
  }
  @media (max-width: 640px) {
    .post .header-bar h1 {
      font-size: 1.6rem;
    }
    .post .post-item-link {
      column-gap: 1rem;
    }
    .post .post-item-thumb {
      width: 108px;
    }
    .post .post-item-title {
      font-size: 1.08rem;
    }
    .post .post-item-desc {
      font-size: 0.85rem;
    }
  }
pagination:
  enabled: true
  collection: posts
  permalink: /page/:num/
  per_page: 5
  sort_field: date
  sort_reverse: true
  trail:
    before: 1 # The number of links before the current page
    after: 3 # The number of links after the current page
---

<div class="post">
  {% assign blog_name_size = site.blog_name | size %}
  {% assign blog_description_size = site.blog_description | size %}

{% if blog_name_size > 0 or blog_description_size > 0 %}
    <div class="header-bar">
      <h1>{{ site.blog_name }}</h1>
      <h2>{{ site.blog_description }}</h2>
    </div>
{% endif %}

{% if site.display_tags or site.display_categories %}
    <div class="blog-filters">
      {% for tag in site.display_tags %}
        <a href="{{ tag | slugify | prepend: '/blog/tag/' | relative_url }}"><span class="blog-filter-hash">#</span>{{ tag }}</a>
        {% unless forloop.last %}<span class="blog-filter-sep">·</span>{% endunless %}
      {% endfor %}
      {% if site.display_tags and site.display_categories %}<span class="blog-filter-sep">·</span>{% endif %}
      {% for category in site.display_categories %}
        <a href="{{ category | slugify | prepend: '/blog/category/' | relative_url }}">{{ category }}</a>
        {% unless forloop.last %}<span class="blog-filter-sep">·</span>{% endunless %}
      {% endfor %}
    </div>
{% endif %}

  <hr class="blog-rule" />

{% assign featured_posts = site.posts | where_exp: "p", "p.featured == true or p.featured == 'true'" %}
{% assign is_first_page = false %}
{% if paginator.page == 1 or paginator.page == nil %}
    {% assign is_first_page = true %}
{% endif %}

{% if featured_posts.size > 0 and is_first_page %}
    <div class="pinned-posts">
      {% for post in featured_posts %}
        {% assign read_time = post.content | number_of_words | divided_by: 180 | plus: 1 %}
        <a class="pinned-post" href="{{ post.url | relative_url }}">
          <div class="pinned-label"><i class="fa-solid fa-thumbtack fa-xs" aria-hidden="true"></i> 置顶</div>
          <h2 class="pinned-title">{{ post.title }}</h2>
          <p class="pinned-desc">{{ post.description }}</p>
          <p class="post-item-meta">
            <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: '%Y-%m-%d' }}</time>
            <span class="post-item-dot">·</span>
            {{ read_time }} 分钟阅读
          </p>
        </a>
      {% endfor %}
    </div>
{% endif %}

  <ul class="post-list">
    {% if page.pagination.enabled %}
      {% assign postlist = paginator.posts | where_exp: "p", "p.featured != true and p.featured != 'true'" %}
    {% else %}
      {% assign postlist = site.posts | where_exp: "p", "p.featured != true and p.featured != 'true'" %}
    {% endif %}

    {% for post in postlist %}
      {% if post.external_source == blank %}
        {% assign read_time = post.content | number_of_words | divided_by: 180 | plus: 1 %}
      {% else %}
        {% assign read_time = post.feed_content | strip_html | number_of_words | divided_by: 180 | plus: 1 %}
      {% endif %}
      {% assign primary_category = post.categories | first %}
      {% if primary_category == blank %}
        {% assign primary_category = post.tags | first %}
      {% endif %}
      {% if post.redirect == blank %}
        {% assign post_href = post.url | relative_url %}
      {% elsif post.redirect contains '://' %}
        {% assign post_href = post.redirect %}
      {% else %}
        {% assign post_href = post.redirect | relative_url %}
      {% endif %}

      <li class="post-item">
        <a class="post-item-link" href="{{ post_href }}"{% if post.redirect contains '://' %} target="_blank" rel="noopener"{% endif %}>
          <div class="post-item-body">
            {% if primary_category %}<div class="post-item-cat">{{ primary_category }}</div>{% endif %}
            <h2 class="post-item-title">{{ post.title }}</h2>
            {% if post.description %}<p class="post-item-desc">{{ post.description }}</p>{% endif %}
            <p class="post-item-meta">
              <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: '%Y-%m-%d' }}</time>
              <span class="post-item-dot">·</span>
              {{ read_time }} 分钟阅读
            </p>
          </div>
          {% if post.thumbnail %}
            <span class="post-item-thumb">
              <img src="{{ post.thumbnail | relative_url }}" alt="" width="800" height="500" loading="lazy" decoding="async" />
            </span>
          {% endif %}
        </a>
      </li>
    {% endfor %}

  </ul>

{% if postlist.size == 0 %}
    <p class="text-center" style="color: var(--global-text-color-light); padding: 2rem 0;">暂无其它文章。</p>
{% endif %}

{% if page.pagination.enabled %}
    {% include pagination.liquid %}
{% endif %}
</div>
