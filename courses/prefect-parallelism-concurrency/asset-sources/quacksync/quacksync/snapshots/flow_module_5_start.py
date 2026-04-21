"""Starting state for Module 5.

Scoring now runs in a process pool. Fetch, enrich, and score are all
parallel - but writes are still serial. In this module you'll map
`write_duck` across scored ducks and discover that the `DatabasePool` only
allows 5 concurrent connections. You'll fix it with a global concurrency
limit.
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, get_run_logger
from prefect.states import State
from prefect.task_runners import ProcessPoolTaskRunner

from .tasks import enrich_duck, fetch_duck, score_duck, write_duck

SEEDS = Path(__file__).parent / "seeds"


@flow(name="quacksync", task_runner=ProcessPoolTaskRunner(max_workers=4))
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks (parallel fetch, enrich, score)")

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
        duck = future.result()
        write_duck(duck)

    return {
        "count": len(duck_ids),
        "succeeded": len(scored),
        "failed": len(failed_ids),
    }


if __name__ == "__main__":
    duck_ids = json.loads((SEEDS / "ducks_500.json").read_text())
    quacksync(duck_ids)
