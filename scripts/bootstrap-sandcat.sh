#!/bin/bash
set -euo pipefail

CALDERA_HOST="${CALDERA_HOST:-caldera}"
CALDERA_PORT="${CALDERA_PORT:-8888}"
SANDCAT_GROUP="${SANDCAT_GROUP:-castle-train-01}"
CALDERA_BASE="http://${CALDERA_HOST}:${CALDERA_PORT}"
CALDERA_API_KEY="${CALDERA_API_KEY:-ADMIN123}"
SANDCAT_BIN="/opt/sensel/sandcat"
SANDCAT_USER="sensel-svc"
HEALTH_URL="${CALDERA_BASE}/api/v2/health"

log() { echo "[bootstrap-sandcat] $*"; }

wait_for_caldera() {
  local attempt=1
  while [ "${attempt}" -le 60 ]; do
    if curl -sf -H "KEY: ${CALDERA_API_KEY}" "${HEALTH_URL}" >/dev/null 2>&1; then
      log "Caldera healthy at ${HEALTH_URL}"
      return 0
    fi
    log "waiting for Caldera (${attempt}/60)..."
    sleep 5
    attempt=$((attempt + 1))
  done
  log "Caldera did not become healthy"
  return 1
}

validate_deploy_command() {
  local cmd="$1"
  if echo "${cmd}" | grep -Eqi '0\.0\.0\.0|ngrok|cloudflared|tailscale|public'; then
    log "deploy command rejected: disallowed endpoint"
    return 1
  fi
  if ! echo "${cmd}" | grep -q 'caldera:8888'; then
    log "deploy command rejected: must target caldera:8888"
    return 1
  fi
  if ! echo "${cmd}" | grep -q 'castle-train-01'; then
    log "deploy command rejected: must use group castle-train-01"
    return 1
  fi
  if ! echo "${cmd}" | grep -q '/file/download'; then
    log "deploy command rejected: must use /file/download"
    return 1
  fi
  return 0
}

run_default_deploy() {
  log "using header-based /file/download deploy (Caldera v5.3.0 Sandcat docs)"
  curl -sk -X POST \
    -H 'file:sandcat.go' \
    -H 'platform:linux' \
    -H "server:${CALDERA_BASE}" \
    -H "group:${SANDCAT_GROUP}" \
    "${CALDERA_BASE}/file/download" > "${SANDCAT_BIN}.tmp"
  mv "${SANDCAT_BIN}.tmp" "${SANDCAT_BIN}"
  chmod 755 "${SANDCAT_BIN}"
  chown "${SANDCAT_USER}:${SANDCAT_USER}" "${SANDCAT_BIN}"
}

wait_for_caldera

if [ -n "${SANDCAT_DEPLOY_COMMAND:-}" ]; then
  log "using SANDCAT_DEPLOY_COMMAND from environment"
  validate_deploy_command "${SANDCAT_DEPLOY_COMMAND}"
  eval "${SANDCAT_DEPLOY_COMMAND}"
else
  run_default_deploy
fi

if [ ! -x "${SANDCAT_BIN}" ]; then
  log "sandcat binary missing after deploy"
  exit 1
fi

log "starting sandcat as ${SANDCAT_USER}"
exec runuser -u "${SANDCAT_USER}" -- "${SANDCAT_BIN}" \
  -server "${CALDERA_BASE}" \
  -group "${SANDCAT_GROUP}" \
  -v
