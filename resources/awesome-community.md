# Awesome Community — tools, integrations, and projects using V4

A curated list of community projects. Submit yours via PR — see [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Inference runtimes

- **[vLLM](https://github.com/vllm-project/vllm)** — high-throughput OpenAI-compatible server. Day-one V4 support.
- **[SGLang](https://github.com/sgl-project/sglang)** — fast inference with RadixAttention, strong for agent workflows. Day-one V4 support.
- **[TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)** — NVIDIA's highly optimized runtime. Check release notes for V4 support.
- **[llama.cpp](https://github.com/ggerganov/llama.cpp)** — V4 GGUF quants expected; check recent commits.
- **[Ollama](https://ollama.com/)** — check their library for V4 entries.

## Managed hosts (third-party, non-DeepSeek)

- **[Together AI](https://www.together.ai/)**
- **[Fireworks AI](https://fireworks.ai/)**
- **[DeepInfra](https://deepinfra.com/)**
- **[OpenRouter](https://openrouter.ai/)** — aggregator with V4 access
- **[Parasail](https://parasail.io/)**
- **[Atlas Cloud](https://www.atlascloud.ai/)**

*Availability and pricing vary. Verify each vendor's current V4 offering.*

## SDK / integration layers

- **[LiteLLM](https://github.com/BerriAI/litellm)** — unified SDK that routes to V4, OpenAI, Claude, Gemini, etc. via one API.
- **[OpenAI Python SDK](https://github.com/openai/openai-python)** — works directly against V4's OpenAI-compatible endpoint.
- **[Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)** — works directly against V4's Anthropic-compatible endpoint.
- **[LangChain / LangGraph](https://python.langchain.com/)** — V4 via the OpenAI wrapper.
- **[LlamaIndex](https://www.llamaindex.ai/)** — V4 via the OpenAI-compatible adapter.

## Developer tools that support V4

- **[Aider](https://aider.chat/)** — pair programming in terminal; configure against V4 endpoint.
- **[Cline](https://github.com/cline/cline)** — VS Code agent, OpenAI-compatible, works with V4.
- **[Cursor](https://cursor.com/)** — check current V4 availability; historically adds new models quickly.
- **[Continue](https://continue.dev/)** — OSS VS Code / JetBrains AI assistant, OpenAI-compatible.

## Fine-tuning frameworks

- **[Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl)** — mature fine-tuning toolkit.
- **[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)** — broad model support, Chinese community-maintained.
- **[torchtune](https://github.com/pytorch/torchtune)** — PyTorch-native, expect V4 recipes shortly.
- **[Unsloth](https://github.com/unslothai/unsloth)** — memory-efficient fine-tuning; check V4 support.

## Evaluation

- **[lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)** — standard harness for MMLU-Pro, GPQA, etc.
- **[LiveCodeBench official runner](https://github.com/LiveCodeBench/LiveCodeBench)** — reproducing the 93.5 score.
- **[SWE-Bench](https://github.com/princeton-nlp/SWE-bench)** — reproducing the 80.6 SWE-Verified score.
- **[LiveBench](https://livebench.ai/)** — contamination-resistant benchmark suite.
- **[HELM](https://crfm.stanford.edu/helm/)** — Stanford's holistic eval framework.

## Community writeups (curated)

*Only independently-written analyses — not press-release restatements.*

- [Simon Willison — "DeepSeek V4: almost on the frontier, a fraction of the price"](https://simonwillison.net/2026/Apr/24/deepseek-v4/)
- Hacker News discussion threads — search *DeepSeek V4* on [news.ycombinator.com](https://news.ycombinator.com).

## Submission criteria

We include projects that:
- Actually work with V4 (not just planned support)
- Are open-source or have transparent pricing
- Don't overclaim — ("works with V4" ≠ "has V4 as a default")

We do **not** include:
- Paid courses or closed-source products unless they fill a genuine gap
- "X for V4" wrappers that add no value over the base API
- Link-farm content

---

**To add your project**: open a PR modifying this file. Please include a one-sentence description of what it does and a link to working code or docs.
