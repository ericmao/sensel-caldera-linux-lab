#!/usr/bin/env python3
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
    "SEN-LNX-005": 100614,
    "SEN-LNX-006": 100615,
    "SEN-LNX-007": 100616,
    "SEN-LNX-008": 100617,
    "SEN-LNX-009": 100618,
    "SEN-LNX-010": 100619,
    "SEN-LNX-011": 100620,
    "SEN-LNX-012": 100627,
    "SEN-LNX-013": 100628,
    "SEN-LNX-014": 100629,
    "SEN-LNX-015": 100630,
    "SEN-LNX-016": 100631,
    "SEN-LNX-017": 100632,
    "SEN-LNX-018": 100633,
    "SEN-LNX-019": 100634,
}

ABILITY_NAME_TO_SCENARIO = {
    "SEN-LNX-001 Local Account Discovery": "SEN-LNX-001",
    "SEN-LNX-002 Network Configuration Discovery": "SEN-LNX-002",
    "SEN-LNX-003 Process Discovery": "SEN-LNX-003",
    "SEN-LNX-004 Synthetic Data Staging": "SEN-LNX-004",
    "SEN-LNX-005 System Information Discovery": "SEN-LNX-005",
    "SEN-LNX-006 File and Directory Discovery": "SEN-LNX-006",
    "SEN-LNX-007 Archive Staged Collection": "SEN-LNX-007",
    "SEN-LNX-008 System Owner User Discovery": "SEN-LNX-008",
    "SEN-LNX-009 System Service Discovery": "SEN-LNX-009",
    "SEN-LNX-010 Automated Collection": "SEN-LNX-010",
    "SEN-LNX-011 Simulated Exfil Size Check": "SEN-LNX-011",
    "SEN-LNX-012 Remote System Discovery": "SEN-LNX-012",
    "SEN-LNX-013 Remote Service Discovery": "SEN-LNX-013",
    "SEN-LNX-014 Simulated Lateral Plan": "SEN-LNX-014",
    "SEN-LNX-015 Tier2 System Information Discovery": "SEN-LNX-015",
    "SEN-LNX-016 Tier2 File and Directory Discovery": "SEN-LNX-016",
    "SEN-LNX-017 Tier2 Synthetic Data Staging": "SEN-LNX-017",
    "SEN-LNX-018 Tier2 Archive Staged Collection": "SEN-LNX-018",
    "SEN-LNX-019 Tier2 Simulated Exfil Size Check": "SEN-LNX-019",
}

ABILITY_TO_HOST = {
    "SEN-LNX-012": "caldera-linux-target-01",
    "SEN-LNX-013": "caldera-linux-target-01",
    "SEN-LNX-014": "caldera-linux-target-01",
    "SEN-LNX-015": "caldera-linux-target-02",
    "SEN-LNX-016": "caldera-linux-target-02",
    "SEN-LNX-017": "caldera-linux-target-02",
    "SEN-LNX-018": "caldera-linux-target-02",
    "SEN-LNX-019": "caldera-linux-target-02",
}

