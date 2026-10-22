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

你好，我是 **Fengjutian**。我关注 AI 智能体、开发者工具与个人知识管理，喜欢把想法做成可运行、可验证的开源项目。

目前的方向覆盖 AI 编辑器、代码智能体、多智能体协作、知识星图与 Rust 命令行工具，站内收录 **30 余个**公开仓库。精选作品见[项目页面](/projects/)，全部项目在 [GitHub](https://github.com/fengjutian) 上。

## 关注方向

- **AI 原生开发工具与代码智能体** —— [Blade AI Editor](https://github.com/fengjutian/Blade-AI-Editor)、[weber-code-agent](https://github.com/fengjutian/weber-code-agent)
- **多智能体协作与知识组织** —— [mix-knowledg](https://github.com/fengjutian/mix-knowledg)、[NeuralNotes](https://github.com/fengjutian/NeuralNotes)
- **Rust、TypeScript 与 Python 应用开发** —— [catshell](https://github.com/fengjutian/catshell)、[IT-Master](https://github.com/fengjutian/IT-Master)
- **面向真实场景的产品原型** —— [九峰兰亭商业](https://github.com/fengjutian/jiufenglanting-business)

## 精选项目

{% assign featured_projects = site.projects | where: "featured", true | sort: "importance" %}
<div class="row row-cols-1 row-cols-md-3">
  {% for project in featured_projects limit: 3 %}
    {% include projects.liquid %}
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
