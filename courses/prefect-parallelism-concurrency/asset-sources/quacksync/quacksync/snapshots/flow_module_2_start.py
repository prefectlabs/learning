"""Starting state for Module 2.

Identical to the Module 1 baseline: fully sequential. Your job in this module
is to replace the fetch and enrich loops with `.submit()` and chain the
futures so Prefect can run them concurrently.
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, get_run_logger

from .tasks import enrich_duck, fetch_duck, score_duck, write_duck

SEEDS = Path(__file__).parent / "seeds"


@flow(name="quacksync")
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks sequentially")

    for duck_id in duck_ids:
        duck = fetch_duck(duck_id)
        duck = enrich_duck(duck)
        duck = score_duck(duck)
        write_duck(duck)

    return {"count": len(duck_ids)}


if __name__ == "__main__":
    duck_ids = json.loads((SEEDS / "ducks_50.json").read_text())
    quacksync(duck_ids)
