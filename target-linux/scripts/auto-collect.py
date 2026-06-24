#!/usr/bin/env python3
"""Copy prior discovery artifacts into an automated collection directory."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

DEST = Path("/tmp/sensel-auto-collect")
SOURCES = (
    "/tmp/sensel-discovery-003.txt",
    "/tmp/sensel-discovery-008.txt",
    "/tmp/sensel-discovery-009.txt",
)


def main() -> int:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in SOURCES:
        path = Path(src)
        if path.is_file():
            shutil.copy2(path, DEST / path.name)
            copied += 1
    if copied == 0:
        print("auto-collect: no source artifacts found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
