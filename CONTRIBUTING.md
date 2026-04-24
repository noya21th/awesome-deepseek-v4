# Contributing

Thank you for wanting to make this repo better. Contributions of all sizes are welcome — especially from people who are not native English speakers.

---

## The four kinds of contribution we need most

1. **Corrections.** Find a wrong number, a broken link, an outdated quote, a sentence that overclaims? Open a PR. Small PRs are great.
2. **Translations.** Native-speaker review of the Arabic, Hindi, Japanese, German, French, and Chinese pages. The initial translations were drafted carefully but will read awkwardly to native speakers in places.
3. **Benchmark reproductions.** Ran your own eval of V4 on MMLU-Pro, SWE-Bench, a custom dataset? Add your numbers + the exact harness config to [`docs/benchmarks-community.md`](./docs/).
4. **Community tools.** Shipped something that works with V4 (a fine-tune, an integration, a wrapper, a useful blog post)? PR it into [`resources/awesome-community.md`](./resources/awesome-community.md).

---

## What we will NOT merge

- **Unsourced claims.** Every factual assertion must cite a primary source.
- **Overhyping.** "V4 DESTROYS CLAUDE" does not fly. We value credibility more than engagement.
- **Undisclosed affiliations.** If you work for a vendor, disclose it in the PR.
- **Link-spam to paid courses** or wrappers that add no value.
- **Politicized content** on topics unrelated to V4's technical and commercial profile.
- **AI-generated slop** that wasn't read by a human author.

---

## Style guide

- **Tone**: professional, concise, honest. No emoji spam. No hype words ("revolutionary", "game-changing").
- **Numbers**: always cite the source inline.
- **Links**: prefer stable primary sources (Hugging Face, arXiv, official vendor docs) over blogs where possible.
- **Hedging**: say "as of 2026-04-25" when making dated claims. Reality moves fast.
- **Markdown**: GitHub-flavored, fenced code blocks with language hint, tables over prose where tabular data fits.

---

## PR workflow

1. Fork the repo.
2. Create a branch: `git checkout -b fix/broken-link-in-faq` (conventional naming helps reviewers).
3. Make your change.
4. Run `make check` if we have a check pipeline set up (coming soon).
5. Open a PR with a title that matches `fix: …`, `docs: …`, `i18n: …`, `feat: …`, etc.
6. In the PR body, link the primary source(s) for any factual change.
7. Be patient — maintainers review in good faith but asynchronously.

---

## Translation guidelines

If you're contributing to an `i18n/<lang>/` page:

- **Read the whole English README first.** The structure, section order, and source links should match.
- **Localize examples** where appropriate (e.g., use a locally famous math problem instead of √2 if that reads better).
- **Do NOT translate code, CLI commands, file paths, or model identifiers.**
- **Be careful with numbers and units.** Keep the same numeric values; localize separators per language conventions.
- **Right-to-left languages** (Arabic) should use `<div dir="rtl">` blocks where GitHub's markdown renderer respects it.
- **Credit yourself** in a comment at the top of the file if you want, or stay anonymous — both fine.

---

## Adding to the community tools list

To add a project to [`resources/awesome-community.md`](./resources/awesome-community.md), the project must:

- Actually work with V4 (not just have "V4 support planned").
- Be open-source OR have transparent pricing.
- Add genuine value over the base API.

Submit PRs with:
- Project name (linked)
- One-sentence description
- Link to working docs or a runnable repo

---

## Conduct

See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md). Short version: be kind, assume good faith, keep it about the work.

---

## Licensing your contribution

By opening a PR, you agree to release your contribution under this repository's [MIT License](./LICENSE).

If you're copying text from another source (blog, paper, vendor docs), make sure the license permits it and **cite the source**. When in doubt, paraphrase and link.

---

## Recognition

All contributors will be listed in `CONTRIBUTORS.md` (coming soon). Significant translators may be credited at the top of their respective `i18n/<lang>/README.md`.

Thank you. This repo is useful because the community makes it so.
