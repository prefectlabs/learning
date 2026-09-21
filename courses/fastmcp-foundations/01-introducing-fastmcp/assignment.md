---
slug: introducing-fastmcp
id: dxytadeeckcv
type: challenge
title: Build Your First MCP Server
teaser: Write a one-tool MCP server in a dozen lines of Python and call it from the command line.
notes:
- type: text
  contents: |-
    # One plug for every assistant

    Every AI assistant has its own way of reaching outside systems, and until recently every team wrote its own glue code for each one. A tool that worked in one chat product had to be rebuilt for the next. The Model Context Protocol (MCP) replaces that with a shared standard.

    You build one **server** that offers capabilities, and any MCP **client** (Claude, ChatGPT, Cursor, or a chatbot your own organization built) can use it. Think of the wall outlet: the utility company doesn't care what you plug in, and the assistant doesn't care what sits behind your server. Your data, your API, your expertise, offered once and usable everywhere.
- type: text
  contents: |-
    # Three things a server can offer

    An MCP server hands an assistant three kinds of things.

    **Tools** are functions the assistant can call. Verbs. *Look up a forecast. Search the catalog. File the request.*

    **Resources** are content the assistant can read. Nouns. *The data dictionary. The policy. A note on where the numbers come from.*

    **Prompts** are saved instructions with blanks to fill in. Recipes. *Brief me on this dataset. Should this event keep its date?*

    Most servers start with tools, and that's where you'll start. You'll add the other two in a later challenge.
- type: text
  contents: |-
    # What FastMCP does for you

    The protocol itself involves message formats, capability negotiation, and schemas. You won't touch any of it. FastMCP is the Python framework that handles the protocol so you can write ordinary functions.

    You write a function. You put one decorator above it. The function's name, docstring, and type hints become the contract the assistant sees. That's the whole idea, and this challenge proves it in about a dozen lines.

    The sandbox already has FastMCP 4 installed inside a project folder called `fastmcp-101`. The terminal opens there with the environment activated.
tabs:
- id: 5gtdhcnitbwa
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- id: tcd69prhmzrq
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root/fastmcp-101
difficulty: basic
timelimit: 1200
enhanced_loading: null
---

# Build Your First MCP Server

You're going to write the smallest useful MCP server: one tool that says hello. It won't do anything impressive, and that's the point. Once you've seen how little code stands between a Python function and something an AI assistant can call, the rest of this track is just adding more functions.

You'll write the file in the **Code Editor** tab and run commands in the **Terminal** tab. The terminal starts inside `/root/fastmcp-101` with the project's Python environment already active, so `fastmcp` is ready to use.

<!-- Bootstrap bundle used by track_scripts/setup-fastmcp-sandbox: ![](../assets/fastmcp-101.tar.gz) -->

## Step 1: Confirm the tools are ready

Before writing anything, check that FastMCP is installed and which version you have. This track uses FastMCP 4, the current major version, and a few things you'll see later (like the CLI commands) are specific to it.

```run
fastmcp version
```

The first line should read `FastMCP version: 4.` followed by a patch number.

## Step 2: Write the server

In the **Code Editor** tab, create a new file at the top of the `fastmcp-101` folder called `hello.py` and paste this in:

```python
from fastmcp import FastMCP

mcp = FastMCP("Hello Server")


@mcp.tool
def greet(name: str) -> str:
    """Say hello to someone by name."""
    return f"Hello, {name}! Welcome to MCP."


if __name__ == "__main__":
    mcp.run()
```

Four things to notice. `FastMCP("Hello Server")` creates the server object. `@mcp.tool` registers the function beneath it as a tool. The docstring becomes the tool's description, which is what the assistant reads to decide *when* to use it. The type hint `name: str` tells the assistant what input to send. The `mcp.run()` at the bottom is what a desktop client would call to start the server; you won't need it for the CLI commands below.

Save the file.

## Step 3: List what the server offers

Ask FastMCP to start your server, request its tool list, and shut it down again. This is exactly the first thing any client does when it connects.

```run
fastmcp list hello.py
```

You should see one tool, `greet(name: str)`, with your docstring under it.

## Step 4: Call the tool

Now call the tool the way an assistant would, except no assistant is involved. You're the client.

```run
fastmcp call hello.py greet name=Ada
```

## Step 5: See what the assistant sees

Finally, look at the contract your docstring and type hints produced. This JSON is what gets sent to the assistant. You didn't write any of it; FastMCP built it from your function.

```run
fastmcp list hello.py --json
```

Find the `description` field and the `inputSchema`. The description is your docstring, word for word. The schema says `name` is a required string. Change either one in your code and the contract changes with it.

## Verify

`fastmcp list hello.py` shows exactly one tool named `greet`. `fastmcp call` prints `"Hello, Ada! Welcome to MCP."` inside a small JSON result. Click **Check** when you see both.

If the list comes back empty, make sure `@mcp.tool` sits on the line directly above `def greet`, with no blank line between them, and that you saved the file.
