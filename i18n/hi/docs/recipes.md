# रेसिपी — V4 के साथ असली काम करने के पैटर्न

10 कॉपी-पेस्ट करके चलने योग्य वर्कफ़्लो। हर रेसिपी में **क्या**, **V4 क्यों**, **न्यूनतम कोड**, **आम लागत**।

*सारे कोड मान लेते हैं कि `export DEEPSEEK_API_KEY=sk-...` सेट है।*

---

## रेसिपी 1 — पूरी रिपॉज़िटरी की कोड रिव्यू

**क्या**: पूरी रिपो V4-Pro को दें और संरचित PR-स्तर रिव्यू रिपोर्ट पाएँ।

**V4 क्यों**: 1M कॉन्टेक्स्ट + SOTA कोड बेंचमार्क (LiveCodeBench 93.5) + $3.48/Mtok आउटपुट। Claude Opus पर 20× महंगा, और 200K कॉन्टेक्स्ट चंकिंग मजबूर करता है — जो क्रॉस-फ़ाइल रीज़निंग नष्ट कर देता है।

```python
import os, pathlib
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

SKIP = {".git", "node_modules", "dist", "build", "__pycache__", ".venv"}
EXTS = {".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java", ".md"}

def pack_repo(root: str) -> str:
    parts = []
    for p in pathlib.Path(root).rglob("*"):
        if any(s in p.parts for s in SKIP): continue
        if p.is_file() and p.suffix in EXTS and p.stat().st_size < 200_000:
            parts.append(f"\n\n===== {p} =====\n{p.read_text(errors='ignore')}")
    return "".join(parts)

resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content":
         "You are a senior engineer doing a pull-request review. Produce a "
         "markdown report with severity (critical/major/minor), file:line, "
         "rationale. Focus on correctness, security, concurrency. Ignore style."},
        {"role": "user", "content": f"Review this repository:\n{pack_repo('.')}"},
    ],
    extra_body={"thinking": {"type": "enabled"}},
)
print(resp.choices[0].message.content)
```

**लागत**: 500K टोकन रिपो की रिव्यू ≈ **$1–3** (V4-Pro)। वही काम Opus पर: $30–50।

---

## रेसिपी 2 — लंबे दस्तावेज़ पर Q&A (सटीकता चेतावनी के साथ)

**क्या**: 200 पेज के अनुबंध, मेडिकल रिकॉर्ड, शोध पत्र पर प्रश्नों का उत्तर।

**V4 क्यों**: V3.2 के 27% FLOPs में 1M कॉन्टेक्स्ट। लेकिन तकनीकी रिपोर्ट स्पष्ट करती है: **128K के ऊपर retrieval सटीकता घटती है** — हल्के retrieval के साथ जोड़ें।

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def qa(doc: str, question: str) -> str:
    # अगर डॉक < 128K tokens है तो सीधे भेजें; बड़ा हो तो BM25 से top 100K निकालें
    resp = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "केवल दिए गए दस्तावेज़ से उत्तर दें। यदि उत्तर दस्तावेज़ में नहीं है तो कहें। "
             "संभव हो तो अनुभाग/पेज का उद्धरण दें।"},
            {"role": "user", "content": f"दस्तावेज़:\n{doc}\n\nप्रश्न: {question}"},
        ],
    )
    return resp.choices[0].message.content
```

**लागत**: 100K दस्तावेज़ + 1 प्रश्न ≈ **$0.18** (Pro) / **$0.015** (Flash)।

**Flash या Pro**: Flash निष्कर्षणात्मक ("समाप्ति क्लॉज क्या है?") के लिए; Pro अनुमान-आधारित ("क्या यह अनुबंध IP जोखिम लाता है?") के लिए।

---

## रेसिपी 3 — कोडिंग एजेंट (मल्टी-टर्न + टूल्स)

**क्या**: मल्टी-टर्न एजेंट जो फ़ाइलें पढ़ सकता है, कमांड चला सकता है, कार्य पूरा होने तक iterate करता है।

**V4 क्यों**: Codeforces 3206 + native `tools` स्कीमा + 1M कॉन्टेक्स्ट लंबे टूल कॉल इतिहास को बिना eviction के रखता है।

```python
import json, os, subprocess
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "फ़ाइल की सामग्री पढ़ें।",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "shell कमांड चलाएँ, stdout/stderr लौटाएँ।",
        "parameters": {"type": "object",
                       "properties": {"cmd": {"type": "string"}},
                       "required": ["cmd"]}}},
]

def handle(name, args):
    if name == "read_file": return open(args["path"]).read()
    if name == "run_shell":
        r = subprocess.run(args["cmd"], shell=True, capture_output=True, text=True)
        return f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"

