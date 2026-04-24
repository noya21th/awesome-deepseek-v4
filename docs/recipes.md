# Recipes — practical patterns for using V4

Copy-paste-runnable workflows. Every recipe includes **what it does**, **why V4 specifically**, **minimal code**, and a **cost estimate**.

*All code assumes `export DEEPSEEK_API_KEY=sk-...` is set.*

---

## Recipe 1 — Whole-repo code review

**What**: feed an entire repo to V4-Pro and get a structured PR-review-style report.

**Why V4**: 1M context + SOTA code benchmarks (LiveCodeBench 93.5) + $3.48/Mtok output. On Claude Opus this costs 20× more and 200K context means chunking — which destroys cross-file reasoning.

```python
import os, pathlib
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

# Pack the repo into one message. Skip binaries, node_modules, .git.
SKIP = {".git", "node_modules", "dist", "build", "__pycache__", ".venv"}
EXTS = {".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java", ".md"}

def pack_repo(root: str) -> str:
    parts = []
    for p in pathlib.Path(root).rglob("*"):
        if any(s in p.parts for s in SKIP): continue
        if p.is_file() and p.suffix in EXTS and p.stat().st_size < 200_000:
            parts.append(f"\n\n===== {p} =====\n{p.read_text(errors='ignore')}")
    return "".join(parts)

repo_text = pack_repo(".")

resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content":
         "You are a senior engineer doing a pull-request review. Produce a "
         "markdown report with severity (critical/major/minor), file:line, "
         "rationale. Focus on correctness, security, concurrency. Ignore style."},
        {"role": "user", "content": f"Review this repository:\n{repo_text}"},
    ],
    extra_body={"thinking": {"type": "enabled"}},
)
print(resp.choices[0].message.content)
```

**Cost**: a 500K-token repo review runs ~**$1–3** on V4-Pro. Same job on Opus: ~$30–50.

---

## Recipe 2 — Long-document Q&A (with the accuracy caveat)

**What**: answer questions against a 200-page contract, medical chart, or research paper.

**Why V4**: 1M context at 27% of V3.2's FLOPs. But the technical report flags that **retrieval accuracy degrades past 128K**, so we combine long-context with lightweight retrieval.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def qa_over_document(doc_text: str, question: str) -> str:
    # Rule of thumb: if doc is < 128K tokens, stuff it directly.
    # If larger, do a cheap BM25 retrieval to pull the top 100K most-relevant
    # chunks, then hand those to V4.
    # (Any BM25 lib works — rank_bm25, whoosh, etc.)
    context = doc_text  # assume < 128K here; use BM25 for larger docs

    resp = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "Answer strictly from the provided document. If the answer "
             "isn't in the document, say so. Cite section/page when possible."},
            {"role": "user", "content": f"DOCUMENT:\n{context}\n\nQUESTION: {question}"},
        ],
    )
    return resp.choices[0].message.content
```

**Cost**: a 100K-token doc + one question is **~$0.18** on V4-Pro, **~$0.015** on V4-Flash.

**When to choose Flash vs Pro**: Flash for extractive questions ("what's the termination clause?"), Pro for inferential ones ("does this contract expose us to IP risk?").

---

## Recipe 3 — Coding agent with tool use

**What**: a multi-turn agent that can read files, run commands, and iterate until a task is done.

**Why V4**: Codeforces 3206 + native `tools` schema + 1M context fits long tool-use histories without eviction.

```python
import json, os, subprocess
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "Run a shell command. Returns stdout/stderr.",
        "parameters": {"type": "object",
                       "properties": {"cmd": {"type": "string"}},
                       "required": ["cmd"]}}},
]

def handle_call(name, args):
    if name == "read_file":
        return open(args["path"]).read()
    if name == "run_shell":
        r = subprocess.run(args["cmd"], shell=True, capture_output=True, text=True)
        return f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"

messages = [
    {"role": "system", "content": "You are a coding agent. Use tools to inspect the repo and complete the task."},
    {"role": "user", "content": "Find and fix any Python files with syntax errors."},
]

