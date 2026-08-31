---
slug: connect-assets-with-dependencies
id: 7dkpriynqsck
type: challenge
title: Connect Assets with Dependencies
teaser: Declare dependencies with deps, load raw files into DuckDB, and watch Dagster
  run the graph in order.
notes:
- type: text
  contents: |-
    # What a dependency is

    A dependency is a relationship between two assets. It has a direction, and the vocabulary for that direction is worth getting straight early, because the UI, the docs, and your coworkers all use it.

    An asset is **downstream** when it depends on something else. It's **upstream** when something else depends on it. Back to the cookies: dough is downstream of flour, and flour is upstream of dough. The same relationship, described from two ends.

    You'll also hear family terms. A **child** is downstream of its **parent**. An **ancestor** is further back up the chain: flour is the parent of dough, dough is the parent of cookies, so flour is an ancestor of cookies.

    In Dagster you declare the relationship on the child. The asset that needs something names what it needs. Ordering, the arrows in the lineage graph, and knowing when an input has gone stale all fall out of that one declaration.
- type: text
  contents: |-
    # Assets and database execution

    You have two files on disk. Files are fine for storage and miserable for analysis, so the next move in almost every pipeline is loading them into a database.

    This project ships with DuckDB, an embedded analytical database. There's no server to run and no credentials to manage. The whole database is a single file at `data/staging/data.duckdb`, and the path comes from the `DUCKDB_DATABASE` environment variable in the project's `.env`. DuckDB can also read a parquet or CSV file directly inside a `SELECT`, which means loading a raw file is one SQL statement rather than a parsing script.

    Here's the part that matters for your mental model: **Dagster does not run your SQL**. Your asset function opens a connection and executes the query itself. Dagster decides when that function runs, guarantees that its upstream assets ran first, and records what happened. The computation lives wherever you put it, which in this challenge is DuckDB.

    One consequence of an embedded database: only one process can write to the file at a time. Several assets materializing together will contend for it. That's why the connection gets wrapped in Dagster's `backoff` helper, which retries the connect instead of failing the run.
- type: text
  contents: |-
    # Two places the work can happen

    Once data is in a database, you have a choice for every transformation you write.

    Push the work into the database and let SQL do it. Joins, filters, and aggregations over large tables belong here. The rows never leave the engine, so memory on your machine stops being the limit.

    Or pull the rows into Python and compute in memory. You give up the engine's scale, and you get every Python library there is: pandas for reshaping, GeoPandas for geometry, Matplotlib for a chart, whatever your model needs.

    Both are assets. The `@dg.asset` decorator does not care which one you chose, and neither does the lineage graph. You'll write one of each in this challenge, and the deciding question is usually simple: how much data has to be in memory at once, and does a library exist that does this better than SQL?
tabs:
- id: eyixtwjhfhaa
  title: Terminal
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
  cmd: /bin/bash
- id: y1jd9mxtxdy8
  title: Dagster Dev
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
  cmd: /bin/bash
- id: fhloilhvwijo
  title: Code Editor
  type: code
  hostname: dagster-sandbox
  path: /root/project-dagster-university/dagster_university/dagster_essentials
- id: mp2bccjcsm7a
  title: Dagster UI
  type: service
  hostname: dagster-sandbox
  port: 3000
difficulty: basic
timelimit: 1800
enhanced_loading: null
---
Connect Assets with Dependencies
===

You finished the last challenge with two assets sitting next to each other in the graph. `taxi_trips_file` downloads a month of trip records. `taxi_zones_file` downloads the neighborhood lookup. Neither one knows the other exists, and neither one is useful yet, because raw files on disk are where analysis starts, not where it happens.

In this challenge you'll add five assets that build on those files, and the important word in that sentence is *on*. You'll load the parquet into a DuckDB table, do the same for the zones CSV, join the two into per-neighborhood trip counts, draw a map of Manhattan from the result, and aggregate the trips into a weekly summary. Each of those declares what it depends on, and Dagster turns those declarations into execution order, into the arrows you see in the lineage graph, and into the answer when someone asks what a broken file affects.

One thing to check before you start. The Dagster server should still be running in the [Dagster Dev](tab-Dagster-Dev) tab from the last challenge. If that tab is empty or the process stopped, start it again there and leave it running.

```bash
dg dev --host 0.0.0.0 --port 3000
```

Load the trips file into DuckDB
===

