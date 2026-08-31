---
slug: persist-results-and-create-artifacts
id: mpca3plyqueh
type: challenge
title: Persist Results and Create Artifacts
teaser: Use persisted results, caching, and artifacts to make workflows faster and
  easier to understand.
notes:
- type: text
  contents: |-
    # What PAL 103 emphasizes

    Module 103 focuses on data-aware orchestration: persisted results, caching, and
    artifacts that communicate what a workflow produced. The slides also introduce
    transactions, remote storage, and notifications as ways to make stateful workflows
    more reliable and easier to operate.
- type: text
  contents: |-
    # Local-first adaptation

    In this course we keep the core PAL ideas local. You'll persist a task result,
    reuse it via a cache policy, and create both a Prefect markdown artifact and a
    local report file so the outcome is easy to inspect.
tabs:
- id: gvurq96fk0lx
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: sq3b5zvxtyf9
  title: Code Editor
  type: code
  hostname: prefect-sandbox
  path: /root/pal
- id: idngbqmfsr4g
  title: Prefect UI
  type: browser
  hostname: local-prefect-server
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
# Persist Results and Create Artifacts

This challenge combines the PAL 103 themes of results, caching, and artifacts.

## Step 1: Create a cached, persisted task

Create `/root/pal/results_artifacts.py` with a task named `build_weather_table` that:

- uses `@task(persist_result=True, cache_policy=INPUTS, log_prints=True)`
- accepts a temperature value
- returns a small `pandas.DataFrame`

Import `INPUTS` from `prefect.cache_policies`.

## Step 2: Create a report task

Add a second task named `write_report` that:

- takes the DataFrame
- writes a file named `weather_report.md`
- calls `create_markdown_artifact(...)` with a short markdown summary

## Step 3: Build the flow

Add a flow named `weather_report_flow` that:

- calls `build_weather_table(72.0)` twice so cache reuse is possible
- passes the DataFrame into `write_report`
- prints a short message when the report is ready

Run the script once:

```run
cd /root/pal
uv run results_artifacts.py
```

## Step 4: Interpret the PAL concepts

PAL 103 also covers remote storage, user management, and automatic notifications. In
production, those ideas extend this same pattern: persisted data and meaningful run
outputs give automation something stable to act on.

## Verify

Before clicking **Check**, make sure:

- the persisted task uses `persist_result=True`
- the cached task uses `cache_policy=INPUTS`
- the script calls `create_markdown_artifact`
- running it creates `weather_report.md`
