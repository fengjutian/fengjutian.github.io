---
layout: post
title: Everything Project：50 个应用、0 个前端框架，它在重写「一个软件该有多大」
date: 2026-11-17 13:30:00 +0800
thumbnail: assets/img/blog/everything-monorepo-fifty-apps.jpg
description: 51 个目录、50 个应用、0 个 UI 框架、15 个 AGPL：拆开 HeyPuter 的 monorepo，看它怎么把 Excel、Photoshop、AutoCAD 各压成能单独 npm run dev 的目录，以及这份压缩的代价落在哪里。
tags: [开源, 开发者工具, 架构设计]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/everything-monorepo-fifty-apps.jpg
---

51 个目录。50 个真正能跑的 Web 应用。0 个 React / Vue / Svelte 依赖。15 个 AGPL 许可证。

这四个数字指向同一个仓库：HeyPuter 的 [everything](https://github.com/HeyPuter/everything)。它 2026-10-13 建库，五周涨到 8,581 star，口号是「The world's software. Rebuilt, and open-sourced.」——把 Excel、Photoshop、AutoCAD、Slack、Salesforce 这些东西逐个重写一遍。

大部分介绍会停在这里：清单很长，野心很大，浏览器很强。但清单不是项目。**这篇只讲一件事：它是怎么把「一款软件」压缩成一个目录的，以及压缩省下的和挪走的分别是什么。**

## 一、三个数字

**51。**`src/` 下的目录数。其中 50 个有 `package.json`，各自 `npm install && npm run dev`，也各自对应一次部署；第 51 个是 `src/assets`，CI 的原话是「index.html, no source yet」，第一版过滤就把它跳过了。

**0。**50 个 `package.json` 里，`react`、`vue`、`svelte`、`angular` 的出现次数。不是「用得少」，是一次都没有。

**15。**自带 AGPL-3.0 全文的目录数。剩下 35 个不声明许可证，继承仓库根目录那份 1,080 字节的 MIT。

第三个数字最容易被略过，但它决定了一个项目能不能被拿去商用。后面第九节专门讲。

## 二、它是什么：九类五十个

README 把应用分成九类，我按目录逐个核过：

| 类别       | 数量 | 代表应用                                                          | 对标                               |
| ---------- | ---- | ----------------------------------------------------------------- | ---------------------------------- |
| 办公       | 7    | Spreadsheet / Documents / Presentation / Whiteboard / PDF / Notes | Excel、Word、PowerPoint、Airtable  |
| 协作       | 6    | Meetings / Teamchat / Email / Calendar / Contacts / Signatures    | Zoom、Slack、Gmail、DocuSign       |
| 创意       | 6    | Photo / Video / Vector / Audio / Music / 3D Studio                | Photoshop、Premiere、Maya          |
| 工程       | 4    | CAD / Parametric / Circuits / Building Design                     | AutoCAD、SolidWorks、Altium、Revit |
| 效率       | 5    | Tasks / Projects / Wiki / Time Tracking / Surveys                 | Todoist、Trello、Notion            |
| 财务       | 4    | Accounting / Invoicing / Expenses / Cap Table                     | QuickBooks、Carta                  |
| 业务       | 12   | CRM / Help Desk / POS / Inventory / Hiring / Legal / Fleet …      | Salesforce、Zendesk、Square        |
| 开发者工具 | 1    | API Client                                                        | Postman                            |
| 游戏       | 5    | Chess / Backgammon / Checkers / Solitaire / Sudoku                | —                                  |

这张表读起来像产品清单，其实是目录清单。每个条目对应一个文件夹，文件夹里有自己的 `package.json`、自己的 `vite.config`、自己的端口、自己的 `dist/`。**它们之间没有共享的构建，没有共享的组件包，也没有一条命令能把 50 个一起启动。**

## 三、仓库的形状

先把字节算清楚，因为「50 个应用」这个说法会让人以为仓库是均匀的。实际不是：

![仓库的字节构成，以及 50 个应用的许可证分布]({{ '/assets/img/blog/everything-monorepo-fifty-apps/fig-01-repo-anatomy.png' | relative_url }})

_1,327 MB 里只有 168 MB 是应用源码；单是 `src/whiteboard/tmp/` 就占了 551 MB。_

`src/whiteboard/tmp/` 里有 4,375 个文件，是一批 WCAG 无障碍审计的导出页，大的单个 3 MB，已经提交进仓库。CI 的 checkout 那一步用了 `filter: blob:none` 加 `sparse-checkout: .github`，注释写得很直接：「keeps whiteboard's tracked tmp/ folder out of this job」——只取文件名，不取内容，就为了不让这 551 MB 进流水线。

这件事值得记下来，因为它和「重写世界软件」是同一枚硬币的两面：**项目的组织能力全部押在目录约定上，而目录约定管不住任何一个目录里放什么。**

## 四、没有 workspace 的 monorepo

「Monorepo」这个词通常意味着 Nx、Turborepo、pnpm workspaces 那一套：统一依赖、任务图、增量构建。Everything 一个都没有——根目录下没有 `package.json`。

它有的是三个东西：

**第一，CI 靠约定发现应用。**`ci.yml` 里只有一句 `git ls-tree -r --name-only HEAD src | grep -E '^src/[^/]+/package\.json$'`，凡是有 `package.json` 的目录就是一个应用。然后只跑改动过的那些，测试用 `vitest --changed`，`spreadsheet` 和 `documents` 各切 4 个分片，其余的整包跑。

**第二，dev server 伪装成子域名。**`dev/puter-localhost.mjs` 只有 728 字节，一个 Vite 插件，把 `npm run dev` 打印的地址从 `localhost:5173` 改成 `cad.puter.localhost:5173`。注释解释了为什么这样够用：浏览器本来就把 `*.localhost` 解析到回环，Vite 也接受 `.localhost` 主机名，「nothing else needs configuring」。

**第三，部署是一张 51 项的清单。**根目录的 `amplify.yml` 里，每个应用一个 `appRoot`，各自 `nvm install 22`、`npm ci`、`npm run build`、发布 `dist/`。

![仓库到 51 次部署的链路，以及后端实际所在的位置]({{ '/assets/img/blog/everything-monorepo-fifty-apps/fig-04-one-repo-many-subdomains.png' | relative_url }})

_一份仓库，51 个 Amplify 应用；后端不在维护者手里（右半部分第八节展开）。_

所以严格说，这不是 monorepo，是**一个文件夹里的 51 个 polyrepo**。共享的只有两样：那份 728 字节的 Vite 插件，和一份 CI 工作流的 YAML。

## 五、四层，和一个借来的底座

一个应用长什么样？把 50 个目录摊开看，结构几乎是一致的四层：

![每个应用的四层结构，以及底部那条借来的底座]({{ '/assets/img/blog/everything-monorepo-fifty-apps/fig-02-app-anatomy.png' | relative_url }})

_四层各自实现；只有最底下那一层是同一个东西。_

**界面层**是原生 DOM 加 canvas。没有虚拟 DOM，没有响应式框架，网格、面板、菜单、对话框全部手写。代价是每个应用都要自己写一遍焦点管理、键盘导航和无障碍语义；好处是没有一层抽象横在“我点了这个像素”和“它变了”之间，这对 CAD 的对象捕捉、图像编辑器的画布变换这类交互是决定性的。

**内核层**是这个项目真正的工程量所在，而且每个应用的内核都不一样：

- Spreadsheet 自己写了公式引擎，README 说支持 **510 个以上函数**，包括 `LAMBDA`、`LET`、`GROUPBY`、动态数组溢出、`QUERY` 查询语言，还有 `IMPORTRANGE`；`.xlsx` 用的是真实的 xlsx 文件，靠 vendored 的 SheetJS 读写，再补上 SheetJS 社区版不支持的样式和图表。
- Wiki 自己写了块编辑器，用 Yjs 做 CRDT 合并。
- CAD 自己写了几何内核、R-tree 拾取和 DWG 读写。

**计算层**把重活推出主线程：Rust、OpenCascade、Tesseract 这类东西编译成 WebAssembly，跑在 Web Worker 里。

**渲染层**最终只有一块 canvas：WebGPU 优先，WebGL2 兜底。

而「借来的引擎」这条界线划得挺清醒：**格式与算法可以借，产品逻辑必须自己写。**SheetJS（Apache-2.0）、Yjs（MIT）、ag-psd（MIT）、OpenCascade（LGPL-2.1，以独立可替换的 wasm 模块形式随包发布）、Rust 编译的 `photo-engine.wasm`——每一个都能在 `THIRD_PARTY_NOTICES` 里找到出处。

复用的方式也值得说一句：目录之间没有共享包，**代码是复制过去的**。Wiki 的协作层注释写着「Request authentication and the deployment flow are adapted from `src/whiteboard`」；Spreadsheet 的邮件 worker 写着「adapted from the Calendar app's」。省掉了抽象层的成本，代价是同一个 bug 要在 N 个目录里修 N 次。

## 六、Photo Studio 的账

Photo Studio（`ps.puter.com`）是这个仓库里最像「不可能在浏览器里做」的那个。它的 README 有 4 万字节，我只挑三件能验证的事。

**第一，文档模型是图块化的不可变快照。**破坏性像素内容存成 256 px 的图块，历史状态之间共享，改一笔只分配被碰到的图块，撤销就是换一个引用。合成器只上传变了的图块。

**第二，GPU 有两条路。**WebGPU 是主合成器，WebGL2 是备用路径，两套 shader 行为对齐。这也意味着它需要安全上下文（HTTPS 或 localhost），部署上没有退路。

**第三，上限写得很坦白。**这一节我认为比功能列表更值得读：

| 项         | 上限 / 代价                                                           |
| ---------- | --------------------------------------------------------------------- |
| 像素层位深 | 8 位/通道；16、32 位只支持导入与合成，破坏性工具会转成 8 位           |
| 文档尺寸   | 单边 8,192 px，总共 2,400 万像素                                      |
| AI 功能    | 需要 Puter 账号；生成结果约 100 万像素（Edit with Prompt 长边 1,024） |
| 实时协作   | 每个参与者都要有 Puter 账号，评审链接也一样                           |
| 并发写入   | 同一个 256 px 图块上的并发绘画只保留一个人的版本                      |

这些不是「待办事项」，是架构的边界。一个浏览器里的 Photoshop 替代品，被三件事卡住：内存、WebGPU 的可用性、以及「真实像素数据必须活在某个人的存储里」。

顺带说一句它的许可证：**这张表里的每一个功能，都在 AGPL-3.0 之下。**如果你想把它做成一个内部设计工具再对外提供服务，得先读第九节。

## 七、CAD 的一条直线

CAD（`cad.puter.com`）是另一个方向：不追求像素，追求精确。它没有框架，没有自建服务器，用 Vanilla JavaScript + WebGL2 + Vite。

从命令行敲进 `LINE 0,0 @200<30` 到屏幕上出现一条线，中间是五段：

![一条 LINE 命令穿过的五段代码]({{ '/assets/img/blog/everything-monorepo-fifty-apps/fig-03-cad-command-path.png' | relative_url }})

_命令行、交互、模型、细分、渲染——五段都在这个目录里，没有一段来自框架。_

几个能说明「精确」这件事有多贵的细节：

- **空间索引是 R-tree**，拾取、框选、对象捕捉都走它，而不是遍历实体。
- **模型空间按约一千个对象切块**，每块有自己的 GPU buffer，改一个对象只重传它所在的那块。
- **线是 instanced quad**，线型和抗锯齿在片元着色器里算，顶点只描述实例。
- **坐标拆成高低两个 float**，图纸离原点再远，拾取和渲染也不抖。

文件格式是它最硬的一块：DWG 导入支持 R13 到 2018，导出写 DWG 2004；DXF 走 R2000 ASCII；原生格式 `.cad` 是压缩 JSON。**DWG 的读写是照着 Open Design Specification 自己实现的**，跑在 Web Worker 里。

然后是这个项目最诚实的一行：**Early Alpha。「请不要依赖它处理正式工程项目，重要图纸请自己留副本。」**

## 八、后端在用户家里

回到图 4 的右半部分。这些应用没有维护者的后端，`dist/` 是纯静态的，放在哪都能跑。它们连的是浏览器里的 `https://js.puter.com/v2/`——一行 script，没有 API key，提供账号、文件、KV、AI 和邮件。

这件事的意义不在「省了服务器」，在于**数据的归属被换成了另一个人**：

| 应用        | 数据存在哪                                                         |
| ----------- | ------------------------------------------------------------------ |
| Spreadsheet | 你自己的 Puter 云盘里的真 `.xlsx` 文件；版本快照在 `.versions/` 下 |
| Wiki        | `wiki/tree.ywk`、`wiki/pages/<id>.ywk`，每个文件是一个 Yjs 文档    |
| CAD         | `.cad` 压缩 JSON；云文件在你的 Puter 盘，本地文件在设备上          |

更有意思的是协作。Wiki 的共享空间不是跑在维护者的服务器上：**第一个分享页面的人，会在自己的 Puter 账号里部署一个小 worker**（`puter.workers.create`），共享数据存在这个人的 KV 和文件里，被邀请的人拿着受限凭证调这个 worker，worker 每次请求都校验角色。Photo Studio 的「Invite to Edit」是同一套模式。

也就是说，「无后端」的准确含义是：**没有我们的后端。**代价是权限模型变成了「谁的文件谁部署」——文档的所有者同时是这台协作服务器的主人，也是它的运维。这在团队内部很好用，在「把链接发给客户」这类场景里就有问题（README 自己承认：评审链接也必须登录）。

## 九、许可证：15 和 35

这是我最想让读者带走的一节。

仓库根目录的 `LICENSE` 是 MIT，1,080 字节。但有 15 个目录自带一份 34.5 KB 的 AGPL-3.0 全文，并且在自己的 `package.json` 里写 `"license": "AGPL-3.0-only"`：

| 类别 | AGPL 的应用                                                 | 数量 |
| ---- | ----------------------------------------------------------- | ---- |
| 办公 | Spreadsheet、Presentation、PDF、Notes                       | 4    |
| 创意 | Photo Studio、Video Studio、Vector Studio、Audio Studio、3D | 5    |
| 工程 | CAD、Parametric、Circuits、Building Design                  | 4    |
| 协作 | Email                                                       | 1    |
| 效率 | Whiteboard                                                  | 1    |

剩下的 35 个不声明，按根目录的 MIT 走。

这个划分**不是按难度来的**。Notes 和 Email 是 AGPL，但同一个仓库里的 Teamchat 和 Wiki 是 MIT——后两个的技术难度一点儿也不低。从目录和 README 的写法看，这更像是**按批次**划的：早期那批重型应用一起选了 AGPL，后来的长尾应用默认不写。这是我从仓库结构推的，不是官方说法。

对使用者来说，差别很实际：

- 想自建一个内部工具，MIT 那 35 个随便改。
- 想把 Spreadsheet 或 Photo Studio 改一改，做成对外提供的 SaaS，AGPL 的「网络使用」条款会要求你把修改后的源码也提供出去。
- 想拿来当学习材料，两者都没问题——但得知道自己在读哪一份许可证。

顺带一个容易被读漏的地方：README 的说法并不统一。MIT 的应用沿用仓库级那句话——「This repository … MIT unless explicitly stated otherwise」；AGPL 的应用则改成「This app … AGPL-3.0-only」。加上根 README 里那句「unless explicitly stated otherwise」，只看 README 的人很容易把 15 个 AGPL 应用也当成 MIT。**想确认，唯一可靠的位置是每个目录的 `package.json`。**

## 十、局限

按重要性排，都是仓库自己写着的或能从结构里直接量出来的：

1. **50 次部署是线性成本。**每加一个应用，就多一个 Amplify 应用、一份 `npm ci`、一个域名、一套监控。共享的只有那 728 字节的插件。
2. **仓库卫生不均。**551 MB、4,375 个文件的 `tmp/` 已经提交，CI 只能绕开它。
3. **测试并非全绿。**`ci.yml` 里 `whiteboard` 挂着 `continue-on-error`，注释写的是两个 presence-relay 顺序测试在 CI 负载下会挂；整个应用的测试约 27 分钟。
4. **代码风格没有统一。**工作流里那句话是「Only apps whose code is already Prettier-clean are held to it」——实际只有 whiteboard 受约束。
5. **重型应用普遍是 Early Alpha。**CAD 和 Parametric 的 README 都写着不要用于正式工程；Photo Studio 有 8,192 px / 2,400 万像素 / 8 位的硬上限。
6. **云能力绑定 Puter.js。**AI 功能要账号，协作要账号，离线只能靠 IndexedDB 里的草稿。
7. **跨应用集成几乎没有。**没有共享数据模型，`IMPORTRANGE` 这种是个例而不是协议。
8. **没有共享组件，只有复制。**省了抽象，但同一个修复要在多个目录里重复。
9. **它仍然是一个五周大的仓库。**68 个 open issue，功能密度和稳定性不在一个量级上。

## 十一、我的判断

我不觉得这个项目最重要的意义是「50 款软件的免费替代品」。那件事的成败取决于太多别的东西：格式兼容、字体、打印、协作、以及用户为什么愿意换。

它真正在赌的是一件更小、也更容易验证的事：**一款软件的默认大小，可以是一个目录。**

这个赌注押的不是代码量，是三个约定：一个 `package.json` 就是一个产品；一行 script 就是一个后端；一份 `LICENSE` 就是一个法律边界。三个约定各自都很便宜，合起来就解释了为什么这个仓库能在五周里从 0 长到 50 个应用——**它把「要不要做这个产品」的决策成本降到了几乎为零。**

代价也在同一处：约定只管「放哪」，不管「怎么连」。50 个应用之间目前唯一的公共设施，是那一行 `js.puter.com/v2`。

所以下一步值得盯的不是它又加了几个应用，而是三件更小的事：

1. 根目录会不会出现 `package.json`。一旦出现，就说明有人开始做共享包，目录即产品的约定开始松动。
2. 会不会出现跨应用的调用协议。有意思的是，每个应用其实都已经有一层「动词」：Photo Studio 有 command registry，CAD 有一整套命令行，Spreadsheet 有对象模型和脚本沙箱。**如果哪天要接 agent，接口最可能从这些注册表里长出来，而不是从一个新框架里。**
3. AGPL 的目录会不会继续增加。这是最能看出团队意图的一个指标——它决定这个仓库最终是「可以自建的工具箱」，还是「只能自己用的展示柜」。

顺便说一句，这和我最近在看的干预接口是同一个问题：一个系统对外暴露了哪些动词，决定了它能被谁、以什么方式组合。50 个应用各自定义了自己的动词，然后就没有然后了。这既是它现在的样子，也是它最大的空间。

## 项目与资料

- 仓库：[HeyPuter/everything](https://github.com/HeyPuter/everything)（根目录 MIT，15 个子项目 AGPL-3.0）
- 在线体验：[Spreadsheet](https://spreadsheet.puter.com/) · [Photo Studio](https://ps.puter.com/) · [CAD](https://cad.puter.com/) · [Wiki](https://wiki.puter.com/) · [Parametric](https://parametric.puter.com/)
- 值得读的几份 README：[`src/photo-studio`](https://github.com/HeyPuter/everything/tree/main/src/photo-studio)（架构与局限）、[`src/cad`](https://github.com/HeyPuter/everything/tree/main/src/cad)（几何与 DWG）、[`src/spreadsheet`](https://github.com/HeyPuter/everything/tree/main/src/spreadsheet)（公式引擎）、[`src/parametric`](https://github.com/HeyPuter/everything/tree/main/src/parametric)（OpenCascade）
- 仓库结构：[`.github/workflows/ci.yml`](https://github.com/HeyPuter/everything/blob/main/.github/workflows/ci.yml) · [`amplify.yml`](https://github.com/HeyPuter/everything/blob/main/amplify.yml) · [`dev/puter-localhost.mjs`](https://github.com/HeyPuter/everything/blob/main/dev/puter-localhost.mjs)
- 依赖的云：[Puter](https://github.com/HeyPuter/puter)（AGPL-3.0）与 [Puter.js 文档](https://docs.puter.com)

**数据说明：**文件数、字节数、许可证分布、star 数取自 GitHub API 的 `git/tree?recursive=1` 与各目录 `package.json`（2026-11-17）；功能数字取自各应用 README；四张示意图是我按仓库结构绘制的，不是项目官方图表。
