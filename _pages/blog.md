---
layout: default
permalink: /blog/
title: 博客
description: 记录 AI、开发者工具、知识管理与产品实践。
nav: true
nav_order: 2
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

<link rel="stylesheet" href="{{ '/assets/css/blog.css' | relative_url }}" />

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
