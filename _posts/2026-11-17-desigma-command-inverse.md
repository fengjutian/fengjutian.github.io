---
layout: post
title: Desigma：撤销不该靠人保证，它该由命令自己算出来
date: 2026-11-17 13:30:00 +0800
thumbnail: assets/img/blog/desigma-command-inverse.jpg
description: 从 Command 枚举返回自己的逆操作，到 256 px 分块缓存与逐字节可重复的 CPU 渲染，拆解 Desigma 如何把撤销做成唯一的编辑原语，并让协作与 MCP Agent 共用同一个栈。
tags: [AI, 开源, 开发者工具]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/desigma-command-inverse.jpg
---

一个创建于 2026 年 10 月 11 日、到今天刚满五周的 Rust 项目，已经有 1,237 个 star、124 个 fork，以及**超过 1,600 个测试**。

1,600 个测试这件事比 star 数更值得看。设计工具的测试很难写——你很难为一个“拖动后卡片看起来对不对”断言一个值。Desigma 能把测试做到这个规模，是因为它在两件事上做了非常规的选择：**渲染结果逐字节可复现**，以及**每一次编辑都自带精确的逆操作**。

第二个选择才是这篇文章要讲的东西。它看起来只是个数据结构决定，实际上撑住了三件通常要各写一套的事。

