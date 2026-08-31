---
slug: enrich-assets-with-metadata
id: qls2gkzwdnr3
type: challenge
title: Enrich Assets with Metadata
teaser: Add descriptions, asset groups, row counts, and a rendered chart, so the pipeline
  explains itself.
notes:
- type: text
  contents: |-
    # The table nobody can explain

    Every data platform eventually produces the same artifact: a table that six people depend on and nobody can describe. The name made sense to whoever created it. Something refreshes it on some cadence. The person who wrote it left in March.

    That gap is what a data catalog is supposed to close, and it's why catalogs usually show up as a separate product you buy, populate by hand, and then watch drift out of date the week after you finish populating it. The documentation lives in one system, the pipeline lives in another, and the two agree only by accident.

    Dagster puts the catalog and the pipeline in the same place. Descriptions, groupings, row counts, and rendered charts attach to the asset definition itself, in the file that produces the data. Change the code and the documentation moves with it, because it's in the same commit.
- type: text
  contents: |-
    # Two kinds of metadata

    Go back to the cookies from the first challenge.

    Some facts about a batch of cookies are true before the oven is on: the recipe, the serving suggestion, the fact that this belongs on the dessert side of the kitchen and not the dinner side. That's **definition metadata**. It's fixed, it travels with the definition, and it reads the same today as it did last month.

    Other facts only exist once you pull the tray out: how many cookies you got, when they were baked, who baked them. That's **materialization metadata**. It's produced at runtime, and it changes with every batch.

    Dagster carries both, and the split is worth holding onto. Definition metadata answers "what is this, and where does it belong." Materialization metadata answers "what happened last time, and how does that compare to the run before." Trusting a pipeline you didn't write takes both.
- type: text
  contents: |-
    # The last challenge

    This is the end of the course. You already have a pipeline that works: assets with declared dependencies, a shared DuckDB resource, monthly and weekly partitions, jobs, a schedule, and a sensor watching a directory.

    What's left is making it legible to someone who isn't you. You'll sort the assets into groups so the graph reads at a glance, record how many rows each materialization actually loaded, and render a chart straight into the UI so the answer to an ad hoc request appears next to the run that produced it.

    The code changes are small. Watch what they do to the asset graph.
tabs:
- id: sc4fgzeaybm2
  title: Terminal
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
- id: uzk5uguxvbxl
  title: Dagster Dev
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
- id: xgkrj01k4cc9
  title: Code Editor
  type: code
  hostname: dagster-sandbox
  path: /root/project-dagster-university/dagster_university/dagster_essentials
- id: opbazdxdrshv
  title: Dagster UI
  type: service
  hostname: dagster-sandbox
  port: 3000
difficulty: basic
timelimit: 1500
enhanced_loading: null
---
Enrich Assets with Metadata
===

Your pipeline runs. Seven challenges in, it fetches files, loads them into DuckDB, aggregates them by week, draws a map of Manhattan, and answers requests that land in a folder. Nobody has to babysit it.

This challenge asks a different question. Hand the project to a colleague on Monday morning and give them no context. Can they tell which assets are raw extracts and which are derived? Can they tell whether last night's run loaded three million rows or three? Right now the honest answer is no, and the fix is metadata: the descriptions, groupings, and runtime facts that turn a working graph into one a stranger can read.

You'll work in the same two files you've been editing all course, `src/dagster_essentials/defs/assets/trips.py` and `src/dagster_essentials/defs/assets/requests.py`. Every terminal opens in the project with the virtual environment active, so `dg` and `python` work bare.

Start the UI and see what's missing
===

You need `dg dev` running to watch any of this land. It's a long-running process, so give it its own terminal. Click into the [Dagster Dev](tab-Dagster-Dev) tab and start it there. If it's still running from the last challenge, leave it alone.

```bash
dg dev --host 0.0.0.0 --port 3000
```

Now open the [Dagster UI](tab-Dagster-UI) tab, click **Catalog** in the left sidebar, and click **View lineage** to open the asset graph.

Look at the shape of it. Every asset in the project sits inside one grey box labeled `default`, from the raw CSV download all the way through to the ad hoc request chart. The dependencies are drawn correctly, but nothing in the picture tells you which of these are extracts, which are loaded tables, and which are reports. That's the first thing you'll fix.

Click any asset box and look at the panel on the right. There's no record count, no preview, nothing about what the last run actually produced. That's the second thing.

The descriptions you already wrote
===

One piece of documentation is already in place. Every asset you've written in this course opens with a triple-quoted string right under the `def` line, and Dagster reads those. A [Python docstring](https://peps.python.org/pep-0257/) is documentation embedded in the code itself, which is why it beats a comment: `help()` can find it, your editor can find it, and Dagster surfaces it in the UI.

Here's `taxi_zones_file` as you wrote it back in the first challenge. The docstring is doing double duty.

