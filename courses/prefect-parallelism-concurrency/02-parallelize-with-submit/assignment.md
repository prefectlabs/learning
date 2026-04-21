---
slug: parallelize-with-submit
type: challenge
title: Parallelize with .submit()
teaser: Fan out the fetch and enrich stages with PrefectFutures, then chain them so Prefect infers the dependency.
notes:
- type: text
  contents: |-
    # Calling vs submitting

    When you call a Prefect task the normal way - `duck = fetch_duck(duck_id)`
    - it runs right now, on the calling thread, and blocks until the result
    is ready. That's great for correctness, terrible for throughput.

    Calling `task.submit(...)` instead hands the work to the flow's task
    runner and returns a `PrefectFuture` immediately. Your flow keeps going,
    submits the next task, and only blocks when something actually needs the
    result. That's the unlock for parallelism in Prefect.

    The future is the thing you pass around. It knows which task is running,
    its current state, and how to retrieve the eventual value. You can also
    pass a future *into* another task's `submit(...)`, and Prefect will
    automatically infer the dependency for you.
- type: text
  contents: |-
    # The two classic pitfalls

    Most "my flow isn't actually parallel" bugs fall into one of two
    patterns:

    1. **Calling `.result()` inside the submission loop.** The loop blocks
       on every iteration, so you get a sequential flow wearing a parallel
       costume.
    2. **Forgetting that `.submit()` doesn't block.** You assume the loop
       finished the work when it actually just queued it.

    You'll intentionally hit the first pitfall in this module so you can see
    the timings collapse, and then you'll fix it.
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

# Fan out fetch and enrich with futures

The Module 1 flow is sequential on purpose. The fetch and enrich stages are
both I/O-bound, which means most of their time is spent waiting on HTTP
responses. Running them one at a time is the single cheapest mistake in the
pipeline. In this challenge you'll fix it using `.submit()` and future
chaining, then you'll stumble into - and repair - the classic "my flow
isn't actually parallel" bug.

You'll still leave scoring and writing sequential. Parallelizing them is
the next two modules' job, and doing it now would just mask the teaching
here.

## Step 1: Start fresh

The stack from Module 1 may already be running, but let's make sure it is.
The helper will no-op if both servers are already up.

```run
./start-stack.sh
```

## Step 2: Submit fetch in parallel

Open `quacksync/flow.py`. Replace the fetch loop with a call to
`fetch_duck.submit(...)`. `submit` returns a future right away, so the
entire loop finishes in milliseconds even if the underlying HTTP calls
haven't returned yet.

Change the body of `quacksync` to this:

```python
@flow(name="quacksync")
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks (fetch parallel)")

    fetch_futures = [fetch_duck.submit(duck_id) for duck_id in duck_ids]

    for future in fetch_futures:
        duck = future.result()
        duck = enrich_duck(duck)
        duck = score_duck(duck)
        write_duck(duck)

    return {"count": len(duck_ids)}
```

Run it and compare the wall-clock time to your Module 1 baseline.

```run
time uv run python -m quacksync.flow
```

You should see fetch finish fast in parallel, with enrich/score/write still
sequential - so the total runtime should shrink, but not dramatically yet.

## Step 3: Chain fetch into enrich

You can do better. Pass the fetch future directly into
`enrich_duck.submit(...)`. Prefect sees the future, treats it as a
dependency, and waits for it to resolve before the enrich task runs.
Crucially, enrich tasks **also** run concurrently with each other because
each one only depends on its own upstream fetch.

Replace the loop with this:

```python
@flow(name="quacksync")
def quacksync(duck_ids: list[int]) -> dict:
    logger = get_run_logger()
    logger.info(f"Processing {len(duck_ids)} ducks (fetch+enrich parallel)")

    fetch_futures = [fetch_duck.submit(duck_id) for duck_id in duck_ids]
    enrich_futures = [enrich_duck.submit(f) for f in fetch_futures]

    for future in enrich_futures:
        duck = future.result()
        duck = score_duck(duck)
        write_duck(duck)

    return {"count": len(duck_ids)}
```

Notice that `enrich_futures` contains one future per duck and we only call
`.result()` at the point where score actually needs the value. The second
loop still forces serial scoring and writing - that's intentional, those
are the next two modules.

## Step 4: See what happens when you `.result()` too early

Prefect's behavior here is subtle, and writing it wrong silently undoes the
parallelism. Introduce the bug on purpose so you can recognize it in your
own code later.

Temporarily change the enrich line to this:

```python
enriched = [enrich_duck.submit(f.result()) for f in fetch_futures]
```

Now each iteration of the list comprehension blocks until the fetch for
*that* duck is done before submitting the next fetch at all. You've
accidentally reintroduced a sequential step. Run the flow and confirm the
runtime went back up.

```run
time uv run python -m quacksync.flow
```

Now revert the change - remove the `.result()` call so `enrich_duck.submit`
receives the future directly, the way it was before.

## Step 5: Commit the working version

Once the chained version is back in place, do one final clean run on the
50-duck seed. The check script will look for `.submit(` in `flow.py` to
confirm you're using futures and will run a fresh flow.

```run
time uv run python -m quacksync.flow
```

## Verify

You should see:

- `flow.py` uses `fetch_duck.submit(...)` and `enrich_duck.submit(...)`.
- `fetch_duck.submit` receives a raw `duck_id` (no `.result()` inside the
  comprehension).
- `enrich_duck.submit` receives a future, not a resolved value.
- Runtime on 50 ducks is noticeably faster than the Module 1 baseline.
- 50 rows in `quacksync.db`.
