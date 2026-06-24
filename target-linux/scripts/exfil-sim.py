#!/usr/bin/env python3
"""Simulate exfiltration size planning with local byte counts only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_STAGE = Path("/tmp/sensel-training-staging")
DEFAULT_ARCHIVE = Path("/tmp/sensel-staging.tar.gz")
DEFAULT_OUT = Path("/tmp/sensel-exfil-sim.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate exfil size check (local only)")
    parser.add_argument("--stage", default=str(DEFAULT_STAGE))
    parser.add_argument("--archive", default=str(DEFAULT_ARCHIVE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    stage = Path(args.stage)
    archive = Path(args.archive)
    out = Path(args.out)

    files: list[dict[str, int | str]] = []
    staging_bytes = 0
    if stage.is_dir():
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                size = path.stat().st_size
                staging_bytes += size
                files.append({"path": str(path), "size": size})
    archive_bytes = archive.stat().st_size if archive.is_file() else 0
    payload = {
        "simulated": True,
        "note": "Local byte count only; no network exfiltration performed",
        "staging_bytes": staging_bytes,
        "archive_bytes": archive_bytes,
        "would_transfer_bytes": staging_bytes + archive_bytes,
        "files": files,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"artifact_path": str(out), "would_transfer_bytes": payload["would_transfer_bytes"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
