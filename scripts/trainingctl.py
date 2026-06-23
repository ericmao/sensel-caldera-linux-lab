#!/usr/bin/env python3
"""SenseL Caldera Linux Lab control CLI."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = ROOT / "training/scenarios/SEN-APT29-LNX-01-safe-discovery.yaml"
REPORT_JSON = ROOT / "reports/SEN-APT29-LNX-01-correlation.json"
REPORT_MD = ROOT / "reports/SEN-APT29-LNX-01-summary.md"
ALLOWED_ABILITIES = {
    "SEN-LNX-001",
    "SEN-LNX-002",
    "SEN-LNX-003",
    "SEN-LNX-004",
}
ALLOWED_TARGET = "caldera-linux-target-01"
ALLOWED_TENANT = "castle-train-01"


def load_scenario() -> dict:
    return yaml.safe_load(SCENARIO_PATH.read_text(encoding="utf-8"))


def run_compose(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    return subprocess.run(
        ["docker", "compose", *args],
        cwd=ROOT,
        env=env,
        check=check,
        text=True,
        capture_output=not check,
    )


def cmd_validate(_: argparse.Namespace) -> int:
    scenario = load_scenario()
    errors: list[str] = []

    if scenario.get("tenant_id") != ALLOWED_TENANT:
        errors.append(f"tenant_id must be {ALLOWED_TENANT}")
    if scenario.get("target") != ALLOWED_TARGET:
        errors.append(f"target must be {ALLOWED_TARGET}")
    if scenario.get("group") != ALLOWED_TENANT:
        errors.append(f"group must be {ALLOWED_TENANT}")

    abilities = scenario.get("abilities") or []
    for ability in abilities:
        if ability not in ALLOWED_ABILITIES:
            errors.append(f"ability not allowlisted: {ability}")

    if errors:
        for err in errors:
            print(f"VALIDATION ERROR: {err}", file=sys.stderr)
        return 1

    print("Validation passed")
    return 0


def cmd_up(_: argparse.Namespace) -> int:
    run_compose(["up", "-d", "--build"])
    return 0


def cmd_down(_: argparse.Namespace) -> int:
    run_compose(["down"])
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    result = run_compose(["ps"], check=False)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def cmd_deploy_agent(_: argparse.Namespace) -> int:
    result = run_compose(
        ["exec", "-T", "target-linux", "/opt/sensel/scripts/bootstrap-sandcat.sh"],
        check=False,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def cmd_run_manual(_: argparse.Namespace) -> int:
    scenario = load_scenario()
    steps = [
        "Manual Caldera UI operation steps (instructor-led)",
        "========================================",
        "",
        "1. Open http://127.0.0.1:8888 and login (default: red / admin).",
        "2. Navigate to Campaigns -> Adversary Profiles -> + New Profile.",
        f"3. Name the profile '{scenario['title']}' and add abilities in order:",
    ]
    for idx, ability in enumerate(scenario["abilities"], start=1):
        steps.append(f"   {idx}. {ability}")
    steps.extend(
        [
            "4. Go to Agents and confirm target-linux Sandcat agent is online (group castle-train-01).",
            "5. Start a new Operation:",
            "   - Select the adversary profile created above",
            "   - Select the target-linux Sandcat agent",
            f"   - Group: {scenario['group']}",
            "6. Run the operation and wait for all four abilities to complete.",
            "7. Export the operation report JSON from Debrief or operation details.",
            "8. Run correlation:",
            "   python3 scripts/trainingctl.py correlate \\",
            "     --operation-report /path/to/operation-report.json \\",
            "     --wazuh-alerts fixtures/wazuh-alerts.ndjson",
            "",
            "Note: this command does NOT invoke Caldera APIs automatically.",
        ]
    )
    print("\n".join(steps))
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    source = Path(args.source)
    if not source.exists():
        print(f"Source not found: {source}", file=sys.stderr)
        return 1
    out = ROOT / "reports/collected-wazuh-alerts.ndjson"
    out.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Collected alerts written to {out}")
    return 0


def cmd_correlate(args: argparse.Namespace) -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from correlate import build_summary, correlate, load_ndjson

    operation_report = json.loads(Path(args.operation_report).read_text(encoding="utf-8"))
    wazuh_alerts = load_ndjson(Path(args.wazuh_alerts))
    tenant_id = args.tenant_id or ALLOWED_TENANT
    hostname = args.hostname or ALLOWED_TARGET
    window = int(args.time_window or os.environ.get("CORRELATION_TIME_WINDOW_SEC", "300"))

    result = correlate(operation_report, wazuh_alerts, tenant_id, hostname, window)
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    REPORT_MD.write_text(build_summary(result), encoding="utf-8")
    print(f"Wrote {REPORT_JSON}")
    print(f"Wrote {REPORT_MD}")
    return 0


def cmd_cleanup(_: argparse.Namespace) -> int:
    run_compose(
        [
            "exec",
            "-T",
            "target-linux",
            "bash",
            "-lc",
            "rm -rf /tmp/sensel-training-staging/*; pkill -f /opt/sensel/sandcat || true",
        ],
        check=False,
    )
    print("Cleanup completed (staging cleared, sandcat stopped; marker log preserved)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SenseL Caldera Linux Lab CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")
    sub.add_parser("up")
    sub.add_parser("down")
    sub.add_parser("status")
    sub.add_parser("deploy-agent")
    sub.add_parser("run-manual")

    collect = sub.add_parser("collect")
    collect.add_argument("--source", default=str(ROOT / "fixtures/wazuh-alerts.ndjson"))
    collect.add_argument("--fixture", action="store_true", help="Use default fixture")

    corr = sub.add_parser("correlate")
    corr.add_argument(
        "--operation-report",
        default=str(ROOT / "fixtures/caldera-operation-report.sample.json"),
    )
    corr.add_argument("--wazuh-alerts", default=str(ROOT / "fixtures/wazuh-alerts.ndjson"))
    corr.add_argument("--tenant-id", default=ALLOWED_TENANT)
    corr.add_argument("--hostname", default=ALLOWED_TARGET)
    corr.add_argument("--time-window", default=None)

    sub.add_parser("cleanup")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    handlers = {
        "validate": cmd_validate,
        "up": cmd_up,
        "down": cmd_down,
        "status": cmd_status,
        "deploy-agent": cmd_deploy_agent,
        "run-manual": cmd_run_manual,
        "collect": cmd_collect,
        "correlate": cmd_correlate,
        "cleanup": cmd_cleanup,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
