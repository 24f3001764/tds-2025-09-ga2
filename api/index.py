from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data on startup (adjust path/content for your bundle)
import pandas as pd

telemetry = pd.read_json("q-vercel-latency.json")  # Place your actual JSON here

@app.post("/")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    results = {}

    for region in regions:
        df = telemetry[telemetry["region"] == region]
        avg_latency = float(df["latency"].mean())
        p95_latency = float(np.percentile(df["latency"], 95))
        avg_uptime = float(df["uptime"].mean())
        breaches = int((df["latency"] > threshold).sum())

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
    return results
