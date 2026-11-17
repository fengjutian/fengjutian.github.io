---
layout: page
title: 技术文章论点编辑
description: 把资料整理成有中心论点的技术文章，而不是功能说明书。
category: 内容创作
models: [ChatGPT, Claude]
tags: [技术写作, 编辑, 结构]
variables: [audience, thesis, evidence]
prompt: |
  请面向 {{audience}} 写一篇技术文章。

  中心论点：{{thesis}}
  可用证据：
  {{evidence}}

  文章必须围绕一个可辩论的判断展开。先用具体问题建立语境，再解释机制与证据，随后讨论限制和反例，最后回到论点。
  删除无法服务论点的功能罗列。不要虚构数据、引用或使用体验；不确定的信息要明确标注。
---

## 提示词

```text
{{ page.prompt }}
```

## 使用方法

`thesis` 应该是一个判断句，而不是宽泛主题。例如“延迟执行让干预实验可序列化”比“介绍某个工具”更有效。
