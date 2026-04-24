"""
Thinking mode on V4-Pro — shows how to request extended reasoning.

  pip install openai
  export DEEPSEEK_API_KEY=sk-...
  python python_thinking_mode.py
"""
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
)

# The exact `extra_body` key for Thinking mode may evolve. Confirm against
# https://api-docs.deepseek.com/ before production use.
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {
            "role": "user",
            "content": (
                "Prove that the sum of the first n odd positive integers is n^2. "
                "Then give one reason this is beautiful."
            ),
        },
    ],
    extra_body={"thinking": {"type": "enabled"}},
)

choice = resp.choices[0].message

# Some deployments expose the reasoning trace as `reasoning_content`; others
# inline it as a <thinking>...</thinking> block in `content`.
if hasattr(choice, "reasoning_content") and choice.reasoning_content:
    print("=== thinking ===")
    print(choice.reasoning_content)
    print("=== answer ===")

print(choice.content)
