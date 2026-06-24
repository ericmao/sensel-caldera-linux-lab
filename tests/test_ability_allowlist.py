from pathlib import Path

import yaml

ALLOWED = {f"SEN-LNX-{idx:03d}" for idx in range(1, 20)}


def test_ability_allowlist(root: Path) -> None:
    ability_dir = root / "caldera-plugin-sensel/data/abilities/sensel-linux"
    files = sorted(p.stem for p in ability_dir.glob("SEN-LNX-*.yml"))
    assert set(files) == ALLOWED
    assert len(files) == 19


def _load_ability_commands(root: Path) -> list[tuple[str, str]]:
    ability_dir = root / "caldera-plugin-sensel/data/abilities/sensel-linux"
    commands: list[tuple[str, str]] = []
    for path in sorted(ability_dir.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        command = data[0]["platforms"]["linux"]["sh"]["command"]
        commands.append((path.name, command))
    return commands


def test_ability_yaml_parses(root: Path) -> None:
    for name, command in _load_ability_commands(root):
        assert command.strip(), f"{name} must define a sh command"


def test_ability_commands_are_single_line(root: Path) -> None:
    for name, command in _load_ability_commands(root):
        assert "\n" not in command.strip(), f"{name} sh command must be single-line for Caldera sh executor"
        assert ";" in command, f"{name} command should use semicolon separators"


def test_abilities_do_not_reference_sensitive_paths(root: Path) -> None:
    ability_dir = root / "caldera-plugin-sensel/data/abilities/sensel-linux"
    banned = ["/etc/shadow", "id_rsa", "mimikatz", "curl http", "wget "]
    for path in ability_dir.glob("*.yml"):
        content = path.read_text(encoding="utf-8").lower()
        for token in banned:
            assert token not in content, f"{path.name} contains banned token {token}"
