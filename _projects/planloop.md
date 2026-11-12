---
layout: page
title: planloop
description: 将智能体计划变成可校验数据，用验收、记忆和预算约束执行过程。
importance: 5
category: AI 与开发者工具
featured: true
github: https://github.com/fengjutian/planloop
---

## 这是什么

planloop 是一个以可验证计划为核心的智能体执行框架。它关注的不是让规划器说得更聪明，而是让每一步都能被独立验收、被记忆约束，并在超出预算时停止。

项目通过事件日志、任务图、三层验收、失败重规划和 Git 提交点，减少“模型宣布完成，但任务其实没有完成”的失效。

## 技术栈

- **Python** —— 规划、调度、执行与验证核心
- **SQLite、FTS5、向量检索** —— 证据驱动的持久记忆
- **Git** —— 节点级提交点、失败回滚和变更溯源
- **Docker** —— 可选的无网络执行沙箱

## 当前能力

项目已经覆盖预算、状态板、HTN 到 DAG 分解、三层验收、重规划、审计、记忆、安全审批、模型分档路由和对照基准。

