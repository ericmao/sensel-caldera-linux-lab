#!/usr/bin/env bash
# Deploy SenseL IT NDR Edge stack from Portal bundle (production / SPAN capture).
# For Docker Caldera lab inline NDR use: make up-ndr
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE_DIR="${SENSEL_NDR_BUNDLE_DIR:-}"
INSTALL_SCRIPT="${BUNDLE_DIR}/install.sh"

if [[ -z "${BUNDLE_DIR}" ]]; then
  echo "Usage: SENSEL_NDR_BUNDLE_DIR=/path/to/portal-bundle $0" >&2
  echo "Example: SENSEL_NDR_BUNDLE_DIR=~/Downloads/sensel-it-ndr-company-* $0" >&2
  exit 1
fi

if [[ ! -f "${INSTALL_SCRIPT}" ]]; then
  echo "ERROR: install.sh not found in ${BUNDLE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${BUNDLE_DIR}/.env" ]] && [[ -f "${ROOT}/ndr/portal.env" ]]; then
  echo "==> Copying ${ROOT}/ndr/portal.env to bundle .env"
  cp -f "${ROOT}/ndr/portal.env" "${BUNDLE_DIR}/.env"
fi

echo "==> Running Portal NDR installer (clones sensel-ot-edge-sensor, starts Suricata stack)"
echo "    Compose: docker compose -f docker-compose.openwrt.yml -f docker-compose.ndr-it.yml -f docker-compose.suricata.yml"
exec bash "${INSTALL_SCRIPT}"
