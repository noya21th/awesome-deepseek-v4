# Pricing

Three ways to pay for V4, in order of increasing commitment and decreasing $/token.

*Prices as of 2026-04-24. Closed-model prices are public list prices; check each vendor for the current rate.*

---

## 1. DeepSeek's official API

From the [official V4 launch announcement][api-news]:

| Model | Input | Output | Context |
|---|---|---|---|
| `deepseek-v4-flash` | **$0.14** / Mtok | **$0.28** / Mtok | 1M |
| `deepseek-v4-pro` | **$1.74** / Mtok | **$3.48** / Mtok | 1M |

Endpoint: `https://api.deepseek.com/v1` (OpenAI-compatible) or `https://api.deepseek.com/anthropic` (Anthropic-compatible).

Cache hit / cache miss discounts: referenced in the DeepSeek API docs, check current rates.

**⚠️ Deprecation:** `deepseek-chat` and `deepseek-reasoner` retire on **2026-07-24 15:59 UTC**. Migrate to `deepseek-v4-pro` or `deepseek-v4-flash`. See [migration-from-v3.md](../getting-started/migration-from-v3.md).

---

## 2. Third-party managed hosts

Multiple providers host V4 weights on Western infrastructure, typically with:
- No training on your data
- US/EU data residency
- OpenAI-compatible endpoint
- Slightly higher per-token price vs DeepSeek-direct, usually still undercutting closed frontier

Known hosts (non-exhaustive, verify each):
- Together AI
- Fireworks AI
- DeepInfra
- Parasail
- Atlas Cloud

Pricing varies but typically sits between DeepSeek-direct and closed frontier. Check the provider.

---

## 3. Self-hosting

**Hardware floor** (not official — community estimates):

| Config | Model | Notes |
|---|---|---|
| 8× H200 (141 GB) | V4-Flash FP8 | Comfortable, full 1M context possible with KV cache offload |
| 8× H100 (80 GB) | V4-Flash FP8 | Possible, tight at long context |
| 16× H200 | V4-Pro FP4+FP8 | Recommended minimum for Pro |
| 8× H200 | V4-Pro | Only with aggressive quant and shorter context |

Software: vLLM, SGLang, and TensorRT-LLM have all announced V4 support. See [getting-started/local-deployment.md](../getting-started/local-deployment.md).

**$/token at scale** — self-hosting V4-Pro on rented H200 capacity typically lands around **$0.3–0.8 / Mtok output** at >70% GPU utilization. Cheaper than DeepSeek's own API above ~5B tokens/month of steady load.

---

## Comparison with closed frontier

| Model | Input | Output | Context | Weights available |
|---|---|---|---|---|
| **DeepSeek V4-Flash** | **$0.14** | **$0.28** | 1M | ✅ MIT |
| **DeepSeek V4-Pro** | **$1.74** | **$3.48** | 1M | ✅ MIT |
| Claude Haiku 4.6 | ~$1 | ~$5 | 200K | ❌ |
| Claude Sonnet 4.6 | ~$3 | ~$15 | 200K | ❌ |
| Claude Opus 4.6 | ~$15 | ~$75 | 200K | ❌ |
| GPT-5-Nano | ~$0.1 | ~$0.4 | 400K | ❌ |
| GPT-5.4 | ~$2.5 | ~$10 | 400K | ❌ |
| Gemini 3.1-Pro | ~$2 | ~$8 | 1M | ❌ |

---

## Total cost of ownership — when does each option win?

**Use DeepSeek's API** if:
- You're under 500M tokens/month.
- You don't have MLOps headcount.
- DeepSeek's jurisdiction is acceptable for your data.

**Use a third-party managed host** if:
- You need US/EU data residency but don't want to run GPUs.
- You need higher rate limits or SLAs than DeepSeek's own API provides.
- You want multiple open-weight models on one endpoint.

**Self-host** if:
- You're over ~5B tokens/month of steady load.
- You have compliance requirements that forbid data leaving your network.
- You need to fine-tune and keep the result.
- You need predictable, flat-rate costs vs per-token billing.

---

## The hidden costs (be honest)

Self-hosting isn't free:

- 8× H200 on-demand in a hyperscaler is ~$20–30/hr. Reserved is cheaper; owned is cheaper still.
- Inference stack engineering (vLLM tuning, KV-cache management, autoscaling) is a real ongoing cost.
- Monitoring, canarying, and safety evaluations don't go away because the model is open.

A realistic rule of thumb: for teams under 5 engineers, **the managed API is almost always cheaper all-in** than self-hosting, even at high token volumes, until you're spending ~$100K/month on inference.

---

## Sources

[api-news]: https://api-docs.deepseek.com/news/news260424
