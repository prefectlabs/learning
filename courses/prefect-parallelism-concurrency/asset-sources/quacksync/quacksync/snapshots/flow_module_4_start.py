"""Starting state for Module 4.

Fetch and enrich are mapped and partial failures are tolerated. Scoring and
writing are still sequential. In this module you'll swap in a
`ProcessPoolTaskRunner` for scoring so the CPU-bound step stops being the
bottleneck.
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, get_run_logger
from prefect.states import State

from .tasks import enrich_duck, fetch_duck, score_duck, write_duck

SEEDS = Path(__file__).parent / "seeds"


@flow(name="quacksync")
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks (mapped fetch+enrich)")

    fetched = fetch_duck.map(duck_ids)
    enriched_states: list[State] = enrich_duck.map(fetched, return_state=True)

    success_count = 0
    failed_ids: list[int] = []
    for duck_id, state in zip(duck_ids, enriched_states):
        if state.is_completed():
            duck = state.result()
            duck = score_duck(duck)
            write_duck(duck)
            success_count += 1
        else:
            failed_ids.append(duck_id)
            logger.warning(f"Enrichment failed for duck {duck_id}: {state.type}")

    return {
        "count": len(duck_ids),
        "succeeded": success_count,
        "failed": len(failed_ids),
        "failed_ids": failed_ids,
    }


if __name__ == "__main__":
    duck_ids = json.loads((SEEDS / "ducks_500.json").read_text())
    quacksync(duck_ids)
