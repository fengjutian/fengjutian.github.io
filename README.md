# Fengjutian · 独立开发者

这是 [fengjutian.github.io](https://fengjutian.github.io) 的源码仓库，也是我的个人博客与项目作品集。

站点主要记录 AI 智能体、开发者工具、知识管理和产品实践，收录正在维护的开源项目、技术文章与开发动态。

## 关注方向

- **AI 原生开发工具与代码智能体**：探索模型如何真正进入日常编码流程。
- **多智能体协作与知识组织**：研究智能体之间的分工、信息连接与冲突消解。
- **Rust、TypeScript 与 Python 应用开发**：从命令行工具到桌面应用，将想法做成可运行的软件。
- **真实场景中的产品原型**：从具体需求出发，构建能够被使用和验证的数字产品。

## 精选项目

| 项目                                                       | 简介                                             | 技术方向                 |
| ---------------------------------------------------------- | ------------------------------------------------ | ------------------------ |
| [Folixa](https://github.com/fengjutian/Folixa)             | 基于 Qt 6 与 PDFium 的原生 AI PDF 编辑器         | C++、原生桌面应用        |
| [DocuFlowAI](https://github.com/fengjutian/DocuFlowAI)     | 融合 LSP 与多运行时智能体执行的 AI 开发工作区    | Rust、TypeScript、AI     |
| [SuperDBA](https://github.com/fengjutian/SuperDBA)         | 面向开发者与 AI 智能体的开源数据库工作空间       | TypeScript、Rust、数据库 |
| [Veyra Studio](https://github.com/fengjutian/Veyra-Studio) | 本地优先、与宿主无关的 AI 界面设计环境           | TypeScript、Tauri        |
| [planloop](https://github.com/fengjutian/planloop)         | 通过验收、记忆和预算约束智能体计划执行           | Python、AI Agent         |
| [Strata](https://github.com/fengjutian/Strata)             | 整合工作项、周期、模块、页面与分析的项目管理平台 | TypeScript、Django       |

更多项目可以在站点的[项目页面](https://fengjutian.github.io/projects/)和[仓库页面](https://fengjutian.github.io/repositories/)查看。

## 站点内容

```text
_pages/         独立页面：首页、博客、项目、动态和仓库
_posts/         技术文章
_projects/      精选项目介绍
_news/          站点与项目动态
_data/          社交信息、GitHub 仓库快照、履历和其他结构化内容
_bibliography/  论文与引用数据
assets/         本站自有样式、图片、Notebook 和 RenderCV 配置
docs/           al-folio 使用与维护文档
test/           插件集成测试与视觉回归测试
```

新增文章时，在 `_posts/` 下创建 `YYYY-MM-DD-slug.md`：

```yaml
---
layout: post
title: 文章标题
date: 2026-11-12 12:00:00 +0800
description: 用一句话概括文章内容。
tags: [AI, 开源]
categories: [技术随笔]
---
```

## 技术栈

- [Jekyll](https://jekyllrb.com/)：静态站点生成。
- [al-folio](https://github.com/alshedivat/al-folio)：站点基础与内容结构。
- `al_folio_core` 与 `al_*` 插件：布局、样式及搜索、数学公式、评论等功能。
- GitHub Actions：构建、检查并部署至 GitHub Pages。
- Playwright：视觉回归与交互测试。
- Prettier：Markdown、YAML、Liquid 等文件的格式检查。

本仓库采用 al-folio v1 的 thin starter 架构。页面布局、Liquid include、Sass 和功能 JavaScript 由版本化 Ruby gem 提供；本仓库主要保存站点配置、内容、文档和跨插件测试。修改前请先阅读 [AGENTS.md](AGENTS.md) 和[架构说明](docs/ARCHITECTURE.md)。

## 本地运行

### Docker

推荐使用 Docker，避免在本机单独配置 Ruby、ImageMagick 和 Jekyll：

```bash
docker compose up -d
```

启动后访问：

```text
http://127.0.0.1:8080/
```

查看日志或停止服务：

```bash
docker compose logs --tail=80
docker compose down
```

### 本机环境

本机已安装 Ruby、Bundler、Node.js 和所需系统依赖时，可以运行：

```bash
bundle install
npm ci
bundle exec jekyll serve
```

默认访问地址为 `http://localhost:4000/`。

## 检查与测试

提交内容前至少运行格式和 starter 边界检查：

```bash
npm ci
npm run lint:prettier
npm run lint:style-contract
```

验证站点构建：

```bash
bundle exec jekyll build
```

运行视觉测试：

```bash
npx playwright install chromium webkit
npm run test:visual
```

完整的集成测试命令及 Docker 验证流程见 [AGENTS.md](AGENTS.md#validated-local-command-set)。

## 配置与部署

站点的主要配置位于 [_config.yml](_config.yml)，包括：

- 站点标题、描述、域名和语言；
- 博客、分页、归档和相关文章；
- 搜索、评论、分析及社交信息；
- al-folio 插件开关与兼容设置；
- Jekyll 构建时需要排除的文件。

推送到 `main` 后，GitHub Actions 会构建站点并部署到 GitHub Pages。部署流程定义在 [deploy.yml](.github/workflows/deploy.yml)。

部署前会运行 `python3 bin/sync_github_repositories.py`，从 GitHub API 刷新全部公开仓库，项目数量、原创/Fork 分类及更新时间无需手工维护。

> 添加或移除 al-folio 插件时，必须同时更新 `Gemfile` 和 `_config.yml`；只修改其中一个会导致插件不生效。

## 许可证与致谢

站点基于 [al-folio](https://github.com/alshedivat/al-folio) 构建，感谢其维护者和插件生态的贡献。

仓库代码与模板部分遵循 [MIT License](LICENSE)。文章、个人资料和项目介绍等原创内容的权利归作者所有，转载或引用时请注明来源。
