import asyncio
import random
import time

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

app = FastAPI()

# --- Metric definitions (create once, at module level) ---------------------
REQS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
LAT = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Requests currently being processed",
)
ORDERS = Counter("orders_created_total", "Orders created (business metric)")


# --- Middleware: records every request -------------------------------------
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    if request.url.path == "/metrics":      # don't measure the scrape itself
        return await call_next(request)

    IN_PROGRESS.inc()
    start = time.perf_counter()
    status = 500                            # assume failure unless we get a response
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        elapsed = time.perf_counter() - start
        # Use the route template (/items/{id}), not the raw URL (/items/42),
        # so label values stay bounded.
        route = request.scope.get("route")
        path = route.path if route else "unmatched"
        REQS.labels(request.method, path, str(status)).inc()
        LAT.labels(request.method, path).observe(elapsed)
        IN_PROGRESS.dec()


# --- Metrics endpoint ------------------------------------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# --- Sample routes so you have traffic to look at (replace with your own) --
@app.get("/")
def home():
    return {"hello": "world"}


@app.get("/slow")
async def slow():
    await asyncio.sleep(random.uniform(0.05, 1.5))
    return {"ok": True}


@app.get("/error")
def error():
    raise HTTPException(status_code=500, detail="boom")


@app.post("/orders")
def create_order():
    ORDERS.inc()
    return {"created": True}
