# 常见问题

HN / Reddit / X 上每个 V4 帖子都会冒出来的问题，一次性答完。

---

## 基础

### DeepSeek V4 是什么？
DeepSeek-AI 于 2026-04-24 发布的两个开源 MoE 语言模型：**V4-Pro**（1.6T / 49B 激活）和 **V4-Flash**（284B / 13B 激活）。都是 1M tokens 上下文、Thinking/Non-Thinking 双模式、MIT 协议。

### V4 真的开源吗？
**权重：是，MIT。**可下载、运行、微调、商用，无任何附加条件。
**训练代码和数据：不是。**DeepSeek 给了详细技术报告但未公开完整预训练流水线。这和 Llama、Qwen 等"开源权重"模型是一样的模式——**"开源权重" ≠ OSI 意义上的"开源"**。

### 协议到底允许什么？
MIT。意味着：商用 ✅、修改 ✅、再分发 ✅、私用 ✅。再分发时必须包含 MIT 声明。没有叠加任何 AUP（可接受使用政策）。

### V4-Pro 和 V4-Flash 有什么区别？

| | V4-Pro | V4-Flash |
|---|---|---|
| 总参数 | 1.6T | 284B |
| 激活参数 | 49B | 13B |
| 质量档位 | ≈ GPT-5.4 / Claude Opus 4.6 | ≈ Claude Haiku / GPT-5-Mini |
| API 价格（输入/输出） | $1.74 / $3.48 | $0.14 / $0.28 |
| 自托管门槛 | 16× H200 | 8× H200 |

成本敏感场景从 Flash 开始，质量敏感场景用 Pro。

---

## 对比

### V4 和 Claude 4.6 / GPT-5.4 / Gemini 3.1-Pro 怎么比？
短版本：**代码 SOTA、推理持平、世界知识有差距。**详见 [vs Claude/GPT/Gemini 对比](./comparison.md)。

### V4 和 Qwen 3.5、Llama 4、GLM-5 怎么比？
都是强势开源权重选项。V4 在代码和长上下文上领先；Llama 4 生态最成熟；Qwen 多语种最强；GLM-5 在排行榜顶部中体积最轻。

### V4 做代码真的比 Opus 好？
公开基准（LiveCodeBench 93.5 vs 88.8、Codeforces 3206）是的。SWE-Bench Verified 80.6 vs 80.8 —— 打平。**在你自己的代码库上应该同时评测。**公开基准只是代理指标。

---

## 实操

### V4 能用我现有的 OpenAI / Claude 代码吗？
能。V4 **同时**兼容 OpenAI ChatCompletions 和 Anthropic Messages 协议。改 `base_url` 和模型名，大部分 SDK 代码不动即可切换。

### 有免费额度吗？
DeepSeek 平台历来给新账号免费额度，具体看 platform.deepseek.com 当前条款。也可以通过第三方托管（OpenRouter、Together 等）的免费层白嫖。

### 速率限制怎么样？
Preview 期间官方没公布正式速率限制。社区反馈 Flash 宽松、Pro 偏紧。生产负载建议联系 DeepSeek 销售或用有 SLA 保障的第三方托管。

### V4 支持多模态（图片/音频/视频）吗？
**不支持——Preview 阶段仅文本。**技术报告把多模态列为未来工作。

### V4 支持函数调用/工具使用吗？
支持，OpenAI 兼容 `tools` 格式 + Anthropic 兼容 `tools` 格式（各自端点）。见 [examples/python_tool_calls.py](../../../examples/python_tool_calls.py)。

### Thinking 模式是什么？
V4 的双模式设置：要么产生可见的推理轨迹（`thinking: enabled`），要么直接作答（`thinking: disabled`）。同一个模型，同一个价格，不同输出风格。难推理/代码开，简单对话关。

### 上下文窗口到底多长？
**1,000,000 tokens。**但技术报告指出 **128K 以上检索准确率下降** —— 你可以塞 1M，但深处的精确检索变得不可靠。RAG 型任务加检索层胜于裸长上下文。

---

## 自托管

### V4 能在笔记本上跑吗？
不能。V4-Flash FP8 就 ~160GB 权重。最低现实配置是 8× H100 80GB。

### 单卡 H100 能跑 V4 吗？
不能。极度量化的 Flash 短上下文或许可以，但质量是未知数。单卡用户建议走托管 API。

### vLLM / SGLang / TensorRT-LLM 支持吗？
vLLM、SGLang 日零支持。TensorRT-LLM 预计会支持，查看 NVIDIA 发布说明。详见 [local-deployment.md](../../../getting-started/local-deployment.md)。

### V4 真能在华为昇腾上跑？
HN 的报道是：**能。**DeepSeek 训练和部署 V4 使用华为芯片，生产栈无 CUDA 依赖。这是 AI 供应链去耦合的重要信号。具体操作查华为 MindIE 文档。

---

## 隐私 / 治理

### DeepSeek 会用我的 prompt 训练吗？
官方 API 上：看 platform.deepseek.com 当前隐私政策。第三方托管上（Together、Fireworks 等）：选不训练的供应商。自托管：数据不出你的网络。

### V4 有审查吗？
与所有中国背景实验室训练的模型一样，V4 在某些话题上（特别是涉及中国政治敏感话题）有护栏，这点与西方模型不同。对绝大多数商用场景无关。如果对你有影响：
- **API 上**：过滤发生在服务端，不可改
- **权重上**：社区有 "abliteration" 等去过滤技术，但非官方支持，自负其责

### V4 用于合规场景（医疗/法律/金融）安全吗？
- **法律上**：MIT 协议允许
- **合规上**：看你的监管机构。自托管 V4 到 VPC 内是和 HIPAA / SOC2 / GDPR 兼容的——和任何自托管模型一样
- **API 上**：合规状况依赖于 DeepSeek 自己的认证情况

### 能嵌到卖的产品里吗？
能。MIT 无商用限制。最佳实践是在关于页/文档里标注模型出处（DeepSeek）。

---

## 本仓库本身

### 这个仓库官方吗？
**不。**这是社区维护的资源。DeepSeek-AI 没有创作或背书。见 [DISCLAIMER.md](../../../DISCLAIMER.md)。

### 为什么做这个而不是直接链到 DeepSeek 官方文档？
三点：
1. **翻译** —— 7 种语言一等公民，而不是机翻补丁
2. **对比** —— DeepSeek 不能可信地对比自己和 Claude/GPT，中立社区仓库可以
3. **迁移** —— 迁移指南从"你现在在用别家 API"的角度写，DeepSeek 官方不会这么写

### 怎么贡献？
见 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。特别希望：母语审校、基准复现、非常规硬件部署、社区工具提交。

### 怎么跟进更新？
Watch 这个仓库，或关注 CHANGELOG.md。本仓库承诺随 V4 更新同步维护。
