---
layout: post
title: DeepSeek-V4.1-Flash-1017-Uncensored：不重新训练模型，直接修改权重，让 AI 改变回答行为
date: 2026-11-12 17:50:00 +0800
thumbnail: assets/img/blog/deepseek-v4-weight-editing.jpg
description: 从闭式权重编辑、MoE 架构、能力评测和部署方式出发，分析如何在不重新训练模型的情况下改变大模型的拒绝行为。
tags: [AI, 开源]
categories: [技术随笔, 工程实践]
---

![DeepSeek V4 模型封面图](https://images.openai.com/static-rsc-4/_WiTzs7yqceq0QYZQgnM89A0E2zGkeEltRyd2eE4AN945tPDs0nEtuxxx5zTlaNW3UjQlgIjRUf9N1PN_-cpVZ8tkYJN8iEIQyeF7jYiL7DwXN0Q6VPU2kG3tm1ANZBjgooqHKH8uWyuXSG2gbdP0KSlUF7IMOGDFCg0xLMCB_E?purpose=inline)

_图片来源：[TechSifted](https://techsifted.com/posts/deepseek-v4-review-april-2026/)_

在大语言模型的发展过程中，模型能力与安全对齐一直是两个重要方向。

模型不仅需要具备知识、推理和代码生成能力，还需要通过安全对齐机制控制某些类型的输出。

但是，这种机制也可能产生过度拒绝：一些正常的技术研究、学术分析和安全测试请求，也可能被模型拒绝。

有没有办法不重新训练模型，仅通过修改模型内部参数，就改变它的拒绝回答行为？

MoonMath.ai 发布的 DeepSeek-V4.1-Flash-1017-Uncensored，提供了一个值得研究的案例。

项目地址：[Hugging Face · DeepSeek-V4.1-Flash-1017-Uncensored](https://huggingface.co/MoonMath-ai/DeepSeek-V4.1-Flash-1017-uncensored)

## 一、它是什么？

这是基于 DeepSeek-V4.1-Flash-1017 修改而来的 Uncensored 模型。

它并不是从零训练的新模型，也不是通过 LoRA 或传统 Fine-tuning 微调得到的模型。

根据 MoonMath.ai 的模型说明，它采用了一种叫作 Closed-form Weight Edit（闭式权重编辑）的技术，直接修改模型权重，并将修改结果合并到原生 FP8 Checkpoint 中。

![模型权重原理图](https://images.openai.com/static-rsc-4/oQqLfHCxbuim6wfYsuyebgSVD3xhDyGNVbdU9ZYlytWbHyKz1kUb2vs9fozJspskQ7vjArFZ2KMxXoXvf3iei91UFkJJcwK-TNcZDLLQw99NuGy4W80xiri5e0ee790A5K84Ci6PrM7pmO0MqmmgI5mJq0dQzBOYk3Yt8UQbLb8?purpose=inline)

_图片来源：[楠楠自瑜：什么是模型权重](https://cnutshell.net/tutorial/what-is-model-weights/)_

项目方表示，修改主要针对模型的拒绝回答行为，384 个 Routed Experts 保持不变。

它希望实现的目标是：

- 降低模型的拒绝回答倾向。
- 尽可能保留原模型的知识能力。
- 尽可能保留数学和逻辑推理能力。
- 不需要重新执行完整的模型训练流程。

简单来说，它研究的是如何改变模型的行为，而不是重新创造一个模型。

## 二、核心技术：不训练模型，直接修改权重

传统上，改变模型行为通常有三种方法。

| 方法               | 技术原理                   | 是否需要训练   |
| ------------------ | -------------------------- | -------------- |
| Prompt Engineering | 修改提示词                 | 否             |
| Fine-tuning        | 使用数据更新模型参数       | 是             |
| Weight Editing     | 直接对模型权重进行数学编辑 | 不需要梯度训练 |

MoonMath.ai 采用的是第三种方法。

![权重编辑原理图](https://images.openai.com/static-rsc-4/p8wvC4ASUtpyCt8dF61aw-iHDXsGvca20U02HFYML8oAoC_1Kes8UPMwiMmIP0u46otpSY2tFAJEFcVxm6K-L5SSuZ3ed0FF573U8_doN-iRkxiwtqqVCCadx2Q9MyjIgGMQGpJUYhL4V37ecEAXvePwIUq_MZuxekoX2ccOCow?purpose=inline)

_图片来源：[Yong Cao](https://x.com/YongCaoPlus)_

传统微调的过程大致是：

1. 准备训练数据。
2. 将数据输入模型。
3. 计算预测结果与目标结果之间的损失。
4. 通过反向传播计算梯度。
5. 使用优化器更新模型权重。
6. 重复训练，直到达到预期效果。

Weight Editing 则采用不同的思路。

它通过数学方法计算需要修改的权重变化量，再将变化量应用到原始模型参数中。

可以将其抽象为：

\[ W'=W+\Delta W \]

其中：

- \(W\)：原始模型权重。
- \(\Delta W\)：计算得到的修改量。
- \(W'\)：编辑后的模型权重。

这只是权重编辑的一般性表达，并非该项目公开的完整计算公式。

这种方法的价值在于，不需要通过完整的梯度训练流程改变模型行为。

但它也不是简单删除几个参数就能完成。如何确定编辑方向、影响哪些网络层，以及如何控制能力损失，才是真正的技术难点。

## 三、模型架构：763B 参数的 MoE 模型

![MoE 模型架构示意图](https://images.openai.com/static-rsc-4/luVoesxYBARLAR0Ghsn6pbsed13C3fqwpJyU6RljA4MDxNEcW2zp0vAwQp0kZiwPXJX3idhG3RGD_8ITTWuRzVnPklWB6apkYmO_bwcasqsXXzvetA9ZxxGXqCev_svOL7I9lnjPB2dZlul8C4tBxNO-d1g1ACMbuB6fcoeAFy4?purpose=inline)

_图片来源：[Founders Creative](https://www.founderscreative.org/model-architecture-behind-deepseek-r1/)_

DeepSeek-V4.1-Flash-1017-Uncensored 继承了基础模型的 MoE 架构。

根据 Hugging Face 模型卡：

| 参数           | 信息                     |
| -------------- | ------------------------ |
| 基础模型       | DeepSeek-V4.1-Flash-1017 |
| 总参数量       | 763B                     |
| 权重格式       | FP8 Checkpoint           |
| 架构           | Mixture of Experts       |
| Routed Experts | 384 个                   |
| 文件格式       | Safetensors              |
| 许可证         | MIT                      |
| 修改方式       | Closed-form Weight Edit  |

MoE（Mixture of Experts，混合专家架构）是目前大规模语言模型常用的技术路线。

它的核心思想是：并不是每次处理 Token 都需要调用全部专家，而是通过 Router 路由机制，选择部分专家参与计算。

这样可以在保持较大模型容量的同时，减少每次推理需要执行的计算量。

需要区分两个概念：

- 总参数量：模型拥有的全部参数。
- 激活参数量：处理单个 Token 时实际参与计算的参数。

因此，763B 并不意味着每个 Token 都会激活 763B 参数。

## 四、模型修改效果：能力是否保留？

这是该项目最值得关注的地方。

如果模型修改后拒绝行为减少了，但数学、逻辑和知识能力也大幅下降，那么这种修改就没有太大意义。

MoonMath.ai 对基础模型和修改模型使用相同的评测流程，公布了以下结果。

![大模型评测数据示意图](https://images.openai.com/static-rsc-4/g93aoW19jrX82nMfm15HvwC8p5_ettR2vCDEPfbgO7SQzTF3LNxWrVw4QGo8_dGQypkuE_q_Z68o7Jg7yky2_hT8wKjQl7GJOV5_JaHiU0mChUVOZ97PB1A7pHrvzqVjz9zN-ns6kZ49eVsTE5eDrKq39MUp7OxpQyOotMDxtRo?purpose=inline)

_图片来源：[LG AI Research](https://www.lgresearch.ai/blog/view?seq=618)_

| Benchmark          | 原始模型 | 修改后 |
| ------------------ | -------: | -----: |
| MMLU               |   88.22% | 87.91% |
| MMLU-Pro           |   69.90% | 69.42% |
| MMLU-Pro Reasoning |    85.7% |  84.7% |
| GPQA-Diamond       |    81.3% |  84.8% |
| GSM8K              |    93.5% |  96.0% |

从官方公布的数据来看，修改后的模型在这组测试中的表现与基础模型比较接近。

例如：

- MMLU 下降 0.31 个百分点。
- MMLU-Pro 下降 0.48 个百分点。
- GSM8K 提升 2.5 个百分点。
- GPQA-Diamond 提升 3.5 个百分点。

这些结果来自模型发布方，尚不能视为独立第三方验证。

## 五、最明显的变化：拒绝回答率

这个模型真正的目标并不是提升 Benchmark 分数，而是改变模型的拒绝回答行为。

MoonMath.ai 对模型进行了有害问题和正常问题的测试。

| 指标               | 原始模型 | 修改后 |
| ------------------ | -------: | -----: |
| 有害问题拒绝率     |    87.3% |   1.8% |
| 正常问题过度拒绝率 |     6.3% |     0% |

其中：

- 有害问题测试集：1,410 个问题。
- 正常问题测试集：350 个问题。

![AI 安全与红队测试示意图](https://images.openai.com/static-rsc-4/KNp0yyICwJDvmGm39zDQVrekzCuJaB-2eb_hyJ4hZsHB82CJPY9bQQR-P9nSQDFlURMn3N7Y7SyHgmSZDzNUBHNaTXMr06Du1Cyddj3MBPLzLNOzvr7AtNnMSb7O5uZQ0sm_bnfqf3Nf0AzWU7_bL69ccnh8Y9lOxCwoK0oQHhk?purpose=inline)

_图片来源：[AI Roads](https://airoads.org/electives/module-d/)_

此外，项目还公布了 StrongREJECT 和 HarmBench 测试结果。

| 测试集           | 原始模型 | 修改后 |
| ---------------- | -------: | -----: |
| HarmBench-320    |     0.38 |   0.95 |
| StrongREJECT     |     0.02 |   0.99 |
| Real-CVE Exploit |     0.12 |   1.00 |

这里的分数越高，表示模型对测试请求的配合程度越高，并不是安全性越高，也不是漏洞利用成功率。

这说明修改后的模型在这些测试中大幅降低了拒绝行为。

需要特别强调：模型更愿意回答，不代表答案更正确，也不代表模型更安全。项目方明确要求仅用于获得授权的安全研究，不应公开部署。

## 六、如何部署？

该模型采用原生 FP8 Checkpoint，可以使用支持相应架构的推理框架。

官方推荐 SGLang。

![大模型并行部署架构图](https://images.openai.com/static-rsc-4/dlDduZF4BgtHJS-75zKgF66rI2A2ToTzApE3r-L4171abUVF-cFokQ74wbz5wMH_MC9GesDmXKRGyUU2pLnlA1iphY4BWOL63Lk58PJLrum92zRhJaJjVTLahwohFWNM4mPrRdknwn7pu2JvNhHZ0qVWIMhlXgewhNuOkPTgY1Y?purpose=inline)

_图片来源：[Jarvis Labs](https://jarvislabs.ai/blog/expert-parallelism-mixed-strategies-vllm)_

官方给出的启动示例：

```bash
python -m sglang.launch_server \
  --model-path MoonMath-ai/DeepSeek-V4.1-Flash-1017-uncensored \
  --tp-size 4 \
  --ep-size 4 \
  --trust-remote-code \
  --reasoning-parser deepseek-v41 \
  --tool-call-parser deepseekv41
```

主要参数：

| 参数              | 说明                   |
| ----------------- | ---------------------- |
| model-path        | 模型权重路径           |
| tp-size           | 张量并行规模           |
| ep-size           | 专家并行规模           |
| trust-remote-code | 允许加载模型自定义代码 |
| reasoning-parser  | 推理内容解析器         |
| tool-call-parser  | 工具调用解析器         |

需要注意，TP=4、EP=4 不代表只需要四张 GPU 就一定能够运行。实际硬件需求取决于并行策略、显存、权重分布和推理框架支持情况。

## 七、它有什么研究价值？

我认为这个项目值得关注的地方，不是 Uncensored 这个标签，而是它展示的模型行为编辑思路。

### 1. 模型安全研究

可以对比修改前后的模型行为，研究安全对齐机制如何影响模型回答。

### 2. 模型权重编辑

研究能否通过数学方法直接改变模型的某种行为，而不重新训练整个模型。

### 3. AI 红队测试

在隔离且获得授权的环境中，研究模型对不同攻击提示和安全测试请求的响应。

### 4. 模型能力与行为解耦

模型的知识、推理能力与回答策略并不完全是同一个维度。这个项目提供了一个研究它们之间关系的案例。

## 八、总结

DeepSeek-V4.1-Flash-1017-Uncensored 展示了一种不同于传统 Fine-tuning 的模型修改方式。

它通过 Closed-form Weight Edit 直接编辑模型权重，尝试改变拒绝回答行为，同时尽可能保留基础模型的知识和推理能力。

这个项目真正值得研究的问题是：

> 大模型的行为究竟有多少可以通过权重编辑进行调整？

如果未来能够更精确地编辑模型内部的特定行为，同时保持其他能力不变，那么模型定制可能不再完全依赖大规模训练。

从这个角度看，Weight Editing 值得成为大模型开发者持续关注的一条技术路线。

## 项目与参考资料

- [修改后的模型仓库](https://huggingface.co/MoonMath-ai/DeepSeek-V4.1-Flash-1017-uncensored)
- [基础模型](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)

本文参数和评测数据依据 MoonMath.ai 官方模型卡整理，测试结果未经独立第三方验证。该模型明确限制为获得授权的安全研究用途。

文中架构示意图用于解释通用技术原理，不代表 MoonMath.ai 公开了对应的内部网络结构或权重编辑细节。
