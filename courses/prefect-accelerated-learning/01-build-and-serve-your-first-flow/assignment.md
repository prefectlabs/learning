---
slug: build-and-serve-your-first-flow
id: ob7n4cvl6vsb
type: challenge
title: Build and Serve Your First Flow
teaser: Turn a Python script into a Prefect flow, then serve it locally with a schedule.
notes:
- type: text
  contents: |-
    # From scripts to orchestration

    PAL module 101 introduces workflow orchestration as the practice of running the
    right steps in the right order at the right time, with recovery when things fail.
    Prefect's role is to keep your Python code readable while adding scheduling,
    observability, and deployment concepts only where you need them.
- type: text
  contents: |-
    # The first PAL milestone

    The original 101 module focused on writing a simple weather workflow, then turning
    it into something you can serve and schedule. In this lab you'll keep that same
    progression, but in a self-paced format that runs entirely in your local sandbox.
tabs:
- id: klp7kdy2zzot
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: cslobnic68g9
  title: Code Editor
  type: code
  hostname: prefect-sandbox
  path: /root/pal
- id: rpa9z3zj2dhz
  title: Prefect UI
  type: browser
  hostname: local-prefect-server
difficulty: basic
timelimit: 900
enhanced_loading: null
---
# Build and Serve Your First Flow

In PAL 101, the first working example is a weather script that becomes a flow and then
becomes a served deployment. We'll follow that same arc here.

## Step 1: Create a local weather flow

Create `/root/pal/weather_service.py` with a function named `fetch_weather` that:

- uses `httpx` to call the Open-Meteo API
- is decorated with `@flow(log_prints=True)`
- accepts `lat` and `lon` parameters with defaults
- prints the forecasted temperature and returns it

Start from this structure:

```python
import httpx
from prefect import flow


@flow(log_prints=True)
def fetch_weather(lat: float = 38.9, lon: float = -77.0):
    ...
```

Run it once:

```run
cd /root/pal
uv run weather_service.py
```

## Step 2: Turn the flow into a served deployment

Update the `__main__` block so the script serves the flow instead of executing it once.
Use the deployment name `pal-weather-service`.

Your main block should call `fetch_weather.serve(...)`.

## Step 3: Add a schedule

Add a cron schedule that runs every 5 minutes:

```python
cron="*/5 * * * *"
```

## Step 4: Verify locally

Use the local UI tab to confirm the server is available, then verify your script contains:

- a Prefect flow
- a served deployment
- a cron schedule

## Verify

Before clicking **Check**, make sure:

- `weather_service.py` exists in `/root/pal`
- it contains `@flow`
- it contains `.serve(`
- it contains the cron string `*/5 * * * *`