Start with the imports. Open `src/dagster_essentials/defs/assets/trips.py` in the [Code Editor](tab-Code-Editor) tab. You need three additions at the top: `duckdb` to talk to the database, `os` to read the database path out of the environment, and `backoff` from Dagster's utilities to make the connection retry instead of failing when another asset holds the file.

```python
import duckdb
import os
import dagster as dg
from dagster._utils.backoff import backoff
```

Leave the `requests` and `constants` imports you already have. Now add the asset at the bottom of the same file. The shape will look familiar, with one new argument on the decorator.

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(
    deps=["taxi_trips_file"]
)
def taxi_trips() -> None:
    """
    The raw taxi trips dataset, loaded into a DuckDB database
    """
    query = """
        create or replace table trips as (
          select
            VendorID as vendor_id,
            PULocationID as pickup_zone_id,
            DOLocationID as dropoff_zone_id,
            RatecodeID as rate_code_id,
            payment_type as payment_type,
            tpep_dropoff_datetime as dropoff_datetime,
            tpep_pickup_datetime as pickup_datetime,
            trip_distance as trip_distance,
            passenger_count as passenger_count,
            total_amount as total_amount
          from 'data/raw/taxi_trips_2023-03.parquet'
        );
    """

    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={
            "database": os.getenv("DUCKDB_DATABASE"),
        },
        max_retries=10,
    )
    conn.execute(query)
```

Read it from the top. `deps=["taxi_trips_file"]` is the whole dependency declaration, and it takes asset keys as strings. The SQL creates a table called `trips` by selecting straight out of the parquet file, renaming the source columns into something you'd want to type in a query later. `backoff` wraps `duckdb.connect`, retrying up to ten times on `RuntimeError` and `duckdb.IOException`, and passes the database path through from `DUCKDB_DATABASE`. Then `conn.execute(query)` does the actual work.

Notice what `deps` does *not* do. No parquet file gets handed to your function. Dagster is not moving data between these assets, it's promising that `taxi_trips_file` is up to date before `taxi_trips` runs, and recording the edge between them. The asset reads the file off disk by path, exactly as it would if you ran it by hand.

That `DUCKDB_DATABASE` variable comes from the `.env` file in the project root, and it resolves to `data/staging/data.duckdb`. Confirm it's there, because an empty value would quietly hand you an in-memory database that vanishes when the run ends.

```run
cat .env
```

Save the file, then validate it from the [Terminal](tab-Terminal) tab.

```run
dg check defs
```

Reload the definitions and materialize
===

Switch to the [Dagster UI](tab-Dagster-UI) tab and open the global asset lineage view. Your new asset isn't there. That's expected, not broken.

Dagster loaded your code once when `dg dev` started. Because the project is installed in editable mode, edits inside an existing asset's function body get picked up automatically, but adding a brand new asset changes the set of definitions Dagster knows about, and that requires a reload. Click **Reload definitions** near the top right of the page.

`taxi_trips` appears, with an arrow running into it from `taxi_trips_file`. That arrow is the `deps` argument you just wrote, rendered.

Now materialize the whole graph. With nothing selected, the button in the top right reads **Materialize all**; click it, then click through to the run that starts. The two file assets re-download their data, so give it a minute.

Watch the order on the **Run details** page. `taxi_trips_file` and `taxi_zones_file` start at the same time, because nothing connects them and Dagster has no reason to serialize them. `taxi_trips` sits and waits. It doesn't begin until `taxi_trips_file` finishes successfully, and if that download had failed, `taxi_trips` would never have run at all. You didn't write that logic. You declared a dependency and got it.

Check the table from outside Dagster
===

The UI says the asset materialized. Confirming the table is really in DuckDB is a different claim, and it's worth proving once so you trust the green box later. Run this in the [Terminal](tab-Terminal) tab.

```run
python - <<'PY'
import duckdb
conn = duckdb.connect(database="data/staging/data.duckdb")
print(conn.execute("select count(*) from trips").fetchall())
PY
```

You should get back a single row with a count in the millions, which is roughly how many yellow cab trips New York City ran in March 2023. The path is hardcoded here because a plain shell doesn't read the project's `.env` the way `dg dev` does.

If you get an IO or lock error instead, a run is probably still holding the database. Wait for it to finish and try again. This snippet opens its connection and exits, which releases the file. Leaving a Python REPL open on that database will block your next materialization.

Practice: build the taxi_zones asset
===

Same pattern, second dataset. The zones CSV is on disk from the last challenge and it needs to become a table so you can join trips to neighborhoods.

In `trips.py`, add an asset named `taxi_zones` that depends on `taxi_zones_file` and creates a table called `zones` with four columns:

- `zone_id`, which is the `LocationID` column, renamed
- `zone`
- `borough`
- `geometry`, which is the `the_geom` column, renamed

Two hints worth having. Use `constants.TAXI_ZONES_FILE_PATH` for the source file instead of typing the path again, which means the query needs to be an f-string. And DuckDB reads a CSV in a `SELECT` the same way it reads parquet, so the shape of the statement doesn't change.

When you've written it, validate and materialize it.

```run
dg check defs
```

Then reload definitions in the [Dagster UI](tab-Dagster-UI), select `taxi_zones` in the asset graph, and click **Materialize selected**.

Practice: check your taxi_zones asset
===

Write yours before you read this. Comparing two working versions teaches more than copying one.

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(
    deps=["taxi_zones_file"]
)
def taxi_zones() -> None:
    query = f"""
        create or replace table zones as (
            select
                LocationID as zone_id,
                zone,
                borough,
                the_geom as geometry
            from '{constants.TAXI_ZONES_FILE_PATH}'
        );
    """

    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={
            "database": os.getenv("DUCKDB_DATABASE"),
        },
        max_retries=10,
    )
    conn.execute(query)
```

