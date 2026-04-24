# Benchmarks

Every number on this page traces to a primary source — the V4-Pro model card, the technical report (*DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence*), or the official API announcement. If a number here doesn't match its source, open an issue.

*All numbers are for the Preview V4 models as of 2026-04-24.*

---

## Headline table — V4-Pro Max (Thinking mode) vs. frontier

Source: [DeepSeek-V4-Pro model card][hf-v4-pro].

| Benchmark | What it measures | Opus-4.6 Max | GPT-5.4 xHigh | Gemini-3.1-Pro | **DS-V4-Pro Max** |
|---|---|---|---|---|---|
| **LiveCodeBench** | Post-cutoff code generation | 88.8 | — | 91.7 | **93.5** 🥇 |
| **Codeforces Rating** | Competitive-programming Elo | — | 3168 | 3052 | **3206** 🥇 |
| **SWE-Bench Verified** | Real GitHub issue fixes | 80.8 | — | 80.6 | 80.6 |
| **HumanEval** | Python code correctness | — | — | — | 90.0 |
| MMLU-Pro | Broad academic knowledge | 89.1 | 87.5 | **91.0** | 87.5 |
| GPQA Diamond | Graduate-level reasoning | 91.3 | 93.0 | **94.3** | 90.1 |
| SimpleQA-Verified | Short-answer factuality | 46.2 | 45.3 | **75.6** | 57.9 |
| IMOAnswerBench | Olympiad math | — | — | — | 89.8 |
| HMMT 2026 Feb | US math contest | — | — | — | 95.2 |
| Putnam 2025 (formal proof) | Math olympiad with proof | — | — | — | **120/120** 🥇 |
| MRCR @ 1M | Long-context retrieval | — | — | — | 83.5 |
| CorpusQA @ 1M | Long-context QA | — | — | — | 62.0 |

### How to read this honestly

- **V4 leads on code:** LiveCodeBench 93.5 and Codeforces 3206 are state-of-the-art among publicly-accessible models. Codeforces 3206 ≈ top-30 human competitive programmer.
- **V4 leads on formal math:** Putnam-2025 formal proof is 120/120 — a perfect score.
- **V4 is competitive on reasoning:** GPQA Diamond 90.1 is ~3–4 points behind the frontier, not a different league.
- **V4 trails on world knowledge:** SimpleQA-Verified 57.9 vs Gemini's 75.6. Gemini's retrieval stack remains ahead; for pure fact retrieval, budget for this gap.
- **V4 trails Claude by 0.2 on SWE-Bench Verified** (80.6 vs 80.8). Effectively a tie for real-world coding tasks.

---

## Efficiency benchmarks

From the V4 technical report[^2]:

> **DeepSeek-V4-Pro** attains only **27 % of single-token FLOPs** and **10 % of KV cache size** relative to DeepSeek-V3.2 at 1M-token context.
>
> **DeepSeek-V4-Flash** achieves **10 % of single-token FLOPs** and **7 % of KV cache size** under the same conditions.

These efficiency gains come from the **Hybrid Attention Architecture** (Compressed Sparse Attention + Heavily Compressed Attention) and **token-wise compression** — see [architecture.md](./architecture.md).

---

## Architecture spec

Source: V4-Pro model card + technical report.

| Spec | V4-Pro | V4-Flash |
|---|---|---|
| Total parameters | **1.6 T** | **284 B** |
| Activated parameters / token | 49 B | 13 B |
| Layers | 61 | 43 |
| Hidden dim | 7,168 | 4,096 |
| Routed experts | 384 | 256 |
| Active experts / token | 6 | 6 |
| Head dim | 512 | 512 |
| Attention | Hybrid CSA + HCA, Sparse MQA, SWA | Hybrid CSA + HCA |
| Precision | FP4 (MoE experts) + FP8 (rest) | FP8 |
| Context length | 1,000,000 tokens | 1,000,000 tokens |
| Pre-training tokens | 33 T | 32 T |
| Pre-training batch size | 94.4 M tokens | 75.5 M tokens |
| Weights size on disk | ~865 GB | ~160 GB |

---

## Sampling recommendations

- Default: `temperature = 1.0, top_p = 1.0`
- Think-Max mode: context window ≥ **384K tokens**
- Chat template: use the `encoding_dsv4` helper included in the model repo (a generic chat template will break Thinking mode parsing)

---

## Where V4's own report says it's weak (honesty)

Direct from the tech report:

- **Trails Gemini 3.1-Pro on knowledge-heavy benchmarks.**
- **Long-context retrieval degrades above 128K tokens** — the 1M context is usable, but retrieval accuracy drops as you go deeper.
- **Text-only.** No multimodal support in the preview release.
- **Architecture is "relatively complex"** — the authors flag future simplification as planned work.

If any of these is a deal-breaker for you, the frontier closed models (or a retrieval-augmented pipeline on top of V4) will serve you better.

---

## Reproducing these numbers

DeepSeek has not yet published the exact evaluation harness used for the model card numbers. Standard setups should reproduce within ±1.5 points:

- **MMLU-Pro, GPQA**: [lm-eval-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- **LiveCodeBench**: [LiveCodeBench official runner](https://github.com/LiveCodeBench/LiveCodeBench)
- **SWE-Bench Verified**: [SWE-Bench official](https://github.com/princeton-nlp/SWE-bench)
- **Codeforces Rating**: run submissions against past contests, compute Elo using standard CF formula

Community reproductions land in [benchmarks-community.md](./benchmarks-community.md) (TBA). Please PR your runs.

---

## Sources

[^1]: [DeepSeek-V4-Pro model card][hf-v4-pro]
[^2]: [DeepSeek-V4 technical report (PDF)][tech-report] — *Towards Highly Efficient Million-Token Context Intelligence*
[^3]: [Official DeepSeek V4 API announcement (2026-04-24)][api-news]

[hf-v4-pro]: https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
[tech-report]: https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf
[api-news]: https://api-docs.deepseek.com/news/news260424
