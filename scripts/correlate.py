"""Correlation logic for Caldera operation reports and Wazuh alerts."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCENARIO_TO_RULE = {
    "SEN-LNX-001": 100610,
    "SEN-LNX-002": 100611,
    "SEN-LNX-003": 100612,
    "SEN-LNX-004": 100613,
}

ABILITY_NAME_TO_SCENARIO = {
    "SEN-LNX-001 Local Account Discovery": "SEN-LNX-001",
    "SEN-LNX-002 Network Configuration Discovery": "SEN-LNX-002",
    "SEN-LNX-003 Process Discovery": "SEN-LNX-003",
    "SEN-LNX-004 Synthetic Data Staging": "SEN-LNX-004",
}


def parse_ts(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def load_ndjson(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            items.append(json.loads(line))
    return items


def scenario_from_chain_link(link: dict[str, Any]) -> str | None:
    name = link.get("ability_name", "")
    if name in ABILITY_NAME_TO_SCENARIO:
        return ABILITY_NAME_TO_SCENARIO[name]
    match = re.search(r"(SEN-LNX-\d{3})", name)
    return match.group(1) if match else None


def correlate(
    operation_report: dict[str, Any],
    wazuh_alerts: list[dict[str, Any]],
    tenant_id: str,
    hostname: str,
    time_window_sec: int = 300,
) -> dict[str, Any]:
    operation = operation_report.get("operation", {})
    operation_id = operation.get("id")
    chain = operation_report.get("chain", [])

    correlations: list[dict[str, Any]] = []
    for link in chain:
        scenario_id = scenario_from_chain_link(link)
        if not scenario_id:
            continue
        finish_raw = link.get("finish")
        if not finish_raw:
            continue
        finish_ts = parse_ts(finish_raw)
        window_start = finish_ts - timedelta(seconds=time_window_sec)
        window_end = finish_ts + timedelta(seconds=time_window_sec)

        matched_alerts = []
        technique_id = None
        for alert in wazuh_alerts:
            alert_ts_raw = alert.get("timestamp") or alert.get("@timestamp")
            if not alert_ts_raw:
                continue
            alert_ts = parse_ts(str(alert_ts_raw))
            data = alert.get("data") or {}
            alert_scenario = data.get("scenario_id")
            alert_tenant = data.get("tenant_id")
            alert_host = (alert.get("agent") or {}).get("name")
            if alert_scenario != scenario_id:
                continue
            if alert_tenant != tenant_id:
                continue
            if alert_host and alert_host != hostname:
                continue
            if not (window_start <= alert_ts <= window_end):
                continue
            technique_id = data.get("technique_id")
            matched_alerts.append(alert)

        correlations.append(
            {
                "scenario_id": scenario_id,
                "technique_id": technique_id,
                "operation_id": operation_id,
                "caldera_run_id": operation_id,
                "tenant_id": tenant_id,
                "hostname": hostname,
                "caldera_finish": finish_raw,
                "expected_wazuh_rule_id": SCENARIO_TO_RULE.get(scenario_id),
                "matched_wazuh_alerts": matched_alerts,
                "correlation_status": "matched" if matched_alerts else "unmatched",
            }
        )

    return {
        "scenario_id": "SEN-APT29-LNX-01",
        "tenant_id": tenant_id,
        "hostname": hostname,
        "operation_id": operation_id,
        "time_window_sec": time_window_sec,
        "correlations": correlations,
    }


def build_summary(correlation: dict[str, Any]) -> str:
    lines = [
        "# SEN-APT29-LNX-01 Correlation Summary",
        "",
        f"- Tenant: `{correlation['tenant_id']}`",
        f"- Host: `{correlation['hostname']}`",
        f"- Operation ID: `{correlation.get('operation_id')}`",
        f"- Time window: `{correlation['time_window_sec']}s`",
        "",
        "## Results",
    ]
    for item in correlation["correlations"]:
        status = item["correlation_status"]
        rule = item.get("expected_wazuh_rule_id")
        lines.append(
            f"- `{item['scenario_id']}` -> {status} (expected rule {rule}, "
            f"alerts matched: {len(item['matched_wazuh_alerts'])})"
        )
    return "\n".join(lines) + "\n"
