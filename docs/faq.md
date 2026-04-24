# FAQ

Answers to the questions that show up in every V4 thread on Hacker News, Reddit, and Twitter.

---

## The basics

### What is DeepSeek V4?
Two open-weight MoE language models released by DeepSeek-AI on 2026-04-24: **V4-Pro** (1.6T / 49B activated) and **V4-Flash** (284B / 13B activated). Both have 1M token context, dual Thinking/Non-Thinking modes, and MIT licensing.

### Is V4 really open source?
**Weights: yes, MIT.** You can download, run, fine-tune, and commercialize them with no strings.
**Training code and data: no.** DeepSeek publishes a detailed technical report but not their full pre-training pipeline. This is the same pattern as Llama, Qwen, and every other "open-weight" model — "open-weight" is not the same as "open-source" in the OSI sense.

### What does the license actually allow?
MIT. That means: commercial use ✅, modification ✅, redistribution ✅, private use ✅. You must include the MIT notice in redistributions. There is no acceptable-use policy layered on top.

### What's the difference between V4-Pro and V4-Flash?

| | V4-Pro | V4-Flash |
|---|---|---|
| Total params | 1.6T | 284B |
| Active params | 49B | 13B |
| Quality tier | ≈ GPT-5.4 / Claude Opus 4.6 | ≈ Claude Haiku / GPT-5-Mini |
| API price (in/out $/Mtok) | $1.74 / $3.48 | $0.14 / $0.28 |
| Self-host floor | 16× H200 | 8× H200 |

Start with Flash for cost-sensitive workloads, Pro for quality-sensitive ones.

---

## Comparisons

### How does V4 compare to Claude 4.6 / GPT-5.4 / Gemini 3.1-Pro?
Short version: **wins on code, competitive on reasoning, trails on world knowledge.** Full detail in [vs-closed-source.md](./vs-closed-source.md).

### How does V4 compare to Qwen 3.5, Llama 4, GLM-5?
All four are strong open-weight options. V4 leads on code and long-context; Llama 4 has the broadest deployment ecosystem; Qwen is strongest on multilingual; GLM-5 is the lightest at the top of the leaderboard. Full detail in [vs-open-source.md](./vs-open-source.md).

### Is V4 really better than Opus for coding?
On published benchmarks (LiveCodeBench 93.5 vs 88.8, Codeforces 3206), yes. On SWE-Bench Verified, 80.6 vs 80.8 — a tie. **On your real codebase, you should benchmark both.** Public benchmarks are proxies.

---

## Practical / operational

### Can I use V4 through my existing OpenAI or Claude code?
Yes. V4 exposes **both** OpenAI ChatCompletions and Anthropic Messages protocols. Change the `base_url` and the model name — most SDK code works unchanged. See [migration-from-openai.md](../getting-started/migration-from-openai.md) / [migration-from-claude.md](../getting-started/migration-from-claude.md).

### Is there a free tier?
DeepSeek's platform historically has had free-tier credits for new accounts; check platform.deepseek.com for current terms. You can also run V4 for free via a managed host's free tier (e.g., OpenRouter, Together) where available.

### What's the API rate limit?
Not officially published at preview launch. Community-reported limits are generous for Flash, tighter for Pro. Production workloads should talk to DeepSeek sales or use a third-party managed host with guaranteed SLAs.

### Does V4 support multimodal (images, audio, video)?
**No — text-only at the preview release.** The technical report lists multimodal as future work.

### Does V4 support function calling / tool use?
Yes, OpenAI-compatible `tools` schema and Anthropic-compatible `tools` on the respective endpoints. See [examples/python_tool_calls.py](../examples/python_tool_calls.py).

### What's Thinking mode?
A dual-mode setting where V4 either produces a visible reasoning trace (`thinking: enabled`) or answers directly (`thinking: disabled`). Same model, same price, different output. Enable it for hard reasoning / code; disable for simple chat.

### How long is the context window really?
**1,000,000 tokens.** However the technical report notes that **long-context retrieval degrades above 128K tokens** — you can stuff 1M in, but finding a specific fact deep in the context becomes less reliable. For RAG-style workloads, chunking + retrieval on top of V4 still beats naive full-context.

---

## Self-hosting

### Can I run V4 on my laptop?
No. Even V4-Flash at FP8 is ~160 GB of weights. The minimum realistic self-host config is 8× H100 80GB for Flash.

### Can I run V4 on a single H100?
No. Possibly a heavily-quantized Flash at short context, but quality at that point is speculative. Use a managed API for single-GPU users.

### Is vLLM / SGLang / TensorRT-LLM supported?
vLLM and SGLang announced day-one support. TensorRT-LLM is expected; check NVIDIA's release notes. See [local-deployment.md](../getting-started/local-deployment.md).

### Does V4 actually run on Huawei Ascend?
Per HN reporting, **yes** — DeepSeek reportedly trained and serves V4 on Huawei chips without CUDA dependency on their production stack. This is a significant data point for AI supply-chain decoupling. If you want to run V4 on Ascend, check Huawei's MindIE documentation.

---

## Privacy / governance

### Does DeepSeek train on my prompts?
On their direct API, check the current privacy policy at platform.deepseek.com. On a third-party managed host (Together, Fireworks, etc.), you choose a host with a no-training policy. Self-hosted: your data never leaves your network.

### Is V4 censored?
Like every model trained by a Chinese-based lab, V4 has some topical guardrails that differ from Western models (particularly around PRC-sensitive political topics). For most commercial workloads this is irrelevant. If it isn't for your use case:
- **On the API**: filters happen server-side, not editable.
- **On the weights**: community un-filtering / "abliteration" is possible but not officially endorsed. Do your own diligence.

### Is V4 safe to use for regulated workloads (healthcare, legal, finance)?
- **Legally**: MIT license permits it.
- **Compliance**: depends on your regulator. Self-hosting V4 inside a VPC is compatible with HIPAA / SOC2 / GDPR — same as any other self-hosted model.
- **The API**: compliance profile depends on DeepSeek's own certifications. Check their docs.

### Can I use V4 in products I sell to customers?
Yes. MIT license is unrestricted commercial use. You should still credit DeepSeek in your about page or docs where model provenance matters.

---

## The repo itself

### Is this repo official?
**No.** This is a community-maintained resource. DeepSeek-AI did not author or endorse it. See [DISCLAIMER.md](../DISCLAIMER.md).

### Why build this instead of just linking to DeepSeek's docs?
Three reasons:
1. **Translation** — English is only one of seven languages here, and the translations are first-class, not machine-fallback.
2. **Comparison** — DeepSeek can't credibly compare itself to Claude and GPT. A neutral community repo can.
3. **Migration** — the migration guides are written from the perspective of someone using the *other* vendor today.

### How can I contribute?
See [CONTRIBUTING.md](../CONTRIBUTING.md). Especially needed: native-speaker review of non-English pages, benchmark reproductions, deployment notes for unusual hardware, and community tool submissions.

### How do I stay updated?
Watch this repo, or follow the CHANGELOG.md. This repo commits to tracking V4 updates as they ship.
