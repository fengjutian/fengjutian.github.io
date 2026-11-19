---
layout: post
title: StemStudio：给 AI 的不是代码，是能被检查的命令
date: 2026-11-19 16:40:00 +0800
thumbnail: assets/img/blog/stemstudio-command-contract.jpg
description: 从三进程本地架构、Stem Script 的四层命令契约、playground copilot 为什么被收窄，到仓库三个月没提交这件事——拆解一个浏览器 3D 引擎凭什么敢让 AI 直接改场景。
tags: [AI, 开源, 开发者工具]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/stemstudio-command-contract.jpg
---

**一条 DSL**。**三个进程**。**212 star**。

[StemStudio](https://github.com/Stem-Studio/Engine) 是一个跑在浏览器里的 3D 游戏编辑器加运行时：React + Three.js + WebGPU，行为脚本、ECS、物理、多人、AI copilot 全在里面，MIT，2026-05-20 建库。

介绍它的人一般会说「浏览器变成了完整游戏引擎」。我觉得那句话没错，但漏掉了它真正的设计决定。

翻 `docs/stem-script.md` 的第一段，有一句写得很硬：

> Stem Script is not a general-purpose scripting language. Each line resolves to an immutable command intent.

**它给 AI 的不是 JavaScript，是一条命令契约。**这才是这个项目值得写的地方。

## 一、先看看它长什么样

![StemStudio 的 dashboard：描述游戏 → 生成，或者导入 .stemscript 文件夹]({{ '/assets/img/blog/stemstudio-command-contract/src-dashboard.png' | relative_url }})

_dashboard 实拍，2026-11-19 用无头 Chrome 抓的。注意横幅上的 BYOK 提示和「Import stemscript folder」。_

界面本身说明了它的三条入口：**描述一句话生成**、**导入 `.stemscript` 文件夹**、**从空白开始**。左边那条「Switch to folder storage」是 local-first 的另一种存法——项目写进你选的文件夹，而不是浏览器数据库。

## 二、三个进程，都在你自己的机器上

![三个本地进程与端口]({{ '/assets/img/blog/stemstudio-command-contract/fig-01-three-processes.png' | relative_url }})

_`bun run dev` 起三个：编辑器 5173、Go 写的 AI 代理 8081、Colyseus 的多人房间 2567。_

这是 local-first 的落地方式，不是口号：

- **编辑器**在浏览器里，项目存 IndexedDB 或你选的文件夹；
- **AI 代理**是本地的 Go 程序，拿着你自己的 key 去调 provider——中间没有它的服务器，因为**根本没有它的服务器**；
- **多人 sidecar** 是 Node + Colyseus，`bun run dev` 时自动拉起，两个标签页就能进同一个房间。

不用 AI 就不启动代理，不写多人就不启动 sidecar。代价是本地要装三样东西：Bun 1.0+、Go 1.21+、Node 20+。

顺带一个硬约束：**它要求 WebGPU，不支持 WebGL**。Chromium 上还有文件夹存储；Firefox / Safari 能用，但只能存 IndexedDB。

## 三、一行脚本，四层，最后变成一次不可变的意图

![Stem Script 的四层]({{ '/assets/img/blog/stemstudio-command-contract/fig-02-command-contract.png' | relative_url }})

_DSL 文本 → 解析后的命令意图 → CommandsRegistry → engine handler。_

看一个真实的 `.stemscript` 片段（取自文档）：

```stemscript
project title "Tiny Obby"
add group name=Level
add box name=Ground size=12,0.1,12 position=0,-0.05,0 color=#2d3748 parent=Level
add capsule name=Player size=0.5,1.8,0.5 position=0,0.9,0 color=#3b82f6
update Player tag=Player
physics engine rapier gravity=-9.81
behavior attach Player behaviorId=character config={isDefault:true,walkSpeed:3}
camera "DefaultCamera" cameraType=THIRD_PERSON defaultDistance=6
```

它长得像 shell 命令和 JSON 的混血：一行一条命令，`key=value` 传参，向量写成 `0,1,0`，配置块用 JSON 字面量，含空格的字符串加引号。`add box` 是简写，展开成 registry 里的 `create_primitive`。

关键是每一行都要先变成**一个不可变的命令意图**——命令名加归一化参数——然后跨过编辑器/引擎边界，由注册的 handler 执行。文档把这句话说得很清楚：_handler 可以改场景、导资源、配运行时，但脚本那一行本身是一个稳定的请求，可以被检查、校验、重放、保存、复查和 diff。_

而这一切成立的前提是一句更朴素的话：

> The parser does not run arbitrary JavaScript.

解析器只做分词、别名解析和参数归一化。**它不是一个小运行时，所以它没有能力做坏事。**

## 四、为什么命令比代码好管

这不是口味问题。同一份能力，用「让 AI 写 Three.js 代码」和「让 AI 发命令」两种方式交付，工程属性完全不同：

| 维度     | 让 AI 写代码         | 让 AI 发命令                      |
| -------- | -------------------- | --------------------------------- |
| 校验     | 只能等它跑挂         | 参数可以逐条校验                  |
| 重放     | 靠代码本身可重入     | 同一份命令文件重放，结果可预期    |
| 复查     | 得读懂整段 JS        | 一行一个动作，可以 diff           |
| 权限     | 代码里的能力等于全部 | 能表达的动作就是命令表里的那些    |
| 兼容演进 | 改 API 就断          | 简写可以演进，raw registry 名兜底 |

这也是为什么 `.stemscript` 能当一个游戏的根文件——`Stem-Studio/Games-StemScript` 里那些例子，整套游戏就是一个脚本加一堆资产。

## 五、连 copilot 自己也被收窄了

![Script Tool 与 playground copilot 的权限差别]({{ '/assets/img/blog/stemstudio-command-contract/fig-03-copilot-boundary.png' | relative_url }})

_同一个命令契约，人和 AI 走同一条路，但 AI 被挡在需要「你亲手选文件」的动作外面。_

这一处是我读文档时最意外的：**同一个 AI 有两套权限**。

- **Script Tool**（项目所有者/管理员）能 `import`、`exec`（选文件或文件夹）、`dump scene`、`export scene`、`save`，还能跑管理员命令 `check` / `test`；
- **playground 里的 copilot** 只能做只读检查（`list` / `get`）和实时编辑（`add box`、`behavior attach`）；需要文件选择器、项目任务存储、外部资源搜索、打包导出的命令，一律拒绝，**改给你 import / exec 那两行，让你自己执行**。

这个设计比「AI 什么都能干」成熟。理由也很实在：在浏览器里，文件选择器必须由用户手势触发——这不是权限洁癖，是平台限制。但把它显式化成权限分层，而不是让 AI 撞墙报错，是可维护的做法。

还有一处细节值得记：管理员命令 `check` / `test` 不是另写一套断言，而是**从写命令派生出探测**。也就是说，测试的可信度来自「它测的就是刚才那条命令」。

## 六、局限

1. **仓库三个月没推过提交。**建库 2026-05-20，最后一次 push 是 **2026-08-09**，13 个 open issue。212 star、34 fork。这是公司项目，不是个人玩具——团队表里有 CTO、Head of Engineering 这些角色，官网 buildwithstem.com——但活跃度就摆在这里。
2. **WebGPU 是硬门槛。**不支持 WebGL，意味着老设备、部分 Linux 驱动、旧 Safari 直接出局。这不是能靠 polyfill 绕的。
3. **多人只是开发级。**Colyseus sidecar 跑在你本机，房间调度、持久化、认证、扩容、反作弊都没有。文档也没假装有。
4. **AI 能力全是外链。**BYOK 意味着你不付订阅费，但要付 provider 的钱；而且没有 key 时，生成入口就只剩「自己描述」的壳。
5. **三套工具链。**Bun + Go + Node 同时装，对只想试试的人来说门槛不低。
6. **没有第三方复现。**性能、稳定性、能撑多大的场景，都只有作者自己的说法。

## 七、我的判断

我认为它最值得抄的不是「浏览器里跑引擎」，而是**把 AI 的操作面做成一个有边界的命令表**。

这件事在很多「AI + 工具」的项目里被忽略了：大家忙着让模型多能，很少问「它做的每一步能不能被检查」。Stem Script 的答案是把动作收窄到可枚举——收窄会损失表达力，但换来四件事：能校验、能重放、能 diff、能限权。

我在别的项目里见过同一个动作的不同版本：Hypit 把时间轴收窄成词的投影，AnyCrawl 把解析收窄成 schema，Blender Skills 把验收收窄成六项检查。StemStudio 的版本是**把「改游戏」收窄成命令**。说法不同，问的是同一件事：**你愿意为「可检查」放弃多少表达力？**

它给出的答案偏保守，也因此更容易被信任。至于这个项目本身还能不能继续长——看一眼提交时间就知道，那已经不是技术问题了。

## 项目与资料

- 仓库：[Stem-Studio/Engine](https://github.com/Stem-Studio/Engine)（MIT）
- Stem Script 文档：[docs/stem-script.md](https://github.com/Stem-Studio/Engine/blob/main/docs/stem-script.md)
- 用 `.stemscript` 写的完整游戏：[Stem-Studio/Games-StemScript](https://github.com/Stem-Studio/Games-StemScript)
- 官网：[buildwithstem.com](https://buildwithstem.com)

数据来源：star / fork / issue / 建库与最后 push 时间 / 许可取自 GitHub REST API（2026-11-19）；三个端口、依赖版本、provider 列表、WebGPU 要求与浏览器支持范围取自 README；四层契约、「不可变命令意图」「解析器不执行任意 JavaScript」、Script Tool 与 playground copilot 的权限差别、`check` / `test` 的派生方式取自 `docs/stem-script.md` 原文。dashboard 截图是 2026-11-19 用本机无头 Chrome 访问 `buildwithstem.com/dashboard?mode=playground` 得到的，未做任何修改。
