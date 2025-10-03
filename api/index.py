from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os
import json

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# Load telemetry; assumes q-vercel-latency.json is in the same folder
json_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
with open(json_path, "r") as f:
    data = pd.DataFrame(json.load(f))

@app.post("/")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    result = {}
    for region in regions:
        subset = data[data["region"] == region]
        # handle if there are no records for a region
        if not len(subset):
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
            }
            continue
        result[region] = {
            "avg_latency": float(subset["latency"].mean()),
            "p95_latency": float(np.percentile(subset["latency"], 95)),
            "avg_uptime": float(subset["uptime"].mean()),
            "breaches": int((subset["latency"] > threshold).sum()),
        }
    return result
