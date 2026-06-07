from __future__ import annotations

from pathlib import Path

from skills import SkillsManager


def test_skills_toml_wins_over_tool_skills(tmp_path: Path) -> None:
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


def test_pyproject_tool_skills_marks_python_project_root(tmp_path: Path) -> None:
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

    assert manager.project.root == project_root
    assert manager.get_config("agents") == ["agents"]


def test_local_config_writes_active_project_config(tmp_path: Path) -> None:
    (tmp_path / "skills.toml").write_text('agents = ["agents"]\n', encoding="utf-8")
    manager = SkillsManager(tmp_path)

    manager.set_config("install.mode", "copy", local=True)

    assert 'mode = "copy"' in (tmp_path / "skills.toml").read_text(encoding="utf-8")
