# الوصفات — أنماط عملية للعمل مع V4

<div dir="rtl">

10 أنماط سير عمل جاهزة للنسخ واللصق. كل وصفة: **ماذا**، **لماذا V4**، **الحد الأدنى من الكود**، **التكلفة النموذجية**.

*يفترض الكود `export DEEPSEEK_API_KEY=sk-...`*

---

## الوصفة 1 — مراجعة كود لمستودع كامل

**ماذا**: تمرير مستودع كامل إلى V4-Pro والحصول على تقرير مراجعة بصيغة PR.

**لماذا V4**: سياق 1M + أفضل معايير كود (LiveCodeBench 93.5) + 3.48 $/مليون رمز للخرج. Claude Opus أغلى 20×، وسياق 200K يفرض التقطيع — مما يدمر الاستدلال عبر الملفات.

</div>

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

<div dir="rtl">

**التكلفة**: مستودع 500K رمز ≈ **1–3 $** (V4-Pro). نفس المهمة على Opus: 30–50 $.

---

## الوصفة 2 — أسئلة وأجوبة على مستند طويل

**ماذا**: الإجابة عن أسئلة في عقد من 200 صفحة، أو سجل طبي، أو ورقة بحثية.

**لماذا V4**: سياق 1M بـ 27% من FLOPs الخاصة بـ V3.2. لكن التقرير التقني يذكر أن **دقة الاسترجاع تنخفض فوق 128K** — نجمعها مع استرجاع خفيف.

</div>

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

def qa(doc: str, question: str) -> str:
    # إذا كان المستند < 128K رمز، أدخله مباشرة؛ وإلا استخرج أول 100K بواسطة BM25
    resp = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":
             "أجب حصرًا من المستند المقدم. إن لم تكن الإجابة موجودة فقل ذلك. "
             "استشهد بالقسم/الصفحة إن أمكن."},
            {"role": "user", "content": f"المستند:\n{doc}\n\nالسؤال: {question}"},
        ],
    )
    return resp.choices[0].message.content
```

<div dir="rtl">

**التكلفة**: مستند 100K رمز + سؤال ≈ **0.18 $** (Pro) / **0.015 $** (Flash).

**Flash أم Pro**: Flash للأسئلة الاستخراجية، Pro للأسئلة الاستنتاجية.

---

## الوصفة 3 — وكيل برمجي (متعدد الجولات + أدوات)

**ماذا**: وكيل يقرأ الملفات، ينفذ الأوامر، ويكرر حتى إنجاز المهمة.

**لماذا V4**: Codeforces 3206 + تنسيق `tools` الأصلي + سياق 1M يستوعب التاريخ الطويل.

</div>

```python
import json, os, subprocess
from openai import OpenAI
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com/v1")

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "قراءة محتوى الملف.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "تنفيذ أمر shell، إرجاع stdout/stderr.",
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
    {"role": "system", "content": "أنت وكيل برمجي. استخدم الأدوات للبحث وإنجاز المهمة."},
    {"role": "user", "content": "ابحث عن ملفات Python بأخطاء نحوية وأصلحها."},
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

<div dir="rtl">

**التكلفة**: جلسة 20 جولة بتاريخ 10K رمز ≈ **0.10–0.30 $**.

---

## الوصفة 4 — خط أنابيب دفعي عالي الحجم

**ماذا**: ترجمة، تصنيف، إثراء، توليد تخليقي بنطاق ملايين الرموز يوميًا.

**لماذا V4-Flash**: 0.14 $/0.28 $ لكل مليون رمز هو الأرخص في الجودة شبه الحدودية.

</div>

```python
import os, asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                    base_url="https://api.deepseek.com/v1")

async def translate(text: str) -> str:
    r = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": "ترجم إلى اليابانية. أخرج الترجمة فقط."},
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

<div dir="rtl">

**التكلفة**: 10,000 ترجمة قصيرة (~2M رمز) ≈ **0.30–0.60 $**.

---

## الوصفة 5 — مدرس رياضيات / إثبات رسمي

**ماذا**: حلول بمستوى أولمبياد مع سلاسل استدلال كاملة.

**لماذا V4**: Putnam 2025 إثبات رسمي **120/120 علامة كاملة**، HMMT 95.2.

</div>

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
             "أنت مدرب أولمبياد رياضيات. أظهر الاستدلال الكامل، ثم أعطِ الإجابة النهائية بصيغة FINAL: <الإجابة>."},
            {"role": "user", "content": problem},
        ],
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=32_000,
    )
    msg = r.choices[0].message
    return getattr(msg, "reasoning_content", "") or "", msg.content
```

<div dir="rtl">

**التكلفة**: لكل مسألة أولمبياد **0.05–0.20 $**.

---

## الوصفة 6 — تجاوز فشل متعدد الموردين مع LiteLLM