for _ in range(20):  # cap iterations
    r = client.chat.completions.create(
        model="deepseek-v4-pro", messages=messages, tools=tools,
        extra_body={"thinking": {"type": "enabled"}},
    )
    msg = r.choices[0].message
    messages.append(msg.model_dump(exclude_none=True))
    if not msg.tool_calls:
        print(msg.content); break
    for c in msg.tool_calls:
        out = handle_call(c.function.name, json.loads(c.function.arguments))
        messages.append({"role": "tool", "tool_call_id": c.id, "content": out})
```

**Cost**: a 20-turn agent with 10K-token history runs **~$0.10–0.30** per session.

---

## Recipe 4 — High-volume batch pipeline

**What**: translate, classify, enrich, or generate content at millions-of-tokens-per-day scale.

**Why V4-Flash**: $0.14/$0.28 per Mtok is the cheapest near-frontier-quality tier available. At this price point, V4-Flash undercuts even GPT-5-Nano for most tasks.

```python
import os, asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                    base_url="https://api.deepseek.com/v1")

async def translate_one(text: str) -> str:
    r = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": "Translate to Japanese. Output only the translation."},
                  {"role": "user", "content": text}],
        extra_body={"thinking": {"type": "disabled"}},  # batch → no thinking
    )
    return r.choices[0].message.content

async def run(texts, concurrency=32):
    sem = asyncio.Semaphore(concurrency)
    async def go(t):
        async with sem: return await translate_one(t)
    return await asyncio.gather(*(go(t) for t in texts))

# asyncio.run(run([...list of 10k texts...]))
```

**Cost**: translating 10K short texts (~2M tokens total) runs **~$0.30–0.60** on V4-Flash.

---

## Recipe 5 — Math tutor with proof checking

**What**: generate solutions to olympiad-level problems with step-by-step reasoning traces, optionally verify with a formal prover.

**Why V4**: Putnam 2025 formal proof **120/120 perfect score**, HMMT 95.2, IMOAnswerBench 89.8.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def solve(problem: str) -> tuple[str, str]:
    """Return (reasoning_trace, final_answer)."""
    r = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "You are a math olympiad coach. Show your full reasoning, then "
             "give a clearly-boxed final answer like FINAL: <answer>."},
            {"role": "user", "content": problem},
        ],
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=32_000,  # generous — deep proofs run long
    )
    msg = r.choices[0].message
    trace = getattr(msg, "reasoning_content", "") or ""
    return trace, msg.content

trace, ans = solve("Prove that there are infinitely many primes of the form 4k+1.")
print(ans)
```

**Cost**: ~**$0.05–0.20** per olympiad problem, depending on reasoning depth.

---

## Recipe 6 — Multi-vendor fallback with LiteLLM

**What**: one client that routes to V4, Claude, and GPT with automatic fallback on error or rate-limit.

**Why V4 unlocks this**: V4 is cheap enough that a 3-vendor fallback strategy is finally economical — you don't lose margin by hedging.

```python
# pip install litellm
import os
from litellm import Router

router = Router(model_list=[
    {"model_name": "smart",
     "litellm_params": {"model": "deepseek/deepseek-v4-pro",
                        "api_key": os.environ["DEEPSEEK_API_KEY"],
                        "api_base": "https://api.deepseek.com/v1"}},
    {"model_name": "smart",
     "litellm_params": {"model": "claude-opus-4-6",
                        "api_key": os.environ.get("ANTHROPIC_API_KEY")}},
    {"model_name": "smart",
     "litellm_params": {"model": "gpt-5.4",
                        "api_key": os.environ.get("OPENAI_API_KEY")}},
], fallbacks=[{"smart": ["smart"]}])   # cascading retry within the group

resp = router.completion(
    model="smart",
    messages=[{"role": "user", "content": "Summarize the EU AI Act in 5 bullets."}],
)
print(resp.choices[0].message.content)
```

**Cost**: 95%+ of traffic lands on V4-Pro (cheapest tier in the group), so you pay near-V4 prices while keeping Claude/GPT as insurance.

---

## Recipe 7 — Self-host V4 with vLLM + OpenAI clients

**What**: run V4-Flash inside your own network and expose it as an OpenAI-compatible endpoint.

**Why V4**: the only open-weight model at this quality tier in April 2026. Required for air-gapped compliance (HIPAA, SOC2, government workloads).

