import json
import subprocess
import sys
from pathlib import Path


def test_correlation_output(root: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/trainingctl.py"),
            "correlate",
            "--operation-report",
            str(root / "fixtures/caldera-operation-report.sample.json"),
            "--wazuh-alerts",
            str(root / "fixtures/wazuh-alerts.ndjson"),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    report = json.loads((root / "reports/SEN-APT29-LNX-01-correlation.json").read_text(encoding="utf-8"))
    assert report["tenant_id"] == "castle-train-01"
    assert report["hostname"] == "caldera-linux-target-01"
    assert len(report["correlations"]) == 4
    assert all(item["correlation_status"] == "matched" for item in report["correlations"])
    assert (root / "reports/SEN-APT29-LNX-01-summary.md").exists()


def test_chain_c_correlation_output(root: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/trainingctl.py"),
            "correlate",
            "--scenario",
            "SEN-APT29-LNX-04",
            "--operation-report",
            str(root / "fixtures/caldera-operation-report.chain-c.sample.json"),
            "--wazuh-alerts",
            str(root / "fixtures/wazuh-alerts-chain-c.ndjson"),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    report = json.loads((root / "reports/SEN-APT29-LNX-04-correlation.json").read_text(encoding="utf-8"))
    assert report["tenant_id"] == "castle-train-01"
    assert set(report["hostnames"]) == {"caldera-linux-target-01", "caldera-linux-target-02"}
    assert len(report["correlations"]) == 8
    assert all(item["correlation_status"] == "matched" for item in report["correlations"])
    assert (root / "reports/SEN-APT29-LNX-04-summary.md").exists()
