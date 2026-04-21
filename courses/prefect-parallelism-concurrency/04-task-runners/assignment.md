---
slug: task-runners
type: challenge
title: Task Runners for the CPU-Bound Step
teaser: Move the scoring step onto a ProcessPoolTaskRunner, benchmark it against threads, and debug a real pickling error.
notes:
- type: text
  contents: |-
    # The task runner picks your parallelism model

    Prefect has two built-in single-machine task runners:

    - `ThreadPoolTaskRunner` (the default). Great for I/O-bound work -
      waiting on HTTP, DB, disk. The GIL is fine because those tasks
      spend most of their time waiting, not computing.
    - `ProcessPoolTaskRunner`. Uses real OS processes, so Python bytecode
      runs in parallel across cores. Required for CPU-bound work. The
      cost is that arguments and return values must be pickleable.

    QuackSync's `score_duck` is a tight NumPy loop. Threads can't help you
    here because the GIL keeps only one Python bytecode executing at a
    time. This is the module where the choice of task runner stops being
    trivia and starts showing up in wall-clock time.
- type: text
  contents: |-
    # Pickling and why people get surprised

    `ProcessPoolTaskRunner` sends arguments and results between processes
    using pickle. Most things pickle fine: ints, strings, dicts, lists,
    dataclasses, NumPy arrays, your own simple classes.

    The things that *don't* pickle are usually the things that own OS
    resources: open files, database connections, sockets, threading locks,
    local functions, lambdas. When a task returns or receives one of these,
    you'll see a very loud `TypeError: cannot pickle ...` the first time
    you switch runners.

    That's not a Prefect quirk - it's how process pools have always worked
    in Python. Knowing what to look for saves a lot of time.
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
timelimit: 2700
---

# Unlock the scoring step with a process pool

Module 3 left scoring as a serial loop at the bottom of the flow. Even
though fetch and enrich are mapped and concurrent, scoring now dominates
runtime because it's CPU-bound and still runs one duck at a time. This
module is where you finally parallelize it - and pick the right runner for
the job.

You'll start by mapping `score_duck` under the default thread pool and see
how the GIL caps the speedup. Then you'll switch to
`ProcessPoolTaskRunner`, hit a real pickling error that's been quietly
waiting for you in the tasks module, debug it, and finally measure the
speedup.

## Step 1: Start the stack

```run
./start-stack.sh
```

## Step 2: Map the scoring step under the default runner

Open `quacksync/flow.py`. Replace the score-and-write loop with a `.map()`
call for `score_duck` so at least *something* is happening concurrently
there.

The interesting part of the flow body should look like this:

```python
fetched = fetch_duck.map(duck_ids)
enriched_states: list[State] = enrich_duck.map(fetched, return_state=True)

enriched = []
failed_ids: list[int] = []
for duck_id, state in zip(duck_ids, enriched_states):
    if state.is_completed():
        enriched.append(state.result())
    else:
        failed_ids.append(duck_id)

scored_futures = score_duck.map(enriched)

for future in scored_futures:
    write_duck(future.result())
```

Run it and time it. The default runner is threads, and because scoring is
CPU-bound you should see only a modest improvement:

```run
time uv run python -m quacksync.flow
```

Jot down the elapsed time. This is your thread-pool baseline for the
scoring step.

## Step 3: Switch to a process pool

At the top of `flow.py`, import the process pool runner and set it on the
flow:

```python
from prefect.task_runners import ProcessPoolTaskRunner

@flow(name="quacksync", task_runner=ProcessPoolTaskRunner(max_workers=4))
def quacksync(duck_ids: list[int]) -> dict:
    ...
```

Run the flow again.

```run
time uv run python -m quacksync.flow
```

It will fail. Look at the traceback - you'll see something like:

```text
TypeError: cannot pickle '_thread.lock' object
```

This is not a Prefect bug. Someone (me) added a `threading.Lock` to the
return value of `score_duck` in `tasks.py`. When a thread pool ran the
flow nobody noticed because nothing ever crossed a process boundary. The
moment you flipped the runner to processes, every return value has to be
picklable - and locks aren't.

## Step 4: Find and fix the pickling bug

Open `quacksync/tasks.py`. You'll see something like this at the top:

```python
from threading import Lock

class DuckResult(dict):
    def __init__(self, data):
        super().__init__(data)
        self._lock = Lock()
```

And `score_duck` returns a `DuckResult(...)`. That lock is never used for
anything. Remove the class and have `score_duck` return a plain dict:

```python
@task
def score_duck(duck: dict) -> dict:
    duck["score"] = score_record(duck, ScorerConfig())
    return duck
```

Make sure the `from threading import Lock` import is gone too - linters
will flag the unused import otherwise.

Now re-run with the process pool:

```run
time uv run python -m quacksync.flow
```

You should see no pickling error, a noticeable drop in wall-clock time on
the scoring stage, and the usual ~475 rows in the database.

## Step 5: Record your results

Create `results-module-4.md` in `/root/quacksync` with your three numbers:

```text
# Module 4 results

| Runner                    | Elapsed (seconds) |
|---------------------------|-------------------|
| Thread pool (sequential)  |                   |
| Thread pool (.map)        |                   |
| Process pool (.map)       |                   |

For QuackSync in production, I would pick ... because ...
```

You don't have to re-time the sequential version if you still have it
from Module 1 - just copy that number.

## Verify

You should have:

- `flow.py` calls `score_duck.map(...)` and sets
  `task_runner=ProcessPoolTaskRunner(...)`.
- `tasks.py` no longer imports `threading.Lock` or returns a `DuckResult`.
- The flow completes end-to-end with ~475 rows in the database.
- `results-module-4.md` exists with a comparison table.
