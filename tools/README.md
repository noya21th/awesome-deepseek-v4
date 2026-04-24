# Tools

Single-file Python CLIs. Each is runnable with `python <script>.py`. Only dependency (when needed) is the `openai` package.

```bash
pip install openai
export DEEPSEEK_API_KEY=sk-...
```

| Tool | What it does |
|---|---|
| [`v4_cost_calc.py`](./v4_cost_calc.py) | Compare monthly LLM spend across V4, Claude, GPT, Gemini. Accepts token counts (`5M`, `500K`) or an OpenAI usage CSV. |
| [`v4_migrate_env.py`](./v4_migrate_env.py) | Scan a codebase for OpenAI/Anthropic config and rewrite it to DeepSeek V4. Dry-run by default; use `--apply` to write. |
| [`v4_repo_review.py`](./v4_repo_review.py) | Pack a repository into V4-Pro and get a structured Critical/Major/Minor review. |
| [`v4_chat.py`](./v4_chat.py) | Minimal streaming REPL for V4 with `/think`, `/model`, `/save` commands. |

---

## Examples

**Compare the cost of running 5M input + 2M output tokens per month:**
```bash
python v4_cost_calc.py --input 5M --output 2M
```

**Migrate an existing project from OpenAI to V4-Pro (dry-run first):**
```bash
python v4_migrate_env.py /path/to/project
python v4_migrate_env.py /path/to/project --apply
```

**Review a repo:**
```bash
python v4_repo_review.py . --focus security -o review.md
```

**Chat:**
```bash
python v4_chat.py --model flash --no-think
```

All tools are MIT-licensed as part of this repository.
