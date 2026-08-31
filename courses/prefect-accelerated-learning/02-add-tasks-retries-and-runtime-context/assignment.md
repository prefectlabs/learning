---
slug: add-tasks-retries-and-runtime-context
id: hpdscfstvc7d
type: challenge
title: Add Tasks, Retries, and Runtime Context
teaser: Break a flow into tasks, log useful context, and add resilience with retries.
notes:
- type: text
  contents: |-
    # What PAL 102 adds

    Module 102 moves from simple flows into orchestration and observation. The key
    ideas are tasks, structured logging, runtime context, workflow state, retries,
    and configuration primitives like variables and blocks.
- type: text
  contents: |-
    # What matters in practice

    Prefect tasks let you add retries, caching, and better observability around the
    pieces of a workflow that actually do the work. Logging and runtime context make
    runs easier to understand, especially once you stop thinking of a flow as just a
    single script.
tabs:
- id: f8udiy51zln8
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: sb7f7xj5kbya
  title: Code Editor
  type: code
  hostname: prefect-sandbox
  path: /root/pal
- id: xzggqxtcxxtp
  title: Prefect UI
  type: browser
  hostname: local-prefect-server
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
# Add Tasks, Retries, and Runtime Context

This challenge adapts the PAL 102 weather examples into a local lab.

## Step 1: Create a task-based pipeline

Create `/root/pal/weather_tasks.py` with:

- a task named `fetch_weather`
- a task named `save_weather`
- a flow named `pipeline`

`fetch_weather` should call Open-Meteo and return the current forecasted temperature.
`save_weather` should write that value to `weather.csv`.

## Step 2: Add flow retries and logging

Decorate the flow with:

- `retries=3`
- `log_prints=True`

Inside the flow, print the result from `save_weather`.

## Step 3: Log runtime context

Import `runtime` from `prefect` and print at least one useful value from flow run
context, such as the run name:

```python
from prefect import runtime
print(runtime.flow_run.name)
```

## Step 4: Run the flow

Execute the script:

```run
cd /root/pal
uv run weather_tasks.py
```

Confirm that `weather.csv` is created in `/root/pal`.

## Step 5: Connect the concepts

In PAL 102, variables and blocks are used for server-side configuration. Because this
course stays mostly local, treat them as conceptual tools for values you would want to
reuse across runs when you move from local development to shared environments.

## Verify

Before clicking **Check**, make sure:

- `weather_tasks.py` contains two `@task` decorators
- the flow uses `retries=3` and `log_prints=True`
- the script references `runtime.flow_run`
- running the script creates `weather.csv`
