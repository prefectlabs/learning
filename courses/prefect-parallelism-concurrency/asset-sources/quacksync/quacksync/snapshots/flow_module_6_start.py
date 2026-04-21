"""Starting state for Module 6.

All four stages are now parallel and the database pool is protected by a
`db-writes` concurrency limit. The one thing still broken: we're hammering
the Enrichment API and eating 429s silently. In this module you'll add a
rate limit and a concurrency limit around enrichment, then deploy QuackSync
with deployment-level concurrency.
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, get_run_logger
from prefect.concurrency.sync import concurrency
from prefect.states import State
from prefect.task_runners import ProcessPoolTaskRunner

from .database import pool
from .scoring import ScorerConfig, score_record
from .tasks import enrich_duck, fetch_duck, score_duck

SEEDS = Path(__file__).parent / "seeds"


def _write_with_limit(duck: dict) -> int:
    with concurrency("db-writes"):
        pool.upsert_duck(duck)
    return duck["id"]


@flow(name="quacksync", task_runner=ProcessPoolTaskRunner(max_workers=4))
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks (all parallel, DB protected)")

    fetched = fetch_duck.map(duck_ids)
    enriched_states: list[State] = enrich_duck.map(fetched, return_state=True)

    scored = []
    failed_ids: list[int] = []
    for duck_id, state in zip(duck_ids, enriched_states):
        if state.is_completed():
            scored.append(score_duck.submit(state.result()))
        else:
            failed_ids.append(duck_id)

    for future in scored:
        _write_with_limit(future.result())

    return {
        "count": len(duck_ids),
        "succeeded": len(scored),
        "failed": len(failed_ids),
    }


if __name__ == "__main__":
    duck_ids = json.loads((SEEDS / "ducks_500.json").read_text())
    quacksync(duck_ids)