messages = [
    {"role": "system", "content": "तुम कोडिंग एजेंट हो। टूल्स से रिपो की जाँच करो और कार्य पूरा करो।"},
    {"role": "user", "content": "सिंटैक्स त्रुटियों वाली सभी Python फ़ाइलें खोजकर ठीक करें।"},
]

for _ in range(20):
    r = client.chat.completions.create(
        model="deepseek-v4-pro", messages=messages, tools=tools,
        extra_body={"thinking": {"type": "enabled"}},
    )
    msg = r.choices[0].message
    messages.append(msg.model_dump(exclude_none=True))
    if not msg.tool_calls:
        print(msg.content); break
    for c in msg.tool_calls:
        out = handle(c.function.name, json.loads(c.function.arguments))
        messages.append({"role": "tool", "tool_call_id": c.id, "content": out})
```

**लागत**: 20 टर्न, ~10K टोकन इतिहास ≈ **$0.10–0.30** / सत्र।

---

## रेसिपी 4 — हाई-वॉल्यूम बैच पाइपलाइन

**क्या**: प्रति दिन मिलियन टोकन स्केल पर अनुवाद, वर्गीकरण, एनरिचमेंट, सिंथेटिक जनरेशन।

**V4-Flash क्यों**: $0.14/$0.28 प्रति Mtok near-frontier क्वालिटी में सबसे सस्ता। GPT-5-Nano से भी सस्ता।

```python
import os, asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                    base_url="https://api.deepseek.com/v1")

async def translate(text: str) -> str:
    r = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": "जापानी में अनुवाद करें। केवल अनुवाद आउटपुट करें।"},
                  {"role": "user", "content": text}],
        extra_body={"thinking": {"type": "disabled"}},
    )
    return r.choices[0].message.content

async def run(texts, concurrency=32):
    sem = asyncio.Semaphore(concurrency)
    async def go(t):
        async with sem: return await translate(t)
    return await asyncio.gather(*(go(t) for t in texts))
```

**लागत**: 10,000 छोटे अनुवाद (~2M tokens) ≈ **$0.30–0.60** (V4-Flash)।

---

## रेसिपी 5 — गणित ट्यूटर / औपचारिक प्रमाण

**क्या**: पूर्ण रीज़निंग चेन के साथ ओलंपियाड स्तर के समाधान।

**V4 क्यों**: Putnam 2025 औपचारिक प्रमाण **120/120 परफ़ेक्ट**, HMMT 95.2, IMOAnswerBench 89.8।

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def solve(problem: str):
    r = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "तुम गणित ओलंपियाड कोच हो। पूरी रीज़निंग दिखाओ, फिर FINAL: <उत्तर> दो।"},
            {"role": "user", "content": problem},
        ],
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=32_000,
    )
    msg = r.choices[0].message
    return getattr(msg, "reasoning_content", "") or "", msg.content
```

**लागत**: प्रति ओलंपियाड समस्या **$0.05–0.20**।

---

## रेसिपी 6 — LiteLLM के साथ मल्टी-वेंडर फ़ॉलबैक

**क्या**: एक क्लाइंट जो V4, Claude, GPT को रूट करता है, त्रुटि/रेट लिमिट पर स्वचालित फ़ॉलबैक।

**V4 इसे संभव बनाता है**: V4 इतना सस्ता है कि 3-वेंडर फ़ॉलबैक रणनीति आख़िरकार आर्थिक रूप से व्यवहार्य है।

```python
# pip install litellm
import os
from litellm import Router

router = Router(model_list=[
    {"model_name": "smart",
     "litellm_params": {"model": "deepseek/deepseek-v4-pro",
                        "api_key": os.environ["DEEPSEEK_API_KEY"],
                        "api_base": "https://api.deepseek.com/v1"}},
    {"model_name": "smart",
     "litellm_params": {"model": "claude-opus-4-6",
                        "api_key": os.environ.get("ANTHROPIC_API_KEY")}},
    {"model_name": "smart",
     "litellm_params": {"model": "gpt-5.4",
                        "api_key": os.environ.get("OPENAI_API_KEY")}},
], fallbacks=[{"smart": ["smart"]}])

resp = router.completion(
    model="smart",
    messages=[{"role": "user", "content": "EU AI Act को 5 बिंदुओं में summarize करें।"}],
)
print(resp.choices[0].message.content)
```

**लागत**: 95%+ ट्रैफ़िक V4-Pro पर (समूह में सबसे सस्ता)।

---

## रेसिपी 7 — vLLM के साथ V4 सेल्फ-होस्ट + OpenAI क्लाइंट

**क्या**: अपने नेटवर्क में V4-Flash चलाएँ, OpenAI-संगत endpoint के रूप में expose करें।

