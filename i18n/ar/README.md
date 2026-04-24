<div align="center" dir="rtl">

<img src="../../assets/banner.svg" alt="awesome-deepseek-v4" width="900">

# awesome-deepseek-v4

**مركز موارد عملي متعدد اللغات لـ [DeepSeek V4](https://huggingface.co/collections/deepseek-ai/deepseek-v4).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![غير رسمي](https://img.shields.io/badge/status-unofficial-lightgrey.svg)](../../DISCLAIMER.md)
[![PRs مرحب بها](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../CONTRIBUTING.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-DeepSeek--V4-yellow)](https://huggingface.co/collections/deepseek-ai/deepseek-v4)

**🌍 اختر لغتك**

[English](../../README.md) · [简体中文](../zh-CN/README.md) · [Français](../fr/README.md) · [**العربية**](./README.md) · [日本語](../ja/README.md) · [Deutsch](../de/README.md) · [हिन्दी](../hi/README.md)

</div>

---

<div dir="rtl">

## ورقة المواصفات

| | **DeepSeek-V4-Pro** | **DeepSeek-V4-Flash** |
|---|---|---|
| المعاملات الإجمالية | **1.6 ت** MoE | **284 ب** MoE |
| المعاملات المُفعَّلة | 49 ب | 13 ب |
| الخبراء (الموجّهة × النشطة) | 384 × 6 | 256 × 6 |
| طول السياق | 1,000,000 رمز | 1,000,000 رمز |
| رموز التدريب | 33 ت | 32 ت |
| الدقة | FP4 (خبراء) + FP8 | FP8 |
| سعر الإدخال | 1.74 $ / مليون رمز | 0.14 $ / مليون رمز |
| سعر الإخراج | 3.48 $ / مليون رمز | 0.28 $ / مليون رمز |
| الرخصة | MIT · استخدام تجاري مسموح | MIT · استخدام تجاري مسموح |
| الأوضاع | Thinking · Non-Thinking | Thinking · Non-Thinking |

المواصفات الكاملة: [docs/architecture.md](../../docs/architecture.md) · المعايير: [docs/benchmarks.md](../../docs/benchmarks.md) · التسعير: [docs/pricing.md](../../docs/pricing.md) · جداول المقارنة: [docs/comparison.md](../../docs/comparison.md).

---

## بداية في 60 ثانية

V4 يتحدث بروتوكولي OpenAI ChatCompletions و Anthropic Messages **معًا**.

</div>

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/v1")
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "أثبت أن √2 عدد غير نسبي."}],
)
print(resp.choices[0].message.content)
```

```python
from anthropic import Anthropic
client = Anthropic(api_key="sk-...", base_url="https://api.deepseek.com/anthropic")
msg = client.messages.create(
    model="deepseek-v4-pro", max_tokens=1024,
    messages=[{"role": "user", "content": "أثبت أن √2 عدد غير نسبي."}],
)
print(msg.content[0].text)
```

<div dir="rtl">

---

## محتوى المستودع

### البدء والهجرة
- [**البدء السريع بالـ API**](../../getting-started/api-quickstart.md)
- [**النشر المحلي**](../../getting-started/local-deployment.md) — vLLM / SGLang / transformers
- [**الهجرة من DeepSeek V3**](../../getting-started/migration-from-v3.md)
- [**الهجرة من OpenAI**](../../getting-started/migration-from-openai.md) — تغيير سطرين
- [**الهجرة من Anthropic Claude**](../../getting-started/migration-from-claude.md) — تغيير سطرين

### مرجع
- [**المعايير**](../../docs/benchmarks.md)
- [**المعمارية**](../../docs/architecture.md) — CSA+HCA / mHC / Muon / OPD
- [**التسعير**](../../docs/pricing.md)
- [**جداول المقارنة**](../../docs/comparison.md)

### للعمل الفعلي
- [**الوصفات**](./docs/recipes.md) 🇸🇦 — **10 أنماط جاهزة للنسخ واللصق** مع تقديرات التكلفة.
- [**دليل الكتابة للنموذج**](../../docs/prompting-guide.md) ⚠️ إنجليزي
- [**الضبط الدقيق**](../../docs/fine-tuning.md) ⚠️ إنجليزي
- [**الأسئلة الشائعة**](./docs/faq.md) 🇸🇦

> *حاليًا تُرجمت الوثيقتان الأكثر قيمة فقط — الوصفات والأسئلة الشائعة — إلى العربية. تبقى الصفحات الأخرى بالإنجليزية. مساهمات الترجمة مرحب بها عبر PR (انظر [CONTRIBUTING](../../CONTRIBUTING.md)).*

### موارد
- [الروابط الرسمية](../../resources/official-links.md)
- [قائمة المجتمع](../../resources/awesome-community.md)
- [الأوراق البحثية](../../resources/papers.md)

### أمثلة
[OpenAI SDK](../../examples/python_openai_basic.py) · [Anthropic SDK](../../examples/python_anthropic_basic.py) · [Thinking](../../examples/python_thinking_mode.py) · [Tool calls](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh)

### أدوات CLI ([`tools/`](../../tools/))
سكربتات Python بملف واحد. التبعية الوحيدة: `openai`.
- [**v4-cost-calc**](../../tools/v4_cost_calc.py) — مقارنة الإنفاق الشهري: V4 vs Claude / GPT / Gemini.
- [**v4-migrate-env**](../../tools/v4_migrate_env.py) — فحص مشروع وتحويل إعداد OpenAI/Anthropic إلى V4.
- [**v4-repo-review**](../../tools/v4_repo_review.py) — إرسال مستودع إلى V4-Pro للحصول على مراجعة كود منظمة.
- [**v4-chat**](../../tools/v4_chat.py) — REPL طرفي بالبث.

### الاستضافة الذاتية ([`deploy/`](../../deploy/))
نقطة نهاية متوافقة مع OpenAI على عتادك.
- [**Docker Compose**](../../deploy/docker-compose.yml) — أمر `docker compose up` واحد.
- [**Kubernetes**](../../deploy/k8s/deployment.yaml) — Deployment + Service + ConfigMap للإنتاج.
- [**systemd**](../../deploy/systemd/v4-vllm.service) — ملف وحدة للنشر المباشر على العتاد.

### مكتبة التعليمات ([`prompts/`](../../prompts/))
تعليمات نظام مُختبرة. كل منها يحدد النموذج والوضع الموصى به.
- البرمجة: [code-reviewer](../../prompts/coding/code-reviewer.md) · [bug-hunter](../../prompts/coding/bug-hunter.md) · [refactor-planner](../../prompts/coding/refactor-planner.md) · [test-writer](../../prompts/coding/test-writer.md)
- الوكلاء: [coding-agent](../../prompts/agents/coding-agent.md) · [research-agent](../../prompts/agents/research-agent.md) · [planner](../../prompts/agents/planner.md)
- الكتابة: [technical-writer](../../prompts/writing/technical-writer.md) · [translator](../../prompts/writing/translator.md)
- التحليل: [contract-reviewer](../../prompts/analysis/contract-reviewer.md) · [paper-summarizer](../../prompts/analysis/paper-summarizer.md)
- التعليم: [math-tutor](../../prompts/education/math-tutor.md)

---

## المساهمة

PRs مرحب بها — التصحيحات والترجمات والمعايير الجديدة والأدوات. انظر [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## الرخصة

- محتوى هذا المستودع الأصلي: [MIT](../../LICENSE).
- أوزان DeepSeek V4 وتقريرها الفني: MIT، © DeepSeek-AI.
- "DeepSeek" علامة تجارية لـ DeepSeek-AI. هذا المشروع **ليس تابعًا لـ DeepSeek-AI** — انظر [DISCLAIMER](../../DISCLAIMER.md).

</div>

---

<div dir="rtl">

## القائم على الصيانة

**AI小蓝鲸** — أنشر عن الذكاء الاصطناعي والنماذج مفتوحة الأوزان باللغة الصينية. نفس الاسم على جميع المنصات:

| المنصة | الحساب |
|---|---|
| 📕 Xiaohongshu (小红书) | [AI小蓝鲸](https://www.xiaohongshu.com/search_result?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8&type=54) |
| 📺 Bilibili (B站) | [AI小蓝鲸](https://search.bilibili.com/upuser?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎵 Douyin (抖音) | [AI小蓝鲸](https://www.douyin.com/search/AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎬 WeChat Channels (视频号) | **AI小蓝鲸** (البحث داخل WeChat) |

PRs مرحب بها من أي منصة.

</div>

---

<div align="center">

ضع ⭐ إذا وفّر عليك هذا المستودع وقتًا.

</div>
