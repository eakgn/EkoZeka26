#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

echo "[AquaSanayi AI] Sunucu başlatılıyor: http://${HOST}:${PORT}"
exec uv run uvicorn ekozeka26.app:app --host "${HOST}" --port "${PORT}"
