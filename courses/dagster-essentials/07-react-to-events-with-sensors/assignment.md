---
slug: react-to-events-with-sensors
type: challenge
title: React to Events with Sensors
teaser: Build a sensor that watches a directory and launches a run for every request that lands in it.
notes:
- type: text
  contents: |-
    # What a sensor is

    A sensor is a small function Dagster runs on a loop. It looks at the world, decides whether anything worth acting on has changed, and hands back a list of runs to launch. By default it wakes up every 30 seconds, does its check, and goes back to sleep.

    That loop is the whole idea. A file lands in cloud storage. An upstream table finishes loading. A worker slot frees up somewhere. Your pipeline notices and reacts, without anyone opening the UI to click a button.

    In this challenge the sensor watches a directory on disk. The mechanics are identical for S3, an API, or a database table. Only the observation changes.
- type: text
  contents: |-
    # Schedules answer "when." Sensors answer "what happened."

    You already have a schedule that runs the taxi pipeline on the 5th of every month. Schedules are the right tool when the timing is known in advance and the work happens whether or not anything changed.

    Plenty of real work does not fit that shape. A vendor drops a file whenever their export finishes. A stakeholder asks a question on a Tuesday afternoon. Polling on a clock either wastes runs on empty checks or leaves data sitting for hours.

    Sensors close that gap. The trigger stops being the calendar and becomes the event itself, which means the pipeline responds at the speed the business actually moves.
- type: text
  contents: |-
    # Run configuration

    Assets usually get everything they need from their partition key and their upstream dependencies. Sometimes they need a value that only exists at launch time: a customer name, a date range, an email address.

    Dagster handles this with run configuration. You define a class that describes the fields your asset expects, and Dagster fills it in from the run's config when the run starts. Schedules can supply it. Sensors can supply it. You can type it by hand in the UI's Launchpad.

    You will use it here to pass a borough and a date range from a JSON request file straight into the asset that builds the report.
tabs:
- title: Terminal
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
- title: Dagster Dev
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
- title: Code Editor
  type: code
  hostname: dagster-sandbox
  path: /root/project-dagster-university/dagster_university/dagster_essentials
- title: Dagster UI
  type: service
  hostname: dagster-sandbox
  port: 3000
difficulty: intermediate
timelimit: 2400
---
Your stakeholders keep asking the same shape of question. How did the December holidays change rush hour ridership in Manhattan? What did the second week of January look like in Staten Island? Every answer is the same motion: write a query, filter to a borough and a date range, build a chart, paste it into Slack. Twenty minutes you do not get back, several times a week.

A schedule cannot help you here, because nobody knows when the next question is coming. But the question itself arrives as an event. Someone fills out an intake form and a JSON file lands in `data/requests`. That file is the trigger you have been missing.

In this challenge you will build three pieces that turn that file into a finished report: an asset that takes a borough and a date range as run configuration, a job that materializes it, and a sensor that watches the directory and launches a run for every new request it finds.

Configure an asset at run time
===

Every asset you have written so far knew what to compute before the run started. The partition key told `taxi_trips` which month to load. This one is different. It cannot know what borough to analyze until somebody asks, so the values have to arrive with the run.

Dagster models that with a config class. You subclass `dg.Config`, declare the fields you expect, and Dagster populates them from the run's configuration before your asset body executes. Start by scaffolding a new file to hold the request asset.

```run
dg scaffold defs dagster.asset assets/requests.py
```

The scaffold leaves a stub behind. Open `src/dagster_essentials/defs/assets/requests.py` in the [Code Editor](tab-Code-Editor) and replace its contents with the config class below. Four string fields, one for each thing a request carries, plus the name of the file it came from so the report can be named to match.

```python
# src/dagster_essentials/defs/assets/requests.py
import dagster as dg

class AdhocRequestConfig(dg.Config):
    filename: str
    borough: str
    start_date: str
    end_date: str
```

