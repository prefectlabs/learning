---
slug: concurrency-limits
type: challenge
title: Concurrency Limits Protect the Database
teaser: Map writes across 500 ducks, watch the connection pool explode, then throttle writes with a global concurrency limit.
notes:
- type: text
  contents: |-
    # Why you'd ever throttle a parallel flow

    Most scaling lessons are about going faster. This module is about
    going slower - on purpose. The QuackSync SQLite pool allows up to 5
    concurrent connections, because real databases have real connection
    pools and real downstream systems have real capacity. If you open 50
    connections at once you don't "win" - you get refused with a
    `ConnectionPoolExhausted` error and half your writes disappear.

    Concurrency limits in Prefect let a flow be aggressively parallel
    *and* polite to the things it depends on. You decide how many task
    runs can touch a resource at a time; Prefect queues the rest.
- type: text
  contents: |-
    # Levels of concurrency control

    Prefect gives you concurrency at four levels. Know them so you can
    reach for the right one:

    - **Global concurrency limits**: named, reusable slots shared across
      flows. Great for "at most N writers to the DB, ever."
    - **Tag-based task limits**: any task with a given tag counts against
      a shared pool. Great for team-wide conventions.
    - **Work pool concurrency**: caps how many flow runs execute on a
      worker pool at once.
    - **Deployment concurrency**: caps how many runs of a specific
      deployment execute at once.

    You'll use the first one today, and touch the fourth in Module 6.
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

# Protect the connection pool with a concurrency limit

QuackSync is now aggressively parallel on the read side: fetch and enrich
are mapped, scoring runs in a process pool. The last stage - `write_duck`
- is still sequential, which is the only reason you haven't been seeing
pool-exhaustion errors yet.

In this module you'll map `write_duck`, watch it crash, and then fix it
the right way: a global concurrency limit named `db-writes` that caps
concurrent writers to 5. The work still fans out, but Prefect queues
tasks as they wait for a slot, so the database never sees more than five
in-flight connections.

## Step 1: Start the stack

```run
./start-stack.sh
```

## Step 2: Map the writes and watch it fail

Open `quacksync/flow.py`. Replace the write loop with a mapped call:

```python
write_futures = write_duck.map(scored_futures)
for future in write_futures:
    future.result()
```

Run the flow.

```run
uv run python -m quacksync.flow
```

You'll see a batch of `write_duck` tasks fail with
`ConnectionPoolExhausted: Pool exhausted: 5/5 in use`. Depending on the
order of scheduling, somewhere between a handful and most of your writes
will succeed; the rest raise. This is exactly the class of failure a naive
fan-out produces against any real connection pool.

## Step 3: Create the global concurrency limit

Global concurrency limits live at the Prefect server. You create them
with the CLI. Name the limit `db-writes` and give it 5 slots - the same
as the DB pool.

```run
uv run prefect gcl create db-writes --limit 5
```

You can see it in the Prefect UI under **Concurrency**, and inspect it
from the CLI:

```run
uv run prefect gcl inspect db-writes
```

## Step 4: Acquire a slot inside `write_duck`

The simplest way to enforce the limit is the `concurrency()` context
manager. Wrap the database call so each task has to acquire a slot
before it runs its SQL statement.

Update `quacksync/tasks.py`:

```python
from prefect.concurrency.sync import concurrency

@task
def write_duck(duck: dict) -> int:
    with concurrency("db-writes", occupy=1):
        pool.upsert_duck(duck)
    return duck["id"]
```

`occupy=1` says this task uses one slot. When all 5 slots are in use,
additional tasks block inside the context manager until someone releases.

Run the flow again:

```run
uv run python -m quacksync.flow
```

Every successful duck should now land in the database with zero
connection-pool errors. The Prefect UI's concurrency view shows `db-writes`
filling to 5 and draining in batches.

## Step 5: Confirm the end state

The count in the database should match the number of enriched (non-poisoned)
ducks.

```run
sqlite3 quacksync.db 'SELECT COUNT(*) FROM ducks;'
```

That number should be in the mid-470s and stable - no connection-pool
errors, no missing rows.

## Verify

You should have:

- A global concurrency limit named `db-writes` with 5 slots.
- `tasks.py` wraps the database call in `concurrency("db-writes", ...)`.
- `flow.py` calls `write_duck.map(...)` (no more serial write loop).
- The database has around 475 rows and the flow run in the Prefect UI
  shows zero failed writes.
