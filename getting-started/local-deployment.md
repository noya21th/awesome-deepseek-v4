# Local / Self-Hosted Deployment

How to run V4 on your own hardware. This page is a **starting point** — inference frameworks move quickly around new model releases. Always check the framework's own release notes for current V4 support.

---

## Before you start: hardware check

| Model | Disk | Minimum GPU memory (inference, 1M context) |
|---|---|---|
| V4-Flash (284B / 13B active, FP8) | ~160 GB | 8× H100 80GB (tight) or 8× H200 141GB (comfortable) |
| V4-Pro (1.6T / 49B active, FP4+FP8) | ~865 GB | 16× H200 recommended; 8× H200 possible with offload |

The **activated** parameter count (13B / 49B) determines compute cost per token. The **total** parameter count determines memory required to hold the model. You need memory for all experts even though only a subset is active per token.

---

## Option 1 — Hugging Face `transformers` (smallest footprint for testing)

```bash
pip install "transformers>=4.52" accelerate safetensors
```

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL = "deepseek-ai/DeepSeek-V4-Flash"   # start with Flash unless you have 16+ GPUs

tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)

# V4 uses a custom chat template via encoding_dsv4 — see model card
from encoding_dsv4 import encode_messages
prompt = encode_messages(
    [{"role": "user", "content": "What is the capital of France?"}],
    thinking_mode="thinking",
)

ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
out = model.generate(ids, max_new_tokens=512, temperature=1.0, top_p=1.0)
print(tokenizer.decode(out[0]))
```

`transformers` direct loading is **fine for functional testing, slow for production**. For throughput, use vLLM or SGLang.

---

## Option 2 — vLLM (recommended for production)

vLLM publishes V4 day-one support. Check their release notes for the exact minimum version.

```bash
pip install "vllm>=0.10"   # check vLLM's V4 announcement for the real minimum
```

Serve V4-Flash:
```bash
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --tensor-parallel-size 8 \
  --max-model-len 1048576 \
  --quantization fp8 \
  --trust-remote-code \
  --port 8000
```

Now you have an **OpenAI-compatible endpoint at `http://localhost:8000/v1`** — point any OpenAI SDK at it with `base_url="http://localhost:8000/v1"`.

For V4-Pro, you typically need `--tensor-parallel-size 16` plus `--pipeline-parallel-size 2` across 2 nodes, or aggressive expert-parallel sharding within 1 node. See the vLLM V4 docs.

---

## Option 3 — SGLang

SGLang also announced V4 support at launch.

```bash
pip install "sglang[all]"

python -m sglang.launch_server \
  --model-path deepseek-ai/DeepSeek-V4-Flash \
  --tp 8 \
  --context-length 1048576 \
  --trust-remote-code
```

SGLang's RadixAttention is particularly good at long-context + agent workflows where you repeatedly prefill similar prompts.

---

## Option 4 — Managed hosts (no GPU ops)

If you don't want to run GPUs at all but need something cheaper/more private than DeepSeek's direct API, managed V4 hosts include (check each for current pricing and availability):

- Together AI
- Fireworks AI
- DeepInfra
- Parasail
- Atlas Cloud

Most expose an OpenAI-compatible endpoint. Your code is the same as the [API quickstart](./api-quickstart.md), with their base URL.

---

## Quantization

DeepSeek ships V4-Pro as **FP4 + FP8 mixed** natively (FP4 for MoE experts, FP8 for the rest). This is the canonical format. Going lower (INT4, AWQ, GPTQ) is possible but evaluate community quants against the official FP8/FP4 weights before shipping if quality matters.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| OOM at 1M context | KV cache too big for your GPUs. Lower `--max-model-len` to 128K–256K for most workloads. |
| Garbage output with custom chat template | Use `encoding_dsv4` helper from the model card, not a generic chat template. |
| Thinking output not appearing | Check the exact flag name in the current DeepSeek API / runtime docs. |
| Slow first token | MoE cold-start cost on the first request. Warm up with a dummy prompt. |

---

## Sources

- [DeepSeek-V4-Pro model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro)
- [DeepSeek-V4-Flash model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)
- [vLLM](https://github.com/vllm-project/vllm) / [SGLang](https://github.com/sgl-project/sglang) release notes