If yours differs, match it. Later challenges join against this table by these exact column names.

Confirm the table landed, same way as before.

```run
python - <<'PY'
import duckdb
conn = duckdb.connect(database="data/staging/data.duckdb")
print(conn.execute("select count(*) from zones").fetchall())
PY
```

Roughly 260 rows, one per taxi zone in the city.

Move the computation into Python
===

Everything so far has handed the work to DuckDB and let it stay there. Some transformations don't fit that shape. You need a library SQL doesn't have, or you're building a file rather than a table, and the rows have to come into Python memory to do it.

Those assets tend to be analysis rather than ingestion, so they get their own file. One module holding every asset in a project stops being readable fast. Scaffold a second asset file with `dg`, which puts it where Dagster expects.

```run
dg scaffold defs dagster.asset assets/metrics.py
```

Open `src/dagster_essentials/defs/assets/metrics.py` in the [Code Editor](tab-Code-Editor), delete the scaffolded placeholder, and start with the imports. Two of these are new: GeoPandas reads and writes geographic data, and Matplotlib draws the chart. You'll use both in the next few minutes.

```python
import os
from datetime import datetime, timedelta

import dagster as dg
import duckdb
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from dagster._utils.backoff import backoff

from dagster_essentials.defs.assets import constants
```

Nothing about this file is special to Dagster. It's a new Python module in the defs folder, and Dagster picks up any asset it finds there once you reload definitions.

Count trips by neighborhood
===

The first metrics asset answers a question the raw tables can't: which Manhattan neighborhoods do the most rides start in? That requires both tables, so it depends on both. Add this to the bottom of `metrics.py`.

```python
# src/dagster_essentials/defs/assets/metrics.py
@dg.asset(
    deps=["taxi_trips", "taxi_zones"]
)
def manhattan_stats() -> None:
    query = """
        select
            zones.zone,
            zones.borough,
            zones.geometry,
            count(1) as num_trips,
        from trips
        left join zones on trips.pickup_zone_id = zones.zone_id
        where borough = 'Manhattan' and geometry is not null
        group by zone, borough, geometry
    """

    conn = duckdb.connect(os.getenv("DUCKDB_DATABASE"))
    trips_by_zone = conn.execute(query).fetch_df()

    trips_by_zone["geometry"] = gpd.GeoSeries.from_wkt(trips_by_zone["geometry"])
    trips_by_zone = gpd.GeoDataFrame(trips_by_zone)

    with open(constants.MANHATTAN_STATS_FILE_PATH, 'w') as output_file:
        output_file.write(trips_by_zone.to_json())
```

Four things happen here, and the split between them is the point. The SQL joins `trips` to `zones` on the pickup location, keeps Manhattan, and counts rides per neighborhood, so the heavy work stays in DuckDB. Then `fetch_df()` pulls the result back as a pandas DataFrame, which is small now: a few dozen rows, one per zone.

The last two steps are why this asset needed Python at all. The `geometry` column arrives as text, in a format called well-known text, which is a shape written out as a string. `gpd.GeoSeries.from_wkt` turns those strings into real geometry objects, and wrapping the DataFrame in a `GeoDataFrame` gives you something the geospatial tools understand. Then it writes the whole thing to a GeoJSON file at `data/staging/manhattan_stats.geojson`.

