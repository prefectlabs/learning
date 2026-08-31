---
slug: define-your-first-asset
id: dmxcjsido5ga
type: challenge
title: Define Your First Asset
teaser: Scaffold, write, and materialize a Dagster asset that pulls real NYC taxi
  data to disk.
notes:
- type: text
  contents: |-
    # Why an orchestrator at all?

    Data engineering is the work of collecting, storing, and shaping data so other people can act on it. The data is usually scattered across systems, often inconsistent, and frequently too large to move around casually. Doing that by hand works right up until it doesn't.

    An orchestrator is the tool that takes over when the manual version stops scaling. It runs work on a schedule or in response to an event, keeps steps in the right order, retries what fails, and records what happened. That last part matters more than people expect. When a pipeline breaks at 3 a.m., the question is never "did something break." It's "what broke, when, and what does it affect downstream."

    The earliest orchestrators solved one narrow problem: run these scripts, in this order, at this time. Modern ones are judged on something harder. Can you see the whole system at a glance and understand it?
- type: text
  contents: |-
    # Two ways to model a workflow

    Picture a pipeline that bakes cookies.

    A **task-centric** workflow describes the steps: gather ingredients, combine them, add chocolate chips, bake. It's a sequence of verbs. It works, and it's how most orchestration has been done for years. But look at what it hides. Cookie dough gets made somewhere in the middle of that sequence, and nothing in the graph says so. The dough is a by-product of a step, not a thing the system knows about.

    An **asset-centric** workflow describes the outputs instead: wet ingredients and dry ingredients combine into cookie dough, cookie dough plus chocolate chips becomes chocolate chip cookie dough, and that gets baked into cookies. Nouns, not verbs. Each thing the pipeline produces is a named object with its own definition.

    Now add peanut butter cookies. In the task-centric version you find the middle of the sequence, fork it, and re-run the whole thing. In the asset-centric version you add one new asset, peanuts, point it at the cookie dough you already have, and you're done.
