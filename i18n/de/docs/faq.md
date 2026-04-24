# FAQ

Die Fragen, die in jedem V4-Thread auf HN / Reddit / X auftauchen.

---

## Grundlagen

### Was ist DeepSeek V4?
Zwei Open-Weight-MoE-Sprachmodelle, veröffentlicht von DeepSeek-AI am 2026-04-24: **V4-Pro** (1,6 T / 49 B aktiv) und **V4-Flash** (284 B / 13 B aktiv). Beide: 1M Token Kontext, Thinking/Non-Thinking Dual-Mode, MIT-Lizenz.

### Ist V4 wirklich Open Source?
**Gewichte: ja, MIT.** Download, Betrieb, Fine-Tuning, kommerzielle Nutzung bedingungslos.
**Trainingscode und -daten: nein.** DeepSeek veröffentlicht einen detaillierten technischen Bericht, aber nicht die vollständige Pre-Training-Pipeline. Gleiches Muster wie Llama, Qwen — „Open-Weight" ist nicht „Open Source" im OSI-Sinne.

### Was erlaubt die Lizenz genau?
MIT: kommerzielle Nutzung ✅, Modifikation ✅, Weitergabe ✅, private Nutzung ✅. MIT-Hinweis bei Weitergabe beilegen. Kein überlagernder AUP.

### Unterschied V4-Pro / V4-Flash?

| | V4-Pro | V4-Flash |
|---|---|---|
| Gesamtparameter | 1,6 T | 284 B |
| Aktive Parameter | 49 B | 13 B |
| Qualitätsklasse | ≈ GPT-5.4 / Claude Opus 4.6 | ≈ Claude Haiku / GPT-5-Mini |
| API-Preis (in/out) | 1,74 $ / 3,48 $ | 0,14 $ / 0,28 $ |
| Self-Host-Untergrenze | 16× H200 | 8× H200 |

Kostenkritische Last: Flash. Qualitätskritische Last: Pro.

---

## Vergleich

### V4 vs Claude 4.6 / GPT-5.4 / Gemini 3.1-Pro?
Kurz: **SOTA in Code, Gleichstand im Reasoning, Lücke beim Weltwissen.** Details: [Vergleichstabellen](./comparison.md).

### V4 vs Qwen 3.5 / Llama 4 / GLM-5?
Alle stark. V4 führt bei Code und langem Kontext; Llama 4 hat das reifste Ökosystem; Qwen ist am stärksten multilingual; GLM-5 ist am schlankesten an der Spitze der Leaderboards.

### Ist V4 wirklich besser als Opus bei Code?
Auf öffentlichen Benchmarks (LiveCodeBench 93,5 vs 88,8, Codeforces 3206): ja. SWE-Bench Verified: 80,6 vs 80,8 — Gleichstand. **Evaluiert beide auf eurer echten Codebase.**

---

## Praxis

### Kann ich meinen OpenAI- / Claude-Code mit V4 benutzen?
Ja. V4 spricht sowohl OpenAI ChatCompletions als auch Anthropic Messages. `base_url` und Modellname ändern.

### Gibt es ein kostenloses Kontingent?
DeepSeek hat Neukonten historisch kostenlose Credits gewährt. Aktuelle Bedingungen auf platform.deepseek.com. Auch Free Tiers bei Drittanbietern (OpenRouter, Together) nutzbar.

### Welche Rate-Limits?
In der Preview keine offiziellen Zahlen. Community berichtet: Flash großzügig, Pro straffer. Produktionslasten: entweder DeepSeek-Vertrieb oder Drittanbieter-Host mit SLA.

### Unterstützt V4 Multimodal (Bild/Audio/Video)?
**Nein — in der Preview nur Text.** Der technische Bericht listet Multimodal als zukünftige Arbeit.

### Unterstützt V4 Function Calling / Tool Use?
Ja. OpenAI-kompatibles `tools`-Schema + Anthropic-kompatibles `tools` (jeweilige Endpunkte). Siehe [examples/python_tool_calls.py](../../../examples/python_tool_calls.py).

