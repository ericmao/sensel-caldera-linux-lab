"""Compose targets for NDR cloud overlay."""

from __future__ import annotations

from pathlib import Path

import yaml


def test_compose_ndr_cloud_file_exists(root: Path) -> None:
    path = root / "compose.ndr.cloud.yml"
    assert path.is_file()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    services = data.get("services") or {}
    assert "edge-console" in services
    assert "packet-sensor" in services
    assert "sensel-edge-agent" in services
    ports = services["edge-console"].get("ports") or []
    assert any("8090" in str(p) for p in ports)


def test_makefile_has_ndr_cloud_targets(root: Path) -> None:
    makefile = (root / "Makefile").read_text(encoding="utf-8")
    assert "up-ndr-cloud:" in makefile
    assert "down-ndr-cloud:" in makefile
    assert "compose.ndr.cloud.yml" in makefile


def test_bootstrap_scripts_exist(root: Path) -> None:
    assert (root / "scripts/ensure-edge-sensor.sh").is_file()
    assert (root / "scripts/bootstrap-ndr-cloud.sh").is_file()