```bash
# Server side: 8× H100 80GB or 8× H200
pip install "vllm>=0.10"

python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --tensor-parallel-size 8 \
  --max-model-len 1048576 \
  --quantization fp8 \
  --trust-remote-code \
  --port 8000
```

```python
# Client side: nothing special — it's just OpenAI
from openai import OpenAI

client = OpenAI(api_key="dummy",
                base_url="http://your-internal-host:8000/v1")

resp = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash",
    messages=[{"role": "user", "content": "Hello from the VPC."}],
)
```

**Cost at scale**: on owned / reserved 8× H200, V4-Flash self-hosted lands around **$0.10–0.30 per Mtok output** at >70% utilization — cheaper than the DeepSeek API above ~5B tokens/month.

---

## Recipe 8 — Aider (terminal pair programmer) with V4

**What**: Aider is a terminal AI pair programmer that edits files in git commits. V4-Pro is currently its strongest backend for code.

```bash
pip install aider-chat
export DEEPSEEK_API_KEY=sk-...
aider --model openai/deepseek-v4-pro \
      --openai-api-base https://api.deepseek.com/v1 \
      --openai-api-key $DEEPSEEK_API_KEY
```

Inside Aider:
```
> /add src/auth.py src/session.py
> refactor these two files so sessions are stored in Redis instead of memory
```

Aider shows a diff, you accept, it commits. Repeat.

**Cost**: a typical coding session (2–3 hours, moderate edits) runs **~$1–5** on V4-Pro.

---

## Recipe 9 — Cline (VS Code agent) with V4

**What**: [Cline](https://github.com/cline/cline) is a VS Code extension that turns the editor into a tool-using coding agent.

In Cline's settings:
- **API Provider**: OpenAI Compatible
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key**: your DeepSeek key
- **Model ID**: `deepseek-v4-pro`

Then describe a task in the Cline panel — it plans, reads/writes files, runs terminal commands, and iterates.

**Cost**: ~**$0.20–1.00** per complex task.

---

## Recipe 10 — Synthetic data for fine-tuning a smaller model

**What**: use V4-Flash to generate high-quality training data for a smaller student model you fine-tune yourself.

**Why V4**: at $0.28/Mtok output, generating 100M tokens of high-quality synthetic data costs **$28**. Three years ago this was a $30K+ operation.

```python
import os, json
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def gen_example(seed_prompt: str) -> dict:
    r = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content":
             "Generate a high-quality SFT example. Output JSON: "
             "{\"user\": ..., \"assistant\": ...}"},
            {"role": "user", "content": f"Topic seed: {seed_prompt}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)

# Generate 10K examples across your seed topics, dedupe, filter, then SFT
# a smaller model (Qwen-2B, Llama-3B, etc.) on the result.
```

Worth pairing with classical quality filters (perplexity, dedup via MinHash, LLM-as-judge grading).

---

## Cost cheat-sheet (quick reference)

| Workload | Model | Typical cost |
|---|---|---|
| Whole-repo review (500K tok) | V4-Pro | $1–3 |
| Long-doc QA (100K tok + Q) | V4-Pro | ~$0.18 |
| Long-doc QA (100K tok + Q) | V4-Flash | ~$0.015 |
| 20-turn coding agent | V4-Pro | $0.10–0.30 |
| 10K batch translations | V4-Flash | $0.30–0.60 |
| Olympiad math problem | V4-Pro | $0.05–0.20 |
| 2-hour Aider session | V4-Pro | $1–5 |
| 100M-token synthetic dataset | V4-Flash | ~$28 |

---

## Golden rules across all recipes

1. **Temperature 1.0, Top-P 1.0** — V4 was tuned here; don't port Claude/GPT hyperparameters.
2. **Thinking ON for**: math, code, planning, multi-step reasoning. **OFF for**: chat, classification, batch.
3. **Flash for volume, Pro for quality** — most production systems want both, routed by task.
4. **Don't naively use 1M context for precise retrieval past 128K** — add a retriever.
5. **Cache long system prompts** — V4 exposes caching; check the current DeepSeek API docs for parameter names.
6. **Keep an OpenAI/Claude fallback** via LiteLLM — vendor resilience is finally cheap.

---

Submit your own recipe via PR — see [CONTRIBUTING.md](../CONTRIBUTING.md).
