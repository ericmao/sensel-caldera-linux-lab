from pathlib import Path

import pytest
import yaml

SCENARIO_FILES = [
    "SEN-APT29-LNX-01-safe-discovery.yaml",
    "SEN-APT29-LNX-02-staging-archive.yaml",
    "SEN-APT29-LNX-03-collection-exfil-sim.yaml",
    "SEN-APT29-LNX-04-simulated-lateral.yaml",
    "SEN-NDR-LNX-01-ndr-gateway.yaml",
]

SCENARIO_EXPECTATIONS = {
    "SEN-APT29-LNX-01": {"abilities": 4, "min_abilities": 4},
    "SEN-APT29-LNX-02": {"abilities": 6, "min_abilities": 6},
    "SEN-APT29-LNX-03": {"abilities": 6, "min_abilities": 6},
    "SEN-APT29-LNX-04": {"abilities": 8, "min_abilities": 8},
    "SEN-NDR-LNX-01": {"abilities": 5, "min_abilities": 5},
}


@pytest.fixture(params=SCENARIO_FILES)
def scenario_path(root: Path, request) -> Path:
    return root / "training/scenarios" / request.param


@pytest.fixture
def scenario(scenario_path: Path) -> dict:
    return yaml.safe_load(scenario_path.read_text(encoding="utf-8"))


def test_scenario_yaml_schema(scenario: dict) -> None:
    required = {
        "id",
        "title",
        "adversary_profile",
        "group",
        "target",
        "tenant_id",
        "timeout_minutes",
        "abilities",
        "expected_wazuh_rule_ids",
        "cleanup",
        "prohibited",
    }
    assert required.issubset(scenario.keys())
    expected = SCENARIO_EXPECTATIONS[scenario["id"]]
    assert len(scenario["abilities"]) == expected["abilities"]
    assert len(scenario["expected_wazuh_rule_ids"]) == expected["abilities"]


def test_scenario_ability_files_exist(root: Path, scenario: dict) -> None:
    ability_root = root / "caldera-plugin-sensel/data/abilities"
    for ability in scenario["abilities"]:
        matches = list(ability_root.rglob(f"{ability}.yml"))
        assert len(matches) == 1, f"expected one ability file for {ability}, found {len(matches)}"
        path = matches[0]

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert data[0]["technique"]["attack_id"]
