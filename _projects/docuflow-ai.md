---
layout: page
title: DocuFlowAI
description: 融合原生代码编辑器、LSP 与多运行时智能体执行的 AI 开发工作区。
importance: 2
category: AI 与开发者工具
featured: true
github: https://github.com/fengjutian/DocuFlowAI
---

## 这是什么

DocuFlowAI 正在构建一个面向 AI 协作开发的工作区，将代码编辑、语言服务和智能体运行时组织在统一工程中。

项目包含原生编辑器、Hermes 与 Pi 等智能体适配、任务编排、工作树隔离、执行审计和安全边界实验。

## 技术栈

- **Rust** —— 原生编辑器、文本模型和 LSP 客户端
- **TypeScript** —— 智能体适配、任务编排与运行时服务
- **Tree-sitter、LSP** —— 语法高亮、诊断与代码补全
- **Docker、WSL2** —— 智能体任务的执行边界与隔离实验

## 当前进展

当前已接入实时语法高亮、语言服务器诊断与补全，并持续完善多运行时调度、权限控制和执行追踪。
