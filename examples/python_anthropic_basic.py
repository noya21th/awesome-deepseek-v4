"""
Minimal Anthropic-SDK example hitting DeepSeek V4.

  pip install anthropic
  export DEEPSEEK_API_KEY=sk-...
  python python_anthropic_basic.py
"""
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/anthropic",
)

msg = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Give me three counterintuitive facts about the oceans."},
    ],
)

print(msg.content[0].text)
print("---")
print(f"tokens: in={msg.usage.input_tokens}, out={msg.usage.output_tokens}")
