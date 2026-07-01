# AVLBench adapter metadata (Phase 2A / 2B)

This directory contains **read-only adapter metadata** for guacamole-ai AVLBench integration.

**No autonomous runner execution code lives here.** Compose, Caldera abilities, Wazuh rules, and Suricata rules are unchanged.

## Files

| File | Purpose |
| --- | --- |
| `runner_contract.yaml` | Phase 2A Controlled Lab Runner contract |
| `manual_live_smoke.yaml` | Phase 2B operator manual live smoke gate |
| `safe_templates/caldera_linux_safe_ttp.yaml` | Lab-side mirror of `caldera-safe-ttp-v1` template |
| `lab_capabilities.yaml` | Machine-readable capability inventory |
| `evidence_mapping.yaml` | Lab artifact → AVL evidence plane mapping |
| `sample_external_lab_ref.yaml` | Example `ExternalLabRef` for control plane |
| `samples/` | Read-only fixture JSON for evidence import |
| `live_exports/` | Operator live export drop zone (created at run time) |

## Phase 2B manual live smoke

Requires **both** control-plane env vars:

```bash
AVL_LAB_RUNNER_LIVE_ENABLED=true
AVL_LAB_RUNNER_MANUAL_CONFIRM=I_UNDERSTAND_THIS_RUNS_LOCAL_LAB
```

Allowlisted training scenarios: `SEN-NDR-LNX-01`, `SEN-APT29-LNX-01`.  
See guacamole-ai `avlbench/lab-runner/manual-live-smoke.md`.

## Phase 2A runner boundary

guacamole-ai `ControlledLabRunnerClient` — dry-run stub methods only by default.

## Documentation

- [docs/AVL_RUNNER_ADAPTER_CONTRACT.md](../docs/AVL_RUNNER_ADAPTER_CONTRACT.md)
- guacamole-ai: `avlbench/integrations/sensel-caldera-linux-lab.md`
- guacamole-ai: `avlbench/lab-runner/manual-live-smoke.md`

## Safety

Typed templates + capability tokens only. No arbitrary shell, public tunnel, host networking, or Docker socket access. API does not auto-execute live lab actions.
