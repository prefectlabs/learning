---
slug: test-your-server-with-code
type: challenge
title: Test Your Server with Code
teaser: Use FastMCP's in-memory client to test the server the way an assistant would, in under a second.
notes:
- type: text
  contents: |-
    # From poking at it to proving it

    So far you've tested with the CLI, which is fine for a quick look but not repeatable. Real projects need tests that run the same way every time, on every change, without anyone typing commands.

    FastMCP ships a `Client` that connects to a server three ways: by URL, by launching a file, or **in memory**, straight to the server object in the same Python process. In-memory means no port, no subprocess, and tests that finish in well under a second. Best of all, the same `Client` class connects to your deployed URL later, so code you write against it now keeps working after deployment.
- type: text
  contents: |-
    # What the tests check

    Your project already has `tests/test_server.py`. Every test follows the same shape: open a client on `mcp`, do one thing, assert one fact. There are tests for the tool list, for the descriptions, for input validation, for the resource, and for the prompt.

    The two validation tests are worth a look. They call tools with bad input, an out-of-range `days_ahead` and a malformed date, and confirm the server answers with a readable error instead of crashing. Those run offline because your functions validate before they ever call the weather API. One test does reach the live API, and it's marked `integration` so it's skipped unless you ask for it.
tabs:
- title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root/fastmcp-101
difficulty: basic
timelimit: 1200
enhanced_loading: null
---

# Test Your Server with Code

You've built a server with all three MCP primitives. Now you'll prove it works the way a developer would: with a test suite, and with a few lines of client code you write yourself. This is also your first look at the `Client` class, the other half of FastMCP. Everything you build here transfers directly to talking to a deployed server in the next challenge.

Open `tests/test_server.py` in the **Code Editor** and read it before running anything. Each test is short enough to understand in one pass.

## Step 1: Run the offline tests

Pytest is already installed in the project. The `integration` test is excluded by default, so this runs entirely in memory.

```run
pytest
```

You should see six tests pass and one deselected. If any fail, the failure message names the function or piece that's missing, and the earlier challenges have the fix.

## Step 2: Run the live test too

Now include the test that calls Open-Meteo for real. It's slower, since it goes over the network, but it proves the full path.

```run
pytest -m integration
```

## Step 3: Write your own client

Tests are one kind of client. Write the smallest possible one by hand so the pattern sticks. In the **Code Editor**, create `check_client.py` at the top of the project folder:

```python
import asyncio

from fastmcp import Client

from weather_server.server import mcp


async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("Tools:", [tool.name for tool in tools])

        result = await client.call_tool(
            "get_weather_forecast", {"location": "Denver", "days_ahead": 2}
        )
        print(result.data)


asyncio.run(main())
```

`Client(mcp)` connects in memory to the server object you imported. The `async with` block opens and closes the connection. `result.data` is the Python value your function returned; the raw protocol response is on `result.content` if you ever need it. Save the file and run it:

```run
python check_client.py
```

## Step 4: See what a deployment platform sees

Before Prefect Horizon deploys a server, it loads it and asks the same questions a client would. You can run that check yourself. The `file.py:mcp` form names the exact server object inside the file.

```run
fastmcp inspect weather_server/server.py:mcp
```

## Verify

`pytest` reports `6 passed, 1 deselected`. `pytest -m integration` reports `1 passed`. Your client script prints the three tool names and a two-day Denver forecast. `fastmcp inspect` shows 3 tools, 1 prompt, 1 resource, and a FastMCP version starting with 4. Click **Check**.
