"""Validate AVL manual live smoke contract (Phase 2B)."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "avlbench-adapter"


@pytest.fixture
def manual_live_config() -> dict:
    path = ADAPTER / "manual_live_smoke.yaml"
    assert path.is_file(), "manual_live_smoke.yaml must exist"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_manual_live_smoke_schema(manual_live_config: dict) -> None:
    required = {
        "phase",
        "lab_id",
        "allowlisted_templates",
        "allowlisted_training_scenarios",
        "allowlisted_targets",
        "allowlisted_networks",
        "required_env",
        "allowlisted_manual_steps",
        "expected_artifacts",
        "safety",
    }
    assert required.issubset(manual_live_config.keys())
    assert manual_live_config["safety"]["api_auto_execution"] is False
    assert manual_live_config["required_env"]["manual_confirm"] == (
        "AVL_LAB_RUNNER_MANUAL_CONFIRM=I_UNDERSTAND_THIS_RUNS_LOCAL_LAB"
    )


def test_manual_live_steps_subset_of_allowlist(manual_live_config: dict) -> None:
    allowlisted = set(manual_live_config["allowlisted_manual_steps"])
    step_ids = {step["step_id"] for step in manual_live_config["manual_steps"]}
    assert step_ids.issubset(allowlisted)


def test_training_scenarios_exist_on_disk(manual_live_config: dict) -> None:
    for item in manual_live_config["allowlisted_training_scenarios"]:
        yaml_rel = item["yaml"]
        path = ROOT / yaml_rel
        assert path.is_file(), f"missing training scenario file: {yaml_rel}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["id"] == item["id"]
