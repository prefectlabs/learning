"""QuackSync tasks.

The `@task` definitions are stable across modules - what changes module to
module is how `flow.py` composes them (sequential, `.submit()`, `.map()`,
with concurrency, with rate limits, etc.).
"""
from __future__ import annotations

import httpx
from prefect import task

from .database import pool
from .scoring import ScorerConfig, score_record

CATALOG_URL = "http://127.0.0.1:8000/ducks/{duck_id}"
ENRICH_URL = "http://127.0.0.1:8000/enrichment/{duck_id}"


@task
def fetch_duck(duck_id: int) -> dict:
    """Fetch basic duck info from the Duck Catalog API."""
    response = httpx.get(CATALOG_URL.format(duck_id=duck_id), timeout=5.0)
    response.raise_for_status()
    return response.json()


@task
def enrich_duck(duck: dict) -> dict:
    """Enrich a duck with pricing, stock, and review data.

    Raises on non-2xx responses. In Module 6, learners add a `rate_limit` and a
    `concurrency` block here so the calls stay within the Enrichment API's
    budget.
    """
    response = httpx.get(ENRICH_URL.format(duck_id=duck["id"]), timeout=5.0)
    response.raise_for_status()
    enrichment = response.json()
    return {**duck, **{k: v for k, v in enrichment.items() if k != "id"}}


@task
def score_duck(duck: dict) -> dict:
    """CPU-bound scoring step. Picklable by default."""
    duck["score"] = score_record(duck, ScorerConfig())
    return duck


@task
def write_duck(duck: dict) -> int:
    """Persist a scored duck. Protected by the DB pool (max 5) in Module 5."""
    pool.upsert_duck(duck)
    return duck["id"]
