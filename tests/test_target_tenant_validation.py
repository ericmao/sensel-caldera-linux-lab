import subprocess
import sys
from pathlib import Path


def test_trainingctl_validate_passes(root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/trainingctl.py"), "validate"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_scenario_target_and_tenant(scenario: dict) -> None:
    assert scenario["tenant_id"] == "castle-train-01"
    assert scenario["target"] == "caldera-linux-target-01"
    assert scenario["group"] == "castle-train-01"
