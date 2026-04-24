# Architecture Deep-Dive

A plain-English walkthrough of what's new inside V4, with citations back to the technical report[^1].

The V4 paper frames the work around one thesis: **million-token context isn't a capability problem anymore — it's an efficiency problem.** The architecture changes are engineered against that thesis.

---

## Six things that are new in V4

1. **Hybrid Attention (CSA + HCA)** — replaces full attention with a mix of two compressed variants.
2. **Manifold-Constrained Hyper-Connections (mHC)** — new residual connection scheme.
3. **Muon optimizer** — replaces AdamW for most parameters.
4. **FP4 weights for routed experts** — halves memory vs FP8, negligible quality loss.
5. **On-Policy Distillation (OPD)** — post-training recipe using specialist domain experts.
6. **Anticipatory Routing + SwiGLU Clamping** — stability fixes for training at this scale.

---

## 1. Hybrid Attention: CSA + HCA

The single largest architectural change in V4 is in the attention mechanism.

**Compressed Sparse Attention (CSA)** — most layers use this. For each query, only a sparse subset of keys is attended to, and those keys are themselves compressed. The result: FLOPs grow sub-linearly with sequence length, not quadratically.

**Heavily Compressed Attention (HCA)** — a smaller number of layers use this more aggressive compression scheme for the highest-efficiency long-context pathway.

Combined with **Sparse Multi-Query Attention (MQA)** and **Sliding Window Attention (SWA)** in select layers, this is what gets V4-Pro down to 27% of V3.2's single-token FLOPs at 1M context.

**Why you should care:** this is what makes the million-token context actually usable. On V3.2, a 1M-context request was theoretically supported but economically unattractive. On V4, it's a first-class default.

---

## 2. Manifold-Constrained Hyper-Connections (mHC)

In transformer blocks, the residual connection (`x + f(x)`) is what keeps gradients flowing at depth. For very deep MoE models (61 layers in V4-Pro), standard residuals can cause representations to drift along pathological directions.

mHC **constrains the residual update to lie on a learned manifold**, reducing this drift. The practical effect: training stability at 61 layers × 384 experts.

The paper positions this as a necessary condition for training at V4-Pro's scale without loss spikes.

---

## 3. Muon optimizer (replacing AdamW)

V4 uses [Muon](https://arxiv.org/abs/2502.16982) for most parameters, with AdamW retained for embeddings and a few other stability-sensitive components.

Muon is a second-order-ish optimizer that approximates orthogonalization of gradient updates via Newton-Schulz iterations. It trades a small per-step compute increase for a large reduction in the **number of steps needed to converge** — particularly at scale.

**Practical impact on the community:** V4 is the largest production model to date using Muon as the primary optimizer. Its success is a significant data point for the pre-training community.

---

## 4. FP4 for routed experts, FP8 for everything else

**V4-Pro's weights are mixed precision by design, not by quantization.**

- **MoE expert parameters**: FP4 (E2M1, 4 bits per weight)
- **Attention, embeddings, shared experts, layer norm**: FP8

Because each token only activates 6 of 384 routed experts, the FP4 savings compound: the active computation is almost entirely through FP4-stored experts. The non-expert pathway (attention, etc.) stays at FP8 where precision matters more.

**Disk size:** ~865 GB for V4-Pro (vs roughly 1.5 TB for an equivalent FP8-only MoE).
**Inference:** Modern GPUs (H100/H200/B200) have FP8 paths; FP4 matmul is supported natively on B200 and emulated on H200. Some runtimes dequantize to FP8 on the fly.

---

## 5. On-Policy Distillation (OPD)

The V4 post-training recipe uses **specialist domain experts** (smaller models fine-tuned on individual domains like code, math, writing) to generate training data for the main V4 model.

Critically, this is **on-policy**: the specialist generates completions for prompts that the main model itself found difficult, so the distillation signal is tailored to the student's weaknesses.

The paper credits OPD with much of V4-Pro's domain-specific lead on code (LiveCodeBench 93.5) and formal math (Putnam 120/120).

---

## 6. Stability: Anticipatory Routing + SwiGLU Clamping

At 384 experts, **router collapse** (all tokens going to a few experts) is a real training hazard.

- **Anticipatory Routing** decouples the main backbone updates from the router updates, so a bad routing step doesn't cascade into main-weight instability.
- **SwiGLU Clamping** bounds the linear and gate components of the SwiGLU activation to prevent the occasional blow-up that shows up at FP8 at scale.

Neither is glamorous. Both are load-bearing.

---

## What V4 does NOT change from V3

For context on the continuity:

- **MoE gating mechanism**: still top-K routing with auxiliary load-balancing loss (refined, not replaced).
- **Tokenizer family**: updated but same general BPE approach.
- **Base recipe for alignment** (RLHF + preference data): similar shape, with OPD added on top.

V4 is an efficiency + scaling paper, not a wholesale rethink of the post-training stack.

---

## Open questions the paper leaves for future work

Directly from the technical report:

1. **Long-context retrieval degrades past 128K tokens.** The model can ingest 1M, but finding a specific fact deep in the context becomes unreliable. V4 is a big step, not a solved problem.
2. **Architecture is "relatively complex."** The authors flag simplification as planned work for V4.5 or V5.
3. **Multimodal extension.** The preview is text-only. Vision/audio integration is future work.

---

## TL;DR for engineers

If you only remember three things:

1. **1M context is cheap now** — 27% of V3.2's FLOPs and 10% of its KV cache at full length. Budget your infra accordingly.
2. **The code/math lead is structural**, not just more parameters — hybrid attention + OPD specialists are what produce the Codeforces-3206 / Putnam-120 results.
3. **FP4 + FP8 mixed is the new normal for open-weight frontier models**, and V4 is the cleanest public example. Your inference stack needs FP4 support to run Pro at native precision.

---

[^1]: *DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence*. [PDF](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf).
