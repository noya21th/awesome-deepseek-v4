# Deploy

Three ways to self-host DeepSeek V4, in order of increasing complexity.

All three expose an **OpenAI-compatible endpoint** — the same `openai` SDK works against them, just with a different `base_url`.

---

## 1. Docker Compose (single host)

The fastest path to a running V4 endpoint.

```bash
cd deploy
docker compose up -d
# wait 60-120 seconds for model download + load
curl http://localhost:8000/v1/models
```

Requirements:
- NVIDIA Container Toolkit installed
- 8× H100 80GB or 4× H200 141GB (adjust `--tensor-parallel-size`)
- ~200GB free disk for weights

Edit [`docker-compose.yml`](./docker-compose.yml) to switch to V4-Pro (raise `--tensor-parallel-size` to 16 and change `--model` to `deepseek-ai/DeepSeek-V4-Pro`).

---

## 2. Kubernetes

Production pattern: a `Deployment` + `Service` + `ConfigMap`.

```bash
kubectl apply -f deploy/k8s/deployment.yaml
kubectl get pods -l app=v4-vllm
kubectl port-forward svc/v4-vllm 8000:80   # for local smoke testing
```

See [`k8s/deployment.yaml`](./k8s/deployment.yaml) for:
- GPU resource requests (`nvidia.com/gpu: 8`)
- Readiness / liveness probes tuned for vLLM cold-start
- ConfigMap-driven model name and TP size

For V4-Pro across two nodes, add a `topologySpreadConstraints` block and raise `TP_SIZE` to 16.

---

## 3. Bare-metal systemd

For dedicated inference hosts without container orchestration.

```bash
# 1. Create a vllm user, install uv or venv, pip install vllm
sudo useradd -m -d /opt/v4-vllm vllm
sudo -u vllm bash -c 'cd /opt/v4-vllm && python -m venv .venv && .venv/bin/pip install vllm'

# 2. Install the unit
sudo cp deploy/systemd/v4-vllm.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now v4-vllm

# 3. Watch it come up
journalctl -u v4-vllm -f
```

See [`systemd/v4-vllm.service`](./systemd/v4-vllm.service) for the unit.

---

## Testing the endpoint

Any of the three approaches exposes the same API:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer dummy" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-v4-flash",
       "messages": [{"role":"user","content":"Hello"}]}'
```

```python
from openai import OpenAI
client = OpenAI(api_key="dummy", base_url="http://localhost:8000/v1")
print(client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "Hello"}],
).choices[0].message.content)
```

---

## Sizing cheat sheet

| Model | Min GPU config | Comfortable config | Max context |
|---|---|---|---|
| V4-Flash (FP8) | 8× H100 80GB | 8× H200 141GB | 1M |
| V4-Flash (FP8) | 4× H200 141GB | — | 256K |
| V4-Pro (FP4+FP8) | 16× H200 141GB | 2-node 16× H200 | 1M |
| V4-Pro (FP4+FP8) | 8× H200 + KV offload | — | 128K |

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `OOM at load` | Drop `--max-model-len` to 131072 or 262144 for testing. |
| `CUDA error: invalid argument` | Driver/vLLM version mismatch. Use the pinned vLLM image tag. |
| Long first-request latency | MoE cold start. Send a warm-up request after readiness probe passes. |
| HF download is slow | Set `HF_HUB_ENABLE_HF_TRANSFER=1`. |
| Container cannot see GPUs | NVIDIA Container Toolkit not installed / `--gpus all` missing. |

---

## Managed alternatives

If you want V4 without running GPUs, see [`resources/awesome-community.md`](../resources/awesome-community.md) for a list of third-party hosts (Together, Fireworks, DeepInfra, OpenRouter, Parasail, Atlas Cloud).