- 仓库：[deepfounder-ai/desigma](https://github.com/deepfounder-ai/desigma)（MIT OR Apache-2.0 双许可，Rust，15 个 crate）
- 文档：[`docs/`](https://github.com/deepfounder-ai/desigma/tree/main/docs)（协作协议、AI 生图、安装说明各一篇）
- 下载：[Releases](https://github.com/deepfounder-ai/desigma/releases)（macOS `.dmg`、Windows 安装包、Linux `.tar.gz`，**均未签名**）

本文只讲一件事：**Desigma 如何把“撤销”从一个人人都在实现的功能，变成整个编辑器唯一需要正确一次的编辑原语。**功能清单（自动布局、变体、白板、Deck、动画预设、Figma 导入）在 README 上比我能写得更全，我不复述。

## 一、先把规模说清楚

| 数字        | 是什么                                                         |
| ----------- | -------------------------------------------------------------- |
| 15 个 crate | `desigma-doc` / `engine` / `render` / `gpu` / `fig` / `mcp` 等 |
| 1,600+      | workspace 内的测试数，含驱动 UI 的合成输入测试                 |
| 256 px      | 并行分块缓存的 tile 尺寸                                       |
| 5,000 层    | 官方称在此规模页面上平移与拖拽“仍在一帧预算内”                 |
| 32          | `desigma-mcp` 暴露的工具数                                     |

技术栈是 `egui`（界面）+ `tiny-skia`（CPU 光栅化）+ `wgpu`（可选 GPU 路径），不依赖 Electron 和 WebView。不过“不用 Electron”只是结果，不是它的论点，理由在第七节。

## 二、撤销在设计工具里为什么是硬问题

一个普通编辑器里，撤销一块文本就是恢复一段字符串。

设计工具不一样。用户拖动一个图层，同时被牵动的东西可能有：

- **自动布局**：父容器里其它元素的位置与尺寸会重排；
- **组件实例**：改主组件时所有实例同步更新，但每个实例保留自己的覆盖；
- **变量与模式**：切换主题模式会让一批绑定了变量的属性整体变更；
- **动画**：一个属性上有多个关键帧轨道；
- **原型**：连线和交互也可能被顺带改写。

所以“撤销一次拖动”的难点不是记住旧坐标，而是**让这一堆联动结果整体回到原样，且不多不少**。

最直觉的写法是给每个命令两个方法，一个正着做、一个反着做——通常落成一个带 `execute` 与 `undo` 的 trait。问题在于这两份实现是两段独立代码，它们必须对同一个状态得出同一个结果，而这个“必须”只能靠人保证。**但仓库里不是这么写的。**

## 三、仓库里的写法：apply 返回自己的逆

看 `crates/desigma-doc/src/history.rs`。`Command` 不是 trait，是 **enum**；`apply` 的返回值就是撤销它所需的那条命令：

![撤销由谁计算：两条路的差别不在风格，在谁保证逆操作是对的]({{ '/assets/img/blog/desigma-command-inverse/fig-01-inverse-by-construction.png' | relative_url }})

_左边是常见的 trait 写法，两条路径各写一次；右边是仓库里的写法，只有一个入口。_

```rust
pub enum Command {
    Insert { parent: NodeId, index: usize, nodes: Vec<Node> },
    Remove { id: NodeId },
    Reparent { id: NodeId, parent: NodeId, index: usize },
    Update { node: Box<Node> },
    Batch(Vec<Command>),
    // …还有 SetVariables / SetNodeMotion / SetTimeline 等
}

impl Command {
    pub fn apply(self, doc: &mut Document) -> Result<Command, DocError> { … }
}
```

文件头那句注释把设计意图写得很清楚：“Every edit goes through `Command`; applying returns its inverse.”

于是整个撤销栈只有几十行：

```rust
pub fn exec(&mut self, doc: &mut Document, cmd: Command) -> Result<(), DocError> {
    let inv = cmd.apply(doc)?;
    self.undo.push(inv);
    self.redo.clear();
    Ok(())
}
```

栈里存的不是“操作记录”，而是**能把它抵消掉的那条命令**。`undo()` 做的事就是弹出栈顶再 `apply` 一次——不需要知道原操作是什么，也不需要为原操作额外保存快照。

这个设计的好处不是代码短，而是**逆操作没有第二份实现可以和第一份不一致**。`Update` 的逆就是“把旧节点还回去”，这个逻辑写在 `apply` 里面，和正向逻辑共处一个 `match` 分支，改一个必然看到另一个。

## 四、一条命令的一生

![一次改名编辑，两次 apply：命令在栈里存的是它自己的逆]({{ '/assets/img/blog/desigma-command-inverse/fig-02-command-lifecycle.png' | relative_url }})

_名字从 `Rectangle` 改成 `Renamed` 再撤销：每一步都是同一个 `apply`，只是喂进去的命令不同。_

`Command::Update` 处理方式值得一提，它是“把整个节点换掉”：

```rust
Command::Update { mut node } => {
    let cur = doc.get_mut(node.id).ok_or(DocError::NotFound(node.id))?;
    node.parent = cur.parent;
    node.children = std::mem::take(&mut cur.children);
    let old = std::mem::replace(cur, *node);
    Command::Update { node: Box::new(Node { children: Vec::new(), ..old }) }
}
```

执行时把旧节点换出来、新节点换进去，返回的逆命令里装的就是那个旧节点。**一次 `mem::replace` 同时完成“应用”和“制造逆操作”两件事**，这也是它快的原因——不需要遍历属性逐项比对差异。

## 五、一个原语，三处分叉

这才是这套设计真正的产出。因为“每次编辑都能精确回退”是一个可以被复用的性质，另外两件事就不用各自发明一套：

![一个原语，三处分叉：它们共享的不是代码，是同一个撤销栈]({{ '/assets/img/blog/desigma-command-inverse/fig-03-one-primitive-three-forks.png' | relative_url }})

**第一处是编辑器本身。**`Ctrl+Z` 弹栈再 `apply`，这部分和所有编辑器一样。

**第二处是协作。**Desigma 的实时协作是 P2P 的：通过 [iroh](https://github.com/n0-computer/iroh) 的 QUIC 连接，端到端加密，直连不通时走公共中继（仍然加密）；没有账号也没有服务器，由打开文件的那台机器充当 host。合并规则是**按属性**的：两个人分别改同一图层的颜色和位置，两边都能留下；往同一容器里插入，两条都保留；删除优先于编辑。

最值得注意的一条是：**你的撤销只撤销你自己的编辑。**（从代码结构推断，这更接近“每位参与者各持一份 `History`，只有本地操作会入栈”，而不是把远端操作也塞进同一个栈。）

**第三处是 MCP。**`desigma-mcp` 暴露 32 个工具，覆盖导入、检查图层与 token、生成代码、编辑（图层 / 页面 / 组件 / 实例 / 动画）与保存。开启编辑器的 agent bridge（`desigma --bridge`，或偏好设置里那一项）之后，“同一批工具会编辑屏幕上打开的那份文档，并共享它的 Undo”。

这句话的分量值得拆开：**Agent 的一次改动，对人来说就是一步 `Ctrl+Z`。**它不是新做的功能，是“命令持有自己的逆”这个前提让这件事免费成立。如果没有这个前提，agent 想做可回退的编辑，就得在应用层再造一套事务。

## 六、边界：什么时候“换整块”更划算

这套设计也不是没有取舍。看 enum 就能发现有两类命令：

| 类型               | 例子                                                           | 逆操作怎么来               |
| ------------------ | -------------------------------------------------------------- | -------------------------- |
| 结构化             | `Insert` / `Remove` / `Reparent` / `Update`                    | 精确反向，只动被改的那部分 |
| 整体替换（`Set*`） | `SetVariables` / `SetNodeMotion` / `SetTimeline` / `SetStyles` | 把旧的那一整块塞回去       |

后者是明确的妥协：变量集合、动画轨道这类状态形状复杂，算精细差分得不偿失，直接把旧快照换回来更省事。源码注释里写得很直白——动画编辑全部编译成 `SetNodeMotion`，“so undo is a snapshot swap”。

`Batch` 的反向逻辑同样干脆：逐条 `apply`，收集返回的逆命令，然后 **reverse** 一下，就是整批的逆。

还有一个细节说明作者踩过坑：`History` 里有个 `for_each_command_mut`，用来遍历撤销栈与重做栈（包括 `Batch` 内部）去**改写已存命令里引用的节点**。因为文档变化后，栈里那些“旧节点快照”可能已经和当前文档不一致，需要被修正。这类问题正是快照式撤销的典型后遗症。

## 七、确定性：为什么用 CPU 渲染反而是个前提

如果你只把 `tiny-skia` 当成“另一个渲染库”，就会漏掉它在这套架构里的位置。README 的原话是：`desigma-render` 在 CPU 上用 tiny-skia 绘制，**因此输出可以逐字节复现**；而且分块拼起来的结果与整页渲染一致。

![确定性的用处：让“两个截图一样吗”变成一个可以被断言的布尔值]({{ '/assets/img/blog/desigma-command-inverse/fig-04-determinism-to-assertion.png' | relative_url }})

_确定性不是为了洁癖，是为了让“这次改动有没有动到别的地方”变成 CI 能回答的问题。_

这条性质直接支撑了 `desigma-diff`：它比对截图时会做抗锯齿检测与 SSIM，并生成一份 HTML 报告。也就是说，**“视觉回归”在这个项目里是可用的**——一张基线图与一张新图之间的差异能被判定，而不是靠人眼看。

而这正是第二节那个“撤销有没有回到原样”的另一半：**撤销的断言靠单元测试（比较文档结构），渲染的断言靠截图比对（比较像素）。**两者都要求系统本身不给结果注入随机性。

代价也在同一处：CPU 光栅化要自己还性能债。于是有了空间索引与 256 px 的并行分块缓存——官方说的是五千层页面上平移和拖拽“仍在一帧预算内”。注意这条承诺是分块缓存背书的结果，不是 CPU 渲染天然如此。

顺带一提 `wgpu` 那条路的位置：它是可选加速，**并且带 CPU fallback**。它不承担“可重复”这个承诺，所以确定性测试仍然跑在 CPU 路径上。

## 八、它并不打算成为 Figma 的复刻

这点容易被误读。“Figma 替代品”是社区给的说法，项目自己的表述克制得多：文件兼容与熟悉的工作流是开发指南，**复刻 Figma 的编辑器外观不是目标**。

它真正想覆盖的是“设计文件能去哪里”：

| 方向 | 支持的东西                                                                                              |
| ---- | ------------------------------------------------------------------------------------------------------- |
| 读入 | `.fig`（zip 容器 + kiwi schema，deflate 或 zstd）、Figma REST JSON、Pencil `.pen`、SVG、原生 `.desigma` |
| 写出 | `.desigma`、Figma REST JSON、PNG / JPG / SVG / PDF、动画 GIF / WebM（AV1）/ PNG 序列                    |
| 交付 | Dev mode：量测、盒模型，以及 CSS / Tailwind / SwiftUI / Jetpack Compose / React 代码                    |

几个我需要点名的诚实之处：

- **`.fig` 格式没有公开规范。**他们的解码器依据社区逆向工程，并且明确提醒：真实文件上会有缺口。
- **导入不回写。**`.fig` 与 `.pen` 都是单向往 `.desigma`，保存不会写回原格式。
- **PDF 是栅格的。**Deck 的 Slide PDF / Deck PDF 都存在，但每页是高分辨率位图，文字不可选——README 自己把 PDF 导出也列进了早期缺口清单里。

## 九、局限

按重要性排：

1. **它自己说了不是专业日常工具。**README 的原话是 “not yet a replacement for professional daily work”，最大的缺口是协作、插件、PDF 导出、真实 `.fig` 文件覆盖度，以及**没有代码签名的发布包**。
2. **发布包未签名。**Windows 会弹 SmartScreen（要 More info → Run anyway），macOS 要走“仍要打开”或 `xattr -dr com.apple.quarantine`。这不是小事，很多人在第一步就放弃。
3. **`Set*` 类命令是快照式撤销。**变量、动画、样式这类整体状态靠换整块回退，意味着栈里的旧快照需要 `for_each_command_mut` 定期修正——快照式设计的后遗症，代码里已经能看到应对它的补丁。
4. **协作仍标注 beta。**P2P 意味着 host 关掉文件会话就结束，字体也还没同步过去；能拿到一份副本，但不是真正的多端持久化。
5. **插件能力被刻意收窄。**只支持 `document:insert-svg` 与 `storage:local` 两种权限，下载上限 16 个资源 / 单文件 2 MiB / 总计 8 MiB。这是安全上的克制，也意味着短时间不可能有 Figma 那样的插件生态。
6. **AI 生图用的是你自己的 OpenRouter key**，费用自负，key 存系统钥匙串（Windows 凭据管理器 / macOS 钥匙串 / Linux Secret Service）。它不是内置能力，是一条外接管道。
7. **15 个 crate 的学习成本不低。**想读懂它的渲染与布局，得在 `doc` / `engine` / `render` 三层之间来回跳。

## 十、我的判断

Desigma 值得学的不是“用 Rust 写个 Figma”这个叙事，而是它把两个通常被当成“实现细节”的东西提成了一等约束：

- **每次编辑都能精确回退** → 于是撤销、协作的按人撤销、Agent 的共享撤销栈，三件事共用一个原语；
- **渲染输出可复现** → 于是“改坏了没有”可以被 CI 而不是人眼回答。

这两条都属于同一类工程品味：**先让系统的行为可断言，再往上堆功能。**1,600 个测试是这个选择的证据，不是勤奋的证据。

如果要继续验证这条路，我会盯三件可检验的事：

1. **`Set*` 快照命令会不会成为瓶颈。**变量密集的文件里，每次编辑都换整块，栈的深度与内存会不会失控——这决定了这套设计的适用上限。
2. **确定性在 wgpu 路径上怎么处理。**如果将来 GPU 成为默认渲染路径，“逐字节可复现”要么被放弃，要么需要在 GPU 上重建确定性（固定批次、禁用无序原子）。这是个真正的技术分叉点。
3. **MCP 的工具粒度会不会收敛成“事务”。**现在是 32 个工具，每个都可能改动文档；当 agent 连续调用十几个工具时，人希望的是“这一步是 agent 干的一件事”，而不是十几次撤销。

第三点是我最在意的，也是它和我最近在读的那条线的接口：NNsight / pyvene 那套东西之所以有用，是因为它把“模型内部发生了什么”变成了可读、可改、可归因的量。**归根结底是同一个动作：先让一个变化可以被精确定位、精确回退，你才有资格谈理解它。**

一个设计工具愿意为了“可归因”付出 CPU 渲染和 1,600 个测试的代价，这件事本身比它现在缺多少功能更值得注意。

## 项目与资料

- 仓库：[github.com/deepfounder-ai/desigma](https://github.com/deepfounder-ai/desigma)（MIT OR Apache-2.0，双许可；许可证只覆盖代码，不含名称与图标——fork 需换名换标识）
- 文档：[`docs/`](https://github.com/deepfounder-ai/desigma/tree/main/docs)（[协作协议](https://github.com/deepfounder-ai/desigma/blob/main/docs/collaboration.md)、[AI 生图](https://github.com/deepfounder-ai/desigma/blob/main/docs/ai-images.md)、[安装](https://github.com/deepfounder-ai/desigma/blob/main/docs/install.md)）
- MCP：[`crates/desigma-mcp/README.md`](https://github.com/deepfounder-ai/desigma/blob/main/crates/desigma-mcp/README.md)、[`docs/agent-workflows.md`](https://github.com/deepfounder-ai/desigma/blob/main/docs/agent-workflows.md)
- 插件注册表：[deepfounder-ai/desigma-plugins](https://github.com/deepfounder-ai/desigma-plugins)
- 撤销实现：[`crates/desigma-doc/src/history.rs`](https://github.com/deepfounder-ai/desigma/blob/main/crates/desigma-doc/src/history.rs)

```sh
git clone https://github.com/deepfounder-ai/desigma
cd desigma
cargo run --release -p desigma-app               # 编辑器，带一份演示文档
cargo run --release -p desigma-app -- file.fig   # 直接打开一个 Figma 文件
cargo test --workspace                           # 那 1,600+ 个测试
```

```sh
# 无头截图，适合接进 CI
desigma --fixture showcase --select Home --size 1600x1000 --scale 2 --screenshot hero.png
desigma-diff compare reference.png actual.png --out diff.png
```

数据来源与口径：star / fork / 创建时间取 GitHub API（2026-11-17）；crate 清单、1,600+ 测试、256 px tile、5,000 层、32 个 MCP 工具、41 个动画预设、19 种混合模式、iroh 协作细节、格式矩阵、未签名发布与早期缺口清单均来自 README；`Command` 是 enum、`apply` 返回逆命令、`Batch` 反向、`for_each_command_mut`、`SetNodeMotion` 的注释原文与 `exec` 的写法均来自 `crates/desigma-doc/src/history.rs` 源码。常见教程会把命令写成带 `execute` / `undo` 的 trait，本文以仓库实现为准；另有流传的架构图里画着一个 “Layout Engine” 组件，crate 表里并无此项，布局能力分布在 `desigma-doc`（模型）与 `desigma-engine`（布局与文本测量）中。“确定性是视觉回归的前提”“协作的按人撤销更像每人一份 History”是我的推断，已在正文标注。
