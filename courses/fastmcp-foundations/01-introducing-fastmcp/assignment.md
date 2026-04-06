---
slug: introducing-fastmcp
id: dxytadeeckcv
type: challenge
title: Introducing FastMCP
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
  path: /root
- id: oz9yjcrkbbvp
  title: FastMCP Cloud
  type: browser
  hostname: fastmcp-cloud
difficulty: ""
enhanced_loading: null
---
Introduction to MCP
===

The Model Context Protocol (MCP) is often described as "the USB-C port for AI": a standardized way to connect Large Language Models (LLMs) to external tools and data sources.

**What is MCP?**

MCP provides a uniform interface that lets LLMs interact with:
- **Resources**: Data sources that can be loaded into the LLM's context (like GET endpoints)
- **Tools**: Functions that execute code or produce side effects (like POST endpoints)
- **Prompts**: Reusable templates for LLM interactions

Think of MCP as an API specifically designed for LLM interactions. Instead of building custom integrations for each LLM client, MCP servers work with any MCP-compatible client (Cursor, Claude Code, ChatGPT, or custom applications).

**Why MCP Matters**

Before MCP, connecting LLMs to your data and tools required custom integrations for each platform. MCP standardizes this process, making it possible to:
- Build once, use everywhere
- Connect LLMs to your existing APIs and databases
- Create reusable tools that work across different AI platforms
- Maintain security and access control in one place

Why FastMCP Exists
===

While the official MCP Python SDK provides core protocol functionality, **FastMCP 2.0** extends far beyond basic implementation to deliver everything needed for production.

**FastMCP 2.0 Features:**

🚀 **Fast**: High-level interface means less code and faster development

🍀 **Simple**: Build MCP servers with minimal boilerplate. Just decorate Python functions.

🐍 **Pythonic**: Feels natural to Python developers

🔍 **Complete**: Enterprise auth (Google, GitHub, Azure, Auth0, WorkOS), deployment tools, testing frameworks, and client libraries

**The FastMCP Advantage**

FastMCP handles all the complex protocol details so you can focus on building. In most cases, decorating a Python function is all you need:

```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
def hello(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"
```

That's it. FastMCP handles the rest: protocol communication, error handling, type validation, and more.

Environment Setup
===

Set up your development environment. We're using `uv` for package management.

**Install UV package manager:**

