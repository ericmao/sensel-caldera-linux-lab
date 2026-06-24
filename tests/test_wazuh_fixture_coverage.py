import json
from pathlib import Path


def test_wazuh_fixture_coverage(root: Path) -> None:
    fixture = root / "fixtures/wazuh-alerts.ndjson"
    lines = [line for line in fixture.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 11

    rule_ids = set()
    scenario_ids = set()
    for line in lines:
        alert = json.loads(line)
        rule_ids.add(int(alert["rule"]["id"]))
        scenario_ids.add(alert["data"]["scenario_id"])

    assert rule_ids == set(range(100610, 100621))
    assert scenario_ids == {f"SEN-LNX-{idx:03d}" for idx in range(1, 12)}


def test_wazuh_test_events_exist(root: Path) -> None:
    events_dir = root / "wazuh/manager/test-events"
    for idx in range(1, 20):
        path = events_dir / f"sen-lnx-{idx:03d}.json"
        assert path.exists()


def test_wazuh_chain_c_fixture_coverage(root: Path) -> None:
    fixture = root / "fixtures/wazuh-alerts-chain-c.ndjson"
    lines = [line for line in fixture.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 8

    rule_ids = set()
    scenario_ids = set()
    hosts = set()
    for line in lines:
        alert = json.loads(line)
        rule_ids.add(int(alert["rule"]["id"]))
        scenario_ids.add(alert["data"]["scenario_id"])
        hosts.add(alert["agent"]["name"])

    assert rule_ids == set(range(100627, 100635))
    assert scenario_ids == {f"SEN-LNX-{idx:03d}" for idx in range(12, 20)}
    assert hosts == {"caldera-linux-target-01", "caldera-linux-target-02"}
