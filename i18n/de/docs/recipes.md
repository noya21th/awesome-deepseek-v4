# Rezepte — praktische Patterns für echte Arbeit mit V4

10 kopierbare Workflows. Jedes Rezept hat **Was**, **Warum V4**, **Minimal-Code**, **typische Kosten**.

*Der Code setzt voraus, dass `export DEEPSEEK_API_KEY=sk-...` gesetzt ist.*

---

## Rezept 1 — Code-Review eines ganzen Repositorys

**Was**: ein gesamtes Repo an V4-Pro übergeben und einen strukturierten PR-Review-Report erhalten.

**Warum V4**: 1M Kontext + SOTA Code-Benchmarks (LiveCodeBench 93,5) + 3,48 $/Mtok Output. Auf Claude Opus 20× teurer, und 200K Kontext erzwingt Chunking — was Cross-File-Reasoning zerstört.

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

**Kosten**: Review eines 500K-Token-Repos ≈ **1–3 $** (V4-Pro). Gleiche Arbeit auf Opus: 30–50 $.

---

## Rezept 2 — Lang-Dokument-QA (mit Genauigkeitshinweis)

**Was**: Fragen zu einem 200-seitigen Vertrag, Patientenakte, Forschungsarbeit beantworten.

**Warum V4**: 1M Kontext bei 27% der V3.2-FLOPs. Aber der technische Bericht stellt klar: **Retrieval-Genauigkeit nimmt über 128K ab** — mit leichtgewichtiger Suche kombinieren.

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def qa(doc: str, question: str) -> str:
    # Bei Dokumenten < 128K Tokens direkt einspeisen;
    # größere: vorher per BM25 die relevantesten ~100K extrahieren.
    resp = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "Antworte ausschließlich aus dem bereitgestellten Dokument. "
             "Wenn die Antwort nicht drinsteht, sage es. Zitiere Abschnitt/Seite wenn möglich."},
            {"role": "user", "content": f"DOKUMENT:\n{doc}\n\nFRAGE: {question}"},
        ],
    )
    return resp.choices[0].message.content
```

**Kosten**: 100K-Token-Dokument + eine Frage ≈ **0,18 $** (Pro) / **0,015 $** (Flash).

**Flash vs. Pro**: Flash für Extraktion ("Was sagt die Kündigungsklausel?"), Pro für Inferenz ("Besteht ein IP-Risiko?").

---

## Rezept 3 — Coding-Agent (Multi-Turn + Tools)

**Was**: Multi-Turn-Agent, der Dateien liest, Befehle ausführt und iteriert, bis die Aufgabe erledigt ist.

**Warum V4**: Codeforces 3206 + natives `tools`-Schema + 1M Kontext fasst lange Tool-Call-Historien ohne Eviction.

```python
import json, os, subprocess
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Datei-Inhalt lesen.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "Shell-Befehl ausführen, stdout/stderr zurückgeben.",
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
    {"role": "system", "content": "Du bist ein Coding-Agent. Nutze Tools zur Inspektion und erledige die Aufgabe."},
    {"role": "user", "content": "Finde und repariere alle Python-Dateien mit Syntaxfehlern."},
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

**Kosten**: 20-Runden-Session, ~10K Tokens Historie ≈ **0,10–0,30 $**.

---

## Rezept 4 — Hochvolumige Batch-Pipeline

**Was**: Übersetzung, Klassifikation, Anreicherung, synthetische Generierung in Millionen-Token-pro-Tag-Größenordnung.

**Warum V4-Flash**: 0,14 $/0,28 $ pro Mtok ist der Boden für Frontier-nahe Qualität. Billiger als GPT-5-Nano für die meisten Aufgaben.

```python
import os, asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                    base_url="https://api.deepseek.com/v1")

async def translate(text: str) -> str:
    r = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": "Übersetze ins Japanische. Gib nur die Übersetzung aus."},
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

**Kosten**: 10.000 kurze Übersetzungen (~2M Tokens) ≈ **0,30–0,60 $**.

---

## Rezept 5 — Mathe-Tutor / formale Beweise

**Was**: Lösungen auf Olympiaden-Niveau mit vollständiger Argumentationsspur.

**Warum V4**: Putnam 2025 formaler Beweis **120/120 Punkte**, HMMT 95,2, IMOAnswerBench 89,8.

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
             "Du bist Olympiade-Mathematik-Coach. Zeige die vollständige Argumentation, "
             "dann gib die finale Antwort klar als FINAL: <Antwort>."},
            {"role": "user", "content": problem},
        ],
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=32_000,
    )
    msg = r.choices[0].message
    return getattr(msg, "reasoning_content", "") or "", msg.content

trace, ans = solve("Beweise, dass es unendlich viele Primzahlen der Form 4k+1 gibt.")
print(ans)
```

**Kosten**: pro Olympiade-Aufgabe **0,05–0,20 $** je nach Tiefe.

---

## Rezept 6 — Multi-Vendor-Fallback mit LiteLLM

**Was**: ein Client routet zu V4, Claude und GPT, bei Fehler/Rate-Limit automatische Umschaltung.

