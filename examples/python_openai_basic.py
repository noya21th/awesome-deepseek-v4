"""
Minimal OpenAI-SDK example hitting DeepSeek V4.

  pip install openai
  export DEEPSEEK_API_KEY=sk-...
  python python_openai_basic.py
"""
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
)

resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "You are a careful assistant. Cite sources when you can."},
        {"role": "user", "content": "Give me three counterintuitive facts about the oceans."},
    ],
    temperature=1.0,
    top_p=1.0,
)

print(resp.choices[0].message.content)
print("---")
print(f"tokens: in={resp.usage.prompt_tokens}, out={resp.usage.completion_tokens}")
