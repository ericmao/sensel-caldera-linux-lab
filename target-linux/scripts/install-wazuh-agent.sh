#!/bin/bash
# Install Wazuh agent when ENABLE_WAZUH=true (Phase 2)
set -euo pipefail

WAZUH_VERSION="${WAZUH_VERSION:-4.14.1-1}"
WAZUH_MANAGER_HOST="${WAZUH_MANAGER_HOST:?WAZUH_MANAGER_HOST is required when ENABLE_WAZUH=true}"
WAZUH_MANAGER_PORT="${WAZUH_MANAGER_PORT:-1514}"
WAZUH_ENROLLMENT_HOST="${WAZUH_ENROLLMENT_HOST:-$WAZUH_MANAGER_HOST}"
WAZUH_ENROLLMENT_PORT="${WAZUH_ENROLLMENT_PORT:-1515}"
WAZUH_AGENT_NAME="${WAZUH_AGENT_NAME:-caldera-linux-target-01}"
WAZUH_ENROLLMENT_MODE="${WAZUH_ENROLLMENT_MODE:-none}"

if [ "${ENABLE_WAZUH:-false}" != "true" ]; then
  echo "Wazuh agent install skipped (ENABLE_WAZUH=false)"
  exit 0
fi

if ! command -v wazuh-agent >/dev/null 2>&1 && [ ! -f /var/ossec/bin/wazuh-control ]; then
  curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring \
    --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import
  chmod 644 /usr/share/keyrings/wazuh.gpg
  echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
    > /etc/apt/sources.list.d/wazuh.list
  apt-get update
  WAZUH_MANAGER="${WAZUH_MANAGER_HOST}" WAZUH_AGENT_NAME="${WAZUH_AGENT_NAME}" \
    apt-get install -y wazuh-agent="${WAZUH_VERSION}"
fi

if [ -f /opt/sensel/ossec.conf.fragment.xml ]; then
  python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET

fragment = ET.parse("/opt/sensel/ossec.conf.fragment.xml").getroot()
conf_path = Path("/var/ossec/etc/ossec.conf")
tree = ET.parse(conf_path)
root = tree.getroot()
for child in fragment:
    root.append(child)
tree.write(conf_path, encoding="utf-8", xml_declaration=True)
PY
fi

case "${WAZUH_ENROLLMENT_MODE}" in
  key_mount)
    if [ -f /run/secrets/wazuh/client.keys ]; then
      install -m 640 -o wazuh -g wazuh /run/secrets/wazuh/client.keys /var/ossec/etc/client.keys
    else
      echo "key_mount mode requires /run/secrets/wazuh/client.keys" >&2
      exit 1
    fi
    ;;
  auto_enroll)
    /var/ossec/bin/agent-auth -m "${WAZUH_ENROLLMENT_HOST}" -p "${WAZUH_ENROLLMENT_PORT}" -A "${WAZUH_AGENT_NAME}"
    ;;
  none)
    echo "Wazuh enrollment mode=none; configure manager manually if needed"
    ;;
  *)
    echo "Unknown WAZUH_ENROLLMENT_MODE: ${WAZUH_ENROLLMENT_MODE}" >&2
    exit 1
    ;;
esac

/var/ossec/bin/wazuh-control start
