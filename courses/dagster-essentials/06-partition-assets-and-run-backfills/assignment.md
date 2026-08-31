---
slug: partition-assets-and-run-backfills
type: challenge
title: Partition Assets and Run Backfills
teaser: Slice the taxi data by month and week, then backfill three months of history in a single click.
notes:
- type: text
  contents: |-
    # Partitions split an asset into slices

    Every materialization you have run so far rebuilt an entire dataset from scratch. One month of taxi trips, downloaded and loaded, top to bottom, every time.

    A partition is a named slice of an asset. March 2023 is a partition. The week of January 8th is a partition. Dagster tracks each one separately: which slices exist, which are missing, which failed, and when each was last updated.

    Splitting an asset this way buys you four things. You only compute the slice that changed. You can run slices in parallel. You can test one slice before committing to a hundred. And when something breaks, you can see exactly which slice broke instead of staring at one giant red run.

    A partition is a mental model as much as a physical one. In the UI there is still a single `taxi_trips` asset no matter how many months it holds. How those months land in storage is your call: one DuckDB table with a `partition_date` column, or one Parquet file per month in object storage.
- type: text
  contents: |-
    # Backfills run a range of partitions at once

    A backfill materializes many partitions in one action, usually as one run per partition.

    You will reach for backfills constantly. New pipelines start life with an empty asset and years of history sitting in the source system. Logic changes, and last quarter's numbers were computed the old way. A weekend outage leaves three days missing while the schedule keeps marching forward.

    In every case the fix is the same shape: pick the range, launch the backfill, watch the slices fill in.
- type: text
  contents: |-
    # Why incremental beats "run it all again"

    Your schedule currently rebuilds everything on the fifth of every month. That works while the dataset is small, and it stops working the moment it is not. Reprocessing all of history to capture one new month is wasted compute, wasted time, and a longer window in which something can fail.

    Once the assets are partitioned, the monthly schedule materializes exactly one partition per tick. History stays put. New data arrives on its own.

    In this challenge you will partition the trip assets by month, partition the weekly metric by week, point both jobs at those partitions, and then backfill three months of NYC taxi data from the Dagster UI.
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

Your pipeline has a hard-coded month in it. `taxi_trips_file` fetches `2023-03` and nothing else, and `taxi_trips` replaces the whole `trips` table on every run. To load January, you would edit the code. To load February, you would edit it again. That is not a pipeline, that is a script with a scheduler bolted on.

Partitions fix this. You will define a monthly partition and a weekly partition, wire them into the assets and jobs you already built, and then use the partition key at runtime to decide which month to fetch. Once that is in place, launching three months of history is one dialog in the UI instead of three code edits. NYC OpenData has taxi trips going back to 2009, so you will stay inside a three month window to keep the sandbox honest about disk and download time.

Create the monthly partition
===

Partitioning an asset starts with a partitions definition, an object that describes the full set of slices an asset can have. Dagster ships prebuilt hourly, daily, weekly, and monthly definitions for time-based data, and by convention they all live in one file. Your project already has the date range you need in `assets/constants.py`.

Check the constants first so you know exactly what range you are about to partition:

```run
grep DATE src/dagster_essentials/defs/assets/constants.py
```

`START_DATE` is `2023-01-01` and `END_DATE` is `2023-04-01`. A monthly partition over that range produces three partitions: January, February, and March 2023.

Now create the file that will hold every partition in the project:

```run
touch src/dagster_essentials/defs/partitions.py
```

Open [the Code Editor](tab-Code-Editor) and add the monthly partition to `src/dagster_essentials/defs/partitions.py`. Reading the dates from `constants` instead of hard-coding them means one edit later widens the range for every asset at once.

```python
# src/dagster_essentials/defs/partitions.py
import dagster as dg
from dagster_essentials.defs.assets import constants

start_date = constants.START_DATE
end_date = constants.END_DATE

monthly_partition = dg.MonthlyPartitionsDefinition(
    start_date=start_date,
    end_date=end_date
)
```

Practice: create a weekly partition
===

`trips_by_week` aggregates by week, so a monthly partition would be the wrong shape for it. Using `dg.WeeklyPartitionsDefinition` and the same start and end dates, add a `weekly_partition` to the same file.

