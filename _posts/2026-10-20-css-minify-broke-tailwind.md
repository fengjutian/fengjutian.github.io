---
layout: post
title: 一次 CSS 压缩把整站布局打散
date: 2026-10-20 15:30:00 +0800
description: 预编译 Tailwind 的间距 token 不能二次压缩：var(--spacing) 被拆成 var( -  - spacing) 的排查过程。
tags: [开发者工具, 开源]
categories: [技术随笔, 工程实践]
---

这个站的样式是**预编译产物**——主题 gem 直接带一份编译好的 Tailwind CSS，站点本身不跑 Tailwind 构建，也不允许引入 Tailwind 构建管线。

于是就有了一条纪律：产物出来之后，**不能再被二次压缩**。

## 症状

某次调整构建配置之后，整站布局塌了：导航栏不固定、间距全部归零、卡片贴在一起。控制台没有报错，HTML 也没有异常。

第一反应是 Tailwind 版本问题，第二反应是缓存。第三反应才是去打开编译产物看一眼。

## 真凶

打开构建出来的 `assets/css/main.css`，看到这样的片段：

<!-- prettier-ignore -->
```css
.fixed-top {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 1030;
}

.p-2 {
  padding: calc(var( -  - spacing) * 2);
}
```

`var(--spacing)` 被拆成了 `var( -  - spacing)`。

原因在 CSS 规范里：CSS 自定义属性里，`--` 后面紧跟一个标识符时属于**自定义属性名**。而变量替换发生在*值*的位置，压缩器把 `var(--spacing)` 的值 `0.25rem` 替换进去时，如果替换结果本身以 `--` 开头（比如 `calc(--spacing)` 或 `--spacing` 形式的表达式），规范要求用 `var()` 再包一层做替换保护。

于是压缩器写出了 `var( -  - spacing)`：它想表达的是「把 `--spacing` 这个变量的值取出来」，但在压缩后的字面量里，两个减号被拆开，语义从「变量名」退化成「两个负号运算符」。

结果就是：**所有使用 `var(--spacing)` 的间距工具类全部失效**。而 Tailwind v4 的间距刻度是整套工具类的基础，于是整站一起塌。

## 处理方式

不是去修压缩器，而是**关掉二次压缩**：

```yaml
jekyll-minifier:
  # CSS already minified upstream (Tailwind build ships tailwind.css).
  # Re-minifying via cssminify2 mangles Tailwind v4 spacing tokens inside calc(),
  # turning `var(--spacing)` into the invalid `var( -  - spacing)` and breaking every
  # spacing/positioning utility. Disable it.
  compress_css: false
  compress_javascript: false
```

理由很简单：CSS 已经由上游压缩过一次，站点再压一遍没有任何收益，只有风险。JS 的压缩则交给 `jekyll-terser` 单独处理。

## 排查这类问题的通用顺序

1. **先看产物，再看源码**。构建出来的 CSS 里长什么样，比任何配置推断都可靠。
2. **看「突然消失」的那一类声明**。这里消失的是 `padding` / `margin` / `gap`，指向间距刻度，而不是指向某个组件。
3. **怀疑压缩器时要怀疑「二次处理」**。任何「已经优化过一遍的产物」都不该被默认再优化一遍。

后来我把这条写进了配置注释里。配置项会被人改动，但注释会留在原地——下一次谁再动这个开关，至少知道为什么当初关掉了它。
