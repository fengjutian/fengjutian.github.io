---
layout: post
title: DroidDeck：手机跑 PC 游戏不难，难的是让 Android 相信自己正在当主机
date: 2026-11-17 14:25:00 +0800
thumbnail: assets/img/blog/droiddeck-android-handheld-host.jpg
description: 两个月两万星、十九万次下载之后，DroidDeck 的发布说明里几乎没有一句在讲模拟器：全是 proot 的微秒、ntsync 的往返、双屏的焦点。拆开看它到底补了 Android 缺的哪几层。
tags: [开源, Android, 游戏]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/droiddeck-android-handheld-host.jpg
---

一台骁龙手机接上手柄，进 Steam 大屏界面，点开《荒野大镖客 2》，退出游戏，切到 KDE 桌面开终端。

这套流程听起来像云游戏，其实是本地跑的。项目叫 DroidDeck：

- 源码：[Droid-Deck/DroidDeck](https://github.com/Droid-Deck/DroidDeck)（GPL-3.0）
- 官网：[droid-deck.dev](https://droid-deck.dev)（README 特意写了一句：只从这个仓库的 Releases 下载）
- 形态：一个 Android APK，加一套要另外下载的 Linux 运行时

我在它身上花了一晚上，最后想明白一件事，也是这篇要讲的全部：**FEX 和 Wine 早就有别人写好了，DroidDeck 真正在写的是它们和 Android 之间的那一层。**翻译 x86 只是这件事里最不新鲜的部分。

## 一、三个数字

**20,543。**这是本文写作时（2026-11-17）的 star 数。仓库建于 2026-09-24，也就是说这些星是八周内涨起来的。

**195,108。**0.7.1 主 APK 的下载次数，发布七天。APK 本身 92.1 MB，同版本还有三个换了包名的构建（PUBG、安兔兔、鲁大师），各自还有几千次下载。

**1.7 µs。**0.6.7 之后，Wine 两个线程之间一次 event ping-pong 的往返成本。动手之前是 24–29 µs。

第三个数字最能说明这个项目是什么：一个「让手机玩 PC 游戏」的项目，发布说明里最长的段落却在讨论互斥量等待和进程快照——因为它遇到的瓶颈，早就不是「x86 指令怎么在 ARM 上跑」了。

## 二、先说清楚它不是什么

大部分介绍会把它写成「Wine + Proton 的游戏模拟器」。这个说法把主次搞反了。按代码归属摊开看：

| 层                   | 是谁的代码                        | DroidDeck 做了什么                       |
| -------------------- | --------------------------------- | ---------------------------------------- |
| Android 启动器与会话 | 自己的 Kotlin / Compose           | 十英尺界面、会话守护、输入路由、驱动选择 |
| Linux 用户空间       | Ubuntu 26.04 + Kubuntu Plasma     | 打包、裁剪、注入 shim                    |
| 系统调用边界         | PRoot                             | 18 个补丁 + 一个 `libblfastpath.so`      |
| x86-64 指令          | FEX-Emu（MIT）                    | 自己的构建、TSO 行为、AppImage 启动链    |
| Windows API          | Wine（经 DroidDeck-Proton）       | 跟着 GE-Proton11-12 走，补 ARM64 的坑    |
| 图形翻译             | DXVK / VKD3D-Proton / Zink        | 编成 ARM64X，按 GPU 选版本               |
| GPU 驱动             | Mesa / Turnip / RADV              | DD-Turnip 分支、MaliBridge、补丁         |
| 合成与帧控           | gamescope（BSD-2）                | 帧率上限、亮度音量接管、焦点             |
| 商店后端             | Legendary / gogdl / nexus-backend | 挑着用，挑不动的自己写                   |

真正属于「模拟器」的那一格，几乎全是别人的。项目自己在写的是**宿主**：一台 Android 手机上本来不存在的、SteamOS 有的那些系统服务。

## 三、两个世界，一条桥

Android 应用进程是唯一有权限的那一侧：只有它的 `nativeLibraryDir` 允许 `exec`，只有它能拿 Surface，只有它能碰电源和手柄。Linux 那一侧跑在 ptrace 之下，没有 root、没有真的 `/`、`/proc` 是编出来的。

![Android 侧的启动器与会话守护，和 ptrace 之下的 Linux 客人；中间是 DroidDeck 自己写的那条带子]({{ '/assets/img/blog/droiddeck/fig-01-two-worlds.png' | relative_url }})

_上下两块都是别人的代码。项目的工程量集中在中间：三条通道、两个方向。_

桥上有三条通道：

1. **系统调用翻译**。客人的每次 `openat` 都要被改写成宿主的真实路径，这条路的成本决定了整个运行时的下限（下一节）。
2. **agent**。会话里常驻一个 `droiddeck-agent`，它用会话自己的环境执行命令、发布 gamescope 的焦点、连 Steam 客户端的 DevTools（那个端口只接受客人进程）。宿主和它用会话根目录下的请求/应答文件通信——不是 socket，不是 binder，就是文件。
3. **Surface 合成**。gamescope 画出来的东西要变成 Android 的一个 `SurfaceView`，反过来触摸和手柄事件要穿过去。

这三条通道解释了这个项目为什么长成这样：它不是一个被移植过来的 Linux 桌面，而是一个 Android 应用**假装**自己有一个 Linux 子系统。

## 四、proot：把每条系统调用从 60 微秒砍到 2 微秒

PRoot 用 ptrace 实现 `chroot` 和 bind mount：客人每发一次系统调用，内核停两次，PRoot 改写参数再放行。它能跑，但每条路径调用要 15–60 µs。

DroidDeck 维护了 18 个 PRoot 补丁，外加一个 `libblfastpath.so`：libc 的 `open`/`stat`/`access` 这些包装函数在进内核之前就被拦下来直接翻译，成本降到 0.6–1.9 µs。`exec` 仍然要 0.4–0.8 ms，因为那条路躲不开 ptrace。

这个优化有个明确的边界，项目自己写得很清楚：**glibc 内部**的路径调用（ld.so、fts、realpath、nss、`__open_nocancel`）和裸 `svc` 指令仍然走 PRoot，还是 15–60 µs。所以 `find` 扫两千七百个文件的速度不会变。

更值得读的是 `docs/development/proroot-analysis.md`。那是一份对一个闭源竞品（proroot）的静态分析：作者用 NDK 的 `llvm-readelf`、`llvm-nm`、`llvm-strings` 把五个 arm64 二进制读了一遍，画出它的架构——不用 ptrace，而是在加载时把 glibc 里的 `svc #0` 指令**就地改写**成跳转，落到自己的 trampoline 上。

结论是「不换」：

> proroot 不是替换 proot 的模板。它没有 tracer 可以兜底，漏掉一个调用点、或者遇到一个没见过的 glibc，就会静默地破坏隔离或正确性。它对 DroidDeck 的价值，是作为 proot **前面**的一条快路径。
>
> ——译自 `docs/development/proroot-analysis.md`

我很少在项目文档里看到这么干脆的「我们评估过，不采用，理由是」。同一份文档里还给出了具体做法：在自己的 `libblfastpath.so` 构造器里 patch glibc 的 svc 站点，把快路径的覆盖面从 libc 包装推进到 glibc 内部。

## 五、让线程能等：ntsync 和一次上下文切换

把路径翻译做快之后，下一个瓶颈是**等待**。游戏是多线程的，Wine 需要实现 Windows 的 event、semaphore、mutex，而 Android 的内核里没有能直接对应的东西。

Linux 内核有一种叫 ntsync 的驱动，专门实现 NT 的同步对象语义。Android 上没有它，所以项目自己写了一份 `droiddeck-ntsync`，语义照着内核文档 `Documentation/userspace-api/ntsync.rst` 实现，并从 0.6.7 起成为 Wine 的默认同步方式。

效果是这样的：

![五组操作在改动前后的成本，每行按自己的 before 归一化]({{ '/assets/img/blog/droiddeck/fig-02-microsecond-ledger.png' | relative_url }})

_这些数字全部来自项目自己的发布说明和开发文档；每组是独立的测量，不能横着比。_

- 两个线程之间的 event ping-pong：24–29 µs → **1.7–2.0 µs**
- 信号量和互斥量等待：约 **0.12 µs**
- x86 程序里的 `RaiseException` 在 Proton 里被处理：14.7–20.3 µs → **2.2–2.7 µs**（Wine 的 arm64 上下文切换不再经过内核信号）
- Windows 进程快照：5.9–7.6 ms → **2.4–3.4 ms**，因为进程列表直接读 `/proc` 拿内存计数
- 《荒野大镖客 2》启动期间的 PRoot 停顿：**少 47%**；状态文件拷贝从每分钟约 7,000 次降到 **9 次**
- 《龙与地下城 Online》进图：50 秒 → **4 秒**（FEX 不再丢弃翻译好的代码块，也不再去碰 Wine 的内存锁）

这就是那三个数字背后的东西。帧数不是靠某个神奇的翻译器提上去的，是靠把几十万次、每次几十微秒的操作逐个变成几微秒。

## 六、两套 Steam 客户端

这一节是我读文档时最意外的部分。

Steam 客户端本身**不是**跑在 Proton 里的。DroidDeck 默认安装的是 Valve 给 Steam Deck 编译的 **arm64 Linux 原生客户端**（`steamrtarm64/steam`）——Valve 并不支持这个构建，只是把它发布在 Steam Deck 的客户端通道上。

安装器只保留清单里的 `*_linuxarm64_linuxarm64` 那一个块，跳过 Valve 同时发布的 x86-64 SteamRT 3c 客户端。x86-64 客户端走 FEX 是**回退方案**：如果哪天的清单里 arm64 块消失了，才退到那一步。

通道逻辑里也能看出这套东西有多脆：

| 情况                           | 行为                                            |
| ------------------------------ | ----------------------------------------------- |
| 默认                           | `steamdeck_publicbeta`（清单 `..._linuxarm64`） |
| 客户端连续两次启动后没显示出来 | 触发修复；再两次，自动退到 `steamdeck_stable`   |
| beta 清单里没有 arm64 组件     | 安装日志列出清单的块名，退到 stable             |
| stable 也没了                  | 只剩 x86-64 客户端走 FEX                        |

还有一个只有在这种环境里才会遇到的问题：Valve 2026-10-15 的 beta 把 x86 客户端塞进了 Steam Runtime 容器（pressure-vessel），而那个容器需要非特权的 user/mount namespace 和一个 D-Bus session bus——Android 应用两样都没有。于是有了 `STEAM_STEAMRT_RECURSION_GUARD`（告诉客户端它已经在容器里，别再自己套一层）和一个 `droiddeck-steamrt-shim`：逐文件链接 Valve 的运行时，把 `steam-runtime-check-requirements` 换成 `exit 0`。

**你在别人的平台上跑一个别人不支持的构建，就意味着要替它维护一整套降级路径。**这一段比我读过的任何「SteamOS 兼容层」介绍都具体。

## 七、图形：一条 D3D 调用，四条驱动路径

游戏发出的还是 Direct3D，出口只有一个 Vulkan。

![D3D 经 DXVK / VKD3D-Proton / Zink 落到 Vulkan，再由 Auto 按 GPU 挑一对驱动]({{ '/assets/img/blog/droiddeck/fig-03-gpu-driver-paths.png' | relative_url }})

_六个格子里只有一个状态是「默认」。_

几个值得单独说的点：

**DXVK 和 VKD3D-Proton 编成了 ARM64X。**这不是性能优化，是正确性要求：Wine 既能跑被 FEX 翻译的 x64 程序，也能跑原生 arm64 的 Windows 程序（比如 `Wow-arm64.exe`）。原生程序加载不了只有 ARM64EC 的 `dxgi.dll`，所以每个 DLL 都得两种都有。项目文档里甚至写了这条规则的例外条件：只有当包里每个 Direct3D 和 DXGI DLL 都是 ARM64X 时，才给 ARM64X 的 Proton 用 `arm64ec` 包。

**Turnip 默认走系统内存。**游戏、Steam 客户端、模拟器和 AppImage/Flatpak/Snap 程序默认带 `TU_DEBUG=sysmem`，也就是 Turnip 的系统内存渲染路径。文档只写了默认值和开关，没写原因（我的猜测是 tiled 内存在这类设备上更不稳，但这是推测）。0.7.1 之后模拟器可以拿到「游戏 GPU 设置」，不再被一律按系统内存处理。

**DD-Turnip 是 Turnip 的一个分支。**0.4.0 换到更新的 Mesa，修的是 Adreno 8xx 上间接绘制过早读取参数的问题——现象是 UE5 游戏经 VKD3D-Proton 跑起来地面全黑或阴影过重。

**非 Adreno 是另一套栈。**Mali 走 MaliBridge 加 Venus（把客人的 Vulkan 转发给主机），Xclipse 950/960 用上游 RADV 的一对驱动，PowerVR 用自带 Mesa 加一个补丁（`d55418dae7`，修 Zink 下颜色纹理掉色，0.7.1 修的就是 Pixel 10 Pro 上的灰度画面）。Adreno 6xx 按公开的表格选，DXVK 固定停在 gplasync 2.7.1。

**Adreno 710 那两档目前没法选。**README 写得很直白：Adreno 710 不受支持；710 和 720 用的那对驱动永远走 sysmem，关不掉。0.6.7 之后 Retroid Pocket Duo 的 Adreno 722 能被认成 Supported，但那是另一档。

至于 D3D12，0.6.7 补上了 feature level 12_1，于是《赛博朋克 2077》能过掉光追初始化，《机械战警：暴戾之城》和 ReSkate 能跑。ReSkate 需要 12_1 这一条，是写在它的 README 里的。

![Mali 设备上打开 GPU via Mali bridge 之后的样子]({{ '/assets/img/blog/droiddeck/shot-mali-gpu.jpg' | relative_url }})

_0.7.0 才开始有 Mali / PowerVR / Xclipse 的初步支持，截图来自官方发布说明。_

## 八、商店：跑厂商的客户端，还是重写它的协议

DroidDeck 支持 Steam、GOG、Epic、Xbox、EA、Battle.net、itch.io、Game Jolt（0.7.0 加入）。它不是「把八个启动器塞进一个壳」，每个商店的实现策略都不一样，而策略的选择标准很清楚：**能跑厂商自己的客户端就跑，跑不动就把协议重写一遍。**

| 商店       | 策略                                                                 |
| ---------- | -------------------------------------------------------------------- |
| Steam      | 官方客户端，arm64 原生（见上一节）                                   |
| GOG        | gogdl，支持 depot 增量、修复复用已校验分块、银河格式云存档           |
| Epic       | Legendary 的一个改造分支；官方 Linux 启动器预览版走 FEX              |
| Xbox       | nexus-backend 0.2.15（Xodus 分支）+ nexus-runtime 的 Windows 模块    |
| EA         | 按 EA app 的协议自己实现（GraphQL 查询原样内嵌，因为 EA 按哈希匹配） |
| Battle.net | 跑暴雪**真实客户端**，在独立的 Proton prefix 里                      |
| itch.io    | butler，附带 itch.io 自己编的 7-Zip                                  |
| Game Jolt  | 和 itch.io 同一套浏览/安装/更新逻辑                                  |

几个细节值得单独拎出来：

- **Xbox 需要真的 Windows 模块。**`nexus-runtime` 提供 `wintypes.dll`、C++ 的 `nexus-xgameruntime`，游戏才能加载。授权走的是 delegation-compact 设备票据。云游戏是另一条路：WebRTC 客户端来自 Greenlight，默认网页播放器，可选的原生播放器能叠 DroidDeck 自己的帧生成。
- **EA 商店的代码是项目自己的**，但协议不是猜出来的——照着 Maxima 记录下来的 EA app 流程走：登录、GraphQL、构建归档、在线激活许可证、LSX 游戏端点。
- **《魔兽世界》的插件**可以从 zip 导入，能通过 WoWInterface 的 MMOUI 接口搜索，CurseForge 直接开浏览器（无 API、无 key）。
- **Battle.net 中国区**、安装在 microSD 和 USB SSD 上、11 GB 手机上《暗黑 4》需要的内存选项，都在 0.6.7 到 0.7.1 之间修过。

这就是「开源兼容层」最难的部分：不是写代码，是**跟着别人随时会变的私有协议跑**。

## 九、掌机感是这些细节堆出来的

真正的掌机不是「能启动游戏」，是亮度键、音量键、暂停、双屏、待机都对得上。这一段是 DroidDeck 和「手机上的 Steam 前端」差距最大的地方。

**双屏。**Retroid Pocket Duo 和 AYN Thor 这类设备，下屏可以放 Dashboard（下载、截图、Steam 聊天、游戏内数据）、键盘加触控板、终端、Deck grips，或者一整张 **KDE 桌面**。桌面和游戏可以交换屏幕，游戏在下屏、桌面上屏跑 fastfetch 都行。当别的应用占了下屏（比如 Retroid 自己的性能面板），DroidDeck 会切回单屏模式，拿回来再切回去。

![上屏 Redout，下屏 Dashboard 的 In-game stats：60.2 fps、DXVK、16.6 ms、68°C 和每个核的频率]({{ '/assets/img/blog/droiddeck/shot-dual-screen-dashboard.jpg' | relative_url }})

_In-game stats 不只显示帧率，它读的是游戏自己输出的遥测——赛车游戏的速度、挡位、转速、踏板。_

顺带一个反面案例：AYN Odin 2 系列曾经被识别出一个「不存在的第二屏」，导致侧边栏和返回菜单消失。0.7.0 修了——自动双屏现在要求真的存在第二块触摸屏。

**HUD。**DroidDeck HUD 是 FusionHUD 的分支（GPL-3.0，带署名条款），读数对齐 Valve 的 MangoHud 构建，帧时间来自 gamescope 的补丁。它现在有五种尺寸加一个横条样式，可以拖到屏幕边缘收成一个小标签，能分别开关 1% 和 0.1% low。0.7.0 之后，即使系统不给读 GPU 负载和频率（比如 Retroid Pocket Duo 和部分 Adreno 8xx），HUD 也能显示。

![横条 HUD 压在 Steam 大屏界面顶部，一排显示帧率、帧时间、low、GPU、CPU、温度、显存、内存、电池和 Adreno 740]({{ '/assets/img/blog/droiddeck/shot-hud-strip.jpg' | relative_url }})

_横条样式：一行放下 FPS、帧时间曲线、1%/0.1% low、GPU、CPU、温度、VRAM、RAM、电池、GPU 型号和时钟。_

**键鼠和手柄。**硬件鼠标键盘接到了「像 PC」的程度：隐藏光标的游戏里镜头不再冻结，Steam 会话里能看见指针，点击落在你指的位置。0.7.0 加了统一的控制器配置档——一个命名档同时描述实体手柄、主屏布局和副屏布局，用一个全尺寸编辑器改。摇杆死区 0 到 25% 可调。长按 Back 就是 Steam Deck 上的 QAM 键，Steam 会弹出自己的快捷键列表；长按 Home 发 Steam Guide 键。

**桌面是一张真的桌面。**0.6.7 起是 Ubuntu 26.04 LTS 加 Kubuntu 的 Plasma，Discover、`apt`、Flatpak、Snap 都能用，Android 的键盘和「下载」「文档」文件夹直接映射进去。

![Kubuntu 桌面上的 Discover 在列 Ubuntu 目录里的应用]({{ '/assets/img/blog/droiddeck/shot-kubuntu-desktop.jpg' | relative_url }})

_README 的局限里写了两条：桌面合成是软件渲染，Firefox 在 proot 下的沙箱被削弱。_

## 十、功耗：从 9.5 W 到 7.1 W

掌机是被电池定义的。这一段的数字比帧数更让我意外：

- 锁 60 fps 的一局游戏：**9.5 W → 7.1 W**（0.6.7 的帧调度重写，屏幕 tick 独立成线程，新帧到就画）
- 画中画里挂着的会话降到 30 fps：在 RedMagic Astra 2 上省约 **1 W**
- 挂起一整夜：电量掉 **2%**
- 恢复会话时立刻从 zram 读回内存，而不是让重游戏卡上几分钟
- 内存 ≤13 GB 的设备上，游戏会立刻读回的那部分内存不再每 30 秒被重新压缩一次

还有一条我觉得最能说明「在别人的系统里」：骁龙 8 Gen 2 上，Steam 曾经被默认钉在一个核上跑；改成不钉之后，Steam 菜单的 1% low 从 41.7 fps 变成 62.5 fps。

同一个思路还出现在发行方式上。同一份代码发布**四个包名**：`com.droiddeck.launcher`，以及 `com.tencent.ig`（PUBG）、`com.antutu.benchmark.full`、`com.ludashi.benchmark`。文档只说明发布流程会分别签这四个包，没写理由。从包名和 Android 的每应用调度策略看，这更像是为了拿到系统给「游戏 / 跑分应用」的那份调度和锁频待遇——**这是我的推断，不是官方说法**。

## 十一、眼镜、VR，和住在掌机里的 agent

**智能眼镜是有分级表的。**VITURE（One/Pro/Luma/Beast/Pro 2）、RayNeo Air/GT、XREAL（1S、One、One Pro、One Pro+、Aura）、Rokid Max/Max 2 都在支持矩阵里，分成「集成」「依赖 SDK」「实验性」「只出画面」四级。集成意味着真的有 USB 传输和 IMU 读数；只出画面意味着 Android 能投个屏，DroidDeck 管不了它。

能力上分 3DoF（转头、俯仰、翻滚，绕一块虚拟屏幕）和 6DoF（加上位移）。6DoF 目前只有 VITURE Luma Ultra 是「实验性、需要手动打开」。这份文档写得非常克制，连「一个不认识的显示模式索引会让 Aura 重启」这种坑都写了。

**手部追踪是手机摄像头做的。**MediaPipe 的 Pose Landmarker (Lite)、BlazePose GHUM 3D、Hand Landmarker 跑在 CameraX 的帧上，配合 Kalman 滤波、1€ 滤波、Horn 的四元数方法做融合。Joy-Con 手柄的体感位置移植了 Google GVR SDK 的手臂模型，手部骨架来自 Valve OpenVR 的 `handskeletonsimulation` 样例。SteamVR 是直接立体渲染，不是投一块虚拟屏。

**最后一件我觉得很 2026 的事：掌机里住着一个 agent。**

DroidDeck 带一个 `droiddeckctl`，通过 ADB 驱动整台设备：起停会话、启动游戏、等游戏拿到焦点、发输入、抓 UI 树、截图录像、进会话里跑命令。背后是一个 `content://com.droiddeck.launcher.agent` 的 provider，要求 `DUMP` 权限（ADB shell 有）。

有意思的是 UI 树怎么抓：它**从应用内部读 Compose 的语义树**，而不是用 UI Automator——因为在双屏设备上，UI Automator 抓的是当前获得焦点的窗口，那经常是别的应用。

更妙的是应用里那个 Agent tab：它把 `tools/agent/AGENTS.md` 和一套 skills 写进设备上 Claude Code 和 Codex 的全局指令与 skills 目录，只替换自己那一块标记，用户自己写的东西不动。也就是说，你可以在掌机上让一个 agent 帮你调这台掌机。

## 十二、它做不到什么

按重要性排：

1. **桌面合成是软件渲染的。**这是 README 自己列的第一条局限。KDE 能用，但没有 GPU 合成那种流畅度。
2. **proot 下 Firefox 的沙箱被削弱。**这是架构决定的，不是没修。
3. **Adreno 710 完全不受支持**，720 只能走固定驱动。买设备前要查表。
4. **兼容性和性能按机型、驱动、游戏、散热剧烈变化。**README 的原话是「vary by device」。
5. **Android 14 及以上要关掉「子进程限制」。**这是一个真实的安全妥协，项目给的替代是「Fix it for me」引导按钮。0.6.7 还因为一个无障碍服务把若干银行应用挡在门外，0.6.9 才改成只在你真的打开时才声明。
6. **它在追一个别人不管的构建。**Valve 不支持 arm64 客户端，随时可能改清单。
7. **商店协议会变。**EA 的 GraphQL 按哈希匹配、GOG 的登录要过 Cloudflare、Battle.net 有中国区差异——每一条都是长期维护成本。
8. **仓库还很年轻。**2026-09-24 建仓，本文写作时有 623 个 open issue。0.7.1 本身就是在修 0.7.0 引入的「Processing install script」卡死和无尽加载。
9. **92 MB 的 APK + 约 3 GB 运行时 + 1.1 GB 桌面和模拟器。**这不是一个轻量方案。

## 十三、我的判断

我不觉得这个项目最重要的意义是「手机能跑 PC 游戏」。那件事在它出现之前就有人做过，做得也不差。

它证明的是另一件事：**Android 缺的不是性能，是一层能被别人补上的宿主服务。**前台抢占、可等待的线程原语、能翻译的系统调用、能合成的 Surface、能停下来的挂起——这些东西 SteamOS 天生就有，Android 天生没有，而它们全都可以在应用层补出来，代价是微秒级的账要一笔一笔算。

这也让它的技术路线有一个可验证的岔路口。0.7.0 的发布说明里提到「原生 ARM64 程序的 `dxgi.dll`」和「ARM64EC 调用方仍然跳过模拟器」——如果 Windows 游戏开始出 arm64 原生版本，FEX 这一层会缩水；而 proot、ntsync、双屏焦点、商店协议这些胶水，只会更值钱。

换句话说：**翻译层会过时，宿主层不会。**这大概是我从这个仓库里学到的最有用的一句话。

## 项目与资料

- 仓库：[Droid-Deck/DroidDeck](https://github.com/Droid-Deck/DroidDeck)
- 发布：[Releases](https://github.com/Droid-Deck/DroidDeck/releases)（0.7.1，2026-11-10）
- 官网：[droid-deck.dev](https://droid-deck.dev)
- 发布说明归档：[docs/releases](https://github.com/Droid-Deck/DroidDeck/tree/main/docs/releases)
- 开发者文档：[docs/development](https://github.com/Droid-Deck/DroidDeck/tree/main/docs/development)（`proroot-analysis.md`、`game-environment.md`、`x86-64-steam-client.md` 值得读）
- 眼镜支持矩阵：[docs/smart-glasses-support.md](https://github.com/Droid-Deck/DroidDeck/blob/main/docs/smart-glasses-support.md)
- 开发进度日志：[docs/progress-log.md](https://github.com/Droid-Deck/DroidDeck/blob/main/docs/progress-log.md)

**许可证：**GPL-3.0。

**图片说明：**本文的四张截图取自项目官方 Releases 的发布说明（`docs/releases/media`），按 GPL-3.0 使用并注明来源；三张示意图是我根据 README 与开发文档绘制的，不是项目官方架构图。文中所有性能数字都来自项目自己的发布说明或开发文档，没有第三方复测。
