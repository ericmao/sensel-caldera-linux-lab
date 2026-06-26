# Inline NDR gateway — jasonish/suricata (same family as sensel-ot-edge-sensor) + iptables router.
FROM jasonish/suricata:7.0.5

USER root

RUN set -eux; \
    if command -v microdnf >/dev/null 2>&1; then \
      microdnf install -y iptables iputils; \
      microdnf clean all; \
    elif command -v dnf >/dev/null 2>&1; then \
      dnf install -y iptables iputils; \
      dnf clean all; \
    elif command -v apt-get >/dev/null 2>&1; then \
      apt-get update; \
      apt-get install -y --no-install-recommends iptables iproute2 iputils-ping procps; \
      rm -rf /var/lib/apt/lists/*; \
    else \
      echo "no supported package manager in base image" >&2; exit 1; \
    fi; \
    mkdir -p /var/log/suricata /etc/suricata/rules

COPY ndr/suricata/suricata.yaml /etc/suricata/suricata.yaml
COPY ndr/suricata/rules/ /etc/suricata/rules/
COPY ndr/entrypoint.sh /usr/local/bin/ndr-entrypoint.sh
RUN chmod +x /usr/local/bin/ndr-entrypoint.sh

HEALTHCHECK --interval=15s --timeout=5s --retries=10 --start-period=25s \
    CMD pidof suricata >/dev/null && ping -c1 -W2 172.31.0.2 >/dev/null

ENTRYPOINT ["/usr/local/bin/ndr-entrypoint.sh"]
