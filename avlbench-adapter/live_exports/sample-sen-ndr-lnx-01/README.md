# sample-sen-ndr-lnx-01

Reference operator live export for **AVLBench Phase 2C import rehearsal**.

These files simulate what an operator would place under `live_exports/<run_id>/` after a manual Caldera training run. They are **not** produced by CI live execution.

Import via guacamole-ai `LiveExportImporter.import_rehearsal()`.

WAF plane is intentionally absent — importers must preserve `detection_gap` semantics when WAF is required by contract.
