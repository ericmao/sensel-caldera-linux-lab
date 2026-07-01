# AVLBench B0 sample fixture references (read-only)

These files document how **sensel-caldera-linux-lab** artifacts map to guacamole-ai B0 fixtures.

**No lab execution or compose changes** are made in Phase 1C.

| Lab artifact | AVL plane | B0 fixture file (control plane) |
| --- | --- | --- |
| Caldera operation report | `caldera_operation_events` | `caldera_operation_events.json` |
| `/var/log/sensel-training/caldera-events.json` | `target_markers` | `target_markers.json` |
| Wazuh alerts (rules 100610–100634) | `wazuh_events` | `wazuh_events.json` |
| Suricata `eve.json` (SID 9000010+) | `ndr_events` | `ndr_events.json` |
| WAF (OWASP CRS reference) | `waf_events` | `waf_events.example.json` (example only) |

**Phase 1C:** The control plane Golden Path fixture includes normalized `waf_events.json`. This lab repo provides `waf_events.example.json` with S0/S1/S2 placeholder events for documentation — not imported unless copied to `waf_events.json`.

See `b0_golden_path_mapping.yaml` and `guacamole-ai/avlbench/integrations/reference-waf-owasp-crs-modsecurity.md`.
