# Fine-tuning V4

How to adapt V4 to your domain, and when it's worth doing vs. just prompting.

---

## Should you fine-tune at all?

**Ask these three questions first:**

1. Can the task be solved with a well-engineered system prompt + few-shot examples? **Try prompting first.** V4 is strong out of the box.
2. Do you have ≥ 1,000 high-quality domain examples? **Below that, RAG + prompting usually beats fine-tuning.**
3. Do you need **proprietary knowledge embedded in the model** (not retrievable at inference)? That's the main fine-tune-is-worth-it case.

If your answer to (3) is yes and you have the data, keep reading.

---

## Fine-tuning options, ranked by cost

### 1. LoRA on V4-Flash (recommended starting point)
- **Hardware**: 4–8× H100 80GB or 4× H200.
- **Cost**: ~$200–2,000 per training run depending on dataset size.
- **Time**: hours to a day.
- **Good for**: domain adaptation, style transfer, task specialization.

### 2. QLoRA on V4-Flash (cheapest)
- **Hardware**: 2–4× H100, or 1× H200 with heavy offload.
- **Cost**: ~$50–500 per run.
- **Quality trade-off**: small but real. Use if budget > quality.

### 3. LoRA on V4-Pro
- **Hardware**: 16+× H200 or a multi-node cluster.
- **Cost**: thousands of dollars per run.
- **When**: Flash-LoRA isn't hitting your quality bar and you're willing to pay for the top tier.

### 4. Full fine-tune of V4-Pro
- **Hardware**: a real cluster — 64+× H200 minimum.
- **Cost**: tens of thousands of dollars per run.
- **When**: very rarely. Most gains come from LoRA.

---

## Recommended toolkit (as of 2026-04)

Stack that has working V4 recipes:

- **Training**: [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl), [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory), [torchtune](https://github.com/pytorch/torchtune) — check for V4-adapted configs, they were rolling out day-of-release.
- **Data**: [Curator](https://github.com/bespokelabsai/curator) or plain JSONL. Quality > quantity — always.
- **Evaluation**: your own held-out set, plus [lm-eval-harness](https://github.com/EleutherAI/lm-evaluation-harness) for general-capability regressions.
- **Inference of the fine-tuned model**: vLLM or SGLang with the base V4 weights + LoRA adapters merged or hot-swapped.

---

## Dataset guidance

**Size:**
- LoRA: 1K–10K high-quality examples is a good starting range.
- Full fine-tune: 100K+ examples.

**Quality:**
- Every example should be one you'd be proud to show a customer.
- 100 perfect examples > 10,000 mediocre ones. Garbage in, garbage out applies 10× at this scale.
- Balance task distribution — if 95% of your data is one format, the model will over-fit to that format.

**Format:**
- Use the V4 chat template (`encoding_dsv4`). Do not roll your own.
- Include `system`, `user`, `assistant` turns as they'll appear at inference.
- If you're training Thinking mode, include realistic reasoning traces — not template-filled placeholders.

---

## Training recipe defaults (LoRA on V4-Flash)

*These are conservative starting points. Tune on a small pilot first.*

```yaml
base_model: deepseek-ai/DeepSeek-V4-Flash
adapter: lora
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj

learning_rate: 1.0e-5
lr_scheduler: cosine
warmup_ratio: 0.03
num_epochs: 2
gradient_accumulation_steps: 4
micro_batch_size: 1
sequence_len: 8192

optimizer: adamw_torch   # Muon is used in pre-training; for LoRA, AdamW is standard
bf16: true
gradient_checkpointing: true
flash_attention: true
```

Notes:
- Don't train at 1M context. Fine-tuning at the full context is wasteful — train at 4K–16K, long-context behavior transfers.
- **Freeze the routing network.** Accidentally fine-tuning the MoE router destabilizes the model quickly. Most toolkits do this by default; verify.

---

## Common pitfalls

1. **Over-training.** Two epochs is usually plenty. Three+ epochs on a small dataset destroys general capability.
2. **Thinking-mode collapse.** If you train only on Non-Thinking examples, the model loses Thinking ability. Include both, or pick one and own the trade-off.
3. **Benchmark regression.** Always hold out 20% of general-capability evals. Domain gains are free-looking until you measure base-capability loss.
4. **Multilingual degradation.** Training heavily on English data will erode V4's multilingual quality. Mix in non-English examples if multilingual matters.
5. **Router-collapse from FP4 adapters.** Keep adapters in BF16/FP16, not FP4, during training.

---

## How to evaluate your fine-tune

Before → after comparison on:

- **Your domain eval** (custom, matched to your use case)
- **General capability regression**: a 200-example random sample of MMLU-Pro
- **Code regression** if code matters: HumanEval
- **Multilingual regression** if languages matter: MGSM
- **Instruction following**: IFEval

If domain eval +10, general capability −5, it's a good trade. If domain +2, general −15, you've over-specialized.

---

## Legal / licensing

Fine-tuned V4 weights **are yours under MIT**. You can:
- Keep them private.
- Open-source them (most labs do).
- Embed them in a commercial product.
- Sell API access to them.

There's no "derivative of a derivative" clause — MIT is MIT. You should still include the upstream MIT notice in any redistribution.

---

## When you have your fine-tune working

Consider:
- Publishing to Hugging Face (if the data policy allows) — the community benefits.
- Writing a blog post with eval numbers — it's now part of the V4 ecosystem narrative.
- Opening a PR here to add your fine-tune to [`resources/awesome-community.md`](../resources/awesome-community.md).
