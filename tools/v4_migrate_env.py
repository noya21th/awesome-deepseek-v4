#!/usr/bin/env python3
"""
v4-migrate-env — scan a codebase for OpenAI / Anthropic SDK config and propose
migration to DeepSeek V4.

  python v4_migrate_env.py PATH                 # dry-run (default)
  python v4_migrate_env.py PATH --apply         # actually write changes
  python v4_migrate_env.py PATH --target flash  # migrate to V4-Flash instead of Pro

Scans .py / .ts / .tsx / .js / .mjs / .env files. Skips .git, node_modules,
virtualenvs, build dirs.
"""
from __future__ import annotations
import argparse, os, re, sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__",
             ".venv", "venv", "env", ".next", ".turbo"}
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".mjs", ".jsx"}
ENV_NAMES = {".env", ".env.local", ".env.development", ".env.production"}

def replacements(target_model: str) -> list[tuple[re.Pattern, str, str]]:
    # (pattern, replacement, human description)
    dsv4_base_openai = "https://api.deepseek.com/v1"
    dsv4_base_anthropic = "https://api.deepseek.com/anthropic"
    return [
        # OpenAI base URL
        (re.compile(r'"https://api\.openai\.com/v1/?"'),
         f'"{dsv4_base_openai}"',
         "OpenAI base URL → DeepSeek OpenAI-compatible endpoint"),
        (re.compile(r"'https://api\.openai\.com/v1/?'"),
         f"'{dsv4_base_openai}'",
         "OpenAI base URL → DeepSeek OpenAI-compatible endpoint"),
        # Anthropic base URL
        (re.compile(r'"https://api\.anthropic\.com/?"'),
         f'"{dsv4_base_anthropic}"',
         "Anthropic base URL → DeepSeek Anthropic-compatible endpoint"),
        # OpenAI model names
        (re.compile(r'(["\'])gpt-5\.?4(?:-\w+)?\1'),
         rf'\1{target_model}\1',
         f"gpt-5.4 → {target_model}"),
        (re.compile(r'(["\'])gpt-5-nano\1'),
         rf'\1deepseek-v4-flash\1',
         "gpt-5-nano → deepseek-v4-flash"),
        (re.compile(r'(["\'])gpt-5-mini\1'),
         rf'\1deepseek-v4-flash\1',
         "gpt-5-mini → deepseek-v4-flash"),
        # Claude model names
        (re.compile(r'(["\'])claude-opus-4-6(?:-\w+)?\1'),
         rf'\1{target_model}\1',
         f"claude-opus-4-6 → {target_model}"),
        (re.compile(r'(["\'])claude-sonnet-4-6(?:-\w+)?\1'),
         rf'\1{target_model}\1',
         f"claude-sonnet-4-6 → {target_model}"),
        (re.compile(r'(["\'])claude-haiku-4-6(?:-\w+)?\1'),
         rf'\1deepseek-v4-flash\1',
         "claude-haiku-4-6 → deepseek-v4-flash"),
        # env var names (ambiguous — just flag, don't rewrite)
    ]

ENV_FLAGS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OPENAI_BASE_URL",
    "ANTHROPIC_BASE_URL",
]

def walk(root: Path):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            p = Path(dp) / fn
            if p.suffix in CODE_EXTS or p.name in ENV_NAMES:
                yield p

def process_file(p: Path, rules: list[tuple[re.Pattern, str, str]], apply: bool):
    try:
        text = p.read_text()
    except (UnicodeDecodeError, PermissionError):
        return None
    original = text
    hits: list[str] = []
    for pat, repl, desc in rules:
        def _sub(m: re.Match) -> str:
            hits.append(f"  • {desc}: {m.group(0)!r}")
            return pat.sub(repl, m.group(0))
        text = pat.sub(_sub, text)
    # Also flag env var usage without rewriting (key names must stay set by user)
    if p.name in ENV_NAMES:
        for flag in ENV_FLAGS:
            if re.search(rf"^\s*{flag}\s*=", text, re.MULTILINE):
                hits.append(f"  ⚠ {p}: {flag} detected — set DEEPSEEK_API_KEY instead "
                            f"(keep the {flag} line if you want fallback)")
    if hits and text != original and apply:
        p.write_text(text)
    return hits if hits else None

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="Directory to scan.")
    ap.add_argument("--apply", action="store_true",
                    help="Actually write changes. Default is dry-run.")
    ap.add_argument("--target", choices=["pro", "flash"], default="pro",
                    help="Which V4 tier to target (default: pro).")
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if not root.exists(): sys.exit(f"Path not found: {root}")

    target_model = "deepseek-v4-pro" if args.target == "pro" else "deepseek-v4-flash"
    rules = replacements(target_model)

    total_files = total_hits = 0
    for p in walk(root):
        hits = process_file(p, rules, apply=args.apply)
        if hits:
            print(f"\n{p.relative_to(root)}")
            for h in hits: print(h)
            total_files += 1
            total_hits += len(hits)

    print(f"\n---\n{total_hits} change(s) in {total_files} file(s). "
          f"{'APPLIED.' if args.apply else 'DRY RUN — rerun with --apply to write.'}")

if __name__ == "__main__":
    main()
