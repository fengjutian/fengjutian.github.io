---
layout: post
title: magpie：它调度的不是模型，是会过期的额度
date: 2026-11-17 14:20:00 +0800
thumbnail: assets/img/blog/magpie-quota-cache-gateway.jpg
description: 从九种路由模式、五种 Stays 与「宁可 503 也不发明文」的脱敏规则出发，拆解 magpie 如何把订阅额度当库存出清，又如何在八十八个 Agent 的配置文件里进得去、退得出来。
tags: [AI, 开源, 开发者工具]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/magpie-quota-cache-gateway.jpg
---

`127.0.0.1:3425`。

这个端口上跑的是 magpie：一个本地网关，把 Claude Code、Codex、Gemini CLI 和另外八十几个 AI 编程工具接到同一个入口，再由它决定每个请求该发给谁。

- 源码：[yetone/magpie](https://github.com/yetone/magpie)（MIT）
- 文档：[usemagpie.ai/docs](https://usemagpie.ai/docs/start)
- 形态：菜单栏应用 / 窗口 / TUI / CLI / Web，Docker 与 Termux 也能跑

它的 slogan 是「Every agent's model. One place.」。

但我读完之后认为，它真正在做的事情比这句 slogan 具体得多：**它调度的不是模型，是会过期的额度。**而这套调度有一个比额度更强的约束——上一个请求留下的缓存。

本文只讲这两件事，以及为了做成它们必须付的那笔工程账。

## 一、两个数字

**第一个数字是 3425。**所有 Agent 都被指向它，它说四种协议：OpenAI Chat Completions、OpenAI Responses、Anthropic Messages、Gemini。任意一侧进来，任意一侧出去，中间翻译——流式、工具调用、推理内容都要跟着翻。

这是整个产品的支点。没有它，后面所有功能（多账户、路由、脱敏、记账）都无处落脚。

**第二个数字是 88。**README 里那张「Supported agents」清单，我数了一遍：88 个名字，从 Claude Code、Codex、Cursor CLI，到 Zed、VS Code Chat、JetBrains Air，再到 Hermes Agent、Kimi Code、Qwen Code……

有意思的是它自己文档里的三个口径：对照页写的是「Over 20」，入门页列了 22 个，README 列了 88 个。

这不是笔误，是「支持」在这类工具里有三层意思：**认得它的配置文件**（88）、**验证过它真的能用**（20 上下）、**值得在文档里手把手写一遍**（12 个在对照表里点名）。三个数都对，但只有一个数能当承诺用。

## 二、账：九种路由模式，其实是同一个问题

![三条成员的用量、余量与重置时刻，四种策略各看其中一个数]({{ '/assets/img/blog/magpie-quota-cache-gateway/fig-01-quota-as-inventory.png' | relative_url }})

_额度的三个属性——用了多少、还剩多少、什么时候重置——撑起了全部路由策略。图里的数字是示意，不是实测。_

官方文档列了九种成员之间的分配方式。把它们摊开看，会发现它们回答的是同一个问题：**一批会过期的余额，怎么在过期前用掉。**

| 模式     | 它在最大化什么                                   |
| -------- | ------------------------------------------------ |
| `smart`  | 先用在**最近就要重置**的那份额度，少浪费一次重置 |
| `pace`   | 用在「剩余额度 ÷ 距重置小时数」最高的那个        |
| `drain`  | 一个用到尽再换下一个，且换过去就不回来           |
| `usage`  | 用在用得最少的那个                               |
| `rotate` | 每个消息换一个，工具调用留在同一个               |
| `weight` | 按你给的权重分摊，摊开而不是成串                 |
| `fast`   | 用最近首 token 最快、写得最快的那个              |
| `cheap`  | 用**这一小时**单价最低的那个                     |
| `order`  | 按你排的顺序，不行再下一个                       |

`smart` 和 `pace` 的区别值得单独说，因为它俩经常被混为一谈：

- `smart` 问的是「谁的额度马上过期」——它害怕的是**浪费**；
- `pace` 问的是「谁剩下的额度按小时摊下来最多」——它害怕的是**提前用光**。

一个是清库存，一个是控流速。同一批余额，两种怕法。

而 `cheap` 是我在这个项目里看到最不像推理引擎的一行逻辑：它按**此时此刻的单价**排序。DeepSeek 自己的 API、Command Code、OpenCode Go 上的 DeepSeek 模型，在工作日的 01:00–04:00 与 06:00–10:00 UTC 两个时段价格翻倍；Ollama Cloud 上的 DeepSeek V4.1 Flash 与 V4 Pro 在 12:00–18:00 UTC 是原价，其余时间半价。

于是「同一个模型挂在两个渠道上」变成了一次可以套利的价差，而路由器知道现在是几点钟。

## 三、缓存：路由的自由度被一个更便宜的变量按住了

![同一个对话跨五轮，账户 A 一直应答；第五轮额度用尽才换人，并重读整段上下文]({{ '/assets/img/blog/magpie-quota-cache-gateway/fig-02-stickiness.png' | relative_url }})

_切换账户的成本不是一次请求，而是一次重新 prefill：整段上下文按未命中价重算。_

如果只按上面那张表路由，每一次请求都独立挑一个成员，看起来最「公平」。但真实世界里这会亏钱：厂商的提示词缓存是按会话积累的，换一个账户，缓存就没了，整段上下文按未命中价重算。

所以 magpie 里有一个叫 Stays 的维度，管「一个会话在应答它的那个账户上待多久」：

| Stays     | 什么时候换人                                             |
| --------- | -------------------------------------------------------- |
| `auto`    | 默认。一轮之内绝不换；跨轮时，只要缓存还值得留就留在原地 |
| `session` | 整个会话不换，除非它答不了                               |
| `turn`    | 一轮之内不换；你下次开口时重新路由                       |
| `strict`  | 永不换。额度用尽就把错误原样抛给 Agent                   |
| `off`     | 每个请求都重新路由                                       |

五种模式里最有信息量的是 `auto` 的措辞：**「跨轮时，只要厂商缓存还值得留」。**

这句话承认了一件事：路由的正确解不是「最优成员」，而是「最优成员 + 迁移成本」。而这个成本是厂商替你记的，你看不到它，只能看着它慢慢变便宜。

`strict` 是这条逻辑的极端版本：宁可让 Agent 收到一个额度错误，也不偷偷换账户。文档只写了「永不换」，没有解释为什么；从接口形状推断，它的用途是给那些「换账户等于为同一段上下文付两次钱，而错误至少看得见」的场景。

## 四、手：把网关写进八十八个配置文件

![网关两侧都是双向箭头，另有一条反向的写配置路径]({{ '/assets/img/blog/magpie-quota-cache-gateway/fig-03-two-directions.png' | relative_url }})

_请求/响应是一对，脱敏/还原是一对，写配置/还原是第三对。第三对在界面里最不可见。_

前面两节都是「账」。但 magpie 还有一半工作量在另一件事上：它要改别人家的配置文件。

这件事听起来很简单——把 `ANTHROPIC_BASE_URL` 指向 3425 就完了。实际不是：

- Claude Code 的模型是 `~/.claude/settings.json` 的 `env` 块里的几个变量；
- Codex 是 `~/.codex/config.toml` 里的一张 `[model_providers.magpie]` 表，外加一份 `magpie-models.json`；
- OpenCode、Crush、Pi 这类是加一个 provider 条目，再写 `magpie/provider/model`；
- Gemini CLI 是 `GOOGLE_GEMINI_BASE_URL` 加 API-key 认证模式。

每种格式都不一样，而且每一种都可能被用户手改过。所以它承诺三件事：**只改它需要的键**、**注释与顺序原样保留**、**原子写入**。

然后是我认为这类工具最容易被忽略、也最该被检查的那一半：

- `magpie <agent> default` 把它写进去的东西删掉，还原被替换掉的原值——包括你原来自己设过的那个 `ANTHROPIC_BASE_URL`；
- 卸载脚本先把每个 Agent 接回原样，再拆掉自己装的东西；你已经删掉 magpie 了，它会临时下一个回来做这件事；
- `claude-magpie` 给了一条不写文件的路径：同一个 `claude`，加上 magpie 的环境变量跑起来，`~/.claude/settings.json` 一个字都不动。

我在图里把这条路径画成一条反方向的箭头，因为它的失败模式和正向完全不同：正向写错了，你当场发现连不上；反向还原错了，你可能要过三天才在一次诡异的行为里发现某个字段被留在了别人家的格式上。

还有一个坑值得单独记：**改配置不会影响已经在跑的会话。**Agent 在启动时读配置，所以切模型之后必须开新会话；Codex 还要重启一次，因为它的模型清单也是启动时构建的。

## 五、脱敏：两条「宁可失败」

![值换成占位符出站，回复里的占位符换回真值入站]({{ '/assets/img/blog/magpie-quota-cache-gateway/fig-04-masking-fails-closed.png' | relative_url }})

_默认关闭。开启后它在网关里跑，所以在任何供应商、任何账户前面都生效。_

这部分设计得比大多数同类功能更狠，狠在三个默认值上。

**第一，同一个值永远是同一个占位符。**占位符是「种类 + 八位带密钥的哈希」，所以 `sk-proj-…` 每次出现都是同一个 `{% raw %}{{API_KEY_srhjgvja}}{% endraw %}`。

这一条不是为了好看。换成随机占位符，同一段对话里同一个键前后不一样，模型的推理就会断，厂商的提示词缓存会失效，Anthropic 那种带签名的 thinking 块甚至会校验不过。**换一个稳定的假名，是整个功能能不能用的前提。**

**第二，值只在内存里。**落盘的审计记录只有种类、长度和前几个字符——所以万一有人拿到了 `~/.config/magpie/masking`，他拿到的是「这里有 33 个字符的 API Key」，不是 key。

**第三，跑不了就不发。**

- 脱敏插件被手动关掉，或者你开着的本地模型答不上来 → **503**，明说「什么都没发出去」；
- 某个种类的策略设成 Block → **400**，并在错误里写出「我刚才拦下了一个 33 字符的 sk- 开头的键，什么都没发」，但错误信息本身不含那个值；
- 「把会被改写的请求转给本机模型」这条旁路失败时也是失败，**不会退回去脱敏后发给供应商**。

第三点是整个设计里我最认同的一处。脱敏功能的失败模式有两种：一种是拒绝工作（用户会骂，但他安全），一种是降级成明文继续发（没人会骂，因为他不知道）。选前者需要一点纪律。

代价也写得很直白：模型只看到 `{% raw %}{{API_KEY_…}}{% endraw %}`，所以「为什么这个 token 被拒了」这类需要读值本身的问题做不了——把它放进 Never mask。另外，图片里的文字不会被脱敏，截图里的密钥照样会发出去。

规则清单本身是一份值得收藏的工程清单：从 `sk-`、`ghp_`、`glpat-`、`AIza`、`AKIA` 这类形状，到 `-----BEGIN PRIVATE KEY-----`，到钱包私钥（WIF、BIP32 `xprv`、`0x`、Solana、Sui、Aptos、Stellar、NEAR `ed25519:`、Nostr `nsec1`、Zcash、以及 BIP39 的 12–25 词种子）。

妙的是那些**只在校验通过时才脱敏**的条目：Solana 的签名和私钥长得像，`0x` 开头的交易哈希和私钥长得更像，所以前者按校验位判断，后者只在 `PRIVATE_KEY=`、`--private-key`、`new Wallet(…)`、私钥这些上下文后面才动手。

「宁可漏一点，也不要把用户的哈希改成占位符」——这条取舍贯穿整份规则表。

## 六、订阅复用：让 Claude Code 去驱动你本机的 `claude`

订阅账户能被别的 Agent 用，是 magpie 最像「魔法」的一部分，实现方式其实很朴素：它不假装自己是 Anthropic。

- **Claude**：它调用你本机真正的 `claude` 二进制，再把 Agent 的工具通过 MCP 桥过去。所以文档里有一句：保持 Claude Code 安装着。
- **ChatGPT / Copilot / Gemini Code Assist**：走各自订阅的通道；
- **Antigravity**：通过你自己的 `agy` CLI。

这也解释了「每日预热」这个功能为什么存在：Claude 和 ChatGPT 的额度是按 5 小时窗口滚动的，magpie 可以在你指定的时间把窗口起跑，或者在上一个窗口重置的瞬间起跑——本质上是在管理一批有相位差的额度。

官方在这里放了一句不太常见、但很该有的警告：**Google 可能会封掉一个在 Antigravity 之外被使用的 Antigravity 账户，所以用一个你输得起的。**

订阅是怎么被发现的也值得知道：它读 Claude Code 和 Codex 的登录文件、读 Keychain。不想让它读，就关掉 Settings → Privacy → Subscription accounts，或者 `magpie accounts discovery off`；`MAGPIE_NO_ACCOUNTS=1` 只影响一次运行。

## 七、同一层上还堆了什么

这些不是本文重点，但它们决定了这东西是「一个切换器」还是「一层基础设施」：

- **用法账本**：tokens、缓存读写、推理、调用次数，按每个 Agent、每个模型分；成本按标价算成美元或人民币（可以给某个模型设自己的价）。还有配额窗口、Bills、OTLP 导出。
- **上下文解剖**：把一个请求的窗口拆成系统提示词、工具定义、指令文件、技能、会话……给每个 Agent 打一个百分制，标签是「起点精简」或「MCP 偏重」。这段文本**只在内存里保留最近 10 个请求**，落盘的只有结构，没有内容。
- **插件**：npm 上的 OpenCode 插件可以直接装；Bun 在第一次需要时下载。中间件钩子三个：`onRequest`、`onEvent`、`onResponse`，一个钩子抛错或超时，请求按原样放行。
- **现成中间件**：`model-map`、`param-override`、`system-prompt`、`word-guard`、`think-tags`——README 自己说，这几个是「New API 为它的渠道做的事，JSON 都一样」。
- **Library**：instructions、MCP server、skill、subagent 写一次，按每个 Agent 的格式分发，并且**只删除自己写进去的部分**。
- **给所有模型配搜索**：一个模型自己不会搜，就用你挂的搜索 API（Tavily、Brave、Exa、Firecrawl、SearXNG…），按你拖的顺序问；一个 API 可以挂多个 key 轮着用。搜索还能以 MCP server 的形式挂回给任何 Agent。
- **共享与远程**：局域网共享给每个客户端发带日/周/月限额的网关 key；Remote magpie 让你的笔记本用台式机的 provider 和路由组；Docker 与 WebDAV/S3/加密 GitHub 同步。

## 八、和谁比

官方自己写了一页对着 CC Switch 与 Claude Code Router 的对照，这一页的写法比大多数「对比表」诚实：另外两列只写它们 README 里说过的话，没说的地方写「not stated」。

|            | magpie                                            | CC Switch          | Claude Code Router   |
| ---------- | ------------------------------------------------- | ------------------ | -------------------- |
| 主要手段   | 改配置 + 本地网关                                 | 改配置（可选代理） | 本地网关             |
| 协议转换   | 四种协议双向                                      | 路由模式下支持部分 | 四种格式但单入口     |
| 订阅登录   | Claude / ChatGPT / Copilot / Gemini / Antigravity | 部分（Beta）       | 未说明               |
| 路由自由度 | 九种模式 + 五种 Stays + 规则                      | 失败队列 + 熔断    | 请求条件、改写、重试 |
| 许可       | MIT                                               | MIT                | MIT                  |

三者的差异不在功能表，而在**它们各自假设你的痛点是什么**：CC Switch 假设你想手动切；CCR 假设你想写规则；magpie 假设你有多个账户，并且它们的额度会自己过期。

LiteLLM 与 New API 不在同一层：那是给团队用的服务端网关，做的是预算、鉴权、渠道分发；magpie 做的是**单机上几十个别家产品的配置文件**。这两件事的技术难点几乎不重叠。

## 九、边界

1. **它必须一直开着。**模型走网关，网关跟着应用跑；关掉窗口它还在菜单栏或托盘里，`magpie daemon install` 才是不用开窗的那种。
2. **代理软件会劫持 3425。**Surge / Clash / mihomo 开着 TUN 或增强模式时，`127.0.0.1:3425` 会被送进代理，Agent 拿到 502，而 magpie 的 Routing 页一片空白。得给 `127.0.0.0/8` 加一条 DIRECT 规则。这是这类工具最典型的一类报障。
3. **订阅复用踩的是别人的授权边界。**Antigravity 那条警告就是明证；它不承诺任何订阅都提供通用 API，也不承诺不违反供应商的使用条款。
4. **脱敏不是内容审核。**图片里的文字、你自己没列进规则的格式、被你放进 Never mask 的值，都照发不误。
5. **遥测是真的有，尽管写得极清楚。**每天一次上报：随机 id、版本、系统、在用哪些 Agent/供应商/模型（自己加的一律记为 `custom`）、装了哪些插件、以及合作方位置的展示次数。`DO_NOT_TRACK=1` 可关；源码构建不上报。但有两类计数是关不掉的：`usemagpie.ai/go/…` 的点击，和 `/api/icon` 的图标代理——服务器总归看得见自己的访问。
6. **它不收 PR。**README 明写：只有维护者能开。想要什么去 Discord 说。对 MIT 项目来说这不常见，但作者把「谁负责这件事」说清楚了。
7. **发布链做得比多数商业软件细。**每个发布文件带 GitHub Actions 的 SLSA 证明（`gh attestation verify`），应用的自动更新校验一份用内置 ed25519 公钥签名的 SHA-256 清单，从 v0.1.3891 起连证明也一起校验，镜像站只能搬文件、不能改文件。

## 十、我的判断

三条可以验证的下一步。

**一，`cheap` 与缓存的对价。**按小时计价的路由很少见，但它和第三节的缓存约束是有冲突的：为了省下 DeepSeek 的峰谷价差而换渠道，可能赔掉一整段上下文的缓存。官方没有给这两者的对照数字。可验证的做法很简单：同一个长会话，分别在 `cheap` 和 `Stays=strict` 下跑，比较总成本——如果前者更贵，这条模式就该在长会话里被规则挡掉。

**二，`pace` 里那个 90%。**文档写「一个剩余量在 90% 以上的账户，要等其他账户都答不了才轮到它」。这个阈值是个魔数，没有公开的测量依据。85/90/95 三档跑同一个负载，看重置前的浪费率，就能知道它是不是拍的。

**三，八十八份配置契约的回归测试。**这是我觉得最有价值、也最没人做的事：每个 Agent 的配置文件都是一份外部契约，上游一改格式，magpie 的写入或还原就会坏——而**还原坏了没人当场发现**。

我上一篇写 MNN 的支持矩阵时，关心的是「同一列精度在不同后端上的成熟度完全不同」。magpie 这里其实也有同一张矩阵，只是它的列只有两列：

**写得进去**，和**退得出来**。

第一列在 CI 里、在用户装上的第一天就被反复验证；第二列只在你决定不用它的那天生效，而且只生效一次。任何按这个思路做工具的人，都该先想清楚第二列的测试怎么写——因为那一列错的时候，用户已经没有退路了。

## 项目与资料

- [GitHub 源码](https://github.com/yetone/magpie)（MIT）：Go 主程序 + Bun 跑的插件，`internal/redact` 与 `internal/masking` 是脱敏实现
- [官方文档](https://usemagpie.ai/docs/start)：路由九种模式、Stays、规则、终端命令
- [Privacy masking](https://usemagpie.ai/docs/masking)：占位符、规则清单、三条「不许」
- [与其他工具的对照](https://usemagpie.ai/docs/alternatives)：CC Switch 与 Claude Code Router，标注了各自的 README 日期
- [Plugins](https://usemagpie.ai/docs/plugins) 与 [magpie-community/plugins](https://github.com/magpie-community/plugins)：中间件与钩子
- [Intent routing](https://usemagpie.ai/docs/intent)：那个只读用户消息的分类器
- [Remote magpie](https://usemagpie.ai/docs/remote) / [Docker](https://usemagpie.ai/docs/docker) / [Sync](https://usemagpie.ai/docs/sync)

文中功能与数字均核对自 README 与上述文档；我没有在真机上跑过 magpie，也没有验证「88 个 Agent」里有多少是真正测试过的——那个数只有维护者知道。封面与插图为自制示意图，未使用项目截图。
