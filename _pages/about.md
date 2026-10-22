---
layout: about
# 首页的 h1 用的是 site.title，page.title 只负责导航栏第一项（关于我），
# 所以这里保持「关于我」，别和站点标题重复。
title: 关于我
permalink: /
subtitle: 独立开发者 · AI 工具与知识管理产品

profile:
  align: right
  image: github-avatar.png
  image_circular: true
  more_info: >
    <p><a href="https://github.com/fengjutian">GitHub @fengjutian</a></p>
    <p>主要在做 AI 编辑器、代码智能体与知识工具。</p>

selected_papers: false
social: true # includes social icons at the bottom of the page

# 主题自带的 announcements / latest_posts 区块渲染的是英文标题（"news" / "latest posts"）
# 和英文日期（"Oct 22, 2026"）。本站是中文内容，所以这两块保持关闭，
# 页面下方改用手写 Liquid 复用同样的 .news / .table / .news-title 结构，
# 标题与日期换成中文。
announcements:
  enabled: false
  scrollable: true # adds a vertical scroll bar if there are more than 3 news items
  limit: 5 # leave blank to include all the news in the `_news` folder

latest_posts:
  enabled: false
  scrollable: true # adds a vertical scroll bar if there are more than 3 new posts items
  limit: 3 # leave blank to include all the blog posts
---

<!-- about 布局不渲染 page._styles，首页样式走这张独立样式表。 -->
<link rel="stylesheet" href="{{ '/assets/css/home.css' | relative_url }}" />

<p class="home-lead">你好，我是 <strong>Fengjutian</strong>。我关注 AI 智能体、开发者工具与个人知识管理，喜欢把想法做成可运行、可验证的开源项目。</p>

<!--
  这段必须用纯 Markdown，不能写成 <p>...</p> 原始 HTML 块：
  Kramdown 不会解析 HTML 块内部的 Markdown，[项目页面](/projects/) 会原样输出到页面上。
-->
目前的方向覆盖 AI 编辑器、代码智能体、多智能体协作、知识星图与 Rust 命令行工具，站内收录 **30 余个**公开仓库。精选作品见 [项目页面](/projects/)，全部项目在 [GitHub](https://github.com/fengjutian) 上。

## 关注方向

<div class="dir-grid">
  <div class="dir-card">
    <h3 class="dir-title">AI 原生开发工具与代码智能体</h3>
    <p class="dir-desc">让模型能力真正进入日常编码流程，而不只是停在演示里。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/Blade-AI-Editor">Blade AI Editor</a>
      <a href="https://github.com/fengjutian/weber-code-agent">weber-code-agent</a>
    </p>
  </div>
  <div class="dir-card">
    <h3 class="dir-title">多智能体协作与知识组织</h3>
    <p class="dir-desc">多个智能体共同组织、处理和连接知识，而不是各自为战。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/mix-knowledg">mix-knowledg</a>
      <a href="https://github.com/fengjutian/NeuralNotes">NeuralNotes</a>
    </p>
  </div>
  <div class="dir-card">
    <h3 class="dir-title">Rust、TypeScript 与 Python 应用开发</h3>
    <p class="dir-desc">从命令行到桌面端，把想法做成能跑起来、能被验证的工具。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/catshell">catshell</a>
      <a href="https://github.com/fengjutian/IT-Master">IT-Master</a>
    </p>
  </div>
  <div class="dir-card">
    <h3 class="dir-title">面向真实场景的产品原型</h3>
    <p class="dir-desc">把本地需求转化成可用的数字产品，而不是停在需求文档里。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/jiufenglanting-business">九峰兰亭商业</a>
    </p>
  </div>
</div>

## 精选项目

{% assign featured_projects = site.projects | where: "featured", true | sort: "importance" %}
<div class="proj-grid">
  {% for project in featured_projects %}
    <div class="proj-card">
      <div class="proj-top">
        <span class="proj-cat">{{ project.category }}</span>
        <i class="fa-solid fa-arrow-up-right-from-square proj-arrow"></i>
      </div>
      <h3 class="proj-title">
        <a href="{% if project.redirect %}{{ project.redirect }}{% else %}{{ project.url | relative_url }}{% endif %}">{{ project.title }}</a>
      </h3>
      <p class="proj-desc">{{ project.description }}</p>
      <div class="proj-foot">
        <a class="proj-gh" href="{{ project.github }}" title="GitHub 源码仓库"><i class="fa-brands fa-github"></i> 源码</a>
      </div>
    </div>
  {% endfor %}
</div>

更多项目见 [全部开源仓库](/repositories/)。

## 最近在写

{% assign recent_posts = site.posts %}
<div class="news">
  <div class="table-responsive">
    <table class="table table-sm table-borderless">
      {% for item in recent_posts limit: 3 %}
        <tr>
          <th scope="row" style="width: 20%">{{ item.date | date: '%Y-%m-%d' }}</th>
          <td><a class="news-title" href="{{ item.url | relative_url }}">{{ item.title }}</a></td>
        </tr>
      {% endfor %}
    </table>
  </div>
</div>

## 最近动态

{% assign recent_news = site.news | reverse %}
<div class="news">
  <div class="table-responsive">
    <table class="table table-sm table-borderless">
      {% for item in recent_news limit: 4 %}
        <tr>
          <th scope="row" style="width: 20%">{{ item.date | date: '%Y-%m-%d' }}</th>
          <td>
            {% if item.inline %}
              {{ item.content | remove: '<p>' | remove: '</p>' | emojify }}
            {% else %}
              <a class="news-title" href="{{ item.url | relative_url }}">{{ item.title }}</a>
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </table>
  </div>
</div>

全部动态见 [动态](/news/)。
