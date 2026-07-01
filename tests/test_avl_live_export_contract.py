"""Validate AVL live export sample contract (Phase 2C)."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "avlbench-adapter/live_exports/sample-sen-ndr-lnx-01"


@pytest.fixture
def manifest() -> dict:
    path = SAMPLE / "manifest.yaml"
    assert path.is_file()
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_live_export_manifest_schema(manifest: dict) -> None:
    required = {
        "run_id",
        "scenario_id",
        "template_id",
        "training_scenario",
        "target_id",
        "network_id",
        "exported_at",
        "exported_by",
        "source_repo",
        "files",
        "safety_attestation",
    }
    assert required.issubset(manifest.keys())
    assert manifest["training_scenario"] == "SEN-NDR-LNX-01"
    attestation = manifest["safety_attestation"]
    for key in (
        "no_public_tunnel",
        "no_host_network",
        "no_docker_socket_to_agent",
        "no_destructive_payload",
        "local_lab_only",
    ):
        assert attestation[key] is True


def test_live_export_files_exist(manifest: dict) -> None:
    for logical, filename in manifest["files"].items():
        path = SAMPLE / filename
        assert path.is_file(), f"missing {logical}: {filename}"
