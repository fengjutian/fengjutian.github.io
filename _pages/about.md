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

<!--
  about 布局不渲染 page._styles，首页样式走这张独立样式表。

  正文里的段落一律写成显式 HTML（<p> + <a>），不要用 Markdown 链接语法：
  Kramdown 在 HTML 块前后解析 Markdown 时，[文字](链接) 会被原样输出到页面上，
  链接不会变成可点的 <a>。写成显式 HTML 就绕开了这个坑。
-->

<link rel="stylesheet" href="{{ '/assets/css/home.css' | relative_url }}" />

<p class="home-lead">你好，我是 <strong>Fengjutian</strong>。我关注 AI 智能体、开发者工具与个人知识管理，喜欢把想法做成可运行、可验证的开源项目。</p>

{% assign github_data = site.data.github_repositories %}
<p>目前的方向覆盖 AI 编辑器、代码智能体、原生桌面工具、数据工作空间与协作产品。GitHub 现有 <strong>{{ github_data.total }}</strong> 个公开仓库，其中 <strong>{{ github_data.original_count }}</strong> 个原创仓库。全部内容见<a href="/projects/">项目页面</a>。</p>

## 关注方向

<div class="dir-grid">
  <div class="dir-card">
    <h3 class="dir-title">AI 原生开发工具与代码智能体</h3>
    <p class="dir-desc">让模型能力真正进入日常编码流程，而不只是停在演示里。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/DocuFlowAI">DocuFlowAI</a>
      <a href="https://github.com/fengjutian/planloop">planloop</a>
    </p>
  </div>
  <div class="dir-card">
    <h3 class="dir-title">原生桌面工具与数据工作空间</h3>
    <p class="dir-desc">把 AI、文档与数据库能力放进可靠、可验证的本地工作流。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/Folixa">Folixa</a>
      <a href="https://github.com/fengjutian/SuperDBA">SuperDBA</a>
    </p>
  </div>
  <div class="dir-card">
    <h3 class="dir-title">AI 设计与实时视觉创作</h3>
    <p class="dir-desc">探索本地优先的 AI 设计环境、交互画布与实时视觉工具。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/Veyra-Studio">Veyra Studio</a>
      <a href="https://github.com/fengjutian/ParticleStudio">ParticleStudio</a>
    </p>
  </div>
  <div class="dir-card">
    <h3 class="dir-title">协作平台与真实场景产品</h3>
    <p class="dir-desc">把团队协作和经营需求转化为可以部署、持续演进的产品。</p>
    <p class="dir-links">
      <a href="https://github.com/fengjutian/Strata">Strata</a>
      <a href="https://github.com/fengjutian/ShopOS">ShopOS</a>
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

<p class="proj-more">更多项目见 <a href="/projects/">全部公开仓库</a>。</p>

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

<p>全部动态见 <a href="/news/">动态</a>。</p>
