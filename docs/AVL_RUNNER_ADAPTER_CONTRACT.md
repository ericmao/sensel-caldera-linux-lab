# AVL Controlled Lab Runner — Adapter Contract

**Lab:** sensel-caldera-linux-lab  
**Phase:** 0 (metadata only — no runner implementation in this repo)

## Role

This repository is an **external controlled lab reference**, not the AVL control plane. Future integration allows the guacamole-ai Controlled Lab Runner to request **typed operations only** via adapter metadata in `avlbench-adapter/`.

## Current lab capabilities

| Layer | Component | Evidence output |
| --- | --- | --- |
| Attack simulation | Caldera 5.3.0 + Sandcat | Operation reports, ability chain |
| Safe abilities | SEN-LNX-001..019 | Target markers JSON |
| EDR | Wazuh Agent → Manager (Phase 2) | Alerts rules 100610–100634 |
| NDR | Suricata inline (`ndr-gateway`) | `eve.json` SID 9000010–9000020 |
| Correlation | `trainingctl correlate` | Three-plane markdown/JSON reports |
| Cloud smoke | `up-ndr-cloud` Edge Console | Portal MQTT (training tenant only) |

All operations remain on **localhost Docker** / isolated bridge networks.

## Future adapter boundary

### Allowed requests (Phase 1+)

| Request | Purpose |
| --- | --- |
| `prepare_lab` | Validate compose stack, networks, health |
| `run_safe_template` | Execute approved Caldera ability chain template |
| `collect_report` | Export Caldera operation report |
| `collect_markers` | Read `/var/log/sensel-training/caldera-events.json` |
| `collect_wazuh_fixture` | Export Wazuh alerts (fixture or live) |
| `collect_suricata_fixture` | Export Suricata `eve.json` |
| `reset_lab` | Run documented cleanup / marker reset |

### Forbidden requests (always)

- Arbitrary shell or command passthrough
- New exploit or unrestricted payload
- Production or Internet targets
- Public tunnel exposure
- Docker socket mount
- Host networking mode
- Destructive file operations
- Privileged target containers

## Control plane registration

Registered in guacamole-ai `ExternalLabRegistry` as `sensel-caldera-linux-lab` with **`enabled: false`**.

See also:

- `avlbench-adapter/lab_capabilities.yaml`
- `avlbench-adapter/evidence_mapping.yaml`
- `avlbench-adapter/sample_external_lab_ref.yaml`
