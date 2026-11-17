---
layout: page
title: 图像生成艺术指导
description: 用主体、构图、光线、材质和约束组织可迭代的图像提示词。
category: 视觉创作
models: [GPT Image, Midjourney, Gemini]
tags: [图像生成, 艺术指导, 构图]
variables: [subject, composition, style, constraints]
prompt: |
  创作一张以“{{subject}}”为主体的图像。

  构图与镜头：{{composition}}
  视觉语言：{{style}}
  必须遵守：{{constraints}}

  保持清晰的视觉层级和单一焦点。明确光源方向、色彩关系、材质表现与背景信息密度。
  不要添加未要求的文字、标志、边框或多余主体。若约束冲突，优先遵守“必须遵守”部分。
---

## 提示词

```text
{{ page.prompt }}
```

## 使用方法

把风格拆成可观察属性，例如色彩、光线、材质和媒介，不要只填写艺术家姓名。
