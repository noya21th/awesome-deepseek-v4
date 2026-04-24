#!/usr/bin/env python3
"""
v4-repo-review — pack a repository's source into V4-Pro and get a structured
code-review report.

  python v4_repo_review.py /path/to/repo
  python v4_repo_review.py . --focus security
  python v4_repo_review.py . --max-bytes 800000 --model deepseek-v4-flash

Required: pip install openai
Env: DEEPSEEK_API_KEY
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__",
             ".venv", "venv", "env", ".next", ".turbo", "target"}
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".mjs", ".jsx", ".go", ".rs",
             ".java", ".kt", ".rb", ".php", ".c", ".h", ".cpp", ".hpp",
             ".cs", ".swift", ".scala", ".sql", ".md"}
SIZE_LIMIT_PER_FILE = 200_000  # bytes — skip enormous generated files

FOCUS_PROMPTS = {
    "correctness": "Focus on bugs, logic errors, race conditions, and correctness failures.",
    "security":    "Focus on security issues: injection, auth, secrets, input validation, crypto misuse.",
    "performance": "Focus on performance: hot loops, N+1 queries, blocking I/O, memory growth.",
    "maintainability": "Focus on maintainability: coupling, naming, dead code, architecture.",
    "all":         "Cover correctness, security, performance, and maintainability. Ignore style.",
}

def walk_repo(root: Path):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in sorted(fns):
            p = Path(dp) / fn
            if p.suffix in CODE_EXTS and p.stat().st_size < SIZE_LIMIT_PER_FILE:
                yield p

def pack(root: Path, max_bytes: int) -> tuple[str, list[Path]]:
    buf = []
    used = 0
    packed_files = []
    for p in walk_repo(root):
        try:
            content = p.read_text(errors="ignore")
        except PermissionError:
            continue
        chunk = f"\n\n===== {p.relative_to(root)} =====\n{content}"
        if used + len(chunk) > max_bytes:
            break
        buf.append(chunk)
        used += len(chunk)
        packed_files.append(p)
    return "".join(buf), packed_files

def review(repo_text: str, focus: str, model: str, api_key: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai package is required: pip install openai")
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    system = (
        "You are a senior engineer doing a pull-request review. "
        f"{FOCUS_PROMPTS[focus]} "
        "Output a markdown report with issues grouped by severity "
        "(Critical / Major / Minor). For each issue give: file:line, "
        "1–2 sentence rationale, and a concrete suggested fix. "
        "Do not comment on style. Be concise."
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Review this repository:\n{repo_text}"},
        ],
        extra_body={"thinking": {"type": "enabled"}},
    )
    return resp.choices[0].message.content or ""

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="Repository root.")
    ap.add_argument("--focus", choices=list(FOCUS_PROMPTS), default="all")
    ap.add_argument("--model", default="deepseek-v4-pro")
    ap.add_argument("--max-bytes", type=int, default=800_000,
                    help="Approx max chars to send to the model (default 800K ~= 200K tokens).")
    ap.add_argument("-o", "--output", help="Write report to this file in addition to stdout.")
    args = ap.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key: sys.exit("Set DEEPSEEK_API_KEY")

    root = Path(args.path).resolve()
    if not root.is_dir(): sys.exit(f"Not a directory: {root}")

    print(f"Packing {root}…", file=sys.stderr)
    text, files = pack(root, args.max_bytes)
    print(f"Packed {len(files)} files, {len(text):,} chars. Calling {args.model}…",
          file=sys.stderr)

    report = review(text, args.focus, args.model, api_key)
    print(report)
    if args.output:
        Path(args.output).write_text(report)
        print(f"\n[Report also saved to {args.output}]", file=sys.stderr)

if __name__ == "__main__":
    main()
