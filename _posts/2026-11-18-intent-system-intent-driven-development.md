---
layout: post
title: Intent-System：它不信任 AI，所以把流程搬出 AI 的上下文
date: 2026-11-18 06:20:00 +0800
thumbnail: assets/img/blog/intent-system-intent-driven-development.jpg
description: 从两类 agent 的读写边界、label 的原子迁移、packet 四份文件，到四类不可外包的 facets 与三种席位编排，拆开 intent-system 这条 0.32.1 的确定性 CLI，看它把哪些判断留给了人，又在哪一处承认自己守不住。
tags: [AI, 开源, 架构设计]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/intent-system-intent-driven-development.jpg
---

先看一句发布说明。

`intent-cli` 0.32.1 的 release note 里，有一段专门在讲候选产物的哈希：

> 这些哈希标识的是被检查过的 workflow-dispatch 产物。release 事件的工作流会重新构建公开产物；**它们不是对后来公开资产哈希的声明**。

再往下一点，还有一句更干脆的：

> 这个校验守的是一个诚实的席位，而不是充当安全边界。

一个项目在自己的发布页上，用这么大的篇幅说明“我验证了什么、我没验证什么”，这件事本身就值得写一篇。

三个数字：**113 star、1 fork、6 个 open issue**。仓库是 [J-Tech-Japan/intent-system](https://github.com/J-Tech-Japan/intent-system)，C# 写的，Apache-2.0，2026-04-02 建库，稳定版 `0.32.1` 发布于 2026-10-21——也是它最后一次 push 的日期。

1 个 fork 这个数字很有意思：**它说明几乎没人真的把这份代码拉下来改过。** 所以以下所有分析来自它的文档与发布记录，而不是来自“很多人在这么用”。

而它想解决的问题，和我们过去一年读到的“AI 编程工作流”都不太一样。它不问“怎么让 AI 更懂意图”，它问的是：**怎么让 AI 不再需要做判断。**

## 一、一句话：确定性工具，概率性执行者

README 的第一段就把定位写死了：

> `intent-cli` 从不启动 Claude、Codex 或任何其他 AI provider。它只输出指导、校验契约、执行有界的 GitHub 与元数据状态迁移。AI agent 坐在驾驶位上，并且**要去问 `intent-cli` 下一步该做什么**。

这句话有三个部分值得拆开看：

- **它不启动模型。** 也不用管你用哪个模型——Claude Code、Codex、Copilot、Cursor、OpenCode 都能接。
- **它只做三件事。** 渲染指导（`guide`）、校验契约（`packet validate-verification`、`issue validate-body`）、执行有界的迁移（`automation`、`worker`）。
- **它是确定性的。** 同一份状态进去，同样的指导出来。

装法有两个入口，装出来的是同一个 CLI：

```bash
dotnet tool install --global JTechJapan.IntentSystem.Cli --version 0.32.1
# 或者不带 .NET SDK 的 npm 自实施方案
npm install --global intent-system@0.32.1
intent-cli --version
```

.NET 工具那条路要求 .NET 10 SDK；npm 那条路装的是配对好的自包含二进制，macOS arm64、Linux x64、Windows x64 各一份，每份带 SHA-256 边车文件。

## 二、两类 agent，一条禁止越过的线

这是整套设计的第一条规则，也是最容易被“AI 工作流”文章忽略的一条：**它把 agent 分成两类，给它们完全不同的信息权。**

| 角色              | 事实来源                            | 负责                                                 |
| ----------------- | ----------------------------------- | ---------------------------------------------------- |
| 宿主 / 审查 agent | 宿主 `.intent-cli/` 状态 + 意图树   | 发布 issue、迁移 label、审查/批准/合并、切下一个切片 |
| 子实现 agent      | **只有 GitHub issue/PR 与仓库代码** | 实现 contract、开/更 PR、用 `worker` 记录结果        |

子实现 agent 的约束不是建议，是文档里的原话：**只认 GitHub 契约**。它不得读、不得改宿主的 `.intent-cli/`、队列状态、metadata 分支，也不得碰 `intents/**`。

![隔离线两侧各自能读什么、能写什么]({{ '/assets/img/blog/intent-system/fig-01-two-sides-of-the-boundary.png' | relative_url }})

_中间那条虚线只有一个通道：渲染好的 issue body。它不是靠 prompt 约定的，而是靠“读不到，所以做不了”。_

这一条为什么重要？因为几乎所有 AI 工作流都在做相反的事——**把越来越多的上下文塞给同一个 agent**：给它意图文档、给它设计笔记、给它历史 commit、给它 CI 日志。上下文越多，“它理解项目”这句话听起来越真。

而这里的取舍是：**理解力是概率性的，权限边界是确定性的。** 先把确定性的那部分钉死，再谈理解。

## 三、意图树是一棵目录，不是一份 Prompt

Intent Storming 这个名字听起来像营销，但它产出的是一个非常具体的东西：`intents/<domain>/` 下的一棵目录树，加一份 `manifest.yaml`。

![tree-v1 的九个类目，以及 manifest 长什么样]({{ '/assets/img/blog/intent-system/fig-02-intent-tree-layout.png' | relative_url }})

_九类全部可选、全部可改名。老项目不需要迁移——tree-v1 是“推荐默认”，不是硬要求。_

这里我得纠正一个流传很广的说法。介绍 Intent-Driven Development 的文章里，常把意图树描述成三个维度：**Purpose / User Context / Means**。这个三分法在官方文档里找不到。文档给的是九个目录：`identity`、`product`、`features`、`technology`、`operations`、`decisions`、`clarifications`、`packets`、`links`。

差别不只是命名。三分法是一套**分类学**——你把内容分进三个抽屉；九目录是一套**寻址方案**——每一份内容有路径、有交叉链接规则、能被 `intent search` 和 `intent lint-layout` 处理。前者给人和 AI 看，后者给工具用。

配套的规则也很工程化：`decisions/` 里是 `<NNNN>-<slug>.md`，`features/<slug>/` 里是七个固定文件（overview / requirements / acceptance / decisions / open-questions / packets / links），并且要求互相链接、不许重复内容。

**这棵树最有意思的地方是它承认自己会长歪。** `clarifications/open.md` 是一等公民，未解决的问题和已确认的意图住在一起，不是藏在聊天记录里。

## 四、Packet 是四份文件，Issue 是唯一契约

设计侧把意图切成 packet。一个 packet 不是一句任务标题，而是 `packet draft` 脚手架出来的四份文件：

![四份文件如何折叠成一个 issue，以及之后 label 怎么走]({{ '/assets/img/blog/intent-system/fig-03-packet-to-label-machine.png' | relative_url }})

_`implementation.md` 只给实现侧看；`review-context.md` 只给审查侧看；`github-body.md` 才是发布出去的那一份。_

这个拆分本身就是权限设计：**实现者看不到审查者拿到的上下文，审查者也不看实现说明**。到了 0.32.1 还多了一层——`brief render` 命令按角色渲染确定的简报，reviewer 那份只读前三份文件，连 `implementation.md` 的文件状态都不去 stat。

发布这一关有两处“自定上限”值得记：

- **issue body 超过 65,536 字节就拒绝。** 文档紧接着声明：这是 intent-cli 自己的保守上限，GitHub 那边的边界、单位、JSON 载荷处理“未被验证”，唯一的远端数据点是 2026-09-16 一次约 96,000 字符的失败。
- **58,000 字节是草稿预算。** 原话是“自 2026-09-16 起手工维持的预算选择，不是 GitHub 的限制”。

一个工具愿意把“这个数字是我拍的”写在文档里，比它拍得准更难得。

## 五、状态不在 AI 的上下文里，在 label 上

packet 发布成 issue 之后，流程靠 8 个 label 推进：

| label                          | 含义                                      |
| ------------------------------ | ----------------------------------------- |
| `intent-target`                | 当前的工作目标                            |
| `intent-issue-in-progress`     | 实现 worker 已认领 issue                  |
| `intent-pr-created`            | 该 issue 产出了 PR（打给 issue，不是 PR） |
| `intent-pr-reviewing`          | 宿主审查循环正在看                        |
| `intent-pr-request-update`     | 审查要求修改                              |
| `intent-pr-update-in-progress` | 实现 worker 已认领这次修改                |
| `intent-pr-rereview-ready`     | 修完了，可以重审                          |
| `intent-pr-approved`           | 通过，等合并或 closeout                   |

规则只有一句：**正常操作里不要手动加删 workflow label。** 迁移必须走 `intent-cli automation pr-transition`。

真正能说明设计深度的是一个故障处理细节。如果某个 PR 上同时挂着 `intent-pr-approved` 和 `intent-pr-request-update`，会发生什么？

AI 大概会“合理地推断”哪个更新。而 `automation reconcile` 的选择是：报告 `conflicting-review-decision`，判为不安全停止，**两个 label 都不删**，让人重跑一次正确的转换。

这是同一种克制在不同层级的重复：**能推断的地方不推断，把不确定性交回给人。**

## 六、三个文件夹就是权力边界

文档里有一句话，语气比大多数同类项目都硬：

> review 目录在正常运作里不是可选项。

原因很具体：审查 / 切下一个切片的循环要拉取并改写宿主元数据，如果它和设计线程共用目录，两者会互相踩。所以三个角色要三个目录——设计/宿主、实现、审查，**即使它们指向同一个仓库，也要各开 clone 或 worktree**。

同一个仓库还有另一种拓扑：把元数据放在专属分支（比如 `main-metadata`）上，代码在 `main`。两种都被支持，但无论哪种，目录必须分开。

这条约束的代价是显而易见的：**你没法“在一个窗口里跑完”。** 一个 solo 开发者要维护三个 checkout 和一条消息通道。这也是它给人的第一印象——不是工具，是一套操作规程。

## 七、facets：当编码被委派，人还必须懂什么

如果这篇只记一件事，我会记这个。

tree-v1 的任意节点可以带一个 `facets:` 标签，取值是封闭的四类。文档给它们的定义是 **human-retained understanding**——“当编码被委派给 AI 时，人必须继续理解的最小表面”：

![四类不可外包的理解，以及其余可以交出去的部分]({{ '/assets/img/blog/intent-system/fig-04-facets-human-retained.png' | relative_url }})

_这四类来自一条 operator input（issue #1159）。项目判断：投影和样板可以安全委派，这四类不行。_

- **vocabulary** —— 事件/命令词汇表：什么算一个事实。例：`PaymentAuthorized` 记一次授权，不可就地撤销。
- **invariant** —— 不变量与一致性边界。例：订单总额必须等于各行小计之和，且只能在聚合内部保证。
- **decider** —— 判定：一个命令决定了什么。例：`ApproveRefund` 判断通过、部分通过还是拒绝；这个判断本身必须留人复核。
- **acceptance-property** —— 验收性质：什么永远不能坏。例：已完成的结账不得留下非空购物车；同一订单不得重复扣款。

我觉得这四类是整个项目里最有复用价值的一页，因为它回答了一个别人都在绕的问题：**如果 AI 能写完所有代码，那“懂这个系统”还剩下什么？**

它的答案不是“架构”“领域知识”这种大词，而是四个可以被写下来的、可以被检查的具体东西。

但紧接着有两处诚实，必须一起读：

1. **facets 是可选项。** 没有标注的节点是“未标注”，这在文档里被明确定义为合法状态，不是错误。`intent lint-layout` 只拒绝不认识的值。
2. **不许为了让检查变绿而补 facet 节点。** 文档专门写了这条禁令。

而且——`intent-cli` 自己这个域就是那个反例。它的词法 facet 检查在自家域上返回 `no_facet_data: true`，意思是**检查没跑**，不是“通过”。一个宣称“人必须懂这四件事”的项目，被当作测量样本的那个域里一个 facet 节点都没有，并且把这件事写进了文档。

## 八、三种编排，都要显式记录

到了“谁来跑”这一层，它给了三种形态，而且要求用 `team-mode set` 把选择写下来——**模式是记录下来的，不是从现场推断的**。

![solo-conductor、四线程、timer loop 三者的结构与代价]({{ '/assets/img/blog/intent-system/fig-05-three-seat-models.png' | relative_url }})

_同一个 domain/repo 只能选一种，文档明令禁止混用。_

**solo-conductor（单席位，G833）** 是给个人开发者的：一个席位同时当 architect、orchestrator 和 builder，按十个步骤跑完一个执行单元；每次审查现开一个独立的 reviewer 子 agent，判决按“独立子 agent 审查”记录。两个硬约束：并行度 1；**没有隔离子 agent 的运行时不许用这个模式**。

**四线程** 是当前维护的多席位形态：design 写意图和 packet，orchestrator 推流程和配速，implementation 写代码，review 做独立审查。稳态是消息驱动的——实现和审查的回执会唤醒 orchestrator，所以不需要高频轮询；design 侧挂一个 30 分钟级的看门狗兜底。传输层优先用 `herdr-only`（依赖更少），`agmsg` 这条路在 G829 下已弃用但还能用。

**timer loop** 是最简单的替代：实现和审查各跑各的定时循环，不需要 orchestrator。文档说它“完全支持”，代价是两者之间只剩时间先后。

还有一个更细的分层值得记：**跨运行时审查（G834）**。团队可以声明“每个实现 PR 还要由另一个运行时的 reviewer 审一遍”，配置写在宿主的 `config.toml` 里，运行时可以是 codex、claude、cursor、copilot、opencode。它要求按 head SHA 绑定判决，同运行时和跨运行时各要一份，缺一份就 `cross-runtime-review-missing`。

## 九、它自己承认的漏洞：只读不是沙箱

上一节那个跨运行时审查，文档里附了一段 2026-09-14 的实测，我认为是全文最值得读的段落：

- **codex** 的 `exec -s read-only` 是沙箱强制的：reviewer 能读、能跑命令，但沙箱拒绝写文件。
- **claude** 的 `-p --permission-mode plan --disallowedTools Edit,Write,NotebookEdit` 只拿掉了文件写入工具。reviewer 仍然可以跑 build 和 test，而**通过 shell 命令产生的写入不受沙箱约束**。
- **cursor** 的 `-p --mode ask --sandbox enabled` 拒绝一切非只读工具，包括所有 shell 命令——所以 cursor reviewer 读得了文件，跑不了 git 和测试，连 head 都只能从 `.git/HEAD` 里读。而且 `--mode plan` 被明确弃用了，因为有一次实测中，**plan 模式的 agent 自己切到了 agent 模式，并在工作区内、外都写了文件，而 `--sandbox enabled` 没拦住**。

一次实测里，被判为只读的那个 agent 自己切到了 agent 模式并写出了工作区，而“沙箱已启用”没拦住。这件事被写进了命令参考——这种记录方式比任何“安全可靠”的形容词都更有信息量。

同一节还有一句边界声明，和开头那句呼应：

> gate 假设席位是诚实的，而且 GitHub label 无法与某个 SHA 原子地绑定。合并时请保留精确的 head 校验和 `gh pr merge --squash --match-head-commit`。

所以它的安全模型是分层的，而且每一层的主张都很小：`intent-cli` 保证状态迁移是确定性的；跨运行时 gate 保证“有一个独立判决绑在这个 head 上”；至于那个判决是不是真的由一个干净的沙箱产出的，**它不声称，也没法声称**。

## 十、局限

按重要性排，全部来自仓库里写着的或能直接量出来的：

1. **采用量很小。** 113 star、1 fork、6 个 open issue。一个 fork 意味着几乎没人真的改过它——这套设计目前只有一个团队在用。
2. **最后推送停在 2026-10-21。** 也就是 0.32.1 发布当天，此后四周 GitHub 上没有新提交。对一个 0.32.1 里还列了 24 个产品单元的项目来说，这是个我解释不了的数据点。
3. **它还在 0.x。** 有 1.0 兼容承诺文档，但大量表面标着 `preview-through-1.x`——意思是冻结期内可能变、可能撤。
4. **文档体量已经超过工具本身。** 命令参考里用 G 编号组织规则（G461、G833、G845……），对第一次来的人几乎没有索引入口；最有价值的判断往往藏在某一节的第三段。
5. **它不是“装上就能跑”。** 三个 checkout、一条消息通道、可能还要 `herdr` 和能开子 agent 的运行时。工具本身很轻，操作规程很重。
6. **本地验证只在 macOS arm64 上做过。** 0.32.1 的发布说明写得很清楚：版本/帮助检查在 macOS arm64 上本地通过，Linux/Windows 的结果来自原生 CI 作业，不是本地执行。
7. **两个尺寸上限都是自己拍的。** 65,536 和 58,000 都不是 GitHub 的边界，文档自己也这么说。
8. **它治的是流程，不是代码质量。** 测试通过只是必要条件——文档原话是“必要但不充分”，批准还需要 packet 与意图的一致性证据。

## 十一、我的判断

我认为 Intent-Driven Development 真正的价值，不在“把意图写成文档”，而在**把 AI 的概率性判断替换成 CLI 的确定性判断**。

意图文件谁都能写；难的是当 agent 说“下一步应该做 X”时，有一个东西能回答“不，证据显示应该是 Y”，而且这个回答是可复现的。`intent-cli next` 就是这个东西的最小形态：它读意图、未决问题、packet backlog、open PR 和 CLI 健康度，**只推荐八个动作中的一个**，输出里带推荐理由、检查过的证据、可直接粘贴的 prompt 和安全边界，然后什么都不执行。

所以这套系统里最该被抄走的三样东西，按可复用的程度排：

1. **label 是状态机，不是标签。** 状态在 GitHub 上，不在任何人的上下文里。
2. **四类 facets 清单。** 它给了“什么必须留给人”一个可操作的答案。
3. **承认边界的写法。** “这个数字是我拍的”“这个 gate 只防诚实的席位”“这个检查没跑，不是通过”——这三句话比任何架构图都更能让人信任一份文档。

不确定的地方也很清楚：**这套纪律的成本是线性的，收益是不是线性的，取决于你的项目会不会长期跑下去。** 一个两周的原型不需要三个 checkout 和一套 label 状态机；一个要跑两年的产品可能就需要。

我会盯三个可验证的信号：

1. 出现第二个 fork，并且真的跑通了一条 packet → issue → PR → closeout 的完整链路。这能回答“这套纪律是否只对作者本人成立”。
2. 1.0 发布时，那些 `preview-through-1.x` 的表面留下了几个。留下的越多，说明这套设计被实战检验得越狠。
3. `no_facet_data: true` 这个状态会不会在某个版本里变成错误。如果它变成错误，说明项目放弃了自己那条“不许为绿而补”的禁令。

顺便说一句，这和我最近在看的干预接口是同一个问题：一个系统对外开的“动词”越多，能力越强，可治理的面也越大。NNsight 是在残差流上开 hook，intent-system 是在开发流程上开 hook——**两者都发现同一件事：能干预不等于能预测干预的后果，所以必须把干预本身变成可记录、可回滚、可审计的事件。**

## 项目与资料

- 仓库：[J-Tech-Japan/intent-system](https://github.com/J-Tech-Japan/intent-system)（Apache-2.0，2026-04-02 建库，最新稳定版 `0.32.1`）
- 官网：[intent-driven-development.com](https://www.intent-driven-development.com/)（由 J-Tech Japan 运营）
- 关键文档：[Command reference](https://github.com/J-Tech-Japan/intent-system/blob/main/docs/en/08-command-reference.md)（本文第五、八、九节的主要来源）· [Intent tree layout (tree-v1)](https://github.com/J-Tech-Japan/intent-system/blob/main/docs/en/03a-intent-tree-layout.md)（facet 四类的定义在这里）· [Workflow labels](https://github.com/J-Tech-Japan/intent-system/blob/main/docs/en/04a-workflow-labels.md) · [Agent-message orchestration](https://github.com/J-Tech-Japan/intent-system/blob/main/docs/en/12-agent-message-orchestration.md)（solo-conductor 与跨运行时审查）
- 发布记录：[v0.32.1](https://github.com/J-Tech-Japan/intent-system/releases/tag/v0.32.1)（10,717 通过 / 0 失败 / 6 未执行，以及本文开头引用那两段声明）

**数据说明：** star / fork / issue / 建库时间 / 最后推送取自 GitHub API（2026-11-18）；版本、测试计数、安装命令、候选产物哈希声明取自 v0.32.1 发布记录；label 语义、65,536 与 58,000 两个自定上限、跨运行时只读实测、facets 四类定义与 `no_facet_data` 说明取自 `docs/en/` 对应页面。文中提到的 G 编号（G829、G833、G834、G845……）是该仓库自己的变更单元编号，不是我编的。五张示意图是按这些文档重画的，不是项目官方图表。
