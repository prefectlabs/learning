---
slug: organize-definitions-and-code-locations
id: 2o07t9ln4cmc
type: challenge
title: Organize Definitions and Code Locations
teaser: Find out how Dagster discovers your assets, and why code locations keep teams
  out of each other's way.
notes:
- type: text
  contents: |-
    # The Definitions object

    You have written seven assets, but nothing in `trips.py` or `metrics.py` announces itself to Dagster. There is no manifest and no registration call.

    That work happens in one place. Every asset, resource, and schedule in a project belongs to a single `Definitions` object, and that object lives in `definitions.py`. Modern Dagster projects build it by autoloading: the loader walks the `defs` directory, imports what it finds, and collects everything into one object. This is why `dg scaffold` has been putting your files under `defs` the whole time.

    In this challenge you will read that file, prove what it loaded from the command line, and find the same thing in the UI.
- type: text
  contents: |-
    # What a code location is

    A code location is a collection of Dagster definitions. It has exactly two parts: a Python module containing a `Definitions` object, and a Python environment that can import that module.

    The second half is the interesting one. Because each code location carries its own environment, one team can run Python 3.10 and PyTorch v1 while another runs Python 3.13 and PyTorch v2, in the same Dagster deployment. Marketing can ship a change at noon without taking down the machine learning pipelines. A compliance-sensitive dataset can sit behind its own boundary.

    Before code locations, teams solved this by standing up separate deployments. That works until you want to see everything at once. Separate deployments mean separate UIs, separate access management, separate upgrades, and no way for an asset in one to depend on an asset in another. Code locations give you the isolation without the silos.
- type: text
  contents: |-
    # Loading is not free

    Definitions load once, when the code location starts. That means a broken import or a duplicate asset key does not show up when you save the file. It shows up when Dagster next tries to load your code.

    You will cause one of those failures on purpose, read the error the way you would read it on a real project, and then reload the code location to bring it back. Knowing where that error surfaces is the difference between a two-minute fix and an afternoon.
tabs:
- id: h3quuqdyhgzu
  title: Terminal
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
  cmd: /bin/bash
- id: nedgr177fycl
  title: Dagster Dev
  type: terminal
  hostname: dagster-sandbox
  workdir: /root/project-dagster-university/dagster_university/dagster_essentials
  cmd: /bin/bash
- id: ihzxsupmyurh
  title: Code Editor
  type: code
  hostname: dagster-sandbox
  path: /root/project-dagster-university/dagster_university/dagster_essentials
- id: v79t9usda3ua
  title: Dagster UI
  type: service
  hostname: dagster-sandbox
  port: 3000
difficulty: basic
timelimit: 1200
enhanced_loading: null
---
Where your assets actually live
===

You have built seven assets across two files and watched them show up in the asset graph. Look closely at what you wrote, though. Nothing in `trips.py` says "register me." There is no import list, no manifest, no line connecting your functions to the UI you were clicking around in.

Something else is doing that work, and this challenge is about finding it. You will read the file that collects your definitions, confirm from the command line exactly what Dagster loaded, then find the same thing in the UI under a name you have not met yet: the code location. Less typing than the last two challenges. More looking.

Start in the [Code Editor](tab-Code-Editor) and open `src/dagster_essentials/definitions.py`. The whole file is nine lines:

```python
# src/dagster_essentials/definitions.py
from pathlib import Path

from dagster import definitions, load_from_defs_folder


@definitions
def defs():
    return load_from_defs_folder(project_root=Path(__file__).parent.parent.parent)
```

The `@definitions` decorator marks this function as the entry point Dagster calls when it loads your project. `load_from_defs_folder` does the collecting: it walks the `defs` directory, imports every module it finds, and gathers the assets, resources, and schedules into one `Definitions` object. The `parent.parent.parent` climbs from `definitions.py` up through `dagster_essentials` and `src` to the project root, so the loader starts from the same place no matter which directory you ran the command from.

This is why `dg scaffold` has been dropping your files under `defs` since the first challenge. That directory is not a convention for tidiness. It is the search path:

```text
src
└── dagster_essentials
    ├── definitions.py
    └── defs
        └── assets
            ├── __init__.py
            ├── constants.py
            ├── metrics.py
            └── trips.py
```

One more link in the chain. When you run `dg dev`, Dagster reads `pyproject.toml` to learn which module holds the definitions. Open it in the editor and find this block near the bottom:

```toml
[tool.dg]
directory_type = "project"

[tool.dg.project]
root_module = "dagster_essentials"
registry_modules = [
    "dagster_essentials.components.*",
]
```

`root_module` is the whole answer to "how did Dagster find my code." It points at `dagster_essentials`, which contains `definitions.py`, which autoloads `defs`. Three hops from a config file to your asset functions.

Prove what Dagster loaded
===

Reading the code is one thing. Asking Dagster what it actually found is better, and you do not need the UI for it. Run this in the [Terminal](tab-Terminal):

