---
slug: baseline-quacksync
type: challenge
title: Baseline QuackSync
teaser: Run the sequential QuackSync pipeline, measure it, and make a prediction about where parallelism will help.
notes:
- type: text
  contents: |-
    # Meet QuackSync

    Over the next six modules you'll scale a single pipeline - **QuackSync** -
    one primitive at a time. It syncs the Quack Overflow rubber duck store's
    catalog into a local analytics database. For each duck it must:

    1. **Fetch** basic info from the Duck Catalog API
    2. **Enrich** it with pricing and stock from an external, rate-limited API
    3. **Score** it with a CPU-bound recommendation algorithm
    4. **Write** the record to a SQLite database with a connection pool of 5

    The version you'll start with is deliberately slow, deliberately
    sequential, and deliberately correct. That baseline is useful: every
    change you make later is only meaningful next to a number you trusted.

    Before you start tuning anything, you need to know where the time goes
    and why. Spend this module watching the pipeline run, classifying each
    stage as I/O-bound or CPU-bound, and writing a short prediction about
    where parallelism will help - and where it might hurt.
- type: text
  contents: |-
    # Two sides of scaling

    Every production pipeline eventually runs into the same tension:

    - **Throughput** says go faster. Fan out across cores and processes so
      independent work runs in parallel.
    - **Protection** says don't overwhelm the people downstream. Respect
      connection pools, API rate limits, and shared resources.

    Prefect gives you primitives for both sides, and part of being good at
    this is knowing when to reach for which one.

    By the end of Module 6 QuackSync will use `.submit()`, `.map()`,
    `ProcessPoolTaskRunner`, global concurrency limits, `rate_limit`, and
    deployment-level concurrency. Today you're only measuring, so you know
    what the next six modules are actually for.
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
difficulty: basic-intermediate
timelimit: 1800
---

# Run the sequential pipeline and measure it

The starter project is already installed at `/root/quacksync`. In this
challenge you'll start the mock APIs and a local Prefect server, run the
baseline flow against 50 ducks, and read the per-stage timing report the
flow prints at the end. The whole point of this exercise is that you can't
improve a number you haven't measured.

Before you change anything, form a hypothesis: which stages do you expect
parallelism to help? Which ones do you suspect will need a different tool?
You'll come back to this prediction at the end of the module.

## Step 1: Start the stack

A tiny helper script starts the QuackSync mock server on port 8000 and a
local Prefect server on port 4200. Running them in the background means you
can keep working in the same terminal.

```run
./start-stack.sh
```

You should see `Stack is up.` once both servers are ready. The Prefect UI
is available in the **Prefect UI** tab.

## Step 2: Look at the starter flow

Open `quacksync/flow.py` in the code editor. The interesting bit is the
loop inside `quacksync`:

```python
for duck_id in duck_ids:
    with stage("fetch"):
        duck = fetch_duck(duck_id)
    with stage("enrich"):
        duck = enrich_duck(duck)
    with stage("score"):
        duck = score_duck(duck)
    with stage("write"):
        write_duck(duck)
```

Every duck goes through every stage before the next duck starts. That is
correct - no partial writes, no shared-state bugs - but it's also the
slowest possible version of this pipeline. The `stage(...)` context manager
is a tiny helper that accumulates elapsed time per stage so you can see
where the runtime actually goes.

## Step 3: Run the baseline

Run the flow against the 50-duck seed file. Expect this to take roughly
30-45 seconds on the sandbox VM.

```run
uv run python -m quacksync.flow
```

You'll see Prefect log one task run per stage per duck. At the end the flow
logs a dictionary that looks like this:

```text
Stage timings (seconds): {'fetch': 3.1, 'enrich': 11.4, 'score': 18.7, 'write': 0.6}
```

Your numbers will differ, but the **shape** should match: enrichment and
scoring dominate, fetch is modest, and writing is nearly free.

## Step 4: Classify each stage

For each stage, decide whether it is I/O-bound or CPU-bound. This is the
single most important call you'll make in the rest of the course: it
determines which Prefect primitive is the right tool.

- `fetch_duck` calls the local Duck Catalog API over HTTP.
- `enrich_duck` calls the rate-limited Enrichment API over HTTP.
- `score_duck` runs a tight NumPy loop against a reference matrix.
- `write_duck` executes a single SQL `UPSERT` through the pool.

Write your classifications to `notes.md` with a one-sentence justification
per stage. The check script will look for this file with all four stages
mentioned. An example shape:

```text
fetch: I/O-bound - HTTP call, the CPU is idle most of the time
enrich: I/O-bound - another HTTP call, plus upstream rate limits
score:  CPU-bound - tight NumPy loop, no I/O to wait for
write:  I/O-bound - a single SQL statement through a connection pool
```

## Step 5: Write your hypothesis

At the bottom of `notes.md`, add a short paragraph titled
`## Prediction` that answers two questions:

1. Where do you expect parallelism to help most?
2. Where do you expect it to *cause* a new problem?

You'll revisit this prediction in Module 6 to see how close you were. The
check script looks for a `## Prediction` heading with at least a few
sentences of content - it doesn't grade the content itself.

## Verify

You should have:

- The mock server and Prefect server running in the background.
- `quacksync.db` created in `/root/quacksync` with 50 rows.
- `notes.md` in `/root/quacksync` with classifications for all four stages
  and a `## Prediction` section.

Click **Check** when the flow has finished and your notes are written.