Nothing uses this yet. A config class on its own is just a description of what a future run will need to supply.

Write the adhoc_request asset
===

Now the asset that does the work. It takes `config` typed as `AdhocRequestConfig` and `database` typed as `DuckDBResource`, and it declares `taxi_trips` and `taxi_zones` as dependencies. Those two are `deps` rather than function arguments because the asset reads them straight out of DuckDB. Dagster still needs to know the edges exist so the lineage graph stays honest.

Four things happen inside. The report's output path comes from a template already sitting in `constants.py`, with the `.json` extension stripped off the request's filename. The SQL counts pickups in the requested borough, bucketed by hour of day and day of week. Matplotlib turns that DataFrame into a stacked bar chart and writes it to disk. Then the asset reads the PNG back, encodes it, and attaches it as materialization metadata so the chart shows up in the Dagster UI instead of only on the filesystem.

Replace the contents of `src/dagster_essentials/defs/assets/requests.py` with the full file:

```python
# src/dagster_essentials/defs/assets/requests.py
import base64

import dagster as dg
import matplotlib.pyplot as plt
from dagster_duckdb import DuckDBResource

from dagster_essentials.defs.assets import constants


class AdhocRequestConfig(dg.Config):
    filename: str
    borough: str
    start_date: str
    end_date: str


@dg.asset(
    deps=["taxi_trips", "taxi_zones"],
    kinds={"python"},
)
def adhoc_request(config: AdhocRequestConfig, database: DuckDBResource):
    """
    The response to an request made in the `requests` directory.
    See `requests/README.md` for more information.
    """

    # strip the file extension from the filename, and use it as the output filename
    file_path = constants.REQUEST_DESTINATION_TEMPLATE_FILE_PATH.format(
        config.filename.split(".")[0]
    )

    # count the number of trips that picked up in a given borough, aggregated by time of day and hour of day
    query = f"""
        select
            date_part('hour', pickup_datetime) as hour_of_day,
            date_part('dayofweek', pickup_datetime) as day_of_week_num,
            case date_part('dayofweek', pickup_datetime)
                when 0 then 'Sunday'
                when 1 then 'Monday'
                when 2 then 'Tuesday'
                when 3 then 'Wednesday'
                when 4 then 'Thursday'
                when 5 then 'Friday'
                when 6 then 'Saturday'
            end as day_of_week,
            count(*) as num_trips
        from trips
        left join zones on trips.pickup_zone_id = zones.zone_id
        where pickup_datetime >= '{config.start_date}'
        and pickup_datetime < '{config.end_date}'
        and pickup_zone_id in (
            select zone_id
            from zones
            where borough = '{config.borough}'
        )
        group by 1, 2
        order by 1, 2 asc
    """

    with database.get_connection() as conn:
        results = conn.execute(query).fetch_df()

    fig, ax = plt.subplots(figsize=(10, 6))

    # Pivot data for stacked bar chart
    results_pivot = results.pivot(
        index="hour_of_day", columns="day_of_week", values="num_trips"
    )
    results_pivot.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")

    ax.set_title(
        f"Number of trips by hour of day in {config.borough}, from {config.start_date} to {config.end_date}"
    )
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Number of Trips")
    ax.legend(title="Day of Week")

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(file_path)
    plt.close(fig)

    with open(file_path, "rb") as file:
        image_data = file.read()

    base64_data = base64.b64encode(image_data).decode("utf-8")
    md_content = f"![Image](data:image/jpeg;base64,{base64_data})"

    return dg.MaterializeResult(metadata={"preview": dg.MetadataValue.md(md_content)})
```

Notice that `config.borough` and `config.start_date` read like ordinary attributes. That is the point of the config class. The asset body never has to know whether the values came from a sensor, a schedule, or someone typing into the UI.

Give the asset a job
===

