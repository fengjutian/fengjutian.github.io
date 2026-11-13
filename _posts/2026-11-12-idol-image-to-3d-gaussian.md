---
layout: post
title: Idol：一张图片生成百万级 3D 高斯模型，AI 正在重新定义三维建模
date: 2026-11-12 12:00:00 +0800
thumbnail: assets/img/blog/idol-image-to-3d-gaussian.jpg
description: Idol 通过单张图片推断三维结构，最多生成 1,048,576 个 3D Gaussian，为三维资产生成与实时交互提供了新的工作流。
tags: [AI, 开源]
categories: [技术随笔]
toc:
  sidebar: right
  collapse: auto
og_image: /assets/img/blog/idol-image-to-3d-gaussian.jpg
---

如果只给 AI 一张普通照片，它能不能自动理解物体的三维结构，并生成一个可以自由旋转、从不同角度观察的 3D 模型？

过去，这通常需要专业建模软件、多角度拍摄，甚至需要摄影测量和复杂的三维重建流程。

现在，Sperid Labs 开源了一个名为 **Idol** 的 AI 模型，它尝试让这个过程变得简单：

**一张图片输入，最多生成 1,048,576 个 3D Gaussian。**

它不只是将图片转换成一个简单的三维轮廓，而是通过 AI 推断物体的空间结构，生成可以通过 Gaussian Splatting 技术渲染的三维资产。

项目地址：

- Hugging Face：https://huggingface.co/speridlabs/idol
- GitHub：https://github.com/speridlabs/idol-sdk
- 官方研究页面：https://speridlabs.com/research/idol
- 在线 Demo：https://huggingface.co/spaces/speridlabs/idol

## 一、从一张图片到一个三维世界

先看一个实际案例。

下面是一张 AI 生成的黄色机器人鸭子图片。

![Idol 输入图片：黄色机器人鸭子]({{ '/assets/img/blog/idol-image-to-3d-gaussian/fig-01.jpg' | relative_url }})

这是一张普通的二维图片，只有一个观察角度。

Idol 的任务是根据这张图片，推断物体的三维结构，并生成一个可以从不同方向观察的 3D Gaussian 模型。

这意味着，即使原始图片没有展示鸭子的背面，模型也会尝试推断背部、尾部等不可见区域。

另一个案例是复古薄荷绿色踏板摩托车：

![Idol 输入图片：复古薄荷绿色踏板摩托车]({{ '/assets/img/blog/idol-image-to-3d-gaussian/iris-scooter_s1_s42.jpg' | relative_url }}){: loading="lazy" decoding="async"}

这些案例展示了 Idol 的基本能力：输入可以来自现实照片，也可以来自 AI 生成图片或三维渲染图。

需要注意，未拍摄到的区域是模型根据学习到的先验知识进行推断，并不代表真实扫描还原。

## 二、核心技术：3D Gaussian Splatting

要理解 Idol，首先需要了解它采用的三维表示技术。

传统三维建模通常使用 Mesh（网格）描述物体。

一个 Mesh 由顶点、边和三角形面构成，通过几何结构建立物体表面，再配合纹理和材质完成渲染。

而 3D Gaussian Splatting 采用了另一种思路。

它使用大量分布在三维空间中的高斯基元来表达物体。

![3D Gaussian Splatting 三维高斯点云可视化]({{ '/assets/img/blog/idol-image-to-3d-gaussian/teaser.jpg' | relative_url }}){: loading="lazy" decoding="async"}

每个 Gaussian 都包含一组属性：

| 属性                | 作用             |
| ------------------- | ---------------- |
| Position            | 三维空间位置     |
| Scale               | 空间尺寸         |
| Rotation            | 旋转方向         |
| Opacity             | 透明度           |
| Color               | 颜色             |
| Spherical Harmonics | 视角相关颜色表达 |

可以把它理解为：使用大量具有空间位置、尺寸、方向和颜色的微小三维元素，共同组成一个物体。

这些高斯基元经过投影和混合渲染后，就能够形成具有立体感的画面。

与传统 Mesh 相比，Gaussian Splatting 特别适合表达复杂的视觉细节，并支持实时视角渲染。

## 三、Idol 的技术架构

Idol 并不是简单地使用一个图像生成模型直接输出三维点云，而是由多个模型组件共同完成。

整体处理过程可以分为四个阶段。

