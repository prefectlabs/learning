---
slug: turn-functions-into-tools
type: challenge
title: Turn Functions into Tools
teaser: Decorate three working weather functions and read the contract the assistant receives.
notes:
- type: text
  contents: |-
    # A tool is a function plus a contract

    The assistant never sees your code. It sees a contract: the tool's name, a description, and a schema for the inputs. FastMCP builds that contract from three things you already write in normal Python.

    The **docstring** is the job description. The assistant reads it to decide whether this tool fits the question in front of it. The **type hints** are the form it fills out to call you. The **default values** decide which fields on that form are optional.

    That's why a clear one-sentence docstring matters more than clever code. If the description is vague, the assistant will reach for the wrong tool or skip yours entirely.
- type: text
  contents: |-
    # The weather server

    Your project folder already contains `weather_server/server.py` with three working functions. They call Open-Meteo, a free weather API that needs no account or key, and return readable text.

    - `get_weather_forecast(location, days_ahead)` looks up to 16 days ahead
    - `get_historical_weather(location, date)` reports any past date
    - `calculate_rain_probability(location, date)` blends five years of history with the forecast

    Right now they are plain Python. Nothing about them is visible to an assistant. You'll change that by adding one line above each. The helper functions whose names start with an underscore are shared plumbing, and they should stay private.
- type: text
  contents: |-
    # Outcomes, not operations

    Open-Meteo has separate endpoints for geocoding, forecasts, and history. We could have exposed each one as a tool and let the assistant chain them together. We didn't. `calculate_rain_probability` makes six API calls and returns one answer, because "will it rain on my event date" is the question people actually ask.

    Design tools top-down from the outcome the user wants, not bottom-up from the endpoints you happen to have. An assistant pays for every extra call in time and context, and every extra step is a place to go wrong. Three tools that each answer a whole question beat a dozen that each return a fragment.
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
timelimit: 1800
enhanced_loading: null
---

# Turn Functions into Tools

In the last challenge you wrote a tool from scratch. This time the functions are already written and tested, which is the situation you'll usually be in: an organization has code that knows how to answer a question, and the job is to make that knowledge reachable by an assistant. You'll do that by adding `@mcp.tool` above three functions, then read the contract FastMCP builds from them.

Open `weather_server/server.py` in the **Code Editor** tab and skim it before you start. Notice the module docstring at the top, the `mcp = FastMCP("Weather Server")` line, the two private helpers, and the three `TODO` comments.

## Step 1: Confirm the server offers nothing yet

The server object exists, but no functions are registered against it. Listing it proves that.

```run
fastmcp list weather_server/server.py
```

You should see `No tools found.`

## Step 2: Add the decorator

In the editor, find the three lines that read `# TODO (Lesson 2): add @mcp.tool above this function`. Replace each one with `@mcp.tool`, so it sits directly above the `def` line. Leave the underscore helpers alone; you don't want the assistant calling your geocoder directly. Save the file.

The first one should end up looking like this:

```python
@mcp.tool
def get_weather_forecast(location: str, days_ahead: int = 7) -> str:
    """Get the daily weather forecast for a location, up to 16 days ahead.
```

## Step 3: List again

The same command now shows all three tools, each with its docstring.

```run
fastmcp list weather_server/server.py
```

## Step 4: Call the forecast tool

This makes a real request to Open-Meteo and prints three dated lines for Denver.

```run
fastmcp call weather_server/server.py get_weather_forecast location=Denver days_ahead=3
```

## Step 5: Ask for a rain outlook

This is the tool that does real work: five history lookups plus a forecast, blended into one answer. The `$(date -d '+3 days' +%F)` part just asks the shell for a date three days from today in `YYYY-MM-DD` form, so the command works whenever you run it.

```run
fastmcp call weather_server/server.py calculate_rain_probability location=Seattle date=$(date -d '+3 days' +%F)
```

Read the result. It gives you the history, the forecast, and a percentage. An assistant would hand this text to the user in its own words. Notice what it didn't have to do: chain a geocoding call, five archive calls, and a forecast call itself. One tool, one outcome.

## Step 6: Read the contract

Look at the schema for one tool and compare it with the function signature.

```run
fastmcp list weather_server/server.py --json
```

Find `get_weather_forecast`. Its `required` list contains only `location`. `days_ahead` is missing from `required` because it has a default of 7. The assistant can leave it out and your function still works. That's the type system doing your input validation for you, with no extra code.

## Verify

`fastmcp list weather_server/server.py` shows exactly three tools: `get_weather_forecast`, `get_historical_weather`, and `calculate_rain_probability`. The forecast call returns three dated lines. Click **Check** when both are true.

If a call says it could not find a location, try a simpler place name. The geocoder likes `Washington` better than `Washington, DC`.
