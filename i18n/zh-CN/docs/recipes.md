# 配方集 —— V4 真实能用的工作流

可复制粘贴就能跑的 10 种模式。每个配方包含**做什么**、**为什么用 V4**、**最小可运行代码**、**典型成本**。

*所有代码假设已执行 `export DEEPSEEK_API_KEY=sk-...`*

---

## 配方 1 —— 整仓库代码审查

**做什么**：把整个 repo 一次性送进 V4-Pro，得到一份结构化 PR 级评审报告。

**为什么用 V4**：1M 上下文 + LiveCodeBench 93.5 代码 SOTA + $3.48/Mtok 输出。同样任务在 Claude Opus 上贵 20 倍，200K 上下文强制分块 —— 分块就毁掉跨文件推理。

```python
import os, pathlib
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

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

**成本**：500K tokens 的 repo 评审约 **$1–3**（V4-Pro）。同任务 Opus 上：$30–50。

---

## 配方 2 —— 长文档 QA（含精度坑说明）

**做什么**：对 200 页合同、病历、论文做问答。

**为什么用 V4**：1M 上下文 FLOPs 只有 V3.2 的 27%。但技术报告明写 **128K 以上检索准确率下降**，所以配合轻量检索用。

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def qa(doc: str, question: str) -> str:
    # 文档 < 128K tokens 直接塞；更大的先做 BM25 挑出前 100K 相关段
    resp = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "只基于提供的文档回答。若文档中无答案，明确说明。"
             "尽可能引用段落/页码。"},
            {"role": "user", "content": f"文档：\n{doc}\n\n问题：{question}"},
        ],
    )
    return resp.choices[0].message.content
```

**成本**：100K tokens 文档 + 一个问题 ≈ **$0.18**（Pro）/ **$0.015**（Flash）。

**Flash vs Pro 选谁**：抽取式（"终止条款是什么"）用 Flash；推理式（"本合同有 IP 风险吗"）用 Pro。

---

## 配方 3 —— 代码 Agent（多轮工具调用）

**做什么**：能读文件、运行命令、反复迭代直到任务完成的多轮 Agent。

**为什么用 V4**：Codeforces 3206 + 原生 `tools` 格式 + 1M 上下文装得下超长工具调用历史。

```python
import json, os, subprocess
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "读取文件内容。",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "运行 shell 命令，返回 stdout/stderr。",
        "parameters": {"type": "object",
                       "properties": {"cmd": {"type": "string"}},
                       "required": ["cmd"]}}},
]

def handle(name, args):
    if name == "read_file": return open(args["path"]).read()
    if name == "run_shell":
        r = subprocess.run(args["cmd"], shell=True, capture_output=True, text=True)
        return f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"

messages = [
    {"role": "system", "content": "你是代码 Agent，用工具探查仓库并完成任务。"},
    {"role": "user", "content": "找到并修复所有有语法错误的 Python 文件。"},
]

for _ in range(20):
    r = client.chat.completions.create(
        model="deepseek-v4-pro", messages=messages, tools=tools,
        extra_body={"thinking": {"type": "enabled"}},
    )
    msg = r.choices[0].message
    messages.append(msg.model_dump(exclude_none=True))
    if not msg.tool_calls:
        print(msg.content); break
    for c in msg.tool_calls:
        out = handle(c.function.name, json.loads(c.function.arguments))
        messages.append({"role": "tool", "tool_call_id": c.id, "content": out})
```

**成本**：20 轮、历史约 10K tokens 的 Agent 会话 ≈ **$0.10–0.30**。

---

## 配方 4 —— 大批量流水线

**做什么**：百万 tokens/天 级的翻译、分类、内容丰富、合成生成。

**为什么用 V4-Flash**：$0.14/$0.28 是准前沿质量档的地板价。GPT-5-Nano 在大多数任务上也更贵。

```python
import os, asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                    base_url="https://api.deepseek.com/v1")

async def translate(text: str) -> str:
    r = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": "翻译为日文，只输出译文。"},
                  {"role": "user", "content": text}],
        extra_body={"thinking": {"type": "disabled"}},
    )
    return r.choices[0].message.content

async def run(texts, concurrency=32):
    sem = asyncio.Semaphore(concurrency)
    async def go(t):
        async with sem: return await translate(t)
    return await asyncio.gather(*(go(t) for t in texts))
```

**成本**：翻译 1 万条短文本（约 200 万 tokens）≈ **$0.30–0.60**。

---

## 配方 5 —— 数学辅导 / 形式化证明

**做什么**：产出带完整推理过程的奥数级解答。

**为什么用 V4**：Putnam 2025 形式化证明 **120/120 满分**、HMMT 95.2、IMOAnswerBench 89.8。

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def solve(problem: str):
    r = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "你是奥数教练。展示完整推理，然后用 FINAL: <答案> 明确给出最终答案。"},
            {"role": "user", "content": problem},
        ],
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=32_000,
    )
    msg = r.choices[0].message
    trace = getattr(msg, "reasoning_content", "") or ""
    return trace, msg.content

