---
slug: add-resources-and-prompts
type: challenge
title: Add Resources and Prompts
teaser: Give the assistant something to read and a saved recipe to run, using the other two MCP primitives.
notes:
- type: text
  contents: |-
    # What tools don't cover

    Tools *do* things. But an assistant often needs two other kinds of help from your server.

    Sometimes it needs background before it acts: where the data comes from, what the numbers mean, what the server does *not* cover. That's a **resource**, content the assistant can read on request. Resources have addresses called URIs, like `weather://about`, the same idea as a web address but for your server.

    And sometimes users keep asking the same shape of question. *Should we keep this outdoor event on this date?* A **prompt** captures that phrasing once, with blanks for the details, so the assistant asks your tools the right way every time and users can pick it from a menu instead of typing the whole thing.
- type: text
  contents: |-
    # Which one do I write?

    A rule of thumb that holds up well:

    - If the assistant needs to **act or compute**, write a tool.
    - If it needs **background it should read**, write a resource.
    - If people keep asking the **same shaped question**, write a prompt.

    All three use the same pattern you already know: a Python function with a decorator above it. The decorator changes; your habits don't.
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

# Add Resources and Prompts

Your weather server has three tools. In this challenge you'll round it out with one resource and one prompt, so an assistant connected to it can read where the data comes from and a user can pick "plan an outdoor event" from a menu. Both take about ten lines, and both use decorators that work like the one you already know.

## Step 1: Add the resource and the prompt

In the **Code Editor**, open `weather_server/server.py` and find the line near the bottom that reads `# TODO (Lesson 3): add a resource and a prompt below this line`. Replace it with this block:

```python
@mcp.resource("weather://about")
def about() -> str:
    """Explain what this server does and where its data comes from."""
    return (
        "Weather Server answers forecast, history, and rain-probability questions. "
        "Data comes from Open-Meteo (open-meteo.com), a free and open weather API. "
        "Forecasts reach 16 days ahead; history covers roughly 80 years."
    )


@mcp.prompt
def plan_outdoor_event(location: str, date: str) -> str:
    """Ask the assistant to decide whether an outdoor event should keep its date."""
    return (
        f"I'm planning an outdoor event in {location} on {date}. "
        "Check the chance of rain and the forecast, then tell me plainly whether "
        "to keep the date or pick a backup, and why."
    )
```

The resource decorator takes the URI as its argument; that address is how a client asks for it. The prompt decorator works exactly like the tool decorator: the function's parameters become the blanks a user fills in. Save the file.

## Step 2: List everything

The `list` command only shows tools by default. Ask for the other two kinds as well.

```run
fastmcp list weather_server/server.py --resources --prompts
```

## Step 3: Read the resource

Anything with `://` in it is treated as a resource URI, so the same `call` command reads it.

```run
fastmcp call weather_server/server.py weather://about
```

## Step 4: Render the prompt

Fill in the two blanks and see the message an assistant would receive. The `--prompt` flag tells FastMCP the name refers to a prompt rather than a tool.

```run
fastmcp call weather_server/server.py plan_outdoor_event --prompt location=Chicago date=2026-10-01
```

## Verify

The list shows three tools, one resource at `weather://about`, and one prompt called `plan_outdoor_event(location, date)`. Reading the resource prints the Open-Meteo sentences. The rendered prompt has Chicago and the date filled in. Click **Check**.

If the resource or prompt doesn't appear, confirm the new block sits *above* the `if __name__ == "__main__":` line and that the file is saved.
