---
layout: post
title: Diagram Design：50 种图表是目录，能拒绝你的检查才是产品
date: 2026-11-17 14:55:00 +0800
thumbnail: assets/img/blog/diagram-design-agent-skill-lint.jpg
description: 67,720 星的 Agent Skill：50 份图表参考合计 481 KB，画一张流程图却只读 1,079 字节；拆解它把审美写成 4px 网格、9 个节点上限、六条连线规则和一组会失败的检查。
tags: [AI, 开源, 开发者工具]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/diagram-design-agent-skill-lint.jpg
---

**67,720。**这是 2026-11-17 的 star 数。仓库建于 2026-04-16，也就是说这七个月里它涨了六万七千星。

第二个数字是 **1,079**：画一张流程图时，agent 真正读进上下文的那份类型参考有多少字节。

第三个数字更小，也不在任何宣传文案里：**9**。一张图最多 9 个节点，超过就该拆成两张。

项目叫 Diagram Design，一套给 AI agent 用的图表设计 skill：50 种图表类型，产物是一个自包含的 HTML 文件，图本身是内联 SVG。

- 源码：[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)（MIT，4,535 个 fork）
- 官网：[diagramdesign.dev](https://diagramdesign.dev)，画廊：[cathrynlavery.github.io/diagram-design](https://cathrynlavery.github.io/diagram-design/)
- 作者：Cathryn Lavery（LittleMight），做过 SELF Journal 那类纸本工具，写设计和 AI
- 安装：`npx skills add cathrynlavery/diagram-design`

我把 `SKILL.md`、`style-guide.md`、`onboarding.md` 和 `scripts/` 的清单读了一遍。读完的判断是：**这个项目的产品不是那 50 种图，而是一份能被检查的审美契约。** 本文只讲后者怎么被写出来。

## 一、它要解决的问题：AI 不缺理解，缺约束

让 Claude Code 或 Cursor 画一张系统架构图，你大概率会拿到这种东西：一堆大小相同的圆角矩形、几条交叉的斜线、一个渐变背景、每个框都被标成“重要”。

内容基本没错。它知道 React 在左边、PostgreSQL 在下边、Redis 该挂在后端旁边。**它缺的不是理解，是有人告诉它：一次只准用两个 accent 色、连线只能是直角、标签必须让开 6 像素。**

Diagram Design 做的就是把这些“有人告诉它”，写成 50 份可加载的参考文件。

它和现有工具的差别，README 自己列了一张表，我核对过，没有夸大：

|        | Mermaid / PlantUML | draw.io / Excalidraw               | Diagram Design                         |
| ------ | ------------------ | ---------------------------------- | -------------------------------------- |
| 怎么画 | 写文本             | 手拖                               | 对 agent 说                            |
| 布局   | 渲染器自动         | 手动                               | agent 在 4px 网格上摆，CI 查重叠与裁切 |
| 长相   | 渲染器主题         | 你画成什么样就什么样               | 一套编辑式风格，可换肤                 |
| 输出   | 一段会渲染的文本   | 可拖拽的 `.drawio` / `.excalidraw` | 一个内联 SVG 的 HTML，可导 SVG / PNG   |
| 事后改 | 改文本             | 改画布                             | 再问一次 agent，或直接改 SVG           |

表下紧接着一句我很意外的坦白：**“输出质量取决于你用的模型，同一段 prompt 两次可能摆得不一样。”** 作者没有藏这个。

## 二、50 种是目录，1 KB 才是设计

先看一个数字，它解释了为什么“50 种”没有把上下文撑爆。

![50 份类型参考的体积分布：最大 43,216 字节，中位数 6,798，最小的流程图参考 1,079 字节]({{ '/assets/img/blog/diagram-design-agent-skill-lint/fig-01-reference-size-tail.png' | relative_url }})

_按 GitHub 目录接口的文件体积统计，`skills/diagram-design/references/type-*.md` 共 50 份、492,155 字节；柱状图按体积降序。_

- **50 份合计 492,155 字节（约 481 KB）**，平均 9,843，中位数 6,798。
- 最重的是 `type-line.md`：**43,216 字节**，因为折线本体之外，它还要覆盖斜率图、山脊图、流图、bump 四个变体。
- 最轻的是 `type-flowchart.md`：**1,079 字节**。
- `SKILL.md` 本身 31,967 字节，每次都读。

所以“画个流程图”这件事的真实成本是 **31,967 + 1,079 = 33,046 字节**。50 份参考全塞进去是 481 KB，压到 33 KB，差的这近 15 倍就是渐进式加载的全部意义。

细看 `SKILL.md` §3 的加载规则，它不是简单地“按需读一个文件”：先判断这件事是不是**行为**驱动（排队、容量、权限边界、生命周期），如果是，先读 `semantic-patterns.md` 选一个语义模式，再落到最接近的可视类型上。九个模式里有“扇入队列/瓶颈”“安全铺装路”“补偿式安全层”这种名字——它们描述的是图要让人看见什么，而不是图长什么样。

这也是我在这篇里最想强调的一层：**它把“选哪种图”和“图长什么样”拆成了两个决策。** 模型先答前者，再答后者，出错时你能定位到是哪一步错了。

## 三、预算：9 个节点之后，图就该拆开

`SKILL.md` §7 有一张四行的预算表，全篇最硬的约束在这里：

| 项目            | 上限 |
| --------------- | ---- |
| 节点            | 9    |
| 箭头 / 状态转移 | 12   |
| accent 元素     | 2    |
| 注释卡片        | 2    |

跟着一句判词：**“超过 9 个节点，它多半是两张图。”**

![同一套链路：左边 13 个节点、5 处 accent，右边 7 个节点、1 处 accent]({{ '/assets/img/blog/diagram-design-agent-skill-lint/fig-02-complexity-budget.png' | relative_url }})

_左图是 §9 删除测试要打回的样子：五个框一样重，读者找不到重点。右图删掉 6 个“永远和邻居一起出现”的框。_

配套的是 §9 的四问删除测试：能不能删一个节点、能不能合并两个节点、能不能删一条箭头、能不能删一个标签。作者在 README 里写的原话是：**“质量最高的动作通常是删除。”**

这句话听起来像设计鸡汤，但落在这里是可执行的：9 是数字，12 是数字，“能合并吗”有明确答案。**它把一个审美辩论变成了判断题。** agent 能执行，人也能验收——图上数一数节点就知道有没有超标。

## 四、六条连线规则：可以被拒的错误

如果只让我从仓库里抄一样东西，我抄这六条。

![三处会被拒的连线：斜线、压在连线上的标签、两条线共用出口；右边是同一张图的合法改法]({{ '/assets/img/blog/diagram-design-agent-skill-lint/fig-03-connector-rules.png' | relative_url }})

_`primitives-core.md` 的 mandatory connector rules。§9 逐条检查，`verify_geometry.py` 逐条验证。_

六条规则是：

1. **只走直角。** 两点不同轴时必须用 `r=8` 的圆角直角弯（9 个节点以上的密集布局放宽到 `r=6`），斜线直接判失败。
2. **标签必须让开。** 每个箭头标签下面有不透明遮罩，和线之间留 6–10px，站在线的侧边，不能压线。
3. **不许重叠。** 平行走线间距 ≥12px，交叉处用桥接。
4. **扇出要分点。** 同一个框边上的多条线，各自取 `L * k / (N + 1)` 的位置，彼此 ≥12px。
5. **不许穿过后画的框。** 只能绕路；实在绕不开时改虚线并去掉箭头。
6. **遮罩不许压后画的节点。** 标签先画，节点后画就没事，反过来就是错的。

这六条之所以值得抄，是因为它们是“AI 味”里**可以被代码判定**的那一部分。斜线、压线标签、共用出口——三个词都能写成几何断言。仓库里还有一批按类型写的 `test-verify-*.py`——我数到 38 个，而树接口的列表是被截断的，实际只会更多。

## 五、设计系统：一个 accent，三种字，4px 网格

`references/style-guide.md` 是唯一允许出现十六进制色的地方，其余文件只写语义角色名（`paper`、`ink`、`accent`）。这不是洁癖，是为了让换肤只需改一个文件。

| 角色     | 默认浅色  | 用途                   |
| -------- | --------- | ---------------------- |
| `paper`  | `#f5f5f5` | 页面底色、默认节点填充 |
| `ink`    | `#2d3142` | 正文、主描边           |
| `muted`  | `#4f5d75` | 次要文字、默认箭头     |
| `accent` | `#bf4520` | 1–2 个焦点元素         |
| `link`   | `#2e5aa8` | HTTP / API、外部调用   |

字体只有三种，分工写死：Instrument Serif 负责标题和斜体旁注，Geist sans 600 负责节点名，Geist Mono 负责端口、URL、字段类型这类技术内容。作者专门写了一行禁令：**mono 不许当“开发感”滤镜用，更不许用 JetBrains Mono。**

网格规则更硬：所有坐标、宽高、间距都能被 4 整除；描边 0.8 / 1 / 1.2 三档；圆角只用 4 / 6 / 8，最大 10；阴影一律没有。

还有一条容易被忽略的字体预算：中日韩标签每个全角字符按 1em 计宽，9px 的 mono 子标签不许放汉字，汉字的字号地板是 12px——放不下就砍字，不许缩字号。宽度预算写进了 `verify-treemap.py`，矩形树图的单元格标签会按它检查；12px 的字号地板则只能靠 §9 的清单自查。

## 六、品牌：一个网址换五个 token

这是整个项目里我最想推荐的功能，也是最容易被低估的。

![onboarding 流水线：从网址取渲染值，映射成五个语义角色，再过对比度闸门]({{ '/assets/img/blog/diagram-design-agent-skill-lint/fig-04-onboarding-tokens.png' | relative_url }})

_`onboarding.md` 支持三条来源：网址、已安装的 skill、本地设计系统目录。三者走同一条流水线。_

你说一句 `onboard diagram-design to https://你的站点`，它会：抓页面 → 取 `body` / `h1` / `code` 的渲染值 → 映射成五个语义角色 → 过对比度检查 → 给你一份 diff → 你批准后才写回 `style-guide.md`。

有几处细节比宣传语更值钱：

- **抓取之前必须弹信任确认。** 外部 URL 要单独批准，“你给了网址”不算批准。抓回来的 HTML 一律当不可信数据处理。
- **首用有闸门。** 新项目第一次画图时，如果 style-guide 还是默认值，它会停下来问你要不要先换肤，而不是默默给你一张灰图。
- **对比度是硬门槛。** 品牌原色的 atomic-tangerine 在 `paper` 上只有 2.86:1，压深到 `#bf4520` 才到 4.71:1；现在 `soft` 5.34、`link` 6.13、`muted` 6.11，深色皮肤里 accent 5.21。这些数字由 `verify-contrast.py` 计算，阈值被写成了契约。
- **能存 profile。** 一个客户一套皮肤，项目里放一个 `.diagram-design` 标记文件就能选中对应的 profile，不用每次重新 onboard。

同一个文件改一次，50 种图全部换肤。这和“每张图在 prompt 里写一句用橙色”，效率差着一个数量级。

## 七、导入：四个旋钮和一张收据

导入现有的图，它做的是**重画**，不是转换。

![导入管线：四个 Python 抽取器把源文件读成结构化摘要，再按四个旋钮重画，最后产出 HTML 与一份 fidelity ledger]({{ '/assets/img/blog/diagram-design-agent-skill-lint/fig-05-import-dials.png' | relative_url }})

_抽取器只解析文本：不渲染、不跑浏览器、不联网、不跟随点击目标。_

- **四个源格式**：draw.io（含压缩负载和 PNG/SVG 内嵌图）、Mermaid（`.mmd` 或 Markdown 里的 fenced block）、Excalidraw、PlantUML（仅时序图和类图）。
- **四个旋钮**：Format 4 种、Size 10 个预设（`doc-inline`、`slide-16x9`、`print-a4-landscape` 等）、Detail 3 档（节点上限 24 / 12 / 7）、Audience 3 档（engineer / mixed / executive，只改措辞不改数量）。
- **一张收据**：Fidelity ledger 会写出哪些节点被合并、折叠、丢弃。比如 `Detail: balanced · 12 个源节点 → 画 8 个`，`Collapsed: 判断策略 → 网关上的边标签`。

四个旋钮里，我认为 **Audience** 是最聪明的设计。同一份架构图，给工程师看写 `Auth Service / JWT · RS256 · :8443`，给管理层看写 `Sign-in`，节点数不变、连线不变，只是标签换了措辞。这比“再画一张给老板看的简版”省事得多。

## 八、它自己的数字对不上

写到这里该说实话了。这个项目的“50 种”至少有三套口径：

| 出处                        | 说法                                  |
| --------------------------- | ------------------------------------- |
| README 首屏、`SKILL.md`     | Fifty / 50 种                         |
| `references/type-*.md` 目录 | 50 个文件（我按树接口数过）           |
| GitHub 仓库简介             | 45 diagram types                      |
| `CHANGELOG.md` 2.6          | “The taxonomy now stands at 44 types” |

宣传页先行、简介和 changelog 落后，这是开源项目的常态，不算问题。但它提醒一件事：**看到“支持 N 种”时，去数目录，别读标题。**

其它可核对的版本信息：`SKILL.md` 的 metadata 里还是 2.6 版，最后一次推送是 2026-11-12，还有 38 个开放 issue。CHANGELOG 的 Unreleased 里躺着两条对普通用户挺重要的改动：**WCAG 对比度闸门**和**系统字体离线模式**（用 `system` 字体源，产物完全不联网）。也就是说，离线可用这件事在 main 上已经有了，还没发版。

## 九、局限

1. **闸门是自愿的。** 那张 §9 检查表写在 `SKILL.md` 里，由模型自己执行。仓库的 CI 保护的是它自己的示例图，不是你刚生成的那张。除非 agent 真的跑了 `self_check.py` 和 `verify_geometry.py`，否则没有任何东西能拦住一张斜线乱穿的图。
2. **输出不可拖拽。** 它是 HTML + SVG，不是 draw.io 那种画布源文件。改图要么再问一次 agent，要么手改 SVG；放进 Git 也 diff 不出人类可读的差异。
3. **结果不稳定。** README 自己承认同一段 prompt 两次可能不一样。约束降低方差，不消除方差。
4. **质量吃模型。** skill 提供的是约束和执行顺序，不是能力。用弱模型跑，你得到的是“遵守了 4px 网格的平庸图”。
5. **依赖链不短。** PNG 导出要 Playwright + Chromium，几何检查要 Python 3。缺了这些，闸门就退化成自觉。
6. **50 种里有一半你一辈子用不上。** SBGN、轴测平面图、Wardley map 都在里面，那是列表长度，不是能力证明。

## 十、我的判断

这个项目最值得学的，是把“好看”拆成一组能被拒绝的条件：4 整除、9 个节点、2 个 accent、6 条连线规则、4.71:1 对比度。**每一条都能被代码判定，所以每一条都不依赖模型当天的心情。**

接下来我会做三件可验证的事：

- **借用预算 + 六条规则，而不是借用它的图。** 我在 NNsight / pyvene 那类干预实验里画的激活补丁示意图，很容易一路长到十几个节点。先用 9 个节点的上限重画一遍，看是不是真的更好读——这个实验一周内能做完。
- **把它的 lint 当验收器用。** 几何校验和对比度校验都是纯 Python，可以直接套在已有 SVG 上：不生成图，只检查图。这比再写一套生成器便宜。
- **给“仓库 → 图”的管线加一张收据。** 自动从代码库生成的架构图，最危险的不是画得丑，是悄悄漏掉了三个模块。把 Fidelity ledger 那种“我少了什么”写进产物，比“图看起来对”可信得多。

50 种图表是这个项目的目录页；真正值得读的是后面那 481 KB 里反复出现的同一句话：先删，再画。

## 项目与资料

- 仓库：[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)（MIT License）
- 官网：[diagramdesign.dev](https://diagramdesign.dev) · 画廊：[Diagram Gallery](https://cathrynlavery.github.io/diagram-design/)
- 关键文件：[`SKILL.md`](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/SKILL.md) · [`style-guide.md`](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/style-guide.md) · [`primitives-core.md`](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/primitives-core.md) · [`onboarding.md`](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/onboarding.md) · [`CHANGELOG.md`](https://github.com/cathrynlavery/diagram-design/blob/main/CHANGELOG.md)
- 数据来源：仓库文件体积与类型数量取自 GitHub 树 / 目录接口（2026-11-17 快照）；star、fork、创建与推送时间取自仓库元数据；设计参数、节点上限与连线规则取自 `SKILL.md` 与 `references/style-guide.md`。
