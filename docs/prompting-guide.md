# Prompting V4 — what works, what doesn't

Opinionated, practical guidance for getting the best out of V4. Based on the model card's own recommendations, the technical report's training recipe, and observed community practice.

---

## Defaults you should almost always use

```python
temperature = 1.0
top_p       = 1.0
```

Source: V4-Pro model card. V4 was tuned for these values. Lowering temperature often *hurts* quality on reasoning tasks, because the RL post-training was done at T=1.0.

---

## Thinking vs Non-Thinking — when to flip the switch

Rule of thumb:

| Task type | Recommended mode |
|---|---|
| Math, formal proof, olympiad problems | **Thinking** (always) |
| Competitive coding, complex debugging | **Thinking** |
| Multi-step planning, agent reasoning | **Thinking** |
| Factual Q&A, short summaries | Non-Thinking |
| Chat-style customer support | Non-Thinking |
| High-volume batch classification | Non-Thinking |
| Latency-critical UX (< 1s TTFT) | Non-Thinking |

**Cost note:** Thinking mode tokens count as output tokens. On V4-Pro ($3.48/Mtok output), a verbose Thinking trace can add meaningfully to cost on simple tasks — save it for where it earns its keep.

**For Thinking-Max (hardest reasoning):** set `max_tokens` or context budget to ≥ **384K**, per the model card. Deep reasoning sometimes produces very long traces.

---

## System prompt style that works well

V4 responds well to **explicit structure**. Prompts that leave intent implicit (common with Claude) sometimes get flatter outputs.

**Good**:
```
Role: Senior backend engineer reviewing a pull request.
Goal: Produce a code review comment focused on correctness and security. Ignore style.
Format: Markdown with severity (critical/major/minor), file:line, and a one-sentence rationale per issue.
Constraints: Cap total length at 400 words.
```

**Less good** (for V4):
```
You are a helpful code reviewer.
```

This is not a V4 weakness — it's a stylistic difference versus Claude-4.x, which tolerates terse system prompts exceptionally well. GPT-style prompting transfers to V4 cleanly.

---

## Tool use / function calling

V4 supports OpenAI-style `tools`. Practical guidance:

- **Fewer, well-described tools beat many thin ones.** A 3-tool agent with rich parameter descriptions out-performs a 15-tool agent with one-word descriptions.
- **Model the final answer as a tool, too,** for strict agent loops. It prevents the model from trying to answer mid-loop with commentary.
- **V4 respects tool schemas tightly.** If your schema is wrong, you'll get schema-conforming garbage. Validate schemas before production.

---

## JSON output

For structured outputs, pick in this order:

1. **Dedicated `response_format={"type": "json_object"}`** — cleanest.
2. **Tool calling with a single "return_result" tool** that has a tight JSON schema — most reliable for complex shapes.
3. **Pure prompt "respond with JSON"** — only as a fallback; works but brittle at the margins.

---

## Long-context prompts — do this, not that

At 1M context V4 is capable, but the technical report is explicit that **retrieval accuracy degrades above 128K**. Patterns that work:

- **Put the instruction / question at the end**, not buried in the middle. Models attend more reliably to the end.
- **Chunk logically** — section headers and clear boundaries help the model navigate.
- **For RAG**, don't stuff 1M tokens of retrieved context just because you can. Retrieve precisely, then submit 20–50K of well-chosen context.
- **If you need robust retrieval at depth**, layer a real retriever (BM25, dense, hybrid) on top of V4 rather than relying on pure long-context.

---

## Chain-of-thought: V4 already does this in Thinking mode — don't double up

Explicit "Let's think step by step" prompting was useful on older models. On V4 Thinking mode, **the model already emits an internal reasoning trace**. Adding "think step by step" in the prompt often produces worse outputs than trusting the native Thinking mode.

For Non-Thinking mode, classic CoT prompting still helps.

---

## Multilingual prompting

V4's multilingual performance is strong but uneven across languages. Practical notes:

- **English, Simplified Chinese, French, Spanish, German, Japanese**: expect near-English quality.
- **Arabic, Hindi, Russian, Korean**: solid but occasional calquing.
- **Lower-resource languages**: reliability varies — test.

For the non-English content on this repo (Arabic RTL, Hindi, etc.), we recommend validating model output with native speakers for customer-facing use.

---

## Refusals and safety

V4's refusal profile differs from Claude and GPT:

- It is **more willing to attempt "controversial" technical questions** (security, biology, chemistry at an educational level) than Claude.
- It is **more likely to decline or redirect on certain political topics**, particularly those sensitive in the PRC.
- Refusal text is generally less verbose than Claude's.

For production use, have an eval set that tests refusal behavior on *your* edge cases — every model has surprises.

---

## Common mistakes we see

1. **Turning temperature down to 0.2 "for consistency."** Hurts quality on reasoning. Keep it at 1.0 and seed / retry if you need determinism.
2. **Using a generic chat template instead of `encoding_dsv4`.** Breaks Thinking mode. Always use the official helper.
3. **Setting `max_tokens` too low for Thinking.** Truncates the reasoning trace and produces garbage final answers. Budget generously.
4. **Assuming OpenAI prompt engineering transfers 1:1.** Mostly it does, but V4 benefits from *more* explicit structure than GPT-5.x.
5. **Using V4-Pro Thinking for simple classification.** You're burning output tokens. Flash + Non-Thinking is usually the right default for high-volume simple tasks.

---

## If you take away one thing

**V4 is an excellent model with specific defaults** (T=1.0, Top-P=1.0, `encoding_dsv4`, mode-explicit). Use them. Don't port arbitrary hyperparameters from another model family.