**V4 macht es wirtschaftlich**: V4 ist billig genug, dass eine 3-Anbieter-Redundanz endlich marge-verträglich ist.

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
    messages=[{"role": "user", "content": "Fasse den EU AI Act in 5 Bulletpoints zusammen."}],
)
print(resp.choices[0].message.content)
```

**Kosten**: > 95% des Traffics landet auf V4-Pro (günstigstes in der Gruppe).

---

## Rezept 7 — V4 selbst hosten mit vLLM + OpenAI-Clients

**Was**: V4-Flash im eigenen Netzwerk betreiben, OpenAI-kompatibler Endpunkt exponieren.

**Warum V4**: das einzige Open-Weight-Modell dieser Qualitätsstufe. Pflicht für Air-Gapped-Compliance (HIPAA, SOC2, Behörden).

```bash
# Server: 8× H100 80GB oder 8× H200
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
# Client: einfach OpenAI SDK
from openai import OpenAI
client = OpenAI(api_key="dummy",
                base_url="http://your-internal-host:8000/v1")
```

**Kosten bei Scale**: V4-Flash self-hosted auf reservierten 8× H200, >70% Auslastung ≈ **0,10–0,30 $/Mtok Output**. Billiger als die offizielle API ab ~5 Mrd. Tokens/Monat.

---

## Rezept 8 — Aider (Terminal-Pair-Programming) + V4

Aider ist ein Terminal-AI-Pair-Programmer, der Änderungen via git commit speichert. V4-Pro ist aktuell dessen stärkstes Code-Backend.

```bash
pip install aider-chat
export DEEPSEEK_API_KEY=sk-...
aider --model openai/deepseek-v4-pro \
      --openai-api-base https://api.deepseek.com/v1 \
      --openai-api-key $DEEPSEEK_API_KEY
```

In Aider:
```
> /add src/auth.py src/session.py
> refactore diese zwei Dateien so, dass Sessions in Redis statt im Speicher liegen
```

Aider zeigt Diff, du akzeptierst, es committet. Wiederholen.

**Kosten**: typische 2–3-Stunden-Session mit moderaten Änderungen ≈ **1–5 $** (V4-Pro).

---

## Rezept 9 — Cline (VS Code Agent) + V4

[Cline](https://github.com/cline/cline) ist eine VS-Code-Extension, die den Editor in einen Tool-Using-Agent verwandelt.

Cline-Einstellungen:
- **API Provider**: OpenAI Compatible
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key**: dein DeepSeek-Key
- **Model ID**: `deepseek-v4-pro`

Dann beschreibst du eine Aufgabe im Cline-Panel — es plant, liest/schreibt Dateien, führt Terminal-Befehle aus, iteriert.

**Kosten**: ≈ **0,20–1,00 $** pro komplexer Aufgabe.

---

## Rezept 10 — Synthetische Daten für Fine-Tuning eines kleineren Modells

**Was**: V4-Flash hochqualitative Trainingsdaten für ein eigenes, kleineres Student-Modell generieren lassen.

**Warum V4**: bei 0,28 $/Mtok Output kosten 100M Tokens synthetische Daten **28 $**. Vor drei Jahren war das eine 30.000-$+-Operation.

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
             "Generiere ein hochqualitatives SFT-Beispiel. JSON-Output: "
             "{\"user\": ..., \"assistant\": ...}"},
            {"role": "user", "content": f"Themen-Seed: {seed}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)
```

Kombiniere mit klassischen Qualitätsfiltern (Perplexity, MinHash-Dedup, LLM-as-Judge).

---

## Kosten-Spickzettel

| Workload | Modell | Typische Kosten |
|---|---|---|
| Review ganzes Repo (500K tok) | V4-Pro | 1–3 $ |
| Lang-Doc QA (100K tok + Frage) | V4-Pro | ~0,18 $ |
| Lang-Doc QA (100K tok + Frage) | V4-Flash | ~0,015 $ |
| 20-Runden-Agent | V4-Pro | 0,10–0,30 $ |
| 10.000 Batch-Übersetzungen | V4-Flash | 0,30–0,60 $ |
| Olympiade-Aufgabe | V4-Pro | 0,05–0,20 $ |
| 2h Aider-Session | V4-Pro | 1–5 $ |
| 100M Tokens synthetisch | V4-Flash | ~28 $ |

---

## 6 Goldene Regeln

1. **Temperature = 1,0, Top-P = 1,0** — V4 ist darauf justiert. Keine Claude/GPT-Hyperparameter übernehmen.
2. **Thinking AN**: Mathe/Code/Planung/Mehrstufen-Reasoning. **AUS**: Chat/Klassifikation/Batch.
3. **Flash für Volumen, Pro für Qualität** — die meisten Produktionssysteme nutzen beides.
4. **Nicht naiv 1M Kontext für präzises Retrieval > 128K nutzen** — Retriever einbauen.
5. **Lange System-Prompts cachen** — V4 unterstützt das; Parameter in aktueller API-Doku prüfen.
6. **OpenAI/Claude als Fallback** via LiteLLM — Multi-Vendor-Resilienz endlich bezahlbar.

---

Eigene Rezepte via PR — siehe [CONTRIBUTING.md](../../../CONTRIBUTING.md).
