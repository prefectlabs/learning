from __future__ import annotations

import ast
import asyncio
import importlib
import json
import os
import sys
from pathlib import Path

from fastmcp.resources import ResourceResult
from prefab_ui.app import PrefabApp


WORKSPACE_ROOT = Path(os.environ.get("PROJECT_DASHBOARD_WORKSPACE", "/root/project-dashboard"))
SOURCE_PATH = WORKSPACE_ROOT / "project_dashboard" / "server.py"
BUGS_PATH = WORKSPACE_ROOT / "project_dashboard" / "data" / "bugs.json"
METRICS_PATH = WORKSPACE_ROOT / "project_dashboard" / "data" / "metrics.json"


def load_module():
    sys.path.insert(0, str(WORKSPACE_ROOT))
    if "project_dashboard.server" in sys.modules:
        del sys.modules["project_dashboard.server"]
    return importlib.import_module("project_dashboard.server")


def parse_source() -> tuple[ast.Module, str]:
    source = SOURCE_PATH.read_text()
    return ast.parse(source), source


def get_function(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"Expected function {name!r} to exist in {SOURCE_PATH}")


def decorators_for(tree: ast.Module, name: str) -> list[str]:
    node = get_function(tree, name)
    return [ast.unparse(decorator) for decorator in node.decorator_list]


def assert_decorator(tree: ast.Module, function_name: str, expected_fragment: str) -> None:
    decorators = decorators_for(tree, function_name)
    if not any(expected_fragment in decorator for decorator in decorators):
        raise AssertionError(
            f"{function_name} is missing decorator fragment {expected_fragment!r}. "
            f"Found decorators: {decorators}"
        )


def assert_prefab_app(result: object, function_name: str) -> PrefabApp:
    if not isinstance(result, PrefabApp):
        raise AssertionError(f"{function_name} should return PrefabApp, got {type(result).__name__}")
    return result


def serialized_app(result: PrefabApp) -> str:
    if hasattr(result, "to_json"):
        return json.dumps(result.to_json(), default=str)
    return json.dumps(result.model_dump(by_alias=True), default=str)


class FakeContext:
    def __init__(self) -> None:
        self.state: dict[str, object] = {}

    async def read_resource(self, uri: str) -> ResourceResult:
        if uri != "dashboard://metrics":
            raise AssertionError(f"Unexpected resource URI: {uri}")
        return ResourceResult(METRICS_PATH.read_text())

    async def set_state(self, key: str, value: object, *, serializable: bool = True) -> None:
        self.state[key] = value

    async def get_state(self, key: str) -> object | None:
        return self.state.get(key)


def check_stage_01() -> None:
    tree, _ = parse_source()
    module = load_module()

    assert_decorator(tree, "project_status_board", "mcp.tool(app=True)")
    assert_decorator(tree, "bug_backlog_card", "mcp.tool(app=True)")

    board = assert_prefab_app(module.project_status_board(), "project_status_board")
    backlog = assert_prefab_app(module.bug_backlog_card(), "bug_backlog_card")

    board_dump = serialized_app(board)
    backlog_dump = serialized_app(backlog)

    for expected in ["Heading", "Badge", "Row", "Column", "Project Status Board"]:
        if expected not in board_dump:
            raise AssertionError(f"project_status_board output is missing {expected!r}")

    for expected in ["Heading", "Badge", "Bug Backlog"]:
        if expected not in backlog_dump:
            raise AssertionError(f"bug_backlog_card output is missing {expected!r}")


def check_stage_02() -> None:
    tree, _ = parse_source()
    module = load_module()

    assert_decorator(tree, "bug_report_workflow", "dashboard_app.ui()")
    assert_decorator(tree, "submit_bug_report", "dashboard_app.tool()")

    workflow = assert_prefab_app(module.bug_report_workflow(), "bug_report_workflow")
    workflow_dump = serialized_app(workflow)

    for expected in ["Form", "toolCall", "Updated backlog", "Bug Report Intake"]:
        if expected not in workflow_dump:
            raise AssertionError(f"bug_report_workflow output is missing {expected!r}")

    original_bugs = BUGS_PATH.read_text()
    original_count = len(json.loads(original_bugs))

    try:
        result = module.submit_bug_report(
            title="Validation bug",
            team="API Revamp",
            priority="P2",
            description="Created by the validation script.",
        )
        if not isinstance(result, dict):
            raise AssertionError("submit_bug_report should return a dictionary")
        if "message" not in result or "bugs" not in result:
            raise AssertionError("submit_bug_report should return message and bugs keys")

        updated_bugs = json.loads(BUGS_PATH.read_text())
        if len(updated_bugs) != original_count + 1:
            raise AssertionError("submit_bug_report should append a new bug to bugs.json")
    finally:
        BUGS_PATH.write_text(original_bugs)


def check_stage_03() -> None:
    tree, source = parse_source()
    module = load_module()

    assert_decorator(tree, "dashboard_metrics_resource", "dashboard://metrics")
    assert_decorator(tree, "delivery_metrics_dashboard", "mcp.tool(app=True)")

    if 'ctx.read_resource("dashboard://metrics")' not in source:
        raise AssertionError("delivery_metrics_dashboard should read data through ctx.read_resource")

    fake_ctx = FakeContext()
    dashboard = assert_prefab_app(
        asyncio.run(module.delivery_metrics_dashboard(fake_ctx)),
        "delivery_metrics_dashboard",
    )
    dashboard_dump = serialized_app(dashboard)

    for expected in ["Metric", "LineChart", "BarChart", "Delivery Metrics"]:
        if expected not in dashboard_dump:
            raise AssertionError(f"delivery_metrics_dashboard output is missing {expected!r}")


def check_stage_04() -> None:
    tree, source = parse_source()
    module = load_module()

    assert_decorator(tree, "project_browser", "mcp.tool(app=True)")
    assert_decorator(tree, "selected_project_details", "mcp.tool(app=True)")

    if "ctx.set_state" not in source or "ctx.get_state" not in source:
        raise AssertionError("Stage 4 should use ctx.set_state and ctx.get_state")

    fake_ctx = FakeContext()
    asyncio.run(module.remember_board_filter(fake_ctx, "blocked"))
    if fake_ctx.state.get("active_board_filter") != "blocked":
        raise AssertionError("remember_board_filter should persist the active board filter")

    browser = assert_prefab_app(asyncio.run(module.project_browser(fake_ctx)), "project_browser")
    if "Project Browser" not in serialized_app(browser):
        raise AssertionError("project_browser should render the browser UI")

    asyncio.run(module.remember_selected_project(fake_ctx, "proj-mobile"))
    details = assert_prefab_app(
        asyncio.run(module.selected_project_details(fake_ctx)),
        "selected_project_details",
    )
    details_dump = serialized_app(details)

    for expected in ["Selected Project", "Mobile Beta", "Sprint 12"]:
        if expected not in details_dump:
            raise AssertionError(f"selected_project_details output is missing {expected!r}")


def main() -> None:
    stage_name = sys.argv[1]
    if stage_name == "01":
        check_stage_01()
    elif stage_name == "02":
        check_stage_02()
    elif stage_name == "03":
        check_stage_03()
    elif stage_name == "04":
        check_stage_04()
    else:
        raise AssertionError(f"Unknown stage {stage_name!r}")


if __name__ == "__main__":
    main()