```run
dg list defs
```

You should see a table with your seven assets in it: `taxi_trips_file`, `taxi_zones_file`, `taxi_trips`, `taxi_zones`, `manhattan_stats`, `manhattan_map`, and `trips_by_week`. That table is the contents of the `Definitions` object, printed. Nothing you did registered them by hand. The loader found them because they sit under `defs`.

Listing tells you what is there. Validating tells you whether it all holds together. `dg check defs` loads your definitions and resolves them without running a single line of your asset bodies, which means no downloads, no DuckDB writes, and no waiting:

```run
dg check defs
```

A clean project prints a success message and exits with code 0. A broken one prints the traceback and exits 1. Keep this command close. It is the fastest feedback loop in a Dagster project, and it catches the class of mistake that only appears at load time.

Find the code location in the UI
===

Every definition you just listed belongs to a code location. In the UI, that code location gets a name, a status, and a reload button, so let's go look at it.

Make sure `dg dev` is still running. Switch to the [Dagster Dev](tab-Dagster-Dev) tab and check for the server output from the last challenge. If the process stopped, start it again:

```bash
dg dev --host 0.0.0.0 --port 3000
```

Now [open the Dagster UI](tab-Dagster-UI) and click **Deployment** in the top navigation, then the **Code locations** tab. You will see a single row named `dagster_essentials`, with a green status of **Loaded** and a timestamp for when it was last updated.

That name is not something anyone configured. By default a code location takes the name of the module Dagster loaded, which here is the `root_module` from `pyproject.toml`. One project, one `Definitions` object, one code location, one row. You will keep it that way for this course. On a real deployment this list is where you would see the marketing team's location beside the ML team's, each with its own status and its own Python environment behind it.

Break the code location on purpose
===

A code location loads once, at startup. Edit a file and the running server keeps serving the old version until you tell it otherwise, which means load-time errors surface at a moment you might not expect. The fastest way to understand that is to cause one.

Create a file that defines a second asset using a key that `trips.py` already claimed. Run this in the [Terminal](tab-Terminal):

```run
cat > src/dagster_essentials/defs/assets/duplicate_trips.py <<'EOF'
import dagster as dg


@dg.asset
def taxi_trips() -> None:
    """A second asset claiming a key that trips.py already owns."""
EOF
```

The file is valid Python. Every import resolves, and nothing about it is wrong until Dagster tries to build one `Definitions` object out of every module under `defs` and finds the same asset key twice. Ask for validation and watch it fail:

```run
dg check defs
```

The command exits 1 and the traceback ends with the reason:

```text
dagster._core.errors.DagsterInvalidDefinitionError: Duplicate asset key: AssetKey(['taxi_trips'])
```

Now see what the same failure looks like from the UI. Go back to **Deployment > Code locations** and click **Reload** next to `dagster_essentials`. Reloading tells Dagster to throw away what it has in memory and read the last saved version of your files from disk.

The status flips from **Loaded** to **Failed**, in red. Click **View Error** and you get the same stack trace you just saw in the terminal, without leaving the browser. Note what did not happen: your existing assets are still in the graph, running off the last version that loaded successfully. A failed reload does not take your pipeline down. It refuses to replace working definitions with broken ones.

Fix it and reload
===

Now put it back. Delete the file that claimed the duplicate key:

```run
rm src/dagster_essentials/defs/assets/duplicate_trips.py
```

Confirm the fix at the command line before you touch the UI. This is the habit worth building: validate in the terminal where feedback takes two seconds, and use the UI to see the result:

```run
dg check defs
```

With a clean check, return to **Deployment > Code locations** and click **Reload** one more time. The status returns to **Loaded** and the timestamp updates to right now.

That reload button is not just for recovering from errors. Any time you add an asset, rename one, or change a dependency, the running server needs to be told to pick up the change. You will use it constantly for the rest of this course.

What you've accomplished
===

You now know how your code gets from a file on disk into the Dagster UI, and where to look when it does not.

Before you move on, confirm all of the following:

- `dg check defs` in the [Terminal](tab-Terminal) exits cleanly with a success message
- `dg list defs` shows seven assets: `taxi_trips_file`, `taxi_zones_file`, `taxi_trips`, `taxi_zones`, `manhattan_stats`, `manhattan_map`, and `trips_by_week`
- `src/dagster_essentials/defs/assets/duplicate_trips.py` no longer exists
- In the [Dagster UI](tab-Dagster-UI), **Deployment > Code locations** shows `dagster_essentials` with a status of **Loaded**

The pieces fit together like this. Your assets live in modules under `defs`. `load_from_defs_folder` collects them into one `Definitions` object. That object plus the Python environment around it is a code location, which is the unit Dagster loads, names, monitors, and reloads. Scale that up and code locations are how a hundred engineers ship to one deployment without stepping on each other, each with their own dependencies, each visible in the same UI.

Next, you'll put that isolation to work and start adding definitions beyond assets.