A sensor launches runs of a job, so `adhoc_request` needs one. This job looks like the ones you built for the monthly and weekly pipelines, with one difference: no `partitions_def`, because a request is not tied to a calendar window.

There is also a change to make to an existing job. `trip_update_job` selects `AssetSelection.all()` minus `trips_by_week`, which means it would happily sweep up your new asset and try to run it on a monthly partition it knows nothing about. Subtract it out, the same way you handled `trips_by_week` earlier.

Open `src/dagster_essentials/defs/jobs.py` and make it match this:

```python
# src/dagster_essentials/defs/jobs.py
import dagster as dg

from dagster_essentials.defs.partitions import (
    monthly_partition,
    weekly_partition,
)

trips_by_week = dg.AssetSelection.assets("trips_by_week")
adhoc_request = dg.AssetSelection.assets("adhoc_request")

trip_update_job = dg.define_asset_job(
    name="trip_update_job",
    partitions_def=monthly_partition,
    selection=dg.AssetSelection.all() - trips_by_week - adhoc_request,
)

weekly_update_job = dg.define_asset_job(
    name="weekly_update_job", partitions_def=weekly_partition, selection=trips_by_week
)

adhoc_request_job = dg.define_asset_job(
    name="adhoc_request_job", selection=adhoc_request
)
```

`AssetSelection.all()` is convenient right up until it is not. Every asset you add from here on gets pulled into that job unless you say otherwise, which is worth remembering the next time a scheduled run fails for reasons that have nothing to do with the schedule.

Build the sensor
===

A sensor that only knows how to list a directory would relaunch every report on every tick, forever. It needs memory, and in Dagster that memory is called a **cursor**.

The cursor is a string the sensor writes at the end of each tick and reads at the start of the next one. Yours will hold a small JSON map of filename to last-modified time. Read the cursor, list the directory, compare, request a run for anything new or changed, then write the updated map back. Most sensors you will ever write follow that same four-beat loop, whether the cursor holds file timestamps, the ID of the last record fetched, or an offset into a stream.

Scaffold the sensor file:

```run
dg scaffold defs dagster.sensor sensors.py
```

Now replace the contents of `src/dagster_essentials/defs/sensors.py` with the sensor below. The `@dg.sensor` decorator takes the job to launch. The `context` argument is a `SensorEvaluationContext`, the sensor equivalent of the `AssetExecutionContext` you have seen on assets, and it carries the cursor. The `run_config` block is where the request's JSON gets merged with the filename and handed to the asset under the `adhoc_request` key.

```python
# src/dagster_essentials/defs/sensors.py
import json
import os

import dagster as dg

from dagster_essentials.defs.jobs import adhoc_request_job


@dg.sensor(job=adhoc_request_job)
def adhoc_request_sensor(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    PATH_TO_REQUESTS = os.path.join(
        os.path.dirname(__file__),
        "../../../",
        "data/requests",
    )

    previous_state = json.loads(context.cursor) if context.cursor else {}
    current_state = {}
    runs_to_request = []

    for filename in os.listdir(PATH_TO_REQUESTS):
        file_path = os.path.join(PATH_TO_REQUESTS, filename)
        if filename.endswith(".json") and os.path.isfile(file_path):
            last_modified = os.path.getmtime(file_path)

            current_state[filename] = last_modified

            # if the file is new or has been modified since the last run, add it to the request queue
            if (
                filename not in previous_state
                or previous_state[filename] != last_modified
            ):
                with open(file_path, "r") as f:
                    request_config = json.load(f)

                runs_to_request.append(
                    dg.RunRequest(
                        run_key=f"adhoc_request_{filename}_{last_modified}",
                        run_config={
                            "ops": {
                                "adhoc_request": {
                                    "config": {"filename": filename, **request_config}
                                }
                            }
                        },
                    )
                )

    return dg.SensorResult(
        run_requests=runs_to_request,
        cursor=json.dumps(current_state),
    )
```

