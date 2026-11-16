---
layout: post
title: Airgorah：把 root 赶出 GUI 之后，每个跨边界的参数都得重新验一遍
date: 2026-11-16 13:10:00 +0800
thumbnail: assets/img/blog/airgorah-privilege-boundary.jpg
description: 从 0600 的 socket、SO_PEERCRED 的 uid 校验到 16 个 IPC 请求的参数重验，拆解 Airgorah 如何把 root 关进一个只服务单客户端的 agent。
tags: [开源, 开发者工具, 架构设计]
categories: [技术随笔, 工程实践]
featured: true
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/airgorah-privilege-boundary.jpg
---

把一个 root 进程拆成两个进程，安全性并不会自动变好。

真正起作用的是拆分**之后**被迫写出来的那些检查：当 GUI 不再是 root，它就从「程序的一部分」变成了「一个不可信的调用方」。Airgorah 把这个转折点做得很老实——它没有只画一张架构图，而是把每个跨边界的字符串都重新验了一遍。

- GitHub：[martin-olivier/airgorah](https://github.com/martin-olivier/airgorah)（MIT，v0.9.0）
- 技术栈：Rust（edition 2024）、GTK4、Polkit、Linux 无线子系统
- 本文依据：README、`crates/` 源码（`ipc.rs`、`server.rs`、`main.rs`、`validate.rs`、`deps.rs`、`interface.rs`）、polkit 策略文件与 release changelog

只在自己拥有或获得书面授权的网络上使用这类工具，是本文不再重复的前提。

## 一、三个数字

| 数字   | 在哪                             | 管什么                          |
| ------ | -------------------------------- | ------------------------------- |
| `0600` | agent 创建 socket 后立刻 `chmod` | 除了启动用户和 root，谁都打不开 |
| `16`   | `Request` 枚举的变体数           | 跨边界的**全部**能力清单        |
| `1`    | `listener.accept()` 被调用一次   | 一个 agent 只服务一个客户端     |

0600 是文件系统层的门，16 是协议层的门，1 是生命周期层的门。**三者叠在一起，才构成「agent 只被它启动的那个 GUI 驱动」这句话。**

## 二、它是什么

Airgorah 是一个 Linux 上的 Wi-Fi 安全审计 GUI：扫描周边 AP 与客户端、把网卡切到监听模式、抓包、采集 WPA 握手与 PMKID，最后用词表或掩码爆破验证密码强度。

0.9.0 做了一件不太显眼但很关键的事：**把 `aircrack-ng` 套件和 `mergecap` 从依赖里拿掉了。**扫描、抓包、握手与 PMKID 的解析现在由 Rust 自己完成（`raw_socket.rs` + `sniffer.rs` + `pcap.rs` + `pmkid.rs`），不再需要 `airodump-ng` / `aireplay-ng` 在旁边跑。

但 `aircrack-ng` 并没有消失：它仍是**可选**依赖，用在最后那一步真正的口令破解上（详见第八节）。这个区分很重要——审计流水线是自包含的，破解不是。

## 三、0.8.0：分水岭

| 维度     | 0.8.0 之前             | 0.8.0 之后                         |
| -------- | ---------------------- | ---------------------------------- |
| 进程     | 单个 root 的 GTK 进程  | 普通用户 GUI + root agent          |
| 会话类型 | X11 可用，Wayland 不行 | 两者都可以                         |
| 提权时机 | 启动即 root            | 选完网卡、第一次特权操作时才提权   |
| 设置位置 | `/etc`                 | `$XDG_CONFIG_HOME/airgorah`        |
| 临时抓包 | `/tmp`                 | `/run/airgorah`（tmpfs，重启即空） |

release note 自己写得很清楚：单个 root GTK 进程被拆成「非特权 GUI + 小型特权 agent」，程序因此才能在 Wayland 下工作。**权限模型的改动顺手解决了一个兼容性问题**——这通常是重构做对了的信号。

## 四、边界画在哪

![两个进程与一条 socket]({{ '/assets/img/blog/airgorah-privilege-boundary/fig-01-two-processes.png' | relative_url }})

_root 只在右边那半边；GUI 启动时甚至不会拉起 agent，只检查二进制在不在旁边。_

agent 是 root，但它只 accept 一次、只服务自己的启动者、并且随 GUI 一起退出。

**第一，它只 accept 一次。**`main()` 里 `listener.accept()` 拿到第一个连接、验过身份后就进入请求循环，监听队列不再被消费。多出来的连接只能排队等着——而它们等不到。

**第二，它只服务自己的启动者。**连接进来先做 `SO_PEERCRED` 检查：

```rust
pub fn authorized(stream: &UnixStream, expected_uid: u32) -> bool {
    match getsockopt(stream, PeerCredentials) {
        Ok(cred) => cred.uid() == expected_uid,
        ...
    }
}
```

源码注释把后果写在了明处：没有这一步，本机任何用户都能通过这个 socket 驱动特权操作——包括 deauth。`expected_uid` 来自 `PKEXEC_UID`（pkexec 会把它导出来），没有就走 `getuid()`。

**第三，它和 GUI 一一对应。**socket 路径是 `/run/airgorah/<uid>-<gui pid>.sock`；agent 的「实例号」取的是自己的 `getppid()`——因为 pkexec 是原地 exec，它的父进程正是那个 GUI。两边各自推导、谁也不传参数，路径自然对上。

然后是收尾：socket 建成后立刻 `chmod 0600` 并 `chown` 给启动用户；`/run/airgorah` 本身 0755，抓包目录 0700。客户端断连（EOF）或收到 SIGINT/SIGTERM 时，agent 执行 `app_cleanup()` 并把 socket 文件删掉——**网卡不会带着一个孤儿扫描留在监听模式里**，这是这类工具最常见的现场事故。

## 五、16 个请求与五道门

![一次特权请求的五道门]({{ '/assets/img/blog/airgorah-privilege-boundary/fig-02-five-gates.png' | relative_url }})

_线格式是 4 字节大端长度前缀 + JSON，单帧硬上限 64 MiB。_

跨边界的能力被枚举成一个封闭的集合，一共 16 个：

| 类别     | 请求                                                                    |
| -------- | ----------------------------------------------------------------------- |
| 握手     | `Hello { version }`                                                     |
| 网卡     | `EnableMonitor`、`SetMac`、`DisableMonitor`                             |
| 扫描     | `StartScan`、`StopScan`、`IsScanning`、`ResetScanData`、`GetScanData`   |
| 攻击     | `StartDeauth`、`StopDeauth`、`StopAllDeauth`、`StartPmkid`、`StopPmkid` |
| 抓包     | `GetCaptureChunk { offset }`                                            |
| 生命周期 | `Shutdown`                                                              |

响应只有 6 种（`Ok`、`Error`、`Setup`、`Bool`、`ScanData`、`CaptureChunk`）。

**封闭枚举本身就是一种安全属性**：GUI 能要求的特权动作，等于这个枚举的全部内容，不会因为拼接了一句 shell 命令而变多。而 `Hello` 那一格里同时做了两件事——版本不一致直接拒绝（避免新 GUI 配旧 agent 的字段错位），并顺带回一句「缺了哪些依赖」。

值得注意的是哪些操作**没有**过边界：枚举网卡、探测 5 GHz 能力这些都不需要 root，`ipc.rs` 的注释明说它们留在 GUI 侧，只有监听模式的控制才跨过去。**能不过界就不过界**，这比把边界画好看更重要。

## 六、GUI 是低信任方

`server.rs` 的开头有一句可以直接抄进教科书的话：

> Every request is authorized by peer credentials before this module is reached, and each request argument that becomes a command line is re-validated here, because the GUI is a lower-trust caller once the privilege boundary exists.

翻译过来：**一旦存在特权边界，GUI 就降级成了低信任调用方。**这不是对自家 GUI 的怀疑，而是对「边界」这个词的定义——如果边界另一侧的输入不再被检查，那这条边界只是进程拆分，不是安全边界。

于是 `validate.rs` 只做两件事，但做得够狠：

| 输入     | 规则                                                                      | 防的是什么                   |
| -------- | ------------------------------------------------------------------------- | ---------------------------- |
| 网卡名   | 非空、≤15 字符、不以 `-` 开头、不是 `.` 或 `..`、只允许字母数字与 `_ . -` | 选项注入、路径穿越、奇怪字符 |
| MAC      | 必须是 `xx:xx:xx:xx:xx:xx` 六组十六进制                                   | 注入到 `macchanger` 参数里   |
| 信道过滤 | 必须是已知信道、属于已勾选频段、不重复、不许尾随逗号                      | 把任意字符串塞进扫描参数     |

信道那条规则放在 `crates/common/src/channel.rs` 里被两边共用：GUI 先验一遍是为了给用户即时反馈，agent 再验一遍是为了安全。**同一个函数，两个调用点，两种目的**——这是共享代码里少见的、目的写得很清楚的例子。它还带了一组单元测试，连 `1,,6`、`1,`、`6,6` 这种输入都覆盖了。

还有一条容易被忽略：`StartDeauth` 要求 BSSID **必须已经出现在 agent 自己的扫描结果里**，否则直接返回「unknown access point」。参数合法不等于目标合法——这一层用的是 agent 自己观察到的状态，而不是 GUI 的声称。

## 七、落盘为什么不交给 root

![抓包的分块回传]({{ '/assets/img/blog/airgorah-privilege-boundary/fig-03-capture-streaming.png' | relative_url }})

_capture 留在 root 的 0700 目录里，GUI 按 offset 一块一块取回来，以自己的身份写文件。_

抓包保存的接口是 `GetCaptureChunk { offset }`，返回 `{ data, last }`。GUI 循环取块、累加 offset、自己 `File::create(path)` 写到用户选的位置。

如果换成「agent 直接写 `/home/you/capture.pcap`」，看起来只省了一个接口，实际上把一整类问题搬进了 root 进程：用户提供的路径可能是软链接、可能被替换、可能在检查和使用之间变掉；家目录的权限、挂载点、`umask`，全都变成 root 要考虑的事。

**特权进程不该跟随一个用户提供的路径去写文件。**这条比很多「最小权限」的口号都具体。

## 八、几个不显眼但会咬人的细节

**杀网络管理器之前，先记账。**启用监听模式时如果勾了「杀掉干扰服务」，agent 会用 `systemctl` 逐个检查 19 个候选（`NetworkManager`、`wpa_supplicant`、`iwd`、`dhcpcd`……），停掉正在跑的，并把名字压进一个栈；退出时按栈恢复。没有 `systemctl` 就跳过而不是报错。

**监听模式用 `ip` + `iw`，不用 `airmon-ng`。**`ip link set dev X down` → `iw dev X set type monitor` → `ip link set dev X up`。改 MAC 之前先确认网卡真的在 monitor 模式，否则报错而不是静默失败。

**破解在 xterm 里、以用户身份跑。**`xterm -hold -e aircrack-ng …`，爆破则是 `xterm -e sh -c 'crunch … | aircrack-ng …'`。这一步不进 agent——也就不需要 root。代价是 GUI 的必需依赖变成了 `sh`、`xterm`、`iw` 三件。

**依赖清单按进程分。**`deps.rs` 里每个工具都标了 `Requirer::{Gui, Agent, Both}`，各自在**自己的** PATH 里检查，因为 agent 是 root，`/usr/sbin` 在它的 PATH 里而普通用户看不到。必需的就 5 个（`sh`、`iw`、`xterm`、`ip`、`macchanger`），可选 4 个（`aircrack-ng`、`crunch`、`systemctl`、`pkexec`）。

**提权是懒加载的。**启动时不调 agent，只确认 `airgorah-agent` 就在 GUI 旁边；第一次需要特权的动作才 `pkexec`，并且等连接时有 120 秒上限；如果 pkexec 提前退出（用户点了取消），立刻报「authentication may have been cancelled」，而不是傻等到超时。以 root 直接跑 GUI 会打一条警告——它在 Wayland 下根本不工作。

## 九、代价与局限

1. **依赖不算少。**`xterm` 和 `sh` 是硬依赖，只因为破解结果要在一个终端窗口里看得见；没有 XWayland 的纯 Wayland 会话里，这一环大概率起不来。
2. **一个 GUI 对应一个 agent。**单客户端是安全选择，也意味着多网卡要开多个实例——路径里的 pid 正是为此设计的，但用户得多开窗口。
3. **硬件门槛没变。**网卡必须支持监听模式与数据包注入，笔记本内置网卡经常不支持。
4. **polkit 策略没有例外。**三档（any / inactive / active）全是 `auth_admin`，没有给 `allow_active` 开小门；好处是行为一致，代价是每次都要一次真实认证。
5. **0.8.1 只改构建。**那个版本只修了发布流水线，说明「能装」这件事本身也在持续返工。
6. **破解能力仍是外部的。**审计链路自包含，但最后的破解依赖 `aircrack-ng`；想完全自包含，还差这一步。

## 十、我的判断

Airgorah 最值得学的不是「Rust + GTK4」，而是它承认了一件大多数桌面程序不愿承认的事：**GUI 是攻击面的一部分。**

一旦承认，后面的事情就顺了——能力枚举成封闭集合、按 uid 验对端、参数在特权侧重验、目标必须在自己的观察里、写文件这件脏活留给低权限的一方。这五条没有一条来自「拆分进程」这个动作本身，全都来自拆分之后被迫回答的问题。

这套形状在本地服务里反复出现。我上一篇写的 Yogurt 也是把一个 socket 收到 0600、只读、单账户——**本地进程之间的信任，最后都落在「谁能打开这个文件」和「打开之后你信它多少」两件事上。**

如果要在这套架构上再往前走一步，我会做三件事：

1. **把能力再切细。**现在是「连上就能用全部 16 个请求」；按请求类型发放 capability，可以让「只读的扫描会话」和「能发帧的攻击会话」变成两种授权，而不是一次授权管全部。
2. **给 deauth 单独加一道显式确认。**它是这套接口里唯一会主动影响空口的行为，值得比一次普通点击更重的手续——比如要求输入目标 BSSID 的后六位。
3. **把破解步骤也收进沙箱。**现在它在一个用户终端里跑外部二进制；交给 agent 或一个受限子进程，能让「审计」这条链路的边界完整闭合。

## 项目与资料

- 仓库：[github.com/martin-olivier/airgorah](https://github.com/martin-olivier/airgorah)（MIT）
- 安装 / 使用文档：[wiki: Installation](https://github.com/martin-olivier/airgorah/wiki/Installation)、[wiki: Usage](https://github.com/martin-olivier/airgorah/wiki/Usage)
- 版本记录：[Releases](https://github.com/martin-olivier/airgorah/releases)（0.8.0 拆分进程、0.9.0 加入 PMKID）
- IPC 契约：[`crates/common/src/ipc.rs`](https://github.com/martin-olivier/airgorah/blob/main/crates/common/src/ipc.rs)
- agent 入口与 socket 权限：[`crates/agent/src/main.rs`](https://github.com/martin-olivier/airgorah/blob/main/crates/agent/src/main.rs)
- 请求分发与重验：[`crates/agent/src/server.rs`](https://github.com/martin-olivier/airgorah/blob/main/crates/agent/src/server.rs)、[`validate.rs`](https://github.com/martin-olivier/airgorah/blob/main/crates/agent/src/validate.rs)
- polkit 策略：[`package/.policy`](https://github.com/martin-olivier/airgorah/blob/main/package/.policy)
- 依赖清单：[`crates/common/src/deps.rs`](https://github.com/martin-olivier/airgorah/blob/main/crates/common/src/deps.rs)

数据来源与口径：进程拆分、Wayland、设置与抓包目录迁移来自 0.8.0 的 release changelog；PMKID 与移除 `aircrack-ng` 套件来自 0.9.0 的 changelog；socket 权限、`SO_PEERCRED`、单客户端、清理逻辑、校验规则、16 个请求与 6 种响应、64 MiB 帧上限、5 个必需与 4 个可选工具，均来自本文列出的源码文件；polkit 的 `auth_admin` 三档与 `allow_gui` 来自 `.policy`。文中「为什么这样设计」的判断是我的推断，不是作者的原话——除 `server.rs` 与 `main.rs` 里明确写出的注释外，其余均为我按代码行为反推。
