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
SCENARIO_FILES = {
    "SEN-APT29-LNX-01": ROOT / "training/scenarios/SEN-APT29-LNX-01-safe-discovery.yaml",
    "SEN-APT29-LNX-02": ROOT / "training/scenarios/SEN-APT29-LNX-02-staging-archive.yaml",
    "SEN-APT29-LNX-03": ROOT / "training/scenarios/SEN-APT29-LNX-03-collection-exfil-sim.yaml",
    "SEN-APT29-LNX-04": ROOT / "training/scenarios/SEN-APT29-LNX-04-simulated-lateral.yaml",
}
DEFAULT_SCENARIO = "SEN-APT29-LNX-01"
ALLOWED_ABILITIES = {f"SEN-LNX-{idx:03d}" for idx in range(1, 20)}
ALLOWED_TARGETS = {
    "caldera-linux-target-01",
    "caldera-linux-target-02",
}
ALLOWED_TARGET = "caldera-linux-target-01"
ALLOWED_TENANT = "castle-train-01"
TARGET_SERVICES = ("target-linux", "target-linux-02")
CLEANUP_CMD = (
    "rm -rf /tmp/sensel-training-staging /tmp/sensel-staging.tar.gz /tmp/sensel-staging-tier2.tar.gz "
    "/tmp/sensel-auto-collect /tmp/sensel-exfil-sim.json /tmp/sensel-exfil-sim-tier2.json "
    "/tmp/sensel-lateral-plan.json /tmp/sensel-discovery-*.txt; "
    "pkill -f /opt/sensel/sandcat || true"
)


