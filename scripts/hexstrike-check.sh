#!/usr/bin/env bash
# Verify HexStrike server reachability (Phase 3).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ROOT}/.env"
  set +a
fi

KALI_HOST="${KALI_HOST:-192.168.1.110}"
HEXSTRIKE_SERVER_URL="${HEXSTRIKE_SERVER_URL:-http://${KALI_HOST}:8888}"
HEALTH_URL="${HEXSTRIKE_SERVER_URL%/}/health"

echo "=== Phase 3 HexStrike connectivity ==="
echo "KALI_HOST=${KALI_HOST}"
echo "HEXSTRIKE_SERVER_URL=${HEXSTRIKE_SERVER_URL}"

if ping -c 1 -W 2 "${KALI_HOST}" >/dev/null 2>&1; then
  echo "[ok] ping ${KALI_HOST}"
else
  echo "[fail] ping ${KALI_HOST}"
  exit 1
fi

if curl -sf --connect-timeout 5 "${HEALTH_URL}" >/dev/null; then
  echo "[ok] HexStrike health ${HEALTH_URL}"
  curl -s "${HEALTH_URL}" | head -c 500
  echo ""
else
  echo "[fail] HexStrike health ${HEALTH_URL}"
  echo "  → On Kali: bash scripts/kali/hexstrike-server-setup.sh && start hexstrike_server.py"
  exit 1
fi

MCP_JSON="${ROOT}/.cursor/mcp.json"
if [[ -f "${MCP_JSON}" ]]; then
  echo "[ok] Cursor MCP config present: ${MCP_JSON}"
else
  echo "[warn] Missing ${MCP_JSON} — run: bash scripts/setup-hexstrike-mcp.sh"
fi

echo "=== done ==="
