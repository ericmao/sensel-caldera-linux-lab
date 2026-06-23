import json
from pathlib import Path


def test_wazuh_fixture_coverage(root: Path) -> None:
    fixture = root / "fixtures/wazuh-alerts.ndjson"
    lines = [line for line in fixture.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 4

    rule_ids = set()
    scenario_ids = set()
    for line in lines:
        alert = json.loads(line)
        rule_ids.add(int(alert["rule"]["id"]))
        scenario_ids.add(alert["data"]["scenario_id"])

    assert rule_ids == {100610, 100611, 100612, 100613}
    assert scenario_ids == {"SEN-LNX-001", "SEN-LNX-002", "SEN-LNX-003", "SEN-LNX-004"}


def test_wazuh_test_events_exist(root: Path) -> None:
    events_dir = root / "wazuh/manager/test-events"
    for idx in range(1, 5):
        path = events_dir / f"sen-lnx-00{idx}.json"
        assert path.exists()
