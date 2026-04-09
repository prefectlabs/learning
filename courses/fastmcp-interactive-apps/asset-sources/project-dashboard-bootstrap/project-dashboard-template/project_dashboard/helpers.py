from __future__ import annotations

import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parent
DATA_ROOT = PACKAGE_ROOT / "data"


def read_json(name: str):
    return json.loads((DATA_ROOT / name).read_text())


def load_projects() -> list[dict]:
    return read_json("projects.json")


def load_metrics() -> dict:
    return read_json("metrics.json")


def find_project(project_id: str) -> dict | None:
    for project in load_projects():
        if project["id"] == project_id:
            return project
    return None
