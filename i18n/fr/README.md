<div align="center">

<img src="../../assets/banner.svg" alt="awesome-deepseek-v4" width="900">

# awesome-deepseek-v4

**Centre de ressources multilingue pratique pour [DeepSeek V4](https://huggingface.co/collections/deepseek-ai/deepseek-v4).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Non officiel](https://img.shields.io/badge/status-unofficial-lightgrey.svg)](../../DISCLAIMER.md)
[![PRs bienvenues](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../CONTRIBUTING.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-DeepSeek--V4-yellow)](https://huggingface.co/collections/deepseek-ai/deepseek-v4)

**🌍 Choisissez votre langue**

[English](../../README.md) · [简体中文](../zh-CN/README.md) · [**Français**](./README.md) · [العربية](../ar/README.md) · [日本語](../ja/README.md) · [Deutsch](../de/README.md) · [हिन्दी](../hi/README.md)

</div>

---

## Fiche technique

| | **DeepSeek-V4-Pro** | **DeepSeek-V4-Flash** |
|---|---|---|
| Paramètres totaux | **1,6 T** MoE | **284 B** MoE |
| Paramètres activés | 49 B | 13 B |
| Experts (routés × actifs) | 384 × 6 | 256 × 6 |
| Contexte | 1 000 000 tokens | 1 000 000 tokens |
| Tokens d'entraînement | 33 T | 32 T |
| Précision | FP4 (experts) + FP8 | FP8 |
| Prix entrée | 1,74 $ / Mtok | 0,14 $ / Mtok |
| Prix sortie | 3,48 $ / Mtok | 0,28 $ / Mtok |
| Licence | MIT · usage commercial OK | MIT · usage commercial OK |
| Modes | Thinking · Non-Thinking | Thinking · Non-Thinking |

Spécification complète : [docs/architecture.md](../../docs/architecture.md) · Benchmarks : [docs/benchmarks.md](../../docs/benchmarks.md) · Tarifs : [docs/pricing.md](../../docs/pricing.md) · Tableaux comparatifs : [docs/comparison.md](../../docs/comparison.md).

---

## Démarrage en 60 secondes

V4 parle **à la fois** les protocoles OpenAI ChatCompletions et Anthropic Messages.

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/v1")
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Démontrez que √2 est irrationnel."}],
)
print(resp.choices[0].message.content)
```

```python
from anthropic import Anthropic
client = Anthropic(api_key="sk-...", base_url="https://api.deepseek.com/anthropic")
msg = client.messages.create(
    model="deepseek-v4-pro", max_tokens=1024,
    messages=[{"role": "user", "content": "Démontrez que √2 est irrationnel."}],
)
print(msg.content[0].text)
```

Plus : [quickstart API](../../getting-started/api-quickstart.md) · [mode Thinking](../../examples/python_thinking_mode.py) · [tool calling](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh) · [vLLM local](../../getting-started/local-deployment.md).

---

## Contenu du dépôt

### Démarrage et migration
- [**Quickstart API**](../../getting-started/api-quickstart.md)
- [**Déploiement local**](../../getting-started/local-deployment.md) — vLLM / SGLang / transformers
- [**Migration depuis DeepSeek V3**](../../getting-started/migration-from-v3.md)
- [**Migration depuis OpenAI**](../../getting-started/migration-from-openai.md) — changer 2 lignes
- [**Migration depuis Anthropic Claude**](../../getting-started/migration-from-claude.md) — changer 2 lignes

### Référence
- [**Benchmarks**](../../docs/benchmarks.md)
- [**Architecture**](../../docs/architecture.md) — CSA+HCA / mHC / Muon / OPD
- [**Tarifs**](../../docs/pricing.md)
- [**Tableaux comparatifs**](../../docs/comparison.md)

### Pour travailler
- [**Recettes**](../../docs/recipes.md) — **10 patterns prêts à copier-coller** avec estimations de coût.
- [**Guide de prompting**](../../docs/prompting-guide.md)
- [**Fine-tuning**](../../docs/fine-tuning.md)
- [**FAQ**](../../docs/faq.md)

### Ressources
- [Liens officiels](../../resources/official-links.md)
- [Awesome communauté](../../resources/awesome-community.md)
- [Articles de référence](../../resources/papers.md)

### Exemples
[OpenAI SDK](../../examples/python_openai_basic.py) · [Anthropic SDK](../../examples/python_anthropic_basic.py) · [Thinking](../../examples/python_thinking_mode.py) · [Tool calls](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh)

### Outils CLI ([`tools/`](../../tools/))
CLIs Python mono-fichier. Seule dépendance : `openai`.
- [**v4-cost-calc**](../../tools/v4_cost_calc.py) — comparer la dépense mensuelle : V4 vs Claude / GPT / Gemini.
- [**v4-migrate-env**](../../tools/v4_migrate_env.py) — scanner un projet et migrer la configuration OpenAI/Anthropic vers V4.
- [**v4-repo-review**](../../tools/v4_repo_review.py) — envoyer un dépôt à V4-Pro et obtenir une revue structurée.
- [**v4-chat**](../../tools/v4_chat.py) — REPL terminal en streaming.

### Auto-hébergement ([`deploy/`](../../deploy/))
Un endpoint compatible OpenAI sur votre matériel.
- [**Docker Compose**](../../deploy/docker-compose.yml) — `docker compose up`.
- [**Kubernetes**](../../deploy/k8s/deployment.yaml) — Deployment + Service + ConfigMap.
- [**systemd**](../../deploy/systemd/v4-vllm.service) — unité pour bare-metal.

### Bibliothèque de prompts ([`prompts/`](../../prompts/))
Prompts système testés. Chacun déclare son modèle et son mode recommandés.
- Code : [code-reviewer](../../prompts/coding/code-reviewer.md) · [bug-hunter](../../prompts/coding/bug-hunter.md) · [refactor-planner](../../prompts/coding/refactor-planner.md) · [test-writer](../../prompts/coding/test-writer.md)
- Agents : [coding-agent](../../prompts/agents/coding-agent.md) · [research-agent](../../prompts/agents/research-agent.md) · [planner](../../prompts/agents/planner.md)
- Écriture : [technical-writer](../../prompts/writing/technical-writer.md) · [translator](../../prompts/writing/translator.md)
- Analyse : [contract-reviewer](../../prompts/analysis/contract-reviewer.md) · [paper-summarizer](../../prompts/analysis/paper-summarizer.md)
- Éducation : [math-tutor](../../prompts/education/math-tutor.md)

---

## Contribuer

PRs bienvenues — corrections, traductions, nouveaux benchmarks, nouveaux outils. Voir [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## Licence et avis

- Contenu original : [MIT](../../LICENSE).
- Poids et rapport technique DeepSeek V4 : MIT, © DeepSeek-AI.
- "DeepSeek" est une marque de DeepSeek-AI. Projet **non affilié à DeepSeek-AI** — voir [DISCLAIMER](../../DISCLAIMER.md).

---

## Mainteneur

**AI小蓝鲸** — je publie sur l'IA et les modèles open-source en chinois. Même pseudo sur toutes les plateformes :

| Plateforme | Pseudo |
|---|---|
| 📕 Xiaohongshu (小红书) | [AI小蓝鲸](https://www.xiaohongshu.com/search_result?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8&type=54) |
| 📺 Bilibili (B站) | [AI小蓝鲸](https://search.bilibili.com/upuser?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎵 Douyin (抖音) | [AI小蓝鲸](https://www.douyin.com/search/AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎬 WeChat Channels (视频号) | **AI小蓝鲸** (à rechercher dans WeChat) |

Les PRs sont bienvenues quelle que soit la plateforme.

---

<div align="center">

Mettez ⭐ si ce dépôt vous fait gagner du temps.

</div>
