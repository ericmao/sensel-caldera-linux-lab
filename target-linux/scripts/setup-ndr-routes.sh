#!/bin/bash
# Configure static routes when traffic must traverse the inline NDR gateway.
set -euo pipefail

if [ "${ENABLE_NDR:-false}" != "true" ]; then
  exit 0
fi

GATEWAY="${NDR_GATEWAY:?NDR_GATEWAY required when ENABLE_NDR=true}"
PEER_CIDR="${NDR_PEER_CIDR:-172.30.12.0/24}"
C2_CIDR="${NDR_C2_CIDR:-172.31.0.0/24}"

route_add() {
  local cidr="$1"
  if ! ip route show "${cidr}" 2>/dev/null | grep -q .; then
    ip route add "${cidr}" via "${GATEWAY}"
    echo "[setup-ndr-routes] route ${cidr} via ${GATEWAY}"
  fi
}

route_add "${C2_CIDR}"
route_add "${PEER_CIDR}"

# Ensure Caldera and peer traffic hairpin through the NDR gateway.
ip route replace default via "${GATEWAY}" 2>/dev/null || ip route add default via "${GATEWAY}"
