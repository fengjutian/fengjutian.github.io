---
layout: post
title: Aerial：换桌面不是画界面，是在别人的固件里抢前台
date: 2026-11-17 14:20:00 +0800
thumbnail: assets/img/blog/aerial-tv-launcher-foreground-takeover.jpg
description: 从 89 行机型记录出发，拆解 Aerial 怎么用无障碍服务、窗口事件和通知监听，在只认自家桌面的固件里抢回前台，顺带算一遍电视 GPU 的帧预算。
tags: [开源, 开发者工具, 架构设计]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/aerial-tv-launcher-foreground-takeover.jpg
---

一个开源 Android 桌面，README 里有一张 89 行的机型表。

其中 56 行写着能用，23 行写着「能用，有限制」，10 行写着接管不了。**那 10 行不是「装不上」，是装上了、跑起来了、主页键回不到它。**

![Aerial 首页：壁纸上是时钟和天气，下方一块玻璃底板托着五个磁贴]({{ '/assets/img/blog/aerial-tv-launcher-foreground-takeover/fig-01-aerial-home.jpg' | relative_url }})

_项目仓库里的实机截图。第一排放了 HDMI 1、电视直播、网盘和两个流媒体 —— 桌面只剩应用入口，没有推荐流。_

- 源码：[pengchujin/aerial-tv](https://github.com/pengchujin/aerial-tv)（MIT，Kotlin + Compose）
- 官网：[aerial.qust.me](https://aerial.qust.me)，安装说明：[agent.md](https://aerial.qust.me/agent.md)
- 规模：仓库 2026-10-20 建，2026-11-17 已 12,232 star、1,063 fork、395 个 open issue，最新版 1.99 发布于 11-16

界面像 tvOS 的复制品，这一点很好看出来。这篇文章只讲另一件事：**它怎么在一个不承认它的系统里，成为那个被主页键唤出来的窗口。**

先看一眼它替换掉的是什么。

![小米电视自带桌面：整屏剧集推荐、会员角标、限免标签]({{ '/assets/img/blog/aerial-tv-launcher-foreground-takeover/fig-02-stock-launcher.jpg' | relative_url }})

_首页的第一屏几乎全是内容：一张主视觉、四排推荐、VIP 和「限免」角标。用户自己装的 App 在左边那一列里，要再点一次。_

## 一、HOME 是一个可以声明的 Intent，不是一个可以被信任的接口

原生 Android 里，这件事只需要一个 intent-filter：

```xml
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.HOME" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>
```

声明了 `CATEGORY_HOME`，按主页键时系统弹一次「使用哪个应用」，选「始终」，就结束了。

![同一个主页键在两种系统上的两条路径]({{ '/assets/img/blog/aerial-tv-launcher-foreground-takeover/fig-03-two-home-paths.png' | relative_url }})

_上边是原生 Android TV 的路径；下边是很多国产固件的路径 —— 按键到不了系统解析那一步，Intent 也就没有出现过。_

问题在下面那条路。小米的 PatchWall、TCL 的 `LauncherStrategy`、创维的 `com.tianci.uiservice`，都是**直接按组件名打开自家桌面**，不问系统「谁是默认 HOME」。极米还多一层：首选记录被作废时，它自己的「选择桌面」框（`xgimiframeworkui/.resolver.ResolverActivity`）会盖到前台，Aerial 只能把这个框也当成原桌面来处理。

于是同一份代码要出两个 APK：

| flavor     | manifest 里的 HOME 声明 | 用在                                                   |
| ---------- | ----------------------- | ------------------------------------------------------ |
| `standard` | 有                      | 能装第三方桌面的电视（原生 Android TV、部分小米）      |
| `guard`    | **没有**                | 拒绝安装桌面类 App 的固件（TCL 的 `LauncherStrategy`） |

`docs/ARCHITECTURE.md` 写得很清楚：**两者代码完全相同，只差 manifest。** guard 版不再试图当 Home，它接受自己是个普通 App，然后用下一节的办法把前台抢回来。

## 二、接管：只看前台是谁

Aerial 的守护是一个无障碍服务（`HomeGuardService`）。它监听的事件只有一个：窗口状态变化。原桌面的 HOME Activity 一旦到前台，就 `startActivity` 把自己拉回来。

三个细节决定了这套东西能不能活：

1. **只读窗口，不读内容。** 判断依据是前台窗口的类名在不在 `stockHomes` 里，不碰屏幕上的文字。这既是隐私上的好消息，也是工程上的必然 —— 无障碍读屏在电视上又慢又容易误判。
2. **`stockHomes` 只认系统应用和系统解析出来的默认桌面。** 自己装的、只是多声明了一个 HOME 的 App（比如天马 G）不算原桌面，从 Aerial 里打开它不会被抢回来。电视自己的播放器（`com.tcl.tv`、`com.xiaomi.mitv.tvplayer`）即使声明了 HOME 也不算 —— 除非它真的就是系统解析出的那个，否则每次切信号源都会被当成「原桌面出现」而拉回桌面。
3. **要有退让。** 用户从磁贴主动打开原桌面时，一小时内不拦截；开机、解锁、亮屏之后先等 1.5 秒才判断要不要接管；靠原厂桌面露脸才能结束开机的固件，用一个机型参数 `bootStockMs` 把接管往后推，最多 45 秒。

权限与安装合起来是五条命令，但每一条都不是「优化」，是缺了就残：

```bash
adb shell pm grant app.orchard.tv android.permission.WRITE_SECURE_SETTINGS
adb shell cmd notification allow_listener app.orchard.tv/app.orchard.tv.guard.RevivalListener
adb shell appops set app.orchard.tv SYSTEM_ALERT_WINDOW allow
adb shell am start -n app.orchard.tv/.MainActivity
adb shell cmd package compile -m speed -f app.orchard.tv
```

| 命令                    | 给了什么                 | 缺了会怎样                         |
| ----------------------- | ------------------------ | ---------------------------------- |
| `WRITE_SECURE_SETTINGS` | 能改系统的无障碍服务列表 | 守护启不来，只能当普通 App         |
| `allow_listener`        | 通知使用权               | 被系统清掉之后没人把它拉回来       |
| `SYSTEM_ALERT_WINDOW`   | 悬浮窗                   | 提醒条、部分浮层失效               |
| `am start` + `compile`  | 启动一次并编译           | 靠后台编译要等设备空闲，电视等不到 |

`install.sh` 还会多给一个 `WRITE_SETTINGS`（写亮度之类），并把这个 App 编译一遍。

值得一提的是「编译」这条：项目在 APK 里带了 Baseline Profile，Android 9 及以上直接用 `install-multiple` 连同 `.dm` 一起装，安装时就编译好；只装 APK（U 盘、应用商店、多屏互动推送）的电视拿不到这一步，`odex` 只有几百 KB，编译好应该约 11 MB。差异是首页磁贴从 0.8 秒变成 0.4 秒 —— 在这些电视上，这就是「卡」和「不卡」的分界。

## 三、复活：把「绑定断开」当成心跳

小米待机时会 `killAllThirdApp`，杀掉之后**无障碍授权被系统一并移除**。这时候没有任何回调会告诉 Aerial「你被杀了」，因为进程已经没了。

于是守护不用进程内的东西当心跳，用一个横跨进程生死的东西：通知监听的绑定。

![三条复活路径：通知监听、同步适配器、解锁前绑定]({{ '/assets/img/blog/aerial-tv-launcher-foreground-takeover/fig-04-revival-paths.png' | relative_url }})

_三条路各自对应一类电视。第一条是主路，第二条是给「连通知监听都不给」的 Android 9 低内存机型准备的备胎。_

系统移除无障碍授权时，绑定给 `RevivalListener` 的通知监听会断开，约 0.5 秒后系统重新绑定 —— 这一次绑定会**把整个进程拉起来**。进程一起来，`ensureEnabled()` 把守护重新写进无障碍列表，服务在 `onServiceConnected` 里认出「我是刚被复活的」，于是拉回 Aerial。

第二条路是给准备不了第一条路的电视。小米 MFTP0（Android 9，低内存）不给通知监听，Aerial 就挂一个 `settings` 同步适配器，带一个自己的账号：强停之后 30–60 秒由同步框架拉起，重开守护。守护在跑的时候，这个适配器什么都不做。

第三条路在解锁之前。守护、`RevivalListener`、`BootReceiver` 都声明了 `directBootAware`，用户解锁前就绑定；锁定期间只记窗口、不启动界面、不拦 HOME，因为凭据加密存储还读不了。等到 `ACTION_USER_UNLOCKED` 再接管。极米 Play 6 开机 5 分 35 秒才解锁，这段时间里守护什么都不能做。

最后是一道闸门：**10 分钟内复活 3 次以上，就承认前台未知，不再抢 HOME**（乐视 #63）。这条比前面三条都重要 —— 一个打不赢的守护会变成两台桌面互相抢焦点，而用户看到的是屏幕在闪。

## 四、按键层：这一层没有抽象，只有机型

如果说无障碍是「看」，按键过滤就是「挡」。挡的部分没有一层通用抽象，全是按固件写的例外，出处都在 issue 里：

| 现象                                                 | 处理                                                      | 代价                           |
| ---------------------------------------------------- | --------------------------------------------------------- | ------------------------------ |
| 按主页键时固件强停前台 App（红米投影仪、酷开 C10）   | `filterHomeAlways`：亮屏时一直过滤主页键                  | 按住音量只走一格               |
| 方向键一次跳 2–5 格（乐视 X4-40）                    | `neverFilterKeys`：完全不过滤                             | 主页键交给系统，先露一下原桌面 |
| 手柄事件被过滤后串流卡死重启（小米 MFTR0）           | 插着 `SOURCE_GAMEPAD` 且前台是别的 App 时不过滤           | 这类前台不再拦主页键           |
| 外接鼠标走注入路径，`system_server` 崩（TCL TC8000） | 崩过一次才记住这台固件，然后停止过滤                      | 第一次一定会崩                 |
| 音量键「按下经过过滤层、抬起不经过」（创维酷开）     | 记下固件指纹，之后音量键不再转发，300 ms 没动就自己补一格 | 每台第一次仍会连冲一回         |

这些开关都不在界面上，而是 `assets/devices.json` 里按 `ro.product.model` 匹配的 JSON，一条一个 `note`，写着是哪台电视、哪个 issue 验证的。Agent 在电视上试出来的 JSON 可以整段写进这台电视的偏好，**它原样就是要加进 `devices.json` 的内容**。

我更愿意把这层读成一句话：**兼容性不是一份判断，是一份证据。** 每条例外都能追到一个具体的型号和一条 issue 号，而不是「某些电视可能有问题」。

## 五、帧预算：65ms → 18ms

界面部分有一个数字很能说明电视和手机的区别：第一版在小米那台自测机上，首页帧耗时中位数 **65 ms**；改完约 **18 ms**。这不是「优化了一下」，是从 15 fps 变成 55 fps。

![同一台电视上的七组帧耗时，改之前与改之后]({{ '/assets/img/blog/aerial-tv-launcher-foreground-takeover/fig-05-frame-budget.png' | relative_url }})

_数字都来自作者自己那台小米 MFTR0（Android 14，release，speed 编译）；原文里第一组只写了「小米」，其余几组明确写了 MFTR0。同一台机器、同一次改动前后的 A/B，不是跨机型对比。_

做法可以概括成三条纪律：

**一，每帧只允许一次全屏绘制。** 壁纸和压暗层在 CPU 上预合成，窗口背景设成 null。全屏渐变在电视 GPU 上非常贵 —— 航拍影片上那两层压暗每帧要 22 ms，改成开机时烘焙一张 128×72 的小图再拉伸，GPU 时间 30 → 13 ms，首页移动中位 81 → 31 ms。

**二，玻璃不是实时模糊。** 底板看到的是「它身后那块壁纸的模糊版」，模糊图是 320×180 的预制品，用 `BitmapShader` 按屏幕坐标铺开。面板完全滑入之后，被它盖住的首页干脆不画 —— 过度绘制从 4 层以上降到 1 层，个性化面板 GPU 40 → 12 ms，帧耗时中位 90 → 38 ms。

**三，排版先归一化。** `MainActivity` 把内容缩放到一块 960×540 dp 的设计画布上（`density = 屏幕宽 / 960`）。小米 1080p 屏报 320 dpi、TCL 报 240 dpi，不归一化的话同一份 dp 在两家电视上排出来不一样。磁贴图直接按「聚焦放大后的实际像素」生成，1080p 时 352×198，4K 时 704×396。

关于 4K，项目有一份很诚实的结论：**现在不再自动把界面画成 4K。** 1.51 曾经按「显示模式至少是界面 2 倍」自动打开，结果索尼 X90K 上控制中心掉帧、4K 屏保缩在左上角；1.52 改成只在芯片声明了 4K 界面层（`ro.feature.graphics_4kui`）时打开，又在 TCL 75Q10L 上实测到这层是 GPU 合成后照样按 1080p 送面板 —— 没变清楚，还多耗半个核；另一台 MT9655 的 TCL 每帧 51 ms。所以现在只有强制参数才会走 4K 画布，而且用的是一个放大 2 倍的 RenderNode 加独立 SurfaceView，窗口本身不画东西。

## 六、界面：三条来自遥控器的约束

界面这一层，Aerial 抄的不是 tvOS 的像素，是它的三条约束。

**焦点必须能被看见。** 国产电视都是方向键遥控器，没有 Siri 遥控器那种跟着手指的倾斜。所以默认的 `FocusStyle.HighContrast` 在磁贴外 5 dp 处画一圈 3 dp 白描边，外加一圈淡黑边，保证在亮壁纸上也看得见；描边有自己的透明度弹簧，出现时跟着放大从磁贴边缘长出来，消失得更快，左右移动时不会同时看到两个框。放大是 1.15 倍、临界阻尼（`dampingRatio = 1`）—— 试过 0.66 的回弹，在白框上看起来像在发抖。

**返回键要有地方去。** 在网格里按返回回第一排，在第一排按返回**起屏保**，这是 tvOS 的行为，也被照搬了。

**编辑不该用遥控器。** 电视上显示二维码，手机扫码打开的是同一个图标网格：拖动排序、点一下改名换图标、建文件夹、把 HDMI 加进主屏。实现是一个内嵌的 NanoHTTPD 服务器加一个单文件网页，同一个局域网，没有第三方服务器，也没有手机 App。这条我认为是全文最值得抄的设计：**电视负责显示，手机负责编辑**，两种输入设备各干自己擅长的事。

顺带说一句这个桌面能管到哪一步：HDMI 输入源被当成应用磁贴管理，可以选「接的是 Apple TV / PlayStation / Switch / Xbox / 电脑」，换对应图标、自己起名字，还能设成开机时打开。桌面于是不只是应用列表，而是「这台电视上所有能看的输入」的统一入口。

屏保也在这套东西里：停手一段时间后进屏保，内容是 114 段 Apple TV 航拍（电视支持时播 4K，杜比视界取决于硬件和播放环境），也可以换成照片、时钟，或用手机传上去的视频。首页停在原地约 10 秒，航拍会在磁贴背后开始播，按任意键停在当前画面 —— 影片画在一块垫在界面层下面的 SurfaceView 上，磁贴、时钟和玻璃底板照常画在上面。

## 七、89 行机型记录

回到开头那张表。

![按品牌分组的 89 行机型记录：能用、能用有限制、接管不了]({{ '/assets/img/blog/aerial-tv-launcher-foreground-takeover/fig-06-device-matrix.png' | relative_url }})

_按 README「支持的机型」表逐行统计。一行可能覆盖多款机型，所以这是 89 条记录，不是 89 台电视。_

| 结果         | 行数 | 典型原因                                                                  |
| ------------ | ---- | ------------------------------------------------------------------------- |
| 能用         | 56   | 原生 Android TV；或固件允许第三方当默认桌面                               |
| 能用，有限制 | 23   | 强停后 7–30 秒才回来；开机先露 3–6 秒原桌面；亮度只能在电视自己的设置里调 |
| 接管不了     | 10   | 主页键由固件按组件直开原桌面；无障碍被定期清掉；固件不让写无障碍设置      |

最后那 10 行里，4 行是 Lite 版在 Android 4.x 上的记录。海信的老 VIDAA 更细：遥控器的「主页 / APP / VOD」键被固件走私有通道拉起自家界面，Aerial 接不到。雷鸟 75S78A Plus 的固件约每分钟清一次无障碍。小米电视 2 的主页键由系统直接打开小米桌面，选择框根本不出现。

这不是一张支持矩阵，是一张**失败清单**：每一行都能点进一条 issue 或一份机型笔记，`docs/devices/` 下每个试过的机型都有一份自己的 Markdown，写着「这台电视上哪里不对、试过什么、最后怎么绕」。

配套的是一条诊断流水线：手机页最下面「反馈问题」能生成一份诊断报告（机型、固件指纹、HOME 解析结果、守护状态、各项授权、`TvInputManager` 的实际信号源、最近 150 行内部日志），型号和版本自动填进 GitHub 表单；报告里的 IP、MAC、Wi-Fi 名称和天气城市都打码，不收集账号和已装应用列表。`tools/report.sh` 还能多收一层只有 shell 能读的 `getprop`、appops 和无障碍绑定状态。

**开源硬件软件最难的部分不是写代码，是拿到别人那台电视的证据。** 这份流水线就是为此存在的。

## 八、局限

1. **开机广告去不掉。** 那是固件播的，换桌面管不到。项目在 README 里直接写了这一句，没有把「没有广告」说成「没有广告位」。
2. **原桌面没被卸载，也没被停用。** 它还在应用列表里（小米影视、PatchWall 从「桌面」磁贴进）。这是特性也是边界：想彻底换掉，得 root。
3. **绝大多数电视的界面就是 1080p。** 4K 面板不等于 4K UI，Android TV 的 `config_maxUiWidth` 通常把界面压在 1920；画成 4K 只是多 4 倍绘制量。
4. **固件可以随时封。** 只用「前台窗口」这一个信号加按键注入，遇到每分钟清一次无障碍的固件（雷鸟 T966D5）就是无解，项目也只能写「能装、接管不了」。
5. **安装门槛在产品上，不在代码上。** `WRITE_SECURE_SETTINGS` 只有 ADB 能给；只用 U 盘装 APK 的电视，Aerial 从 1.32 起会在「我的应用」里出现、会提示怎么设为主屏，但主页键还是回原桌面。
6. **航拍影片的版权不属于项目。** 114 段航拍的目录在 `assets/aerials.json`，片子由 Apple 的服务器直接播；Aerial 只是那个目录和播放器。
7. **Lite 是测试版。** Android 4.0–4.4 用另一个模块，包名 `app.orchard.tv.lite`，1.0 只在模拟器和几台新电视上测过。

## 九、我的判断

三件我认为值得继续做、而且可以被验证的事：

**一，把「前台仲裁」抽出来。** 那套「监听窗口 → 判断该不该管 → 退让或接管」的逻辑，和 tvOS 风格没有关系：投影仪、车机、商用大屏都要面对同一个问题，即固件认为前台归它管。现在它长在 `guard/` 里，和这个 App 的首页、儿童与长辈模式缠在一起；抽成一个可复用的运行时，是这个项目最有可能外溢的部分。

**二，让诊断闭环再自动一段。** 现在的人工环节是「把报告变成 `devices.json` 的一条」。报告已经结构化、机型参数已经是 JSON、开关已经是枚举 —— 这一段的自动化程度，决定了这个项目能覆盖多少台电视，而不是能做多好看。

**三，给每种失败模式留一台可回归的机器。** 项目已经有 Android 9 / Android 13 / 4K 几个模拟器镜像，也用 `hid` 造过遥控器来验证按键表。这套东西的价值不在于「测过」，而在于它让第 4 条局限（固件随时能封）变成了一个可以被复现、被讨论的对象。

最后回到我最近一直在写的那条线：MNN 用一张敢给自己标 C 的支持矩阵证明「同一个模型在不同后端上还是不是同一个模型」，colibri 用一道逐字节的闸证明「优化没有改模型」。Aerial 回答的是第三个版本的问题：**同一个桌面，在不同固件上还是不是那个桌面。**

它的答案不是矩阵，也不是闸，而是一份带 issue 号的机型表和一套肯退让的守护逻辑。**这个项目真正的护城河不是那个像 tvOS 的界面，是那 89 行记录，和每一行背后能点开的那条 issue。**

## 项目与资料

- [GitHub 源码](https://github.com/pengchujin/aerial-tv)（MIT）：`app/` 是完整版，`lite/` 是 4.x 版
- [官网](https://aerial.qust.me)：下载、安装脚本、Agent 安装说明
- [README](https://github.com/pengchujin/aerial-tv/blob/main/README.md)：功能、安装步骤、89 行机型表、各品牌开 ADB 的方法
- [docs/ARCHITECTURE.md](https://github.com/pengchujin/aerial-tv/blob/main/docs/ARCHITECTURE.md)：目录结构、`guard/` 的数据流、性能约束与全部帧耗时数字
- [docs/LITE.md](https://github.com/pengchujin/aerial-tv/blob/main/docs/LITE.md)：Android 4.x 版本的边界
- [docs/devices/](https://github.com/pengchujin/aerial-tv/tree/main/docs/devices)：分机型笔记，失败模式的一手记录
- [agent.md](https://aerial.qust.me/agent.md) / [adapt.md](https://aerial.qust.me/adapt.md)：给能执行命令的 Agent 的安装与适配说明

文中框架、机型与性能数字核对自 README、`docs/ARCHITECTURE.md`（2026-11-17 的 main 分支）与 GitHub API；截图取自项目仓库 `site/img/`。89 行统计是对 README 表格逐行的脚本计数。我没有在真机上复现任何一条接管行为，也没有构建过这个 APK。
