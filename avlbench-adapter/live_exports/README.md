# Operator live export drop zone — Phase 2C import rehearsal

Place manually exported lab evidence under an allowlisted subdirectory:

```
avlbench-adapter/live_exports/<run_id>/
├── manifest.yaml
├── caldera_operation_report.json
├── target_markers.json
├── wazuh_alerts.ndjson
├── suricata_alerts.ndjson
└── waf_events.json          # optional
```

## Sample rehearsal pack

See `sample-sen-ndr-lnx-01/` for a committed reference export (simulated operator artifacts).

## Import (guacamole-ai)

```python
from sensel_control_plane.services.avl.fixture_importer import LiveExportImporter

importer = LiveExportImporter()
result = importer.import_rehearsal(
    lab_id="sensel-caldera-linux-lab",
    export_subdir="avlbench-adapter/live_exports/sample-sen-ndr-lnx-01",
    expected_run_id="sample-sen-ndr-lnx-01",
    contract=contract,
    approval=approval,
    token=token,
)
```

Read-only — no Docker, Caldera, shell, or live execution.

## Safety

- Path must stay under `avlbench-adapter/live_exports` (no `..` traversal).
- `manifest.yaml` required; `run_id` must match.
- Template and training scenario must be allowlisted per `manual_live_smoke.yaml`.
- `safety_attestation` flags must all be true.
