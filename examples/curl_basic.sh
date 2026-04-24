#!/usr/bin/env bash
# Raw HTTP example — no SDK required.
#
#   export DEEPSEEK_API_KEY=sk-...
#   bash curl_basic.sh
set -euo pipefail

: "${DEEPSEEK_API_KEY:?export DEEPSEEK_API_KEY=sk-... first}"

curl -sS https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [
      {"role": "system", "content": "You answer in one sentence."},
      {"role": "user", "content": "Why is the sky blue?"}
    ],
    "temperature": 1.0,
    "top_p": 1.0
  }' | python3 -m json.tool
