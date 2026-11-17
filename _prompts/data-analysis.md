---
layout: page
title: 数据分析问题定义
description: 在计算指标之前明确口径、假设、异常值和可回答范围。
category: 分析决策
models: [ChatGPT, Claude, Gemini]
tags: [数据分析, 指标, 决策]
variables: [decision, dataset, definitions]
prompt: |
  我需要用数据支持这个决策：{{decision}}。

  数据集说明：{{dataset}}
  已知口径：{{definitions}}

  请先列出需要确认的指标口径、时间窗口、分组维度、缺失值和异常值处理方式。
  然后给出分析步骤，并区分描述性结果、相关性和因果结论。
  对每个结论说明它回答了什么、不能回答什么，以及可能改变结论的偏差。
  最后给出适合向决策者展示的表格或图表建议。
---

## 提示词

```text
{{ page.prompt }}
```

## 使用方法

先用它检查分析问题是否成立，再让模型编写 SQL、Python 或电子表格公式。