Note the two `deps`. An asset can depend on as many parents as it needs, and Dagster waits on all of them.

Save the file, validate it, and materialize it. Reload definitions in the [Dagster UI](tab-Dagster-UI), select `manhattan_stats` in the asset graph, and click **Materialize selected**.

```run
dg check defs
```

When the run finishes, confirm the file is there and is valid JSON.

```run
ls -lh data/staging/manhattan_stats.geojson && python -c "import json; d=json.load(open('data/staging/manhattan_stats.geojson')); print(len(d['features']), 'zones')"
```

You should see a large file and somewhere between 60 and 70 zones. It's ugly to read and perfectly structured, which is exactly what the next asset wants.

Draw the map
===

Numbers in a GeoJSON file are hard to argue with and harder to look at. The last asset in this chain reads that file back, colors each neighborhood by its trip count, and saves a PNG. It depends only on `manhattan_stats`, because that's the only input it touches.

Add this at the bottom of `metrics.py`.

```python
# src/dagster_essentials/defs/assets/metrics.py
@dg.asset(
    deps=["manhattan_stats"],
)
def manhattan_map() -> None:
    trips_by_zone = gpd.read_file(constants.MANHATTAN_STATS_FILE_PATH)

    fig, ax = plt.subplots(figsize=(10, 10))
    trips_by_zone.plot(column="num_trips", cmap="plasma", legend=True, ax=ax, edgecolor="black")
    ax.set_title("Number of Trips per Taxi Zone in Manhattan")

    ax.set_xlim(-74.05, -73.90)  # Adjust longitude range
    ax.set_ylim(40.70, 40.82)  # Adjust latitude range

    # Save the image
    plt.savefig(constants.MANHATTAN_MAP_FILE_PATH, format="png", bbox_inches="tight")
    plt.close(fig)
```

GeoPandas reads the GeoJSON back into memory, `plot` fills each zone by its `num_trips` value using the `plasma` color scale, and the `set_xlim` and `set_ylim` calls crop the view down to Manhattan so the island fills the frame. Matplotlib writes the result to `data/outputs/manhattan_map.png`.

Reload definitions in the [Dagster UI](tab-Dagster-UI), select `manhattan_map`, and click **Materialize selected**. Then open `data/outputs/manhattan_map.png` from the file tree in the [Code Editor](tab-Code-Editor) tab.

```run
ls -lh data/outputs/manhattan_map.png
```

There's the island, one shape per taxi zone, shaded from dark purple to bright yellow with a legend down the side. The bright zones are Midtown and the Upper East Side. The dark ones are the edges, uptown and along the water. Sit with it for a second, because this picture started as a URL. A parquet file came down off the internet, landed in a database, got joined to a lookup table, aggregated, converted into geometry, and rendered. Six assets, each one a plain Python function, and the only thing connecting them is a list of names in a decorator.

Practice: build the trips_by_week asset
===

Time for a real one. Write an asset in `metrics.py` named `trips_by_week` that depends on `taxi_trips` and produces a CSV at `constants.TRIPS_BY_WEEK_FILE_PATH`, with this schema:

- `period` - a string representing the Sunday of the week aggregated by, ex. `2023-03-05`
- `num_trips` - The total number of trips that started in that week
- `passenger_count` - The total number of passengers that were on a taxi trip that week
- `total_amount` - The total sum of the revenue produced by trips that week
- `trip_distance` - The total miles driven in all trips that happened that week

You already know everything you need. A few notes that will save you time:

- There are several right answers here. Aggregating in SQL is valid. So is pulling a DataFrame and aggregating in pandas.
- No new imports are required, though you're welcome to add any you want.
- Hard code the date range to the data you actually have, `2023-03-05` through `2023-04-01`. Real taxi data has stray timestamps from other years in it, and filtering to a known window keeps the output clean.
- DuckDB does date math. `'2023-03-05'::date + interval '1 week'` works exactly like it reads.

The exact numbers depend on how you filter, but your CSV should come out looking like this:

```shell
period,num_trips,total_amount,trip_distance,passenger_count
2023-03-05,679681,18495110.72,2358944.42,886486
2023-03-12,686461,19151177.45,2664123.87,905296
2023-03-19,640158,17908993.09,2330611.91,838066
```

**Extra credit.** Suppose the full `trips` table is too large to fit in memory, but one week of it fits comfortably. How would you structure the function then? That constraint changes the answer, and it's the reason the reference solution is written the way it is.

