<div align="center">

<img src="../../assets/banner.svg" alt="awesome-deepseek-v4" width="900">

# awesome-deepseek-v4

**Praktisches mehrsprachiges Ressourcen-Hub für [DeepSeek V4](https://huggingface.co/collections/deepseek-ai/deepseek-v4).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Inoffiziell](https://img.shields.io/badge/status-unofficial-lightgrey.svg)](../../DISCLAIMER.md)
[![PRs willkommen](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../CONTRIBUTING.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-DeepSeek--V4-yellow)](https://huggingface.co/collections/deepseek-ai/deepseek-v4)

**🌍 Wähle deine Sprache**

[English](../../README.md) · [简体中文](../zh-CN/README.md) · [Français](../fr/README.md) · [العربية](../ar/README.md) · [日本語](../ja/README.md) · [**Deutsch**](./README.md) · [हिन्दी](../hi/README.md)

</div>

---

## Datenblatt

| | **DeepSeek-V4-Pro** | **DeepSeek-V4-Flash** |
|---|---|---|
| Gesamtparameter | **1,6 T** MoE | **284 B** MoE |
| Aktive Parameter | 49 B | 13 B |
| Experten (geroutet × aktiv) | 384 × 6 | 256 × 6 |
| Kontextlänge | 1.000.000 Tokens | 1.000.000 Tokens |
| Trainings-Tokens | 33 T | 32 T |
| Präzision | FP4 (Experten) + FP8 | FP8 |
| Input-Preis | 1,74 $ / M Tokens | 0,14 $ / M Tokens |
| Output-Preis | 3,48 $ / M Tokens | 0,28 $ / M Tokens |
| Lizenz | MIT · kommerzielle Nutzung OK | MIT · kommerzielle Nutzung OK |
| Modi | Thinking · Non-Thinking | Thinking · Non-Thinking |

Vollständige Spezifikation: [docs/architecture.md](../../docs/architecture.md) · Benchmarks: [docs/benchmarks.md](../../docs/benchmarks.md) · Preise: [docs/pricing.md](../../docs/pricing.md) · Vergleichstabellen: [docs/comparison.md](../../docs/comparison.md).

---

## 60-Sekunden-Quickstart

V4 spricht **gleichzeitig** die Protokolle OpenAI ChatCompletions und Anthropic Messages.

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/v1")
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Beweise, dass √2 irrational ist."}],
)
print(resp.choices[0].message.content)
```

```python
from anthropic import Anthropic
client = Anthropic(api_key="sk-...", base_url="https://api.deepseek.com/anthropic")
msg = client.messages.create(
    model="deepseek-v4-pro", max_tokens=1024,
    messages=[{"role": "user", "content": "Beweise, dass √2 irrational ist."}],
)
print(msg.content[0].text)
```

Mehr: [API-Quickstart](../../getting-started/api-quickstart.md) · [Thinking-Modus](../../examples/python_thinking_mode.py) · [Tool-Calls](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh) · [Lokales vLLM](../../getting-started/local-deployment.md).

---

## Repository-Inhalt

### Einstieg und Migration
- [**API-Quickstart**](../../getting-started/api-quickstart.md)
- [**Lokales Deployment**](../../getting-started/local-deployment.md) — vLLM / SGLang / transformers
- [**Migration von DeepSeek V3**](../../getting-started/migration-from-v3.md)
- [**Migration von OpenAI**](../../getting-started/migration-from-openai.md) — 2 Zeilen ändern
- [**Migration von Anthropic Claude**](../../getting-started/migration-from-claude.md) — 2 Zeilen ändern

### Referenz
- [**Benchmarks**](../../docs/benchmarks.md)
- [**Architektur**](../../docs/architecture.md) — CSA+HCA / mHC / Muon / OPD
- [**Preise**](../../docs/pricing.md)
- [**Vergleichstabellen**](../../docs/comparison.md)

### Für echte Arbeit
- [**Rezepte**](./docs/recipes.md) 🇩🇪 — **10 Copy-Paste-Muster** mit Kostenschätzung.
- [**Prompting-Leitfaden**](../../docs/prompting-guide.md) ⚠️ Englisch
- [**Fine-Tuning**](../../docs/fine-tuning.md) ⚠️ Englisch
- [**FAQ**](./docs/faq.md) 🇩🇪

> *Aktuell sind nur die zwei wertvollsten Detaildokumente — Rezepte und FAQ — ins Deutsche übersetzt. Andere Seiten bleiben englisch. Übersetzungsbeiträge willkommen per PR (siehe [CONTRIBUTING](../../CONTRIBUTING.md)).*

### Ressourcen
- [Offizielle Links](../../resources/official-links.md)
- [Awesome Community](../../resources/awesome-community.md)
- [Relevante Paper](../../resources/papers.md)

### Beispiele
[OpenAI SDK](../../examples/python_openai_basic.py) · [Anthropic SDK](../../examples/python_anthropic_basic.py) · [Thinking](../../examples/python_thinking_mode.py) · [Tool calls](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh)

### CLI-Werkzeuge ([`tools/`](../../tools/))
Einzeldatei-Python-CLIs. Einzige Abhängigkeit: `openai`.
- [**v4-cost-calc**](../../tools/v4_cost_calc.py) — monatliche Kosten vergleichen: V4 vs Claude / GPT / Gemini.
- [**v4-migrate-env**](../../tools/v4_migrate_env.py) — Projekt scannen und OpenAI/Anthropic-Konfiguration auf V4 umstellen.
- [**v4-repo-review**](../../tools/v4_repo_review.py) — Repository an V4-Pro übergeben und strukturierten Review erhalten.
- [**v4-chat**](../../tools/v4_chat.py) — Streaming-Terminal-REPL.

### Self-Hosting ([`deploy/`](../../deploy/))
OpenAI-kompatibler Endpunkt auf eigener Hardware.
- [**Docker Compose**](../../deploy/docker-compose.yml) — ein `docker compose up`.
- [**Kubernetes**](../../deploy/k8s/deployment.yaml) — Deployment + Service + ConfigMap.
- [**systemd**](../../deploy/systemd/v4-vllm.service) — Unit-Datei für Bare-Metal.

### Prompt-Bibliothek ([`prompts/`](../../prompts/))
Getestete System-Prompts mit empfohlenem Modell und Modus.
- Code: [code-reviewer](../../prompts/coding/code-reviewer.md) · [bug-hunter](../../prompts/coding/bug-hunter.md) · [refactor-planner](../../prompts/coding/refactor-planner.md) · [test-writer](../../prompts/coding/test-writer.md)
- Agenten: [coding-agent](../../prompts/agents/coding-agent.md) · [research-agent](../../prompts/agents/research-agent.md) · [planner](../../prompts/agents/planner.md)
- Schreiben: [technical-writer](../../prompts/writing/technical-writer.md) · [translator](../../prompts/writing/translator.md)
- Analyse: [contract-reviewer](../../prompts/analysis/contract-reviewer.md) · [paper-summarizer](../../prompts/analysis/paper-summarizer.md)
- Bildung: [math-tutor](../../prompts/education/math-tutor.md)

---

## Mitwirken

PRs willkommen — Korrekturen, Übersetzungen, neue Benchmarks, Community-Tools. Siehe [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## Lizenz

- Originalinhalt dieses Repositorys: [MIT](../../LICENSE).
- DeepSeek-V4-Gewichte und technischer Bericht: MIT, © DeepSeek-AI.
- „DeepSeek" ist eine Marke von DeepSeek-AI. Dieses Projekt ist **nicht mit DeepSeek-AI verbunden** — siehe [DISCLAIMER](../../DISCLAIMER.md).

---

## Maintainer

**AI小蓝鲸** — ich poste auf Chinesisch über KI und Open-Weight-Modelle. Gleicher Handle auf allen Plattformen:

| Plattform | Handle |
|---|---|
| 📕 Xiaohongshu (小红书) | [AI小蓝鲸](https://www.xiaohongshu.com/search_result?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8&type=54) |
| 📺 Bilibili (B站) | [AI小蓝鲸](https://search.bilibili.com/upuser?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎵 Douyin (抖音) | [AI小蓝鲸](https://www.douyin.com/search/AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎬 WeChat Channels (视频号) | **AI小蓝鲸** (innerhalb WeChat suchen) |

PRs von überall sind willkommen.

---

<div align="center">

Bitte ⭐, wenn dir dieses Repo Zeit spart.

</div>