```python
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg

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

Find `taxi_zones_file` in the asset graph in the [Dagster UI](tab-Dagster-UI). That sentence about the NYC Open Data portal is printed under the asset key. You wrote it as a docstring and got catalog documentation for free.

There's a second way to set a description, and it's worth seeing once so you recognize it in someone else's code. The `description` parameter on the decorator overrides the docstring entirely.

```python
@dg.asset(
    description="The raw CSV file for the taxi zones dataset. Sourced from the NYC Open Data portal."
)
def taxi_zones_file() -> None:
    """
      This will not show in the Dagster UI
    """
```

Try it. In the [Code Editor](tab-Code-Editor), open `trips.py`, change the docstring on `taxi_zones_file` to something obviously wrong like `This will not show in the Dagster UI`, add the `description` parameter above it, and save. Reload definitions in the UI and confirm the parameter wins.

Then undo both edits and put the real docstring back. For the rest of this challenge the docstrings stay in charge, because documentation that lives next to the code it describes is documentation that gets updated.

Sort the assets into groups
===

An **asset group** is a label that tells Dagster which assets belong together. It tidies the graph, and it does something more useful than that: jobs can select an entire group by name instead of listing assets one by one, so adding an asset to a group can be enough to get it scheduled.

Two rules to keep in mind. An asset belongs to exactly one group at a time, and an asset with no group lands in `default`, which is the box you're looking at right now.

You set a group with the `group_name` parameter. Start with `taxi_zones_file`, which is a raw file pulled off the internet and nothing more.

```python
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg

@dg.asset(
    group_name="raw_files",
)
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

Save it, then confirm the project still loads from the [Terminal](tab-Terminal) tab before you go near the UI. `dg check defs` parses your definitions without starting a server, which makes it the fastest way to catch a typo in a decorator.

```run
dg check defs
```

Back in the [Dagster UI](tab-Dagster-UI), click **Reload definitions**. A second grey box appears, labeled `raw_files`, with `taxi_zones_file` alone inside it. One parameter, and the graph started sorting itself.

Practice: group the rest
===

You've seen the pattern. Do the other five yourself, in `trips.py` and `requests.py`.

- Add `taxi_trips_file` to the `raw_files` group
- Add `taxi_zones` and `taxi_trips` to an `ingested` group
- Add `adhoc_request` to a `requests` group

Think about why those lines fall where they do. `raw_files` is anything pulled from an outside source and written to disk untouched. `ingested` is anything that made it into DuckDB. `requests` is work triggered by a person asking a question.

The three metrics assets, `trips_by_week`, `manhattan_stats`, and `manhattan_map`, are deliberately left out. Group them into `metrics` if you want the whole graph tidy, or leave them in `default` and watch how the ungrouped box behaves next to the named ones. Either is a defensible choice.

When you're done, check the project loads.

```run
dg check defs
```

Practice: check your work
===

Try it before you read this. Comparing your version to a working one teaches more than copying it does.

Every one of those edits has the same shape, no matter which file it's in:

```python
@dg.asset(
    group_name="GROUP_NAME"
)
def name_of_asset():
```

If an asset already had parameters on its decorator, like `partitions_def` or `deps`, `group_name` sits alongside them rather than replacing them.

Reload definitions in the [Dagster UI](tab-Dagster-UI) and look at the graph again. `raw_files` holds the two downloads, `ingested` holds the two DuckDB tables, `requests` holds the ad hoc asset, and whatever you left ungrouped sits in `default`. The arrows between the boxes now read as a story: files come in, tables get built, questions get answered.

Record how many rows landed
===

Grouping is definition metadata. It's true before anything runs. Now for the other kind.

Right now a successful run of `taxi_trips_file` tells you one thing: it didn't fail. It doesn't tell you whether March pulled three million trips or three hundred, which is exactly the distinction that separates a healthy pipeline from a quietly broken one. Two changes fix that. The asset returns a `MaterializeResult` carrying a `metadata` dictionary, and each value gets wrapped in a `MetadataValue` so Dagster knows how to render it.

Open `trips.py` in the [Code Editor](tab-Code-Editor). Counting rows in a parquet file needs pandas, which isn't imported in this file yet, so add it at the top.

```python
import pandas as pd
```

In `taxi_trips_file`, after the line that writes the downloaded bytes to disk, read the file back and count the rows.

```python
num_rows = len(pd.read_parquet(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)))
```

Then return that count as metadata. The dictionary key is the label you'll see in the UI, and `MetadataValue.int` types the value as an integer so Dagster renders and plots it as a number rather than a string.

```python
return dg.MaterializeResult(
    metadata={
        'Number of records': dg.MetadataValue.int(num_rows)
    }
)
```

The asset used to return nothing. Now it returns something, so update the annotation to match.

