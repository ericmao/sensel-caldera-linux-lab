from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def scenario(root: Path) -> dict:
    path = root / "training/scenarios/SEN-APT29-LNX-01-safe-discovery.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))
