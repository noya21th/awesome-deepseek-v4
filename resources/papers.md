# Related Papers

Primary and upstream papers that matter for understanding V4.

---

## The V4 paper itself

- **DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence** (2026)
  - [PDF](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf)
  - Introduces: Hybrid CSA+HCA attention, mHC residuals, FP4/FP8 mixed precision, OPD post-training, Anticipatory Routing.

---

## Upstream DeepSeek papers V4 builds on

- **DeepSeek-V3** (2024) — establishes the base MoE architecture, GRPO-style post-training, auxiliary-loss-free load balancing.
  - [Paper](https://arxiv.org/abs/2412.19437)
- **DeepSeek-V2** (2024) — introduces Multi-Head Latent Attention (MLA). V4 evolves from this attention lineage.
  - [Paper](https://arxiv.org/abs/2405.04434)
- **DeepSeek-R1** (2025) — RL-based reasoning training that prefigures V4's Thinking mode.
  - [Paper](https://arxiv.org/abs/2501.12948)
- **DeepSeekMoE** (2024) — the MoE expert-specialization approach that scales to 384 experts in V4-Pro.
  - [Paper](https://arxiv.org/abs/2401.06066)

---

## Background on V4's architectural innovations

### Muon optimizer
- [Muon: An Optimizer for Hidden Layers in Neural Networks](https://arxiv.org/abs/2502.16982) — Keller Jordan et al. V4 uses Muon for most parameters; largest model to date to do so in a production run.

### Sparse / compressed attention lineage
- [Longformer: The Long-Document Transformer](https://arxiv.org/abs/2004.05150) — sliding window attention (SWA), which V4 incorporates.
- [BigBird: Transformers for Longer Sequences](https://arxiv.org/abs/2007.14062) — sparse attention precedents.
- [StreamingLLM](https://arxiv.org/abs/2309.17453) — attention sinks, relevant for long-context inference.

### MoE scaling
- [Switch Transformer](https://arxiv.org/abs/2101.03961) — foundational MoE paper.
- [Mixtral of Experts](https://arxiv.org/abs/2401.04088) — Mistral's 8×7B MoE; the open-source MoE baseline.

### Low-precision training
- [FP8-LM: Training FP8 Large Language Models](https://arxiv.org/abs/2310.18313) — methodology that underlies V4's FP8 base precision.

---

## Papers we recommend reading right after the V4 paper

If you want to understand the V4 paper deeply, these three are the best companions:

1. **DeepSeek-V3** (for the MoE + post-training foundation V4 inherits).
2. **DeepSeek-V2 / MLA** (for the attention lineage CSA/HCA evolve from).
3. **Muon** (for the optimizer that replaces AdamW).

---

## Ecosystem papers worth knowing

- [LiveCodeBench](https://arxiv.org/abs/2403.07974) — the contamination-resistant code benchmark V4 tops.
- [SWE-Bench](https://arxiv.org/abs/2310.06770) — the real-GitHub-issues benchmark where V4 ties Claude at 80.6.
- [MMLU-Pro](https://arxiv.org/abs/2406.01574) — the upgraded MMLU V4 scores 87.5 on.
- [GPQA](https://arxiv.org/abs/2311.12022) — graduate-level reasoning benchmark.

---

## Contributing to this list

Open a PR with papers that genuinely help someone understand V4 or reproduce its results. Keep it to primary research — blog posts go in [`awesome-community.md`](./awesome-community.md).
