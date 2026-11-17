---
layout: page
title: 面向风险的代码审查
description: 先找真实缺陷和回归风险，再讨论风格与可维护性。
category: 软件工程
models: [ChatGPT, Claude, Gemini]
tags: [代码审查, 调试, 测试]
variables: [language, change, context]
prompt: |
  你是一名资深 {{language}} 工程师。请审查下面的代码变更。

  目标：{{context}}
  变更：
  {{change}}

  请按严重程度列出发现，优先检查：正确性、边界条件、并发与状态、安全、性能和兼容性。
  每个发现必须包含具体位置、触发条件、影响和最小修复建议。不要把纯风格偏好当成缺陷。
  最后指出缺失的测试；如果没有实质问题，请明确说明。
---

## 提示词

```text
{{ page.prompt }}
```

## 使用方法

把语言、改动内容和业务背景分别替换到变量中。提供 diff 通常比提供完整文件更容易得到聚焦的审查结果。

## 预期输出

按严重程度排列的问题清单、修复建议，以及需要补充的测试。
