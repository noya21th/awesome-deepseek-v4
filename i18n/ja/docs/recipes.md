# レシピ集 — V4 で実際に仕事をするパターン

コピー＆ペーストで動く 10 のワークフロー。各レシピに**何をするか**、**なぜ V4 か**、**最小コード**、**典型的なコスト**を記載。

*すべてのコードは `export DEEPSEEK_API_KEY=sk-...` が設定済みを前提。*

---

## レシピ 1 — リポジトリ全体のコードレビュー

**何**：リポジトリ全体を V4-Pro に投入し、構造化された PR レビューレポートを取得。

**なぜ V4**：1M コンテキスト + LiveCodeBench 93.5（SOTA）+ $3.48/Mtok 出力。Claude Opus なら 20 倍高い上に、200K コンテキストではチャンク分割が必須 — 分割するとクロスファイル推論が失われる。

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

resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content":
         "You are a senior engineer doing a pull-request review. Produce a "
         "markdown report with severity (critical/major/minor), file:line, "
         "rationale. Focus on correctness, security, concurrency. Ignore style."},
        {"role": "user", "content": f"Review this repository:\n{pack_repo('.')}"},
    ],
    extra_body={"thinking": {"type": "enabled"}},
)
print(resp.choices[0].message.content)
```

**コスト**：500K tokens のレビューで約 **$1–3**（V4-Pro）。同作業の Opus：$30–50。

---

## レシピ 2 — 長文書 QA（精度注意付き）

**何**：200 ページの契約書、カルテ、論文に対する質問応答。

**なぜ V4**：1M コンテキストで V3.2 の 27% の FLOPs。ただし技術レポートは **128K 超で検索精度が低下**すると明記 — 軽量検索と組み合わせる。

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def qa(doc: str, question: str) -> str:
    # 128K tokens 未満ならそのまま投入；それ以上なら BM25 で上位 100K を抽出
    resp = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "提供された文書のみに基づいて回答せよ。文書にない場合は明記。"
             "可能なら節・ページを引用せよ。"},
            {"role": "user", "content": f"文書:\n{doc}\n\n質問: {question}"},
        ],
    )
    return resp.choices[0].message.content
```

**コスト**：100K tokens 文書 + 1 質問 ≈ **$0.18**（Pro）/ **$0.015**（Flash）。

**Flash か Pro か**：抽出的な質問（「解約条項は？」）は Flash、推論的な質問（「IP リスクはあるか？」）は Pro。

---

## レシピ 3 — コーディング Agent（多ターン + ツール使用）

**何**：ファイル読込・コマンド実行・反復で完了させる多ターン Agent。

**なぜ V4**：Codeforces 3206 + ネイティブな `tools` 形式 + 1M コンテキストで長い履歴も保持。

```python
import json, os, subprocess
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "ファイル内容を読み取る。",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "シェルコマンドを実行し stdout/stderr を返す。",
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
    {"role": "system", "content": "あなたはコーディング Agent。ツールで調査しタスクを完了せよ。"},
    {"role": "user", "content": "構文エラーのある Python ファイルを見つけて修正せよ。"},
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

**コスト**：20 ターン、履歴約 10K tokens のセッション ≈ **$0.10–0.30**。

---

## レシピ 4 — 大規模バッチパイプライン

**何**：百万 tokens/日規模の翻訳・分類・コンテンツ付与・合成生成。

**なぜ V4-Flash**：$0.14/$0.28 はフロンティア近傍品質帯の床値。GPT-5-Nano より多くのタスクで安い。

```python
import os, asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                    base_url="https://api.deepseek.com/v1")

async def translate(text: str) -> str:
    r = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": "日本語に翻訳、翻訳のみ出力。"},
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

**コスト**：1 万件の短文翻訳（約 200 万 tokens）≈ **$0.30–0.60**。

---

## レシピ 5 — 数学チューター / 形式化証明

**何**：完全な推論過程付きの数学オリンピック級解答を生成。

**なぜ V4**：Putnam 2025 形式化証明 **120/120 満点**、HMMT 95.2、IMOAnswerBench 89.8。

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
             "あなたは数学五輪コーチ。完全な推論を示し、FINAL: <答え> で最終解を明示。"},
            {"role": "user", "content": problem},
        ],
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=32_000,
    )
    msg = r.choices[0].message
    trace = getattr(msg, "reasoning_content", "") or ""
    return trace, msg.content

trace, ans = solve("4k+1 の形の素数が無限に存在することを証明せよ。")
print(ans)
```

**コスト**：1 問あたり **$0.05–0.20**（推論深度による）。

---

## レシピ 6 — LiteLLM によるマルチベンダーフォールバック

**何**：単一クライアントから V4、Claude、GPT にルーティングし、エラー／レート制限時に自動フェイルオーバー。

**V4 が経済的に成立させる**：V4 は Claude/GPT より大幅に安いので、3 ベンダー冗長戦略が初めて成立する — 保険を 2 枚かけても利益を食わない。

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
    messages=[{"role": "user", "content": "EU AI Act を 5 つの箇条書きで要約せよ。"}],
)
print(resp.choices[0].message.content)
```

