# FAQ

HN / Reddit / X पर हर V4 थ्रेड में आने वाले सवाल।

---

## मूल बातें

### DeepSeek V4 क्या है?
2026-04-24 को DeepSeek-AI द्वारा रिलीज़ किए गए दो ओपन-वेट MoE भाषा मॉडल: **V4-Pro** (1.6T / 49B सक्रिय) और **V4-Flash** (284B / 13B सक्रिय)। दोनों: 1M टोकन कॉन्टेक्स्ट, Thinking/Non-Thinking डुअल मोड, MIT लाइसेंस।

### V4 वाकई ओपन सोर्स है?
**वेट्स: हाँ, MIT।** डाउनलोड, रन, फाइन-ट्यून, व्यावसायिक उपयोग बिना शर्त।
**ट्रेनिंग कोड और डेटा: नहीं।** DeepSeek विस्तृत तकनीकी रिपोर्ट देता है पर पूरी pre-training pipeline नहीं। वही पैटर्न Llama, Qwen जैसा — "ओपन-वेट" OSI के अर्थ में "ओपन सोर्स" नहीं है।

### लाइसेंस असल में क्या अनुमति देता है?
MIT: व्यावसायिक उपयोग ✅, संशोधन ✅, पुनर्वितरण ✅, निजी उपयोग ✅। पुनर्वितरण के समय MIT नोटिस शामिल करें। कोई AUP overlay नहीं।

### V4-Pro और V4-Flash में क्या अंतर?

| | V4-Pro | V4-Flash |
|---|---|---|
| कुल पैरामीटर | 1.6T | 284B |
| सक्रिय पैरामीटर | 49B | 13B |
| गुणवत्ता श्रेणी | ≈ GPT-5.4 / Claude Opus 4.6 | ≈ Claude Haiku / GPT-5-Mini |
| API मूल्य (इन/आउट) | $1.74 / $3.48 | $0.14 / $0.28 |
| स्व-होस्ट न्यूनतम | 16× H200 | 8× H200 |

लागत-संवेदनशील: Flash। गुणवत्ता-संवेदनशील: Pro।

---

## तुलना

### V4 बनाम Claude 4.6 / GPT-5.4 / Gemini 3.1-Pro?
संक्षेप: **कोड में SOTA, रीज़निंग में बराबरी, फैक्ट रिकॉल में पीछे।** विवरण: [तुलना तालिकाएँ](./comparison.md)।

### V4 बनाम Qwen 3.5 / Llama 4 / GLM-5?
सभी सक्षम ओपन-वेट विकल्प। V4 कोड और लंबे कॉन्टेक्स्ट में आगे; Llama 4 सबसे परिपक्व ecosystem; Qwen सबसे मज़बूत multilingual; GLM-5 leaderboards के शीर्ष में सबसे हल्का।

### क्या V4 वाकई Opus से बेहतर कोड करता है?
सार्वजनिक benchmarks पर (LiveCodeBench 93.5 vs 88.8, Codeforces 3206): हाँ। SWE-Bench Verified: 80.6 vs 80.8 — बराबरी। **अपनी codebase पर दोनों का मूल्यांकन करें।**

---

## व्यावहारिक

### क्या मैं अपना मौजूदा OpenAI / Claude कोड V4 के साथ उपयोग कर सकता हूँ?
हाँ। V4 OpenAI ChatCompletions और Anthropic Messages दोनों बोलता है। `base_url` और मॉडल नाम बदलें।

### क्या मुफ़्त क्रेडिट है?
DeepSeek ने ऐतिहासिक रूप से नए खातों को क्रेडिट दिया है। वर्तमान शर्तें platform.deepseek.com पर देखें। Third-party hosts (OpenRouter, Together) के free tiers भी उपलब्ध।

### Rate limits क्या हैं?
Preview में कोई आधिकारिक आँकड़े नहीं। Community का कहना: Flash उदार, Pro तंग। Production: DeepSeek sales से संपर्क करें या SLA वाले third-party host का उपयोग करें।

### क्या V4 multimodal (इमेज/ऑडियो/वीडियो) सपोर्ट करता है?
**नहीं — Preview केवल text।** तकनीकी रिपोर्ट multimodal को भविष्य के कार्य के रूप में सूचीबद्ध करती है।

### क्या V4 function calling / tool use सपोर्ट करता है?
हाँ। OpenAI-संगत `tools` schema + Anthropic-संगत `tools`।

