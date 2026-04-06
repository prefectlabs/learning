#!/bin/bash
set -euxo pipefail

TRACK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKSPACE_ROOT="/root/project-dashboard"
TEMPLATE_ROOT="${TRACK_ROOT}/assets/project-dashboard/template"
STAGE_ROOT="${TRACK_ROOT}/assets/project-dashboard/stages"

export PATH="/root/.local/bin:${PATH}"

stop_preview() {
  pkill -f "fastmcp dev apps" || true
}

ensure_workspace_root() {
  mkdir -p "${WORKSPACE_ROOT}"
}

sync_stage() {
  local stage_name="$1"

  ensure_workspace_root

  find "${WORKSPACE_ROOT}" -mindepth 1 -maxdepth 1 ! -name '.venv' -exec rm -rf {} +
  cp -R "${TEMPLATE_ROOT}/." "${WORKSPACE_ROOT}/"
  cp -R "${STAGE_ROOT}/${stage_name}/." "${WORKSPACE_ROOT}/"
}

ensure_environment() {
  ensure_workspace_root

  if [ ! -x /root/.local/bin/uv ]; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi

  if [ ! -d "${WORKSPACE_ROOT}/.venv" ]; then
    cd "${WORKSPACE_ROOT}"
    uv venv --python 3.12 .venv
    source .venv/bin/activate
    uv pip install -e .
  fi
}

run_stage_check() {
  local stage_name="$1"

  source "${WORKSPACE_ROOT}/.venv/bin/activate"
  PYTHONPATH="${WORKSPACE_ROOT}" \
    python "${TRACK_ROOT}/assets/project-dashboard/check_stage.py" "${stage_name}"
}
