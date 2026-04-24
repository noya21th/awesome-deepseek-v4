#!/usr/bin/env python3
"""
v4-cost-calc — estimate monthly LLM spend across V4 and closed-frontier models.

Usage:
  python v4_cost_calc.py --input 5M --output 2M
  python v4_cost_calc.py --input 5000000 --output 2000000 --requests 10000
  python v4_cost_calc.py --from-openai-csv usage.csv

Numbers with suffix K/M/B are parsed (5M = 5_000_000).
All prices in USD per 1M tokens. Closed-model prices are public list prices —
verify with each vendor before signing contracts.
"""
from __future__ import annotations
import argparse, csv, sys
from dataclasses import dataclass

# $/Mtok — (input, output). Closed figures are approximate public list prices.
PRICES = {
    "DeepSeek V4-Flash":  (0.14, 0.28),
    "DeepSeek V4-Pro":    (1.74, 3.48),
    "Claude Haiku 4.6":   (1.00, 5.00),
    "Claude Sonnet 4.6":  (3.00, 15.00),
    "Claude Opus 4.6":    (15.00, 75.00),
    "GPT-5-Nano":         (0.10, 0.40),
    "GPT-5.4":            (2.50, 10.00),
    "Gemini 3.1-Pro":     (2.00, 8.00),
}

@dataclass
class Quote:
    name: str
    input_cost: float
    output_cost: float
    @property
    def total(self) -> float: return self.input_cost + self.output_cost

def parse_amount(s: str) -> int:
    s = s.strip().upper().replace(",", "").replace("_", "")
    mul = 1
    if s.endswith("K"): mul, s = 1_000, s[:-1]
    elif s.endswith("M"): mul, s = 1_000_000, s[:-1]
    elif s.endswith("B"): mul, s = 1_000_000_000, s[:-1]
    return int(float(s) * mul)

def quotes(in_tok: int, out_tok: int) -> list[Quote]:
    out = []
    for name, (p_in, p_out) in PRICES.items():
        out.append(Quote(name, in_tok / 1e6 * p_in, out_tok / 1e6 * p_out))
    return sorted(out, key=lambda q: q.total)

def render(qs: list[Quote], in_tok: int, out_tok: int) -> str:
    cheapest = qs[0].total
    rows = [("Model", "Input $", "Output $", "Total $", "× cheapest")]
    for q in qs:
        mul = q.total / cheapest if cheapest > 0 else 1.0
        rows.append((q.name, f"{q.input_cost:,.2f}", f"{q.output_cost:,.2f}",
                     f"{q.total:,.2f}", f"{mul:.1f}×"))
    widths = [max(len(r[i]) for r in rows) for i in range(5)]
    lines = []
    for i, r in enumerate(rows):
        lines.append(" | ".join(c.ljust(widths[j]) for j, c in enumerate(r)))
        if i == 0: lines.append("-+-".join("-" * w for w in widths))
    header = f"Monthly cost: {in_tok:,} input + {out_tok:,} output tokens"
    return header + "\n" + "=" * len(header) + "\n\n" + "\n".join(lines)

def read_openai_csv(path: str) -> tuple[int, int]:
    """Parse an OpenAI usage CSV (columns like n_context_tokens_total,
    n_generated_tokens_total). Returns total (in, out) summed."""
    total_in = total_out = 0
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        in_keys = [k for k in reader.fieldnames or [] if "context" in k.lower() or "input" in k.lower() or "prompt" in k.lower()]
        out_keys = [k for k in reader.fieldnames or [] if "generated" in k.lower() or "output" in k.lower() or "completion" in k.lower()]
        if not in_keys or not out_keys:
            sys.exit(f"Could not find input/output token columns in {path}. "
                     f"Found columns: {reader.fieldnames}")
        for row in reader:
            try: total_in += int(float(row[in_keys[0]] or 0))
            except: pass
            try: total_out += int(float(row[out_keys[0]] or 0))
            except: pass
    return total_in, total_out

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", help="Monthly input tokens (e.g. 5M, 500K).")
    p.add_argument("--output", help="Monthly output tokens.")
    p.add_argument("--from-openai-csv", metavar="PATH",
                   help="Parse an OpenAI-exported usage CSV instead.")
    args = p.parse_args()

    if args.from_openai_csv:
        in_tok, out_tok = read_openai_csv(args.from_openai_csv)
    elif args.input and args.output:
        in_tok, out_tok = parse_amount(args.input), parse_amount(args.output)
    else:
        p.print_help(); sys.exit(1)

    print(render(quotes(in_tok, out_tok), in_tok, out_tok))

if __name__ == "__main__":
    main()
