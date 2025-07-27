from fastapi import FastAPI, Response
from pydantic import BaseModel
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random

app = FastAPI()

HELPFULNESS_GAUGE = Gauge("agent_helpfulness_score", "Helpfulness score")
TRANSPARENCY_GAUGE = Gauge("agent_transparency_score", "Transparency score")
REQUEST_COUNT = Counter("agent_requests_total", "Total requests")

class QueryRequest(BaseModel):
    text: str

@app.post("/orchestrate")
async def orchestrate_agents(request: QueryRequest):
    REQUEST_COUNT.inc()
    
    # Simulate multi-agent processing with realistic delays
    import time
    time.sleep(2)
    
    # Generate realistic demo metrics
    helpfulness = round(random.uniform(0.7, 0.95), 2)
    transparency = round(random.uniform(0.6, 0.90), 2)
    
    HELPFULNESS_GAUGE.set(helpfulness)
    TRANSPARENCY_GAUGE.set(transparency)
    
    return {
        "workflow": "multi_agent_orchestration",
        "input": request.text,
        "result": f"Classified as POSITIVE_SENTIMENT. Summary: This text shows {request.text[:50]}...",
        "helpfulness_score": helpfulness,
        "transparency_score": transparency,
        "runtime_seconds": 2.1
    }

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    return {"status": "healthy"}