trace, ans = solve("证明形如 4k+1 的素数有无穷多个。")
print(ans)
```

**成本**：每道奥数题 **$0.05–0.20**（取决于推理深度）。

---

## 配方 6 —— LiteLLM 多厂商容灾

**做什么**：一个客户端同时路由 V4、Claude、GPT，错误或限流自动切换。

**V4 让这件事变便宜**：V4 比 Claude/GPT 便宜很多，3 厂商容灾策略终于经济可行 —— 加两个备胎不吃利润。

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
], fallbacks=[{"smart": ["smart"]}])

resp = router.completion(
    model="smart",
    messages=[{"role": "user", "content": "用 5 条要点总结欧盟 AI 法案。"}],
)
print(resp.choices[0].message.content)
```

**成本**：95%+ 流量落在 V4-Pro（组里最便宜），你几乎只付 V4 的钱，Claude/GPT 只是保险。

---

## 配方 7 —— vLLM 自托管 + OpenAI 客户端

**做什么**：在自己内网跑 V4-Flash，暴露 OpenAI 兼容端点。

**为什么用 V4**：准前沿质量档唯一的开源权重。合规场景（HIPAA、SOC2、政务）必备。

```bash
# 服务端：8× H100 80GB 或 8× H200
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
# 客户端：依然用 openai SDK
from openai import OpenAI
client = OpenAI(api_key="dummy",
                base_url="http://内网地址:8000/v1")
resp = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash",
    messages=[{"role": "user", "content": "VPC 内 hello"}],
)
```

**规模化成本**：自有/预留 8× H200 上自托管 V4-Flash，>70% 利用率下约 **$0.10–0.30 / Mtok 输出**。5B tokens/月以上的稳态负载比官方 API 便宜。

---

## 配方 8 —— Aider（终端结对编程）+ V4

Aider 是个终端里的 AI 结对编程工具，会自动 git commit 你的修改。V4-Pro 是它当前最强的代码后端。

```bash
pip install aider-chat
export DEEPSEEK_API_KEY=sk-...
aider --model openai/deepseek-v4-pro \
      --openai-api-base https://api.deepseek.com/v1 \
      --openai-api-key $DEEPSEEK_API_KEY
```

Aider 内：
```
> /add src/auth.py src/session.py
> 把这两个文件里的 session 存储从内存改成 Redis
```

Aider 展示 diff，你同意，它 commit。循环。

**成本**：典型 2–3 小时编程会话，中等改动量 ≈ **$1–5**（V4-Pro）。

---

## 配方 9 —— Cline（VS Code Agent）+ V4

[Cline](https://github.com/cline/cline) 是 VS Code 扩展，把编辑器变成工具调用 Agent。

Cline 设置中：
- **API Provider**：OpenAI Compatible
- **Base URL**：`https://api.deepseek.com/v1`
- **API Key**：你的 DeepSeek Key
- **Model ID**：`deepseek-v4-pro`

然后在 Cline 面板描述任务 —— 它会规划、读写文件、运行终端命令、迭代。

**成本**：单个复杂任务 ≈ **$0.20–1.00**。

---

## 配方 10 —— 用 V4-Flash 生成合成数据微调小模型

**做什么**：用 V4-Flash 批量生成高质量训练数据，喂给你要微调的小模型。

**为什么用 V4**：$0.28/Mtok 输出的价格下，生成 1 亿 tokens 合成数据只要 **$28**。三年前这是 3 万美金起的活。

```python
import os, json
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def gen(seed: str) -> dict:
    r = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content":
             "生成一条高质量 SFT 样本。输出 JSON: "
             "{\"user\": ..., \"assistant\": ...}"},
            {"role": "user", "content": f"主题种子：{seed}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)

# 跑 1 万条，去重、筛选，再 SFT 一个小模型（Qwen-2B、Llama-3B 等）。
```

配合经典质量过滤（困惑度、MinHash 去重、LLM-as-judge 评分）效果更好。

---

## 成本快速参考

| 工作负载 | 模型 | 典型成本 |
|---|---|---|
| 整仓库审查（500K tok） | V4-Pro | $1–3 |
| 长文档 QA（100K tok + 问题） | V4-Pro | ~$0.18 |
| 长文档 QA（100K tok + 问题） | V4-Flash | ~$0.015 |
| 20 轮代码 Agent | V4-Pro | $0.10–0.30 |
| 1 万条批量翻译 | V4-Flash | $0.30–0.60 |
| 一道奥数题 | V4-Pro | $0.05–0.20 |
| 2 小时 Aider 会话 | V4-Pro | $1–5 |
| 1 亿 tokens 合成数据 | V4-Flash | ~$28 |

---

## 通用六金律

1. **Temperature = 1.0，Top-P = 1.0** —— V4 就是按这组调的，别从 Claude/GPT 照搬其他值。
2. **开 Thinking**：数学、代码、规划、多步推理；**关 Thinking**：聊天、分类、批量任务。
3. **Flash 跑量，Pro 求质** —— 多数生产系统两个都用，按任务路由。
4. **别天真地 1M 上下文做精准检索 —— 128K 之后降质**，配 RAG。
5. **长 system prompt 开缓存** —— V4 支持，具体参数看官方 API 文档。
6. **LiteLLM 留 OpenAI/Claude 备胎** —— 多厂商容灾终于便宜到值得做。

---

通过 PR 提交你的配方 —— 见 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。
