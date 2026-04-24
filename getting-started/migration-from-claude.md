# Migrating from Anthropic Claude → DeepSeek V4

V4 natively speaks the **Anthropic Messages protocol**. You can keep using `anthropic` SDK with just a base URL change.

*Source: [Official V4 launch announcement, 2026-04-24](https://api-docs.deepseek.com/news/news260424).*

---

## The 2-line change

```diff
  from anthropic import Anthropic

  client = Anthropic(
-     api_key=os.environ["ANTHROPIC_API_KEY"],
-     # default base_url = https://api.anthropic.com
+     api_key=os.environ["DEEPSEEK_API_KEY"],
+     base_url="https://api.deepseek.com/anthropic",
  )

  msg = client.messages.create(
-     model="claude-opus-4-6",
+     model="deepseek-v4-pro",
      max_tokens=1024,
      messages=[...],
  )
```

---

## Model mapping

| Claude model | Recommended V4 replacement | Notes |
|---|---|---|
| Claude Haiku 4.6 | `deepseek-v4-flash` | Flash is cheaper per-token, 1M context |
| Claude Sonnet 4.6 | `deepseek-v4-pro` (non-Thinking) | Similar quality tier, much cheaper |
| Claude Opus 4.6 | `deepseek-v4-pro` (Thinking mode) | V4-Pro Max benchmarks within a few points of Opus Max |
| Claude with extended thinking | `deepseek-v4-pro` + Thinking mode | Same model, enable Thinking |

---

## Feature compatibility matrix

| Feature | Claude | DeepSeek V4 (Anthropic endpoint) | Notes |
|---|---|---|---|
| Messages API | ✅ | ✅ | Drop-in |
| Streaming | ✅ | ✅ | Drop-in |
| Tool use | ✅ | ✅ | Drop-in |
| Prompt caching | ✅ | ⚠️ check current docs | V4 has a caching mechanism; parameter names evolve |
| Extended thinking | ✅ | ✅ | V4 has dual-mode Thinking |
| Vision input | ✅ | ❌ | V4 is text-only (preview) |
| PDF input | ✅ | ❌ | Extract text client-side |
| Computer Use / agent tools | ✅ (beta) | ❌ | No 1:1 replacement |
| System prompt | ✅ | ✅ | Drop-in |
| Multi-turn with tool results | ✅ | ✅ | Drop-in |

---

## Expected cost delta

At the **Opus 4.6** quality tier:

| | Claude Opus 4.6 | V4-Pro | Saving |
|---|---|---|---|
| Input $/Mtok | ~$15 | $1.74 | ~88% |
| Output $/Mtok | ~$75 | $3.48 | ~95% |
| Context window | 200K | 1M | 5× longer |

For an agent workload (heavy output, many tool calls, long conversation history), the output-token savings alone can be 10-20× at equivalent quality tier — assuming V4's code/reasoning is good enough for your task (it is, for most).

At the **Sonnet 4.6** tier the delta is smaller but still material (~60–75% cheaper on output).

---

## Gotchas specific to Claude → V4

1. **Claude prompts are often terse; V4 prompts work better with slightly more explicit structure.** If you depended on Claude's particular instruction-following style, re-test.
2. **Tool use JSON**: Claude's nested content-block format is supported on the Anthropic endpoint. Validate once.
3. **Prompt caching savings may not transfer 1:1.** Claude's cache semantics are distinct. Test your long system prompts for cache-hit effectiveness on V4.
4. **Safety / refusal behavior differs.** V4 has a different refusal profile than Claude. Re-run your safety eval set during canary.
5. **No Computer Use.** If your product uses Claude's Computer Use beta, there is no equivalent on V4 — keep Claude for that specific path.

---

## Recommended migration path

1. **Set up a second client** pointing at DeepSeek. Keep the Anthropic client in place.
2. **Shadow test on 5–10% of traffic** for 1–2 weeks. Log both responses, score on your own eval.
3. **Migrate the easiest tier first** — Haiku → V4-Flash. Latency and quality should be comparable, savings are immediate.
4. **Opus → V4-Pro is the highest-value migration** but also the most sensitive. Pilot on an internal / non-customer-facing workload before rolling out.
5. **Keep Claude as a fallback.** Multi-vendor resilience is cheap insurance.

---

## When NOT to migrate

- You depend on **vision**, **PDF input**, or **Computer Use**.
- Your product has been **exhaustively prompt-engineered against Claude's specific instruction-following behavior** and changing it is riskier than the cost savings.
- You have a **compliance requirement** that forbids non-US model vendors and you don't want to self-host.

For all three, the hybrid pattern (V4 for compatible paths, Claude for the rest) usually beats an all-or-nothing migration.
