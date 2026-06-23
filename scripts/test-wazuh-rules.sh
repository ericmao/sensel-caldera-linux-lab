#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULES="${ROOT}/wazuh/manager/local_rules.xml"
EVENTS_DIR="${ROOT}/wazuh/manager/test-events"

if ! command -v wazuh-logtest >/dev/null 2>&1; then
  echo "wazuh-logtest not found; skipping live rule test (use pytest fixtures instead)"
  exit 0
fi

TMP_RULES="$(mktemp)"
cp "${RULES}" "${TMP_RULES}"

for event in "${EVENTS_DIR}"/sen-lnx-*.json; do
  name="$(basename "${event}")"
  echo "Testing ${name}..."
  wazuh-logtest -q -f "${TMP_RULES}" < "${event}" || {
    echo "Rule test failed for ${name}" >&2
    exit 1
  }
done

echo "All wazuh-logtest events passed"
