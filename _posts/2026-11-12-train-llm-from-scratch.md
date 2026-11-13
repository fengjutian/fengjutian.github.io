---
layout: post
title: Train LLM From Scratch：从零开始训练自己的大语言模型
date: 2026-11-12 18:00:00 +0800
thumbnail: assets/img/blog/train-llm-from-scratch.jpg
description: 使用原生 PyTorch，从 Tokenizer、Transformer 和预训练出发，逐步理解 SFT、DPO、PPO、GRPO 与大语言模型的完整训练流程。
tags: [AI, 开源, 开发者工具]
categories: [技术随笔, 工程实践]
---

![从零训练大语言模型](https://images.openai.com/static-rsc-4/ulnIQPfz-5W7h0GbDzrSTeSTVfcQrBC49yzuCqNNlSB3NrF1InOJ60Z_HbJ-3gqZdkOYqloiTl-EkoU9qpXdu5kH4PQ1s00yMd6eQ1f31m2wKFJCuUeWSU-aDG9UNu1E_oOVMITX4Qdbf4hC_AmkCFUnBInJlZRbMcagt5iRV5Y?purpose=inline)

当我们使用 DeepSeek、ChatGPT 或 Qwen 时，通常只需要调用一个 API，就能获得强大的语言模型能力。

但一个更值得研究的问题是：

**如果不使用现成的大模型框架，能不能从零开始实现 Transformer，并亲自完成一个大语言模型的训练？**

GitHub 上的开源项目 [Train LLM From Scratch](https://github.com/FareedKhan-dev/train-llm-from-scratch)，提供了一条完整的实践路径。

它使用原生 PyTorch，从数据处理、Tokenizer、Transformer 架构，到模型预训练、监督微调、奖励模型和强化学习，逐步展示大语言模型的构建过程。

项目作者没有把核心实现隐藏在 Transformers、TRL 或 PEFT 等高级框架后面，而是尽可能自己实现关键算法，让开发者能够直接阅读模型训练的底层代码。

## 一、这个项目究竟做什么？

简单来说，它是一套从零开始构建和训练大语言模型的教学型工程项目。

传统的模型使用方式通常是：

```text
下载预训练模型
       ↓
加载模型权重
       ↓
输入 Prompt
       ↓
生成文本
```

而这个项目展示的是另一条路线：

```text
原始文本
   ↓
数据清洗与 Tokenization
   ↓
构建 Transformer
   ↓
Pretraining 预训练
   ↓
Base Model 基础模型
   ↓
SFT 监督微调
   ↓
Reward Model 奖励模型
   ↓
DPO / PPO / GRPO
   ↓
模型评估
   ↓
对话模型
```

这意味着开发者不只是学习如何调用一个模型，而是能够理解模型从随机初始化到具备文本生成和指令遵循能力的整个过程。

项目覆盖了现代 LLM 训练中非常重要的几个环节：

- 从文本数据中构建训练语料。
- 使用 BPE 等方法进行 Tokenization。
- 使用 PyTorch 实现 Transformer。
- 使用 Next Token Prediction 进行预训练。
- 使用 SFT 训练指令遵循能力。
- 使用 DPO、PPO、GRPO 等方法进行模型对齐。
- 使用 GSM8K 等数据集评估模型。

## 二、从 Tokenizer 开始：让模型理解文字

![Tokenizer 与文本处理](https://images.openai.com/static-rsc-4/N6Y_viJs7wx9ji20cNPX2Loo2mi6L9_0WYt9fcMUD0GW78ZzMe2AOJe2_Yu3Eb6hajEJ09x0gyOIOoAK5oB6ySomMTBFXuTJp5p9fD6tZQ6sI4J5EiETLuxlNlptpcmmWuIPbclk4IEfTYB87d4xv8DRt071hYr0xFuXO-lgkTY?purpose=inline)

大语言模型并不直接理解人类看到的文字，它真正处理的是数字序列。

例如：

```text
原始文本：

Artificial Intelligence

        ↓

Tokenizer

        ↓

Token IDs：

[若干整数]
```

项目将文本转换成 Token ID，再将 Token 数据保存到磁盘，供训练阶段使用。

它涉及两种重要的 Tokenizer 使用方式：

1. 使用现成的 tiktoken `r50k_base` 词表。
2. 从训练语料中学习自己的 BPE Tokenizer。

其中，BPE（Byte Pair Encoding）是一种常见的子词分词算法。

理解 Tokenizer 非常重要，因为它决定了文本如何被模型表示，也会影响模型的词表规模、Embedding 参数量以及不同语言的 Token 效率。

## 三、使用 PyTorch 从零实现 Transformer

![Transformer 模型架构](https://images.openai.com/static-rsc-4/-kxmOlChEtPVGTPj0wBgnoXztKRGv4_qH61PnKARimOOy6bR-TfJZZ7V0_FfPyQJhgBhleueRMEFk61eN-4ydcBUr0BpJqz-Ivbgk7dgxhTVNHP_WkQoLo1R-PAtDodwtiOwSSc-yJc6w9-atcAMdaX1QlTXf8S7AdZ8aXPQBwc?purpose=inline)

Transformer 是当前主流大语言模型的核心架构。

项目没有直接调用 Transformers 库来构建模型，而是把 Transformer 拆成多个独立组件。

主要包括：

| 模块                 | 作用                     |
| -------------------- | ------------------------ |
| Token Embedding      | 将 Token ID 转换为向量   |
| Positional Embedding | 表示 Token 位置信息      |
| Self-Attention       | 建立上下文关联           |
| Multi-Head Attention | 从多个特征空间理解上下文 |
| MLP                  | 进行特征变换             |
| LayerNorm            | 稳定网络训练             |
| Residual Connection  | 改善深层网络的信息传递   |
| LM Head              | 预测下一个 Token         |

一个简化的 Transformer Block 可以表示为：

```python
class Block(nn.Module):
    def __init__(self, n_head, n_embed, context_length):
        super().__init__()

        self.ln1 = nn.LayerNorm(n_embed)
        self.attn = MultiHeadAttention(
            n_head, n_embed, context_length
        )

        self.ln2 = nn.LayerNorm(n_embed)
        self.mlp = MLP(n_embed)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x
```

代码体现了 Transformer 的核心结构：

- Attention 负责处理不同 Token 之间的关联。
- MLP 负责进行特征变换。
- Residual Connection 保留并传递原始信息。

通过堆叠多个 Transformer Block，就可以构建完整的语言模型。

项目将这些组件组织在 `src/models/` 目录中，方便开发者逐个研究和修改。

## 四、不止 GPT-2：支持现代大语言模型架构

项目还实现了现代 Transformer 架构中的多个重要技术。

| 技术     | 作用                       |
| -------- | -------------------------- |
| RoPE     | 旋转位置编码               |
| RMSNorm  | 更简洁的归一化方式         |
| SwiGLU   | 改进前馈网络结构           |
| GQA      | 降低 KV Cache 存储开销     |
| MLA      | 压缩注意力机制中的潜在表示 |
| MoE      | 使用多个专家网络稀疏计算   |
| KV Cache | 避免重复计算历史 Token     |

这部分很值得研究。

因为现代大语言模型并不是简单地增加 Transformer 层数和参数量，而是在注意力机制、归一化、前馈网络、缓存和专家路由等方面不断优化。

项目同时提供经典 Transformer 和现代架构的实现，开发者可以在相同的训练环境下研究不同设计的差异。

## 五、Pretraining：让模型学会预测下一个 Token

![模型预训练](https://images.openai.com/static-rsc-4/CzgWpyeB56_SGAxfasSaNbyE_shZcZb35ELOUbpHLZz2TDyWhhMGe5IQEMEHFUtsRjFhioGEw9mCgnt5qDCoE7oeoSFbtuKHTcfQC3CjPyFjsAVxdquh0GcomUApoZvtJz5l4NcwUSPQTyiNMcO3OeKVvFPyLFxTHtyoH67qs-8?purpose=inline)

预训练是大语言模型建立语言能力的基础。

它的核心目标是：

**根据已经出现的 Token，预测下一个 Token。**

例如：

```text
输入：

人工智能正在改变

目标：

世界
```

模型通过预测结果与真实 Token 之间的差异计算 Cross Entropy Loss，再通过反向传播更新模型参数。

项目支持不同规模的模型配置，例如：

| 模型配置               | 参数规模        |
| ---------------------- | --------------- |
| Tiny                   | 数十万参数      |
| 13M                    | 约 1,314 万参数 |
| 77M                    | 约 7,703 万参数 |
| Post-training 默认配置 | 约 4.06 亿参数  |

需要注意，这些是项目配置中的模型规模，并不代表它们已经具备商业级大模型能力。

项目还支持：

- 单 GPU 训练。
- 多 GPU DistributedDataParallel。
- BF16 混合精度。
- 梯度累积。
- 梯度检查点。
- Checkpoint 保存和恢复。
- Cosine Learning Rate Schedule。
- Muon 优化器。

对于开发者而言，这些功能不仅能帮助理解模型训练，也能学习实际训练工程如何组织。

## 六、普通笔记本也能训练吗？

这是项目比较有吸引力的地方。

项目专门提供了 Laptop Track，让开发者使用普通 CPU 笔记本训练一个极小的 Transformer。

例如，项目展示了一个约 636K 参数的经典架构模型，以及一个约 369K 参数的现代架构模型。

作者提供的示例中，前者在笔记本 CPU 上训练约 8 分钟，后者约 5 分钟。

训练结束后，模型已经可以生成简单的故事文本。

当然，这不是说普通笔记本能够训练出 DeepSeek 或 ChatGPT，而是让开发者能够在低成本环境中亲自观察模型训练的全过程。

这对于学习 Transformer 非常有价值。

## 七、Post-Training：从基础模型到对话模型

预训练结束后，模型获得了基本的语言生成能力，但不一定能够很好地理解和执行用户指令。

因此，需要进行后训练。

项目覆盖了多个重要算法。

### 1. SFT：监督微调

使用问题和答案组成的指令数据集训练模型。

例如：

```text
User:
13 + 29 等于多少？

Assistant:
42
```

项目使用 Assistant-only Loss Mask，让训练损失主要作用于 Assistant 的回答部分。

### 2. Reward Model：奖励模型

通过人类偏好数据，让模型学习判断不同回答的质量。

项目使用 Bradley-Terry Loss 训练奖励模型。

### 3. DPO：直接偏好优化

DPO 不需要执行完整的传统强化学习流程，而是直接使用优质答案和劣质答案之间的偏好关系优化模型。

项目还支持 ORPO、KTO、IPO 和 SimPO 等方法。

### 4. PPO：近端策略优化

PPO 通过奖励信号优化模型生成策略。

项目实现了 GAE 优势估计、Clipped Policy Loss 等关键机制。

### 5. GRPO：组相对策略优化

![GRPO 后训练](https://images.openai.com/static-rsc-4/6265erMQbXPcJord-IgppLaZQnKvSsMQFePaRG6YAdaRJm3YrB1RJN7mGlXGc4PSOqq_LIr1UB24Yo3u7q6phSB7Qw95X2mu4mVl80UWILy5T2jwefl4gcB_NT7OuZxeFcdxMu8OfZiOPJIw_YWY-dhtcTkEQi2VyfMZWx5NtLQ?purpose=inline)

GRPO 是 DeepSeek-R1 技术路线中受到广泛关注的方法。

它让模型针对同一个问题生成多个答案，根据组内奖励表现计算相对优势，再优化模型策略。

与 PPO 相比，GRPO 不需要单独训练 Value Network。

项目还提供 Dr. GRPO、DAPO 和 GSPO 等相关实现。

## 八、模型评估与文本生成

训练模型不能只看 Loss，还需要评估它是否真正获得了目标能力。

项目提供 GSM8K 数学问题评估流程，可以比较 Base、SFT、DPO、PPO 和 GRPO 等不同阶段的模型表现。

此外，项目还实现了多种文本生成能力：

- Temperature 采样。
- Top-K 采样。
- Top-P 采样。
- Min-P 采样。
- Speculative Decoding。
- Int8 权重量化。

这些功能让项目不仅包含训练过程，也包含模型推理和生成阶段。

## 九、工程结构：一套完整的 LLM 实验平台

项目的目录结构比较清晰：

```text
train-llm-from-scratch/
│
├── src/
│   ├── models/
│   ├── tokenizer/
│   ├── optim/
│   ├── inference/
│   └── post_training/
│
├── config/
├── configs/
├── data_loader/
├── scripts/
├── tests/
├── docs/
├── ui/
└── pyproject.toml
```

主要模块：

| 目录          | 职责                       |
| ------------- | -------------------------- |
| models        | Transformer 和现代模型架构 |
| tokenizer     | Tokenizer 实现             |
| optim         | 优化器和学习率调度         |
| inference     | 模型推理与文本生成         |
| post_training | SFT、DPO、PPO、GRPO        |
| data_loader   | 数据集加载                 |
| scripts       | 训练与执行入口             |
| configs       | 训练配置                   |
| tests         | 自动化测试                 |
| docs          | 技术文档                   |
| ui            | Streamlit 可视化控制台     |

项目还提供 Streamlit 控制面板，可以通过界面查看和执行不同训练阶段。

这让它不仅仅是一个 Transformer 教学代码示例，也逐渐成为一套完整的实验工程。

## 十、如何运行第一个模型？

首先克隆项目：

```bash
git clone https://github.com/FareedKhan-dev/train-llm-from-scratch.git

cd train-llm-from-scratch
```

安装依赖：

```bash
pip install -e .
```

准备最小训练数据：

```bash
python scripts/prepare_tiny_data.py
```

使用 CPU 或 GPU 训练 Tiny 模型：

```bash
python scripts/train_transformer.py \
  --preset tiny \
  --arch modern
```

训练完成后生成文本：

```bash
python scripts/generate_text.py \
  --model_path models/tiny.pt
```

如果想使用可视化控制台：

```bash
pip install -e ".[ui]"

streamlit run ui/app.py
```

建议第一次先运行 Tiny 配置，理解数据、模型、Loss 和生成之间的关系，再逐步尝试 13M、77M 等更大的配置。

## 十一、这个项目适合什么人？

我认为它主要适合四类开发者：

### 1. 想理解大模型原理的开发者

不满足于只会调用 API，希望理解 Tokenizer、Attention、Transformer 和模型训练过程。

### 2. 想进入 AI 模型研发领域的工程师

希望从应用开发进一步深入模型架构、预训练和后训练。

### 3. 研究模型训练算法的人

希望直接阅读 DPO、PPO、GRPO、LoRA 等算法的 PyTorch 实现。

### 4. 想自己训练小模型的人

希望从一个极小的 Transformer 开始，逐步建立自己的数据处理、训练和推理流程。

## 十二、总结

Train LLM From Scratch 最有价值的地方，不是让开发者快速获得一个可以商业部署的大模型，而是把大语言模型的训练过程拆解成可以理解、修改和运行的代码。

从原始文本到 Tokenizer，从 Transformer 到预训练，再到 SFT、DPO、PPO 和 GRPO，项目覆盖了大语言模型研发中的重要技术环节。

对于希望深入 AI 领域的开发者来说，它提供了一条非常直观的学习路径：

**先理解模型如何构建，再理解模型如何训练，最后理解模型如何通过后训练获得更符合人类需求的行为。**

AI 开发不应该永远停留在调用模型 API。

理解模型内部的工作机制，才能真正从模型使用者走向模型研发者。

## 项目与参考资料

- [项目仓库](https://github.com/FareedKhan-dev/train-llm-from-scratch)
- [官方文档](https://fareedkhan-dev.github.io/train-llm-from-scratch/)
- 许可证：MIT

本文根据项目公开仓库及官方文档整理。训练时间、模型规模和硬件需求会随配置、数据和运行环境变化。文中配图为技术主题示意图，不代表该仓库的实际运行截图。
