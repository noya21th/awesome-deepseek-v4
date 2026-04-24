# Prompts library for DeepSeek V4

Battle-tested system prompts, organized by role. Every prompt specifies the recommended **model** (Pro or Flash), **mode** (Thinking or Non-Thinking), and a **minimum usable shape** for the user turn.

## How to use a prompt

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/v1")

# Load the prompt text (everything after the YAML frontmatter)
with open("prompts/coding/code-reviewer.md") as f:
    body = f.read().split("---", 2)[2].strip()

resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": body},
        {"role": "user", "content": "<paste your diff here>"},
    ],
    extra_body={"thinking": {"type": "enabled"}},
)
print(resp.choices[0].message.content)
```

---

## Catalog

### Coding
| Prompt | Use case | Model | Mode |
|---|---|---|---|
| [code-reviewer](./coding/code-reviewer.md) | Pull-request review focused on correctness + security | Pro | Thinking |
| [bug-hunter](./coding/bug-hunter.md) | Isolate a bug from symptom + code + logs | Pro | Thinking |
| [refactor-planner](./coding/refactor-planner.md) | Plan a multi-file refactor before writing code | Pro | Thinking |
| [test-writer](./coding/test-writer.md) | Generate thorough tests for a function | Flash | Thinking |

### Agents
| Prompt | Use case | Model | Mode |
|---|---|---|---|
| [coding-agent](./agents/coding-agent.md) | Multi-turn agent that writes and edits code | Pro | Thinking |
| [research-agent](./agents/research-agent.md) | Web-search-and-synthesize agent | Pro | Thinking |
| [planner](./agents/planner.md) | Plain planning agent — breaks a goal into steps | Flash | Thinking |

### Writing
| Prompt | Use case | Model | Mode |
|---|---|---|---|
| [technical-writer](./writing/technical-writer.md) | Developer-facing docs and tutorials | Pro | Non-Thinking |
| [translator](./writing/translator.md) | Faithful, idiomatic translation with notes | Flash | Non-Thinking |

### Analysis
| Prompt | Use case | Model | Mode |
|---|---|---|---|
| [contract-reviewer](./analysis/contract-reviewer.md) | Flag risks in a commercial contract | Pro | Thinking |
| [paper-summarizer](./analysis/paper-summarizer.md) | Research-paper summary with critique | Pro | Thinking |

### Education
| Prompt | Use case | Model | Mode |
|---|---|---|---|
| [math-tutor](./education/math-tutor.md) | Solve with full reasoning and explanation | Pro | Thinking |

---

## Prompt file format

Each prompt file is:

```markdown
---
name: <short name>
use-case: <one line>
model: pro | flash
mode: thinking | non-thinking
languages: [en, zh, ...]
---

<The full system prompt text goes here. It is a self-contained instruction
block that should work when placed into the "system" role of a chat request.>

## Minimum user turn shape

<What the user should send in the first turn — e.g., "paste the diff",
"describe the bug + paste logs", etc.>

## Example

<Short example input → output pair, optional.>
```

---

## Contributing a prompt

PRs welcome. A good prompt:

1. Has a single clear role — not "helpful assistant" junk.
2. Specifies output format explicitly.
3. Has failure modes addressed (what to do when the input is insufficient, ambiguous, or out-of-scope).
4. Has been tested on V4 — works well with `temperature=1.0, top_p=1.0`.
5. Declares its recommended model and mode.

Shorter is better when it works. Don't pad.
