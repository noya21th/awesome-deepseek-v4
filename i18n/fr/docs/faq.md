# FAQ

Les questions qui apparaissent dans tous les fils HN / Reddit / X sur V4.

---

## Bases

### Qu'est-ce que DeepSeek V4 ?
Deux modèles open-weight MoE publiés par DeepSeek-AI le 2026-04-24 : **V4-Pro** (1,6 T / 49 B actifs) et **V4-Flash** (284 B / 13 B actifs). Les deux : 1M tokens de contexte, modes Thinking/Non-Thinking, licence MIT.

### V4 est-il vraiment open source ?
**Poids : oui, MIT.** Téléchargement, exécution, fine-tuning, utilisation commerciale sans restriction.
**Code et données d'entraînement : non.** DeepSeek publie un rapport technique détaillé mais pas le pipeline complet. C'est le même schéma que Llama, Qwen — « open-weight » n'est pas « open source » au sens OSI.

### Que permet exactement la licence ?
MIT : usage commercial ✅, modification ✅, redistribution ✅, usage privé ✅. Inclure la notice MIT lors de la redistribution. Pas d'AUP superposée.

### Quelle est la différence V4-Pro / V4-Flash ?

| | V4-Pro | V4-Flash |
|---|---|---|
| Paramètres totaux | 1,6 T | 284 B |
| Paramètres actifs | 49 B | 13 B |
| Niveau de qualité | ≈ GPT-5.4 / Claude Opus 4.6 | ≈ Claude Haiku / GPT-5-Mini |
| Tarif API (in/out) | 1,74 $ / 3,48 $ | 0,14 $ / 0,28 $ |
| Seuil d'auto-hébergement | 16× H200 | 8× H200 |

Cas sensibles au coût : Flash. Cas sensibles à la qualité : Pro.

---

## Comparaisons

### V4 vs Claude 4.6 / GPT-5.4 / Gemini 3.1-Pro ?
Résumé : **SOTA en code, à égalité en raisonnement, en retrait sur la connaissance factuelle.** Détails : [tableaux comparatifs](./comparison.md).

### V4 vs Qwen 3.5 / Llama 4 / GLM-5 ?
Tous solides. V4 mène en code et long contexte ; Llama 4 a l'écosystème le plus mature ; Qwen est le plus fort en multilingue ; GLM-5 est le plus léger en haut de classement.

### V4 est-il vraiment meilleur que Opus en code ?
Sur les benchmarks publics (LiveCodeBench 93.5 vs 88.8, Codeforces 3206) : oui. SWE-Bench Verified : 80.6 vs 80.8 — ex-aequo. **Évaluez les deux sur votre propre base de code.**

---

## Pratique

### Puis-je utiliser mon code OpenAI / Claude existant avec V4 ?
Oui. V4 parle à la fois le protocole OpenAI ChatCompletions et le protocole Anthropic Messages. Changez `base_url` et le nom du modèle.

### Y a-t-il un crédit gratuit ?
DeepSeek a historiquement offert des crédits aux nouveaux comptes. Voir les conditions actuelles sur platform.deepseek.com. Vous pouvez aussi utiliser les free tiers de hôtes tiers (OpenRouter, Together).

### Quelles limites de débit ?
Pas de chiffres officiels en preview. La communauté rapporte : Flash généreux, Pro plus serré. Charges de production : contactez les ventes DeepSeek ou utilisez un hôte tiers avec SLA.

### V4 supporte-t-il le multimodal (image/audio/vidéo) ?
**Non — texte uniquement en preview.** Le rapport technique liste le multimodal en travaux futurs.

### V4 supporte-t-il function calling / tool use ?
Oui. Schéma `tools` compatible OpenAI + compatible Anthropic (sur les endpoints respectifs). Voir [examples/python_tool_calls.py](../../../examples/python_tool_calls.py).

### Qu'est-ce que le mode Thinking ?
Double mode de V4 : soit le modèle émet une trace de raisonnement visible (`thinking: enabled`), soit il répond directement (`thinking: disabled`). Même modèle, même prix, style de sortie différent. Activez pour maths/code, désactivez pour chat simple.

### Quelle est la vraie longueur de contexte utile ?
**1 000 000 tokens.** Mais le rapport technique note que **la précision de récupération se dégrade au-delà de 128K** — on peut en mettre 1M mais la récupération précise en profondeur est peu fiable. Pour du RAG, ajoutez un retriever.

---

## Auto-hébergement

### V4 tourne-t-il sur un laptop ?
Non. V4-Flash FP8 fait ~160 GB de poids. Minimum réaliste : 8× H100 80GB.

### V4 tient-il sur une seule H100 ?
Non. Flash très quantifié avec contexte court peut-être, mais qualité incertaine. Utilisateurs mono-GPU : prenez l'API managée.

### vLLM / SGLang / TensorRT-LLM sont-ils supportés ?
vLLM et SGLang : support Day-0. TensorRT-LLM : voir les notes NVIDIA. Détails : [local-deployment.md](../../../getting-started/local-deployment.md).

### V4 tourne-t-il vraiment sur Huawei Ascend ?
D'après HN : **oui.** DeepSeek entraîne et sert V4 sur puces Huawei, sans dépendance CUDA en production. Signal important pour le découplage de la chaîne d'approvisionnement IA. Voir la doc Huawei MindIE.

---

## Confidentialité / gouvernance

### DeepSeek entraîne-t-il sur mes prompts ?
Sur l'API officielle : voir la politique de confidentialité sur platform.deepseek.com. Sur un hôte tiers (Together, Fireworks) : choisissez un fournisseur sans entraînement sur données. Auto-hébergement : données ne quittent pas votre réseau.

### V4 est-il censuré ?
Comme tous les modèles entraînés par labs chinois, V4 a des garde-fous sur certains sujets (notamment politique sensible en Chine) qui diffèrent des modèles occidentaux. Pour la majorité des usages commerciaux c'est sans importance. Si c'est critique pour vous :
- **API** : filtres côté serveur, non modifiables
- **Poids** : techniques communautaires d'« abliteration », à vos risques

### V4 est-il sûr pour les charges régulées (santé/droit/finance) ?
- **Légalement** : MIT permet
- **Conformité** : dépend de votre régulateur. V4 auto-hébergé dans un VPC est compatible HIPAA / SOC2 / GDPR
- **API** : dépend des certifications DeepSeek

### Puis-je l'intégrer dans un produit vendu ?
Oui. MIT sans restriction commerciale. Meilleure pratique : mentionner la provenance du modèle (DeepSeek) dans votre page « À propos » ou vos docs.

---

## Ce dépôt

### Est-ce officiel ?
**Non.** Ressource communautaire. DeepSeek-AI n'en est pas l'auteur ni ne l'approuve. Voir [DISCLAIMER.md](../../../DISCLAIMER.md).

### Pourquoi pas juste des liens vers la doc officielle ?
Trois raisons :
1. **Traduction** — 7 langues de première classe, pas du machine-translation réactif
2. **Comparaison** — DeepSeek ne peut pas se comparer à Claude/GPT de manière crédible ; un dépôt communautaire neutre, oui
3. **Migration** — les guides sont écrits du point de vue « vous utilisez déjà l'API d'un autre »

### Comment contribuer ?
Voir [CONTRIBUTING.md](../../../CONTRIBUTING.md). Spécialement bienvenus : relectures par natifs, reproductions de benchmarks, notes de déploiement sur matériel atypique, outils communautaires.

### Comment rester à jour ?
Watch ce dépôt, ou suivez CHANGELOG.md. Engagement : suivre les mises à jour de V4.
