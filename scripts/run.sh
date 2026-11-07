#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

# Opsiyonel: OpenCode / port-yoklayıcıların ürettiği erişim logu gürültüsünü kapatmak için
#   ACCESS_LOG=off bash scripts/run.sh
EXTRA_ARGS=()
if [ "${ACCESS_LOG:-on}" = "off" ]; then
  EXTRA_ARGS+=(--no-access-log)
fi

echo "[AquaSanayi AI] Sunucu başlatılıyor: http://${HOST}:${PORT}"
if [ "${ACCESS_LOG:-on}" = "off" ]; then
  echo "[AquaSanayi AI] Erişim logu kapalı (ACCESS_LOG=off). Uygulama logları görünmeye devam eder."
fi
exec uv run uvicorn ekozeka26.app:app --host "${HOST}" --port "${PORT}" "${EXTRA_ARGS[@]}"
