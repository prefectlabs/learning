---
slug: rate-limits-capstone
type: challenge
title: Rate Limits & the QuackSync Capstone
teaser: Add rate limits and retries around the Enrichment API, then deploy QuackSync with deployment-level concurrency.
notes:
- type: text
  contents: |-
    # Rate limit vs concurrency limit

    People mix these up all the time. They solve different problems:

    - **Concurrency limit**: "At most N in-flight at a time." Great for
      connection pools, GPU slots, licensed seats.
    - **Rate limit**: "At most N per time window." Great for external
      APIs that publish RPS/RPM budgets, paid APIs where cost tracks
      volume, or systems that penalize bursts.

    QuackSync's Enrichment API enforces **both**: 10 requests per second
    **and** 3 concurrent connections. That's why you need both
    primitives, not one or the other.
- type: text
  contents: |-
    # The capstone

    By the end of this module, QuackSync will be:

    - Fully parallel across fetch, enrich, and score.
    - Polite to the database (5 concurrent writers).
    - Polite to the Enrichment API (10 RPS and 3 concurrent connections,
      with retries and jitter for residual 429s).
    - Deployed with a deployment-level concurrency cap so three
      back-to-back triggers don't try to run three flows at once.

    That's the shape of a production pipeline: aggressive where it can
    be, protective where it must be, and observable throughout.
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
difficulty: intermediate-advanced
timelimit: 3000
---

# Tame the Enrichment API and ship QuackSync

The mock Enrichment API has been quietly enforcing its limits the entire
course: 10 requests per second, 3 concurrent connections, and a clear 429
response when either is violated. Modules 3-5 worked despite that because
fetch and enrich ran at modest fan-out; once you're mapping 500 ducks in
parallel with a process pool, you're now hammering it and eating 429s
(silently retrying, or just failing). You'll fix that here.

Then you'll package QuackSync as a Prefect deployment with a concurrency
cap of 2, so the operator gets a guarantee that three back-to-back
triggers will still only run two at a time.

## Part A: Tame the Enrichment API

### Step 1: Start the stack and measure the damage

```run
./start-stack.sh
```

Run the flow once before changing anything so you can see the 429s in the
mock server logs and the failed task runs in the Prefect UI.

```run
uv run python -m quacksync.flow
```

In the terminal you should see warnings about failed enrichments beyond
the usual 25 poisoned IDs. Those extras are 429s, not real failures.

### Step 2: Add a rate limit and a concurrency block to `enrich_duck`

Both limits live at the Prefect server. Create them:

```run
uv run prefect gcl create enrichment-api-rps --limit 10 --slot-decay-per-second 10
uv run prefect gcl create enrichment-api-conns --limit 3
```

The RPS limit uses `slot-decay-per-second 10` so slots replenish at 10
per second - that's how Prefect turns a named limit into a true rate
limit. The concurrency limit is a classic "at most 3 in flight" slot pool.

Now wrap the HTTP call in `enrich_duck`. Update `quacksync/tasks.py`:

```python
from prefect.concurrency.sync import concurrency, rate_limit

@task(retries=3, retry_delay_seconds=[1, 2, 4], retry_jitter_factor=0.5)
def enrich_duck(duck: dict) -> dict:
    rate_limit("enrichment-api-rps", occupy=1)
    with concurrency("enrichment-api-conns", occupy=1):
        response = httpx.get(ENRICH_URL.format(duck_id=duck["id"]), timeout=5.0)
        response.raise_for_status()
    enrichment = response.json()
    return {**duck, **{k: v for k, v in enrichment.items() if k != "id"}}
```

Three things are doing work there:

- `rate_limit("enrichment-api-rps", occupy=1)` acquires one slot against
  the replenishing pool. If the caller is ahead of budget, it blocks
  until a slot is available. This is the "no more than 10 per second"
  half.
- `concurrency("enrichment-api-conns", occupy=1)` keeps at most 3
  in-flight enrichments at any moment. This is the "no more than 3
  connections" half.
- Retries with exponential backoff and jitter handle residual 429s from
  the edges of the rate-limit window. Jitter is important - without it
  every retry collides at exactly the same tick.

### Step 3: Run and verify zero 429s

Delete the old database and re-run against 500 ducks.

```run
rm -f quacksync.db
uv run python -m quacksync.flow
```

Check the mock server terminal output - you should see a steady trickle
of requests and no 429 entries. The only failed ducks should be the ~25
poisoned IDs. The runtime will be longer than in Module 5 (the rate limit
bounds throughput to 10 RPS on that stage) and that's the correct
outcome: respecting the limit is the whole point.

## Part B: Ship it

### Step 4: Create a deployment with a concurrency cap

Add a deployment at the bottom of `flow.py` so QuackSync can be triggered
on a schedule. The concurrency cap is set directly on the deployment so
it survives restarts of the worker process.

```python
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        quacksync.deploy(
            name="quacksync-local",
            work_pool_name="default",
            cron="*/15 * * * *",
            concurrency_limit=2,
        )
    else:
        duck_ids = json.loads((SEEDS / "ducks_500.json").read_text())
        quacksync(duck_ids)
```

Create the `default` work pool and register the deployment.

```run
uv run prefect work-pool create default --type process --overwrite
uv run python -m quacksync.flow deploy
```

### Step 5: Confirm the concurrency guarantee

Trigger three runs back-to-back and confirm only two execute at a time.

```run
uv run prefect deployment run quacksync/quacksync-local
uv run prefect deployment run quacksync/quacksync-local
uv run prefect deployment run quacksync/quacksync-local
```

In the Prefect UI, under **Deployments -> quacksync-local**, you should
see two runs in **Running** state and one sitting in **AwaitingConcurrencySlot**
until a slot opens.

You don't need to wait for all three to complete for the check to pass -
the deployment registration, the concurrency cap, and the rate-limit
names are what the check validates.

## Verify

You should have:

- `enrichment-api-rps` and `enrichment-api-conns` global concurrency
  limits registered.
- `enrich_duck` uses both `rate_limit(...)` and `concurrency(...)` and
  has retries with backoff and jitter configured.
- A `quacksync-local` deployment with `concurrency_limit=2`.
- Zero 429 errors in the mock server log during the final run.
