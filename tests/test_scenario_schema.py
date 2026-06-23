from pathlib import Path

import yaml


def test_scenario_yaml_schema(scenario: dict) -> None:
    required = {
        "id",
        "title",
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
    assert scenario["id"] == "SEN-APT29-LNX-01"
    assert len(scenario["abilities"]) == 4
    assert len(scenario["expected_wazuh_rule_ids"]) == 4


def test_scenario_ability_files_exist(root: Path, scenario: dict) -> None:
    ability_dir = root / "caldera-plugin-sensel/data/abilities/sensel-linux"
    for ability in scenario["abilities"]:
        path = ability_dir / f"{ability}.yml"
        assert path.exists(), f"missing ability file {path}"

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert data[0]["technique"]["attack_id"]