Try it before you read on. When you are done, your `partitions.py` should match this. Later steps import both names, so fix any differences now.

```python
# src/dagster_essentials/defs/partitions.py
import dagster as dg
from dagster_essentials.defs.assets import constants

start_date = constants.START_DATE
end_date = constants.END_DATE

monthly_partition = dg.MonthlyPartitionsDefinition(
    start_date=start_date,
    end_date=end_date
)

weekly_partition = dg.WeeklyPartitionsDefinition(
    start_date=start_date,
    end_date=end_date
)
```

Two definitions, same range, different grain. Nothing uses them yet.

Partition the taxi_trips_file asset
===

Right now `taxi_trips_file` has `month_to_fetch = "2023-03"` sitting in the function body. Attaching a partition to the asset lets Dagster tell the function which month it is running for, and the hard-coded string goes away.

Three changes turn this asset into a partitioned one. Open `src/dagster_essentials/defs/assets/trips.py` and work through them.

First, import the partition at the top of the file:

```python
from dagster_essentials.defs.partitions import monthly_partition
```

Second, pass it to the decorator with `partitions_def`. This is what tells Dagster the asset has three slices rather than one value:

```python
@dg.asset(
    partitions_def=monthly_partition
)
```

Third, add `context` as the first argument to the function. The `context` argument is not partition-specific, and this is the first time you have used it: it carries metadata about how Dagster is running your asset, including which partition it is materializing, which job triggered it, and what metadata previous materializations attached. Type hint it with `dg.AssetExecutionContext` and read `context.partition_key` from it.

One wrinkle. `context.partition_key` hands you `2023-03-01`, but the NYC OpenData files are named `yellow_tripdata_2023-03.parquet`. Slicing the last three characters off the key gives you the format the source system expects. Here is the finished asset:

```python
# src/dagster_essentials/defs/assets/trips.py
from dagster_essentials.defs.partitions import monthly_partition

@dg.asset(
    partitions_def=monthly_partition
)
def taxi_trips_file(context: dg.AssetExecutionContext) -> None:
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
```

The function body did not get more complicated. It got less hard-coded.

Practice: partition the taxi_trips asset
===

`taxi_trips` loads the parquet file into DuckDB, and it currently uses `create or replace table trips`. Replacing the table on every run is exactly the behavior partitions are meant to kill, because materializing February would erase January.

Partition it by month yourself, using these guidelines:

- Partition by the month of the parquet file, not the month of the trip. A month's file can contain stray records from outside that month, and you want the slice to match the file you fetched.
- Add a `partition_date` column so each row records which partition inserted it.
- The table now has to survive across runs, so the SQL has three jobs: create the table if it does not already exist, delete any rows for this `partition_date` so a re-run does not duplicate them, then insert the month's records.

That delete is the part worth pausing on. It is what makes the asset safe to run twice, which is what makes a backfill safe to relaunch.

Compare your version to this one and match it, since the rest of the course uses this asset as-is:

```python
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster_essentials.defs.partitions import monthly_partition

@dg.asset(
    deps=["taxi_trips_file"],
    partitions_def=monthly_partition,
)
def taxi_trips(context: dg.AssetExecutionContext, database: DuckDBResource) -> None:
    """
    The raw taxi trips dataset, loaded into a DuckDB database, partitioned by month.
    """

    partition_date_str = context.partition_key
    month_to_fetch = partition_date_str[:-3]

    query = f"""
        create table if not exists trips (
            vendor_id integer, pickup_zone_id integer, dropoff_zone_id integer,
            rate_code_id double, payment_type integer, dropoff_datetime timestamp,
            pickup_datetime timestamp, trip_distance double, passenger_count double,
            total_amount double, partition_date varchar
        );

        delete from trips where partition_date = '{month_to_fetch}';

        insert into trips
        select
            VendorID, PULocationID, DOLocationID, RatecodeID, payment_type, tpep_dropoff_datetime,
            tpep_pickup_datetime, trip_distance, passenger_count, total_amount, '{month_to_fetch}' as partition_date
        from '{constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)}';
    """

    with database.get_connection() as conn:
        conn.execute(query)
```

The `trips` table already exists from earlier challenges without a `partition_date` column, so this new SQL will fail against it. You will drop it a few steps from now.

Point the monthly job at the partition
===