def load_scenario(scenario_id: str = DEFAULT_SCENARIO) -> dict:
    path = SCENARIO_FILES.get(scenario_id)
    if not path or not path.exists():
        raise ValueError(f"unknown scenario: {scenario_id}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_scenario(scenario: dict) -> list[str]:
    errors: list[str] = []
    if scenario.get("tenant_id") != ALLOWED_TENANT:
        errors.append(f"tenant_id must be {ALLOWED_TENANT}")
    targets = scenario.get("targets") or [scenario.get("target")]
    if not targets or any(target not in ALLOWED_TARGETS for target in targets):
        errors.append(f"targets must be subset of {sorted(ALLOWED_TARGETS)}")
    if scenario.get("target") and scenario.get("target") not in targets:
        errors.append("target must be included in targets")
    if scenario.get("group") != ALLOWED_TENANT:
        errors.append(f"group must be {ALLOWED_TENANT}")

    abilities = scenario.get("abilities") or []
    if len(abilities) < 4:
        errors.append("scenario must include at least four abilities")
    for ability in abilities:
        if ability not in ALLOWED_ABILITIES:
            errors.append(f"ability not allowlisted: {ability}")

    expected_rules = scenario.get("expected_wazuh_rule_ids") or []
    if len(expected_rules) != len(abilities):
        errors.append("expected_wazuh_rule_ids must match abilities count")

    return errors


def report_paths(scenario_id: str) -> tuple[Path, Path]:
    report_json = ROOT / f"reports/{scenario_id}-correlation.json"
    report_md = ROOT / f"reports/{scenario_id}-summary.md"
    return report_json, report_md


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


def cmd_validate(args: argparse.Namespace) -> int:
    scenario_ids = SCENARIO_FILES if args.scenario == "all" else {args.scenario: SCENARIO_FILES[args.scenario]}
    errors: list[str] = []
    for scenario_id, path in scenario_ids.items():
        if not path.exists():
            errors.append(f"missing scenario file for {scenario_id}")
            continue
        scenario = yaml.safe_load(path.read_text(encoding="utf-8"))
        for err in validate_scenario(scenario):
            errors.append(f"{scenario_id}: {err}")

    if errors:
        for err in errors:
            print(f"VALIDATION ERROR: {err}", file=sys.stderr)
        return 1

    print(f"Validation passed ({len(scenario_ids)} scenario(s))")
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
    rc = 0
    for service in TARGET_SERVICES:
        result = run_compose(
            ["exec", "-T", service, "/opt/sensel/scripts/bootstrap-sandcat.sh"],
            check=False,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        rc = rc or result.returncode
    return rc


def cmd_run_manual(args: argparse.Namespace) -> int:
    scenario = load_scenario(args.scenario)
    profile = scenario.get("adversary_profile") or scenario["title"]
    steps = [
        "Manual Caldera UI operation steps (instructor-led)",
        "========================================",
        "",
        f"Scenario: {scenario['id']} — {scenario['title']}",
        "",
        "1. Open http://127.0.0.1:8888 and login (default: red / admin).",
        "2. Navigate to Campaigns -> Adversary Profiles -> + New Profile.",
        f"3. Name the profile '{profile}' and add abilities in order:",
    ]
    for idx, ability in enumerate(scenario["abilities"], start=1):
        steps.append(f"   {idx}. {ability}")

    targets = scenario.get("targets") or [scenario.get("target")]
    agent_note = (
        "4. Go to Agents and confirm BOTH Sandcat agents are online "
        f"({', '.join(targets)}, group castle-train-01)."
        if len(targets) > 1
        else "4. Go to Agents and confirm target-linux Sandcat agent is online (group castle-train-01)."
    )
    agent_select = (
        "   - Select BOTH target-linux agents (NOT ad-hoc empty profile)"
        if len(targets) > 1
        else "   - Select the target-linux Sandcat agent"
    )

    steps.extend(
        [
            agent_note,
            "5. Start a new Operation:",
            f"   - Adversary profile: {profile} (NOT ad-hoc empty profile)",
            agent_select,
            f"   - Group: {scenario['group']}",
            "   - Autonomous: ON",
            f"6. Run the operation and wait for all {len(scenario['abilities'])} abilities to complete.",
            "7. Export the operation report JSON from Debrief or operation details.",
            "8. Run correlation:",
            "   python3 scripts/trainingctl.py correlate \\",
            f"     --scenario {scenario['id']} \\",
            "     --operation-report /path/to/operation-report.json \\",
            (
                "     --wazuh-alerts fixtures/wazuh-alerts-chain-c.ndjson"
                if scenario["id"] == "SEN-APT29-LNX-04"
                else "     --wazuh-alerts fixtures/wazuh-alerts.ndjson"
            ),
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

    scenario_id = args.scenario
    operation_report = json.loads(Path(args.operation_report).read_text(encoding="utf-8"))
    wazuh_alerts = load_ndjson(Path(args.wazuh_alerts))
    tenant_id = args.tenant_id or ALLOWED_TENANT
    hostname = args.hostname or ALLOWED_TARGET
    window = int(args.time_window or os.environ.get("CORRELATION_TIME_WINDOW_SEC", "300"))

    result = correlate(
        operation_report,
        wazuh_alerts,
        tenant_id,
        hostname,
        window,
        scenario_id=scenario_id,
    )
    report_json, report_md = report_paths(scenario_id)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    report_md.write_text(build_summary(result), encoding="utf-8")
    print(f"Wrote {report_json}")
    print(f"Wrote {report_md}")
    return 0


def cmd_cleanup(_: argparse.Namespace) -> int:
    for service in TARGET_SERVICES:
        run_compose(
            [
                "exec",
                "-T",
                service,
                "bash",
                "-lc",
                CLEANUP_CMD,
            ],
            check=False,
        )
    print("Cleanup completed on all targets (artifacts cleared, sandcat stopped; marker logs preserved)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SenseL Caldera Linux Lab CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument(
        "--scenario",
        choices=[*SCENARIO_FILES.keys(), "all"],
        default="all",
    )

    sub.add_parser("up")
    sub.add_parser("down")
    sub.add_parser("status")
    sub.add_parser("deploy-agent")

    run_manual = sub.add_parser("run-manual")
    run_manual.add_argument("--scenario", choices=SCENARIO_FILES.keys(), default=DEFAULT_SCENARIO)

    collect = sub.add_parser("collect")
    collect.add_argument("--source", default=str(ROOT / "fixtures/wazuh-alerts.ndjson"))
    collect.add_argument("--fixture", action="store_true", help="Use default fixture")

    corr = sub.add_parser("correlate")
    corr.add_argument("--scenario", choices=SCENARIO_FILES.keys(), default=DEFAULT_SCENARIO)
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
