#!/usr/bin/env python3
"""Write NDJSON training markers for SenseL / Wazuh correlation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MARKER_LOG = Path("/var/log/sensel-training/caldera-events.json")


def write_marker(
    scenario_id: str,
    technique_id: str,
    result: str,
    artifact_path: str,
    host: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scenario_id": scenario_id,
        "technique_id": technique_id,
        "host": host or os.environ.get("TARGET_AGENT_NAME", "caldera-linux-target-01"),
        "tenant_id": tenant_id or os.environ.get("TENANT_ID", "castle-train-01"),
        "event_type": "caldera_training_marker",
        "result": result,
        "artifact_path": artifact_path,
    }
    MARKER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with MARKER_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Write SenseL Caldera training marker")
    parser.add_argument("--scenario-id", required=True)
    parser.add_argument("--technique-id", required=True)
    parser.add_argument("--result", choices=["success", "failed"], default="success")
    parser.add_argument("--artifact-path", required=True)
    parser.add_argument("--host")
    parser.add_argument("--tenant-id")
    args = parser.parse_args()

    entry = write_marker(
        scenario_id=args.scenario_id,
        technique_id=args.technique_id,
        result=args.result,
        artifact_path=args.artifact_path,
        host=args.host,
        tenant_id=args.tenant_id,
    )
    print(json.dumps(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