DEFAULT_SURICATA_EXPECTATIONS: dict[str, dict[str, list[int]]] = {
    "SEN-LNX-012": {"required": [], "optional": [9000010]},
    "SEN-LNX-013": {"required": [9000020], "optional": [9000010]},
    "SEN-LNX-014": {"required": [], "optional": [9000010]},
    "SEN-LNX-015": {"required": [], "optional": [9000010]},
    "SEN-LNX-016": {"required": [], "optional": [9000010]},
    "SEN-LNX-017": {"required": [], "optional": [9000010, 9000012]},
    "SEN-LNX-018": {"required": [], "optional": [9000010, 9000012]},
    "SEN-LNX-019": {"required": [], "optional": [9000010, 9000012]},
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


def hostname_from_paw(operation_report: dict[str, Any], paw: str | None) -> str | None:
    if not paw:
        return None
    host_group = operation_report.get("operation", {}).get("host_group", {})
    for hostname, info in host_group.items():
        if info.get("paw") == paw:
            return hostname
    return None


def expected_hostname(
    ability_scenario: str,
    link: dict[str, Any],
    operation_report: dict[str, Any],
    default_hostname: str,
) -> str:
    if ability_scenario in ABILITY_TO_HOST:
        return ABILITY_TO_HOST[ability_scenario]
    paw_host = hostname_from_paw(operation_report, link.get("paw"))
    return paw_host or default_hostname


def alert_signature_id(alert: dict[str, Any]) -> int | None:
    nested = alert.get("alert") or {}
    sid = nested.get("signature_id")
    if sid is not None:
        return int(sid)
    rule = alert.get("rule") or {}
    rid = rule.get("id")
    return int(rid) if rid is not None else None


def correlate_suricata(
    operation_report: dict[str, Any],
    suricata_alerts: list[dict[str, Any]],
    time_window_sec: int,
    expectations: dict[str, dict[str, list[int]]] | None = None,
    default_hostname: str = "caldera-linux-target-01",
) -> list[dict[str, Any]]:
    expectations = expectations or DEFAULT_SURICATA_EXPECTATIONS
    chain = operation_report.get("chain", [])
    correlations: list[dict[str, Any]] = []

    for link in chain:
        ability_scenario = scenario_from_chain_link(link)
        if not ability_scenario or ability_scenario not in expectations:
            continue
        finish_raw = link.get("finish")
        if not finish_raw:
            continue
        finish_ts = parse_ts(finish_raw)
        window_start = finish_ts - timedelta(seconds=time_window_sec)
        window_end = finish_ts + timedelta(seconds=time_window_sec)
        link_hostname = expected_hostname(ability_scenario, link, operation_report, default_hostname)
        spec = expectations[ability_scenario]
        required_sids = spec.get("required") or []
        optional_sids = spec.get("optional") or []

        matched_alerts: list[dict[str, Any]] = []
        matched_sids: set[int] = set()
        for alert in suricata_alerts:
            if alert.get("event_type") not in (None, "alert"):
                continue
            alert_ts_raw = alert.get("timestamp") or alert.get("@timestamp")
            if not alert_ts_raw:
                continue
            alert_ts = parse_ts(str(alert_ts_raw))
            if not (window_start <= alert_ts <= window_end):
                continue
            sid = alert_signature_id(alert)
            if sid is None:
                continue
            if sid not in required_sids and sid not in optional_sids:
                continue
            matched_alerts.append(alert)
            matched_sids.add(sid)

        missing_required = [sid for sid in required_sids if sid not in matched_sids]
        if missing_required:
            status = "unmatched"
        elif matched_sids.intersection(required_sids) or matched_sids.intersection(optional_sids):
            status = "matched"
        else:
            status = "unmatched"

        correlations.append(
            {
                "scenario_id": ability_scenario,
                "hostname": link_hostname,
                "caldera_finish": finish_raw,
                "required_suricata_sids": required_sids,
                "optional_suricata_sids": optional_sids,
                "matched_suricata_sids": sorted(matched_sids),
                "missing_required_suricata_sids": missing_required,
                "matched_suricata_alerts": matched_alerts,
                "suricata_correlation_status": status,
            }
        )

    return correlations


def correlate(
    operation_report: dict[str, Any],
    wazuh_alerts: list[dict[str, Any]],
    tenant_id: str,
    hostname: str,
    time_window_sec: int = 300,
    scenario_id: str = "SEN-APT29-LNX-01",
    suricata_alerts: list[dict[str, Any]] | None = None,
    suricata_expectations: dict[str, dict[str, list[int]]] | None = None,
) -> dict[str, Any]:
    operation = operation_report.get("operation", {})
    operation_id = operation.get("id")
    chain = operation_report.get("chain", [])
    hostnames = sorted(
        {
            expected_hostname(scenario_from_chain_link(link) or "", link, operation_report, hostname)
            for link in chain
            if scenario_from_chain_link(link)
        }
    )

    correlations: list[dict[str, Any]] = []
    for link in chain:
        ability_scenario = scenario_from_chain_link(link)
        if not ability_scenario:
            continue
        finish_raw = link.get("finish")
        if not finish_raw:
            continue
        finish_ts = parse_ts(finish_raw)
        window_start = finish_ts - timedelta(seconds=time_window_sec)
        window_end = finish_ts + timedelta(seconds=time_window_sec)
        link_hostname = expected_hostname(ability_scenario, link, operation_report, hostname)

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
            if alert_scenario != ability_scenario:
                continue
            if alert_tenant != tenant_id:
                continue
            if alert_host and alert_host != link_hostname:
                continue
            if not (window_start <= alert_ts <= window_end):
                continue
            technique_id = data.get("technique_id")
            matched_alerts.append(alert)

        correlations.append(
            {
                "scenario_id": ability_scenario,
                "technique_id": technique_id,
                "operation_id": operation_id,
                "caldera_run_id": operation_id,
                "tenant_id": tenant_id,
                "hostname": link_hostname,
                "caldera_finish": finish_raw,
                "expected_wazuh_rule_id": SCENARIO_TO_RULE.get(ability_scenario),
                "matched_wazuh_alerts": matched_alerts,
                "correlation_status": "matched" if matched_alerts else "unmatched",
            }
        )

    result: dict[str, Any] = {
        "scenario_id": scenario_id,
        "tenant_id": tenant_id,
        "hostname": hostname,
        "hostnames": hostnames or [hostname],
        "operation_id": operation_id,
        "time_window_sec": time_window_sec,
        "correlations": correlations,
    }
    if suricata_alerts is not None:
        result["suricata_correlations"] = correlate_suricata(
            operation_report,
            suricata_alerts,
            time_window_sec,
            suricata_expectations,
            hostname,
        )
    return result


def build_summary(correlation: dict[str, Any]) -> str:
    host_line = correlation.get("hostnames") or [correlation["hostname"]]
    lines = [
        f"# {correlation['scenario_id']} Correlation Summary",
        "",
        f"- Tenant: `{correlation['tenant_id']}`",
        f"- Host(s): `{', '.join(host_line)}`",
        f"- Operation ID: `{correlation.get('operation_id')}`",
        f"- Time window: `{correlation['time_window_sec']}s`",
        "",
        "## Results",
    ]
    for item in correlation["correlations"]:
        status = item["correlation_status"]
        rule = item.get("expected_wazuh_rule_id")
        lines.append(
            f"- `{item['scenario_id']}` on `{item['hostname']}` -> {status} "
            f"(expected rule {rule}, alerts matched: {len(item['matched_wazuh_alerts'])})"
        )

    suricata_items = correlation.get("suricata_correlations") or []
    if suricata_items:
        lines.extend(["", "## Suricata NDR"])
        for item in suricata_items:
            status = item["suricata_correlation_status"]
            required = item.get("required_suricata_sids") or []
            matched = item.get("matched_suricata_sids") or []
            lines.append(
                f"- `{item['scenario_id']}` on `{item['hostname']}` -> {status} "
                f"(required SIDs {required}, matched SIDs {matched})"
            )
    return "\n".join(lines) + "\n"