### Thinking mode क्या है?
V4 का dual mode: या तो दृश्य reasoning trace (`thinking: enabled`) या सीधा उत्तर (`thinking: disabled`)। एक ही मॉडल, एक ही मूल्य, अलग आउटपुट शैली। गणित/कोड के लिए ON, सरल चैट के लिए OFF।

### Context window वास्तव में कितना उपयोगी है?
**1,000,000 टोकन।** पर तकनीकी रिपोर्ट नोट करती है कि **128K से ऊपर retrieval सटीकता घटती है** — आप 1M भर सकते हैं पर गहराई में सटीक retrieval अविश्वसनीय। RAG के लिए retriever जोड़ें।

---

## स्व-होस्टिंग

### क्या V4 laptop पर चलता है?
नहीं। V4-Flash FP8 अकेले ~160GB weights। न्यूनतम वास्तविक: 8× H100 80GB।

### क्या V4 एक H100 पर चलता है?
नहीं। अत्यधिक quantized Flash छोटे context के साथ सैद्धांतिक रूप से चल सकता है पर गुणवत्ता अनिश्चित। Single GPU users: managed API चुनें।

### क्या vLLM / SGLang / TensorRT-LLM समर्थित हैं?
vLLM और SGLang: Day-0 समर्थन। TensorRT-LLM: NVIDIA release notes देखें। विवरण: [local-deployment.md](../../../getting-started/local-deployment.md)।

### क्या V4 वाकई Huawei Ascend पर चलता है?
HN रिपोर्ट के अनुसार: **हाँ।** DeepSeek Huawei चिप्स पर V4 को प्रशिक्षित और serve करता है, production stack में CUDA निर्भरता नहीं। AI आपूर्ति श्रृंखला decoupling का महत्वपूर्ण संकेत।

---

## गोपनीयता / शासन

### क्या DeepSeek मेरे prompts पर train करता है?
आधिकारिक API पर: platform.deepseek.com पर वर्तमान गोपनीयता नीति देखें। Third-party hosts (Together, Fireworks): bिना training वाला provider चुनें। स्व-होस्ट: डेटा आपके network से बाहर नहीं जाता।

### क्या V4 censored है?
सभी Chinese labs द्वारा trained मॉडलों की तरह, V4 में कुछ विषयों (विशेष रूप से China में राजनीतिक रूप से संवेदनशील) पर पश्चिमी मॉडलों से अलग guardrails हैं। अधिकांश व्यावसायिक उपयोगों के लिए अप्रासंगिक।

### क्या V4 regulated workloads (स्वास्थ्य/कानूनी/वित्त) के लिए सुरक्षित है?
- **कानूनी रूप से**: MIT अनुमति देता है
- **Compliance**: आपके नियामक पर निर्भर। VPC में स्व-होस्ट V4 HIPAA / SOC2 / GDPR के साथ संगत
- **API पर**: DeepSeek के प्रमाणपत्रों पर निर्भर

### क्या मैं इसे बेचे जाने वाले उत्पाद में embed कर सकता हूँ?
हाँ। MIT बिना व्यावसायिक प्रतिबंध। Best practice: अपने "About" पेज या docs में मॉडल origin (DeepSeek) का उल्लेख करें।

---

## यह रिपॉज़िटरी

### क्या यह रिपॉज़िटरी आधिकारिक है?
**नहीं।** समुदाय-रखरखाव वाला संसाधन। DeepSeek-AI न तो लेखक है, न अनुमोदक। [DISCLAIMER.md](../../../DISCLAIMER.md) देखें।

### केवल आधिकारिक docs के लिंक क्यों नहीं?
तीन कारण:
1. **अनुवाद** — 7 भाषाएँ first-class, retroactive machine translation नहीं
2. **तुलना** — DeepSeek स्वयं की Claude/GPT से विश्वसनीय तुलना नहीं कर सकता; तटस्थ community repo कर सकता है
3. **माइग्रेशन** — गाइड "आप पहले से किसी और का API उपयोग कर रहे हैं" के दृष्टिकोण से लिखे गए

### योगदान कैसे करूँ?
[CONTRIBUTING.md](../../../CONTRIBUTING.md) देखें। विशेष रूप से चाहिए: देशज वक्ता समीक्षा, benchmark reproductions, असामान्य hardware पर deployment नोट, community tools।

### अपडेट कैसे ट्रैक करूँ?
इस रिपॉज़िटरी को Watch करें, या CHANGELOG.md फ़ॉलो करें। प्रतिबद्धता: V4 updates के साथ तालमेल।
