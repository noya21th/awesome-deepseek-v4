# Comparison tables

Numbers only. No prose. Pick the table you need.

---

## V4 vs closed frontier — benchmarks

Source: [DeepSeek-V4-Pro model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro).

| Benchmark | Opus-4.6 Max | GPT-5.4 xHigh | Gemini-3.1-Pro | **DS-V4-Pro Max** |
|---|---|---|---|---|
| MMLU-Pro | 89.1 | 87.5 | **91.0** | 87.5 |
| SimpleQA-Verified | 46.2 | 45.3 | **75.6** | 57.9 |
| LiveCodeBench | 88.8 | — | 91.7 | **93.5** |
| Codeforces Rating | — | 3168 | 3052 | **3206** |
| SWE-Bench Verified | 80.8 | — | 80.6 | 80.6 |
| GPQA Diamond | 91.3 | 93.0 | **94.3** | 90.1 |
| HumanEval | — | — | — | 90.0 |
| HMMT 2026 Feb | — | — | — | 95.2 |
| Putnam 2025 (formal proof) | — | — | — | **120/120** |
| MRCR @ 1M | — | — | — | 83.5 |

---

## V4 vs closed frontier — pricing ($/Mtok)

| Model | Input | Output | Context | Weights |
|---|---|---|---|---|
| **DeepSeek V4-Flash** | **0.14** | **0.28** | 1M | ✅ MIT |
| **DeepSeek V4-Pro** | **1.74** | **3.48** | 1M | ✅ MIT |
| Claude Haiku 4.6 | ~1 | ~5 | 200K | ❌ |
| Claude Sonnet 4.6 | ~3 | ~15 | 200K | ❌ |
| Claude Opus 4.6 | ~15 | ~75 | 200K | ❌ |
| GPT-5-Nano | ~0.1 | ~0.4 | 400K | ❌ |
| GPT-5.4 | ~2.5 | ~10 | 400K | ❌ |
| Gemini 3.1-Pro | ~2 | ~8 | 1M | ❌ |

*Closed-model prices are public list prices. Verify with each vendor before committing.*

---

## V4 vs open-weight alternatives

| | DeepSeek V4 | Qwen 3.5/3.6 | Llama 4 | Mistral Large 3 | GLM-5.1 |
|---|---|---|---|---|---|
| Flagship total params | 1.6T MoE | ~400B MoE | 70B–405B | ~200B | ~400B |
| License | **MIT** | Apache 2.0 | Llama Community | Mistral license | **MIT** |
| Commercial use | unrestricted | unrestricted | with MAU clause | varies | unrestricted |
| Code strength | 🥇 leads | strong | strong | mid | strong |
| Multilingual | strong | 🥇 leads | strong | strong (EU) | strong |
| Small-tier option | Flash (284B) | 🥇 Qwen 3.6-35B-A3B | Llama-small | Mistral-small | GLM-5-small |
| Ecosystem maturity | emerging | mature | 🥇 mature | mid | mid |

---

## Feature compatibility with existing SDKs

| Feature | via OpenAI SDK | via Anthropic SDK |
|---|---|---|
| Chat / Messages | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| Tool / function calling | ✅ | ✅ |
| JSON output | ✅ | — |
| Thinking mode | ✅ `extra_body` | ✅ |
| Vision input | ❌ (text-only model) | ❌ |
| Audio input | ❌ | ❌ |
| Prompt caching | check API docs | check API docs |

Base URLs:
- OpenAI-compatible: `https://api.deepseek.com/v1`
- Anthropic-compatible: `https://api.deepseek.com/anthropic`

---

## Hardware floor for self-hosting

| Config | What it runs |
|---|---|
| 2× H100 80GB | Not V4 — use Qwen 3.6-35B-A3B instead |
| 8× H100 80GB | V4-Flash (FP8, tight at 1M context) |
| 8× H200 141GB | V4-Flash (FP8, comfortable) |
| 16× H200 | V4-Pro (FP4+FP8) — recommended minimum |
| 2-node cluster | V4-Pro with full 1M context + headroom |

---

## Decision matrix

| You need... | Pick |
|---|---|
| Best code model today | V4-Pro + Thinking |
| Best price/performance for volume | V4-Flash |
| Best world-knowledge retrieval | Gemini 3.1-Pro |
| Air-gapped / regulated deployment | V4 self-hosted (only open-weight option at tier) |
| Multimodal in one model | GPT-5.4 or Gemini 3.1-Pro |
| Smallest self-hostable open model at ~3-Pro quality | Qwen 3.6-35B-A3B |
| Broadest Western open-source ecosystem | Llama 4 |
| Native EU data residency + open weights | Mistral Large 3 |
