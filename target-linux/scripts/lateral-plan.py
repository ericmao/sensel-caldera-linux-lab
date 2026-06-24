#!/usr/bin/env python3
"""Write a simulated lateral-movement plan marker (no remote execution)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("/tmp/sensel-lateral-plan.json")


def main() -> int:
    payload = {
        "simulated": True,
        "note": "Training lateral plan only; no remote execution performed",
        "source_host": os.environ.get("TARGET_AGENT_NAME", "caldera-linux-target-01"),
        "target_host": os.environ.get("LATERAL_TARGET_HOST", "caldera-linux-target-02"),
        "planned_techniques": ["T1018", "T1046", "T1074.001", "T1560.001"],
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"artifact_path": str(OUT), "target_host": payload["target_host"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
