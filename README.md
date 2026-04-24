<div align="center">

<img src="./assets/banner.svg" alt="awesome-deepseek-v4 — community multilingual hub for DeepSeek V4" width="900">

# awesome-deepseek-v4

**Practical, multilingual resource hub for [DeepSeek V4](https://huggingface.co/collections/deepseek-ai/deepseek-v4).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Unofficial](https://img.shields.io/badge/status-unofficial-lightgrey.svg)](./DISCLAIMER.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)
[![Languages](https://img.shields.io/badge/languages-7-blue.svg)](#-read-in-your-language)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-DeepSeek--V4-yellow)](https://huggingface.co/collections/deepseek-ai/deepseek-v4)

**🌍 Read in your language**

[English](./README.md) · [简体中文](./i18n/zh-CN/README.md) · [Français](./i18n/fr/README.md) · [العربية](./i18n/ar/README.md) · [日本語](./i18n/ja/README.md) · [Deutsch](./i18n/de/README.md) · [हिन्दी](./i18n/hi/README.md)

</div>

---

## Fact sheet

| | **DeepSeek-V4-Pro** | **DeepSeek-V4-Flash** |
|---|---|---|
| Total parameters | **1.6 T** MoE | **284 B** MoE |
| Activated per token | 49 B | 13 B |
| Experts (routed × active) | 384 × 6 | 256 × 6 |
| Context length | 1,000,000 tokens | 1,000,000 tokens |
| Training tokens | 33 T | 32 T |
| Precision | FP4 (experts) + FP8 | FP8 |
| API price — input | $1.74 / Mtok | $0.14 / Mtok |
| API price — output | $3.48 / Mtok | $0.28 / Mtok |
| Weights license | MIT — commercial use OK | MIT — commercial use OK |
| Reasoning modes | Thinking · Non-Thinking | Thinking · Non-Thinking |

Full spec: [docs/architecture.md](./docs/architecture.md) · Benchmarks: [docs/benchmarks.md](./docs/benchmarks.md) · Pricing: [docs/pricing.md](./docs/pricing.md) · Comparison tables: [docs/comparison.md](./docs/comparison.md).

---

## 60-second quickstart

V4 speaks **both** OpenAI ChatCompletions and Anthropic Messages protocols.

```python
# OpenAI SDK
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/v1")
resp = client.chat.completions.create(
    model="deepseek-v4-pro",   # or "deepseek-v4-flash"
    messages=[{"role": "user", "content": "Prove √2 is irrational."}],
)
print(resp.choices[0].message.content)
```

```python
# Anthropic SDK
from anthropic import Anthropic
client = Anthropic(api_key="sk-...", base_url="https://api.deepseek.com/anthropic")
msg = client.messages.create(
    model="deepseek-v4-pro", max_tokens=1024,
    messages=[{"role": "user", "content": "Prove √2 is irrational."}],
)
print(msg.content[0].text)
```

More: [API quickstart](./getting-started/api-quickstart.md) · [Thinking mode](./examples/python_thinking_mode.py) · [Tool calling](./examples/python_tool_calls.py) · [Raw curl](./examples/curl_basic.sh) · [Local vLLM](./getting-started/local-deployment.md).

---

## What's in this repo

### Getting started
- [**API quickstart**](./getting-started/api-quickstart.md) — OpenAI / Anthropic compatible endpoints.
- [**Local deployment**](./getting-started/local-deployment.md) — vLLM, SGLang, transformers.
- [**Migration from DeepSeek V3**](./getting-started/migration-from-v3.md) — the deprecation deadline and how to swap.
- [**Migration from OpenAI**](./getting-started/migration-from-openai.md) — drop-in, 2-line change.
- [**Migration from Anthropic Claude**](./getting-started/migration-from-claude.md) — drop-in, 2-line change.

### Core reference
- [**Benchmarks**](./docs/benchmarks.md) — headline scores with primary-source citations.
- [**Architecture**](./docs/architecture.md) — CSA+HCA attention, mHC, Muon, On-Policy Distillation.
- [**Pricing**](./docs/pricing.md) — API, managed hosts, self-hosting TCO.
- [**Comparison tables**](./docs/comparison.md) — V4 vs. Claude / GPT / Gemini / Qwen / Llama / Mistral / GLM.

### Doing real work
- [**Recipes**](./docs/recipes.md) — **10 copy-paste patterns** with cost estimates: whole-repo review, long-doc QA, coding agent, batch pipeline, math tutor, LiteLLM fallback, self-host, Aider, Cline, synthetic data.
- [**Prompting guide**](./docs/prompting-guide.md) — temperature, Thinking mode, prompt style.
- [**Fine-tuning**](./docs/fine-tuning.md) — LoRA / QLoRA / full fine-tune recipes and hardware.
- [**FAQ**](./docs/faq.md) — the questions everyone asks.

### Resources
- [Official links](./resources/official-links.md) — canonical URLs.
- [Awesome community](./resources/awesome-community.md) — tools, runtimes, hosts, fine-tunes.
- [Related papers](./resources/papers.md) — V4 paper + upstream lineage.

### Examples
[OpenAI SDK](./examples/python_openai_basic.py) · [Anthropic SDK](./examples/python_anthropic_basic.py) · [Thinking mode](./examples/python_thinking_mode.py) · [Tool calling](./examples/python_tool_calls.py) · [curl](./examples/curl_basic.sh).

### CLI tools ([`tools/`](./tools/))
Single-file Python CLIs. `pip install openai` is the only dependency.
- [**v4-cost-calc**](./tools/v4_cost_calc.py) — compare monthly spend across V4, Claude, GPT, Gemini.
- [**v4-migrate-env**](./tools/v4_migrate_env.py) — scan a codebase for OpenAI/Anthropic config and rewrite to V4.
- [**v4-repo-review**](./tools/v4_repo_review.py) — pack a repo into V4-Pro and get a structured code review.
- [**v4-chat**](./tools/v4_chat.py) — streaming terminal REPL with `/think`, `/model`, `/save`.

### Self-hosting ([`deploy/`](./deploy/))
OpenAI-compatible endpoint on your own hardware.
- [**Docker Compose**](./deploy/docker-compose.yml) — `docker compose up` and you're serving V4.
- [**Kubernetes**](./deploy/k8s/deployment.yaml) — production `Deployment` + `Service` + `ConfigMap`.
- [**systemd**](./deploy/systemd/v4-vllm.service) — bare-metal unit file.

### Prompt library ([`prompts/`](./prompts/))
Battle-tested system prompts. Each declares its recommended model and mode.
- Coding: [code-reviewer](./prompts/coding/code-reviewer.md), [bug-hunter](./prompts/coding/bug-hunter.md), [refactor-planner](./prompts/coding/refactor-planner.md), [test-writer](./prompts/coding/test-writer.md)
- Agents: [coding-agent](./prompts/agents/coding-agent.md), [research-agent](./prompts/agents/research-agent.md), [planner](./prompts/agents/planner.md)
- Writing: [technical-writer](./prompts/writing/technical-writer.md), [translator](./prompts/writing/translator.md)
- Analysis: [contract-reviewer](./prompts/analysis/contract-reviewer.md), [paper-summarizer](./prompts/analysis/paper-summarizer.md)
- Education: [math-tutor](./prompts/education/math-tutor.md)

---

## Contributing

PRs welcome — corrections, translations, new benchmark reproductions, new community tools. See [CONTRIBUTING.md](./CONTRIBUTING.md).

Especially wanted: native-speaker review of Arabic, Hindi, Japanese, German, French pages; benchmark reproductions on your own data; deployment notes for non-Linux, AMD GPUs, Apple Silicon.

---

## License and notices

- Original content of this repository: [MIT](./LICENSE).
- DeepSeek V4 weights and technical report: MIT, © DeepSeek-AI.
- "DeepSeek" is a trademark of DeepSeek-AI. This project is **not affiliated with DeepSeek-AI** — see [DISCLAIMER](./DISCLAIMER.md).

---

## Maintained by

**AI小蓝鲸** — I post about AI and open models in Chinese. Same handle across platforms:

| Platform | Handle |
|---|---|
| 📕 Xiaohongshu (小红书) | [AI小蓝鲸](https://www.xiaohongshu.com/search_result?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8&type=54) |
| 📺 Bilibili (B站) | [AI小蓝鲸](https://search.bilibili.com/upuser?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎵 Douyin (抖音) | [AI小蓝鲸](https://www.douyin.com/search/AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎬 WeChat Channels (视频号) | **AI小蓝鲸** (search inside WeChat) |

PRs from everywhere are welcome regardless of platform.

---

<div align="center">

Star ⭐ if this saves you time. Open an issue or PR if anything is wrong or missing.

</div>
