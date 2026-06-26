# Inline NDR Gateway (Docker Lab)

Suricata-based inline router for the Caldera training lab. Aligns with SenseL **it_ndr** profile
(same Suricata engine family as `sensel-ot-edge-sensor` / Portal bundle).

## Docker lab (localhost)

```bash
make up-ndr          # compose.yml + compose.ndr.yml
make status-ndr
python3 scripts/trainingctl.py run-manual --scenario SEN-NDR-LNX-01
```

Topology:

- `target01_net` — target-linux (172.30.11.10) → NDR (172.30.11.254)
- `target02_net` — target-linux-02 (172.30.12.10) → NDR (172.30.12.254)
- `c2_net` — caldera (172.31.0.2) ↔ NDR (172.31.0.254)

All target ↔ caldera and target ↔ target traffic is routed through `ndr-gateway`.

## Adversary profile

| Field | Value |
|-------|-------|
| Scenario | `SEN-NDR-LNX-01` |
| Profile name | `SEN-LNX-Chain-NDR` |
| Steps | SEN-LNX-012 → 013 → 014 → 017 → 019 |

## Suricata rules (lab SIDs)

| SID | Trigger |
|-----|---------|
| 9000010 | Caldera C2 HTTP `/beacon` (background) |
| 9000011 | Sandcat `POST /file/download` |
| 9000012 | Large C2 HTTP upload |
| 9000020 | ICMP peer probe (Step 2 / SEN-LNX-013) |

Logs: `docker exec ndr-gateway tail -f /var/log/suricata/eve.json`

## Correlation

```bash
python3 scripts/trainingctl.py correlate \
  --scenario SEN-NDR-LNX-01 \
  --operation-report /path/to/operation-report.json \
  --wazuh-alerts fixtures/wazuh-alerts-ndr.ndjson \
  --suricata-alerts fixtures/suricata-alerts-ndr.ndjson
```

## Portal production edge (SPAN / Ubuntu host)

For the full SenseL IT NDR Edge stack from your Portal download bundle:

```bash
cp /path/to/portal-bundle/.env ndr/portal.env   # gitignored
SENSEL_NDR_BUNDLE_DIR=/path/to/portal-bundle bash scripts/setup-ndr-edge.sh
```

That runs the upstream installer:

`docker compose -f docker-compose.openwrt.yml -f docker-compose.ndr-it.yml -f docker-compose.suricata.yml up -d --build`

See `ndr/portal.env.example` for pre-filled Control Plane variables.
