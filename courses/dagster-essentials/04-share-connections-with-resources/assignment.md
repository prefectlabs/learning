---
slug: share-connections-with-resources
type: challenge
title: Share Connections with Resources
teaser: Pull four copies of the same DuckDB connection into one resource your assets borrow.
notes:
- type: text
  contents: |-
    # What's a resource?

    Think about baking. The recipe is the asset: mix these things, bake them for twelve minutes, get cookies. The bowl, the tray, and the oven are not the recipe. They're the equipment the recipe reaches for.

    A resource in Dagster is that equipment. Databases, cloud storage buckets, APIs, the BI tool at the end of the line. External things your assets use but don't own.

    Right now, every asset in your project buys its own oven. In this challenge you'll buy one and let them share it.
- type: text
  contents: |-
    # Why one connection beats four

    Four of your assets open their own DuckDB connection, spread across two files. Today that costs you nothing but a few duplicated lines.

    It gets expensive the day the connection changes. Point the project at MotherDuck instead of a local file, load an extension, add a credential, and you're editing every asset that touches the database. Miss one and you get a pipeline where three assets read from the new place and one still reads from a file on your laptop. Nothing errors. The numbers are just wrong.

    Software engineers call this DRY: don't repeat yourself. One definition, referenced everywhere, means one edit.
- type: text
  contents: |-
    # The part you get for free

    Once the connection is a resource, Dagster can see it.

    The UI will tell you what resources exist, how each one is configured, and exactly which assets use it. That turns "what breaks if we migrate this database" into something you look up instead of something you guess at.

    It also makes swapping environments a config change instead of a code change. Same assets, a local DuckDB file in development, something much bigger in production.
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
difficulty: basic
timelimit: 1800
---
You have seven assets now, split across `trips.py` and `metrics.py`, and four of them open the same way: connect to DuckDB, run a query, move on. That connection code is copy-pasted. It works, and it will keep working right up until the day the connection needs to change.

In this challenge you'll lift that connection out of the assets and into a Dagster resource. Same pipeline, same results, one definition instead of four. You'll also see where Dagster records resource usage, which is the part that pays you back six months from now when someone asks what depends on the warehouse.

Find the repetition
===

Before changing anything, look at what you're changing. Every asset that queries DuckDB calls `duckdb.connect` itself, most of them wrapped in a `backoff` helper to survive the database file being locked by another process.

Count them across both asset files in the [Terminal](tab-Terminal):

```run
grep -n "duckdb.connect" src/dagster_essentials/defs/assets/trips.py src/dagster_essentials/defs/assets/metrics.py
```

You should see four matches: `taxi_trips` and `taxi_zones` in `trips.py`, then `manhattan_stats` and `trips_by_week` in `metrics.py`. The other three assets stay out of it. `taxi_trips_file` and `taxi_zones_file` only download files, and `manhattan_map` reads the GeoJSON that `manhattan_stats` already wrote.

Four is manageable. Forty is a maintenance problem, and real projects get to forty faster than you'd think.

Scaffold the resources file
===

Dagster's `dg` CLI scaffolds resources the same way it scaffolded assets earlier in this course. Run it from the project root:

```run
dg scaffold defs dagster.resources resources.py
```

That creates `resources.py` next to your `assets` directory:

```text
.
└── src
    └── dagster_essentials
        └── defs
            ├── assets
            └── resources.py
```

Open the new file in the [Code Editor](tab-Code-Editor). The scaffold gives you a working skeleton with nothing in it yet:

```python
# src/dagster_essentials/defs/resources.py
import dagster as dg


@dg.definitions
def resources() -> dg.Definitions:
    return dg.Definitions(resources={})
```

The `@dg.definitions` decorator is how this file gets discovered. Dagster scans the `defs` module at load time, finds anything decorated this way, and merges the results. Your job is to fill in that empty dictionary.

Define the DuckDB resource
===

You don't have to write a DuckDB resource from scratch. The `dagster_duckdb` integration library ships one, and it already handles connection retries, which is why the `backoff` helper disappears from your assets in a minute.

First, look at the environment variable the project already uses for the database path:

```run
cat .env
```

That's `DUCKDB_DATABASE=data/staging/data.duckdb`. Your assets read it today with `os.getenv`. The resource will read it with `dg.EnvVar`, which looks similar but behaves differently in a way that matters: `os.getenv` reads the value once, when the code location loads, while `EnvVar` reads it every time a run starts. That means you can point the project at a different database and pick up the change on the next run instead of restarting the web server.

Replace the contents of `resources.py` with this:

```python
# src/dagster_essentials/defs/resources.py
import dagster as dg
from dagster_duckdb import DuckDBResource

database_resource = DuckDBResource(
    database=dg.EnvVar("DUCKDB_DATABASE"),
)


@dg.definitions
def resources() -> dg.Definitions:
    return dg.Definitions(resources={"database": database_resource})
```

Two things are happening. You created one configured instance of `DuckDBResource` and stored it in `database_resource`. Then you gave it the key `"database"`, which is the name your assets will use to ask for it. The key is the contract, so pick names you'll still understand later.

Load the resource and look it up in the UI
===

Definitions only exist once Dagster loads them. If `dg dev` is still running in the [Dagster Dev](tab-Dagster-Dev) tab from the last challenge, leave it. If not, start it there:

```bash
dg dev --host 0.0.0.0 --port 3000
```

Now [open the Dagster UI](tab-Dagster-UI) and find what you just defined:

1. Click **Deployment**.
2. On the **Code locations** tab, click **Reload** next to the `dagster_essentials` code location.
3. Click the code location to open it, then click the **Definitions** tab.
4. Click **Resources** in the left side panel and select **database**.

