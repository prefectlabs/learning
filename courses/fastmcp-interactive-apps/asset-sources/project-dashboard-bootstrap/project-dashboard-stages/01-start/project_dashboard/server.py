from __future__ import annotations

from fastmcp import FastMCP
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, Text


mcp = FastMCP("Project Dashboard")


@mcp.tool(app=True)
def hello_app() -> PrefabApp:
    with Column(gap=2, cssClass="p-6") as view:
        Heading("Hello, MCP apps")
        Text("Change this line.")
    return PrefabApp(title="Hello MCP Apps", view=view)


if __name__ == "__main__":
    mcp.run()