**V4 क्यों**: इस गुणवत्ता स्तर पर एकमात्र open-weight मॉडल। HIPAA, SOC2, सरकारी जैसी नियामक आवश्यकताओं के लिए।

```bash
# सर्वर: 8× H100 80GB या 8× H200
pip install "vllm>=0.10"

python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --tensor-parallel-size 8 \
  --max-model-len 1048576 \
  --quantization fp8 \
  --trust-remote-code \
  --port 8000
```

**स्केल पर लागत**: आरक्षित 8× H200 पर सेल्फ-होस्ट V4-Flash, >70% उपयोगिता ≈ **$0.10–0.30 / Mtok आउटपुट**। 5B+ tokens/महीना पर आधिकारिक API से सस्ता।

---

## रेसिपी 8 — Aider (टर्मिनल पेयर प्रोग्रामर) + V4

Aider एक टर्मिनल AI पेयर प्रोग्रामर है जो परिवर्तनों को git commit के रूप में सहेजता है। V4-Pro इसकी सबसे मज़बूत कोड बैकएंड है।

```bash
pip install aider-chat
export DEEPSEEK_API_KEY=sk-...
aider --model openai/deepseek-v4-pro \
      --openai-api-base https://api.deepseek.com/v1 \
      --openai-api-key $DEEPSEEK_API_KEY
```

Aider में:
```
> /add src/auth.py src/session.py
> इन दोनों फ़ाइलों को refactor करें कि sessions Redis में जाएँ, memory में नहीं
```

**लागत**: आम 2–3 घंटे सत्र, मध्यम संपादन ≈ **$1–5** (V4-Pro)।

---

## रेसिपी 9 — Cline (VS Code एजेंट) + V4

[Cline](https://github.com/cline/cline) एक VS Code एक्सटेंशन है जो एडिटर को tool-using एजेंट बनाता है।

Cline सेटिंग्स:
- **API Provider**: OpenAI Compatible
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key**: आपकी DeepSeek key
- **Model ID**: `deepseek-v4-pro`

**लागत**: जटिल कार्य प्रति ≈ **$0.20–1.00**।

---

## रेसिपी 10 — छोटे मॉडल के fine-tune के लिए सिंथेटिक डेटा

**क्या**: V4-Flash से उच्च-गुणवत्ता प्रशिक्षण डेटा जनरेट करें, फिर छोटे स्टूडेंट मॉडल को खुद fine-tune करें।

**V4 क्यों**: $0.28/Mtok आउटपुट पर, 100M tokens सिंथेटिक डेटा की लागत **$28**। तीन साल पहले यह $30K+ का काम था।

```python
import os, json
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def gen(seed: str) -> dict:
    r = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content":
             "एक उच्च-गुणवत्ता SFT उदाहरण generate करें। JSON output: "
             "{\"user\": ..., \"assistant\": ...}"},
            {"role": "user", "content": f"विषय seed: {seed}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)
```

---

## लागत चीट शीट

| वर्कलोड | मॉडल | आम लागत |
|---|---|---|
| पूरी रिपो रिव्यू (500K tok) | V4-Pro | $1–3 |
| लंबे दस्तावेज़ Q&A (100K + Q) | V4-Pro | ~$0.18 |
| लंबे दस्तावेज़ Q&A (100K + Q) | V4-Flash | ~$0.015 |
| 20-टर्न एजेंट | V4-Pro | $0.10–0.30 |
| 10K बैच अनुवाद | V4-Flash | $0.30–0.60 |
| ओलंपियाड समस्या | V4-Pro | $0.05–0.20 |
| 2 घंटे Aider सत्र | V4-Pro | $1–5 |
| 100M टोकन सिंथेटिक डेटा | V4-Flash | ~$28 |

---

## 6 स्वर्णिम नियम

1. **Temperature = 1.0, Top-P = 1.0** — V4 इन्हीं मानों पर tune हुआ है।
2. **Thinking ON**: गणित/कोड/योजना/मल्टी-स्टेप; **OFF**: चैट/वर्गीकरण/बैच।
3. **वॉल्यूम के लिए Flash, गुणवत्ता के लिए Pro** — उत्पादन में दोनों रूट करें।
4. **128K के ऊपर 1M कॉन्टेक्स्ट में सटीक retrieval के लिए भरोसा न करें** — retriever जोड़ें।
5. **लंबे system prompts कैश करें** — V4 समर्थन करता है।
6. **LiteLLM के माध्यम से OpenAI/Claude fallback बनाए रखें** — मल्टी-वेंडर resilience अब सस्ती है।

---

अपनी रेसिपी PR द्वारा सबमिट करें — [CONTRIBUTING.md](../../../CONTRIBUTING.md) देखें।