Two details are doing quiet work here. `context.cursor` may be empty on the very first tick, so the code falls back to an empty dictionary rather than trying to parse `None`. And the `run_key` combines the filename with its modification time, which gives Dagster a stable identity for the run. Ask for the same `run_key` twice and Dagster skips the second one, so a duplicate tick cannot produce a duplicate report.

Watch your indentation when you paste. A misplaced block here fails as a Python error rather than a Dagster one.

Like schedules, sensors are picked up automatically from your `defs` module. There is no `Definitions` object to edit. Confirm that Dagster can load everything you just wrote:

```run
dg check defs
```

A clean run means the asset, the job, and the sensor all resolve. If it complains about `adhoc_request` not being found, check that the asset name in `jobs.py` matches the function name in `requests.py`.

Load and enable the sensor
===

Sensors ship turned off. That default exists for a good reason: a sensor that starts polling the moment it loads can fire runs you did not expect, against data you have not checked. You turn it on deliberately.

Start Dagster in the [Dagster Dev](tab-Dagster-Dev) tab. Leave it running for the rest of the challenge.

```bash
dg dev --host 0.0.0.0 --port 3000
```

Once the server reports that it is ready, [open the Dagster UI](tab-Dagster-UI) and go to **Assets**, then **Global Asset Lineage**. You should see `adhoc_request` sitting off to the side of the main graph, with dashed edges coming in from `taxi_trips` and `taxi_zones`. If it is missing, click **Reload definitions** in the top right.

Now click **Automation** in the left navigation. Alongside `trip_update_schedule` and `weekly_update_schedule` you will find `adhoc_request_sensor`, with its **Running** toggle switched off and no tick history to speak of.

Click the sensor's name to open its details page. This is where you will spend your time when a sensor misbehaves in production: the job it targets, its evaluation interval, and a tick history showing every time it woke up, what it saw, and what it decided to do. Flip the **Running** toggle on. From here the sensor evaluates every 30 seconds.

Verify
===

Everything is wired. The only thing missing is a question to answer.

Before you drop one, make sure the data is there. The report queries the `trips` and `zones` tables in DuckDB, so `taxi_zones` and the January 2023 partition of `taxi_trips` need to have been materialized in an earlier challenge. If you are not sure, open the **Assets** page and check that both show a recent materialization.

Now create a request. The [Terminal](tab-Terminal) tab is already in the project directory, so write the file straight into `data/requests`:

```run
cat > data/requests/january-staten-island.json <<'EOF'
{
  "start_date": "2023-01-10",
  "end_date": "2023-01-25",
  "borough": "Staten Island"
}
EOF
```

Go back to the sensor's details page in the [Dagster UI](tab-Dagster-UI) and watch the tick history. Within about 30 seconds a new tick appears, and this one is not empty. It reports **1 run requested**. Click through to the run and open the **Configuration** tab: the borough, the dates, and the filename you just wrote are sitting right there in the run config, exactly as the sensor packed them.

Let the run finish. Open the `adhoc_request` asset from the **Assets** page and look at its latest materialization. The `preview` metadata holds the chart itself, a stacked bar of Staten Island pickups by hour of day, colored by day of week, with the evening peak leaning hard toward the end of the week. The same chart is on disk:

```run
ls -l data/outputs/
```

You should see `january-staten-island.png`.

One last thing, because it makes the cursor concrete. Watch the sensor tick a few more times and notice that nothing happens. The file is in the cursor now, so the sensor sees it and moves on. Then touch it:

```run
touch data/requests/january-staten-island.json
```

The modification time changed, the cursor no longer matches, and the sensor requests a fresh run on its next tick. That is the whole mechanism, and it is the same mechanism whether you are watching a folder, an S3 bucket, or a queue.

Your stakeholders now have a self-service report. They fill out a form, and a chart appears. Nobody has to open a laptop on a Tuesday afternoon.
