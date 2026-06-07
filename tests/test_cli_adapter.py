from __future__ import annotations

from pathlib import Path

from skills.core import Core


def test_cli_routes_lifecycle_through_manager(tmp_path: Path, make_skill, capsys) -> None:
    source = tmp_path / "source"
    make_skill(source, "shell-tools", "Prefer safe commands.")
    core = Core()

    add_code = core.main(["-C", str(tmp_path), "add", str(source), "--copy"])
    use_code = core.main(["-C", str(tmp_path), "use", "shell-tools"])
    installed_code = core.main(["-C", str(tmp_path), "installed"])
    remove_code = core.main(["-C", str(tmp_path), "remove", "shell-tools"])

    output = capsys.readouterr().out
    assert add_code == 0
    assert use_code == 0
    assert installed_code == 0
    assert remove_code == 0
    assert "shell-tools ->" in output
    assert "Prefer safe commands." in output
    assert "shell-tools" in output


def test_cli_init_and_parse_are_manager_backed(tmp_path: Path, capsys) -> None:
    core = Core()

    init_code = core.main(["-C", str(tmp_path), "init", "example-skill", "--description", "Example."])
    parse_code = core.main(["-C", str(tmp_path), "parse", "gh:openai/skills@main"])

    output = capsys.readouterr().out
    assert init_code == 0
    assert parse_code == 0
    assert (tmp_path / "example-skill" / "SKILL.md").exists()
    assert "kind = git" in output
