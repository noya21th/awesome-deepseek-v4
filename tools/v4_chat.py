#!/usr/bin/env python3
"""
v4-chat — minimal streaming terminal REPL for DeepSeek V4.

  python v4_chat.py                      # V4-Pro, Thinking mode
  python v4_chat.py --model flash        # V4-Flash
  python v4_chat.py --no-think           # Non-Thinking mode

In-REPL commands:
  /think on|off     toggle Thinking mode for the next turn
  /model pro|flash  switch model
  /clear            clear history
  /save PATH        save transcript to file
  /exit             quit

Required: pip install openai
Env: DEEPSEEK_API_KEY
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", choices=["pro", "flash"], default="pro")
    ap.add_argument("--no-think", action="store_true",
                    help="Start in Non-Thinking mode.")
    ap.add_argument("--system", default="You are a helpful, concise assistant.")
    args = ap.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key: sys.exit("Set DEEPSEEK_API_KEY")

    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai package is required: pip install openai")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    model = f"deepseek-v4-{args.model}"
    think = not args.no_think
    history = [{"role": "system", "content": args.system}]

    print(f"v4-chat · model={model} · thinking={'on' if think else 'off'}")
    print("Type /exit to quit. /think on|off. /model pro|flash. /clear. /save PATH.\n")

    while True:
        try:
            user = input("you ▸ ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not user: continue

        if user.startswith("/"):
            parts = user.split(None, 1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""
            if cmd == "/exit": break
            if cmd == "/clear":
                history = history[:1]; print("[history cleared]\n"); continue
            if cmd == "/think":
                think = arg.lower() != "off"
                print(f"[thinking = {'on' if think else 'off'}]\n"); continue
            if cmd == "/model":
                if arg in ("pro", "flash"):
                    model = f"deepseek-v4-{arg}"
                    print(f"[model = {model}]\n")
                else:
                    print("[usage: /model pro | /model flash]\n")
                continue
            if cmd == "/save":
                if not arg:
                    print("[usage: /save PATH]\n"); continue
                Path(arg).write_text(json.dumps(history, ensure_ascii=False, indent=2))
                print(f"[saved {len(history)} messages to {arg}]\n"); continue
            print(f"[unknown command: {cmd}]\n"); continue

        history.append({"role": "user", "content": user})
        print("v4  ▸ ", end="", flush=True)
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=history,
                stream=True,
                extra_body={"thinking": {"type": "enabled" if think else "disabled"}},
            )
            pieces = []
            for chunk in stream:
                if not chunk.choices: continue
                delta = chunk.choices[0].delta.content or ""
                pieces.append(delta)
                sys.stdout.write(delta); sys.stdout.flush()
            print("\n")
            history.append({"role": "assistant", "content": "".join(pieces)})
        except KeyboardInterrupt:
            print("\n[interrupted]\n")
        except Exception as e:
            print(f"\n[error: {e}]\n")

if __name__ == "__main__":
    main()
