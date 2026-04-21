---
slug: scale-with-map
type: challenge
title: Scale to 500 Ducks with .map()
teaser: Swap submit-in-a-loop for .map(), scale to 500 ducks, and survive the ~25 poisoned enrichments without killing the flow.
notes:
- type: text
  contents: |-
    # .map() vs submit-in-a-loop

    `task.map(iterable)` is Prefect's idiomatic way to apply a task across
    many inputs. It's the same fan-out you built by hand in Module 2, with
    three things made nicer:

    - One line instead of a list comprehension.
    - Clear semantics for which arguments are "mapped" (one per call) and
      which are "unmapped" (the same value passed to every call - wrap
      those in `unmapped(...)`).
    - First-class support for collecting states, not just results, so you
      can route around failures.

    Use `.map()` when you have an iterable of inputs and want one task run
    per item. Use `.submit()` when the shape is more ad hoc - different
    tasks, different arguments, conditional submission.
- type: text
  contents: |-
    # Partial failure is the hard part

    At scale, *something* will fail. The Enrichment API in QuackSync fails
    intentionally for about 25 of the 500 duck IDs in this module's seed
    file. The goal is not to prevent the failures. The goal is to finish
    the 475 successful ducks, log enough context to triage the 25 that
    failed, and return a structured summary so a downstream system (or a
    human on-call) can act on it.

    This is what production pipelines look like. A fail-the-whole-flow
    policy makes sense for one-duck personal scripts - not for a 500-duck
    nightly sync that nobody should have to re-run from scratch because of
    one bad row.
tabs:
- title: "Terminal"
  type: terminal
  hostname: prefect-sandbox
  workdir: /root/quacksync
- title: "Code Editor"
  type: code
  hostname: prefect-sandbox
  path: /root/quacksync
- title: "Prefect UI"
  type: browser
  hostname: prefect-ui
difficulty: intermediate
timelimit: 2400
---

# Refactor to .map() and handle 500 ducks

Module 2 gave you a parallel fetch and enrich pipeline using
`.submit()` inside list comprehensions. It works, but it hides what you're
actually expressing: "run this task for each item in a list." Prefect has a
primitive that says exactly that - `task.map(...)` - and using it makes
both the intent and the failure handling cleaner.

In this challenge you'll convert the fetch-and-enrich chain to `.map()`,
scale the seed up to 500 ducks, and handle the ~25 duck IDs whose
enrichment deliberately raises. Scoring and writing stay in a plain loop
for now - you'll fix those in Modules 4 and 5.

## Step 1: Start the stack

```run
./start-stack.sh
```

## Step 2: Replace the comprehensions with `.map()`

Open `quacksync/flow.py`. Where the Module 2 code had a list comprehension
with `.submit()`, the `.map()` version is one line shorter and reads like
what it does:

```python
from prefect import flow, get_run_logger

from .tasks import enrich_duck, fetch_duck, score_duck, write_duck


@flow(name="quacksync")
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks (mapped)")

    fetched = fetch_duck.map(duck_ids)
    enriched = enrich_duck.map(fetched)

    for future in enriched:
        duck = future.result()
        duck = score_duck(duck)
        write_duck(duck)

    return {"count": len(duck_ids)}
```

`.map()` returns a list of futures in the order of the input. Passing
`fetched` (a list of futures) into `enrich_duck.map(...)` gives Prefect the
dependency for each item automatically, exactly like chained `.submit()`
did last module.

## Step 3: Scale to 500 ducks

Change the entry point at the bottom of `flow.py` to use the 500-duck seed
file. This is where the run is large enough for failures to appear.

```python
if __name__ == "__main__":
    duck_ids = json.loads((SEEDS / "ducks_500.json").read_text())
    quacksync(duck_ids)
```

Run it. You will see a flood of task runs - and a pile of red failures
from the ~25 poisoned IDs that the Enrichment API is intentionally
rejecting.

```run
uv run python -m quacksync.flow
```

The flow will almost certainly stop short of 500 writes because a failure
in the middle of the second loop will raise on `.result()`. That's the
next thing you'll fix.

## Step 4: Tolerate per-item failures

`.map()` supports `return_state=True`, which gives you a list of
`State` objects instead of futures. States know whether the task succeeded
or failed, so you can branch without triggering the exception.

Update the flow to route around failures:

```python
from prefect.states import State


@flow(name="quacksync")
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks (map with partial failure)")

    fetched = fetch_duck.map(duck_ids)
    enriched_states: list[State] = enrich_duck.map(fetched, return_state=True)

    succeeded = 0
    failed_ids: list[int] = []
    for duck_id, state in zip(duck_ids, enriched_states):
        if state.is_completed():
            duck = state.result()
            duck = score_duck(duck)
            write_duck(duck)
            succeeded += 1
        else:
            failed_ids.append(duck_id)
            logger.warning(f"Enrichment failed for duck {duck_id}: {state.type}")

    summary = {
        "total": len(duck_ids),
        "succeeded": succeeded,
        "failed": len(failed_ids),
        "failed_ids": failed_ids,
    }
    logger.info(f"RunSummary: {summary}")
    return summary
```

Run the flow again.

```run
uv run python -m quacksync.flow
```

The flow should finish. You'll see ~475 writes, a list of ~25 failed IDs
in the logs, and the `RunSummary` dict returned at the end. The exact
count depends on the mock's poison list.

## Step 5: Confirm the outcome in the database

The success count in the logs should match the row count in the database.

```run
sqlite3 quacksync.db 'SELECT COUNT(*) FROM ducks;'
```

If that number is in the 470-479 range, you're in great shape. If it's
500, the mock isn't rejecting anything and something is wrong. If it's
much lower, you probably have a different bug - re-check that score and
write happen inside the `state.is_completed()` branch.

## Verify

You should see:

- `flow.py` calls `fetch_duck.map(...)` and `enrich_duck.map(...)`.
- `enrich_duck.map` uses `return_state=True`.
- The database has somewhere in the neighborhood of 475 rows.
- The returned summary dict contains the failed duck IDs.
