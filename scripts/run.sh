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

RESTART=0
for arg in "$@"; do
  case "${arg}" in
    --restart) RESTART=1 ;;
    -h|--help)
      cat <<EOF
Kullanım: bash scripts/run.sh [--restart]

  --restart   Port ${PORT} üzerinde çalışan eski AquaSanayi sunucusunu kapatıp yeniden başlatır.

Ortam değişkenleri:
  HOST=127.0.0.1   PORT=8000   ACCESS_LOG=off
EOF
      exit 0
      ;;
    *)
      echo "[AquaSanayi AI] Bilinmeyen argüman: ${arg} (--help ile kullanım)" >&2
      exit 2
      ;;
  esac
done

# --- Port çakışması koruması -------------------------------------------------
port_pids() {
  ss -tlnpH "sport = :${PORT}" 2>/dev/null | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u || true
}

is_our_app() {
  # Küçük bir HTTP yoklaması: /api/health 200 ve gövdede uygulama adı geçiyor mu?
  local body
  body="$(curl -fsS --max-time 2 "http://${HOST}:${PORT}/api/health" 2>/dev/null || true)"
  [ -n "${body}" ] && printf '%s' "${body}" | grep -qiE 'aquasanayi|ekozeka|service'
}

PIDS="$(port_pids)"
if [ -n "${PIDS}" ]; then
  if [ "${RESTART}" -eq 1 ]; then
    echo "[AquaSanayi AI] Port ${PORT} dolu (PID: ${PIDS}) → --restart verildi, eski sunucu kapatılıyor..."
    # shellcheck disable=SC2086
    kill ${PIDS} 2>/dev/null || true
    for _ in $(seq 1 25); do
      [ -z "$(port_pids)" ] && break
      sleep 0.2
    done
    if [ -n "$(port_pids)" ]; then
      echo "[AquaSanayi AI] Nazik kapatma yetmedi, SIGKILL gönderiliyor..."
      # shellcheck disable=SC2086
      kill -9 ${PIDS} 2>/dev/null || true
      sleep 0.5
    fi
    if [ -n "$(port_pids)" ]; then
      echo "[AquaSanayi AI] HATA: Port ${PORT} hâlâ serbest değil. Şu komutla kontrol edin:" >&2
      echo "  ss -tlnp 'sport = :${PORT}'" >&2
      exit 1
    fi
  elif is_our_app; then
    echo "[AquaSanayi AI] Sunucu zaten çalışıyor: http://${HOST}:${PORT}"
    echo "[AquaSanayi AI] Kodu yenilediyseniz yeniden başlatmak için: bash scripts/run.sh --restart"
    exit 0
  else
    echo "[AquaSanayi AI] HATA: Port ${PORT} başka bir süreç tarafından kullanılıyor (PID: ${PIDS})." >&2
    echo "  Ayrıntı : ss -tlnp 'sport = :${PORT}'" >&2
    echo "  Kapat   : kill ${PIDS}" >&2
    echo "  Ya da   : bash scripts/run.sh --restart   veya   PORT=8001 bash scripts/run.sh" >&2
    exit 1
  fi
fi

echo "[AquaSanayi AI] Sunucu başlatılıyor: http://${HOST}:${PORT}"
if [ "${ACCESS_LOG:-on}" = "off" ]; then
  echo "[AquaSanayi AI] Erişim logu kapalı (ACCESS_LOG=off). Uygulama logları görünmeye devam eder."
fi
exec uv run uvicorn ekozeka26.app:app --host "${HOST}" --port "${PORT}" "${EXTRA_ARGS[@]}"