### 1. 图片预处理

首先对输入图片进行预处理。

Idol 使用 BiRefNet 进行背景移除，将物体主体从原始背景中分离出来。

随后进行图片裁剪和构图调整。

项目提供两种输入模式：

- `real`：针对现实世界拍摄的照片。
- `synthetic`：针对 AI 生成图片和三维渲染图片。

两种模式主要区别在于裁剪时为物体预留的空间。

### 2. 图像特征提取

Idol 使用 DINOv3 ViT-H+ 提取图像视觉特征。

同时使用 FLUX.2 VAE 对输入图片进行特征编码。

这些信息为后续三维生成提供图像条件。

### 3. 三维结构生成

这是整个系统最核心的部分。

Idol 使用 DiT（Diffusion Transformer）作为去噪网络，通过生成过程推断物体的三维表示。

随后通过两个解码器完成三维结构输出：

- Octree Decoder：解码空间组织结构。
- Gaussian Decoder：将特征转换为 Gaussian 参数。

最终生成包含空间位置、尺度、旋转、颜色和透明度等属性的三维高斯基元。

### 4. 导出三维资产

生成完成后，Idol 将结果保存为标准 3DGS PLY 文件。

主要输出包括：

| 文件           | 用途               |
| -------------- | ------------------ |
| `.ply`         | 三维高斯模型       |
| `_input.png`   | 预处理后的输入图片 |
| `_camera.json` | 预测的输入相机参数 |

PLY 文件可以交给支持 Gaussian Splatting 的查看器进行渲染。

## 四、模型参数与生成能力

Idol 支持不同规模的 Gaussian 输出。

![Idol 不同 Gaussian 数量的细节等级展示]({{ '/assets/img/blog/idol-image-to-3d-gaussian/fig-04.jpg' | relative_url }}){: loading="lazy" decoding="async"}

根据官方公开资料：

| 参数               |      数值 |
| ------------------ | --------: |
| 核心 DiT 参数量    |    370.6M |
| Octree Decoder     |     50.8M |
| Gaussian Decoder   |    237.3M |
| 完整推理组件参数量 |  约 1.80B |
| 默认 Gaussian 数量 |   262,144 |
| 最大 Gaussian 数量 | 1,048,576 |
| 最小 Gaussian 数量 |    32,768 |
| 峰值显存           | 约 7.2 GB |

这里需要区分核心生成模型和完整推理流水线：1.80B 包含图像编码器、背景移除模型和生成组件，并不代表 DiT 本身有 1.80B 参数。

官方公布的不同 GPU 推理性能：

| GPU      |   显存 | 推理时间 |
| -------- | -----: | -------: |
| B300     | 269 GB |   3.4 秒 |
| B200     | 179 GB |   3.6 秒 |
| H200     | 140 GB |   6.6 秒 |
| H100     |  80 GB |   6.7 秒 |
| RTX 5090 |  32 GB |  14.1 秒 |
| RTX 4090 |  24 GB |  19.1 秒 |
| RTX 3080 |  10 GB |  46.2 秒 |

测试条件为 50 个采样步骤、262,144 个 Gaussian，统计 8 张图片的中位推理时间。

这说明 Idol 不仅面向大型 GPU 集群，也具备在消费级 NVIDIA 显卡上运行的能力。

## 五、如何运行 Idol？

项目提供 Python SDK，开发者可以直接将其集成到自己的应用中。

首先克隆项目：

```bash
git clone https://github.com/speridlabs/idol-sdk.git

cd idol-sdk

pip install -e .
```

运行环境：

- Python 3.10+
- PyTorch 2.5+
- NVIDIA GPU
- CUDA 环境

首次运行前，需要在 Hugging Face 接受 DINOv3 和 FLUX.2-dev（仅 VAE）的模型使用条款。

然后登录：

```bash
hf auth login
```

处理现实照片：

```bash
python -m idol.sample \
  --image photo.jpg \
  --mode real
```

处理 AI 生成图片：

```bash
python -m idol.sample \
  --image object.png \
  --mode synthetic
```

Python API：

```python
from idol import IdolPipeline

pipeline = IdolPipeline.from_pretrained(
    "speridlabs/idol"
)

output = pipeline(
    "photo.jpg",
    mode="real",
    seed=42,
    num_gaussians=1048576
)

output.gaussian.save_ply("photo.ply")
```

