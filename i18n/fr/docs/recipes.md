# Recettes — patterns pratiques pour travailler avec V4

10 workflows prêts à copier-coller. Chaque recette indique **quoi**, **pourquoi V4**, **code minimal**, **coût typique**.

*Tout le code suppose `export DEEPSEEK_API_KEY=sk-...` configuré.*

---

## Recette 1 — Revue de code de tout un dépôt

**Quoi** : passer l'ensemble d'un repo à V4-Pro et récupérer un rapport de revue structuré de type PR.

**Pourquoi V4** : 1M de contexte + SOTA code (LiveCodeBench 93.5) + 3,48 $/Mtok en sortie. Sur Claude Opus : 20× plus cher, et le contexte de 200K force le découpage — ce qui ruine le raisonnement inter-fichiers.

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

**Coût** : revue d'un repo de 500K tokens ≈ **1–3 $** (V4-Pro). Même travail sur Opus : 30–50 $.

---

## Recette 2 — Q&R sur long document (avec mise en garde)

**Quoi** : répondre à des questions sur un contrat de 200 pages, un dossier médical, un article scientifique.

**Pourquoi V4** : 1M de contexte à 27 % des FLOPs de V3.2. Mais le rapport technique indique explicitement que **la récupération se dégrade au-delà de 128K** — à combiner avec une recherche légère.

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def qa(doc: str, question: str) -> str:
    # Si le doc fait moins de 128K tokens, on l'injecte tel quel ;
    # au-delà, on fait un BM25 pour extraire les ~100K plus pertinents.
    resp = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "Répondez strictement à partir du document fourni. "
             "Si la réponse n'y figure pas, dites-le. Citez section/page quand possible."},
            {"role": "user", "content": f"DOCUMENT:\n{doc}\n\nQUESTION: {question}"},
        ],
    )
    return resp.choices[0].message.content
```

**Coût** : 100K tokens de document + 1 question ≈ **0,18 $** (Pro) / **0,015 $** (Flash).

**Flash ou Pro** : Flash pour l'extraction ("quelle est la clause de résiliation ?") ; Pro pour l'inférence ("ce contrat expose-t-il à un risque IP ?").

---

## Recette 3 — Agent de code (multi-tours + outils)

**Quoi** : un agent multi-tours qui lit des fichiers, exécute des commandes, et itère jusqu'à ce que la tâche soit finie.

**Pourquoi V4** : Codeforces 3206 + schéma `tools` natif + 1M de contexte qui absorbe les historiques longs sans éviction.

```python
import json, os, subprocess
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Lire le contenu d'un fichier.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "Exécuter une commande shell, retourner stdout/stderr.",
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
    {"role": "system", "content": "Tu es un agent de code. Utilise les outils pour inspecter le repo et accomplir la tâche."},
    {"role": "user", "content": "Trouve et corrige tous les fichiers Python avec erreurs de syntaxe."},
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

**Coût** : session de 20 tours, historique ~10K tokens ≈ **0,10–0,30 $**.

---

## Recette 4 — Pipeline batch à haut volume

**Quoi** : traduction, classification, enrichissement ou génération synthétique à l'échelle de millions de tokens par jour.

**Pourquoi V4-Flash** : 0,14 $ / 0,28 $ par Mtok est le tarif plancher pour la qualité proche frontière. Moins cher que GPT-5-Nano sur la plupart des tâches.

```python
import os, asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                    base_url="https://api.deepseek.com/v1")

async def translate(text: str) -> str:
    r = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": "Traduis en japonais. Sortie : traduction uniquement."},
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

**Coût** : traduction de 10 000 textes courts (~2M tokens) ≈ **0,30–0,60 $**.

---

## Recette 5 — Tuteur mathématique / preuves formelles

**Quoi** : générer des solutions de niveau olympiade avec trace de raisonnement complète.

**Pourquoi V4** : Putnam 2025 preuve formelle **120/120 parfait**, HMMT 95,2, IMOAnswerBench 89,8.

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
             "Tu es entraîneur d'olympiades mathématiques. Montre tout le raisonnement, "
             "puis donne la réponse finale clairement sous la forme FINAL: <réponse>."},
            {"role": "user", "content": problem},
        ],
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=32_000,
    )
    msg = r.choices[0].message
    return getattr(msg, "reasoning_content", "") or "", msg.content

trace, ans = solve("Prouver qu'il existe une infinité de nombres premiers de la forme 4k+1.")
print(ans)
```

**Coût** : par problème d'olympiade **0,05–0,20 $** selon la profondeur de raisonnement.

---

## Recette 6 — Basculement multi-fournisseurs avec LiteLLM

**Quoi** : un seul client route vers V4, Claude et GPT, bascule automatique en cas d'erreur ou de limite.

