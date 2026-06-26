#!/bin/bash
set -euo pipefail

log() { echo "[ndr-gateway] $*"; }

# eth0=target01_net, eth1=target02_net, eth2=c2_net (compose network attach order)
TARGET01_IF="${TARGET01_IF:-eth0}"
TARGET02_IF="${TARGET02_IF:-eth1}"
C2_IF="${C2_IF:-eth2}"

# ip_forward is enabled via compose sysctls; avoid failing on read-only sysctl inside entrypoint.
sysctl -w net.ipv4.conf.all.rp_filter=0 >/dev/null 2>&1 || true
sysctl -w net.ipv4.conf.default.rp_filter=0 >/dev/null 2>&1 || true

iptables -P FORWARD ACCEPT
iptables -t nat -F POSTROUTING 2>/dev/null || true
iptables -t nat -A POSTROUTING -o "${C2_IF}" -j MASQUERADE

log "starting Suricata on ${TARGET01_IF}, ${TARGET02_IF}, ${C2_IF}"
suricata \
  -D \
  -c /etc/suricata/suricata.yaml \
  --pidfile /var/run/suricata.pid \
  -i "${TARGET01_IF}" \
  -i "${TARGET02_IF}" \
  -i "${C2_IF}"

log "NDR gateway ready (forwarding + Suricata IDS)"
tail -F /var/log/suricata/eve.json 2>/dev/null || sleep infinity
