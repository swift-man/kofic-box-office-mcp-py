#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
  echo "Virtual environment not found. Create .venv and install the project first." >&2
  exit 1
fi

source "${VENV_DIR}/bin/activate"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

if [[ -z "${KOFIC_BOX_OFFICE_SERVICE_KEY:-}" && -z "${KOFIC_BOX_OFFICE_SERVICE_KEY_ENCODED:-}" ]]; then
  echo "Set KOFIC_BOX_OFFICE_SERVICE_KEY or KOFIC_BOX_OFFICE_SERVICE_KEY_ENCODED before running." >&2
  exit 1
fi

if [[ -z "${ARKO_EVENT_SERVICE_KEY:-}" && -z "${ARKO_EVENT_SERVICE_KEY_ENCODED:-}" ]]; then
  echo "Set ARKO_EVENT_SERVICE_KEY or ARKO_EVENT_SERVICE_KEY_ENCODED before running." >&2
  exit 1
fi

if [[ -z "${MCST_PERFORMANCE_SERVICE_KEY:-}" && -z "${MCST_PERFORMANCE_SERVICE_KEY_ENCODED:-}" ]]; then
  echo "Set MCST_PERFORMANCE_SERVICE_KEY or MCST_PERFORMANCE_SERVICE_KEY_ENCODED before running." >&2
  exit 1
fi

export KOFIC_BOX_OFFICE_MCP_HOST="${KOFIC_BOX_OFFICE_MCP_HOST:-127.0.0.1}"
export KOFIC_BOX_OFFICE_MCP_PORT="${KOFIC_BOX_OFFICE_MCP_PORT:-8000}"
export KOFIC_BOX_OFFICE_MCP_PATH="${KOFIC_BOX_OFFICE_MCP_PATH:-/mcp}"

echo "Starting Culture Data MCP over streamable-http"
echo "Endpoint: http://${KOFIC_BOX_OFFICE_MCP_HOST}:${KOFIC_BOX_OFFICE_MCP_PORT}${KOFIC_BOX_OFFICE_MCP_PATH}"

exec kofic-box-office-mcp
