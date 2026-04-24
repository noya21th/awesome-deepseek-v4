# Migrating from DeepSeek V3 → V4

*Source: [Official V4 launch announcement, 2026-04-24](https://api-docs.deepseek.com/news/news260424).*

---

## TL;DR

**Keep your `base_url`. Change the model name. Done.**

| Before | After |
|---|---|
| `model="deepseek-chat"` | `model="deepseek-v4-pro"` or `"deepseek-v4-flash"` |
| `model="deepseek-reasoner"` | `model="deepseek-v4-pro"` with Thinking mode |

---

## ⚠️ Hard deadline

Per the official announcement:

> `deepseek-chat` and `deepseek-reasoner` will be **fully retired and inaccessible after Jul 24th, 2026, 15:59 (UTC Time)**.

That is roughly a 3-month migration window from the V4 preview release (2026-04-24).

---

## Which V4 replaces which V3?

| V3 model | Recommended V4 replacement | Why |
|---|---|---|
| `deepseek-chat` | `deepseek-v4-flash` | Flash matches V3-chat's cost tier with better quality, 1M context |
| `deepseek-reasoner` | `deepseek-v4-pro` + Thinking mode | V4-Pro's Thinking mode supersedes the separate reasoner SKU |
| V3 for high-end reasoning | `deepseek-v4-pro` | Same tier, better numbers, still MIT-licensed |

---

## Code diff

```diff
  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ["DEEPSEEK_API_KEY"],
      base_url="https://api.deepseek.com/v1",   # unchanged
  )

  resp = client.chat.completions.create(
-     model="deepseek-chat",
+     model="deepseek-v4-flash",
      messages=[...],
  )
```

That's it for most users.

---

## What changes in behavior

- **Context window**: 128K → 1M by default. Your prompts can now be much longer without changing plan tier.
- **Pricing**: Flash is similar to or cheaper than V3-chat; Pro is cheaper per-token than V3-chat for reasoning-heavy tasks.
- **Thinking mode**: now a first-class parameter, not a separate model SKU.
- **Tokenizer**: updated. Re-count tokens if you have strict budgeting — don't assume old token counts carry over.

---

## What stays the same

- Base URL (`https://api.deepseek.com/v1`)
- API key
- Tool calling format
- JSON output format
- Streaming format
- OpenAI SDK compatibility

---

## Self-hosted V3 users

If you're running V3 on your own GPUs, V4 is **architecturally different** (1M context, FP4+FP8 mixed for Pro). You need to:

1. Download new weights from Hugging Face.
2. Update your inference runtime (vLLM / SGLang) to the V4-supporting version.
3. Swap the chat template to the V4 `encoding_dsv4` helper.

See [local-deployment.md](./local-deployment.md).

---

## Rollback plan

If V4 doesn't work for your use case in the 3-month window, you can keep calling V3 models until **2026-07-24 15:59 UTC**. After that, V3 SKUs are gone from the API.

Self-hosted V3 continues to work indefinitely — you own the weights.