Look at the **Uses** count. It's **0**. The resource is defined and loaded, and not one asset has asked for it yet. That number is your scoreboard for the rest of this challenge.

Refactor taxi_trips
===

Here's `taxi_trips` as it stands, connecting to DuckDB on its own:

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(deps=["taxi_trips_file"])
def taxi_trips() -> None:
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

Start by adding the import that gives you the type hint. Put this near the top of `trips.py`, with the other imports:

```python
# src/dagster_essentials/defs/assets/trips.py
from dagster_duckdb import DuckDBResource
```

Now change the asset itself. The query is untouched. Only the plumbing moves:

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(deps=["taxi_trips_file"])
def taxi_trips(database: DuckDBResource) -> None:
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

    with database.get_connection() as conn:
        conn.execute(query)
```

Three changes, and the middle one is the one people miss:

1. The function takes a new parameter, `database`.
2. That parameter is annotated `DuckDBResource`. The type hint is not decoration. It's how Dagster knows `database` is a resource to inject and not an upstream asset to look up. The parameter name has to match the key you registered in `resources.py`.
3. Eleven lines of connection setup collapse into `with database.get_connection() as conn`. The `backoff` retry logic is gone because `DuckDBResource` already does it.

Practice: refactor the remaining assets
===

You've seen the pattern once. Apply it to the other three yourself: `taxi_zones` in `trips.py`, then `manhattan_stats` and `trips_by_week` in `metrics.py`. Each one needs the parameter, the type hint, and its connection block replaced.

`metrics.py` needs its own copy of the import, since Python imports are per-file:

```python
# src/dagster_essentials/defs/assets/metrics.py
from dagster_duckdb import DuckDBResource
```

Two of the three have wrinkles worth thinking about before you look at the answers. `manhattan_stats` calls `duckdb.connect` directly with no `backoff` wrapper, so its block looks different from the one you just replaced. And `trips_by_week` opens a single connection before its `while` loop and reuses it for every week. With a resource, ask for the connection where you actually use it, inside the loop.

When you're done, compare against these. If yours differs, match it, because the rest of the course assumes this code.

`taxi_zones` is the straightforward one:

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(deps=["taxi_zones_file"])
def taxi_zones(database: DuckDBResource) -> None:
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

    with database.get_connection() as conn:
        conn.execute(query)
```

`manhattan_stats` takes the resource the same way. Its bare `duckdb.connect` line and the `fetch_df` call underneath it become a single `with` block, and everything from the GeoDataFrame conversion down is untouched:

```python
# src/dagster_essentials/defs/assets/metrics.py
@dg.asset(deps=["taxi_trips", "taxi_zones"])
def manhattan_stats(database: DuckDBResource) -> None:
    query = """
        ...  # leave your existing query exactly as it is
    """

    with database.get_connection() as conn:
        trips_by_zone = conn.execute(query).fetch_df()

    ...  # the GeoSeries conversion and the GeoJSON write stay as they are
```

For `trips_by_week`, only two spots change. The signature picks up the resource:

```python
# src/dagster_essentials/defs/assets/metrics.py
@dg.asset(deps=["taxi_trips"])
def trips_by_week(database: DuckDBResource) -> None:
```

Then delete the `conn = backoff(...)` block above the loop and wrap the query execution inside the loop instead:

```python
        with database.get_connection() as conn:
            data_for_week = conn.execute(query).fetch_df()
```

Everything else in that function, the date math, the aggregation, the CSV write, stays exactly as it is. You're changing how the connection is obtained, not what the asset computes.

With all four assets refactored, the old imports in both files have nothing left to import for. Check:

```run
grep -n "backoff\|os.getenv" src/dagster_essentials/defs/assets/trips.py src/dagster_essentials/defs/assets/metrics.py
```

If that returns nothing, delete `import os`, `import duckdb`, and `from dagster._utils.backoff import backoff` from the top of both files. Leave the `geopandas`, `matplotlib`, and `pandas` imports in `metrics.py` alone, since `manhattan_map` and `trips_by_week` still need them. Then confirm the project still loads cleanly:

```run
dg check defs
```

Confirm the resource is doing the work
===

Reload the code location in the [Dagster UI](tab-Dagster-UI) again, then materialize your assets so you can prove the refactor didn't change the pipeline's behavior. Go to **Assets**, select all of them, and click **Materialize selected**. Every asset should land green, same as before.

Now go back to the resource page: **Deployment**, the `dagster_essentials` code location, the **Definitions** tab, then **Resources** in the side panel, and click **database**.

The **Uses** column now reads **4** instead of 0.

Click the **Uses** tab and you'll see them by name: `taxi_trips`, `taxi_zones`, `manhattan_stats`, and `trips_by_week`. The **Configuration** tab next to it shows the resource type and how it's configured. This is the payoff for the refactor. When someone asks which pipelines a database migration would break, or where a spike in warehouse cost is coming from, you have a page that answers it instead of a `grep` and a hopeful guess.

Verify
===

You're done when all of the following are true:

- `dg check defs` exits without errors.
- The `backoff` and `os.getenv` grep returns nothing for either `trips.py` or `metrics.py`.
- `src/dagster_essentials/defs/resources.py` defines `database_resource` and registers it under the key `database`.
- All seven assets materialize successfully from the Dagster UI.
- The **database** resource page shows **Uses: 4**, listing `taxi_trips`, `taxi_zones`, `manhattan_stats`, and `trips_by_week`.

You now have one place to change when the database changes, and a UI that knows who depends on it. The same pattern covers everything else you'll connect to later. Dagster ships integration libraries for S3, Snowflake, BigQuery, dbt, and plenty more, and when there isn't a library, you can pass any Python object into `Definitions` as a resource and type-hint it with `dg.ResourceParam[YourClass]`.
