#!/bin/bash
set -euo pipefail

if [ "${ENABLE_NDR:-false}" = "true" ]; then
  /opt/sensel/scripts/setup-ndr-routes.sh
fi

if [ "${ENABLE_WAZUH:-false}" = "true" ]; then
  /opt/sensel/scripts/install-wazuh-agent.sh
fi

exec /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
