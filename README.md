
### AI Quality Monitoring Demo with Cloud-Native Stack

A demonstration system for securing AI APIs with policy-enforcing proxies using modern cloud-native infrastructure.

## 🔒 Use Case Demonstrated: Secure AI Text Enrichment for Internal Teams

This demo showcases a secure LLM-backed API that analyzes internal text inputs (e.g., support issues) **only after passing through an Envoy proxy configured with a Lua-based dynamic guardrail**.
The guardrail performs **pre-inference input validation** by inspecting raw payloads and blocking sensitive information such as **Social Security Numbers (SSNs)** before the request reaches the AI backend.

Two types of requests are demonstrated:

* A **positive case** with a legitimate inquiry, which is allowed and processed.
* A **negative case** containing an SSN pattern, which is intercepted and blocked with a `403` response.

---

## Architecture

* **Envoy Proxy**: Intercepts and inspects incoming requests via Lua filters
* **FastAPI**: Simulated AI agent backend with natural language task processing
* **Kubernetes**: Deployment and orchestration of the proxy and backend
* **cURL**: Used for demonstration of both allowed and blocked input flows

---

## How the System Works

1. **Clients send input** (text and task type) via HTTP POST to the API.
2. **Envoy proxy** (configured with Lua guardrail) inspects request body.
3. If request contains **PII (like SSNs)**, the proxy **blocks it with a 403**.
4. If clean, it is forwarded to the **FastAPI-based AI agent backend** for processing.

---

## Example Commands

### ✅ Valid Request (Allowed)

```bash
curl -i -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"text":"Our application crashes when uploading large files over 2GB. Can you find the key issue?","task_type":"analyze"}'
```

### ❌ Invalid Request (Blocked – Contains SSN)

```bash
curl -i -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"text":"My SSN is 123-45-6789, please handle this case","task_type":"analyze"}'
```

---

## Deployment Notes

* **Static Envoy Configuration** is used to guarantee enforcement even without dynamic control plane (xDS).
* `kgateway` (formerly part of Gloo Gateway) was not used due to lack of working xDS connectivity between its control plane and the Envoy data plane.
* This direct Envoy setup ensures reproducible, CNCF-friendly policy enforcement via ConfigMap-mounted YAML.