**コスト**：95% 以上のトラフィックが V4-Pro（グループ内最安）に着地、ほぼ V4 の料金のみ。

---

## レシピ 7 — vLLM で自己ホスト + OpenAI クライアント

**何**：自社ネットワーク内で V4-Flash を走らせ、OpenAI 互換エンドポイントを公開。

**なぜ V4**：このクオリティ帯で唯一のオープンウェイト。規制下環境（HIPAA、SOC2、政府系）で必須。

```bash
# サーバ側：8× H100 80GB または 8× H200
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
# クライアント側：そのまま OpenAI SDK を使う
from openai import OpenAI
client = OpenAI(api_key="dummy",
                base_url="http://your-host:8000/v1")
resp = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash",
    messages=[{"role": "user", "content": "VPC 内からこんにちは"}],
)
```

**スケール時のコスト**：自社/予約 8× H200 で V4-Flash を自己ホスト、>70% 稼働率で約 **$0.10–0.30 / Mtok 出力**。月 50 億 tokens 以上の定常負荷では公式 API より安い。

---

## レシピ 8 — Aider（ターミナルのペアプロ）+ V4

Aider はターミナル内 AI ペアプログラマで、変更を自動で git commit する。V4-Pro は現在の最強コードバックエンド。

```bash
pip install aider-chat
export DEEPSEEK_API_KEY=sk-...
aider --model openai/deepseek-v4-pro \
      --openai-api-base https://api.deepseek.com/v1 \
      --openai-api-key $DEEPSEEK_API_KEY
```

Aider 内で：
```
> /add src/auth.py src/session.py
> これら 2 ファイルの session 保存をメモリから Redis に変更して
```

Aider が diff を表示、承認、commit。繰り返し。

**コスト**：典型的な 2–3 時間のセッション、中程度の編集量 ≈ **$1–5**（V4-Pro）。

---

## レシピ 9 — Cline（VS Code Agent）+ V4

[Cline](https://github.com/cline/cline) はエディタをツール使用 Agent 化する VS Code 拡張。

Cline の設定：
- **API Provider**: OpenAI Compatible
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key**: 自分の DeepSeek キー
- **Model ID**: `deepseek-v4-pro`

Cline パネルでタスクを記述 — 計画、ファイル読み書き、ターミナル実行、反復を自動実行。

**コスト**：複雑タスク 1 件で ≈ **$0.20–1.00**。

---

## レシピ 10 — V4-Flash で合成データを生成し小型モデルを fine-tune

**何**：V4-Flash で高品質な学習データを量産し、自分の小型モデルに食わせる。

**なぜ V4**：$0.28/Mtok の出力単価なら、1 億 tokens の合成データが **$28**。3 年前は 3 万ドル超の仕事。

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
             "高品質な SFT サンプルを 1 件生成。JSON で出力: "
             "{\"user\": ..., \"assistant\": ...}"},
            {"role": "user", "content": f"題材シード: {seed}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)

# 1 万件生成 → 重複除去・品質フィルタ → 小型モデル（Qwen-2B、Llama-3B 等）を SFT
```

古典的な品質フィルタ（困惑度、MinHash 重複除去、LLM-as-judge スコアリング）と併用。

---

## コスト早見表

| ワークロード | モデル | 典型コスト |
|---|---|---|
| リポジトリ全体レビュー（500K tok） | V4-Pro | $1–3 |
| 長文書 QA（100K tok + 質問） | V4-Pro | ~$0.18 |
| 長文書 QA（100K tok + 質問） | V4-Flash | ~$0.015 |
| 20 ターン Agent | V4-Pro | $0.10–0.30 |
| 1 万件バッチ翻訳 | V4-Flash | $0.30–0.60 |
| 数学オリンピック 1 問 | V4-Pro | $0.05–0.20 |
| 2 時間 Aider セッション | V4-Pro | $1–5 |
| 1 億 tokens 合成データ | V4-Flash | ~$28 |

---

## 全レシピ共通の 6 原則

1. **Temperature = 1.0、Top-P = 1.0** — V4 はこの値で調整済み。Claude/GPT の値を流用しない。
2. **Thinking ON**：数学・コード・計画・多段推論。**OFF**：チャット・分類・バッチ。
3. **Flash は量、Pro は質** — ほとんどの本番システムは両方使いタスクで振り分け。
4. **1M コンテキストで精密検索しない** — 128K 超で劣化、RAG を併用。
5. **長い system prompt は cache を有効化** — V4 対応、パラメータ名は公式 API ドキュメントで確認。
6. **LiteLLM で OpenAI/Claude を fallback に** — ベンダー冗長が初めて安価に。

---

自作レシピは PR で — [CONTRIBUTING.md](../../../CONTRIBUTING.md) 参照。