**V4 rend la chose économique** : V4 est assez bon marché pour qu'une stratégie à 3 fournisseurs cesse d'être un luxe — la redondance ne mange pas la marge.

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
    messages=[{"role": "user", "content": "Résume l'EU AI Act en 5 puces."}],
)
print(resp.choices[0].message.content)
```

**Coût** : plus de 95 % du trafic atterrit sur V4-Pro (le moins cher du groupe).

---

## Recette 7 — Auto-hébergement V4 avec vLLM + clients OpenAI

**Quoi** : faire tourner V4-Flash sur votre infrastructure interne, exposer un endpoint OpenAI-compatible.

**Pourquoi V4** : le seul modèle open-weight de ce niveau de qualité. Nécessaire pour conformité air-gapped (HIPAA, SOC2, administrations).

```bash
# Serveur : 8× H100 80GB ou 8× H200
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
# Client : c'est juste OpenAI
from openai import OpenAI
client = OpenAI(api_key="dummy",
                base_url="http://your-internal-host:8000/v1")
```

**Coût à l'échelle** : V4-Flash auto-hébergé sur 8× H200 réservés, >70 % d'utilisation ≈ **0,10–0,30 $/Mtok sortie**. Moins cher que l'API officielle au-delà de ~5 Mds tokens/mois.

---

## Recette 8 — Aider (pair-programmer terminal) + V4

Aider est un pair-programmer AI dans le terminal qui commit ses modifications en git. V4-Pro en est actuellement le backend code le plus fort.

```bash
pip install aider-chat
export DEEPSEEK_API_KEY=sk-...
aider --model openai/deepseek-v4-pro \
      --openai-api-base https://api.deepseek.com/v1 \
      --openai-api-key $DEEPSEEK_API_KEY
```

Dans Aider :
```
> /add src/auth.py src/session.py
> refactorise ces deux fichiers pour stocker les sessions dans Redis au lieu de la mémoire
```

Aider montre un diff, vous acceptez, il commit. Répétez.

**Coût** : session typique de 2–3 h, modifications modérées ≈ **1–5 $** (V4-Pro).

---

## Recette 9 — Cline (agent VS Code) + V4

[Cline](https://github.com/cline/cline) est une extension VS Code qui transforme l'éditeur en agent à outils.

Paramètres Cline :
- **API Provider** : OpenAI Compatible
- **Base URL** : `https://api.deepseek.com/v1`
- **API Key** : votre clé DeepSeek
- **Model ID** : `deepseek-v4-pro`

Décrivez une tâche dans le panneau Cline — il planifie, lit/écrit les fichiers, exécute en terminal, itère.

**Coût** : ≈ **0,20–1,00 $** par tâche complexe.

---

## Recette 10 — Données synthétiques pour fine-tuner un modèle plus petit

**Quoi** : utiliser V4-Flash pour générer des données d'entraînement de haute qualité destinées au fine-tuning d'un modèle étudiant plus petit.

**Pourquoi V4** : à 0,28 $/Mtok en sortie, générer 100M tokens de données synthétiques coûte **28 $**. Il y a trois ans c'était une opération à 30 000 $+.

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
             "Génère un exemple SFT de haute qualité. Sortie JSON : "
             "{\"user\": ..., \"assistant\": ...}"},
            {"role": "user", "content": f"Graine de sujet : {seed}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)
```

À coupler avec des filtres de qualité classiques (perplexité, déduplication MinHash, LLM-as-judge).

---

## Aide-mémoire coût

| Charge | Modèle | Coût typique |
|---|---|---|
| Revue d'un repo entier (500K tok) | V4-Pro | 1–3 $ |
| Q&R long document (100K tok + Q) | V4-Pro | ~0,18 $ |
| Q&R long document (100K tok + Q) | V4-Flash | ~0,015 $ |
| Agent 20 tours | V4-Pro | 0,10–0,30 $ |
| 10 000 traductions batch | V4-Flash | 0,30–0,60 $ |
| Problème d'olympiade | V4-Pro | 0,05–0,20 $ |
| Session Aider 2h | V4-Pro | 1–5 $ |
| 100M tokens synthétiques | V4-Flash | ~28 $ |

---

## 6 règles d'or

1. **Temperature = 1,0, Top-P = 1,0** — V4 a été réglé là, ne portez pas les hyperparamètres de Claude/GPT.
2. **Thinking ON** pour maths/code/planification ; **OFF** pour chat/classification/batch.
3. **Flash pour le volume, Pro pour la qualité** — la plupart des systèmes de prod utilisent les deux.
4. **N'utilisez pas naïvement les 1M de contexte pour de la recherche précise au-delà de 128K** — ajoutez un retriever.
5. **Cache pour les longs system prompts** — V4 le supporte ; vérifiez les paramètres sur la doc API.
6. **Gardez un fallback OpenAI/Claude** via LiteLLM — la résilience multi-fournisseurs devient enfin abordable.

---

Proposez votre recette via PR — voir [CONTRIBUTING.md](../../../CONTRIBUTING.md).
