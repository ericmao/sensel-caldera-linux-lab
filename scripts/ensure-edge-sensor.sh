#!/usr/bin/env bash
# Clone sensel-ot-edge-sensor for make up-ndr-cloud (build contexts + config).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="${SENSEL_OT_EDGE_DIR:-${ROOT}/vendor/sensel-ot-edge-sensor}"
REF="${SENSEL_OT_EDGE_REF:-main}"
REPO="${SENSEL_OT_EDGE_REPO:-https://github.com/AvocadoAI-Lab/sensel-ot-edge-sensor.git}"

if [[ -d "${DIR}/.git" ]]; then
  echo "==> Edge sensor repo: ${DIR}"
  exit 0
fi

if [[ -d "${DIR}" ]]; then
  echo "ERROR: ${DIR} exists but is not a git clone. Remove it or set SENSEL_OT_EDGE_DIR." >&2
  exit 1
fi

echo "==> Cloning ${REPO} (${REF}) into ${DIR}"
mkdir -p "$(dirname "${DIR}")"
git clone --depth 1 --branch "${REF}" "${REPO}" "${DIR}"

if [[ ! -f "${DIR}/services/packet-sensor/Dockerfile" ]]; then
  echo "ERROR: clone incomplete — packet-sensor Dockerfile missing." >&2
  exit 1
fi

echo "==> Edge sensor ready at ${DIR}"
