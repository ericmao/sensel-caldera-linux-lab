#!/usr/bin/env python3
"""Correlate Phase 3 assessment JSON with Wazuh alerts (Layer C for external targets)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


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


def correlate_phase3(
    assessment: dict[str, Any],
    wazuh_alerts: list[dict[str, Any]],
    time_window_sec: int = 300,
) -> dict[str, Any]:
    tenant_id = assessment["tenant_id"]
    target_host = assessment["target"]["host"]
    assessed_at = parse_ts(assessment["assessed_at"])

    correlations: list[dict[str, Any]] = []
    for finding in assessment.get("findings", []):
        finding_id = finding["finding_id"]
        expected_rule = finding.get("expected_wazuh_rule_id")
        window_start = assessed_at - timedelta(seconds=time_window_sec)
        window_end = assessed_at + timedelta(seconds=time_window_sec)

        matched = []
        for alert in wazuh_alerts:
            data = alert.get("data") or {}
            if data.get("finding_id") != finding_id:
                continue
            if data.get("tenant_id") != tenant_id:
                continue
            if data.get("target_host") and data.get("target_host") != target_host:
                continue
            ts_raw = alert.get("timestamp") or alert.get("@timestamp")
            if ts_raw:
                alert_ts = parse_ts(str(ts_raw))
                if not (window_start <= alert_ts <= window_end):
                    continue
            matched.append(alert)

        correlations.append(
            {
                "finding_id": finding_id,
                "severity": finding.get("severity"),
                "technique_id": finding.get("technique_id"),
                "expected_wazuh_rule_id": expected_rule,
                "matched_wazuh_alerts": matched,
                "correlation_status": "matched" if matched else "unmatched",
            }
        )

    matched_count = sum(1 for c in correlations if c["correlation_status"] == "matched")
    return {
        "scenario_id": assessment["scenario_id"],
        "tenant_id": tenant_id,
        "target_host": target_host,
        "time_window_sec": time_window_sec,
        "findings_total": len(correlations),
        "findings_matched": matched_count,
        "correlations": correlations,
    }


def build_summary(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['scenario_id']} Phase 3 Correlation Summary",
        "",
        f"- Tenant: `{result['tenant_id']}`",
        f"- Target host: `{result['target_host']}`",
        f"- Time window: `{result['time_window_sec']}s`",
        f"- Matched: **{result['findings_matched']}/{result['findings_total']}**",
        "",
        "## Results",
    ]
    for item in result["correlations"]:
        lines.append(
            f"- `{item['finding_id']}` ({item.get('severity')}) -> "
            f"{item['correlation_status']} (rule {item.get('expected_wazuh_rule_id')}, "
            f"alerts: {len(item['matched_wazuh_alerts'])})"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Correlate Phase 3 assessment with Wazuh alerts")
    parser.add_argument(
        "--assessment",
        default=str(ROOT / "reports/SEN-PHASE3-LW170-assessment.json"),
    )
    parser.add_argument(
        "--wazuh-alerts",
        default=str(ROOT / "fixtures/wazuh-alerts-phase3-livewire.ndjson"),
    )
    parser.add_argument("--time-window", type=int, default=3600)
    args = parser.parse_args()

    assessment = json.loads(Path(args.assessment).read_text(encoding="utf-8"))
    alerts = load_ndjson(Path(args.wazuh_alerts))
    result = correlate_phase3(assessment, alerts, time_window_sec=args.time_window)

    out_json = ROOT / f"reports/{result['scenario_id']}-correlation.json"
    out_md = ROOT / f"reports/{result['scenario_id']}-correlation-summary.md"
    out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(build_summary(result), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
