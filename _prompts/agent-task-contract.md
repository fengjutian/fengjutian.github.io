---
layout: page
title: Agent 任务契约
description: 为编码或研究 Agent 明确目标、范围、约束、验证和完成条件。
category: Agent 工作流
models: [Codex, ChatGPT, Claude]
tags: [Agent, 任务规划, 验证]
variables: [objective, scope, constraints, verification]
prompt: |
  目标：{{objective}}

  工作范围：{{scope}}
  约束：{{constraints}}
  验证方式：{{verification}}

  开始前先检查现有实现和仓库规则。做出完成任务所需的最小改动，保留无关的用户修改。
  对关键假设给出依据；遇到会改变目标或扩大范围的选择时停止并说明。
  完成后运行与风险相称的验证，并报告改动、验证结果、未验证部分和剩余风险。
---

## 提示词

```text
{{ page.prompt }}
```

## 使用方法

把“完成”写成可验证状态，例如测试通过、页面出现某行为或输出满足某种结构。
