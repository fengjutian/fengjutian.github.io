---
layout: page
title: 开源项目深度研究
description: 从证据、架构、实现路径与限制出发分析一个开源项目。
category: 技术研究
models: [ChatGPT, Claude, Gemini]
tags: [开源项目, 架构, 事实核查]
variables: [project, question, sources]
prompt: |
  请基于我提供的一手资料研究 {{project}}，重点回答：{{question}}。

  资料：
  {{sources}}

  先区分资料明确陈述的事实、从代码或文档得出的推断，以及仍然未知的信息。
  然后说明核心架构、关键执行流程、重要设计取舍、已知限制和适用边界。
  每个关键结论都要指向对应证据；不要用功能列表代替分析，也不要补写资料中不存在的事实。
---

## 提示词

```text
{{ page.prompt }}
```

## 使用方法

优先提供官方文档、源代码、论文和发布记录。问题越具体，输出越容易形成明确结论。
