from pathlib import Path

ALLOWED = {"SEN-LNX-001", "SEN-LNX-002", "SEN-LNX-003", "SEN-LNX-004"}


def test_ability_allowlist(root: Path) -> None:
    ability_dir = root / "caldera-plugin-sensel/data/abilities/sensel-linux"
    files = sorted(p.stem for p in ability_dir.glob("SEN-LNX-*.yml"))
    assert set(files) == ALLOWED
    assert len(files) == 4


def test_abilities_do_not_reference_sensitive_paths(root: Path) -> None:
    ability_dir = root / "caldera-plugin-sensel/data/abilities/sensel-linux"
    banned = ["/etc/shadow", "id_rsa", "mimikatz", "curl http", "wget "]
    for path in ability_dir.glob("*.yml"):
        content = path.read_text(encoding="utf-8").lower()
        for token in banned:
            assert token not in content, f"{path.name} contains banned token {token}"