```run
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

**Create your project environment:**

```run
uv venv .venv --python 3.12
source .venv/bin/activate
```

**No API Key Required**

We're using Open-Meteo API for weather data. It's free and doesn't need any registration or API keys.

Building Your First MCP Server
===

We're building a weather MCP server with three tools:

1. **get_weather_forecast**: Forecast up to 16 days ahead
2. **get_historical_weather**: Historical weather for any past date
3. **calculate_rain_probability**: Combines historical patterns with forecasts to predict rain

These tools let LLMs answer questions like:
- "What's the weather forecast for San Francisco?"
- "What was the weather like in NYC on July 4th, 2023?"
- "What's the chance of rain in London next Tuesday?"

**Get the starter code:**

```run
git clone -b dev https://github.com/PrefectHQ/prefect-accelerated-learning.git temp-repo
mkdir mcp-demo
cp -r temp-repo/instruqt-courses/fastmcp/1-introducing-fastmcp/starter-code/* mcp-demo/
rm -rf temp-repo
cd mcp-demo
ls -la
```

You'll see `pyproject.toml` and a `weather_server/` directory containing the server code.

**Install dependencies:**

```run
uv pip install -e . --active
```

This installs FastMCP and requests from the `pyproject.toml` file. Here's how the server works:

```python
from fastmcp import FastMCP

mcp = FastMCP("Weather Probability Server 🌤️")

def get_weather_forecast(location: str, days_ahead: int = 7) -> str:
    """Get weather forecast for a location up to 16 days ahead."""
    # ... geocode location, call Open-Meteo API, format results

def get_historical_weather(location: str, date: str) -> str:
    """Get historical weather for a specific date."""
    # ... validate date, call archive API, return weather data

def calculate_rain_probability(location: str, date: str) -> str:
    """Calculate probability of rain for a future date.

    Combines historical patterns from past 5 years with forecast data
    to provide an intelligent probability assessment.
    """
    # ... fetch historical data, get forecast, calculate weighted probability

if __name__ == "__main__":
    mcp.run()
```

The full implementation is in `weather_server/server.py`. The key pieces:

- **Helper functions** handle geocoding and weather code translations
- **Three functions** need the `@mcp.tool` decorator to become MCP tools
- **Each tool returns a string** with formatted weather information
- **FastMCP handles** all the protocol complexity

**Add the @mcp.tool decorator:**

Right now the three functions (`get_weather_forecast`, `get_historical_weather`, and `calculate_rain_probability`) are just regular Python functions. To make them MCP tools, add the `@mcp.tool` decorator above each function definition:

```python
@mcp.tool
def get_weather_forecast(location: str, days_ahead: int = 7) -> str:
    """Get weather forecast for a location up to 16 days ahead."""
    # ...
```

Add `@mcp.tool` above all three functions in `weather_server/server.py`. This decorator tells FastMCP to expose these functions as tools that LLMs can call.

**Test the server:**

```run
uv run weather_server/server.py
```

The server starts and waits for MCP connections. Press Ctrl+C to stop it.

**How the Tools Work**

Each tool is just a Python function with the `@mcp.tool` decorator:

```python
@mcp.tool
def get_weather_forecast(location: str, days_ahead: int = 7) -> str:
    """Get weather forecast for a location up to 16 days ahead.

    Args:
        location: City name (e.g., "San Francisco" or "London, UK")
        days_ahead: Number of days to forecast (1-16, default: 7)
    """
```

The docstring becomes the tool description that LLMs see. Type hints tell FastMCP what parameters to expect. That's it.

When an LLM calls the tool, your function runs and returns a string. FastMCP handles all the protocol stuff.

GitHub Setup and Deployment
===

Get your code on GitHub so FastMCP Cloud can deploy it.

**Install GitHub CLI if needed:**

```run
sudo apt update && sudo apt install gh -y || brew install gh || echo "GitHub CLI already installed"
gh --version
```

**Configure git (replace YOUR_GITHUB_USERNAME with your actual username):**

```run
git config --global user.email "YOUR_GITHUB_USERNAME@users.noreply.github.com"
git config --global user.name "YOUR_GITHUB_USERNAME"
```

**Initialize git and commit:**

```run
git init
git add weather_server/ pyproject.toml
git status
git commit -m "Initial commit: FastMCP weather server"
```

**Authenticate with GitHub:**

```run
gh auth login
```

Follow the prompts to authenticate. You can use a web browser or token authentication.

**Create repository and push:**

```run
git branch -M main
gh repo create mcp-demo --public --source=. --remote=origin --push
```

**Verify your code is on GitHub:**

```run
git remote -v
git log --oneline
```

Your project is now at `https://github.com/YOUR_USERNAME/mcp-demo`. FastMCP Cloud will deploy directly from this repository.

Deploy to FastMCP Cloud
===

FastMCP Cloud is the fastest way to deploy your MCP server. It's completely free while in beta!

**Step 1: Visit FastMCP Cloud**

Open [fastmcp.cloud](tab-FastMCP-Cloud) in a new tab and sign in with your GitHub account.

**Step 2: Create a New Project**

1. Click **"Create Project"** or **"New Project"**
2. Select your repository: `YOUR_USERNAME/mcp-demo`
3. Click **"Create Project"**

**Step 3: Configure Your Project**

Configure your project settings:

- **Name**: `mcp-demo`
- **Entrypoint**: `weather_server.server:mcp`
  - Format is `module.path:object_name`
- **Authentication**: Disabled (public server)
- **Environment Variables**: None needed (Open-Meteo is free)

**Step 4: Deploy**

Click **"Deploy"** or **"Save"**. FastMCP Cloud will:
1. Clone your repository
2. Install dependencies from `pyproject.toml`
3. Build your FastMCP server
4. Deploy it to a unique URL

**Step 5: Get Your Server URL**

Once deployment succeeds, you'll see your server URL:
```
https://your-project-name.fastmcp.app/mcp
```

Copy this URL. You'll need it to connect clients.

**Automatic Redeployments**

FastMCP Cloud watches your repo and redeploys when you push to `main`. It also deploys preview servers for every PR.

Interact with Your Server
===

Connect to your deployed server and test it.

**Using ChatMCP**

1. Visit [chatmcp.com](tab-ChatMCP)
2. Click **"Connect to Server"**
3. Enter your server URL: `https://your-project-name.fastmcp.app/mcp`
4. Click **"Connect"**

**Try these queries:**

- "What's the weather forecast for San Francisco?"
- "What was the weather in New York on July 4th, 2023?"
- "What's the chance of rain in Seattle next Tuesday?"
- "Will it rain in London on December 25th this year?"

**How It Works**

The LLM sees your three tools and their docstrings. When you ask a weather question, it picks the right tool and calls it with appropriate arguments.

For example, "What's the chance of rain in Seattle next Tuesday?" triggers:
1. LLM figures out next Tuesday's date
2. Calls `calculate_rain_probability("Seattle", "2025-11-18")`
3. Your tool fetches historical data (past 5 years) and forecast data
4. Calculates weighted probability and returns formatted results
5. LLM presents the answer naturally

No prompt engineering, no function calling boilerplate. MCP handles it.

**Testing with Python Client**

You can also test programmatically:

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("https://your-project-name.fastmcp.app/mcp") as client:
        # List available tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # Call a tool
        result = await client.call_tool(
            name="calculate_rain_probability",
            arguments={"location": "San Francisco", "date": "2025-12-25"}
        )
        print(result.content)

asyncio.run(main())
```

Connect to Other Clients
===

Your MCP server works with any MCP-compatible client.

**Cursor IDE**

1. Open Cursor Settings → Features → Model Context Protocol
2. Click "Add Server"
3. Enter: `https://your-project-name.fastmcp.app/mcp`
4. Restart Cursor

Now Cursor can use your weather tools in the editor.

**Claude Code**

1. Open settings → MCP Servers
2. Add your server URL
3. Done

**ChatGPT with MCP**

1. Settings → Integrations → MCP Servers
2. Add your URL

**Security for Production**

Enable authentication in FastMCP Cloud settings:
- Only your organization members can connect
- Use environment variables for API keys
- Consider rate limiting

What You Built
===

You just built and deployed a production MCP server.

**What you did:**

- Created three weather tools using FastMCP
- Deployed to FastMCP Cloud with zero infrastructure
- Connected multiple clients

**Key points:**

- MCP standardizes LLM-tool connections
- FastMCP makes it Pythonic
- FastMCP Cloud handles deployment
- One server, many clients

**Next steps:**

- Add more tools
- Enable authentication
- Connect to your own APIs
- Build more servers

**Resources:**

- [FastMCP Docs](https://gofastmcp.com/)
- [Deployment Guide](https://gofastmcp.com/deployment/fastmcp-cloud)
- [MCP Spec](https://modelcontextprotocol.io/)
- [GitHub](https://github.com/jlowin/fastmcp)

That's it. You've got a working MCP server that connects LLMs to weather data. Now go build something useful.