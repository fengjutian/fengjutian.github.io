---
layout: page
permalink: /sites/
title: 网站
description: 值得反复访问的技术信源、开发工具与研究入口。
nav: true
nav_order: 3
_styles: |
  .ws {
    --ws-muted: #666b73;
    --ws-soft: color-mix(in srgb, var(--global-theme-color) 8%, var(--global-card-bg-color));
    margin-top: 1.75rem;
  }
  html[data-theme="dark"] .ws { --ws-muted: #a7abb3; }
  .ws-toolbar {
    display: grid;
    grid-template-columns: minmax(15rem, 1fr) auto;
    gap: 1rem;
    align-items: center;
    padding: 0.9rem;
    margin-bottom: 1.25rem;
    background: var(--ws-soft);
    border: 1px solid color-mix(in srgb, var(--global-theme-color) 18%, var(--global-divider-color));
    border-radius: 0.85rem;
  }
  .ws-search { position: relative; }
  .ws-search i {
    position: absolute;
    top: 50%;
    left: 0.85rem;
    color: var(--ws-muted);
    pointer-events: none;
    transform: translateY(-50%);
  }
  .ws-search input {
    width: 100%;
    min-height: 2.5rem;
    padding: 0.55rem 0.85rem 0.55rem 2.45rem;
    color: var(--global-text-color);
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 0.6rem;
    outline: none;
    transition: border-color 0.16s ease, box-shadow 0.16s ease;
  }
  .ws-search input::placeholder { color: var(--ws-muted); }
  .ws-search input:focus {
    border-color: var(--global-theme-color);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--global-theme-color) 18%, transparent);
  }
  .ws-count {
    margin: 0;
    font-size: 0.8rem;
    color: var(--ws-muted);
    white-space: nowrap;
  }
  .ws-count strong {
    font-size: 1rem;
    font-weight: 600;
    color: var(--global-text-color);
  }
  .ws-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.35rem;
  }
  .ws-chip {
    display: inline-flex;
    gap: 0.4rem;
    align-items: center;
    min-height: 2rem;
    padding: 0.3rem 0.75rem;
    font-size: 0.78rem;
    line-height: 1;
    color: var(--ws-muted);
    cursor: pointer;
    background: transparent;
    border: 1px solid var(--global-divider-color);
    border-radius: 999px;
    transition: color 0.16s ease, border-color 0.16s ease, background-color 0.16s ease;
  }
  .ws-chip small { font-size: 0.65rem; opacity: 0.75; }
  .ws-chip:hover,
  .ws-chip:focus-visible {
    color: var(--global-theme-color);
    border-color: var(--global-theme-color);
    outline: none;
  }
  .ws-chip[aria-pressed="true"] {
    color: #fff;
    background: var(--global-theme-color);
    border-color: var(--global-theme-color);
  }
  .ws-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
  }
  .ws-card {
    position: relative;
    display: flex;
    min-height: 12.25rem;
    flex-direction: column;
    gap: 0.7rem;
    padding: 0 0 1.15rem;
    overflow: hidden;
    color: var(--global-text-color);
    text-decoration: none;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 0.75rem;
    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .ws-card::before {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    height: 3px;
    content: "";
    background: var(--global-theme-color);
    opacity: 0;
    transform: scaleX(0.35);
    transition: opacity 0.18s ease, transform 0.18s ease;
  }
  .ws-card[hidden] { display: none; }
  .ws-card:hover {
    color: var(--global-text-color);
    text-decoration: none;
    border-color: color-mix(in srgb, var(--global-theme-color) 55%, var(--global-divider-color));
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.1);
    transform: translateY(-3px);
  }
  .ws-card:hover::before { opacity: 1; transform: scaleX(1); }
  .ws-card:focus-visible {
    outline: 2px solid var(--global-theme-color);
    outline-offset: 3px;
  }
  .ws-head {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0 1.15rem;
  }
  .ws-preview {
    position: relative;
    aspect-ratio: 16 / 9;
    overflow: hidden;
    background: var(--ws-soft);
    border-bottom: 1px solid var(--global-divider-color);
  }
  .ws-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: top;
    transition: transform 0.28s ease;
  }
  .ws-card:hover .ws-preview img {
    transform: scale(1.025);
  }
  .ws-icon {
    display: flex;
    width: 2.6rem;
    height: 2.6rem;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    font-weight: 600;
    color: var(--global-theme-color);
    background: color-mix(in srgb, var(--global-theme-color) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--global-theme-color) 16%, transparent);
    border-radius: 0.65rem;
  }
  .ws-icon img {
    width: 100%;
    height: 100%;
    padding: 0.25rem;
    object-fit: contain;
    border-radius: inherit;
  }
  .ws-head-text {
    display: flex;
    min-width: 0;
    flex-direction: column;
  }
  .ws-name {
    font-size: 0.98rem;
    font-weight: 600;
    line-height: 1.35;
    overflow-wrap: anywhere;
  }
  .ws-host {
    overflow: hidden;
    font-size: 0.73rem;
    color: var(--ws-muted);
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .ws-arrow {
    margin-left: auto;
    font-size: 0.72rem;
    color: var(--ws-muted);
    opacity: 0.55;
    transition: color 0.16s ease, opacity 0.16s ease, transform 0.16s ease;
  }
  .ws-card:hover .ws-arrow {
    color: var(--global-theme-color);
    opacity: 1;
    transform: translate(2px, -2px);
  }
  .ws-desc {
    flex: 1;
    margin: 0;
    font-size: 0.82rem;
    line-height: 1.65;
    color: var(--ws-muted);
    padding: 0 1.15rem;
  }
  .ws-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    padding-top: 0.2rem;
    padding-right: 1.15rem;
    padding-left: 1.15rem;
  }
  .ws-tag {
    padding: 0.18rem 0.5rem;
    font-size: 0.67rem;
    color: var(--ws-muted);
    background: color-mix(in srgb, var(--global-text-color) 7%, transparent);
    border-radius: 999px;
  }
  .ws-empty {
    padding: 3.5rem 1rem;
    margin: 0;
    text-align: center;
    color: var(--ws-muted);
    background: var(--ws-soft);
    border: 1px dashed var(--global-divider-color);
    border-radius: 0.75rem;
  }
  .ws-empty i {
    display: block;
    margin-bottom: 0.65rem;
    font-size: 1.35rem;
  }
  .ws-empty[hidden] { display: none; }
  @media (max-width: 991.98px) {
    .ws-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
  @media (max-width: 575.98px) {
    .ws { margin-top: 1.25rem; }
    .ws-toolbar { grid-template-columns: 1fr; gap: 0.65rem; }
    .ws-grid { grid-template-columns: 1fr; }
    .ws-card { min-height: 0; }
  }
  @media (prefers-reduced-motion: reduce) {
    .ws-card,
    .ws-card::before,
    .ws-preview img,
    .ws-arrow { transition: none; }
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

<section class="ws" aria-label="网站收藏">
  <div class="ws-toolbar">
    <label class="ws-search">
      <span class="sr-only">搜索收藏的网站</span>
      <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
      <input id="ws-query" type="search" placeholder="搜索名称、简介或标签…" autocomplete="off" />
    </label>
    <p class="ws-count" aria-live="polite"><strong data-visible-count>{{ sites | size }}</strong> / {{ sites | size }} 个站点</p>
  </div>

  <div class="ws-filters" aria-label="按标签筛选">
    <button type="button" class="ws-chip" data-tag="" aria-pressed="true">全部 <small>{{ sites | size }}</small></button>
    {% for tag in all_tags %}
      {% assign tag_count = 0 %}
      {% for item in sites %}
        {% if item.tags contains tag %}{% assign tag_count = tag_count | plus: 1 %}{% endif %}
      {% endfor %}
      <button type="button" class="ws-chip" data-tag="{{ tag }}" aria-pressed="false">{{ tag }} <small>{{ tag_count }}</small></button>
    {% endfor %}
  </div>

  <div class="ws-grid">
    {% for item in sites %}
      {% assign host = item.url | remove_first: "https://" | remove_first: "http://" | remove_first: "www." | split: "/" | first %}
      {% assign preview = item.preview | default: "/assets/img/sites/default-preview.jpg" %}
      <a
        class="ws-card"
        href="{{ item.url }}"
        target="_blank"
        rel="noopener noreferrer"
        data-tags="{{ item.tags | join: ',' }}"
        data-search="{{ item.name | append: ' ' | append: item.description | append: ' ' | append: item.tags | downcase | escape }}"
        aria-label="访问 {{ item.name }}（在新窗口打开）"
      >
        <span class="ws-preview" aria-hidden="true">
          <img src="{{ preview | relative_url }}" alt="" loading="lazy" width="720" height="405" />
        </span>
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
          <span class="ws-tags" aria-label="标签">
            {% for tag in item.tags %}<span class="ws-tag">{{ tag }}</span>{% endfor %}
          </span>
        {% endif %}
      </a>
    {% endfor %}
  </div>

  <p class="ws-empty" hidden><i class="fa-regular fa-compass" aria-hidden="true"></i>没有找到匹配的站点，试试其他关键词或分类。</p>
</section>

<script>
  (function () {
    var root = document.querySelector(".ws");
    if (!root) return;

    var query = root.querySelector("#ws-query");
    var cards = Array.prototype.slice.call(root.querySelectorAll(".ws-card"));
    var chips = Array.prototype.slice.call(root.querySelectorAll(".ws-chip"));
    var count = root.querySelector("[data-visible-count]");
    var empty = root.querySelector(".ws-empty");
    var activeTag = "";

    function update() {
      var term = query.value.trim().toLowerCase();
      var shown = 0;

      cards.forEach(function (card) {
        var tags = (card.getAttribute("data-tags") || "").split(",");
        var matchesTag = !activeTag || tags.indexOf(activeTag) !== -1;
        var matchesQuery = !term || (card.getAttribute("data-search") || "").indexOf(term) !== -1;
        var visible = matchesTag && matchesQuery;
        card.hidden = !visible;
        if (visible) shown += 1;
      });

      count.textContent = shown;
      empty.hidden = shown !== 0;
    }

    query.addEventListener("input", update);
    root.querySelector(".ws-filters").addEventListener("click", function (event) {
      var chip = event.target.closest("button[data-tag]");
      if (!chip) return;
      activeTag = chip.getAttribute("data-tag");
      chips.forEach(function (button) {
        button.setAttribute("aria-pressed", button === chip ? "true" : "false");
      });
      update();
    });
  })();
</script>
