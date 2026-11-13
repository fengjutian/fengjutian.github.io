---
layout: post
title: OhMyGame：AI 生成游戏不难，难的是让它自己发现游戏跑不起来
date: 2026-11-13 15:58:00 +0800
thumbnail: assets/img/blog/ohmygame-agent-game-studio.jpg
description: 从 30 秒超时、4 个隐藏窗口、6,000 字符截断三个数字出发，拆解 OhMyGame 如何把「试玩」做成 agent 的工具，以及它为此接受的两级信任模型、检查点与插件边界。
tags: [AI, 开源, 开发者工具]
categories: [技术随笔, 工程实践]
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/ohmygame-agent-game-studio.jpg
---

一个 agent 把游戏代码写完，然后呢？

它没有眼睛。它能读到 `controls.js` 里写着 `keydown`，但读不出按下方向键之后角色有没有动。绝大多数 AI 编程工具到此为止：代码生成完毕，任务标记完成。

OhMyGame 这个开源项目在这一步上做了一个具体的选择：**给 agent 开一个隐藏的浏览器窗口，让它自己玩一遍。**

- GitHub：[WhiteTowerAI/ohmygame](https://github.com/WhiteTowerAI/ohmygame)（Apache-2.0，Beta）
- 官网与文档：[ohmygame.ai](https://ohmygame.ai/) / [ohmygame.ai/docs](https://ohmygame.ai/docs/)
- 技术参考：[`docs/runtime.md`](https://github.com/WhiteTowerAI/ohmygame/blob/main/docs/runtime.md)

本文只讲一件事：**它把「验证」变成了一个有预算的工具调用，并为此付出了什么代价。**不是功能盘点——功能列表在 README 上，比这好读。

## 一、三个数字

先看三个数字，它们都来自 `docs/runtime.md`，而且都不是产品卖点，是工程约束：

- **30 秒**：每次 `game_use` 调用的超时；到点就 abort，跟着当前 turn 一起结束。
- **4 个**：同时最多允许存在的隐藏会话数。agent 忘了关，也不会无限开窗口。
- **6,000 字符**：界面上每条工具输出只保留开头和结尾各 6,000 字符，中间丢掉。

前两个是给 agent 的预算，第三个是给界面的预算——它省的是内存，不是上下文。但它们背后是同一种习惯：**这个应用里每一处「看到的东西」都被限了大小**，因为看得太多本身就是成本。

## 二、它是什么

一句话：一个本地优先的 AI 游戏工作室。你描述游戏，agent 写设计文档、生成素材、写代码、开预览、试玩、修问题，最后发一个链接出去。

它自带模型与否的答案是「不」：首次启动要接一个 provider，或者直接接你已经在用的 Claude Code / Codex / OpenCode。40 多家 provider，自带 key，按 provider 计费，没有「运行次数」这种额度。

三种项目类型：Web 游戏（Phaser / Three.js / React Three Fiber）、互动故事（视觉小说、互动电影）、以及通用项目（接任意引擎）。

许可证 Apache-2.0，但**名称和 Logo 不在许可范围内**——这个细节在做二次分发时会被忽略。

## 三、三个进程，各跑什么

架构上它把自己切成三块，而且切得很干脆：

| 进程                    | 端口              | 负责什么                                             |
| ----------------------- | ----------------- | ---------------------------------------------------- |
| Renderer（React）       | `127.0.0.1:43120` | 对话、画布、预览、代码、素材——全部界面               |
| Local Daemon（Fastify） | `127.0.0.1:43110` | Pi agent、工具运行时、插件宿主、预览服务、项目与快照 |
| Electron 主进程         | —                 | 只负责桌面生命周期：起 daemon、等 `/health`、管窗口  |

两个值得注意的地方。

**第一，渲染层没有 Node 权限。**它拿到的只是 daemon 地址和一个一次性 token，而且这个 token 是通过隔离的 preload 桥单独发过来的，主进程只回答主窗口的主框架——嵌进去的 iframe 拿不到。

**第二，Electron 主进程不碰业务。**项目、对话、预览、事件都住在 daemon 里；关掉最后一个窗口时，主进程会先给 daemon 时间收掉 Pi 和预览子进程，再退出。这个分工让「浏览器里跑一份」和「桌面里跑一份」共用同一套 daemon。

## 四、把验证做成工具

![game_use 的调用面]({{ '/assets/img/blog/ohmygame-agent-game-studio/fig-02-game-use-loop.png' | relative_url }})

_五个动作，一个隐藏窗口；返回的是有上限的观察数据，不是全量页面。_

`game_use` 是 OhMyGame 的核心工具，不属于任何插件。它只有五个动作：

`open` 开会话（只接受预览源上的路径、查询串或锚点）→ `inspect` 读 DOM、canvas 状态、console、失败请求 → `act` 点击、输入、按键、触摸、等待 → `capture` 截图 → `close` 销毁。

链路是：daemon 通过**私有 IPC** 把请求转给 Electron 主进程（这条通道不属于渲染层 API），主进程持有按 playtest 隔离的 `BrowserWindow`，用内置 Chromium 跑游戏。

返回的数据全是「有界」的：DOM 和 console 被截断；截图从设备像素缩到页面的 CSS 像素，保持宽高比，好让图像坐标和输入坐标对得上，然后转成 JPEG 回给模型。文档里还写了一句很实在的话：**每次后续请求都会重发这些图，所以它们必须小。**

这就是第一节那些上限的由来。工具接口不是按「人能看多少」设计的，是按「模型能承受多少次往返」设计的。

顺带一个细节：Play 按钮给你自己玩的那个窗口，和 agent 玩的隐藏窗口共享同一个开发服务器和同一份源码。你改一行代码，两边会一起热更新——所以人和 agent 看到的是同一个游戏，不是两份副本。

## 五、信任边界：agent 全权，但三条边守得很死

![三条边界]({{ '/assets/img/blog/ohmygame-agent-game-studio/fig-01-trust-boundaries.png' | relative_url }})

_它能做的事很多，但每一层能读到的东西都被单独限定了。_

这是我认为最值得读的一段，因为文档写得很不讨好自己：

> Pi runs in trusted-local mode. The workspace is Pi's working directory, but `cwd` is not an operating-system security boundary, and enabled Pi tools run without an OhMyGame approval prompt.

翻译过来：**agent 在这个应用里是「完全信任」的。**工作目录不是安全边界，工具执行不带审批提示。任何声称「我们用沙箱保护你」的说法在这里都不成立，他们自己先把话说了。

于是安全设计只好落在别的地方，而且确实落了三处：

**凭证。**用户密钥只存在 daemon 里，写进 daemon 的 stdin——不是环境变量（同用户的其他进程能读环境变量），也不上命令行（进程列表能看到）。做到这一步之后还有一条：daemon 启动的任何子进程都不继承这个 token，包括预览服务器、依赖安装、发布构建、agent 的 shell、stdio MCP 服务器和 Git。

**试玩窗口。**独立 partition、开沙箱、开上下文隔离、关掉 Node 集成；主框架导航只能停在原预览源上，弹窗和下载被拦，权限除了指针锁和键盘锁一律拒绝。agent 能点、能看，但出不去。

**发布。**只上传静态构建产物；工作区、对话、凭证都不进上传包。每次发布是一个不可变的 Deployment，播放链接不变。

这个组合的取舍很清楚：**既然没法在操作系统层面关住一个需要改文件、跑命令的 agent，那就把它能泄露的东西（凭证）和它能碰到的外部世界（窗口、云端）分别关住。**这不是「安全」，是「把损失的上限压到可接受」。

## 六、给了全权，就得能撤回

如果 agent 真的能改你工作区里的一切，那么比「拦住它」更实际的是「能退回去」。

OhMyGame 的做法是**不需要 Git 的快照**：每次消费一条用户消息之前、以及一轮运行结束时，给工作区拍一份私有快照；跑完在对话里列出这一轮的净文件改动；**Undo** 撤回一轮的文件但保留对话，**Reapply** 把内容原样放回。快照存在工作区旁边，不碰你的 `.git`、分支和索引，并且会跳过 `.gitignore` 忽略的东西。

它是第五节的直接后果：**当你决定不做执行审批时，可回滚就成了必需品而不是加分项。**

## 七、画布：文件是唯一真源

一个容易被当成 UI 细节、其实是架构决定的东西：画布和面板读写的是**磁盘上的同一批文件**。

设计文档是 Markdown，画布是 JSON 节点，互动故事的每个画面是磁盘上的一个网页。Design 面板和 Canvas 面板展示的是同一份文档——文档原话是「在任一处编辑，另一处会显示，并且只保存一次」。

好处不是「好看」，是不用维护两套状态。可视化编辑器和 agent 操作的不是两个世界，而是同一个文件夹；agent 改完文件，你在面板里看到的就是改完的。插件还能往画布里加节点（`contributes.canvasNodes`，有类型的输入输出），所以这张画布是开放的数据结构，不是固定功能的界面。

## 八、扩展面是真的，但还没验收

![插件的扩展面]({{ '/assets/img/blog/ohmygame-agent-game-studio/fig-03-plugin-surface.png' | relative_url }})

_一个插件能加六种东西；这也是它敢把引擎交给插件、而不写进核心的原因。_

插件是一个带 `.ohmygame-plugin/plugin.json` 的包，能加：Skills（教 agent 怎么做这类活）、工具、MCP 服务器、面板、项目类型、画布节点。原生代码跑在**每个项目一个的扩展宿主子进程**里，不在 daemon 里——但它不是沙箱，文档明说「代码以你自己的权限运行」。三分钟内崩三次的插件会被隔离，另外还有 `--safe-mode`。

引擎这边，README 列了 Godot、Unity、Unreal、Blender、Aseprite、Tiled 和微信/抖音小游戏；`docs/plugins.md` 里还有 Cocos Creator 和 TapTap Maker。但真实状态是：**十个引擎/平台插件里，只有 Blender 默认开启，而且它只加 Skills（不接引擎进程）**；其余九个默认关闭，并且全部标着 Beta。文档自己也承认「真实引擎、账号、设备那一圈人工验收还挂着」，目前只有自动化的包与开关测试。

也就是说：**扩展面是设计出来的，可用性是待验收的。**这两件事不该混着说。

多人这块反而超出预期：浏览器多人走 Colyseus 房间，有四种权威模型——服务端跑规则、指定一个玩家的浏览器跑（host）、每个客户端跑并用帧回滚对齐（lockstep）、以及人人本地跑（owner）。owner 模式还能开 WebRTC 直连，文档里给了一次实测：两台 5G 手机之间 P2P 往返中位数 70 ms，走服务端约 400 ms。它还老实写了哪类 NAT 连不上，以及 lockstep 目前不做状态比对——所以一个漂移的客户端要等下一局或重连才会被发现。

## 九、局限

1. **Beta，且平台窄。**只有 macOS（Apple Silicon）和 Windows x64；Intel Mac 和 Linux 还在路线图上；Windows 包还没做代码签名，首次安装会被 SmartScreen 拦。
2. **隐私不等于离线。**项目文件和密钥留在本地，但提示词与生成请求会发给你选的 provider；另外**发行版会发使用数据和崩溃报告**（可在设置里关），源码构建不发——所以「本地优先」这句话成立的是项目文件与密钥，不是全部行为。
3. **agent 无审批执行。**这是设计选择，不是漏洞，但意味着你要按「它会改我的工作区」来准备备份和权限。
4. **试玩的覆盖面有限。**它靠 DOM、canvas、console 和截图判断，能测出「按钮没反应」「报错」，测不出「手感不对」「平衡性差」。
5. **引擎插件未验收。**十个引擎/平台插件里九个默认关闭，具体到每个引擎的导出、真机、发布流程都还需要人守着跑。
6. **素材质量取决于外部 provider。**3D、绑定、动画这些环节不是它自己做的。

## 十、我的判断

这个项目真正值得学的不是画布，也不是接了 40 家 provider，而是它把「验证」这件事**降级成了一个普通工具**。

一旦验证是工具，它就能被 agent 反复调用，也就能被预算约束——于是你看到 30 秒、4 个会话、6,000 字符这些数字。这些数字不是性能指标，是**为了让「多跑几次验证」在 token 上负担得起**而做的设计。我觉得这是「agent 产品」和「带 AI 的软件」的分界线：前者必须回答「一次工具调用的输出值多少 token」。

第二个值得学的是它对信任的处理顺序：先承认 agent 拿全权，再分别限制凭证、外部窗口和上传内容，最后用快照兜住「改坏了」这个风险。这个顺序和「先假装沙箱、再让用户点确认」相比，诚实得多，也更难做错。

要往下走，有三个能测的点：

- **验证回合的收益曲线。**同一类游戏，让 agent 试玩 1 次、3 次、10 次，看最终可玩率和 token 成本各是多少。现在没人报这个数。
- **有界返回的阈值。**30 秒和 4 个会话是怎么定的？把这两个数调大调小，量「多跑几轮」带来的修复成功率提升。6,000 字符那条同理，只是它影响的是界面内存而不是上下文。这是长上下文系统里最缺的经验值。
- **检查点的粒度。**一轮一个快照在「改十个文件」的场景下够用，在「改两百个文件」时是否应该换成按文件回滚，值得实测。

回到那句「AI 生成游戏不难」：难的从来不是生成，是**判断生成出来的东西能不能用**。OhMyGame 的答案不是让模型更聪明，而是给它一个窗口、一套有预算的观察接口，再加一条能退回去的路。这三样东西，换成视频剪辑、3D 建模、UI 设计，逻辑是一样的。

## 项目与资料

- [GitHub 仓库](https://github.com/WhiteTowerAI/ohmygame)（Apache-2.0，Beta）
- [官网](https://ohmygame.ai/) · [文档](https://ohmygame.ai/docs/) · [社区作品](https://ohmygame.ai/community/)
- [运行时文档](https://github.com/WhiteTowerAI/ohmygame/blob/main/docs/runtime.md)（`game_use`、信任边界、检查点、发布，本文主要来源）
- [插件文档](https://github.com/WhiteTowerAI/ohmygame/blob/main/docs/plugins.md)（扩展面、原生代码、隔离与安全模式、引擎插件状态）
- [多人与房间](https://github.com/WhiteTowerAI/ohmygame/blob/main/docs/multiplayer.md)（四种权威模型、P2P 实测）
- [外部 Agent 接入](https://github.com/WhiteTowerAI/ohmygame/blob/main/docs/external-agents.md)（MCP）

事实来源：三个数字、五个动作、信任边界与凭证流向、检查点、发布上限取自 `docs/runtime.md`；插件贡献类型、扩展宿主、隔离与安全模式、十个引擎/平台插件的默认状态取自 `docs/plugins.md`；四种多人权威模型与 70 ms / 400 ms 的对比取自 `docs/multiplayer.md`；平台、Bun/Node 版本、许可证与遥测说明取自 README。文中「这个数字是为了让验证负担得起」以及第十节三个待测点是推断，已标注。