- type: text
  contents: |-
    # Why asset-centric fits data engineering

    That cookie example maps directly onto real pipelines, and the payoff shows up in four places.

    **Lineage.** When the graph is made of the things you produce, anyone can trace a dashboard back to the table it reads, back to the file it was built from. You don't have to have written the pipeline to read it.

    **Reuse.** An asset can feed several downstream assets. You declare the dependency instead of duplicating the steps that created it.

    **Freshness.** Because Dagster tracks each asset separately, it knows when an upstream input is stale and can refresh it before anything downstream runs. In a task-centric world you usually find out by failing.

    **Troubleshooting.** When one asset is wrong, you fix that asset and re-run that asset. Not the entire pipeline.

    In Dagster, this building block is called an **asset** (you'll also see the longer name, software-defined asset). It's a Python function with a decorator on it, and it's the thing this whole course is built around.
- type: text
  contents: |-
    # What's an asset, exactly?

    An asset is an object in persistent storage that captures some understanding of the world. If you run a data pipeline today, you're already producing them: a table or view in a warehouse like BigQuery, a file on your machine or in blob storage like S3, a trained TensorFlow or PyTorch model, a dbt model or Fivetran connector. Dagster calls these **software-defined assets** because the definition lives in code, and the code carries the whole recipe.

    Every asset definition has four parts:

    - The `@dg.asset` **decorator**, which tells Dagster this function produces an asset
    - An **asset key** that uniquely identifies it. By default that's the function name, and keys can take prefixes the way files sit inside folders
    - Its **upstream dependencies**, referenced by their asset keys. The next challenge is built entirely around these
    - A **Python function** that computes the asset's contents

    Here's the cookie pipeline from the previous note, written down as code:

    ```python
    @dg.asset
    def cookie_dough(dry_ingredients, wet_ingredients):
        return dry_ingredients + wet_ingredients
    ```

    Notice the name. Assets get **noun** names, a descriptor of what's produced. `cookie_dough` names the thing that exists afterward. A name like `combine_ingredients` would describe the work instead of the result, which is the task-centric habit this whole approach replaces.
- type: text
  contents: |-
    # What you're building

    Over this course you'll build a working pipeline on public data from [NYC OpenData](https://opendata.cityofnewyork.us/), specifically the [TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) covering every yellow cab ride in the city.

    The finished pipeline extracts parquet and CSV files from the open data portal, loads them into a DuckDB database, transforms them into tables you can actually query, and renders a map of Manhattan from the result. Real data, real file sizes, real network calls.

    This challenge is the first link in that chain. You'll scaffold an asset file, write an asset that downloads a month of trip records, watch it materialize in the Dagster UI, break it on purpose to see what failure looks like, and then write a second asset on your own.
tabs:
- id: oaq9jixca7ay
  title: Terminal
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
- id: r8wrvnljkn3v
  title: Dagster Dev
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
- id: ilvjz4wudvsf
  title: Code Editor
  type: code
  hostname: dagster-sandbox
  path: /root/project-dagster-university/dagster_university/dagster_essentials
- id: dhyubiebpg4l
  title: Dagster UI
  type: service
  hostname: dagster-sandbox
  port: 3000
difficulty: basic
timelimit: 1800
enhanced_loading: null
---
Define Your First Asset
===

An asset is an object in persistent storage that captures some understanding of the world. A table in a warehouse. A file in S3. A trained model. If you already run data pipelines, you're producing assets right now, you just may not be naming them.

In this challenge you'll write one. It's called `taxi_trips_file`, and its job is to fetch a month of NYC yellow cab trip records from the city's open data portal and land the parquet file on disk. You'll scaffold it with the `dg` CLI, materialize it from the Dagster UI, read the run details, break it on purpose to see how Dagster reports failure, and then build a second asset yourself.

Everything runs in the sandbox. The repository is already cloned, `uv sync` has already run, and every terminal opens inside the project with the virtual environment active, so `dg` and `python` work bare.

Tour the project
===

Start in the [Terminal](tab-Terminal) tab. You're already in `/root/project-dagster-university/dagster_university/dagster_essentials`, which is the root of the Dagster project for this course. Take a look at what's here.

```run
ls -1
```

A few of these matter now and the rest can wait. `pyproject.toml` carries a `tool.dagster` section that tells the CLI where your definitions live, which is why you can run `dg` commands without passing any arguments. `data/` is where the assets you build will write their output. `src/` holds the code.

Your code lives under `src/dagster_essentials/defs/`. Dagster loads everything it finds in that folder automatically, which is why placing files correctly matters.

```run
find src/dagster_essentials/defs -type f | sort
```

Right now there's only `constants.py`, which holds the file paths this project writes to. Open it and read the two paths at the top. You'll use one of them in a minute.

```run
cat src/dagster_essentials/defs/assets/constants.py
```

Notice `TAXI_TRIPS_TEMPLATE_FILE_PATH`. It has a `{}` in it, waiting for a month, so one template can produce `taxi_trips_2023-03.parquet`, `taxi_trips_2023-04.parquet`, and so on. Keeping paths in one file instead of scattering string literals through your assets pays off the first time a path changes.

Scaffold the asset file
===

You could create the file by hand, but `dg` knows where Dagster expects things to live and will put them there for you. Scaffold a new asset file called `trips.py` inside the `assets` folder.

```run
dg scaffold defs dagster.asset assets/trips.py
```

That adds `src/dagster_essentials/defs/assets/trips.py` to the project with a placeholder asset inside it. Your definitions folder now looks like this:

```
.
└── src
    └── dagster_essentials
        └── defs
            └── assets
                ├── __init__.py
                ├── constants.py
                └── trips.py
```

Before writing any code, confirm that Dagster can still load the project. `dg check defs` parses everything in the defs folder and reports problems without starting a server, which makes it the fastest feedback loop you have.

```run
dg check defs
```

You should see both lines come back clean:

```
All component YAML validated successfully.
All definitions loaded successfully.
```

If you had a syntax error or a bad import, this is where you'd find out. Get in the habit of running it after every edit.

A word on what `dg` is actually doing. Scaffolding comes from **Dagster Components**, the project-structure system introduced in Dagster 1.11 that `dg` uses to organize and generate code. Components go much deeper than file placement, all the way to reusable templates for entire workflow patterns, but they make the most sense once the fundamentals underneath them are solid. This course uses `dg` for scaffolding and validation and leaves the rest of Components for later; the [ETL pipeline tutorial](https://docs.dagster.io/etl-pipeline-tutorial/) picks up that thread.

Write the taxi_trips_file asset
===

Every asset you will ever write has the same four parts: the `@dg.asset` decorator that registers it, an asset key that identifies it (the function name, by default), any upstream dependencies it draws on, and a Python function that computes it. `taxi_trips_file` uses three of the four. Its dependencies arrive in the next challenge, so watch for the other three parts as the file comes together.

Open the [Code Editor](tab-Code-Editor) tab and navigate to `src/dagster_essentials/defs/assets/trips.py`. Delete the scaffolded placeholder code. You're replacing the whole file.

Start with the imports. `requests` fetches the file over HTTP, and `constants` gives you the path to write it to.

```python
import requests
from dagster_essentials.defs.assets import constants
```

Now the function itself. It takes no arguments and returns nothing, which the `-> None` annotation spells out. It downloads the March 2023 yellow taxi parquet file and writes the bytes to disk. Note the docstring: Dagster reads it and displays it in the UI, so it's documentation your team actually sees.

```python
def taxi_trips_file() -> None:
    """
      The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
    """
    month_to_fetch = '2023-03'
    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
        output_file.write(raw_trips.content)
```

That's still just a Python function. Dagster doesn't know it exists. Two things turn it into an asset: importing the Dagster library and adding the `@dg.asset` decorator above the function. The decorator is what registers the function with Dagster, and the function name becomes the **asset key**, the unique identifier Dagster uses everywhere else.

Here's the complete file. Make sure yours matches.

```python
# src/dagster_essentials/defs/assets/trips.py
import requests
from dagster_essentials.defs.assets import constants
import dagster as dg

@dg.asset
def taxi_trips_file() -> None:
    """
      The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
    """
    month_to_fetch = '2023-03'
    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
        output_file.write(raw_trips.content)
```

Save the file, then check it from the [Terminal](tab-Terminal) tab.

```run
dg check defs
```

Clean output means Dagster found your asset and loaded it. One decorator on an ordinary function, and it's part of the graph.

A note on naming while it's fresh: assets get **noun** names that describe what's produced, not verb names that describe the work. `taxi_trips_file`, not `download_taxi_trips`. The name is what everyone downstream will read.

Start the Dagster UI
===

`dg dev` starts a local web server and keeps running, so it needs its own terminal. Click into the [Dagster Dev](tab-Dagster-Dev) tab and run this there. Bind to `0.0.0.0` so the sandbox can route the UI tab to it.

```bash
dg dev --host 0.0.0.0 --port 3000
```

Leave it running for the rest of the challenge. You'll see startup logs, then a line telling you the webserver is serving on port 3000. Any time you edit your asset code, this process picks up the change.

Now open the [Dagster UI](tab-Dagster-UI) tab. You'll land on an overview page that's mostly empty, which is expected with one asset in the project.

Materialize the asset
===

Defining an asset tells Dagster what should exist. **Materializing** it makes it exist: Dagster executes the function and the results get persisted to storage. Each materialization kicks off a **run**, which is a single instance of execution.

In the [Dagster UI](tab-Dagster-UI), click **Catalog** in the left sidebar. You should see `taxi_trips_file` listed with a status of **Never materialized**. If the list is empty, click **Reload definitions** and it will appear.

Click **View lineage** to open the global asset graph. It's a single box right now. That box is your DAG, and it will get considerably more interesting over the next few challenges.

Click the **Materialize** button. A purple toast appears at the bottom of the screen confirming the run started, and the asset box updates as the run progresses. The download is a few dozen megabytes over the public internet, so give it a moment. When it finishes, the box shows **Materialized** with a timestamp.

Back in the [Terminal](tab-Terminal) tab, confirm the file actually landed where `constants.py` said it would.

```run
ls -lh data/raw/
```

You should see `taxi_trips_2023-03.parquet` with a real file size next to it. That file is the asset. Everything else, the decorator, the graph, the run history, is Dagster's record of how it got there.

There's a command-line path too, if you'd rather not have the UI running: `dg launch --assets taxi_trips_file` executes the asset directly and streams every run event to your terminal. Both do the same work. This course leans on `dg dev` because the UI shows more of what Dagster is tracking.

Read the run details
===

A green box tells you a run succeeded. The interesting question is what you get when it doesn't, and the answer lives on the same page either way, so it's worth knowing your way around while things are still working.

In the asset graph, find the **Materialized** label on the `taxi_trips_file` box and click the **date** next to it. That opens the **Run details** page.

Three sections carry the information you'll rely on. At the top are the **run stats**: the run ID, its status, which asset it touched, when it ran, and how long it took. Below that is the **run timeline**, a bar chart of each step in the run with its duration, colored green for success. With one asset there's exactly one bar. Underneath is the **run log**, an event-by-event record of what Dagster did, from resource initialization through `STEP_SUCCESS`.

Scroll the logs and find the `ASSET_MATERIALIZATION` event. That's the moment Dagster recorded that the asset now exists. Every state you see in the UI traces back to events like this one.

Break it on purpose
===

Reading a failure is a skill, and the cheapest time to learn it is when you already know the answer. You're going to break the asset deliberately.

In the [Code Editor](tab-Code-Editor), open `trips.py` and comment out the `constants` import so the file looks like this:

```python
# src/dagster_essentials/defs/assets/trips.py
import requests
# from dagster_essentials.defs.assets import constants # <---- Import commented out here
import dagster as dg

@dg.asset
def taxi_trips_file() -> None:
    """
      The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
    """
    month_to_fetch = '2023-03'
    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
        output_file.write(raw_trips.content)
```

Save it, return to the global asset lineage page in the [Dagster UI](tab-Dagster-UI), and click **Materialize** again. The run fails, and the asset box turns red.

Click the date on the failed asset to open **Run details**. Everything you learned on the successful run still applies, it just reads differently: the status now says **Failure**, the timeline bar is red, the failed step is called out in an **Errored** section, and the logs carry the error.

In the log list, find the `STEP_FAILURE` event. In its **INFO** column, click **View full message** to open the full stacktrace. It names the problem directly: `constants` is not defined, because you removed the import.

Fix it. Uncomment the `from dagster_essentials.defs.assets import constants` line and save the file. Then, rather than starting from scratch, use the **Re-execute all** button near the top right of the Run details page. Dagster re-runs the steps against the corrected code and links the new run to the failed one, so the history shows both what went wrong and what fixed it.

The run should complete successfully this time. Make sure your import is restored before moving on, because the next section builds on this file.

Practice: build the taxi_zones_file asset
===

Time to write one without the answer in front of you. Trip records tell you where a ride started and ended, but only as numeric location IDs. The taxi zones dataset maps those IDs to the actual neighborhoods, and you'll need it in the next challenge.

In the same `trips.py` file, add a second asset that:

- Is named `taxi_zones_file`
- Uses `requests` to fetch `https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv`
- Writes the response to the path already defined for you in `constants.TAXI_ZONES_FILE_PATH`, which resolves to `data/raw/taxi_zones.csv`

Structurally it's the same shape as the asset you just wrote, with one simplification: there's no month in the URL, so you don't need a variable to format into it.

When you're done, validate it and materialize it. Run the check first.

```run
dg check defs
```

Then go to the [Dagster UI](tab-Dagster-UI), reload definitions if the new asset doesn't appear, and materialize `taxi_zones_file` from the asset graph.

Practice: check your work
===

Try it yourself before reading this section. Comparing your version to a working one teaches more than copying it.

Your asset should look close to this:

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset
def taxi_zones_file() -> None:
    """
      The raw CSV file for the taxi zones dataset. Sourced from the NYC Open Data portal.
    """
    raw_taxi_zones = requests.get(
        "https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv"
    )

    with open(constants.TAXI_ZONES_FILE_PATH, "wb") as output_file:
        output_file.write(raw_taxi_zones.content)
```

If yours differs, match it. Later challenges depend on this asset behaving exactly this way.

What You've Accomplished
===

Confirm the end state before you move on. Both files should be on disk with real sizes.

```run
ls -lh data/raw/
```

You're done when:

- `data/raw/taxi_trips_2023-03.parquet` exists and is a few dozen megabytes
- `data/raw/taxi_zones.csv` exists
- `dg check defs` reports all definitions loaded successfully
- The Catalog page in the [Dagster UI](tab-Dagster-UI) lists `taxi_trips_file` and `taxi_zones_file`, both showing a materialization timestamp instead of **Never materialized**

Step back and look at what that took. Two ordinary Python functions, one decorator each, and Dagster now knows what your pipeline produces, when each thing was last built, how long it took, and exactly what the logs said when one of them failed. You didn't write a scheduler, a retry loop, or a logging framework to get any of it.

Right now these two assets sit side by side with nothing between them. In the next challenge you'll connect them, and the graph starts earning its keep.