```python
def taxi_trips_file(context) -> dg.MaterializeResult:
```

Here's the whole asset. Make sure yours matches.

```python
# src/dagster_essentials/defs/assets/trips.py
import pandas as pd
import dagster as dg

@dg.asset(
    partitions_def=monthly_partition,
    group_name="raw_files",
)
def taxi_trips_file(context) -> dg.MaterializeResult:
    """
      The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
    """

    partition_date_str = context.partition_key
    month_to_fetch = partition_date_str[:-3]

    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
        output_file.write(raw_trips.content)

    num_rows = len(pd.read_parquet(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)))

    return dg.MaterializeResult(
        metadata={
            'Number of records': dg.MetadataValue.int(num_rows)
        }
    )
```

Worth noticing what didn't change. The asset still writes the same file to the same path, and everything downstream of it still works the same way. `MaterializeResult` isn't the asset's output, it's the asset's report on what just happened.

```run
dg check defs
```

Watch the numbers show up
===

Metadata attaches at materialization time, which means the runs you've already done don't have it. You need new ones.

In the [Dagster UI](tab-Dagster-UI), click **Reload definitions**, then select the `taxi_trips_file` asset in the graph and materialize its partitions. `taxi_trips_file` is partitioned by month across January through March 2023, so you'll get a backfill dialog. Select all three partitions and launch it.

Each partition re-downloads a parquet file of real size, so this takes a couple of minutes. It's the last slow thing in the course. If you're watching the clock, two partitions is enough to make the next part readable.

When the runs finish, click the `taxi_trips_file` asset. In the panel on the right you'll find `Number of records` under the latest materialization, and because the value is typed as an integer across a partitioned asset, Dagster plots it: months along the X axis, row counts up the Y. Open the asset's own page and switch to the **Plots** tab for the full-size version.

That chart is the payoff. One glance tells you whether February looks like February, and a partition that suddenly loads a tenth of its usual volume stops being something you discover three weeks later in a dashboard.

Practice: add metadata to taxi_zones_file
===

Do the same for `taxi_zones_file`. It's a CSV rather than parquet, and it isn't partitioned, so the shape is slightly different. Work it out before you scroll.

Your version should look close to this:

```python
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg

@dg.asset(
    group_name="raw_files",
)
def taxi_zones_file() -> dg.MaterializeResult:
    """
      The raw CSV file for the taxi zones dataset. Sourced from the NYC Open Data portal.
    """
    raw_taxi_zones = requests.get(
        "https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv"
    )

    with open(constants.TAXI_ZONES_FILE_PATH, "wb") as output_file:
        output_file.write(raw_taxi_zones.content)
    num_rows = len(pd.read_csv(constants.TAXI_ZONES_FILE_PATH))

    return dg.MaterializeResult(
        metadata={
            'Number of records': dg.MetadataValue.int(num_rows)
        }
    )
```

Check it, then materialize `taxi_zones_file` from the graph. With only one materialization there's no plot to draw, but the count shows up on the asset. There are 265 taxi zones in New York City, so that's the number you're looking for.

```run
dg check defs
```

Render the chart in the UI
===

The `adhoc_request` asset already produces something a person would want to look at: a stacked bar chart of trips by hour of day, saved to `data/outputs/` as an image. Useful later, awkward now. To see the answer to the question you just asked, you have to leave Dagster, find the file, and open it.

Metadata can carry Markdown, and Markdown can carry an image encoded directly into the string. That means the chart can live on the run that produced it.

Open `requests.py` in the [Code Editor](tab-Code-Editor) and add the `base64` import at the top of the file.

```python
import base64
import dagster as dg
```

The asset already saves the chart and closes the figure. After that last line, read the image back off disk as bytes.

```python
with open(file_path, 'rb') as file:
    image_data = file.read()
```

Now turn those bytes into something a Markdown renderer understands. `b64encode` converts the binary image to base64, `decode` turns that into a UTF-8 string, and the f-string wraps it in Markdown image syntax with the data inlined instead of pointing at a URL.

```python
base64_data = base64.b64encode(image_data).decode('utf-8')
md_content = f"![Image](data:image/jpeg;base64,{base64_data})"
```

Then return it as metadata. The key `preview` is the label you'll see in the UI, and `MetadataValue.md` is what tells Dagster to render the string as Markdown instead of printing it as a wall of characters.

```python
return dg.MaterializeResult(
    metadata={
        "preview": dg.MetadataValue.md(md_content)
    }
)
```

Same as before, the asset now returns something, so update the signature. Leave the `deps` and `group_name` parameters where they are.

```python
def adhoc_request(config: AdhocRequestConfig, database: DuckDBResource) -> dg.MaterializeResult:
```

The tail of your asset should now read like this, picking up right where the chart gets saved:

