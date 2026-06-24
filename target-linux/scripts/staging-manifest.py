#!/usr/bin/env python3
"""Write a SHA256 manifest for staged synthetic training files."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    stage = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/sensel-training-staging")
    files = []
    for path in sorted(stage.glob("*")):
        if path.name == "manifest.json":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"path": str(path), "sha256": digest, "size": path.stat().st_size})
    manifest = {"tenant_id": "castle-train-01", "files": files}
    (stage / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