对于希望进一步开发的团队，可以将 Python SDK 封装为独立的 HTTP 服务，供 Web、桌面端和移动端调用。

## 六、与其他 Image-to-3D 模型比较

目前 Image-to-3D 已经成为生成式 AI 的重要方向。

几个值得关注的项目：

| 项目       | 主要特点                 |
| ---------- | ------------------------ |
| Idol       | 单张图片生成 3D Gaussian |
| TripoSplat | 单图生成高斯三维表示     |
| TRELLIS    | 支持多种三维结构表示     |
| LGM        | 大规模高斯模型生成       |

官方在相同 H100 测试环境下公布了对比结果：

| 模型       |  PSNR |  SSIM | LPIPS | 新视角 CLIP |
| ---------- | ----: | ----: | ----: | ----------: |
| Idol       | 12.25 | 0.726 | 0.213 |       0.885 |
| TripoSplat | 11.76 | 0.712 | 0.225 |       0.868 |
| TRELLIS    | 11.89 | 0.716 | 0.235 |       0.868 |
| LGM        | 12.46 | 0.722 | 0.237 |       0.784 |

其中 LPIPS 越低越好，其他指标通常越高越好。

Idol 在这组测试中的新视角 CLIP、LPIPS 等指标表现较好，但不同模型的输出规模和测试设置并不完全一致，不能简单认为它在所有场景都优于其他模型。

## 七、Idol 可以用来做什么？

它的价值不仅在于生成一个三维模型，还在于降低了三维内容生产的门槛。

**1. 电商三维展示**

将商品照片转换为三维资产，实现旋转、缩放和多角度展示。

**2. 游戏开发**

根据概念图生成游戏道具、物品和视觉素材，加快前期资产制作。

**3. 数字孪生**

将现实物体转换为三维视觉资产，用于产品展示和空间可视化。

**4. AI 三维设计**

用户提供图片和自然语言指令，AI 生成三维资产，再通过交互工具调整模型。

**5. Web 3D 创作**

将图片转三维能力集成到浏览器，让普通用户也可以创建三维交互内容。

## 八、进一步探索：AI 生成与粒子动画结合

如果把 Idol 与 Three.js、WebGPU 等实时渲染技术结合，还可以探索更有意思的应用。

例如，用户上传一张建筑图片，AI 自动生成三维高斯模型，然后在浏览器中实现：

- 三维模型旋转与观察。
- 粒子扫描。
- 模型解体。
- 粒子聚合。
- 形态重组。
- AI 自然语言控制。

整体流程：

```text
        图片输入
           │
           ▼
      Idol AI 模型
           │
           ▼
      3D Gaussian
           │
           ▼
       PLY 数据解析
           │
           ▼
      粒子渲染引擎
           │
      ┌────┼────┐
      ▼    ▼    ▼
     扫描  解体  重组
           │
           ▼
      交互式 3D 场景
```

这里有一个重要的技术区别：

Gaussian Splatting 并不是传统粒子系统，也不是普通 Mesh。

如果要实现粒子动画，需要读取 PLY 中的高斯位置、颜色、透明度、尺度和旋转属性，再映射到自己的粒子系统中。

也可以直接对 Gaussian 属性进行动态变换，保留其原有的渲染方式。

这为 AI 三维生成与实时视觉创作之间的结合提供了新的可能性。

## 九、总结

Idol 展示了一种值得关注的 AI 三维生成方向：

**从单张图片出发，通过生成模型推断三维结构，再利用 Gaussian Splatting 实现实时三维展示。**

它并不能完全替代传统三维建模，也不能保证准确还原图片中不可见的真实结构。

但它降低了创建三维视觉资产的门槛，让图片成为三维内容生产的一个入口。

对于开发者来说，值得关注的不只是如何运行 Idol，更是如何将它集成到自己的产品中。

当 AI 负责生成三维资产，实时渲染引擎负责展示，交互系统负责编辑，三维创作工具就可能从专业建模软件扩展为人人都能使用的 AI 创作平台。

**一张图片，可能就是一个三维世界的开始。**

---

**项目与参考资料**

- Idol 模型：https://huggingface.co/speridlabs/idol
- 官方研究与案例：https://speridlabs.com/research/idol
- SDK 源码：https://github.com/speridlabs/idol-sdk
- 3D Gaussian Splatting 原始研究：https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
