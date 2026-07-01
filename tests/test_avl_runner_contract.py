"""Validate AVL runner contract and safe template metadata (Phase 2A)."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "avlbench-adapter"


@pytest.fixture
def runner_contract() -> dict:
    path = ADAPTER / "runner_contract.yaml"
    assert path.is_file(), "runner_contract.yaml must exist"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture
def safe_template() -> dict:
    path = ADAPTER / "safe_templates" / "caldera_linux_safe_ttp.yaml"
    assert path.is_file(), "safe template must exist"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_runner_contract_schema(runner_contract: dict) -> None:
    required = {
        "contract_version",
        "lab_id",
        "adapter_type",
        "supported_methods",
        "allowlisted_templates",
        "forbidden_request_flags",
        "audit_event_fields",
    }
    assert required.issubset(runner_contract.keys())
    assert runner_contract["lab_id"] == "sensel-caldera-linux-lab"
    assert runner_contract["live_execution"]["default"] is False
    methods = runner_contract["supported_methods"]
    for name in ("prepare", "execute_template", "collect_evidence", "reset", "teardown"):
        assert name in methods


def test_safe_template_matches_contract(runner_contract: dict, safe_template: dict) -> None:
    assert safe_template["template_id"] in runner_contract["allowlisted_templates"]
    assert safe_template["lab_id"] == runner_contract["lab_id"]
    assert safe_template["dry_run_default"] is True
    assert "forbidden" in safe_template
