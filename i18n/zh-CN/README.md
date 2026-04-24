<div align="center">

<img src="../../assets/banner.svg" alt="awesome-deepseek-v4" width="900">

# awesome-deepseek-v4

**[DeepSeek V4](https://huggingface.co/collections/deepseek-ai/deepseek-v4) 实用多语种资源中心。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![非官方](https://img.shields.io/badge/status-unofficial-lightgrey.svg)](../../DISCLAIMER.md)
[![欢迎 PR](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../CONTRIBUTING.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-DeepSeek--V4-yellow)](https://huggingface.co/collections/deepseek-ai/deepseek-v4)

**🌍 选择你的语言**

[English](../../README.md) · [**简体中文**](./README.md) · [Français](../fr/README.md) · [العربية](../ar/README.md) · [日本語](../ja/README.md) · [Deutsch](../de/README.md) · [हिन्दी](../hi/README.md)

</div>

---

## 参数对照表

| | **DeepSeek-V4-Pro** | **DeepSeek-V4-Flash** |
|---|---|---|
| 总参数 | **1.6 T** MoE | **284 B** MoE |
| 激活参数 | 49 B | 13 B |
| 专家数（路由 × 激活） | 384 × 6 | 256 × 6 |
| 上下文长度 | 1,000,000 tokens | 1,000,000 tokens |
| 训练 tokens | 33 T | 32 T |
| 精度 | FP4（专家）+ FP8 | FP8 |
| API 输入价 | $1.74 / 百万 tokens | $0.14 / 百万 tokens |
| API 输出价 | $3.48 / 百万 tokens | $0.28 / 百万 tokens |
| 协议 | MIT · 商用无限制 | MIT · 商用无限制 |
| 推理模式 | Thinking · Non-Thinking | Thinking · Non-Thinking |

完整规格：[docs/architecture.md](../../docs/architecture.md) · 基准：[docs/benchmarks.md](../../docs/benchmarks.md) · 定价：[docs/pricing.md](../../docs/pricing.md) · 对比表：[docs/comparison.md](../../docs/comparison.md)。

---

## 60 秒上手

V4 **同时**兼容 OpenAI ChatCompletions 和 Anthropic Messages 协议。

```python
# OpenAI SDK
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/v1")
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "证明 √2 是无理数。"}],
)
print(resp.choices[0].message.content)
```

```python
# Anthropic SDK
from anthropic import Anthropic
client = Anthropic(api_key="sk-...", base_url="https://api.deepseek.com/anthropic")
msg = client.messages.create(
    model="deepseek-v4-pro", max_tokens=1024,
    messages=[{"role": "user", "content": "证明 √2 是无理数。"}],
)
print(msg.content[0].text)
```

更多：[API 上手](../../getting-started/api-quickstart.md) · [Thinking 模式](../../examples/python_thinking_mode.py) · [工具调用](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh) · [本地 vLLM 部署](../../getting-started/local-deployment.md)。

---

## 仓库内容

### 上手与迁移
- [**API 快速上手**](../../getting-started/api-quickstart.md)
- [**本地部署**](../../getting-started/local-deployment.md) — vLLM / SGLang / transformers
- [**从 DeepSeek V3 迁移**](../../getting-started/migration-from-v3.md) — 下线死线和替换方案
- [**从 OpenAI 迁移**](../../getting-started/migration-from-openai.md) — 改两行
- [**从 Anthropic Claude 迁移**](../../getting-started/migration-from-claude.md) — 改两行

### 核心参考
- [**基准数据**](../../docs/benchmarks.md)
- [**架构深析**](../../docs/architecture.md) — CSA+HCA / mHC / Muon / On-Policy Distillation
- [**定价**](../../docs/pricing.md)
- [**对比表**](../../docs/comparison.md) — V4 vs Claude / GPT / Gemini / Qwen / Llama / Mistral / GLM

### 真正能用的东西
- [**配方集**](./docs/recipes.md) 🇨🇳 — **10 个可复制粘贴模式** + 成本估算：整仓库审查、长文档 QA、Agent、批量流水线、数学导师、LiteLLM 多厂商容灾、自托管、Aider、Cline、合成数据。
- [**提示词指南**](../../docs/prompting-guide.md) ⚠️ 英文
- [**微调**](../../docs/fine-tuning.md) ⚠️ 英文 — LoRA / QLoRA / 全量微调
- [**FAQ**](./docs/faq.md) 🇨🇳

> *目前只翻译了"配方集"与"FAQ"这两篇最高价值的详细文档。其他详细页面仍为英文 —— 欢迎通过 PR 贡献翻译（见 [CONTRIBUTING](../../CONTRIBUTING.md)）。*

### 资源
- [官方链接](../../resources/official-links.md)
- [Awesome 社区](../../resources/awesome-community.md)
- [相关论文](../../resources/papers.md)

### 示例
[OpenAI SDK](../../examples/python_openai_basic.py) · [Anthropic SDK](../../examples/python_anthropic_basic.py) · [Thinking 模式](../../examples/python_thinking_mode.py) · [工具调用](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh)

### CLI 工具 ([`tools/`](../../tools/))
单文件 Python CLI，仅依赖 `openai`。
- [**v4-cost-calc**](../../tools/v4_cost_calc.py) —— 估算月账单，V4 vs Claude / GPT / Gemini 对比
- [**v4-migrate-env**](../../tools/v4_migrate_env.py) —— 扫项目改 OpenAI/Anthropic 配置为 V4
- [**v4-repo-review**](../../tools/v4_repo_review.py) —— 整仓库打包交 V4-Pro，出结构化 Code Review
- [**v4-chat**](../../tools/v4_chat.py) —— 终端流式 REPL，支持 `/think`、`/model`、`/save`

### 自托管 ([`deploy/`](../../deploy/))
在自己硬件上跑起 OpenAI 兼容端点。
- [**Docker Compose**](../../deploy/docker-compose.yml) —— 一条 `docker compose up`
- [**Kubernetes**](../../deploy/k8s/deployment.yaml) —— 生产级 Deployment + Service + ConfigMap
- [**systemd**](../../deploy/systemd/v4-vllm.service) —— 裸机单元文件

### Prompt 库 ([`prompts/`](../../prompts/))
经过工程化的 system prompts，每个都标明推荐模型与模式。
- 代码：[code-reviewer](../../prompts/coding/code-reviewer.md) · [bug-hunter](../../prompts/coding/bug-hunter.md) · [refactor-planner](../../prompts/coding/refactor-planner.md) · [test-writer](../../prompts/coding/test-writer.md)
- Agent：[coding-agent](../../prompts/agents/coding-agent.md) · [research-agent](../../prompts/agents/research-agent.md) · [planner](../../prompts/agents/planner.md)
- 写作：[technical-writer](../../prompts/writing/technical-writer.md) · [translator](../../prompts/writing/translator.md)
- 分析：[contract-reviewer](../../prompts/analysis/contract-reviewer.md) · [paper-summarizer](../../prompts/analysis/paper-summarizer.md)
- 教育：[math-tutor](../../prompts/education/math-tutor.md)

---

## 贡献

欢迎 PR —— 纠错、翻译、新基准复现、新社区工具。见 [CONTRIBUTING.md](../../CONTRIBUTING.md)。

---

## 协议与声明

- 仓库原创内容：[MIT](../../LICENSE)。
- DeepSeek V4 权重和技术报告：MIT，© DeepSeek-AI。
- "DeepSeek" 是 DeepSeek-AI 的商标。本项目**与 DeepSeek-AI 无关联** —— 见 [DISCLAIMER](../../DISCLAIMER.md)。

---

## 作者

**AI小蓝鲸** —— 在中文平台分享 AI 与开源模型内容。四个平台同名：

| 平台 | 账号 |
|---|---|
| 📕 小红书 | [AI小蓝鲸](https://www.xiaohongshu.com/search_result?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8&type=54) |
| 📺 B 站 | [AI小蓝鲸](https://search.bilibili.com/upuser?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎵 抖音 | [AI小蓝鲸](https://www.douyin.com/search/AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎬 视频号 | **AI小蓝鲸**（微信内搜索） |

欢迎所有平台来的 Issue / PR。

---

<div align="center">

帮到你就点 ⭐。发现错误或缺失欢迎 Issue / PR。

</div>
