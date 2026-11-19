# 微信公众号发布说明

「认知博弈」现在有两个版本，服务两类读者：

|      | 站内版                                                             | 公众号版（本目录）                             |
| ---- | ------------------------------------------------------------------ | ---------------------------------------------- |
| 标题 | 认知博弈：形式化、求解与可辨识性综述                               | 认知博弈：当两个智能体互相预测时，未来如何产生 |
| 读者 | 同行                                                               | 泛技术读者                                     |
| 文体 | 综述：9 处公式、对照表、16 条文献                                  | 叙述：6 处公式（渲染成图）+ 逐条白话解释       |
| 图   | `assets/img/blog/cognitive-game/`（L0–L3、KL、物理/概率/认知三层） | `img/`（第 1–4 层、摸清了/来回拉锯、三本账）   |
| 产物 | `_posts/2026-11-19-cognitive-game-mutual-prediction.md`            | `cognitive-game-wechat.html`                   |

两份的文字与图各自成套，不交叉引用。改其中一份不影响另一份。

## 文件清单

| 文件                         | 用途                                                      |
| ---------------------------- | --------------------------------------------------------- |
| `cognitive-game-wechat.html` | 正文成品，1.21 MB，8 张插图 + 6 个公式全部内嵌为 base64   |
| `wechat-cover-235.jpg`       | 封面首图，1410×600（2.35:1）                              |
| `article.txt`                | 公众号版正文源（排版标记），改文字改这里                  |
| `img/`                       | 白话标注图集（`fig-0N-*.png`）与公式图（`eq-0N-*.png`）   |
| `build.py`                   | 生成器：`article.txt` → 带内联样式的 HTML                 |
| `build_eq.js`                | 公式排版器：MathJax + 无头 Chromium，把 LaTeX 渲成 3× PNG |
| `cover_wechat.py`            | 生成 2.35:1 封面                                          |
| `shot.js`                    | Playwright 截图，检查版式                                 |
| `full.png` / `shots/`        | 渲染预览，不发布                                          |

## 三步发布

1. 双击打开 `cognitive-game-wechat.html`（Chrome / Edge）。
2. 页面里 `Ctrl+A` 全选，`Ctrl+C` 复制。
3. 打开公众号后台 → 新建图文 → 正文区 `Ctrl+V` 粘贴。

编辑器会自动把 8 张插图和 6 张公式图转存到公众号服务器。若某张失败，从 `img/` 里按图序手动拖入。

## 标题与摘要

**标题**

```
认知博弈：当两个智能体互相预测时，未来如何产生
```

**摘要**（上限 120 字，这版 65 字）

```
两个射手互相猜对方，会猜出什么结果？从三层猜测、一团概率，讲到为什么动作也是信号，以及为什么「证明对方在猜你」比「猜得更准」更难。
```

**封面**：`wechat-cover-235.jpg`。上传后再裁一张 1:1 小图，把裁切框压在左侧「认知博弈」四个字上。

## 公式为什么是图片

公众号编辑器会丢弃 MathJax、KaTeX 和 `<math>`，LaTeX 源码会原样显示成 `$$…$$`。唯一的办法是先排版成图片。

`build_eq.js` 做这件事：

```js
// 6 条公式的 LaTeX 写在 EQ 数组里
const EQ = [['eq-01-coupling', String.raw`a_B=\pi_B(b_B), …`], …];
```

打开一个本地 HTML，用 MathJax 3（SVG 字体）排版，等 `MathJax.startup.promise` 落定后用 Playwright 按元素截图，得到透明底、3 倍分辨率的 PNG。`build.py` 读 PNG 头拿到像素宽度，除以 3 得到 CSS 宽度并写死进 `style`，避免公众号把窄公式放大成一整屏。

| 公式图                        | 内容                           | 出现位置                       |
| ----------------------------- | ------------------------------ | ------------------------------ |
| `eq-01-coupling.png`          | 动作与信念的耦合式             | 一、一个具体的局面             |
| `eq-02-interactive-state.png` | 交互状态 = 状态 × 对手模型     | 三、把「他怎么想」拆成几个问题 |
| `eq-03-belief-update.png`     | 信念更新（求和跑在交互状态上） | 六、我动一下，他就变了         |
| `eq-04-recursion.png`         | level-k 与认知层级的递推       | 四、三层就够了                 |
| `eq-05-mixture.png`           | 高斯混合                       | 五、每个人心里都有一团概率     |
| `eq-06-performative.png`      | performative stability         | 七、预测会把预测对象改掉       |

每条公式后面都跟一段白话解释，说明每个符号管什么——这也是公众号版和站内综述的分工：站内给形式定义，这里给读法。

## 图序对照（公众号版）

| 图   | 所在小节                       | 文件（`img/`）                              |
| ---- | ------------------------------ | ------------------------------------------- |
| 图 1 | 一、一个具体的局面             | `fig-01-prediction-becomes-observation.png` |
| 图 2 | 三、把「他怎么想」拆成几个问题 | `fig-02-two-belief-versions.png`            |
| 图 3 | 四、三层就够了                 | `fig-03-recursion-ladder.png`               |
| 图 4 | 五、每个人心里都有一团概率     | `fig-04-two-probability-clouds.png`         |
| 图 5 | 六、我动一下，他就变了         | `fig-05-cognitive-loop.png`                 |
| 图 6 | 七、预测会把预测对象改掉       | `fig-06-reflexivity-schematic.png`          |
| 图 7 | 八、系统会怎样                 | `fig-07-five-dynamics.png`                  |
| 图 8 | 十、如果要动手做               | `fig-08-experiment-bench.png`               |

## 改文字 / 重出

```powershell
node   .mockups\wechat\build_eq.js   # 公式有改动时先跑这个
python .mockups\wechat\build.py      # 生成 HTML
node   .mockups\wechat\shot.js       # 截图核对（可选）
```

`build.py` 先按仓库根目录找图，找不到再找本目录，因此 `article.txt` 里的 `img/…` 直接可用。公式图的 CSS 宽度按 3 倍渲染宽度换算，换分辨率时要同步改 `equation()` 的 `scale`。

## 与站内版的排版差异（同前）

- 无外链：站外链接不可点，`doi:` 与 arXiv 只留在站内版。
- 四列宽表改竖排卡片：手机横滑读不了。
- 样式全内联：编辑器会剥掉 `<style>` 与 class。

## 注意

本目录位于 `.mockups/`，仓库 `.gitignore` 只为它开了一个例外（`!.mockups/wechat/`），预览产物（`full.png`、`shots/`）仍被忽略。公式图与正文 HTML 都随仓库版本化。

`cognitive-game-wechat.html` 已加入 `.prettierignore`：它是单文件内嵌 base64 的产物，格式化只会拆行。
