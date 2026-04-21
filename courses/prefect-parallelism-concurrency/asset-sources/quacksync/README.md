# QuackSync

The running project for **Scaling Workflows with Prefect: Parallelism, Concurrency & Rate Limits**.

QuackSync syncs the Quack Overflow rubber duck store's catalog into a local
SQLite database. It fetches duck metadata, enriches each duck with pricing and
stock data from a rate-limited API, runs a CPU-bound scoring step, and writes
the result to a connection-pool-limited database.

You'll evolve this project one primitive at a time across six modules.

## Layout

- `mock_server.py` - FastAPI mock serving both the Duck Catalog and the
  Enrichment API on `localhost:8000`. The Enrichment API enforces 10 RPS and
  3 concurrent connections, and returns real 429 responses when violated.
- `quacksync/tasks.py` - the core tasks: `fetch_duck`, `enrich_duck`,
  `score_duck`, `write_duck`.
- `quacksync/flow.py` - the flow that ties them together. This file is what
  you'll change from module to module.
- `quacksync/database.py` - a `DatabasePool` wrapper around SQLite that
  enforces a maximum of 5 concurrent connections.
- `quacksync/scoring.py` - the CPU-bound cosine-similarity scorer.
- `quacksync/profile.py` - tiny per-stage timing helper.
- `quacksync/seeds/` - JSON lists of duck IDs (`ducks_50.json`,
  `ducks_500.json`).
- `quacksync/snapshots/` - reference starting states for each module, used by
  challenge setup scripts so you can pick up at any module.

## Running it

In one terminal, start the mock server:

```bash
uv run python mock_server.py
```

In another, run the flow:

```bash
uv run python -m quacksync.flow
```
