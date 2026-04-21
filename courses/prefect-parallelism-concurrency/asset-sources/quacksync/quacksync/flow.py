"""Sequential baseline flow. This is what learners start with in Module 1.

Every module replaces this file (or the relevant portion of it) with a more
scaled, better-behaved version.
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, get_run_logger

from .profile import report, stage
from .tasks import enrich_duck, fetch_duck, score_duck, write_duck

SEEDS = Path(__file__).parent / "seeds"


@flow(name="quacksync")
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks sequentially")

    for duck_id in duck_ids:
        with stage("fetch"):
            duck = fetch_duck(duck_id)
        with stage("enrich"):
            duck = enrich_duck(duck)
        with stage("score"):
            duck = score_duck(duck)
        with stage("write"):
            write_duck(duck)

    timings = report()
    logger.info(f"Stage timings (seconds): {timings}")
    return {"count": len(duck_ids), "stage_timings": timings}


if __name__ == "__main__":
    duck_ids = json.loads((SEEDS / "ducks_50.json").read_text())
    quacksync(duck_ids)
