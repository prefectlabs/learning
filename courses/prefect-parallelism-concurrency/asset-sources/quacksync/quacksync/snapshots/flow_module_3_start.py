"""Starting state for Module 3.

Module 2 left fetch and enrich parallelized via `.submit()` in a loop, with
scoring and writing still sequential. In this module you'll replace the
`.submit()` loops with `.map()`, scale to 500 ducks, and handle partial
failures from the ~25 poisoned duck IDs.
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
    logger.info(f"Processing {len(duck_ids)} ducks (submit fan-out)")

    fetched = [fetch_duck.submit(duck_id) for duck_id in duck_ids]
    enriched = [enrich_duck.submit(f) for f in fetched]

    for future in enriched:
        duck = future.result()
        duck = score_duck(duck)
        write_duck(duck)

    return {"count": len(duck_ids)}


if __name__ == "__main__":
    duck_ids = json.loads((SEEDS / "ducks_50.json").read_text())
    quacksync(duck_ids)
