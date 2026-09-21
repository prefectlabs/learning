---
slug: deploy-to-prefect-horizon
type: challenge
title: Deploy to Prefect Horizon
teaser: Run your server over HTTP, push it to GitHub, deploy it to a public URL, and chat with it.
notes:
- type: text
  contents: |-
    # From your laptop to an address

    So far your server only exists where you run it. When the CLI or a desktop assistant launches it, the two talk over **stdio**: the client starts your program and they exchange messages through standard input and output, like a conversation in the same room. That's fine for one person on one machine.

    To share the server with a team, or connect it from a hosted assistant, it needs an address. Over **HTTP** the server runs as a web service and clients connect to a URL. Same code, different transport. You'll prove that locally first, then let Horizon host it.
- type: text
  contents: |-
    # What Horizon does

    Prefect Horizon deploys FastMCP servers straight from a GitHub repository. You point it at the repo, tell it which file holds the server object, and it installs your dependencies, starts the server, and gives you a URL ending in `/mcp`. Every push to `main` redeploys automatically.

    It also gives you two ways to try the server without configuring any client. **ChatMCP** is an assistant already connected to your server, so you can ask weather questions in plain English and watch which tool it picks. **Playground** lists the tools and lets you call them by hand with explicit arguments, with no assistant in the loop.
- type: text
  contents: |-
    # Before you start

    You need a GitHub account for this challenge. Horizon signs in with GitHub and reads your repository from there. If you don't have one, you can still do Step 1 to see the HTTP transport working, then skip the rest.

    You'll also use two terminals: one to keep the server running, one to talk to it. Both tabs open in the project folder with the environment active.
tabs:
- title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- title: "\U0001F4BB Terminal 2"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root/fastmcp-101
- title: Horizon
  type: browser
  hostname: horizon
difficulty: basic
timelimit: 2400
enhanced_loading: null
---

# Deploy to Prefect Horizon

Your server works, and it's tested. Now you'll put it somewhere other people and other assistants can reach it. First you'll run it as a web service inside the sandbox and connect to it by URL, so the idea of a transport is concrete. Then you'll push the project to your own GitHub account, deploy it on Horizon, and ask it about the weather in plain English.

## Step 1: Run the server over HTTP

In the **Terminal** tab, start the server as a web service. The `file.py:mcp` form names the exact server object, and `--transport http` swaps stdio for a network listener on port 8000.

```run
fastmcp run weather_server/server.py:mcp --transport http --port 8000
```

You'll see the FastMCP banner and then a line saying the server started. Leave it running.

## Step 2: Connect to it by URL

Switch to the **Terminal 2** tab. Instead of a file path, hand `fastmcp list` the address the server is listening on. FastMCP has always exposed HTTP servers at the `/mcp` path.

```run
fastmcp list http://127.0.0.1:8000/mcp
```

Same three tools, reached over the network instead of through a file. Any MCP client on this machine could connect to that address right now. Switch back to the first terminal and press `Ctrl+C` to stop the server.

## Step 3: Sign in to GitHub

The project folder is already a git repository with no commits and no remote, so it's yours to publish. Authenticate the GitHub CLI first. Choose **GitHub.com**, **HTTPS**, and **Login with a web browser**, then follow the one-time code it shows you.

```run
gh auth login
```

Tell git who you are, replacing the placeholder with your GitHub username:

```run
git config --global user.name "YOUR_GITHUB_USERNAME"
git config --global user.email "YOUR_GITHUB_USERNAME@users.noreply.github.com"
```

## Step 4: Commit and push

Make the first commit, then create a public repository under your account and push to it in one command.

```run
git add .
git commit -m "Complete FastMCP 101"
gh repo create fastmcp-101 --public --source=. --remote=origin --push
```

The output ends with the URL of your new repository. Horizon will read from it directly.

## Step 5: Deploy on Horizon

Open the **Horizon** tab and sign in with GitHub. Then:

1. Choose to deploy a new server and select your `fastmcp-101` repository. Grant access if GitHub asks.
2. Fill in the form:
   - **Server name**: something unique to you. This becomes your URL.
   - **Entrypoint**: `weather_server/server.py:mcp`
   - **Authentication**: leave it off for now so ChatMCP and other clients can connect without a login. You can turn it on later.
3. Click **Deploy Server**.

Horizon clones the repo, installs from `pyproject.toml`, and starts the server. It usually finishes in under a minute. When it does, your server is live at `https://<your-server-name>.fastmcp.app/mcp`.

## Step 6: Talk to it

Open your server in Horizon and choose **ChatMCP** from the left-hand menu. Ask it a few questions:

- *What's the forecast for Denver this week?*
- *What was the weather in Chicago on July 4th, 2023?*
- *Should I keep an outdoor event in Seattle next Saturday?*

Watch which tool it picks for each. That choice comes entirely from the docstrings you read in challenge 2. Then choose **Playground** from the same menu to see the raw tool list and call one with explicit arguments.

## Step 7: Connect a real client (optional)

Any MCP client can now use your server. For Claude Code on your own machine, it's one command:

```text
claude mcp add --transport http weather https://<your-server-name>.fastmcp.app/mcp
```

For Cursor or Claude Desktop, Horizon shows a copy-paste connection snippet on your server's page.

## Verify

`fastmcp list` against `http://127.0.0.1:8000/mcp` showed your three tools. `git remote -v` in the terminal shows an `origin` pointing at your own GitHub repository. Horizon shows the deployment as running, and ChatMCP answers a weather question using one of your tools. Click **Check**.

If you skipped GitHub, you can still click **Skip** to finish the track.
