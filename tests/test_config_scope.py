from __future__ import annotations

from pathlib import Path

from skills import SkillsManager, hookimpl
from skills.config import ConfigSource
from skills.plugins import PluginRegistry


def test_skills_toml_is_the_builtin_project_config(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.skills]
agents = ["pyproject"]

[tool.skills.install]
mode = "symlink"
""",
        encoding="utf-8",
    )
    (tmp_path / "skills.toml").write_text(
        """
agents = ["skills-toml"]

[install]
mode = "copy"
""",
        encoding="utf-8",
    )

    manager = SkillsManager(tmp_path)

    assert manager.project.project_config.path == tmp_path / "skills.toml"
    assert manager.get_config("agents") == ["skills-toml"]
    assert manager.get_config("install.mode") == "copy"


def test_pyproject_tool_skills_does_not_mark_project_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    nested = project_root / "nested"
    nested.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text(
        """
[tool.skills]
agents = ["agents"]
""",
        encoding="utf-8",
    )

    manager = SkillsManager(nested)

    assert manager.project.root == nested
    assert manager.get_config("agents") == ["agents"]


def test_local_config_writes_active_project_config(tmp_path: Path) -> None:
    (tmp_path / "skills.toml").write_text('agents = ["agents"]\n', encoding="utf-8")
    manager = SkillsManager(tmp_path)

    manager.set_config("install.mode", "copy", local=True)

    assert 'mode = "copy"' in (tmp_path / "skills.toml").read_text(encoding="utf-8")


def test_plugin_config_sources_are_lower_priority_than_skills_toml(tmp_path: Path) -> None:
    plugin_config = tmp_path / "plugin.toml"
    plugin_config.write_text('agents = ["plugin"]\n', encoding="utf-8")
    (tmp_path / "skills.toml").write_text('agents = ["local"]\n', encoding="utf-8")
    plugins = PluginRegistry()
    plugins.manager.register(_ConfigPlugin(plugin_config), name="test.config")

    manager = SkillsManager(tmp_path, plugins=plugins)

    assert manager.get_config("agents") == ["local"]


def test_plugin_config_sources_fill_missing_project_config(tmp_path: Path) -> None:
    plugin_config = tmp_path / "plugin.toml"
    plugin_config.write_text(
        """
agents = ["plugin"]

[install]
mode = "copy"
""",
        encoding="utf-8",
    )
    plugins = PluginRegistry()
    plugins.manager.register(_ConfigPlugin(plugin_config), name="test.config")

    manager = SkillsManager(tmp_path, plugins=plugins)

    assert manager.get_config("agents") == ["plugin"]
    assert manager.get_config("install.mode") == "copy"


class _ConfigPlugin:
    def __init__(self, path: Path) -> None:
        self.path = path

    @hookimpl
    def config_sources(self, project_root: Path) -> list[ConfigSource]:
        return [
            ConfigSource(
                name="test",
                path=self.path,
                data={
                    "agents": ["plugin"],
                    "install.mode": "copy",
                },
                exists=True,
            )
        ]
