---
slug: flows-tasks-prefect
id: ott2i8g0iye3
type: challenge
title: Flows & Tasks
teaser: Getting Started with Prefect
notes:
- type: text
  contents: |
    # What is Prefect?
    Prefect is an open‑source workflow orchestration tool built primarily for data pipelines, although its flexibility means it can orchestrate any kind of Python-based workflow.

    It allows users to define, schedule, monitor, and manage tasks and flows—complete with retry logic, state tracking, parallel execution, and observability—all without complex infrastructure.

    Rather than building static DAGs, Prefect embraces a Pythonic style: you write normal Python functions and decorate them as @task and @flow, and Prefect handles the rest—dependency resolution, execution, and logging.

    Prefect is often described as the modern answer to heavyweight orchestration systems because of its simplicity and flexibility.

    It offers an API-first approach, a sleek UI/CLI for real-time monitoring, and strong scalability—from small local tasks to enterprise-scale data workflows.
- type: text
  contents: |
    # Why was Prefect created?
    Prefect was born in 2018 from the realization that existing orchestration tools were either too rigid (Airflow‑style DAGs) or not Python-native.

    Its founders—one of whom was a PMC member of Apache Airflow—wanted orchestration to feel natural, intuitive, and Pythonic. In particular, they introduced task mapping early on—a parallel execution pattern that allows dynamic arrays of tasks at runtime—a feature later copied by others.

    Prefect also emerged to address the problems of “negative data engineering”—the idea that even if your code is correct, it might fail due to timing, infrastructure, or external dependencies.

    Prefect helps ensure resilience, reliability, retry logic, visibility, and run recovery, so pipelines actually run robustly in production.

    As one commentary puts it, the tool was designed around the premise: “*Your code probably works. But sometimes it doesn’t.*”
tabs:
- id: y8a9ysqqxqk7
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: thxswa20nmqx
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: prefect-sandbox
  path: /root
- id: v1eqvifcx6qj
  title: Prefect Cloud
  type: browser
  hostname: prefect-io
difficulty: ""
timelimit: 600
enhanced_loading: null
---
Getting started with Prefect
===

Let's install Prefect locally and build a simple flow. We'll use `uv` for package management.

**Install UV package manager:**

```run
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

**Set up your project:**

```run
uv venv && source .venv/bin/activate
uv pip install -U prefect
```

Writing Your First Flow
===

Let's start with some pretty simple Python code. First, we'll create a new Python file for our flow.

**Create your first flow file:**

```run
touch hello_world.py
```

Now let's add some basic Python code to this file. We'll base this on our Hello World example: https://github.com/PrefectHQ/examples/blob/main/flows/hello_world.py

**Add this code to `hello_world.py`:**

```python
def hello(name: str = "Marvin"):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    hello()
```


Try running the code yourself:

```run
uv run hello_world.py
```

When you run this code, you'll see the output: "Hello, Marvin!". (Yes, Marvin The Paranoid Android from The Hitchiker's Guide to the Galaxy - Prefect's beloved mascot! 🤖)

This is just regular Python - nothing fancy yet. Let's change that.

Transform into a Prefect Flow
===

Now let's transform this basic Python script into a Prefect flow. Add the `@flow` decorator to tell Prefect to track, observe, and orchestrate your code.

**Before (regular Python):**
```python
def hello(name: str = "Marvin"):
    print(f"Hello, {name}!")
```

**After (Prefect flow):**
```python
from prefect import flow, get_run_logger, tags

@flow
def hello(name: str = "Marvin"):
    get_run_logger().info(f"Hello, {name}!")

if __name__ == "__main__":
    # Run the flow
    hello()  # Output: "Hello, Marvin!"

    # Run the flow with a different argument
    hello("Arthur")  # Output: "Hello, Arthur!"

    # Run the flow with a "local" tag for organization
    with tags("local"):
        hello()
```

**What just happened?**
- `@flow` transforms your function into an observable, trackable workflow
- `get_run_logger()` provides structured logging that appears in Prefect Cloud
- Each time you run this function, Prefect creates a "flow run" with full metadata

**Replace the contents of `hello_world.py` with the Prefect version above, then run it:**

```run
uv run hello_world.py
```

**What just happened?**

You'll now see much richer output! Notice a few key things:

1. **Temporary Server Started**: Prefect automatically started a local server at `http://127.0.0.1:8006`
2. **Flow Run Names**: Each execution gets a unique name like "infrared-rottweiler" or "screeching-panther"
3. **Structured Logging**: Your `get_run_logger().info()` messages appear with flow run context
4. **State Tracking**: Each flow run shows "Beginning" → your logs → "Finished in state Completed()"
5. **Server Stopped**: The temporary server shuts down when done

This local server gives you essential observability running on your machine! You can even visit `http://127.0.0.1:8006` in a browser during execution to see a local UI.

**Important Note:** This local server is **Prefect Open Source (OSS)** - our free, open-source orchestration platform that individuals and teams use to get started with Prefect. It's different from **Prefect Cloud**, which is our fully-managed enterprise SaaS platform with additional features like user management, authentication, automations, event-driven workflows, and enterprise integrations.

Prefect gives you workflow orchestration whether running locally or in the cloud.

What You've Accomplished
===

In just a few minutes, you've transformed a basic Python script into an observable, trackable workflow. Here's what you now have:

✅ **Local development** with immediate feedback
✅ **Cloud observability** with automatic tracking
✅ **Structured logging** that scales
✅ **Metadata capture** for every execution

This is the foundation that everything else builds on. From here, you can explore:

**Next Steps:**
- **Tasks**: Break flows into atomic, retryable units
- **Work pools**: Execute flows on remote infrastructure
- **Automations**: Event-driven workflows and notifications
- **Deployments**: Production-ready scheduling and CI/CD

You started with pure Python and added orchestration without changing your core logic. This pattern scales from simple scripts to production data pipelines.

## Level Up: Connect to Prefect Cloud

Connect your local environment to Prefect Cloud for centralized observability and team collaboration.

**Get your API key from Prefect Cloud:**

1. [Click here to open Prefect Cloud](tab-Prefect-Cloud)
2. Create a free account if you don't have one
3. In the top-left corner, click on your **workspace name**
4. Select **"API Keys"** from the dropdown menu
5. Click **"Create API Key"**
6. Name it "Instruqt Learning" and click **"Create"**
7. **Copy the API key** that appears

**Authenticate with Prefect Cloud:**

Run this command, replacing `YOUR_API_KEY` with the key you just copied:

```run
uvx prefect-cloud login --key YOUR_API_KEY
```

This connects your local environment to Prefect Cloud so you can deploy and monitor your pipeline.

**Note**: On your local machine, you can authenticate through your browser instead of using an API key. We're using the API key method here to work around limitations of the sandbox environment.

Now re-run your flow to see it tracked in Prefect Cloud:

```run
uv run hello_world.py
```

**View in Prefect Cloud:** [Click here to see your flow runs](tab-Prefect-Cloud)

Navigate to "Flow runs" in the left sidebar and click on your latest run. You'll see:
- **Timeline**: When your flow started and finished
- **Logs**: All structured logging in one place
- **Metadata**: Duration, state, parameters used
- **Tags**: Notice the "local" tag on one of the runs

This is the foundation of observability that scales to complex workflows.
