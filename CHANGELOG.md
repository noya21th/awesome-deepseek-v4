# Changelog

This changelog tracks releases of `awesome-deepseek-v4`, not of DeepSeek V4 itself.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.1.0] — Initial release

### Added

- Main `README.md` (English) plus six fully-localized READMEs: `zh-CN`, `fr`, `ar` (RTL), `ja`, `de`, `hi`.
- Reference documentation:
  - `docs/benchmarks.md` — headline benchmarks with primary-source citations.
  - `docs/architecture.md` — CSA+HCA attention, mHC residuals, Muon optimizer, On-Policy Distillation.
  - `docs/pricing.md` — API, managed-host, self-host TCO.
  - `docs/comparison.md` — comparison tables vs. Claude / GPT / Gemini / Qwen / Llama / Mistral / GLM.
  - `docs/recipes.md` — 10 copy-paste patterns with cost estimates.
  - `docs/prompting-guide.md` — practical prompting for V4.
  - `docs/fine-tuning.md` — LoRA, QLoRA, and full fine-tune guidance.
  - `docs/faq.md` — top community questions.
- Getting-started guides:
  - `getting-started/api-quickstart.md`
  - `getting-started/local-deployment.md`
  - `getting-started/migration-from-v3.md`
  - `getting-started/migration-from-openai.md`
  - `getting-started/migration-from-claude.md`
- Runnable examples under `examples/`:
  - `python_openai_basic.py`
  - `python_anthropic_basic.py`
  - `python_thinking_mode.py`
  - `python_tool_calls.py`
  - `curl_basic.sh`
- Resources:
  - `resources/official-links.md`
  - `resources/awesome-community.md`
  - `resources/papers.md`
- CLI tools under `tools/`:
  - `v4_cost_calc.py` — compare monthly spend across V4 and closed-frontier models.
  - `v4_migrate_env.py` — scan a codebase and rewrite OpenAI/Anthropic config to V4.
  - `v4_repo_review.py` — pack a repository into V4-Pro and get a structured review.
  - `v4_chat.py` — streaming terminal REPL with Thinking-mode and model-switch commands.
- Self-hosting assets under `deploy/`:
  - `docker-compose.yml` — single-command vLLM container serving V4-Flash.
  - `k8s/deployment.yaml` — production Kubernetes manifest.
  - `systemd/v4-vllm.service` — bare-metal unit file.
- Prompt library under `prompts/`:
  - Coding (code-reviewer, bug-hunter, refactor-planner, test-writer).
  - Agents (coding-agent, research-agent, planner).
  - Writing (technical-writer, translator).
  - Analysis (contract-reviewer, paper-summarizer).
  - Education (math-tutor).
- Governance:
  - `LICENSE` (MIT)
  - `DISCLAIMER.md`
  - `CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md`
  - Issue and PR templates under `.github/`.

All factual claims cite a primary source: the V4 model card, the V4 technical report, or the official DeepSeek API announcement.
