"""QuackSync mock server.

Serves two APIs on localhost:8000:

- /ducks/{id}            - Duck Catalog API. Always fast and permissive.
- /enrichment/{id}       - Enrichment API. Enforces:
    * 10 requests per rolling second across all callers
    * 3 concurrent in-flight requests
    * Returns realistic HTTP 429 responses when limits are violated
    * 500 for the ~25 "poisoned" IDs used in Module 3

Everything is deterministic per duck id so learners get the same numbers.
"""
from __future__ import annotations

import asyncio
import random
import time
from collections import deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# --- Config ----------------------------------------------------------------

ENRICH_RPS_LIMIT = 10
ENRICH_CONCURRENCY = 3
BASE_ENRICH_LATENCY_MS = 200  # realistic external API latency

# A fixed set of ~25 duck IDs whose enrichment fails. Learners hit these in
# Module 3 when they scale to 500 ducks.
POISON_IDS = {
    7, 13, 29, 42, 66, 101, 117, 144, 189, 213,
    247, 266, 289, 301, 337, 360, 388, 411, 433, 457,
    469, 478, 481, 492, 499,
}

# --- Shared state ----------------------------------------------------------

_request_times: deque[float] = deque()
_concurrency_sem = asyncio.Semaphore(ENRICH_CONCURRENCY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan, title="QuackSync Mock Server")


# --- Duck Catalog API ------------------------------------------------------


@app.get("/ducks/{duck_id}")
async def get_duck(duck_id: int) -> dict:
    """Fast, always-successful catalog lookup."""
    await asyncio.sleep(0.05)
    rng = random.Random(duck_id)
    return {
        "id": duck_id,
        "name": f"Duck #{duck_id}",
        "color": rng.choice(["yellow", "blue", "red", "green", "pink", "black"]),
        "size": rng.choice(["small", "medium", "large"]),
    }


# --- Enrichment API --------------------------------------------------------


def _check_rate_limit() -> None:
    """Trim the rolling window and raise 429 if the RPS limit is exceeded."""
    now = time.monotonic()
    while _request_times and now - _request_times[0] > 1.0:
        _request_times.popleft()
    if len(_request_times) >= ENRICH_RPS_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {ENRICH_RPS_LIMIT} requests/second",
            headers={"Retry-After": "1"},
        )
    _request_times.append(now)


@app.get("/enrichment/{duck_id}")
async def enrich(duck_id: int) -> JSONResponse:
    """Rate and concurrency limited enrichment lookup."""
    _check_rate_limit()

    if _concurrency_sem.locked():
        raise HTTPException(
            status_code=429,
            detail=(
                f"Concurrency limit exceeded: only {ENRICH_CONCURRENCY} "
                "in-flight requests allowed"
            ),
            headers={"Retry-After": "1"},
        )

    async with _concurrency_sem:
        await asyncio.sleep(BASE_ENRICH_LATENCY_MS / 1000)

        if duck_id in POISON_IDS:
            raise HTTPException(
                status_code=500,
                detail=f"Enrichment failed for duck {duck_id} (poisoned)",
            )

        rng = random.Random(duck_id * 31 + 7)
        return JSONResponse(
            {
                "id": duck_id,
                "price_cents": 500 + rng.randint(0, 4500),
                "stock": rng.randint(0, 200),
                "rating": round(rng.uniform(3.0, 5.0), 2),
                "reviews": rng.randint(0, 2000),
            }
        )


@app.exception_handler(HTTPException)
async def _passthrough(_: Request, exc: HTTPException) -> JSONResponse:
    headers = exc.headers or {}
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
