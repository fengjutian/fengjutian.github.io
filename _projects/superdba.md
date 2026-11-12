---
layout: page
title: SuperDBA
description: 面向开发者与 AI 智能体的开源数据库工作空间。
importance: 3
category: 数据与 AI 工具
featured: true
github: https://github.com/fengjutian/SuperDBA
---

## 这是什么

SuperDBA 将数据库结构探索、SQL 编写、数据编辑、执行计划、Notebook 和 AI 工具连接整合进同一个工作空间。

它同时支持桌面端、浏览器模式和 MCP 服务，让人类开发者与兼容的 AI 客户端可以在受控权限下使用数据库能力。

## 技术栈

- **React、TypeScript** —— 跨桌面端和 Web 的统一界面
- **Rust、Tauri** —— 应用服务与桌面运行时
- **Monaco Editor** —— 感知数据库方言的 SQL 编辑体验
- **MCP** —— 向 AI 客户端暴露受控数据库工具

## 当前能力

项目覆盖 MySQL、MariaDB、PostgreSQL 和 SQLite，并通过插件扩展更多 SQL、NoSQL、向量数据库和云服务。