Practice: check your trips_by_week asset
===

Try it first. Then compare.

This solution is one of many, and it's not the prettiest code in the course. It answers the extra credit by pulling one week at a time and stitching the aggregates together, which is why there's a loop where a single query would do. Later in the course you'll meet partitions, and this asset is the one you'll rewrite with them.

```python
# src/dagster_essentials/defs/assets/metrics.py
@dg.asset(
    deps=["taxi_trips"]
)
def trips_by_week() -> None:
    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={
            "database": os.getenv("DUCKDB_DATABASE"),
        },
        max_retries=10,
    )

    current_date = datetime.strptime("2023-03-05", constants.DATE_FORMAT)
    end_date = datetime.strptime("2023-04-01", constants.DATE_FORMAT)

    result = pd.DataFrame()

    while current_date < end_date:
        current_date_str = current_date.strftime(constants.DATE_FORMAT)
        query = f"""
            select
                vendor_id, total_amount, trip_distance, passenger_count
            from trips
            where pickup_datetime >= '{current_date_str}'::date
              and pickup_datetime < '{current_date_str}'::date + interval '1 week'
        """

        data_for_week = conn.execute(query).fetch_df()

        aggregate = data_for_week.agg({
            "vendor_id": "count",
            "total_amount": "sum",
            "trip_distance": "sum",
            "passenger_count": "sum"
        }).rename({"vendor_id": "num_trips"}).to_frame().T # type: ignore

        aggregate["period"] = current_date

        result = pd.concat([result, aggregate])

        current_date += timedelta(days=7)

    # clean up the formatting of the dataframe
    result['num_trips'] = result['num_trips'].astype(int)
    result['passenger_count'] = result['passenger_count'].astype(int)
    result['total_amount'] = result['total_amount'].round(2).astype(float)
    result['trip_distance'] = result['trip_distance'].round(2).astype(float)
    result = result[["period", "num_trips", "total_amount", "trip_distance", "passenger_count"]]
    result = result.sort_values(by="period")

    result.to_csv(constants.TRIPS_BY_WEEK_FILE_PATH, index=False)
```

Look at where the compute happens. The query pulls one week of raw rows out of DuckDB, and the counting and summing happen in pandas, in memory, one week at a time. Contrast that with `taxi_trips`, which never brought a single row into Python. Same decorator, same graph, entirely different execution.

If yours differs, match it. The rest of the course extends this asset as written.

```run
dg check defs
```

What You've Accomplished
===

Reload definitions in the [Dagster UI](tab-Dagster-UI) one more time, then click **Materialize all** and watch the whole graph run.

The lineage view now shows a connected graph instead of two loose boxes. Both file assets sit on the left. `taxi_trips_file` feeds `taxi_trips`, which feeds both `trips_by_week` and `manhattan_stats`. `taxi_zones_file` feeds `taxi_zones`, which also feeds `manhattan_stats`. And `manhattan_map` hangs off the end. The two downloads start in parallel, `manhattan_stats` waits for both of its parents, and nothing runs before its inputs are ready, in an order you never had to schedule.

Confirm the end state from the [Terminal](tab-Terminal) tab.

```run
ls -lh data/staging/data.duckdb data/staging/manhattan_stats.geojson data/outputs/manhattan_map.png data/outputs/trips_by_week.csv && cat data/outputs/trips_by_week.csv
```

You're done when:

- `data/staging/data.duckdb` exists and holds both a `trips` table and a `zones` table
- `data/staging/manhattan_stats.geojson` exists and parses as JSON
- `data/outputs/manhattan_map.png` exists and shows Manhattan shaded by trip count
- `data/outputs/trips_by_week.csv` exists with a header and four rows, one per week, starting `2023-03-05`
- `dg check defs` reports all definitions loaded successfully
- The asset graph shows all seven assets connected: `taxi_trips` and `taxi_zones` downstream of their file assets, `manhattan_stats` downstream of both tables, `manhattan_map` downstream of `manhattan_stats`, and `trips_by_week` downstream of `taxi_trips`

Seven assets, five of them written in this challenge, and a pipeline that runs itself in the right order. The thing to take from this challenge is how little it took to get there. One argument, `deps`, on a decorator. Everything else, the ordering, the arrows, the ability to point at that map and trace it back to a file on the internet, comes free with that declaration.

Next you'll look at how Dagster finds and organizes all of this code, and what happens when one project grows past a single folder of assets.
