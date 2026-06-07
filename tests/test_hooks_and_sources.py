from __future__ import annotations

from pathlib import Path

import pytest

from skills import SkillsManager, hookimpl
from skills.features.discovery import Skill
from skills.plugins import PluginRegistry


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


def test_render_prompt_hook_can_wrap_skill_output(tmp_path: Path, make_skill) -> None:
    source = tmp_path / "source"
    make_skill(source, "agent-skill", "Use this skill.")
    plugins = PluginRegistry()
    plugins.load()
    plugins.manager.register(_PromptPlugin(), name="test.prompt")
    manager = SkillsManager(tmp_path, plugins=plugins)

    manager.add(str(source), mode="copy")
    installed = manager.use("agent-skill")
    direct = manager.use(str(source), skill="agent-skill")

    assert installed.prompt.startswith("Use the agent-skill skill:\n\n")
    assert direct.prompt.startswith("Use the agent-skill skill:\n\n")
    assert "Use this skill." in installed.prompt


class _PromptPlugin:
    @hookimpl
    def render_prompt(self, skill: Skill, prompt: str, project: object) -> str:
        return f"Use the {skill.name} skill:\n\n{prompt}"
