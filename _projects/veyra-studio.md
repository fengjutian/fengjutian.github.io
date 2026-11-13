---
layout: page
title: Veyra Studio
description: 本地优先、与宿主无关的 AI 界面设计环境。
importance: 4
category: AI 与设计工具
featured: true
github: https://github.com/fengjutian/Veyra-Studio
---

## 这是什么

Veyra Studio 是一个本地优先、与宿主无关的 AI 界面设计环境，目标是让设计文档、命令事务和 AI 编辑能力运行在独立 Studio 中。

项目不再把旧的 MCP-to-Figma 桥接层作为产品运行时，而是逐步建立可独立演进的设计架构。

## 技术栈

- **TypeScript** —— 设计 Schema、命令与事务运行时
- **Tauri v2** —— 桌面应用外壳与原生文件能力
- **本地文件持久化** —— 可验证、可迁移的设计文档存储

## 当前进展

当前处于基础阶段，已经实现设计 Schema、运行时和持久化原型；交互画布、生产级渲染与完整 AI 编辑闭环仍在开发中。

---

**源码**：[GitHub 仓库]({{ page.github }})