### Was ist Thinking Mode?
V4 hat einen Dual-Mode: entweder sichtbare Reasoning-Spur (`thinking: enabled`) oder direkte Antwort (`thinking: disabled`). Gleiches Modell, gleicher Preis, unterschiedlicher Ausgabestil. Für Mathe/Code ein, für einfachen Chat aus.

### Wie lang ist der Kontext wirklich nutzbar?
**1.000.000 Tokens.** Aber der technische Bericht merkt an: **Retrieval-Genauigkeit nimmt über 128K ab** — man kann 1M reinschieben, aber präzises Retrieval tief im Kontext wird unzuverlässig. Für RAG einen Retriever vorschalten.

---

## Self-Hosting

### Läuft V4 auf einem Laptop?
Nein. V4-Flash FP8 allein sind ~160 GB Gewichte. Minimum realistisch: 8× H100 80GB.

### Läuft V4 auf einer einzelnen H100?
Nein. Stark quantisierter Flash mit kurzem Kontext theoretisch, Qualität unsicher. Single-GPU-Nutzer: managed API nehmen.

### vLLM / SGLang / TensorRT-LLM?
vLLM und SGLang: Day-0-Support. TensorRT-LLM: NVIDIA-Release-Notes prüfen. Details: [local-deployment.md](../../../getting-started/local-deployment.md).

### Läuft V4 wirklich auf Huawei Ascend?
Laut HN: **ja.** DeepSeek trainiert und betreibt V4 auf Huawei-Chips, Produktionsstack ohne CUDA-Abhängigkeit. Wichtiges Signal für die Entkopplung der AI-Lieferkette. Siehe Huawei-MindIE-Dokumentation.

---

## Privatsphäre / Governance

### Trainiert DeepSeek auf meinen Prompts?
Offizielle API: aktuelle Datenschutzrichtlinie auf platform.deepseek.com prüfen. Drittanbieter (Together, Fireworks): Provider ohne Training auf Kundendaten wählen. Self-Hosting: Daten verlassen euer Netz nicht.

### Ist V4 zensiert?
Wie alle Modelle chinesischer Labs hat V4 auf bestimmten Themen (besonders politisch sensibel in China) andere Schutzmechanismen als westliche Modelle. Für die meisten kommerziellen Fälle irrelevant. Falls doch relevant:
- **API**: Filter serverseitig, nicht änderbar
- **Gewichte**: Community-Techniken wie „Abliteration", auf eigenes Risiko

### Sicher für regulierte Workloads (Gesundheit/Recht/Finance)?
- **Rechtlich**: MIT erlaubt
- **Compliance**: hängt vom Regulator ab. V4 selbst-gehostet in VPC ist kompatibel mit HIPAA / SOC2 / DSGVO
- **API**: abhängig von DeepSeek-Zertifizierungen

### Kann ich V4 in ein verkauftes Produkt einbauen?
Ja. MIT ohne kommerzielle Einschränkung. Best Practice: Modellherkunft (DeepSeek) in About-Seite oder Docs erwähnen.

---

## Dieses Repository

### Ist dieses Repo offiziell?
**Nein.** Community-Ressource. DeepSeek-AI ist weder Autor noch Befürworter. Siehe [DISCLAIMER.md](../../../DISCLAIMER.md).

### Warum kein simpler Link zur offiziellen Doku?
Drei Gründe:
1. **Übersetzung** — 7 Sprachen als First-Class, nicht nur nachträgliche Maschinenübersetzung
2. **Vergleich** — DeepSeek kann sich nicht glaubwürdig mit Claude/GPT vergleichen; ein neutrales Community-Repo kann
3. **Migration** — Guides aus Sicht von „du nutzt gerade eine andere API", das würde DeepSeek nicht so schreiben

### Wie beitragen?
Siehe [CONTRIBUTING.md](../../../CONTRIBUTING.md). Besonders willkommen: Muttersprach-Review, Benchmark-Reproduktion, Deployment-Notes auf ungewöhnlicher Hardware, Community-Tool-Einreichungen.

### Wie auf dem Laufenden bleiben?
Repo auf Watch, oder CHANGELOG.md folgen. Zusage: mit V4-Updates Schritt halten.
