---
slug: automate-with-jobs-and-schedules
id: jukk0ehyb42y
type: challenge
title: Automate with Jobs and Schedules
teaser: Slice your asset graph into jobs, attach cron schedules, and stop clicking
  Materialize.
notes:
- type: text
  contents: |-
    # Jobs are a slice of the graph

    Up to now you have materialized assets by hand, either one at a time or all at once. That works while the graph is seven assets. It stops working the moment the graph is fifty, and half of them only need to run once a month.

    A **job** solves that. It names a subset of your assets and treats them as one unit of work. You build the selection with the `AssetSelection` class:

    - `AssetSelection.all()` returns every asset in the code location
    - `AssetSelection.assets("some_asset")` returns the assets matching the keys you name

    Selections support set math. `AssetSelection.all() - trips_by_week` means "everything except that one." That is the whole trick behind the two jobs you are about to write: one for the monthly bulk refresh, one for the weekly aggregate that runs on its own cadence.

    Jobs earn their keep later, too. Once you are running on real infrastructure, one job can run in an isolated Kubernetes pod while another runs in a single process.
- type: text
  contents: |-
    # Cron, in one page

    Cron showed up as a Unix scheduling utility in the 1970s and outlived nearly everything that came after it. Its syntax is still how most orchestrators, Dagster included, express "when."

    Five fields, separated by spaces:

    ```
    minute  hour  day-of-month  month  day-of-week
    ```

    An asterisk means "every." So `15 5 * * 1-5` reads as *5:15 AM, Monday through Friday, every month*.

    Two expressions matter in this challenge:

    - `0 0 5 * *` runs at midnight on the 5th of each month
    - `0 0 * * 1` runs at midnight every Monday

    The monthly cadence is not arbitrary. The NYC Taxi & Limousine Commission publishes trip data in monthly batches, so a monthly refresh matches the way the data actually arrives.

    When you write your own expressions, [Crontab Guru](https://crontab.guru/) will translate them into plain English and show you the next few fire times. Useful, but not authoritative. Always confirm the behavior inside Dagster.
- type: text
  contents: |-
    # Ticks, runs, and the daemon

    A schedule pairs a job with a cron expression. When the clock matches, the schedule produces a **tick**. A tick that passes its checks submits a **run**, which is one execution of the job's assets.

    Something has to be watching the clock. When you start `dg dev`, it launches the Dagster webserver *and* the `dagster-daemon`, a long-running process that wakes up, compares the current time against every enabled schedule, and submits runs when one is due. Sensors, which you will meet later, use the same daemon.

    Two things to notice while you work: schedules ship **off** by default, and nothing fires until the daemon is running. If a schedule looks correct and still never runs, those are the first two places to look.
tabs:
- id: zoxmpirnlubz
  title: Terminal
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
  cmd: /bin/bash
- id: cf77w8chijsd
  title: Dagster Dev
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
  cmd: /bin/bash
- id: 8g3sv9b1nqbi
  title: Code Editor
  type: code
  hostname: dagster-sandbox
  path: /root/project-dagster-university/dagster_university/dagster_essentials
- id: itfb3pisbhyq
  title: Dagster UI
  type: service
  hostname: dagster-sandbox
  port: 3000
difficulty: basic
timelimit: 1500
enhanced_loading: null
---
Every asset you have materialized so far started with a human clicking a button. That is fine for building a pipeline. It is a bad way to run one. An orchestrator earns its name by kicking off work when nobody is watching, and the simplest way to get there is a schedule.

In this challenge you will split your taxi graph into two jobs, give each one a cron schedule, and turn them on in the Dagster UI. The monthly bulk refresh gets one cadence. The weekly aggregate gets another. By the end you will have a schedule with a real next-tick timestamp and a run you launched without touching an asset.

Define a job that selects part of the graph
===

Dagster's convention is to give definitions their own module, and `dg` will scaffold the file for you. Run this in the [Terminal](tab-Terminal) to create `src/dagster_essentials/defs/jobs.py`.

```run
dg scaffold defs dagster.job jobs.py
```

The scaffolded file arrives with a commented-out example. Open it in the [Code Editor](tab-Code-Editor) and replace the entire contents with the asset selection below. This pulls a single asset, `trips_by_week`, out of the graph so you can address it separately. It is the weekly aggregate, and it should refresh more often than everything upstream of it.

```python
# src/dagster_essentials/defs/jobs.py
import dagster as dg

trips_by_week = dg.AssetSelection.assets("trips_by_week")
```

Now add the first job underneath it. `define_asset_job` takes a name and a selection, and here the selection is everything in the code location *minus* the asset you just isolated. That subtraction is what keeps the slow weekly aggregate out of the monthly refresh.

```python
trip_update_job = dg.define_asset_job(
    name="trip_update_job", selection=dg.AssetSelection.all() - trips_by_week
)
```

Practice: build the weekly_update_job
===

Your turn. Add a second job to `src/dagster_essentials/defs/jobs.py` named `weekly_update_job` that materializes only the `trips_by_week` asset. You already have the selection sitting at the top of the file, so this one is shorter than the last.

Write it before you read on.

Your finished `jobs.py` should match this. If yours differs, change it, because later lessons use these two jobs exactly as written here.

```python
# src/dagster_essentials/defs/jobs.py
import dagster as dg

trips_by_week = dg.AssetSelection.assets("trips_by_week")

trip_update_job = dg.define_asset_job(
    name="trip_update_job", selection=dg.AssetSelection.all() - trips_by_week
)

weekly_update_job = dg.define_asset_job(
    name="weekly_update_job",
    selection=trips_by_week,
)
```

Create a schedule
===

A job says *what* runs. A schedule says *when*. Scaffold the schedules module the same way you scaffolded the jobs module.

```run
dg scaffold defs dagster.schedule schedules.py
```

Replace the contents of `src/dagster_essentials/defs/schedules.py` with the code below. `ScheduleDefinition` needs two things: the job it targets, and a cron expression. This one points at `trip_update_job` and fires at midnight on the 5th of every month, a few days after the TLC typically publishes the previous month's data.

```python
# src/dagster_essentials/defs/schedules.py
import dagster as dg
from dagster_essentials.defs.jobs import trip_update_job

trip_update_schedule = dg.ScheduleDefinition(
    job=trip_update_job,
    cron_schedule="0 0 5 * *", # every 5th of the month at midnight
)
```

Notice the import. The schedule reaches into the jobs module by name, which is why the job had to exist first. Keep that comment on the cron line. Six months from now, `0 0 5 * *` will not read itself.

Practice: build the weekly_update_schedule
===

One more on your own. Add a schedule to `src/dagster_essentials/defs/schedules.py` that:

- Is named `weekly_update_schedule`
- Runs the `weekly_update_job`, which materializes `trips_by_week`
- Fires every Monday at midnight

The cron expression is in the notes if you need it. Try writing it from the field order first.

Here is the finished file. Match it before continuing.

```python
# src/dagster_essentials/defs/schedules.py
import dagster as dg

from dagster_essentials.defs.jobs import (
    trip_update_job,
    weekly_update_job,
)

trip_update_schedule = dg.ScheduleDefinition(
    job=trip_update_job,
    cron_schedule="0 0 5 * *",  # every 5th of the month at midnight
)

weekly_update_schedule = dg.ScheduleDefinition(
    job=weekly_update_job,
    cron_schedule="0 0 * * 1",  # every Monday at midnight
)
```

Let Definitions pick them up
===

Resources needed a mapping to a specific key. Jobs and schedules do not. Anything defined in the `defs` folder gets loaded into the `Definitions` object automatically, so there is no registry to edit and nothing to import in `definitions.py`.

Confirm it. This command loads the project the same way the webserver does and prints every definition it found.

```run
dg list defs
```

You should see `trip_update_job` and `weekly_update_job` under jobs, and `trip_update_schedule` and `weekly_update_schedule` under schedules, alongside the five taxi assets. If a name is missing, you have a typo or an import error, and this command will tell you which.

Start the schedule in the UI
===

Definitions load when the process starts, so the running server has a stale picture of your code. Switch to the [Dagster Dev](tab-Dagster-Dev) tab, stop the server with `Ctrl+C`, and start it again.

```bash
dg dev --host 0.0.0.0 --port 3000
```

That single command brings up two processes: the webserver you are about to use, and the `dagster-daemon` that watches the clock. Watch the startup logs for both.

Open the [Dagster UI](tab-Dagster-UI) and click **Jobs** in the left sidebar. Both jobs appear in the table, each with a **Schedules/sensors** column showing the schedule attached to it and whether that schedule is enabled. Click `trip_update_job` and you will see its asset graph: four assets, with `trips_by_week` conspicuously absent. That is your subtraction, rendered.

Now click **Automation** in the left sidebar. Both schedules are listed with their type, their target job, last tick, and last run. Every toggle is off, and the tick and run columns are empty, because a schedule you have not enabled does nothing.

Flip the toggle next to `weekly_update_schedule`. The row goes green and a **Next tick** timestamp appears: the next Monday at 00:00. The daemon is now responsible for that job.

Click the schedule name to open its details page. Historical ticks and runs live here, so right now it is empty. In the upper right, click **Preview tick result** and pick a mock evaluation time. Click **Evaluate** and Dagster shows you exactly what the schedule would submit at that moment, without materializing anything. This is how you sanity-check a schedule that only fires once a month instead of waiting a month to find out you had it wrong.

Your Monday tick is real, but it is days away, and you should not have to wait to see the job work. From the schedule details page, open `weekly_update_job` and launch it manually with **Materialize all**. The run page opens and streams logs as `trips_by_week` executes.

If that run fails complaining about a missing `trips` table, materialize `trip_update_job` first to rebuild the upstream data, then launch `weekly_update_job` again.

Verify
===

You are done when all of the following are true:

- `dg list defs` lists two jobs, `trip_update_job` and `weekly_update_job`, and two schedules, `trip_update_schedule` and `weekly_update_schedule`
- The **Jobs** tab shows `trip_update_job` with four assets in its graph and `weekly_update_job` with only `trips_by_week`
- The **Automation** tab shows `weekly_update_schedule` toggled on, with a **Next tick** timestamp on the upcoming Monday at 00:00
- A completed run of `weekly_update_job` appears in the schedule's job history

Leave `weekly_update_schedule` enabled and leave the cron expressions as written. The next challenge builds on this exact state.

You have not just automated a pipeline. You have separated the two questions every production workflow has to answer: which assets belong together, and how often they should run. Jobs answer the first. Schedules answer the second. Keeping them apart is what lets you change one without breaking the other.
