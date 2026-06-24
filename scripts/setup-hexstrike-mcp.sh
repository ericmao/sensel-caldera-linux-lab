#!/usr/bin/env bash
# Generate .cursor/mcp.json for HexStrike from .env (Phase 3).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT}/.env"
OUT="${ROOT}/.cursor/mcp.json"
EXAMPLE="${ROOT}/.cursor/mcp.json.example"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

HEXSTRIKE_SERVER_URL="${HEXSTRIKE_SERVER_URL:-http://192.168.1.110:8888}"
HEXSTRIKE_MCP_SCRIPT="${HEXSTRIKE_MCP_SCRIPT:-${HOME}/hexstrike-ai/hexstrike_mcp.py}"
HEXSTRIKE_MCP_PYTHON="${HEXSTRIKE_MCP_PYTHON:-python3}"

if [[ ! -f "${HEXSTRIKE_MCP_SCRIPT}" ]]; then
  echo "[error] HEXSTRIKE_MCP_SCRIPT not found: ${HEXSTRIKE_MCP_SCRIPT}" >&2
  echo "  Set HEXSTRIKE_MCP_SCRIPT in .env or clone hexstrike-ai to ~/hexstrike-ai" >&2
  exit 1
fi

mkdir -p "${ROOT}/.cursor"

python3 - "${OUT}" "${HEXSTRIKE_MCP_PYTHON}" "${HEXSTRIKE_MCP_SCRIPT}" "${HEXSTRIKE_SERVER_URL}" <<'PY'
import json
import sys

out, py, script, server = sys.argv[1:5]
cfg = {
    "mcpServers": {
        "hexstrike-ai": {
            "command": py,
            "args": [script, "--server", server],
            "description": "Phase 3 — HexStrike AI on Kali (authorized lab scope only)",
            "timeout": 300,
            "disabled": False,
            "alwaysAllow": [],
        }
    }
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print(f"[ok] wrote {out}")
print(f"     server={server}")
print(f"     script={script}")
PY

echo "[next] Reload Cursor (Cmd+Shift+P → Developer: Reload Window)"
echo "[next] Settings → MCP → confirm hexstrike-ai connected"
echo "[next] make hexstrike-check"
