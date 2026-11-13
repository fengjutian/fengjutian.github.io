---
layout: page
permalink: /sites/
title: 网站
description: 平时收集的网站与工具，卡片一览，持续添加。
nav: true
nav_order: 3
_styles: |
  /* 该页专属样式：网站卡片网格 + 标签筛选。
     只用主题自身的 CSS 变量，浅色/暗色模式自动跟随；
     次要文字用自定义灰度，保证 WCAG AA 的 4.5:1 对比度。 */
  .ws {
    --ws-muted: #6b6b6b;
    margin: 1.6rem 0 0;
  }
  html[data-theme="dark"] .ws {
    --ws-muted: #a8a8a8;
  }
  .ws-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem;
    margin: 0 0 1.3rem;
  }
  .ws-count {
    margin-right: 0.35rem;
    font-size: 0.82rem;
    color: var(--ws-muted);
  }
  .ws-chip {
    padding: 0.24rem 0.7rem;
    font-size: 0.78rem;
    line-height: 1.45;
    color: var(--ws-muted);
    cursor: pointer;
    background: transparent;
    border: 1px solid var(--global-divider-color);
    border-radius: 999px;
    transition:
      color 0.16s ease,
      border-color 0.16s ease,
      background-color 0.16s ease;
  }
  .ws-chip:hover {
    color: var(--global-theme-color);
    border-color: var(--global-theme-color);
  }
  .ws-chip[aria-pressed="true"] {
    color: #fff;
    background: var(--global-theme-color);
    border-color: var(--global-theme-color);
  }
  .ws-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
  }
  .ws-card {
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
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
  .ws-card[hidden] {
    display: none;
  }
  .ws-card:hover {
    color: var(--global-text-color);
    text-decoration: none;
    transform: translateY(-2px);
    border-color: var(--global-theme-color);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  }
  .ws-card:focus-visible {
    outline: 2px solid var(--global-theme-color);
    outline-offset: 2px;
  }
  .ws-head {
    display: flex;
    align-items: center;
    gap: 0.65rem;
  }
  .ws-icon {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    width: 2.1rem;
    height: 2.1rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--global-theme-color);
    background: color-mix(in srgb, var(--global-theme-color) 13%, transparent);
    border-radius: 0.45rem;
  }
  .ws-icon img {
    width: 100%;
    height: 100%;
    padding: 0.18rem;
    object-fit: contain;
    border-radius: inherit;
  }
  .ws-head-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .ws-name {
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.35;
    overflow-wrap: anywhere;
  }
  .ws-host {
    overflow: hidden;
    font-size: 0.74rem;
    color: var(--ws-muted);
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .ws-arrow {
    margin-left: auto;
    font-size: 0.68rem;
    color: var(--ws-muted);
    opacity: 0.65;
  }
  .ws-card:hover .ws-arrow {
    color: var(--global-theme-color);
    opacity: 1;
  }
  .ws-desc {
    flex: 1;
    font-size: 0.82rem;
    line-height: 1.55;
    color: var(--ws-muted);
  }
  .ws-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
  }
  .ws-tag {
    padding: 0.16rem 0.45rem;
    font-size: 0.68rem;
    color: var(--ws-muted);
    background: color-mix(in srgb, var(--global-text-color) 7%, transparent);
    border-radius: 999px;
  }
  .ws-empty {
    margin: 1.2rem 0 0;
    font-size: 0.84rem;
    color: var(--ws-muted);
  }
  .ws-empty[hidden] {
    display: none;
  }
  @media (max-width: 575.98px) {
    .ws-grid {
      grid-template-columns: 1fr;
    }
  }
---

{% assign sites = site.data.websites %}
{% assign all_tags = "" | split: "," %}
{% for item in sites %}
{% if item.tags %}
    {% assign all_tags = all_tags | concat: item.tags %}
{% endif %}
{% endfor %}
{% assign all_tags = all_tags | uniq | sort %}

<div class="ws">
  <div class="ws-bar">
    <span class="ws-count">{{ sites | size }} 个站点</span>
    <button type="button" class="ws-chip" data-tag="" aria-pressed="true">全部</button>
    {% for tag in all_tags %}
      <button type="button" class="ws-chip" data-tag="{{ tag }}" aria-pressed="false">{{ tag }}</button>
    {% endfor %}
  </div>

  <div class="ws-grid">
    {% for item in sites %}
      {% assign host = item.url | remove_first: "https://" | remove_first: "http://" | remove_first: "www." | split: "/" | first %}
      <a class="ws-card" href="{{ item.url }}" target="_blank" rel="noopener" data-tags="{{ item.tags | join: ',' }}">
        <span class="ws-head">
          <span class="ws-icon" aria-hidden="true">
            {%- if item.logo -%}
              <img src="{{ item.logo }}" alt="" loading="lazy" />
            {%- elsif item.icon -%}
              {{ item.icon }}
            {%- else -%}
              {{ item.name | slice: 0, 1 }}
            {%- endif -%}
          </span>
          <span class="ws-head-text">
            <span class="ws-name">{{ item.name }}</span>
            <span class="ws-host">{{ host }}</span>
          </span>
          <i class="fa-solid fa-arrow-up-right-from-square ws-arrow" aria-hidden="true"></i>
        </span>
        {% if item.description %}<span class="ws-desc">{{ item.description }}</span>{% endif %}
        {% if item.tags %}
          <span class="ws-tags">
            {% for tag in item.tags %}<span class="ws-tag">{{ tag }}</span>{% endfor %}
          </span>
        {% endif %}
      </a>
    {% endfor %}
  </div>

  <p class="ws-empty" hidden>这个标签下还没有站点。</p>
</div>

<script>
  (function () {
    var bar = document.querySelector(".ws-bar");
    if (!bar) return;
    var cards = Array.prototype.slice.call(document.querySelectorAll(".ws-card"));
    var empty = document.querySelector(".ws-empty");
    var chips = Array.prototype.slice.call(bar.querySelectorAll("button[data-tag]"));

    bar.addEventListener("click", function (event) {
      var chip = event.target.closest("button[data-tag]");
      if (!chip || !bar.contains(chip)) return;
      var tag = chip.getAttribute("data-tag");
      chips.forEach(function (button) {
        button.setAttribute("aria-pressed", button === chip ? "true" : "false");
      });
      var shown = 0;
      cards.forEach(function (card) {
        var tags = (card.getAttribute("data-tags") || "").split(",");
        var match = !tag || tags.indexOf(tag) !== -1;
        card.hidden = !match;
        if (match) shown += 1;
      });
      if (empty) empty.hidden = shown !== 0;
    });
  })();
</script>
