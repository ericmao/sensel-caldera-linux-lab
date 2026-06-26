FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget ca-certificates iproute2 iputils-ping net-tools procps python3 python3-pip sudo supervisor util-linux \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1001 -s /bin/bash sensel-svc

RUN mkdir -p /opt/sensel /opt/sensel-training-data /var/log/sensel-training \
    /tmp/sensel-training-staging /opt/sensel/scripts \
    && chown -R sensel-svc:sensel-svc /opt/sensel /var/log/sensel-training /tmp/sensel-training-staging

COPY target-linux/scripts/marker-writer.py /opt/sensel/scripts/marker-writer.py
COPY target-linux/scripts/staging-manifest.py /opt/sensel/scripts/staging-manifest.py
COPY target-linux/scripts/auto-collect.py /opt/sensel/scripts/auto-collect.py
COPY target-linux/scripts/exfil-sim.py /opt/sensel/scripts/exfil-sim.py
COPY target-linux/scripts/lateral-plan.py /opt/sensel/scripts/lateral-plan.py
COPY scripts/bootstrap-sandcat.sh /opt/sensel/scripts/bootstrap-sandcat.sh
COPY target-linux/scripts/install-wazuh-agent.sh /opt/sensel/scripts/install-wazuh-agent.sh
COPY target-linux/scripts/setup-ndr-routes.sh /opt/sensel/scripts/setup-ndr-routes.sh
COPY wazuh/agent/ossec.conf.fragment.xml /opt/sensel/ossec.conf.fragment.xml
RUN chmod +x /opt/sensel/scripts/*.sh /opt/sensel/scripts/*.py

# Synthetic training data for SEN-LNX-004
RUN printf 'customer_id,name,region\n1001,Demo Corp APAC,APAC\n1002,Demo Corp EMEA,EMEA\n' \
    > /opt/sensel-training-data/customer_demo.csv \
    && printf 'Project: Castle Training Demo\nStatus: synthetic\nOwner: sensel-lab\n' \
    > /opt/sensel-training-data/engineering_demo.txt \
    && printf '{"incident_id":"INC-DEMO-001","severity":"low","summary":"Synthetic training incident"}\n' \
    > /opt/sensel-training-data/incident_demo.json \
    && chmod -R a+r /opt/sensel-training-data

# Tier-2 synthetic data for Chain C (target-linux-02)
RUN mkdir -p /opt/sensel-training-data-tier2 \
    && printf 'account_id,region,balance\n2001,APAC,125000\n2002,EMEA,88000\n' \
    > /opt/sensel-training-data-tier2/finance_demo.csv \
    && printf 'Asset: Internal File Server Tier2\nStatus: synthetic\nOwner: sensel-lab\n' \
    > /opt/sensel-training-data-tier2/server_demo.txt \
    && printf '{"record_id":"REC-T2-001","classification":"internal","summary":"Synthetic tier2 training record"}\n' \
    > /opt/sensel-training-data-tier2/records_demo.json \
    && chmod -R a+r /opt/sensel-training-data-tier2

COPY target-linux/supervisord.conf /etc/supervisor/conf.d/sensel.conf
COPY target-linux/entrypoint.sh /usr/local/bin/target-entrypoint.sh
RUN chmod +x /usr/local/bin/target-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/target-entrypoint.sh"]
