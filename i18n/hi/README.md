<div align="center">

<img src="../../assets/banner.svg" alt="awesome-deepseek-v4" width="900">

# awesome-deepseek-v4

**[DeepSeek V4](https://huggingface.co/collections/deepseek-ai/deepseek-v4) के लिए व्यावहारिक बहुभाषी संसाधन केंद्र।**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![अनौपचारिक](https://img.shields.io/badge/status-unofficial-lightgrey.svg)](../../DISCLAIMER.md)
[![PRs स्वागत है](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../CONTRIBUTING.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-DeepSeek--V4-yellow)](https://huggingface.co/collections/deepseek-ai/deepseek-v4)

**🌍 अपनी भाषा चुनें**

[English](../../README.md) · [简体中文](../zh-CN/README.md) · [Français](../fr/README.md) · [العربية](../ar/README.md) · [日本語](../ja/README.md) · [Deutsch](../de/README.md) · [**हिन्दी**](./README.md)

</div>

---

## विनिर्देश तालिका

| | **DeepSeek-V4-Pro** | **DeepSeek-V4-Flash** |
|---|---|---|
| कुल पैरामीटर | **1.6 T** MoE | **284 B** MoE |
| सक्रिय पैरामीटर | 49 B | 13 B |
| विशेषज्ञ (रूटेड × सक्रिय) | 384 × 6 | 256 × 6 |
| कॉन्टेक्स्ट लंबाई | 1,000,000 टोकन | 1,000,000 टोकन |
| प्रशिक्षण टोकन | 33 T | 32 T |
| परिशुद्धता | FP4 (विशेषज्ञ) + FP8 | FP8 |
| इनपुट मूल्य | $1.74 / M टोकन | $0.14 / M टोकन |
| आउटपुट मूल्य | $3.48 / M टोकन | $0.28 / M टोकन |
| लाइसेंस | MIT · व्यावसायिक उपयोग OK | MIT · व्यावसायिक उपयोग OK |
| मोड | Thinking · Non-Thinking | Thinking · Non-Thinking |

पूरी स्पेक: [docs/architecture.md](../../docs/architecture.md) · बेंचमार्क: [docs/benchmarks.md](../../docs/benchmarks.md) · मूल्य: [docs/pricing.md](../../docs/pricing.md) · तुलना तालिकाएँ: [docs/comparison.md](../../docs/comparison.md)।

---

## 60-सेकंड क्विकस्टार्ट

V4 OpenAI ChatCompletions **और** Anthropic Messages प्रोटोकॉल **दोनों** बोलता है।

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/v1")
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "सिद्ध करें कि √2 अपरिमेय है।"}],
)
print(resp.choices[0].message.content)
```

```python
from anthropic import Anthropic
client = Anthropic(api_key="sk-...", base_url="https://api.deepseek.com/anthropic")
msg = client.messages.create(
    model="deepseek-v4-pro", max_tokens=1024,
    messages=[{"role": "user", "content": "सिद्ध करें कि √2 अपरिमेय है।"}],
)
print(msg.content[0].text)
```

अधिक: [API क्विकस्टार्ट](../../getting-started/api-quickstart.md) · [Thinking मोड](../../examples/python_thinking_mode.py) · [टूल कॉलिंग](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh) · [लोकल vLLM](../../getting-started/local-deployment.md)।

---

## रिपॉज़िटरी सामग्री

### शुरुआत और माइग्रेशन
- [**API क्विकस्टार्ट**](../../getting-started/api-quickstart.md)
- [**लोकल डिप्लॉयमेंट**](../../getting-started/local-deployment.md) — vLLM / SGLang / transformers
- [**DeepSeek V3 से माइग्रेशन**](../../getting-started/migration-from-v3.md)
- [**OpenAI से माइग्रेशन**](../../getting-started/migration-from-openai.md) — 2 लाइनें बदलें
- [**Anthropic Claude से माइग्रेशन**](../../getting-started/migration-from-claude.md) — 2 लाइनें बदलें

### संदर्भ
- [**बेंचमार्क**](../../docs/benchmarks.md)
- [**आर्किटेक्चर**](../../docs/architecture.md) — CSA+HCA / mHC / Muon / OPD
- [**मूल्य**](../../docs/pricing.md)
- [**तुलना तालिकाएँ**](../../docs/comparison.md)

### असली काम के लिए
- [**रेसिपी**](./docs/recipes.md) 🇮🇳 — **10 कॉपी-पेस्ट पैटर्न** लागत अनुमान के साथ।
- [**प्रॉम्प्टिंग गाइड**](../../docs/prompting-guide.md) ⚠️ अंग्रेज़ी
- [**फाइन-ट्यूनिंग**](../../docs/fine-tuning.md) ⚠️ अंग्रेज़ी
- [**FAQ**](./docs/faq.md) 🇮🇳

> *अभी केवल दो सबसे मूल्यवान विस्तृत दस्तावेज़ — रेसिपी और FAQ — हिंदी में अनुवादित हैं। अन्य पृष्ठ अंग्रेज़ी में हैं। PR द्वारा अनुवाद योगदान का स्वागत है ([CONTRIBUTING](../../CONTRIBUTING.md) देखें)।*

### संसाधन
- [आधिकारिक लिंक](../../resources/official-links.md)
- [Awesome समुदाय](../../resources/awesome-community.md)
- [संबंधित पेपर्स](../../resources/papers.md)

### उदाहरण
[OpenAI SDK](../../examples/python_openai_basic.py) · [Anthropic SDK](../../examples/python_anthropic_basic.py) · [Thinking](../../examples/python_thinking_mode.py) · [Tool calls](../../examples/python_tool_calls.py) · [curl](../../examples/curl_basic.sh)

### CLI टूल्स ([`tools/`](../../tools/))
एकल-फ़ाइल Python CLI। एकमात्र निर्भरता: `openai`।
- [**v4-cost-calc**](../../tools/v4_cost_calc.py) — मासिक खर्च की तुलना: V4 vs Claude / GPT / Gemini।
- [**v4-migrate-env**](../../tools/v4_migrate_env.py) — मौजूदा प्रोजेक्ट के OpenAI/Anthropic कॉन्फ़िग को V4 में बदलें।
- [**v4-repo-review**](../../tools/v4_repo_review.py) — पूरी रिपॉज़िटरी V4-Pro को भेजें और संरचित रिव्यू प्राप्त करें।
- [**v4-chat**](../../tools/v4_chat.py) — स्ट्रीमिंग टर्मिनल REPL।

### स्व-होस्टिंग ([`deploy/`](../../deploy/))
अपने हार्डवेयर पर OpenAI-संगत endpoint।
- [**Docker Compose**](../../deploy/docker-compose.yml) — एक `docker compose up`।
- [**Kubernetes**](../../deploy/k8s/deployment.yaml) — प्रोडक्शन Deployment + Service + ConfigMap।
- [**systemd**](../../deploy/systemd/v4-vllm.service) — बेयर-मेटल यूनिट फ़ाइल।

### प्रॉम्प्ट लाइब्रेरी ([`prompts/`](../../prompts/))
परीक्षित सिस्टम प्रॉम्प्ट। प्रत्येक अनुशंसित मॉडल और मोड घोषित करता है।
- कोडिंग: [code-reviewer](../../prompts/coding/code-reviewer.md) · [bug-hunter](../../prompts/coding/bug-hunter.md) · [refactor-planner](../../prompts/coding/refactor-planner.md) · [test-writer](../../prompts/coding/test-writer.md)
- एजेंट: [coding-agent](../../prompts/agents/coding-agent.md) · [research-agent](../../prompts/agents/research-agent.md) · [planner](../../prompts/agents/planner.md)
- लेखन: [technical-writer](../../prompts/writing/technical-writer.md) · [translator](../../prompts/writing/translator.md)
- विश्लेषण: [contract-reviewer](../../prompts/analysis/contract-reviewer.md) · [paper-summarizer](../../prompts/analysis/paper-summarizer.md)
- शिक्षा: [math-tutor](../../prompts/education/math-tutor.md)

---

## योगदान

PRs स्वागत है — सुधार, अनुवाद, नए बेंचमार्क, समुदाय टूल्स। [CONTRIBUTING.md](../../CONTRIBUTING.md) देखें।

---

## लाइसेंस

- इस रिपॉज़िटरी की मूल सामग्री: [MIT](../../LICENSE)
- DeepSeek V4 मॉडल वेट्स और तकनीकी रिपोर्ट: MIT, © DeepSeek-AI
- "DeepSeek" DeepSeek-AI का ट्रेडमार्क है। यह प्रोजेक्ट **DeepSeek-AI से संबद्ध नहीं** है — [DISCLAIMER](../../DISCLAIMER.md) देखें।

---

## अनुरक्षक

**AI小蓝鲸** — मैं चीनी प्लेटफ़ॉर्म पर AI और ओपन मॉडल के बारे में लिखता हूँ। सभी प्लेटफ़ॉर्म पर एक ही हैंडल:

| प्लेटफ़ॉर्म | हैंडल |
|---|---|
| 📕 Xiaohongshu (小红书) | [AI小蓝鲸](https://www.xiaohongshu.com/search_result?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8&type=54) |
| 📺 Bilibili (B站) | [AI小蓝鲸](https://search.bilibili.com/upuser?keyword=AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎵 Douyin (抖音) | [AI小蓝鲸](https://www.douyin.com/search/AI%E5%B0%8F%E8%93%9D%E9%B2%B8) |
| 🎬 WeChat Channels (视频号) | **AI小蓝鲸** (WeChat के भीतर खोजें) |

किसी भी प्लेटफ़ॉर्म से PR का स्वागत है।

---

<div align="center">

समय बचाया तो ⭐ कर दें।

</div>
