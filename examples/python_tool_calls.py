"""
Function / tool calling with DeepSeek V4 — OpenAI-compatible format.

  pip install openai
  export DEEPSEEK_API_KEY=sk-...
  python python_tool_calls.py
"""
import json
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. 'Tokyo'"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["city"],
            },
        },
    }
]


def fake_weather(city: str, unit: str = "celsius") -> dict:
    return {"city": city, "unit": unit, "temp": 22, "condition": "clear"}


messages = [{"role": "user", "content": "What's the weather in Tokyo in celsius?"}]

# Round 1: model decides to call the tool.
first = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    tools=tools,
)

assistant_msg = first.choices[0].message
messages.append(assistant_msg.model_dump(exclude_none=True))

# Execute each tool call the model requested.
for call in assistant_msg.tool_calls or []:
    args = json.loads(call.function.arguments)
    result = fake_weather(**args)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(result),
        }
    )

# Round 2: model reads tool results and produces the final answer.
final = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    tools=tools,
)
print(final.choices[0].message.content)
