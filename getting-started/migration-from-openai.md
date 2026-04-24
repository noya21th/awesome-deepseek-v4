# Migrating from OpenAI → DeepSeek V4

V4 natively speaks OpenAI ChatCompletions. Your SDK, your request shape, your response parsing — all unchanged. Change two things.

---

## The 2-line change

```diff
  from openai import OpenAI

  client = OpenAI(
-     api_key=os.environ["OPENAI_API_KEY"],
-     # default base_url = https://api.openai.com/v1
+     api_key=os.environ["DEEPSEEK_API_KEY"],
+     base_url="https://api.deepseek.com/v1",
  )

  resp = client.chat.completions.create(
-     model="gpt-5.4",
+     model="deepseek-v4-pro",     # or "deepseek-v4-flash"
      messages=[...],
  )
```

---

## Model mapping

| OpenAI model | Recommended V4 replacement | Notes |
|---|---|---|
| GPT-5-Nano | `deepseek-v4-flash` | Flash is often cheaper with 1M context |
| GPT-5-Mini | `deepseek-v4-flash` | Quality similar, long context cheaper |
| GPT-5.4 | `deepseek-v4-pro` | Competitive on most benchmarks, SOTA on code |
| GPT-5.4 xHigh (extended reasoning) | `deepseek-v4-pro` + Thinking mode | Same model, enable Thinking |
| o-series reasoning models | `deepseek-v4-pro` + Thinking mode | V4 Thinking replaces the o-series pattern |

---

## Feature compatibility matrix

| Feature | OpenAI | DeepSeek V4 | Notes |
|---|---|---|---|
| ChatCompletions | ✅ | ✅ | Drop-in |
| Streaming (`stream=True`) | ✅ | ✅ | Drop-in |
| `tools` / function calling | ✅ | ✅ | Drop-in |
| `response_format={"type":"json_object"}` | ✅ | ✅ | Drop-in |
| `response_format` JSON Schema | ✅ | ✅ (check latest API docs) | Verify with a small test |
| Vision input | ✅ | ❌ | V4 is text-only (preview) |
| Audio input | ✅ | ❌ | V4 is text-only |
| Image output | ✅ (gpt-image-1) | ❌ | Not in scope for V4 |
| `logprobs` | ✅ | ⚠️ check docs | |
| Fine-tuning | ✅ | ✅ (self-host + open weights) | V4 fine-tunes are yours to keep |
| Assistants API | ✅ | ❌ | No 1:1 replacement — roll your own |
| Realtime / voice API | ✅ | ❌ | No equivalent |
| Structured outputs (strict mode) | ✅ | ⚠️ partial | Check current V4 API docs |

If any feature in the ❌/⚠️ rows is critical to you, **stay on OpenAI for that specific code path** and migrate the rest. This is a normal pattern.

---

## Expected cost delta

For a typical chat app at GPT-5.4 quality tier, at equal traffic:

| | GPT-5.4 | V4-Pro | Saving |
|---|---|---|---|
| Input $/Mtok | ~$2.5 | $1.74 | ~30% |
| Output $/Mtok | ~$10 | $3.48 | ~65% |
| Context window | 400K | 1M | 2.5× longer |

For a high-volume code-assistant app (input heavy, output moderate), expect **~50–70% savings** with **comparable or better code quality** (LiveCodeBench / Codeforces favor V4).

---

## Gotchas

1. **Tokenizer differs.** Don't assume OpenAI token counts. If you do strict budgeting with `tiktoken`, switch to the DeepSeek tokenizer.
2. **`max_tokens` semantics** may differ for Thinking-mode. Allocate generously during migration testing.
3. **System prompt style**: OpenAI-trained prompts work, but V4 sometimes benefits from more explicit instructions. Re-test your prompts, don't blind-swap.
4. **Tool calling JSON**: shape matches OpenAI, but validate once end-to-end before going to production.
5. **Rate limits**: DeepSeek's rate limits differ. Load-test before cutover.

---

## Recommended migration path

1. **Week 1**: point a canary (~5% traffic) at V4. Log prompts + both responses side-by-side.
2. **Week 2**: diff quality on your own eval set. Tune prompts where V4 differs materially.
3. **Week 3**: ramp to 50%. Monitor latency, error rate, user-visible metrics.
4. **Week 4**: 100%, but keep an OpenAI fallback client for multi-vendor resilience.

**Don't do a hard cutover.** Every migration has surprises.
