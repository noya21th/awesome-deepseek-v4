# API Quickstart

V4 speaks OpenAI ChatCompletions **and** Anthropic Messages protocols on the same base URL. Pick whichever SDK you already have installed.

*Source: [Official API announcement, 2026-04-24](https://api-docs.deepseek.com/news/news260424)*

---

## 1. Get an API key

1. Sign up at [platform.deepseek.com](https://platform.deepseek.com).
2. Create a key in the API Keys page.
3. Export it: `export DEEPSEEK_API_KEY=sk-...`

---

## 2. OpenAI-compatible endpoint

Base URL: `https://api.deepseek.com/v1`

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
)

resp = client.chat.completions.create(
    model="deepseek-v4-pro",   # or "deepseek-v4-flash"
    messages=[
        {"role": "system", "content": "You are a careful assistant."},
        {"role": "user", "content": "Summarize the Black-Scholes model in 3 bullets."},
    ],
    temperature=1.0,
    top_p=1.0,
)
print(resp.choices[0].message.content)
```

Works with Node.js `openai`, Go `openai-go`, Ruby `ruby-openai`, etc. Change the base URL, change the model name, keep everything else.

---

## 3. Anthropic-compatible endpoint

Base URL: `https://api.deepseek.com/anthropic`

```python
from anthropic import Anthropic
import os

client = Anthropic(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/anthropic",
)

msg = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarize the Black-Scholes model in 3 bullets."}],
)
print(msg.content[0].text)
```

---

## 4. Thinking vs Non-Thinking mode

V4 has two reasoning modes. The same model, same price, different output style.

**Thinking mode** (default for hard reasoning / code):
```python
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[...],
    extra_body={"thinking": {"type": "enabled"}},
)
# The model will emit a <thinking>...</thinking> trace before the final answer.
```

**Non-Thinking mode** (lower latency, for simple tasks):
```python
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[...],
    extra_body={"thinking": {"type": "disabled"}},
)
```

Check the official [DeepSeek API docs](https://api-docs.deepseek.com/) for the exact current parameter name — the announcement refers to "dual modes" but the precise SDK flag evolves.

---

## 5. Function calling / tool use

V4 supports OpenAI-style tool calls out of the box:

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}]

resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
)
# resp.choices[0].message.tool_calls → list of calls
```

---

## 6. JSON output

```python
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "List 3 CJK languages as JSON {languages: [...]}."}],
    response_format={"type": "json_object"},
)
```

---

## 7. Streaming

```python
stream = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Write a haiku about compilers."}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

---

## 8. Raw curl (no SDK)

```bash
curl https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [{"role":"user","content":"Hello"}]
  }'
```

---

## Next steps

- Switching from OpenAI? → [migration-from-openai.md](./migration-from-openai.md)
- Switching from Claude? → [migration-from-claude.md](./migration-from-claude.md)
- Upgrading from DeepSeek V3? → [migration-from-v3.md](./migration-from-v3.md)
- Running locally? → [local-deployment.md](./local-deployment.md)