`trip_update_job` runs on the fifth of every month and currently refreshes every asset in full. Now that the trip assets are partitioned, the job should materialize one partition per tick instead, which is both the cheaper option and the correct one.

Jobs take the same `partitions_def` parameter that assets do. Open `src/dagster_essentials/defs/jobs.py`, import `monthly_partition`, and add it to the job:

```python
# src/dagster_essentials/defs/jobs.py
import dagster as dg
from dagster_essentials.defs.partitions import monthly_partition

trips_by_week = dg.AssetSelection.assets("trips_by_week")

trip_update_job = dg.define_asset_job(
    name="trip_update_job",
    partitions_def=monthly_partition, # partitions added here
    selection=dg.AssetSelection.all() - trips_by_week
)
```

Your schedule in `schedules.py` does not change at all. It still points at `trip_update_job` with the cron `0 0 5 * *`. The difference is what a tick now means: one partition, not the entire history.

Practice: partition trips_by_week
===

`trips_by_week` is the last unpartitioned piece. Its current implementation loops from January 2023 to today, aggregating every week in memory and rewriting the whole CSV. Every one of those weeks is a partition waiting to be named.

Update both `trips_by_week` in `assets/metrics.py` and `weekly_update_job` in `jobs.py` to use the `weekly_partition` you defined earlier. The asset should aggregate a single week, and it should append to the CSV rather than replace it.

Start with the asset. The `while` loop disappears, `context.partition_key` becomes the start of the week, and the DuckDB query bounds itself with `interval '1 week'`:

```python
# src/dagster_essentials/defs/assets/metrics.py
from dagster_essentials.defs.partitions import weekly_partition

@dg.asset(
    deps=["taxi_trips"],
    partitions_def=weekly_partition
)
def trips_by_week(context: dg.AssetExecutionContext, database: DuckDBResource) -> None:
    """
    The number of trips per week, aggregated by week.
    """

    period_to_fetch = context.partition_key

    # get all trips for the week
    query = f"""
        select vendor_id, total_amount, trip_distance, passenger_count
        from trips
        where pickup_datetime >= '{period_to_fetch}'
            and pickup_datetime < '{period_to_fetch}'::date + interval '1 week'
    """

    with database.get_connection() as conn:
        data_for_week = conn.execute(query).fetch_df()

    aggregate = data_for_week.agg({
        "vendor_id": "count",
        "total_amount": "sum",
        "trip_distance": "sum",
        "passenger_count": "sum"
    }).rename({"vendor_id": "num_trips"}).to_frame().T # type: ignore

    # clean up the formatting of the dataframe
    aggregate["period"] = period_to_fetch
    aggregate['num_trips'] = aggregate['num_trips'].astype(int)
    aggregate['passenger_count'] = aggregate['passenger_count'].astype(int)
    aggregate['total_amount'] = aggregate['total_amount'].round(2).astype(float)
    aggregate['trip_distance'] = aggregate['trip_distance'].round(2).astype(float)
    aggregate = aggregate[["period", "num_trips", "total_amount", "trip_distance", "passenger_count"]]

    try:
        # If the file already exists, append to it, but replace the existing month's data
        existing = pd.read_csv(constants.TRIPS_BY_WEEK_FILE_PATH)
        existing = existing[existing["period"] != period_to_fetch]
        existing = pd.concat([existing, aggregate]).sort_values(by="period")
        existing.to_csv(constants.TRIPS_BY_WEEK_FILE_PATH, index=False)
    except FileNotFoundError:
        aggregate.to_csv(constants.TRIPS_BY_WEEK_FILE_PATH, index=False)
```

The `try`/`except` is the CSV equivalent of the delete-then-insert you wrote for DuckDB: drop this week's row if it is already there, then write it fresh. Re-running a partition produces the same file either way. The `datetime` and `timedelta` imports at the top of `metrics.py` are now unused, so you can remove that import line.

Then give the weekly job its partition:

```python
# src/dagster_essentials/defs/jobs.py
import dagster as dg
from dagster_essentials.defs.partitions import weekly_partition

trips_by_week = dg.AssetSelection.assets("trips_by_week")

weekly_update_job = dg.define_asset_job(
    name="weekly_update_job",
    partitions_def=weekly_partition,
    selection=trips_by_week,
)
```