```python
    plt.savefig(file_path)
    plt.close(fig)

    with open(file_path, "rb") as file:
        image_data = file.read()

    base64_data = base64.b64encode(image_data).decode('utf-8')
    md_content = f"![Image](data:image/jpeg;base64,{base64_data})"

    return dg.MaterializeResult(
        metadata={
            "preview": dg.MetadataValue.md(md_content)
        }
    )
```

```run
dg check defs
```

Trigger a request and open the preview
===

The `adhoc_request` asset runs when the sensor you built finds a new or modified JSON file in `data/requests/`. Write one from the [Terminal](tab-Terminal) tab. If this file already exists from the sensors challenge, this rewrites it and updates its modification time, which is what the sensor's cursor watches.

```run
cat > data/requests/january-staten-island.json <<'EOF'
{
  "start_date": "2023-01-10",
  "end_date": "2023-01-25",
  "borough": "Staten Island"
}
EOF
```

In the [Dagster UI](tab-Dagster-UI), click **Reload definitions** so your metadata change is picked up. Then open **Automation** in the left sidebar and click `adhoc_request_sensor`.

You don't have to turn the sensor on and wait for it. Click **Preview tick result** near the top right, click **Continue**, then **Apply requests & commit tick result**. That fires exactly one tick, which is the fastest way to test a sensor without changing its schedule.

When the run finishes, go back to the asset graph and select `adhoc_request`. In the panel on the right, under the latest materialization, you'll see the `preview` label you named in the metadata dictionary. Click **[Show Markdown]** and the chart renders in place: trips by hour of day in Staten Island, stacked by day of week, sitting on the run that produced it. Open the asset's page and check the **Events** tab if you'd rather see it there.

Somebody asked a question by dropping a file in a folder. Dagster noticed, ran the query, drew the chart, and put the answer where anyone can find it. No handoff, no attachment, no "let me dig that up for you."

What You've Accomplished
===

Confirm the end state before you finish.

```run
dg check defs
```

You're done when:

- `dg check defs` reports all definitions loaded successfully
- The asset graph shows named groups instead of one `default` box: `raw_files`, `ingested`, and `requests` at minimum
- `taxi_trips_file` and `taxi_zones_file` both return a `dg.MaterializeResult` with a `Number of records` entry
- `taxi_trips_file` shows a plot of record counts across its monthly partitions
- `adhoc_request` shows a `preview` you can expand into a rendered chart

Now look back at the whole thing. Eight challenges ago you had an empty project and a Python function that downloaded a file. Since then you've declared dependencies so Dagster runs the graph in the right order, learned how it discovers your code and why code locations keep teams out of each other's way, pulled three copies of a DuckDB connection into one shared resource, sliced the graph into jobs and put them on a schedule, partitioned assets by month and week and backfilled history, built a sensor that watches a directory and launches runs on its own, and finished by making the whole thing document itself.

That's a production-shaped pipeline. More importantly, it's a way of thinking. You model what your pipeline produces rather than the steps it performs, and almost everything else follows from that one decision: lineage you can read, assets you can rebuild individually, freshness Dagster can reason about, and a catalog that can't drift out of sync with the code because it is the code.

Where to go next
===

Build one of your own. That's the real test, and it's the point where this stops being a course and starts being a skill.

Pick data you actually care about. Your own organization's data is the best choice if you can use it. If not, [NYC OpenData](https://opendata.cityofnewyork.us/) has plenty to work with, and the [311 Service Requests](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9) dataset is a good starting point because it's large, messy, and genuinely interesting. The [public APIs list](https://github.com/public-apis/public-apis) is another good hunting ground. DuckDB will carry you a long way, so there's no need to stand up a warehouse first.

Then aim for a project that exercises everything you just learned:

- Model the pipeline as assets with real dependencies between them
- Use a resource for whatever you connect to, whether that's a database, an API, or a plain Python client
- Transform the data into something worth querying, in memory or in the warehouse
- Partition at least one asset and backfill history through it
- Produce a report or a chart at the end, and put it in the metadata where people will see it
- Try one of [Dagster's integrations](https://docs.dagster.io/integrations) while you're in there

One more tool worth knowing about now that the fundamentals are in your hands: [Dagster Skills](https://github.com/dagster-io/skills), a set of AI assistant skills that generate Dagster code following the same patterns this course taught. It works with Claude Code, Cursor, and other Agent Skills-compatible tools. The order matters, though. The reason to learn assets, resources, and partitions by hand first is that AI-generated scaffolding is only useful to someone who can review it, spot what's wrong, and bend it to their actual business logic. You can do that now.

When you get stuck, the [Dagster docs](https://docs.dagster.io) go far deeper than this course could, and the [Dagster community](https://dagster.io/community) is worth joining for the questions docs don't answer.

And when you finish something, show it to someone. That's the part people skip.
