---
layout: page
title: 提示词
permalink: /prompts/
description: 经过整理、可以直接复用和继续修改的提示词。
nav: true
nav_order: 4
_styles: |
  .post-header { display: none; }
  .prompt-library { --muted: color-mix(in srgb, var(--global-text-color) 62%, transparent); width: calc(100vw - 2rem); max-width: 1780px; min-height: calc(100vh - 8rem); margin: 0 calc(50% - 50vw + 1rem) 2rem; }
  .prompt-shell { display: grid; gap: .65rem; }
  .prompt-sidebar { position: relative; z-index: 6; display: flex; gap: 1rem; align-items: center; min-width: 0; padding: .8rem 0; border-bottom: 1px solid var(--global-divider-color); }
  .prompt-brand { display: flex; flex: 0 0 auto; gap: 0.7rem; align-items: center; margin: 0; font-size: 1.05rem; font-weight: 750; }
  .prompt-brand-mark { display: grid; width: 2rem; height: 2rem; place-items: center; color: #fff; background: linear-gradient(135deg, #7c4dff, #ff7a59); border-radius: 0.65rem; }
  .prompt-search { position: relative; display: block; flex: 0 1 18rem; margin: 0; }
  .prompt-search i { position: absolute; top: 50%; left: 0.85rem; color: var(--muted); pointer-events: none; transform: translateY(-50%); }
  .prompt-search input { width: 100%; min-height: 2.75rem; padding: 0.58rem 0.8rem 0.58rem 2.45rem; color: var(--global-text-color); background: var(--global-card-bg-color); border: 1px solid var(--global-divider-color); border-radius: 999px; }
  .prompt-search input:focus { border-color: var(--global-theme-color); outline: 3px solid color-mix(in srgb, var(--global-theme-color) 16%, transparent); }
  .prompt-filter-label { display: none; }
  .prompt-filters { display: flex; min-width: 0; gap: 0.22rem; overflow-x: auto; scrollbar-width: none; }
  .prompt-filters::-webkit-scrollbar { display: none; }
  .prompt-chip { width: auto; padding: 0.62rem 0.8rem; color: var(--muted); text-align: left; white-space: nowrap; background: transparent; border: 0; border-radius: 0.7rem; cursor: pointer; }
  .prompt-chip:hover, .prompt-chip:focus-visible { color: var(--global-text-color); background: color-mix(in srgb, var(--global-text-color) 6%, transparent); }
  .prompt-chip[aria-pressed="true"] { color: var(--global-text-color); font-weight: 700; background: color-mix(in srgb, var(--global-text-color) 9%, transparent); }
  .prompt-main { min-width: 0; }
  .prompt-topbar { position: sticky; top: 3.5rem; z-index: 5; display: flex; gap: 1rem; align-items: center; min-height: 4rem; padding: 0.65rem 0; background: color-mix(in srgb, var(--global-bg-color) 90%, transparent); backdrop-filter: blur(14px); }
  .prompt-models { display: flex; min-width: 0; gap: 0.25rem; overflow-x: auto; scrollbar-width: none; }
  .prompt-models::-webkit-scrollbar { display: none; }
  .prompt-model { padding: 0.55rem 0.75rem; color: var(--muted); white-space: nowrap; background: transparent; border: 0; border-radius: 999px; cursor: pointer; }
  .prompt-model:hover, .prompt-model:focus-visible, .prompt-model[aria-pressed="true"] { color: var(--global-text-color); background: color-mix(in srgb, var(--global-text-color) 8%, transparent); }
  .prompt-model[aria-pressed="true"] { font-weight: 700; }
  .prompt-count { margin: 0 0 0 auto; color: var(--muted); font-size: 0.78rem; white-space: nowrap; }
  .prompt-grid { column-count: 4; column-gap: 0.35rem; }
  .prompt-card { position: relative; display: inline-block; width: 100%; margin: 0 0 0.35rem; overflow: hidden; vertical-align: top; color: #fff; background: #17171a; border-radius: 0.28rem; cursor: pointer; break-inside: avoid; isolation: isolate; }
  .prompt-card[hidden] { display: none; }
  .prompt-card::before { position: absolute; inset: 0; z-index: 1; content: ""; background: linear-gradient(180deg, transparent 34%, rgba(0,0,0,.08) 52%, rgba(0,0,0,.88)); pointer-events: none; }
  .prompt-card--text { min-height: 22rem; background: linear-gradient(145deg, var(--accent, #6945d2), #15131c 72%); }
  .prompt-card--text:nth-child(3n + 2) { --accent: #176b87; min-height: 28rem; }
  .prompt-card--text:nth-child(3n) { --accent: #9a4c2f; min-height: 18rem; }
  .prompt-card--text::after { position: absolute; top: 12%; right: -18%; width: 15rem; height: 15rem; content: ""; background: radial-gradient(circle, rgba(255,255,255,.24), transparent 68%); border-radius: 50%; filter: blur(3px); }
  .prompt-cover { display: block; width: 100%; min-height: 22rem; max-height: 42rem; object-fit: cover; transition: transform 400ms ease; }
  .prompt-card:hover .prompt-cover { transform: scale(1.018); }
  .prompt-card-body { position: absolute; inset: auto 0 0; z-index: 2; padding: 3rem 1rem 1rem; }
  .prompt-card--text .prompt-card-body { position: relative; display: flex; min-height: inherit; flex-direction: column; justify-content: flex-end; }
  .prompt-category { margin: 0 0 0.3rem; color: rgba(255,255,255,.72); font-size: 0.68rem; font-weight: 650; letter-spacing: 0.06em; }
  .prompt-card h2 { margin: 0; color: #fff; font-size: 1rem; line-height: 1.3; text-shadow: 0 1px 10px rgba(0,0,0,.4); }
  .prompt-description { margin: 0.45rem 0 0; overflow: hidden; color: rgba(255,255,255,.78); font-size: 0.76rem; line-height: 1.45; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
  .prompt-card-actions { display: flex; gap: 0.45rem; margin-top: 0.8rem; opacity: 0; transform: translateY(0.3rem); transition: 180ms ease; }
  .prompt-card:hover .prompt-card-actions, .prompt-card:focus-within .prompt-card-actions { opacity: 1; transform: none; }
  .prompt-copy, .prompt-detail { padding: 0.38rem 0.62rem; color: #fff; font-size: 0.72rem; background: rgba(20,20,22,.62); border: 1px solid rgba(255,255,255,.28); border-radius: 999px; backdrop-filter: blur(8px); }
  .prompt-copy { cursor: pointer; }
  .prompt-copy:hover, .prompt-detail:hover { color: #fff; background: rgba(20,20,22,.88); text-decoration: none; }
  .prompt-empty { margin: 4rem 1rem; color: var(--muted); text-align: center; }
  .prompt-empty[hidden] { display: none; }
  body.prompt-modal-open { overflow: hidden; }
  .prompt-modal { --muted: color-mix(in srgb, var(--global-text-color) 62%, transparent); position: fixed; inset: 0; z-index: 1000; display: grid; padding: 1rem; place-items: center; color: var(--global-text-color); background: rgba(8,8,12,.72); backdrop-filter: blur(5px); }
  .prompt-modal[hidden] { display: none; }
  .prompt-modal-layout { display: grid; width: min(68rem, calc(100vw - 2rem)); max-height: calc(100dvh - 2rem); grid-template-columns: minmax(0, 1.05fr) minmax(20rem, .95fr); overflow: hidden; background: var(--global-bg-color); border: 1px solid var(--global-divider-color); border-radius: 1rem; box-shadow: 0 1.5rem 5rem rgba(0,0,0,.34); }
  .prompt-modal-layout--text { grid-template-columns: 1fr; }
  .prompt-modal-visual { min-height: 35rem; background: linear-gradient(145deg, var(--modal-accent, #6945d2), #15131c 72%); }
  .prompt-modal-visual[hidden] { display: none; }
  .prompt-modal-cover { width: 100%; height: 100%; max-height: calc(100dvh - 2rem); object-fit: cover; }
  .prompt-modal-content { position: relative; display: flex; min-width: 0; flex-direction: column; padding: 2.4rem; overflow-y: auto; }
  .prompt-modal-close { position: absolute; top: 1rem; right: 1rem; display: grid; width: 2.25rem; height: 2.25rem; padding: 0; place-items: center; color: var(--global-text-color); background: color-mix(in srgb, var(--global-text-color) 7%, transparent); border: 0; border-radius: 50%; cursor: pointer; }
  .prompt-modal-close:hover { background: color-mix(in srgb, var(--global-text-color) 13%, transparent); }
  .prompt-modal-category { margin: 1rem 3rem .4rem 0; color: var(--global-theme-color); font-size: .72rem; font-weight: 700; letter-spacing: .08em; }
  .prompt-modal-title { margin: 0; font-size: clamp(1.55rem, 3vw, 2.25rem); line-height: 1.15; }
  .prompt-modal-description { margin: .8rem 0 1.5rem; color: var(--muted); line-height: 1.65; }
  .prompt-modal-label { margin: 0 0 .5rem; font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
  .prompt-modal-prompt { margin: 0; padding: 1rem; overflow: auto; white-space: pre-wrap; color: var(--global-text-color); background: color-mix(in srgb, var(--global-text-color) 5%, transparent); border: 1px solid var(--global-divider-color); border-radius: .75rem; font: inherit; font-size: .86rem; line-height: 1.65; }
  .prompt-modal-models { margin: 1.2rem 0 0; color: var(--muted); font-size: .8rem; }
  .prompt-modal-actions { display: flex; gap: .65rem; margin-top: auto; padding-top: 1.5rem; }
  .prompt-modal-copy, .prompt-modal-detail { padding: .65rem 1rem; border-radius: 999px; }
  .prompt-modal-copy { color: #fff; background: var(--global-theme-color); border: 1px solid var(--global-theme-color); cursor: pointer; }
  .prompt-modal-detail { color: var(--global-text-color); border: 1px solid var(--global-divider-color); }
  .prompt-modal-detail:hover { color: var(--global-theme-color); text-decoration: none; }
  @media (max-width: 1280px) { .prompt-grid { column-count: 3; } }
  @media (max-width: 960px) { .prompt-library { width: 100%; margin: 0 0 2rem; } .prompt-sidebar { flex-wrap: wrap; } .prompt-brand { display: none; } .prompt-search { flex-basis: 100%; } .prompt-filters { width: 100%; } .prompt-topbar { top: 3.25rem; } }
  @media (max-width: 680px) { .prompt-grid { column-count: 2; } .prompt-count { display: none; } .prompt-card-actions { opacity: 1; transform: none; } .prompt-modal { padding: .5rem; } .prompt-modal-layout { display: block; width: calc(100vw - 1rem); max-height: calc(100dvh - 1rem); overflow-y: auto; } .prompt-modal-visual { min-height: 15rem; height: 34dvh; } .prompt-modal-cover { max-height: none; } .prompt-modal-content { padding: 1.4rem; overflow: visible; } }
  @media (max-width: 430px) { .prompt-grid { column-count: 1; } }
---

{% assign prompts = site.prompts | sort: "title" %}
{% assign categories = prompts | map: "category" | compact | uniq | sort %}
{% assign models = "" | split: "," %}
{% for prompt in prompts %}{% if prompt.models %}{% assign models = models | concat: prompt.models %}{% endif %}{% endfor %}
{% assign models = models | uniq | sort %}

<section class="prompt-library" aria-label="提示词库">
  <div class="prompt-shell">
    <aside class="prompt-sidebar" aria-label="提示词筛选">
      <p class="prompt-brand"><span class="prompt-brand-mark" aria-hidden="true"><i class="fa-solid fa-wand-magic-sparkles"></i></span>Prompt Gallery</p>
      <label class="prompt-search"><span class="sr-only">搜索提示词</span><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i><input id="prompt-query" type="search" placeholder="搜索提示词…" autocomplete="off" /></label>
      <p class="prompt-filter-label">分类</p>
      <div class="prompt-filters" data-filter="category">
        <button class="prompt-chip" type="button" data-value="" aria-pressed="true">全部</button>
        {% for category in categories %}<button class="prompt-chip" type="button" data-value="{{ category | escape }}" aria-pressed="false">{{ category }}</button>{% endfor %}
      </div>
    </aside>

    <div class="prompt-main">
      <div class="prompt-topbar">
        <div class="prompt-models" data-filter="model" aria-label="按模型筛选">
          <button class="prompt-model" type="button" data-value="" aria-pressed="true">全部模型</button>
          {% for model in models %}<button class="prompt-model" type="button" data-value="{{ model | escape }}" aria-pressed="false">{{ model }}</button>{% endfor %}
        </div>
        <p class="prompt-count" aria-live="polite"><strong data-prompt-count>{{ prompts | size }}</strong> 个灵感</p>
      </div>

      <div class="prompt-grid">
        {% for prompt in prompts %}
          <article class="prompt-card{% unless prompt.cover %} prompt-card--text{% endunless %}" data-title="{{ prompt.title | escape }}" data-description="{{ prompt.description | escape }}" data-cover="{% if prompt.cover %}{{ prompt.cover | relative_url }}{% endif %}" data-url="{{ prompt.url | relative_url }}" data-category="{{ prompt.category | escape }}" data-models="{{ prompt.models | join: ',' | escape }}" data-search="{{ prompt.title | append: ' ' | append: prompt.description | append: ' ' | append: prompt.prompt | append: ' ' | append: prompt.tags | downcase | escape }}">
            {% if prompt.cover %}<img class="prompt-cover" src="{{ prompt.cover | relative_url }}" alt="{{ prompt.title }}" loading="lazy" decoding="async" />{% endif %}
            <div class="prompt-card-body">
              <p class="prompt-category">{{ prompt.category }}</p><h2>{{ prompt.title }}</h2><p class="prompt-description">{{ prompt.description }}</p>
              <div class="prompt-card-actions"><button class="prompt-copy" type="button" data-copy="prompt-{{ forloop.index }}"><i class="fa-regular fa-copy" aria-hidden="true"></i> 复制</button><button class="prompt-detail" type="button" data-open-prompt aria-haspopup="dialog">查看详情</button></div>
            </div>
            <template id="prompt-{{ forloop.index }}">{{ prompt.prompt }}</template>
          </article>
        {% endfor %}
      </div>
      <p class="prompt-empty" hidden>没有找到匹配的提示词，试试其他关键词或筛选条件。</p>
    </div>

  </div>
</section>

<script>
  (() => {
    const root = document.querySelector(".prompt-library");
    if (!root) return;
    const query = root.querySelector("#prompt-query");
    const cards = [...root.querySelectorAll(".prompt-card")];
    const count = root.querySelector("[data-prompt-count]");
    const empty = root.querySelector(".prompt-empty");
    const active = { category: "", model: "" };
    let modalPrompt = "";
    let returnFocus = null;
    function make(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text) node.textContent = text;
      return node;
    }
    // The dialog is built here rather than in the page markup: the build strips empty
    // elements, so an empty <pre> placeholder never reached the browser and the lookup
    // below threw before the modal could be shown.
    const modal = make("div", "prompt-modal");
    modal.hidden = true;
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "prompt-modal-title");
    const layout = make("div", "prompt-modal-layout");
    const visual = make("div", "prompt-modal-visual");
    const cover = make("img", "prompt-modal-cover");
    cover.alt = "";
    visual.append(cover);
    const content = make("div", "prompt-modal-content");
    const closeButton = make("button", "prompt-modal-close");
    closeButton.type = "button";
    closeButton.setAttribute("aria-label", "关闭详情");
    closeButton.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
    const modalCategory = make("p", "prompt-modal-category");
    const modalTitle = make("h2", "prompt-modal-title");
    modalTitle.id = "prompt-modal-title";
    const modalDescription = make("p", "prompt-modal-description");
    const modalLabel = make("p", "prompt-modal-label", "提示词");
    const modalPromptBox = make("pre", "prompt-modal-prompt");
    const modalModels = make("p", "prompt-modal-models");
    const actions = make("div", "prompt-modal-actions");
    const copyButton = make("button", "prompt-modal-copy");
    copyButton.type = "button";
    copyButton.innerHTML = '<i class="fa-regular fa-copy" aria-hidden="true"></i> 复制提示词';
    const detailLink = make("a", "prompt-modal-detail", "打开完整页面");
    actions.append(copyButton, detailLink);
    content.append(closeButton, modalCategory, modalTitle, modalDescription, modalLabel, modalPromptBox, modalModels, actions);
    layout.append(visual, content);
    modal.append(layout);
    document.body.append(modal);
    function openModal(card) {
      const template = card.querySelector("template");
      modalPrompt = template ? template.content.textContent.trim() : "";
      modalCategory.textContent = card.dataset.category || "";
      modalTitle.textContent = card.dataset.title || "";
      modalDescription.textContent = card.dataset.description || "";
      modalPromptBox.textContent = modalPrompt;
      modalModels.textContent = card.dataset.models ? `适用模型：${card.dataset.models.split(",").join(" · ")}` : "";
      detailLink.href = card.dataset.url || "#";
      if (card.dataset.cover) {
        cover.src = card.dataset.cover;
        cover.alt = card.dataset.title || "";
      } else {
        cover.removeAttribute("src");
        cover.alt = "";
      }
      visual.hidden = !card.dataset.cover;
      layout.classList.toggle("prompt-modal-layout--text", !card.dataset.cover);
      returnFocus = document.activeElement;
      modal.hidden = false;
      document.body.classList.add("prompt-modal-open");
      closeButton.focus();
    }
    function closeModal() {
      modal.hidden = true;
      document.body.classList.remove("prompt-modal-open");
      if (returnFocus) returnFocus.focus();
    }
    function update() {
      const term = query.value.trim().toLocaleLowerCase();
      let visible = 0;
      cards.forEach((card) => {
        const models = card.dataset.models.split(",");
        const matches = (!active.category || card.dataset.category === active.category) && (!active.model || models.includes(active.model)) && (!term || card.dataset.search.includes(term));
        card.hidden = !matches;
        if (matches) visible += 1;
      });
      count.textContent = visible;
      empty.hidden = visible !== 0;
    }
    query.addEventListener("input", update);
    root.querySelectorAll("[data-filter]").forEach((group) => group.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-value]");
      if (!button) return;
      active[group.dataset.filter] = button.dataset.value;
      group.querySelectorAll("button").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      update();
    }));
    root.addEventListener("click", async (event) => {
      const button = event.target.closest("[data-copy]");
      if (button) {
        const template = document.getElementById(button.dataset.copy);
        await navigator.clipboard.writeText(template.content.textContent.trim());
        const original = button.innerHTML;
        button.textContent = "已复制";
        setTimeout(() => { button.innerHTML = original; }, 1400);
        return;
      }
      const card = event.target.closest(".prompt-card");
      if (card) openModal(card);
    });
    closeButton.addEventListener("click", closeModal);
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeModal();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !modal.hidden) closeModal();
    });
    copyButton.addEventListener("click", async () => {
      const original = copyButton.innerHTML;
      try {
        await navigator.clipboard.writeText(modalPrompt);
        copyButton.textContent = "已复制";
      } catch (error) {
        copyButton.textContent = "复制失败";
      }
      setTimeout(() => { copyButton.innerHTML = original; }, 1400);
    });
  })();
</script>