Both jobs now live in `jobs.py` and both import from `partitions.py`, so a single import line covering `monthly_partition` and `weekly_partition` is fine.

Clear the old local state
===

Your DuckDB table and your CSV were both built by the unpartitioned code, and neither one fits the new schema. This cleanup is a local-development chore, not something you would do in production, but skipping it will hand you a confusing failure on the first backfill.

Start by stopping the server. Switch to [the Dagster Dev tab](tab-Dagster-Dev) and press `Ctrl+C`. That also releases DuckDB's file lock and clears the materialization history of the old, unpartitioned assets, so the UI will show a clean slate.

Now drop the `trips` table in [the Terminal](tab-Terminal):

```run
python - <<'PY'
import duckdb
conn = duckdb.connect(database="data/staging/data.duckdb")
conn.execute("drop table trips;")
PY
```

If DuckDB tells you the table does not exist, nothing needed dropping and you can move on. If it complains about a lock, `dg dev` is still running in the other tab.

Remove the weekly CSV as well, since its rows use the old period format:

```run
rm -f data/outputs/trips_by_week.csv
```

Start the server again in [the Dagster Dev tab](tab-Dagster-Dev). Leave it running for the rest of the challenge:

```bash
dg dev --host 0.0.0.0 --port 3000
```

Launch a backfill from the UI
===

Everything is partitioned. Time to fill in the history.

Open [the Dagster UI](tab-Dagster-UI) and click **Reload definitions** so the server picks up your new partitions. Then go to the **Assets** page and open the lineage view.

The graph looks different now. `taxi_trips_file` and `taxi_trips` each carry a partition summary instead of a single materialization timestamp: zero partitions materialized, three missing, zero failed. `trips_by_week` shows the same summary against its own weekly range. `taxi_zones_file` and `taxi_zones` are unpartitioned and unchanged, because not every asset benefits from slicing.

Click **Materialize all**. Because the selection is partitioned, Dagster opens a launch dialog instead of firing a single run. No range is selected by default, so click **All** to select the entire range, then confirm with **Launch backfill**.

If the dialog objects to mixing partition definitions, deselect `trips_by_week` and launch the monthly assets on their own. You will backfill the weekly asset separately in a moment either way.

Now watch it work. Go to **Overview > Backfills** and click into the backfill you just launched. Dagster creates one run per partition, so you will see January, February, and March each moving through their own run with their own logs and their own status. Each month downloads roughly 50 MB of parquet and inserts about three million rows, so give it a few minutes.

When the monthly backfill finishes, select `trips_by_week` in the lineage view and materialize it the same way: click **All** in the dialog to select every week between January 1 and April 1, then launch. These runs are fast, since the data is already sitting in DuckDB and each partition is a single aggregate query.

Verify
===

Head back to the lineage view. `taxi_trips_file` and `taxi_trips` should each report three of three partitions materialized and zero failed, and `trips_by_week` should report every week in its range filled in.

Click `taxi_trips` and open its partition details. Each month is listed as its own entry with its own materialization time. Select **2023-03-01** and you will see that partition's lineage back to `taxi_trips_file`, which is Dagster tracking dependencies at the slice level, not just the asset level.

Confirm the data landed the way the SQL intended, in [the Terminal](tab-Terminal):

```run
python - <<'PY'
import duckdb
conn = duckdb.connect(database="data/staging/data.duckdb", read_only=True)
print(conn.execute("select partition_date, count(*) as trips from trips group by 1 order by 1").fetchdf())
PY
```

You should see three rows, `2023-01`, `2023-02`, and `2023-03`, each with roughly three million trips. Three partitions, three months, one table. If the connection errors out about a lock, a backfill run is still finishing.

Check the weekly output too:

```run
head -5 data/outputs/trips_by_week.csv
```

One row per weekly partition, starting at `2023-01-01`, sorted by period.

That is the whole pattern. Your monthly schedule now materializes one month per tick instead of rebuilding history, your weekly schedule does the same by week, and when you need to reprocess a range you select it in the UI and launch a backfill. You partitioned by time here because the data arrives by time, but Dagster does not require dates: you can partition by a static list of dimensions, such as region or customer, or by a dynamic list whose contents you compute at runtime.
