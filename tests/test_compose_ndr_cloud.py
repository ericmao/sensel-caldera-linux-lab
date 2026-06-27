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


def test_windows_deploy_assets_exist(root: Path) -> None:
    assert (root / "docs/WINDOWS-DEPLOY.md").is_file()
    assert (root / "scripts/windows/lab.ps1").is_file()
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "WINDOWS-DEPLOY.md" in readme
    assert "lab.ps1" in readme


def test_training_guide_21_exists(root: Path) -> None:
    guide = root / "training/TRAINING-GUIDE-2.1.md"
    assert guide.is_file()
    text = guide.read_text(encoding="utf-8")
    assert "SEN-NDR-LNX-01" in text
    assert "make up-ndr-cloud" in text
    assert (root / "training/pdf/README.md").is_file()
