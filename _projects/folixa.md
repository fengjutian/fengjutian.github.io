---
layout: page
title: Folixa
description: 基于 C++20、Qt 6 与 PDFium 构建的原生 AI PDF 编辑器。
importance: 1
category: AI 与开发者工具
featured: true
github: https://github.com/fengjutian/Folixa
---

## 这是什么

Folixa 是一个面向 Windows 的原生 AI PDF 编辑器，采用 C++20、Qt 6 和 PDFium 构建。

项目已经具备 PDF 打开与渲染、连续页面视口、缩放旋转、瓦片缓存，以及独立 AI Worker 与本地 IPC 健康检查等基础能力。

## 技术栈

- **C++20、Qt 6** —— 原生桌面界面与应用架构
- **PDFium** —— PDF 解析与页面渲染
- **CMake、Ninja** —— 可复现的构建、测试和打包流程
- **QLocalSocket / QLocalServer** —— 主程序与 AI Worker 的本地通信

## 当前进展

当前重点是完善 PDF 编辑基础、文本提取和索引，并逐步接入真实模型 Provider。

---

**源码**：[GitHub 仓库]({{ page.github }})