**ماذا**: عميل واحد يوجه إلى V4 و Claude و GPT مع تجاوز فشل تلقائي.

**V4 يجعلها عملية**: V4 رخيص بما يكفي ليجعل استراتيجية 3 موردين مجدية اقتصاديًا.

</div>

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
```

<div dir="rtl">

**التكلفة**: > 95% من حركة المرور تذهب إلى V4-Pro (الأرخص في المجموعة).

---

## الوصفة 7 — استضافة ذاتية لـ V4 مع vLLM

**ماذا**: تشغيل V4-Flash في شبكتك، عرض نقطة نهاية متوافقة مع OpenAI.

**لماذا V4**: النموذج المفتوح الأوزان الوحيد بهذه الجودة. مطلوب للامتثال (HIPAA، SOC2، الحكومات).

</div>

```bash
# الخادم: 8× H100 80GB أو 8× H200
pip install "vllm>=0.10"

python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --tensor-parallel-size 8 \
  --max-model-len 1048576 \
  --quantization fp8 \
  --trust-remote-code \
  --port 8000
```

<div dir="rtl">

**التكلفة على النطاق**: V4-Flash مستضاف ذاتيًا على 8× H200 محجوز، استخدام >70% ≈ **0.10–0.30 $/مليون رمز خرج**.

---

## الوصفة 8 — Aider (برمجة ثنائية طرفية) + V4

Aider أداة برمجة ثنائية في الطرفية، تلتزم تلقائيًا بتغييراتها في git. V4-Pro هو أقوى واجهة كود لها حاليًا.

</div>

```bash
pip install aider-chat
export DEEPSEEK_API_KEY=sk-...
aider --model openai/deepseek-v4-pro \
      --openai-api-base https://api.deepseek.com/v1 \
      --openai-api-key $DEEPSEEK_API_KEY
```

<div dir="rtl">

**التكلفة**: جلسة 2–3 ساعات بتعديلات متوسطة ≈ **1–5 $** (V4-Pro).

---

## الوصفة 9 — Cline (وكيل VS Code) + V4

[Cline](https://github.com/cline/cline) ملحق VS Code يحول المحرر إلى وكيل باستخدام الأدوات.

الإعدادات:
- **API Provider**: OpenAI Compatible
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key**: مفتاح DeepSeek الخاص بك
- **Model ID**: `deepseek-v4-pro`

**التكلفة**: لكل مهمة معقدة ≈ **0.20–1.00 $**.

---

## الوصفة 10 — بيانات تخليقية لضبط نموذج أصغر

**ماذا**: استخدم V4-Flash لتوليد بيانات تدريب عالية الجودة لنموذج طالب أصغر.

**لماذا V4**: بسعر 0.28 $ لكل مليون رمز خرج، 100M رمز بيانات تخليقية = **28 $**. قبل ثلاث سنوات كانت عملية بـ 30,000 $+.

</div>

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
             "ولّد مثالًا SFT عالي الجودة. أخرج JSON: "
             "{\"user\": ..., \"assistant\": ...}"},
            {"role": "user", "content": f"البذرة: {seed}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)
```

<div dir="rtl">

---

## جدول التكاليف السريع

| العبء | النموذج | التكلفة النموذجية |
|---|---|---|
| مراجعة مستودع كامل (500K رمز) | V4-Pro | 1–3 $ |
| أسئلة وأجوبة مستند طويل (100K + سؤال) | V4-Pro | ~0.18 $ |
| أسئلة وأجوبة مستند طويل (100K + سؤال) | V4-Flash | ~0.015 $ |
| وكيل 20 جولة | V4-Pro | 0.10–0.30 $ |
| 10,000 ترجمة دفعية | V4-Flash | 0.30–0.60 $ |
| مسألة أولمبياد | V4-Pro | 0.05–0.20 $ |
| جلسة Aider ساعتين | V4-Pro | 1–5 $ |
| 100M رمز بيانات تخليقية | V4-Flash | ~28 $ |

---

## 6 قواعد ذهبية

1. **Temperature = 1.0، Top-P = 1.0** — V4 مضبوط على هذه القيم. لا تنقل من Claude/GPT.
2. **Thinking ON** للرياضيات/الكود/التخطيط؛ **OFF** للدردشة/التصنيف/الدفعات.
3. **Flash للحجم، Pro للجودة** — أغلب أنظمة الإنتاج تستخدم كليهما.
4. **لا تستخدم سياق 1M بسذاجة للاسترجاع الدقيق فوق 128K** — أضف أداة استرجاع.
5. **التخزين المؤقت للـ system prompts الطويلة** — V4 يدعمه.
6. **احتفظ بـ OpenAI/Claude كـ fallback** عبر LiteLLM.

---

قدم وصفتك الخاصة عبر PR — انظر [CONTRIBUTING.md](../../../CONTRIBUTING.md).

</div>
