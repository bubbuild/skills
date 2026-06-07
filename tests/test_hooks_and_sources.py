from __future__ import annotations

from pathlib import Path

import pytest

from skills import SkillsManager


def test_builtin_source_parser_handles_supported_git_forms(tmp_path: Path) -> None:
    manager = SkillsManager(tmp_path)

    shorthand = manager.parse_source("openai/skills@main")
    tree = manager.parse_source("https://github.com/openai/skills/tree/main/skills/openai-docs")
    ssh = manager.parse_source("git@github.com:openai/skills.git")

    assert shorthand.kind == "git"
    assert shorthand.url == "https://github.com/openai/skills.git"
    assert shorthand.ref == "main"
    assert tree.subpath == "skills/openai-docs"
    assert ssh.url == "git@github.com:openai/skills.git"
    assert ssh.ref is None


def test_builtin_agents_target_is_project_scoped(tmp_path: Path, make_skill) -> None:
    source = tmp_path / "source"
    make_skill(source, "agent-skill")
    manager = SkillsManager(tmp_path)

    manager.add(str(source), mode="copy")

    assert (tmp_path / ".agents" / "skills" / "agent-skill" / "SKILL.md").exists()


def test_unknown_target_requires_a_plugin(tmp_path: Path, make_skill) -> None:
    source = tmp_path / "source"
    make_skill(source, "agent-skill")
    manager = SkillsManager(tmp_path)

    with pytest.raises(ValueError, match="unsupported install target"):
        manager.add(str(source), targets=["codex"])
